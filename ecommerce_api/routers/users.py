from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.database import User, get_session
from utils.auth import get_password_hash, create_access_token, verify_password
from datetime import timedelta

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register")
def register_user(username: str, email: str, password: str, session: Session = Depends(get_session)):
    # Check if user exists
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = session.exec(select(User).where(User.email == email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"message": "User created successfully"}

@router.post("/token")
def login_for_access_token(username: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}