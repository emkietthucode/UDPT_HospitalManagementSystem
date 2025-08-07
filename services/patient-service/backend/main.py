from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uvicorn

# Database Configuration
DATABASE_URL = "sqlite:///./patients.db"  # Sử dụng SQLite cho demo
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=False, index=True)
    address = Column(String(200), nullable=True)
    date_of_birth = Column(String(10), nullable=True)  # Format: YYYY-MM-DD
    gender = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class PatientBase(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# FastAPI App
app = FastAPI(
    title="Patient Management Service",
    description="Microservice for managing patient information",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper Functions
def get_patient_by_id(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_patients(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
):
    query = db.query(Patient)
    
    # Apply filters
    if name:
        query = query.filter(Patient.full_name.ilike(f"%{name}%"))
    if phone:
        query = query.filter(Patient.phone.ilike(f"%{phone}%"))
    if email:
        query = query.filter(Patient.email.ilike(f"%{email}%"))
    
    return query.offset(skip).limit(limit).all()

def create_patient(db: Session, patient: PatientCreate):
    # Check if email or phone already exists
    existing = db.query(Patient).filter(
        (Patient.email == patient.email) | (Patient.phone == patient.phone)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Email or phone number already registered"
        )
    
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient_update: PatientUpdate):
    db_patient = get_patient_by_id(db, patient_id)
    if not db_patient:
        return None
    
    # Update only provided fields
    update_data = patient_update.dict(exclude_unset=True)
    
    # Check for duplicate email/phone if being updated
    if 'email' in update_data or 'phone' in update_data:
        query = db.query(Patient).filter(Patient.id != patient_id)
        if 'email' in update_data:
            query = query.filter(Patient.email == update_data['email'])
        if 'phone' in update_data:
            query = query.filter(Patient.phone == update_data['phone'])
        
        if query.first():
            raise HTTPException(
                status_code=400,
                detail="Email or phone number already exists"
            )
    
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db_patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = get_patient_by_id(db, patient_id)
    if db_patient:
        db.delete(db_patient)
        db.commit()
        return True
    return False

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "patient-service"}

@app.post("/api/v1/patients", response_model=PatientResponse)
async def create_patient_endpoint(
    patient: PatientCreate, 
    db: Session = Depends(get_db)
):
    print('[BE-log] Tạo patient:')
    """Create a new patient"""
    try:
        return create_patient(db, patient)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/patients", response_model=List[PatientResponse])
async def get_patients_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    name: Optional[str] = Query(None, description="Filter by patient name"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    email: Optional[str] = Query(None, description="Filter by email"),
    db: Session = Depends(get_db)
):
    """Get patients with optional filters"""
    try:
        return get_patients(db, skip, limit, name, phone, email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/patients/{patient_id}", response_model=PatientResponse)
async def get_patient_endpoint(
    patient_id: int, 
    db: Session = Depends(get_db)
):
    """Get a specific patient by ID"""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/api/v1/patients/{patient_id}", response_model=PatientResponse)
async def update_patient_endpoint(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    """Update a patient"""
    try:
        updated_patient = update_patient(db, patient_id, patient_update)
        if not updated_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return updated_patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/patients/{patient_id}")
async def delete_patient_endpoint(
    patient_id: int, 
    db: Session = Depends(get_db)
):
    """Delete a patient"""
    try:
        if delete_patient(db, patient_id):
            return {"message": "Patient deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Patient not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/patients/search/count")
async def get_patients_count(
    name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get total count of patients matching filters"""
    try:
        query = db.query(Patient)
        
        if name:
            query = query.filter(Patient.full_name.ilike(f"%{name}%"))
        if phone:
            query = query.filter(Patient.phone.ilike(f"%{phone}%"))
        if email:
            query = query.filter(Patient.email.ilike(f"%{email}%"))
        
        count = query.count()
        return {"total": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)