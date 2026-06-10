from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.core.security import decode_access_token
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_db_dep() -> AsyncSession:
    async for db in get_db():
        yield db

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_dep)) -> models.User:
    token_data = decode_access_token(token)
    if token_data is None or token_data.sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    user = await crud.get_user(db, token_data.sub)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user