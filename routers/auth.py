import re

from fastapi import APIRouter
from pydantic import BaseModel, field_validator

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


@router.get("/auth")
async def auth():
    return {"message": "User authenticated"}
