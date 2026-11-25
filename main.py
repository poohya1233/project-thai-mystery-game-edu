from contextlib import asynccontextmanager

from fastapi import FastAPI

import models
from database.base import Base
from database.connection import engine
from routers import auth_router, game_router, player_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Akkhara Mystery Game Backend",
    description="Backend API for อักขราผจญภัย ไขคำพิชิตหมอก (FastAPI + PostgreSQL + SQLAlchemy 2.0)",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(player_router)
app.include_router(game_router)


@app.get("/")
async def root():
    return {"message": "Akkhara Mystery Game Backend is running"}