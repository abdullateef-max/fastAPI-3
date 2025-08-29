from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = Field(default=True)

class JobApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company: str = Field(index=True)
    position: str
    status: str = Field(default="applied")  # applied, interview, offer, rejected
    date_applied: date = Field(default_factory=date.today)
    user_id: int = Field(foreign_key="user.id")