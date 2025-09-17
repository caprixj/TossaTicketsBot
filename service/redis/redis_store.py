import os
from typing import Optional

from redis.asyncio import Redis


REDIS_URL = os.getenv('REDIS_URL')
CALLBACK_DATA_TTL = 60 * 60 * 24  # 24 hours

_redis: Optional[Redis] = None


def redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis
