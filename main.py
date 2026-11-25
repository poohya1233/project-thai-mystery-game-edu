from fastapi import FastAPI
import models
from database.base import Base
from database.connection import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Akkhara Mystery Game Backend")


@app.get("/")
async def root():
    return {"message": "Hello World"}