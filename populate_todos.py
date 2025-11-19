from database import SessionLocal
from .models import Todos


def seed_todos():
    db = SessionLocal()

    todos = [
        Todos(title='Buy groceries', description='Purchase milk, eggs, and bread from the store', priority=2,
              complete=False),
        Todos(title='Complete FastAPI tutorial', description='Finish the basics and build the first API', priority=3,
              complete=True),
        Todos(title='Workout', description='Go for a 45-min gym session', priority=3, complete=False),
        Todos(title='Pay electricity bill', description='Pay electricity bill before the due date this week',
              priority=1, complete=False),
        Todos(title='Read a tech blog', description='Read about the latest Gen AI developments', priority=3,
              complete=False)
    ]

    db.add_all(todos)
    db.commit()
    db.close()


if __name__ == '__main__':
    seed_todos()
    print("Data added successfully!")
