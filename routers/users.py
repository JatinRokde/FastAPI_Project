from typing import Annotated

from fastapi import Depends, APIRouter
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import User
from .auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/active_user", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency):
    return user
