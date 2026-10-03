from contextlib import asynccontextmanager

import config.logging
from api import AuthRouter, MovieRouter, ReservationRouter, ShowRouter
from config.redis import rate_limiter_redis
from database.database import init_db
from fastapi import FastAPI
from service.rate_limiter import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(AuthRouter)
app.include_router(MovieRouter)
app.include_router(ShowRouter)
app.include_router(ReservationRouter)

app.add_middleware(RateLimiter, rate_limiter_redis)
app.add_middleware(CORSMiddleware, allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)