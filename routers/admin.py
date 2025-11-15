from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Todos, User
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


# Admin dependency
def admin_required(user: user_dependency):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required!")

    return user


admin_dependency = Annotated[User, Depends(admin_required)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency, admin: admin_dependency):
    todos = db.query(Todos).all()
    return todos
