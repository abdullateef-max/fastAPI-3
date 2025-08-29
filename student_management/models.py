from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int
    email: str = Field(unique=True, index=True)
    grades: str = Field(default="[]")  # Store grades as JSON string
    
    def get_grades(self) -> List[Dict[str, Any]]:
        return json.loads(self.grades)
    
    def set_grades(self, grades: List[Dict[str, Any]]):
        self.grades = json.dumps(grades)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)

sqlite_url = "sqlite:///students.db"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session