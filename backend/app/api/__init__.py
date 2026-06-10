from fastapi import APIRouter

from app.api import auth, api_keys, tasks, workflows, ws

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(api_keys.router, prefix="/api-keys")
api_router.include_router(tasks.router, prefix="/tasks")
api_router.include_router(workflows.router, prefix="/workflows")
api_router.include_router(ws.router)
