from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from . import models, database, auth, middleware
from .database import get_session, create_db_and_tables
from .auth import get_current_user, create_user, create_access_token, get_password_hash
from .models import Contact, ContactCreate, ContactUpdate, UserCreate, Token

app = FastAPI(title="Contact Manager API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware for IP logging
app.middleware("http")(middleware.log_middleware)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/register", response_model=Token)
def register(user: UserCreate, session: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = session.exec(select(models.User).where(
        models.User.username == user.username
    )).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    db_user = auth.create_user(user, session)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login_for_access_token(user: UserCreate, session: Session = Depends(get_session)):
    # Authenticate user
    db_user = session.exec(select(models.User).where(
        models.User.username == user.username
    )).first()
    
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/contacts/", response_model=Contact)
def create_contact(
    contact: ContactCreate,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if contact with same email already exists for this user
    existing_contact = session.exec(select(Contact).where(
        (Contact.email == contact.email) & (Contact.user_id == current_user.id)
    )).first()
    
    if existing_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact with this email already exists"
        )
    
    db_contact = Contact(
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        user_id=current_user.id
    )
    
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    return db_contact

@app.get("/contacts/", response_model=List[Contact])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    contacts = session.exec(
        select(Contact)
        .where(Contact.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return contacts

@app.get("/contacts/{contact_id}", response_model=Contact)
def read_contact(
    contact_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    contact = session.exec(
        select(Contact)
        .where((Contact.id == contact_id) & (Contact.user_id == current_user.id))
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    return contact

@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    contact = session.exec(
        select(Contact)
        .where((Contact.id == contact_id) & (Contact.user_id == current_user.id))
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Update only provided fields
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    contact.updated_at = datetime.utcnow()
    
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact

@app.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int,
    current_user: models.User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    contact = session.exec(
        select(Contact)
        .where((Contact.id == contact_id) & (Contact.user_id == current_user.id))
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    session.delete(contact)
    session.commit()
    
    return {"message": "Contact deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)