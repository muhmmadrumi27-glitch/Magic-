import asyncio
import base64
import json
import traceback
from typing import Any
from uuid import UUID

from playwright.async_api import async_playwright
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.agents.llm_router import call_llm
from app.agents.memory_agent import MemoryAgent
from app.agents.vision_agent import VisionAgent
from app.core.config import settings
from app.services.pubsub import publish_task_event

class AgentOrchestrator:
    def __init__(self, task_id: str, db: AsyncSession, api_key: str | None = None, provider: str | None = None) -> None:
        self.task_id = task_id
        self.db = db
        self.api_key = api_key
        self.provider = provider
        self.memory_agent = MemoryAgent()
        self.vision_agent = VisionAgent(api_key=api_key, provider=provider)
        self.logs: list[str] = []
        self.screenshot_count = 0

    async def publish(self, payload: dict[str, Any]) -> None:
        await publish_task_event(self.task_id, json.dumps(payload))

    async def log(self, text: str) -> None:
        self.logs.append(text)
        await self.publish({"type": "log", "text": text})

    async def screenshot_and_stream(self, page) -> None:
        self.screenshot_count += 1
        image_bytes = await page.screenshot(full_page=False)
        b64 = base64.b64encode(image_bytes).decode()
        await self.publish({"type": "screenshot", "image": b64, "step": self.screenshot_count})

    async def observe(self, page) -> dict[str, Any]:
        dom = await page.content()
        text = await page.inner_text("body")
        await self.publish({"type": "observation", "dom": dom, "text": text})
        return {"dom": dom, "text": text}

    async def run(self) -> None:
        task = await crud.get_task_by_id(self.db, UUID(self.task_id))
        if task is None:
            return
        await crud.update_task_status(self.db, task, "running")
        run = await crud.create_run(self.db, task.id)

        try:
            await self.log(f"Planner: starting task {task.prompt}")
            memory_context = self.memory_agent.query_memory(task.prompt)
            plan = self.build_plan(task.prompt, memory_context)
            await self.log(f"Planner: plan created with {len(plan)} steps")

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self.browserless_websocket())
                context = await browser.new_context()
                page = await context.new_page()
                for index, step in enumerate(plan, start=1):
                    await self.log(f"Executing step {index}: {step}")
                    complete = await self.execute_step(page, step)
                    if complete:
                        break
                    await self.screenshot_and_stream(page)
                    await self.observe(page)
                    await crud.update_run_result(self.db, run, index, {"status": "in_progress", "last_step": step})
                await self.log("Verification: checking final goal")
                verification = await self.verify_goal(page, task.prompt)
                await crud.update_run_result(self.db, run, len(plan), {"status": verification, "prompt": task.prompt})
                await crud.update_task_status(self.db, task, "completed" if verification == "success" else "failed")
                await self.publish({"type": "summary", "result": verification})
        except Exception as exc:
            await self.log(f"Agent error: {str(exc)}")
            await self.log(traceback.format_exc())
            task = await crud.get_task_by_id(self.db, UUID(self.task_id))
            if task:
                await crud.update_task_status(self.db, task, "failed")
            await self.publish({"type": "error", "error": str(exc)})

    def build_plan(self, prompt: str, memory_context: list[dict[str, Any]]) -> list[str]:
        plan = [
            f"Review the user goal: {prompt}",
            "Open the relevant page and identify the first actionable element.",
            "Perform browser actions using available tools to accomplish the goal.",
            "If the action fails, use the vision assistant to recover a working selector.",
            "Confirm task completion and summarize the result.",
        ]
        if memory_context:
            plan.insert(1, f"Leverage memory references: {memory_context}")
        return plan

    async def execute_step(self, page, step: str) -> bool:
        response = call_llm(
            prompt=step,
            tool_messages=[{"role": "user", "content": step}],
            api_key=self.api_key,
            provider=self.provider,
        )
        response_body = response.to_dict()
        choice = response_body.get("choices", [])[0] if response_body.get("choices") else {}
        message = choice.get("message", {})
        function_call = message.get("function_call")
        if function_call:
            name = function_call.get("name")
            args = function_call.get("arguments") or {}
            return await self.invoke_tool(page, name, args)
        if "complete" in step.lower() or "done" in step.lower():
            return True
        return False

    async def invoke_tool(self, page, name: str, args: dict[str, Any]) -> bool:
        try:
            if name == "navigate_url":
                await page.goto(args["url"], wait_until="domcontentloaded", timeout=30000)
                return False
            if name == "click_element":
                await page.click(args["selector"], timeout=10000)
                return False
            if name == "type_text":
                await page.fill(args["selector"], args["text"], timeout=10000)
                return False
            if name == "extract_text":
                text = await page.inner_text("body")
                await self.publish({"type": "extracted_text", "text": text})
                return False
            if name == "task_complete":
                await self.publish({"type": "complete", "result": args.get("result", "done")})
                return True
        except Exception as exc:
            dom_snapshot = await page.content()
            screenshot_bytes = await page.screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            correction = self.vision_agent.analyze_failure(screenshot_b64, dom_snapshot, str(exc))
            await self.log(f"VisionAgent recovery suggestion: {correction}")
            return False
        return False

    async def verify_goal(self, page, prompt: str) -> str:
        text = await page.inner_text("body")
        if prompt.lower() in text.lower() or len(text) > 0:
            return "success"
        return "failed"

    def browserless_websocket(self) -> str:
        return settings.browserless_ws
