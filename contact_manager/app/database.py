from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

# SQLite database URL
DATABASE_URL = "sqlite:///./contacts.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session