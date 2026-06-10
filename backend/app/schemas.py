from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: UUID | None = None
    exp: int | None = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class APIKeyCreate(BaseModel):
    provider: str
    api_key: str

class APIKeyRead(BaseModel):
    id: UUID
    provider: str

    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    prompt: str

class TaskRead(BaseModel):
    id: UUID
    prompt: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class RunRead(BaseModel):
    id: UUID
    task_id: UUID
    steps_completed: str
    final_result: dict[str, Any] | None

    class Config:
        orm_mode = True

class WorkflowCreate(BaseModel):
    name: str
    steps: list[dict[str, Any]]

class WorkflowRead(BaseModel):
    id: UUID
    name: str
    steps: list[dict[str, Any]]

    class Config:
        orm_mode = True

class Providers(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    claude = "claude"
    gemini = "gemini"
    groq = "groq"
    deepseek = "deepseek"