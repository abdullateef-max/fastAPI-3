from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.routers import applications, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Job Application Tracker",
    description="API for tracking job applications with authentication",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(applications.router)

@app.get("/")
def read_root():
    return {"message": "Job Application Tracker API"}