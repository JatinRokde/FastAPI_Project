# create_engine: Creates connection to the DB
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# declarative_base: ORM models (tables) in a class-based way
from sqlalchemy.ext.declarative import declarative_base

# sessionmaker: Factory function that creates DB session objects that interacts with DB (run queries, add data, etc.)
from sqlalchemy.orm import sessionmaker

# DB URI (/// -> relative path)
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URI:
    raise ValueError("DATABASE_URL environment variable not set!")

# engine: core interface to the DB, manages connection pool and interacts with directly to the DB (connects FastAPIs to the DB)
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# sessionmaker: factory that creates DB session objects i.e. provides session each time when wants to interact with DB
# (bind=engine): links the session to the previously created engine, so all session use the same DB connection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for all ORM models
Base = declarative_base()
