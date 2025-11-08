from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

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


@app.get("/todos", status_code=status.HTTP_200_OK)
# async def get_todos(db: Session = Depends(get_db)):
async def get_todos(db: db_dependency):
    todos = db.query(Todos).all()
    if todos is not None:
        return todos
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todos not found!")


@app.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail='Todo not found!')
