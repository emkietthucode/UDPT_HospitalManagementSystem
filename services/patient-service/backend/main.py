from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from bson import ObjectId
import uvicorn
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/hospital_management")
DATABASE_NAME = "hospital_management"
COLLECTION_NAME = "patients"

# Insurance Service Configuration
INSURANCE_SERVICE_URL = os.getenv("INSURANCE_SERVICE_URL", "http://127.0.0.1:8002")

# Global variables for database
mongo_client: AsyncIOMotorClient = None
database = None

# Helper function to convert ObjectId to string
def str_object_id(v):
    return str(v) if isinstance(v, ObjectId) else v

# Insurance validation function
async def validate_insurance_card(card_number: str, date_of_birth: str):
    """
    Validate insurance card with Insurance Service
    Returns: (is_valid, card_info, error_message)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{INSURANCE_SERVICE_URL}/api/v1/insurance/validate",
                json={
                    "card_number": card_number,
                    "date_of_birth": date_of_birth
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("is_valid", False), data.get("card_info"), data.get("message", "")
            else:
                return False, None, f"Insurance service error: {response.status_code}"
                
    except httpx.RequestError as e:
        return False, None, f"Failed to connect to insurance service: {str(e)}"
    except Exception as e:
        return False, None, f"Insurance validation error: {str(e)}"

# Process insurance info for patient
async def process_insurance_info(patient_data: dict, date_of_birth: str):
    """
    Process and validate insurance information for a patient
    Updates the patient_data dict with validated insurance info
    """
    if not patient_data.get("insurance_info") or not patient_data["insurance_info"].get("card_number"):
        return True, None  # No insurance info provided, which is okay
    
    card_number = patient_data["insurance_info"]["card_number"]
    
    # Validate with insurance service
    is_valid, card_info, error_msg = await validate_insurance_card(
        card_number, date_of_birth
    )
    
    # Update insurance info
    insurance_info = patient_data["insurance_info"]
    insurance_info["is_validated"] = is_valid
    insurance_info["validation_date"] = datetime.utcnow()
    
    if is_valid and card_info:
        insurance_info["coverage_percentage"] = card_info.get("coverage_percentage")
        insurance_info["notes"] = f"Validated successfully. Hospital level: {card_info.get('hospital_level', 'N/A')}"
    else:
        insurance_info["notes"] = f"Validation failed: {error_msg}"
        # Note: We don't raise an error here since insurance is optional
        # Just log the validation failure
    
    return True, error_msg if not is_valid else None

# Pydantic Models
class InsuranceInfo(BaseModel):
    card_number: Optional[str] = None
    is_validated: bool = False
    validation_date: Optional[datetime] = None
    coverage_percentage: Optional[int] = None
    notes: Optional[str] = None

class PatientBase(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    insurance_info: Optional[InsuranceInfo] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    insurance_info: Optional[InsuranceInfo] = None

class InsuranceValidationRequest(BaseModel):
    patient_id: str
    card_number: str
    full_name: str
    date_of_birth: str

class PatientResponse(PatientBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    
    model_config = {"populate_by_name": True}

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

# Database startup and shutdown events
@app.on_event("startup")
async def startup_event():
    global mongo_client, database
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    database = mongo_client[DATABASE_NAME]
    
    # Create indexes for better performance
    await database[COLLECTION_NAME].create_indexes([
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("phone", ASCENDING)], unique=True),
        IndexModel([("full_name", ASCENDING)]),
    ])

@app.on_event("shutdown")
async def shutdown_event():
    if mongo_client:
        mongo_client.close()

# Database Dependency
async def get_db():
    return database

# Helper Functions
async def get_patient_by_id(db, patient_id: str):
    """Get patient by MongoDB ObjectId"""
    try:
        result = await db[COLLECTION_NAME].find_one({"_id": ObjectId(patient_id)})
        if result:
            result["_id"] = str(result["_id"])
        return result
    except Exception:
        return None

async def get_patients(
    db, 
    skip: int = 0, 
    limit: int = 100,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
):
    """Get patients with optional filters"""
    query = {}
    
    # Apply filters
    if name:
        query["full_name"] = {"$regex": name, "$options": "i"}
    if phone:
        query["phone"] = {"$regex": phone, "$options": "i"}
    if email:
        query["email"] = {"$regex": email, "$options": "i"}
    
    cursor = db[COLLECTION_NAME].find(query).skip(skip).limit(limit)
    patients = []
    async for patient in cursor:
        patient["_id"] = str(patient["_id"])
        patients.append(patient)
    
    return patients

async def create_patient(db, patient: PatientCreate):
    """Create a new patient"""
    # Check if email or phone already exists
    existing = await db[COLLECTION_NAME].find_one({
        "$or": [
            {"email": patient.email},
            {"phone": patient.phone}
        ]
    })
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Email or phone number already registered"
        )
    
    # Create patient document
    patient_dict = patient.model_dump()
    
    # Process insurance information if provided
    if patient_dict.get("insurance_info") and patient_dict["insurance_info"].get("card_number"):
        if not patient_dict.get("date_of_birth"):
            raise HTTPException(
                status_code=400,
                detail="Date of birth is required for insurance validation"
            )
        
        # Validate insurance card
        success, error_msg = await process_insurance_info(
            patient_dict, 
            patient_dict["date_of_birth"]
        )
        
        # If insurance validation fails, we still create the patient but with failed validation status
        # since insurance is optional
    
    patient_dict["created_at"] = datetime.utcnow()
    patient_dict["updated_at"] = datetime.utcnow()
    
    result = await db[COLLECTION_NAME].insert_one(patient_dict)
    
    # Return the created patient
    created_patient = await db[COLLECTION_NAME].find_one({"_id": result.inserted_id})
    created_patient["_id"] = str(created_patient["_id"])
    return created_patient

async def update_patient(db, patient_id: str, patient_update: PatientUpdate):
    """Update a patient"""
    # Check if patient exists
    existing_patient = await get_patient_by_id(db, patient_id)
    if not existing_patient:
        return None
    
    # Prepare update data
    update_data = patient_update.model_dump(exclude_unset=True)
    if not update_data:
        return existing_patient
    
    # Check for duplicate email/phone if being updated
    if 'email' in update_data or 'phone' in update_data:
        conflict_query = {"_id": {"$ne": ObjectId(patient_id)}}
        if 'email' in update_data:
            conflict_query["email"] = update_data['email']
        if 'phone' in update_data:
            conflict_query["phone"] = update_data['phone']
        
        conflict = await db[COLLECTION_NAME].find_one({
            "$and": [
                {"_id": {"$ne": ObjectId(patient_id)}},
                {"$or": [
                    {"email": update_data.get('email')} if 'email' in update_data else {},
                    {"phone": update_data.get('phone')} if 'phone' in update_data else {}
                ]}
            ]
        })
        
        if conflict:
            raise HTTPException(
                status_code=400,
                detail="Email or phone number already exists"
            )
    
    # Process insurance information if provided
    if 'insurance_info' in update_data and update_data['insurance_info'] and update_data['insurance_info'].get('card_number'):
        # Get date of birth for validation
        date_of_birth = update_data.get('date_of_birth', existing_patient.get('date_of_birth'))
        
        if not date_of_birth:
            raise HTTPException(
                status_code=400,
                detail="Date of birth is required for insurance validation"
            )
        
        # Create a copy for insurance processing
        temp_data = {"insurance_info": update_data['insurance_info']}
        
        # Validate insurance card
        success, error_msg = await process_insurance_info(
            temp_data,
            date_of_birth
        )
        
        # Update the insurance info in update_data
        update_data['insurance_info'] = temp_data['insurance_info']
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the patient
    await db[COLLECTION_NAME].update_one(
        {"_id": ObjectId(patient_id)},
        {"$set": update_data}
    )
    
    # Return the updated patient
    return await get_patient_by_id(db, patient_id)

async def delete_patient(db, patient_id: str):
    """Delete a patient"""
    try:
        result = await db[COLLECTION_NAME].delete_one({"_id": ObjectId(patient_id)})
        return result.deleted_count > 0
    except Exception:
        return False

async def get_patients_count(
    db,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
):
    """Get total count of patients matching filters"""
    query = {}
    
    if name:
        query["full_name"] = {"$regex": name, "$options": "i"}
    if phone:
        query["phone"] = {"$regex": phone, "$options": "i"}
    if email:
        query["email"] = {"$regex": email, "$options": "i"}
    
    count = await db[COLLECTION_NAME].count_documents(query)
    return count

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "patient-service"}

@app.post("/api/v1/patients", response_model=PatientResponse)
async def create_patient_endpoint(
    patient: PatientCreate, 
    db = Depends(get_db)
):
    """Create a new patient"""
    try:
        return await create_patient(db, patient)
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
    db = Depends(get_db)
):
    """Get patients with optional filters"""
    try:
        return await get_patients(db, skip, limit, name, phone, email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/patients/{patient_id}", response_model=PatientResponse)
async def get_patient_endpoint(
    patient_id: str, 
    db = Depends(get_db)
):
    """Get a specific patient by ID"""
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/api/v1/patients/{patient_id}", response_model=PatientResponse)
async def update_patient_endpoint(
    patient_id: str,
    patient_update: PatientUpdate,
    db = Depends(get_db)
):
    """Update a patient"""
    try:
        updated_patient = await update_patient(db, patient_id, patient_update)
        if not updated_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return updated_patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/patients/{patient_id}")
async def delete_patient_endpoint(
    patient_id: str, 
    db = Depends(get_db)
):
    """Delete a patient"""
    try:
        if await delete_patient(db, patient_id):
            return {"message": "Patient deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Patient not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/patients/search/count")
async def get_patients_count_endpoint(
    name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db = Depends(get_db)
):
    """Get total count of patients matching filters"""
    try:
        count = await get_patients_count(db, name, phone, email)
        return {"total": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/patients/{patient_id}/validate-insurance")
async def validate_patient_insurance(
    patient_id: str,
    request: InsuranceValidationRequest,
    db = Depends(get_db)
):
    """Validate patient's insurance card with Insurance Service"""
    try:
        # Get patient info
        patient = await get_patient_by_id(db, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Call Insurance Service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{INSURANCE_SERVICE_URL}/api/v1/insurance/validate",
                    json={
                        "card_number": request.card_number,
                        "full_name": request.full_name,
                        "date_of_birth": request.date_of_birth
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    validation_result = response.json()
                    
                    # Update patient's insurance info
                    insurance_info = {
                        "card_number": request.card_number,
                        "is_validated": validation_result["is_valid"],
                        "validation_date": datetime.now(),
                        "coverage_percentage": validation_result.get("coverage_percentage"),
                        "notes": validation_result["message"]
                    }
                    
                    # Update patient record
                    await db[COLLECTION_NAME].update_one(
                        {"_id": ObjectId(patient_id)},
                        {"$set": {"insurance_info": insurance_info}}
                    )
                    
                    return {
                        "message": "Insurance validation completed",
                        "validation_result": validation_result,
                        "patient_updated": True
                    }
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Insurance service error"
                    )
                    
            except httpx.RequestError:
                raise HTTPException(
                    status_code=503,
                    detail="Insurance service unavailable"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)