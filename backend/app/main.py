from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.api import api_router
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.app_name)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/healthz")
async def healthz() -> JSONResponse:
    return JSONResponse({"status": "ok"})
