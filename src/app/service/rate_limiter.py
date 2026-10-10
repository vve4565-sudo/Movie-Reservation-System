from collections.abc import Awaitable, Callable
from datetime import timedelta

from fastapi import HTTPException, Request, Response, status
from fastapi.datastructures import State
from redis.asyncio import Redis
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.types import ASGIApp


class RateLimiter(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        redis: Redis,
    ) -> None:
        super().__init__(app)
        self.redis = redis

    async def dispatch(
        self,
        request: Request[State],
        call_next: Callable[[Request[State]], Awaitable[Response]],
    ) -> Response:

        # user_ip = request.headers["X-Real-IP"]
        user_ip = str(request.client.host)
        if not await self.redis.get(user_ip):
            await self.redis.setex(name=user_ip, time=timedelta(minutes=1), value=1)

        elif int(await self.redis.get(user_ip)) < 120:
            await self.redis.incrby(name=user_ip)

        else:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS)

        response = await call_next(request)
        return response
