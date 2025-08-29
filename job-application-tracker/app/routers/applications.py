from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from app.database import get_session
from app.models import JobApplication, User
from app.schemas import JobApplicationCreate, JobApplicationResponse
from app.dependencies import get_current_user, check_user_agent

router = APIRouter(tags=["applications"])

@router.post("/applications/", response_model=JobApplicationResponse)
def create_job_application(
    application: JobApplicationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    user_agent: str = Depends(check_user_agent)
):
    db_application = JobApplication(**application.dict(), user_id=current_user.id)
    session.add(db_application)
    session.commit()
    session.refresh(db_application)
    return db_application

@router.get("/applications/", response_model=List[JobApplicationResponse])
def read_applications(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    user_agent: str = Depends(check_user_agent)
):
    applications = session.exec(
        select(JobApplication)
        .where(JobApplication.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return applications

@router.get("/applications/search", response_model=List[JobApplicationResponse])
def search_applications(
    status: str = Query(..., description="Filter applications by status"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    user_agent: str = Depends(check_user_agent)
):
    applications = session.exec(
        select(JobApplication)
        .where(JobApplication.user_id == current_user.id)
        .where(JobApplication.status == status)
    ).all()
    
    if not applications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No applications found with status: {status}"
        )
    
    return applications