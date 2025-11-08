from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# ORM models -> database tables
import models
# DB connection object in database.py
from database import engine, SessionLocal
from models import Todos

app = FastAPI()

# Read metadata from ORM models
# creates table automatically if it doesn't exist
# bind=engine -> specify which database to create tables
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


'''Dependency Injection (DI) is a design pattern where you define dependencies (like DB, Auth, Config) separately,
and let the framework (FastAPI) inject them automatically when needed.'''
# Dependency Injection
db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/todos")
# async def get_todos(db: Session = Depends(get_db)):
async def get_todos(db: db_dependency):
    todos = db.query(Todos).all()
    return todos
