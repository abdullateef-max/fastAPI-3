from sqlmodel import Session, select
from app.models import JobApplication, User
from app.schemas import JobApplicationCreate
from typing import List

def get_applications_by_user(session: Session, user_id: int, skip: int = 0, limit: int = 100):
    return session.exec(
        select(JobApplication)
        .where(JobApplication.user_id == user_id)
        .offset(skip)
        .limit(limit)
    ).all()

def get_application_by_id(session: Session, application_id: int, user_id: int):
    return session.exec(
        select(JobApplication)
        .where(JobApplication.id == application_id)
        .where(JobApplication.user_id == user_id)
    ).first()

def create_application(session: Session, application: JobApplicationCreate, user_id: int):
    db_application = JobApplication(**application.dict(), user_id=user_id)
    session.add(db_application)
    session.commit()
    session.refresh(db_application)
    return db_application

def search_applications_by_status(session: Session, status: str, user_id: int):
    return session.exec(
        select(JobApplication)
        .where(JobApplication.user_id == user_id)
        .where(JobApplication.status == status)
    ).all()