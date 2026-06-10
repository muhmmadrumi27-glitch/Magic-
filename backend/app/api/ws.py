import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from fastapi.responses import HTMLResponse

from app.services.pubsub import get_redis
from app.api.deps import get_current_user

router = APIRouter()

@router.websocket("/ws/browser/{task_id}")
async def browser_ws(task_id: str, websocket: WebSocket, token: str | None = None):
    await websocket.accept()
    user = None
    try:
        # JWT is expected as query param token
        if token:
            from app.core.security import decode_access_token
            payload = decode_access_token(token)
            if payload is None or payload.sub is None:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
            user = payload.sub
        else:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        redis = get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"task:{task_id}:channel")

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=10.0)
            if message and message.get("data"):
                payload = message["data"]
                if isinstance(payload, bytes):
                    payload = payload.decode()
                await websocket.send_text(payload)
            await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except WebSocketDisconnect:
        pass
    finally:
        if user is not None:
            await pubsub.unsubscribe(f"task:{task_id}:channel")
            await pubsub.close()