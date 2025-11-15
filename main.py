from fastapi import FastAPI

# ORM models -> database tables
import models
# DB connection object in database.py
from database import engine
from routers import auth, todos, admin

app = FastAPI()

# Read metadata from ORM models
# creates table automatically if it doesn't exist
# bind=engine -> specify which database to create tables
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
