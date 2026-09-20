import json
import logging
from datetime import timedelta
from functools import wraps
from typing import Literal

from redis.asyncio import Redis

lg = logging.getLogger(__name__)

rate_limiter_redis = Redis(
    decode_responses=True,
    retry_on_timeout=True,
)


cache_movie_redis = Redis(db=1, decode_responses=False, retry_on_timeout=True)


def cache_decorator(*, module: Literal["shows", "reservations"]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            if coded := await cache_movie_redis.get(module):
                lg.info(f"load cache for {module}")
                return [json.loads(coded)]

            result = await func(*args, **kwargs)
            lg.info(f"set expired cache for {module}")
            await cache_movie_redis.setex(
                module,
                timedelta(minutes=60),
                *(x.to_bytes() for x in result),
            )

            return result

        return wrapper

    return decorator
