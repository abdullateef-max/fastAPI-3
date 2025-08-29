from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List, Dict, Any
import json

from models import Student, User, create_db_and_tables, get_session, engine
from auth import get_current_user, create_default_user, UserCreate, create_user_in_db, create_user_in_json, load_users
from middleware import log_requests
from database import get_db

app = FastAPI(title="Student Management System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.middleware("http")(log_requests)

# Initialize database and default user
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    create_default_user()

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Student Management System API"}

# User registration endpoint (public)
@app.post("/register/", status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_db)
):
    try:
        # Try to create user in database first
        user = create_user_in_db(user_data, session)
        return {"message": "User created successfully", "user": user}
    except Exception as e:
        # Fallback to JSON file if database fails
        try:
            user = create_user_in_json(user_data)
            return {"message": "User created in JSON file", "user": user}
        except Exception as json_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create user: {str(json_error)}"
            )

# Get current user info (protected)
@app.get("/users/me/")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": getattr(current_user, 'email', 'N/A'),
        "is_active": getattr(current_user, 'is_active', True)
    }

# Get all users (admin only)
@app.get("/users/", response_model=List[Dict[str, Any]])
def get_all_users(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is admin
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can view all users"
        )
    
    # Get users from database
    db_users = session.exec(select(User)).all()
    users_list = []
    
    for user in db_users:
        users_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "source": "database"
        })
    
    # Also include users from JSON file
    json_users = load_users()
    
    for username, user_info in json_users.items():
        # Skip if user already exists in database
        if not any(u["username"] == username for u in users_list):
            users_list.append({
                "id": None,
                "username": user_info["username"],
                "email": user_info["email"],
                "is_active": user_info["is_active"],
                "source": "json"
            })
    
    return users_list

# Create student (protected)
@app.post("/students/", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(
    student: Student,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if email already exists
    existing_student = session.exec(select(Student).where(Student.email == student.email)).first()
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

# Get all students
@app.get("/students/", response_model=List[Student])
def read_students(session: Session = Depends(get_db)):
    students = session.exec(select(Student)).all()
    return students

# Get student by ID
@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int, session: Session = Depends(get_db)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Update student (protected)
@app.put("/students/{student_id}", response_model=Student)
def update_student(
    student_id: int,
    student_update: Student,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if email is being changed to an existing one
    if student_update.email != student.email:
        existing_student = session.exec(select(Student).where(Student.email == student_update.email)).first()
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    student_data = student_update.dict(exclude_unset=True)
    for key, value in student_data.items():
        setattr(student, key, value)
    
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

# Delete student (protected)
@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    session.delete(student)
    session.commit()
    return {"message": "Student deleted successfully"}

# Add grade to student (protected)
@app.post("/students/{student_id}/grades")
def add_grade(
    student_id: int,
    grade: Dict[str, Any],
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    grades = student.get_grades()
    grades.append(grade)
    student.set_grades(grades)
    
    session.add(student)
    session.commit()
    session.refresh(student)
    
    return {"message": "Grade added successfully", "grades": grades}

# Get student grades
@app.get("/students/{student_id}/grades")
def get_grades(student_id: int, session: Session = Depends(get_db)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student.get_grades()

# Search students by name
@app.get("/students/search/{name}")
def search_students(name: str, session: Session = Depends(get_db)):
    students = session.exec(select(Student).where(Student.name.ilike(f"%{name}%"))).all()
    return students

# Get students by age range
@app.get("/students/age/{min_age}/{max_age}")
def get_students_by_age(min_age: int, max_age: int, session: Session = Depends(get_db)):
    students = session.exec(select(Student).where(Student.age >= min_age, Student.age <= max_age)).all()
    return students

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)