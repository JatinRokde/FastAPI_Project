from fastapi import FastAPI

# DB connection object in database.py
from .database import engine
# ORM models -> database tables
from .models import Base
from .routers import auth, todos, admin, users

app = FastAPI()

# Read metadata from ORM models
# creates table automatically if it doesn't exist
# bind=engine -> specify which database to create tables
Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["Health"])
async def check_health():
    return {'status': 'ok'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
