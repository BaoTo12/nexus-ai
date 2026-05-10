import time

import redis.asyncio as aioredis
from fastapi import HTTPException

from app.config import get_settings

settings = get_settings()


async def check_rate_limit(user_id: str) -> None:
    """
    Sliding-window rate limiter using Redis sorted sets.
    Allows RATE_LIMIT_REQUESTS per RATE_LIMIT_WINDOW seconds per user.
    """
    try:
        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        key = f"rate:{user_id}"
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW

        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)   # drop old entries
        pipe.zadd(key, {str(now): now})               # add current request
        pipe.zcard(key)                               # count in window
        pipe.expire(key, settings.RATE_LIMIT_WINDOW)  # auto-expire key
        results = await pipe.execute()
        await r.aclose()

        count = results[2]
        if count > settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Rate limit exceeded. "
                    f"Max {settings.RATE_LIMIT_REQUESTS} requests per "
                    f"{settings.RATE_LIMIT_WINDOW}s."
                ),
            )

    except HTTPException:
        raise
    except Exception:
        # If Redis is down, degrade gracefully — don't block the user
        pass
