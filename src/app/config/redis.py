import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from types import FunctionType
from uuid import UUID

from database.models import Movie, Show
from redis.asyncio import Redis

lg = logging.getLogger(__name__)

rate_limiter_redis = Redis(
    decode_responses=True,
    retry_on_timeout=True,
)


cache_movie_redis = Redis(db=1, decode_responses=True, retry_on_timeout=True)


def show_cache(func: FunctionType):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if coded := await cache_movie_redis.get(f"show:{kwargs['movie_id']}"):
            lg.info("load show cache")
            decoded: dict = json.loads(coded)
            return [json.loads(x) for x in decoded.values()]
            # return [json.loads(x) for x in coded]

        result: list[Show] = await func(*args, **kwargs)
        await cache_movie_redis.set(
            f"show:{kwargs['movie_id']}",
            json.dumps({str(i): x.to_str() for i, x in enumerate(result)}),
            ex=timedelta(minutes=60),
        )
        lg.info("set expired show cache")
        return result

    return wrapper


def movie_cache(func: FunctionType):
    @wraps(func)
    async def wrapper(*args, **kwargs):

        if coded := await cache_movie_redis.get("movies"):
            decoded: dict = json.loads(coded)
            lg.info("load movie cache")
            return [json.loads(x) for x in decoded.values()]

        result: list[Movie] = await func(*args, **kwargs)
        await cache_movie_redis.set(
            "movies",
            json.dumps({str(i): x.to_str() for i, x in enumerate(result)}),
            timedelta(minutes=60),
        )
        lg.info("set expired movie cache")
        return result

    return wrapper
