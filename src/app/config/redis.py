import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from types import FunctionType
from uuid import UUID

from database.models import Movie, Show
from pydantic import TypeAdapter
from redis.asyncio import Redis
from schemas.movie import SOutputMovie
from schemas.show import SShowOutput

lg = logging.getLogger(__name__)

rate_limiter_redis = Redis(
    decode_responses=True,
    retry_on_timeout=True,
)


cache_movie_redis = Redis(db=1, decode_responses=True, retry_on_timeout=True)
show_adapter = TypeAdapter(list[SShowOutput])
movie_adapter = TypeAdapter(list[SOutputMovie])


def show_cache(func: FunctionType):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if coded := await cache_movie_redis.get(f"show:{kwargs['movie_id']}"):
            lg.info("load show cache")
            decoded = json.loads(coded)
            return [SShowOutput.model_validate(x) for x in decoded]

        result: list[SShowOutput] = await func(*args, **kwargs)
        json_string = show_adapter.dump_json(result).decode()
        await cache_movie_redis.set(
            f"show:{kwargs['movie_id']}",
            json_string,
            ex=timedelta(minutes=60),
        )
        lg.info("set expired show cache")
        return result

    return wrapper


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
