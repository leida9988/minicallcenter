import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings
class RedisClient:
    _instance: Optional[redis.Redis] = None
    @classmethod
    async def get_instance(cls) -> redis.Redis:
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
        return cls._instance
    @classmethod
    async def close(cls) -> None:
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None
    @classmethod
    async def set(cls, key: str, value: Any, expire: int = None) -> None:
        redis_client = await cls.get_instance()
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.set(key, value, ex=expire)
    @classmethod
    async def get(cls, key: str, default: Any = None) -> Any:
        redis_client = await cls.get_instance()
        value = await redis_client.get(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    @classmethod
    async def delete(cls, key: str) -> None:
        redis_client = await cls.get_instance()
        await redis_client.delete(key)
    @classmethod
    async def exists(cls, key: str) -> bool:
        redis_client = await cls.get_instance()
        return await redis_client.exists(key) == 1
    @classmethod
    async def expire(cls, key: str, seconds: int) -> None:
        redis_client = await cls.get_instance()
        await redis_client.expire(key, seconds)
    @classmethod
    async def ttl(cls, key: str) -> int:
        redis_client = await cls.get_instance()
        return await redis_client.ttl(key)
    @classmethod
    async def keys(cls, pattern: str) -> list:
        redis_client = await cls.get_instance()
        return await redis_client.keys(pattern)
