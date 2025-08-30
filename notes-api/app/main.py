from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.middleware import count_requests_middleware, get_request_count
from app.routes.notes import router as notes_router
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    create_db_and_tables()
    
    # Create backup file if it doesn't exist
    if not os.path.exists("notes.json"):
        with open("notes.json", "w") as f:
            f.write("[]")
    
    yield
    # Clean up on shutdown (if needed)

app = FastAPI(title="Notes API", version="1.0.0", lifespan=lifespan)

# Add middleware to count requests
app.middleware("http")(count_requests_middleware)

# CORS middleware setup
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notes_router, prefix="/notes", tags=["notes"])

@app.get("/")
def read_root():
    return {"message": "Notes API is running"}

@app.get("/stats/")
def get_stats():
    return {"total_requests": get_request_count()}