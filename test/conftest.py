import pytest
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..database import get_db
from ..main import app
from ..models import User, Todos
from ..routers.auth import get_current_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # keeps the DB alive across multiple connections
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user():
    db = TestingSessionLocal()

    hashed = pwd_context.hash("oldpassword")

    user = User(
        id=1,
        username="test_user",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=hashed,
        role="admin",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    yield user

    db = TestingSessionLocal()
    db.query(Todos).delete()
    db.query(User).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_todo(test_user):
    db = TestingSessionLocal()

    todo = Todos(
        title="Test Todo",
        description="Test Description",
        priority=3,
        complete=False,
        user_id=test_user.id
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    yield todo

    db = TestingSessionLocal()
    db.query(Todos).delete()  # delete ALL todos
    db.commit()
    db.close()


def override_get_current_user():
    db = TestingSessionLocal()
    try:
        return db.query(User).filter(User.id == 1).first()
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
