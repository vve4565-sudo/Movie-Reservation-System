from contextlib import asynccontextmanager

import config.logging
from api import AuthRouter, MovieRouter, ShowRouter
from database.database import init_db
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(AuthRouter)
app.include_router(MovieRouter)
app.include_router(ShowRouter)
