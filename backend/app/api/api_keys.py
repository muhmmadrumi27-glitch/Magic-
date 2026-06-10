from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.deps import get_current_user, get_db_dep
from app.schemas import APIKeyCreate, APIKeyRead

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

@router.post("/", response_model=APIKeyRead)
async def create_api_key(api_key_in: APIKeyCreate, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)) -> APIKeyRead:
    key = await crud.create_api_key(db, current_user.id, api_key_in.provider, api_key_in.api_key)
    return key

@router.get("/", response_model=list[APIKeyRead])
async def list_api_keys(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)) -> list[APIKeyRead]:
    keys = await crud.get_api_keys_for_user(db, current_user.id)
    return keys
