from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.deps import get_current_user, get_db_dep
from app.schemas import WorkflowCreate, WorkflowRead

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/", response_model=WorkflowRead)
async def create_workflow(workflow_in: WorkflowCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)) -> WorkflowRead:
    workflow = await crud.create_workflow(db, current_user.id, workflow_in.name, workflow_in.steps)
    return workflow

@router.get("/", response_model=list[WorkflowRead])
async def list_workflows(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)) -> list[WorkflowRead]:
    return await crud.get_workflows_for_user(db, current_user.id)
