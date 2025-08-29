from sqlmodel import create_engine, Session
from models import sqlite_url, engine

# Dependency for database session
def get_db():
    with Session(engine) as session:
        yield session