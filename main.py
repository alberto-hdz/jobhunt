from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt
import requests
from datetime import datetime
from typing import Optional

app = FastAPI()

# Database setup
DATABASE_URL = "postgresql://albertohdz:H3rN4nD3z1063_@jobhunt.c7ewwo4y0kr8.us-east-2.rds.amazonaws.com:5432/jobhunt"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Job(Base):
    __tablename__ = "jobs"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    job_id = Column(Integer, primary_key=True)
    company = Column(String)
    job_title = Column(String)
    job_description = Column(Text)
    role = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    job_id = Column(Integer, nullable=False)
    date_time = Column(DateTime)
    prep_tips = Column(Text)
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "job_id"],
            ["jobs.user_id", "jobs.job_id"],
            name="fk_jobs"
        ),
    )

Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class JobCreate(BaseModel):
    company: str
    job_title: str
    job_description: Optional[str] = None
    role: str

class InterviewCreate(BaseModel):
    job_id: int
    date_time: str  # Format: "YYYY-MM-DD HH:MM"

class JobResponse(BaseModel):
    user_id: int
    job_id: int
    company: str
    job_title: str
    job_description: Optional[str] = None
    role: str
    status: str
    created_at: datetime

class InterviewResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    date_time: datetime
    prep_tips: Optional[str] = None

# Endpoints
@app.post("/register")
async def register(user: UserCreate):
    db = SessionLocal()
    hashed = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(username=user.username, password_hash=hashed.decode('utf-8'))
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User registered", "user_id": db_user.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")
    finally:
        db.close()

@app.post("/login")
async def login(user: UserCreate):
    db = SessionLocal()
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password_hash.encode('utf-8')):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id = db_user.id
    db.close()
    return {"message": "Login successful", "user_id": user_id}

@app.post("/jobs")
async def add_job(job: JobCreate, user_id: int):
    db = SessionLocal()
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get next job_id for this user
        max_job_id = db.query(Job.job_id).filter(Job.user_id == user_id).order_by(Job.job_id.desc()).first()
        next_job_id = (max_job_id[0] + 1) if max_job_id else 1
        
        # Call Gemini API for status suggestion
        gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        headers = {"Content-Type": "application/json"}
        description = job.job_description if job.job_description else "No description provided"
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Suggest a status for a job application to {job.company} for the role {job.role} with job title {job.job_title}. Description: {description[:500]}. Return a single phrase."
                }]
            }]
        }
        try:
            response = requests.post(f"{gemini_url}?key=AIzaSyAwS2pI5NVj2LimwzuQS7ya8wWC6KBos6A", json=data, headers=headers, timeout=5)
            response.raise_for_status()
            status = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Applied").strip()
        except requests.RequestException as e:
            status = "Applied"  # Fallback status
        
        db_job = Job(
            user_id=user_id,
            job_id=next_job_id,
            company=job.company,
            job_title=job.job_title,
            job_description=job.job_description,
            role=job.role,
            status=status
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return {"message": "Job added", "status": status, "job_id": next_job_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add job: {str(e)}")
    finally:
        db.close()

@app.get("/jobs", response_model=list[JobResponse])
async def get_jobs(user_id: int):
    db = SessionLocal()
    try:
        jobs = db.query(Job).filter(Job.user_id == user_id).all()
        return jobs
    finally:
        db.close()

@app.post("/interviews")
async def add_interview(interview: InterviewCreate, user_id: int):
    db = SessionLocal()
    try:
        # Verify job exists
        job = db.query(Job).filter(Job.user_id == user_id, Job.job_id == interview.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        db_interview = Interview(
            user_id=user_id,
            job_id=interview.job_id,
            date_time=datetime.strptime(interview.date_time, "%Y-%m-%d %H:%M")
        )
        db.add(db_interview)
        db.commit()
        return {"message": "Interview scheduled"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to schedule interview: {str(e)}")
    finally:
        db.close()

@app.get("/interviews", response_model=list[InterviewResponse])
async def get_interviews(user_id: int):
    db = SessionLocal()
    try:
        interviews = db.query(Interview).filter(Interview.user_id == user_id).all()
        return interviews
    finally:
        db.close()

@app.get("/interview-prep/{job_id}")
async def get_interview_prep(user_id: int, job_id: int):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.user_id == user_id, Job.job_id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
        headers = {"Content-Type": "application/json"}
        description = job.job_description if job.job_description else "No description provided"
        data = {
            "contents": [{
                "parts": [{
                    "text": f"Provide interview preparation advice and 5 tailored interview questions for a {job.role} role with job title {job.job_title} at {job.company}. Job description: {description[:500]}. Format as: **Advice:**\n[Advice]\n**Questions:**\n- [Question 1]\n- [Question 2]\n- [Question 3]\n- [Question 4]\n- [Question 5]"
                }]
            }]
        }
        try:
            response = requests.post(f"{gemini_url}?key=AIzaSyAwS2pI5NVj2LimwzuQS7ya8wWC6KBos6A", json=data, headers=headers, timeout=5)
            response.raise_for_status()
            prep_content = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No prep available")
        except requests.RequestException:
            prep_content = "Unable to fetch prep content due to API error."
        return {"job_id": job_id, "prep_content": prep_content}
    finally:
        db.close()