import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import User

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, password):
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


# Dependency Injection
# Session - connection to the database for a single request
db_dependency = Annotated[Session, Depends(get_db)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


@router.post("/auth/add_user")
async def add_user(user_req: UserCreate, db: db_dependency):
    # Check if the user already exists
    existing_user = db.query(User).filter((User.username == user_req.username) | (User.email == user_req.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists.")

    # Hash the password
    password_hash = hash_password(user_req.password)
    new_user = User(
        username=user_req.username,
        email=user_req.email,
        first_name=user_req.first_name,
        last_name=user_req.last_name,
        hashed_password=password_hash,
        role=user_req.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"{new_user.username} added successfully.",
        "user_id": new_user.id
    }
