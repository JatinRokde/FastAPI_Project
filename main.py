from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel, Field
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


class TodoCreate(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(default=0, gt=0, le=5)
    complete: bool = Field(default=False)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Title",
                "description": "Description",
                "priority": 0,
                "complete": False
            }
        }
    }


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


@app.post("/todos/add_todo", status_code=status.HTTP_201_CREATED)
async def add_todo(db: db_dependency, todo_req: TodoCreate):
    todo_model = Todos(**todo_req.model_dump())
    db.add(todo_model)
    db.commit()


@app.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(db: db_dependency, todo_req: TodoCreate, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!")

    todo.title = todo_req.title
    todo.description = todo_req.description
    todo.priority = todo_req.priority
    todo.complete = todo_req.complete

    db.commit()
    # reloads the latest version of that object from DB
    db.refresh(todo)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!")

    # db.query(Todos).filter(Todos.id == todo_id).delete()
    db.delete(todo)
    db.commit()
