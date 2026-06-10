import base64
import httpx
from typing import Any

from app.agents.llm_router import call_llm

VISION_MODELS = ["gpt-4o-vision", "claude-3.5-vision"]

class VisionAgent:
    def __init__(self, api_key: str | None = None, provider: str | None = None) -> None:
        self.api_key = api_key
        self.provider = provider

    def analyze_failure(self, screenshot_b64: str, dom_snapshot: str, error_message: str) -> str:
        prompt = (
            "A browser automation action failed. Use the DOM snapshot and screenshot to identify a robust selector." 
            f"Error: {error_message}\nDOM:\n{dom_snapshot}"
        )
        message = [
            {"role": "system", "content": "You are an expert browser automation assistant."},
            {"role": "user", "content": prompt},
        ]
        response = call_llm(
            prompt=prompt,
            tool_messages=message,
            api_key=self.api_key,
            provider=self.provider,
        )
        body = response.to_dict()
        if body.get("choices"):
            return body["choices"][0].get("message", {}).get("content", "")
        return ""
