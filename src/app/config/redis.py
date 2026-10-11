import json
import logging
from datetime import timedelta
from functools import wraps
from types import FunctionType
from uuid import UUID

from pydantic import TypeAdapter
from redis.asyncio import Redis

from app.config.config import config
from app.schemas.movie import SOutputMovie
from app.schemas.show import SShowOutput

lg = logging.getLogger(__name__)

rate_limiter_redis = Redis(
    decode_responses=True,
    retry_on_timeout=True,
    port=config.REDIS_PORT,
    host=config.REDIS_HOST,
)


cache_movie_redis = Redis(
    db=1,
    decode_responses=True,
    retry_on_timeout=True,
    port=config.REDIS_PORT,
    host=config.REDIS_HOST,
)
movie_adapter = TypeAdapter(list[SOutputMovie])


def show_cache(func: FunctionType):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        movie_id = kwargs["movie_id"]
        start = kwargs["start"]
        cache_key = f"show:{movie_id}:"
        if coded := await cache_movie_redis.get(cache_key + str(start)):
            lg.info("load show cache")
            decoded = json.loads(coded)
            return [SShowOutput.model_validate(x) for x in decoded]

        result: list[SShowOutput] = await func(*args, **kwargs)
        for i in result:
            await cache_movie_redis.set(
                cache_key + str(i.start),
                i.model_dump_json(),
                ex=timedelta(minutes=60),
            )
        lg.info("set expired show cache")
        return result

    return wrapper


async def invalidate_show_cache(movie_id: UUID) -> None:
    pattern = f"show:{movie_id}*"
    keys = [key async for key in cache_movie_redis.scan_iter(match=pattern)]
    if keys:
        await cache_movie_redis.delete(*keys)
        lg.info(
            "invalidated show cache",
            extra={"movie_id": str(movie_id), "keys": len(keys)},
        )


async def invalidate_movie_cache() -> None:
    key = "movies"

    await cache_movie_redis.delete(key)
    lg.info(
        "invalidated show cache",
        extra={"key": key},
    )


def movie_cache(func: FunctionType):
    @wraps(func)
    async def wrapper(*args, **kwargs):

        if coded := await cache_movie_redis.get("movies"):
            decoded = json.loads(coded)
            lg.info("load movie cache")
            return [SOutputMovie.model_validate(x) for x in decoded]

        result: list[SOutputMovie] = await func(*args, **kwargs)
        json_string = movie_adapter.dump_json(result).decode()
        await cache_movie_redis.set(
            "movies",
            json_string,
            timedelta(minutes=60),
        )
        lg.info("set expired movie cache")
        return result

    return wrapper
