from app.services.redis_client import get_redis

async def publish_task_event(task_id: str, payload: str) -> None:
    redis = get_redis()
    await redis.publish(f"task:{task_id}:channel", payload)
