from fastapi import APIRouter, Depends, HTTPException
from slowapi.util import get_remote_address
from slowapi import Limiter
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app import crud
from app.api.deps import get_current_user, get_db_dep
from app.celery_app import celery_app
from app.schemas import TaskCreate, TaskRead

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead)
@limiter.limit("5/minute")
async def create_task(task_in: TaskCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)) -> TaskRead:
    task = await crud.create_task(db, current_user.id, task_in.prompt)
    celery_app.send_task("app.tasks.execute_agent_task", args=[str(task.id)])
    return task

@router.get("/", response_model=list[TaskRead])
async def list_tasks(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)) -> list[TaskRead]:
    return await crud.get_tasks_for_user(db, current_user.id)

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)) -> TaskRead:
    task = await crud.get_task_by_id(db, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
