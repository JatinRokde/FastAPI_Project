import re
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, field_validator
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


class ChangePasswordForm(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, password: str):
        # pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{6,}$"
        errors = []
        if len(password) < 6:
            errors.append('at least 6 characters')
        if not re.search(r'[a-z]', password):
            errors.append('at least one lowercase character')
        if not re.search(r'[A-Z]', password):
            errors.append('at least one uppercase character')
        if not re.search(r'\d', password):
            errors.append('at least one number')
        if not re.search(r'[\W_]', password):
            errors.append('at least one special character')

        if errors:
            raise ValueError("Password must contain " + ", ".join(errors) + ".")

        return password


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


@router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency, db: db_dependency, req: ChangePasswordForm):
    # user from user_dependency calls get_current_user() which creates another session of db
    # Get the user
    current_user = db.query(User).filter(User.id == user.id).first()

    # Verify the old password
    if not pwd_context.verify(req.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    # Hash the new password
    hashed_new_password = pwd_context.hash(req.new_password)
    current_user.hashed_password = hashed_new_password

    db.commit()

    return "Password changed successfully"
