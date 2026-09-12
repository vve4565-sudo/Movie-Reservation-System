from contextlib import asynccontextmanager

from api import AuthRouter
from database.database import init_db
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(AuthRouter)
