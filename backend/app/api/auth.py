from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api.deps import get_db_dep
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.schemas import Token, UserCreate, UserRead

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db_dep)) -> UserRead:
    existing = await crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = await crud.create_user(db, user_in.email, user_in.password)
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_dep)) -> Token:
    user = await crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
