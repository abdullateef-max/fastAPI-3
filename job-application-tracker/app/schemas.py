from pydantic import BaseModel
from datetime import date
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        orm_mode = True

class JobApplicationCreate(BaseModel):
    company: str
    position: str
    status: str = "applied"
    date_applied: date

class JobApplicationResponse(JobApplicationCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True