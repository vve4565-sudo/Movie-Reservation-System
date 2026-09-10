from contextlib import asynccontextmanager

from database.database import engine
from database.models import Base
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
