from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.agents.agent_orchestrator import AgentOrchestrator
from app.core.crypto import decrypt_secret
from app import crud

@celery_app.task(name="app.tasks.execute_agent_task", bind=True)
def execute_agent_task(self, task_id: str) -> None:
    async def run_task() -> None:
        async with AsyncSessionLocal() as db:
            task = await crud.get_task_by_id(db, task_id)
            if task is None:
                return
            api_keys = await crud.get_api_keys_for_user(db, task.user_id)
            provider = api_keys[0].provider if api_keys else None
            api_key = decrypt_secret(api_keys[0].encrypted_key) if api_keys else None
            orchestrator = AgentOrchestrator(task_id=task_id, db=db, api_key=api_key, provider=provider)
            await orchestrator.run()

    import asyncio
    asyncio.run(run_task())
