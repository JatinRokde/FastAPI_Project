import os
import re
from datetime import timedelta, datetime, timezone
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def hash_password(password: str):
    return pwd_context.hash(password)


@router.post("/add_user")
async def add_user(user_req: UserCreate, db: db_dependency):
    # Check if the user already exists
    existing_user = db.query(User).filter((User.username == user_req.username) | (User.email == user_req.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists.")

    '''
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
    '''

    user_data = user_req.model_dump(exclude={"password"})
    hashed_password = hash_password(user_req.password)
    user_data["hashed_password"] = hashed_password
    new_user = User(**user_data)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"{new_user.username} added successfully.",
        "user_id": new_user.id
    }


def authenticate_user(db: db_dependency, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if not username or not user_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # Authenticate the user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password, authentication failed.",
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id},
        expires_delta=access_token_expires
    )

    # Return token
    return {"access_token": access_token, "token_type": "bearer"}
