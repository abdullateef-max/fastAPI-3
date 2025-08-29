from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session, select
from models import User, get_session, engine
import json
import bcrypt
from typing import Dict, Any
from pydantic import BaseModel

security = HTTPBasic()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool = True

# Load users from JSON file
def load_users() -> Dict[str, Dict[str, Any]]:
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save users to JSON file
def save_users(users: Dict[str, Dict[str, Any]]):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

# Hash password
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Authentication dependency
def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    # First check database
    user = session.exec(select(User).where(User.username == credentials.username)).first()
    
    if user and verify_password(credentials.password, user.hashed_password):
        return user
    
    # Fallback to JSON file
    users = load_users()
    if credentials.username in users:
        stored_user = users[credentials.username]
        if verify_password(credentials.password, stored_user["hashed_password"]):
            return stored_user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

# Create user in database
def create_user_in_db(user_data: UserCreate, session: Session):
    # Check if username exists
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    existing_email = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=user_data.is_active
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Create user in JSON file (fallback)
def create_user_in_json(user_data: UserCreate):
    users = load_users()
    
    if user_data.username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists in any user
    for username, user_info in users.items():
        if user_info.get("email") == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    hashed_password = hash_password(user_data.password)
    users[user_data.username] = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "is_active": user_data.is_active
    }
    
    save_users(users)
    return users[user_data.username]

# Create initial admin user if not exists
def create_default_user():
    users = load_users()
    if "admin" not in users:
        users["admin"] = {
            "username": "admin",
            "email": "admin@school.com",
            "hashed_password": hash_password("admin123"),
            "is_active": True
        }
        save_users(users)