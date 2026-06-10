from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.crypto import encrypt_secret
from app.core.security import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def get_user(db: AsyncSession, user_id: UUID) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, email: str, password: str) -> models.User:
    user = models.User(email=email, hashed_password=get_password_hash(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_api_key(db: AsyncSession, user_id: UUID, provider: str, api_key: str) -> models.APIKey:
    encrypted = encrypt_secret(api_key)
    key = models.APIKey(user_id=user_id, provider=provider, encrypted_key=encrypted)
    db.add(key)
    await db.commit()
    await db.refresh(key)
    return key

async def get_api_keys_for_user(db: AsyncSession, user_id: UUID) -> list[models.APIKey]:
    result = await db.execute(select(models.APIKey).where(models.APIKey.user_id == user_id))
    return result.scalars().all()

async def create_task(db: AsyncSession, user_id: UUID, prompt: str) -> models.Task:
    task = models.Task(user_id=user_id, prompt=prompt, status="pending")
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

async def get_task_by_id(db: AsyncSession, task_id: UUID) -> Optional[models.Task]:
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    return result.scalars().first()

async def update_task_status(db: AsyncSession, task: models.Task, status: str) -> models.Task:
    task.status = status
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

async def create_run(db: AsyncSession, task_id: UUID, steps_completed: int = 0) -> models.Run:
    run = models.Run(task_id=task_id, steps_completed=str(steps_completed), final_result={})
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run

async def update_run_result(db: AsyncSession, run: models.Run, steps_completed: int, final_result: dict[str, Any]) -> models.Run:
    run.steps_completed = str(steps_completed)
    run.final_result = final_result
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run

async def create_workflow(db: AsyncSession, user_id: UUID, name: str, steps: list[dict[str, Any]]) -> models.Workflow:
    workflow = models.Workflow(user_id=user_id, name=name, steps=steps)
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow

async def get_workflows_for_user(db: AsyncSession, user_id: UUID) -> list[models.Workflow]:
    result = await db.execute(select(models.Workflow).where(models.Workflow.user_id == user_id))
    return result.scalars().all()

async def get_tasks_for_user(db: AsyncSession, user_id: UUID) -> list[models.Task]:
    result = await db.execute(select(models.Task).where(models.Task.user_id == user_id).order_by(models.Task.created_at.desc()))
    return result.scalars().all()