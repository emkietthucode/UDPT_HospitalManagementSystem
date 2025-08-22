from fastapi import FastAPI, HTTPException, Depends, Query, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime, date, timedelta
from bson import ObjectId
import uvicorn
import os
import httpx
from dotenv import load_dotenv
from urllib.parse import urlparse
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/hospital_management")
# Extract database name from URL if present, fallback to default
_parsed = urlparse(MONGODB_URL)
_db_path = _parsed.path.lstrip('/') if _parsed and _parsed.path else ""
DATABASE_NAME = _db_path or "hospital_management"
COLLECTION_NAME = "patients"
USERS_COLLECTION_NAME = "users"

# New collections for drug catalog, prescriptions, and CLS
DRUGS_COLLECTION = "drugs"
PRESCRIPTIONS_COLLECTION = "prescriptions"
CLS_ORDERS_COLLECTION = "service_orders"
CLS_RESULTS_COLLECTION = "service_results"

# Insurance Service Configuration
INSURANCE_SERVICE_URL = os.getenv("INSURANCE_SERVICE_URL", "http://127.0.0.1:8002")

# Authentication Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

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

# Authentication Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_email(db, email: str):
    """Get user by email from database"""
    try:
        user = await db[USERS_COLLECTION_NAME].find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception:
        return None

async def authenticate_user(db, email: str, password: str):
    """Authenticate user with email and password"""
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(lambda: database)
):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(allowed_roles: List[str]):
    """Role-based access control decorator"""
    def role_checker(current_user: dict = Depends(get_current_active_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

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

# -----------------------------
# Drug (Thuốc) Models
# -----------------------------

class DrugBase(BaseModel):
    drug_code: str = Field(..., description="Mã thuốc duy nhất của bệnh viện")
    drug_name: str = Field(..., description="Tên thuốc")
    dosage_form: Optional[str] = Field(None, description="Dạng bào chế, ví dụ: viên, ống, gói")
    strength: Optional[str] = Field(None, description="Hàm lượng, ví dụ: 500mg, 5mg/ml")
    unit: Optional[str] = Field(None, description="Đơn vị tính, ví dụ: viên, hộp")
    route: Optional[str] = Field(None, description="Đường dùng, ví dụ: uống, tiêm, nhỏ")
    price: Optional[float] = Field(None, ge=0, description="Đơn giá hiện hành")
    is_active: bool = Field(default=True, description="Trạng thái đang sử dụng")

class DrugCreate(DrugBase):
    pass

class DrugUpdate(BaseModel):
    drug_name: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    unit: Optional[str] = None
    route: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None

class DrugResponse(DrugBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}

# --------------------------------------
# Prescription (Đơn thuốc) Models
# --------------------------------------

class PrescriptionItem(BaseModel):
    drug_id: str = Field(..., description="ID thuốc (Mongo ObjectId dạng string)")
    quantity: float = Field(..., gt=0, description="Số lượng")
    dosage: Optional[str] = Field(None, description="Liều lượng, ví dụ: 500mg")
    frequency: Optional[str] = Field(None, description="Tần suất dùng, ví dụ: 2 lần/ngày")
    route: Optional[str] = Field(None, description="Đường dùng, ví dụ: uống")
    instructions: Optional[str] = Field(None, description="Cách dùng chi tiết")

class PrescriptionBase(BaseModel):
    patient_id: str = Field(..., description="ID bệnh nhân (Mongo ObjectId dạng string)")
    doctor_id: str = Field(..., description="ID bác sĩ (Mongo ObjectId dạng string hoặc mã nhân viên)")
    diagnosis: Optional[str] = Field(None, description="Chẩn đoán")
    notes: Optional[str] = Field(None, description="Ghi chú bổ sung")
    status: Literal["draft", "issued", "dispensed", "canceled"] = Field(
        default="draft", description="Trạng thái đơn thuốc"
    )
    items: List[PrescriptionItem] = Field(default_factory=list, description="Danh sách thuốc trong đơn")

class PrescriptionCreate(PrescriptionBase):
    prescribed_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.utcnow(), description="Ngày kê đơn"
    )

class PrescriptionUpdate(BaseModel):
    doctor_id: Optional[str] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[Literal["draft", "issued", "dispensed", "canceled"]] = None
    items: Optional[List[PrescriptionItem]] = None

class PrescriptionResponse(PrescriptionBase):
    id: str = Field(alias="_id")
    prescribed_date: datetime
    total_cost: Optional[float] = Field(None, ge=0)
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}

class PrescriptionStatusUpdate(BaseModel):
    status: Literal["draft", "issued", "dispensed", "canceled"]

# --------------------------------------
# CLS (Cận lâm sàng) Models
# --------------------------------------

class ServiceOrderItem(BaseModel):
    service_code: str = Field(..., description="Mã dịch vụ CLS, ví dụ: XQ-01, CT-HEAD")
    service_name: str = Field(..., description="Tên dịch vụ, ví dụ: X-quang phổi")
    notes: Optional[str] = Field(None, description="Ghi chú chỉ định")

class ServiceOrderCreate(BaseModel):
    patient_id: str = Field(..., description="ID bệnh nhân")
    doctor_id: str = Field(..., description="ID bác sĩ")
    order_date: Optional[datetime] = Field(default_factory=lambda: datetime.utcnow())
    priority: Optional[Literal["normal", "urgent"]] = Field(default="normal")
    items: List[ServiceOrderItem] = Field(default_factory=list)
    status: Literal["ordered", "in_progress", "completed", "canceled"] = Field(default="ordered")
    notes: Optional[str] = None

class ServiceOrderUpdate(BaseModel):
    priority: Optional[Literal["normal", "urgent"]] = None
    items: Optional[List[ServiceOrderItem]] = None
    status: Optional[Literal["ordered", "in_progress", "completed", "canceled"]] = None
    notes: Optional[str] = None

class ServiceOrderResponse(ServiceOrderCreate):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}

class ServiceResultText(BaseModel):
    parameter: str = Field(..., description="Tên chỉ số: Hb, WBC, ...")
    value: str = Field(..., description="Giá trị")
    unit: Optional[str] = Field(None, description="Đơn vị")
    reference_range: Optional[str] = Field(None, description="Khoảng tham chiếu")

class ServiceResultCreate(BaseModel):
    order_id: str = Field(..., description="ID phiếu chỉ định (ServiceOrder)")
    result_date: Optional[datetime] = Field(default_factory=lambda: datetime.utcnow())
    modality: Optional[str] = Field(None, description="Loại máy/phương pháp: X-ray, CT, MRI, Lab")
    text_results: List[ServiceResultText] = Field(default_factory=list, description="Các chỉ số dạng text")
    attachments: Optional[List[str]] = Field(default_factory=list, description="Danh sách URL file (mở rộng)")
    conclusion: Optional[str] = Field(None, description="Kết luận")

class ServiceResultUpdate(BaseModel):
    text_results: Optional[List[ServiceResultText]] = None
    attachments: Optional[List[str]] = None
    conclusion: Optional[str] = None

class ServiceResultResponse(ServiceResultCreate):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}
# Authentication Models
class UserRole:
    PATIENT = "patient"
    DOCTOR = "doctor"
    RECEPTIONIST = "receptionist"
    TECHNICIAN = "technician"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = Field(..., description="User role: patient, doctor, or receptionist")
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    
    model_config = {"populate_by_name": True}

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

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
    # Set a short timeout to avoid hanging the service if MongoDB is down
    timeout_ms = int(os.getenv("MONGODB_TIMEOUT_MS", "2000"))
    mongo_client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=timeout_ms)
    database = mongo_client[DATABASE_NAME]

    # Try ping to ensure connection is available; do not block startup if unavailable
    try:
        await database.command({"ping": 1})
    except Exception as e:
        print(f"[startup] MongoDB ping failed: {e}. Service will start and retry on demand.")

    # Best-effort index creation; do not fail startup if Mongo is not reachable
    try:
        # Patients collection indexes
        await database[COLLECTION_NAME].create_indexes([
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("phone", ASCENDING)], unique=True),
            IndexModel([("full_name", ASCENDING)]),
        ])

        # Users collection indexes
        await database[USERS_COLLECTION_NAME].create_indexes([
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("role", ASCENDING)]),
        ])

        # Drug catalog indexes
        await database[DRUGS_COLLECTION].create_indexes([
            IndexModel([("drug_code", ASCENDING)], unique=True),
            IndexModel([("drug_name", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)])
        ])

        # Prescriptions indexes
        await database[PRESCRIPTIONS_COLLECTION].create_indexes([
            IndexModel([("patient_id", ASCENDING)]),
            IndexModel([("doctor_id", ASCENDING)]),
            IndexModel([("prescribed_date", ASCENDING)]),
            IndexModel([("status", ASCENDING)])
        ])

        # CLS: Service Orders indexes
        await database[CLS_ORDERS_COLLECTION].create_indexes([
            IndexModel([("patient_id", ASCENDING)]),
            IndexModel([("doctor_id", ASCENDING)]),
            IndexModel([("order_date", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
        ])

        # CLS: Service Results indexes
        await database[CLS_RESULTS_COLLECTION].create_indexes([
            IndexModel([("order_id", ASCENDING)]),
            IndexModel([("result_date", ASCENDING)]),
        ])
    except Exception as e:
        print(f"[startup] Index creation skipped due to MongoDB error: {e}")

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

def try_parse_object_id(id_str: str) -> Optional[ObjectId]:
    """Safely parse a string to MongoDB ObjectId, return None if invalid"""
    try:
        return ObjectId(id_str)
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

# --------------------------------------
# Prescription helpers and creation logic
# --------------------------------------

async def get_drug_by_id(db, drug_id: str):
    """Get a drug by id (only active)"""
    object_id = try_parse_object_id(drug_id)
    if object_id is None:
        return None
    drug = await db[DRUGS_COLLECTION].find_one({"_id": object_id, "is_active": True})
    return drug

def serialize_prescription(doc: dict) -> dict:
    """Serialize prescription document to API response format"""
    result = doc.copy()
    result["_id"] = str(result["_id"]) if isinstance(result.get("_id"), ObjectId) else result.get("_id")
    # patient_id may be stored as ObjectId
    if isinstance(result.get("patient_id"), ObjectId):
        result["patient_id"] = str(result["patient_id"])
    # Normalize items drug_id to string
    items = []
    for item in result.get("items", []):
        item_copy = item.copy()
        if isinstance(item_copy.get("drug_id"), ObjectId):
            item_copy["drug_id"] = str(item_copy["drug_id"])
        items.append(item_copy)
    result["items"] = items
    return result

# Helper to serialize drug documents
def serialize_drug(doc: dict) -> dict:
    result = doc.copy()
    if isinstance(result.get("_id"), ObjectId):
        result["_id"] = str(result["_id"])
    return result

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "patient-service"}

@app.get("/db/health")
async def db_health_check():
    """Check MongoDB connectivity and database name"""
    try:
        await database.command({"ping": 1})
        return {"ok": True, "database": DATABASE_NAME}
    except Exception as e:
        return {"ok": False, "database": DATABASE_NAME, "error": str(e)}

# Authentication Endpoints

@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    if user.role not in [UserRole.PATIENT, UserRole.DOCTOR, UserRole.RECEPTIONIST, UserRole.TECHNICIAN]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: patient, doctor, or receptionist"
        )
    
    # Create user document
    user_data = {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "hashed_password": get_password_hash(user.password),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    try:
        result = await db[USERS_COLLECTION_NAME].insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return UserResponse(**user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db = Depends(get_db)):
    """Login user and return JWT token"""
    user = await authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(**current_user)

# Patient Endpoints (Protected)

@app.post("/api/v1/patients", response_model=PatientResponse)
async def create_patient_endpoint(
    patient: PatientCreate, 
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))
):
    """Create a new patient (Receptionist and Doctor only)"""
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
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))
):
    """Get patients with optional filters (Receptionist and Doctor only)"""
    try:
        return await get_patients(db, skip, limit, name, phone, email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/patients/{patient_id}", response_model=PatientResponse)
async def get_patient_endpoint(
    patient_id: str, 
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific patient by ID (All authenticated users can view)"""
    patient = await get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/api/v1/patients/{patient_id}", response_model=PatientResponse)
async def update_patient_endpoint(
    patient_id: str,
    patient_update: PatientUpdate,
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))
):
    """Update a patient (Receptionist and Doctor only)"""
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
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.RECEPTIONIST]))
):
    """Delete a patient (Receptionist only)"""
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
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))
):
    """Get total count of patients matching filters (Receptionist and Doctor only)"""
    try:
        count = await get_patients_count(db, name, phone, email)
        return {"total": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/patients/{patient_id}/validate-insurance")
async def validate_patient_insurance(
    patient_id: str,
    request: InsuranceValidationRequest,
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))
):
    """Validate patient's insurance card with Insurance Service (Receptionist and Doctor only)"""
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

# ---------------------------------------------------------
# New Endpoint: Create Prescription (POST /api/v1/prescriptions)
# ---------------------------------------------------------

@app.post("/api/v1/prescriptions", response_model=PrescriptionResponse)
async def create_prescription_endpoint(prescription: PrescriptionCreate, db = Depends(get_db)):
    """Create an electronic prescription after examination
    Steps:
    - Validate patient exists
    - Validate each drug item exists and is active
    - Compute total cost (sum of item.quantity * drug.price if price exists)
    - Save prescription with timestamps
    """
    # Validate patient id
    patient = await get_patient_by_id(db, prescription.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Validate items and compute total cost
    total_cost = 0.0
    normalized_items = []
    for idx, item in enumerate(prescription.items or []):
        drug_doc = await get_drug_by_id(db, item.drug_id)
        if not drug_doc:
            raise HTTPException(status_code=400, detail=f"Drug not found or inactive at item #{idx+1}")

        price = float(drug_doc.get("price", 0) or 0)
        line_cost = price * float(item.quantity)
        total_cost += line_cost

        normalized_items.append({
            "drug_id": ObjectId(item.drug_id),
            "quantity": float(item.quantity),
            "dosage": item.dosage,
            "frequency": item.frequency,
            "route": item.route or drug_doc.get("route"),
            "instructions": item.instructions,
            "unit_price": price,
            "line_cost": line_cost,
            "drug_snapshot": {
                "drug_code": drug_doc.get("drug_code"),
                "drug_name": drug_doc.get("drug_name"),
                "strength": drug_doc.get("strength"),
                "dosage_form": drug_doc.get("dosage_form"),
                "unit": drug_doc.get("unit")
            }
        })

    now = datetime.utcnow()
    doc = {
        "patient_id": ObjectId(prescription.patient_id),
        "doctor_id": prescription.doctor_id,
        "diagnosis": prescription.diagnosis,
        "notes": prescription.notes,
        "status": prescription.status,
        "items": normalized_items,
        "prescribed_date": prescription.prescribed_date or now,
        "total_cost": round(total_cost, 2),
        "created_at": now,
        "updated_at": now,
    }

    result = await db[PRESCRIPTIONS_COLLECTION].insert_one(doc)
    created = await db[PRESCRIPTIONS_COLLECTION].find_one({"_id": result.inserted_id})
    created_serialized = serialize_prescription(created)
    # Align with response model keys
    created_serialized["_id"] = str(created_serialized["_id"])  # ensure string
    return created_serialized

# ---------------------------------------------------------
# New Endpoint: List Prescriptions by Status (GET)
# ---------------------------------------------------------

@app.get("/api/v1/prescriptions", response_model=List[PrescriptionResponse])
async def list_prescriptions(
    status: Optional[Literal["draft", "issued", "dispensed", "canceled"]] = Query(None, description="Lọc theo trạng thái đơn thuốc"),
    patient_id: Optional[str] = Query(None, description="Lọc theo ID bệnh nhân"),
    doctor_id: Optional[str] = Query(None, description="Lọc theo ID bác sĩ"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db = Depends(get_db)
):
    """List prescriptions for pharmacist view with optional filters by status/patient/doctor"""
    query: dict = {}
    if status:
        query["status"] = status
    if patient_id:
        oid = try_parse_object_id(patient_id)
        if oid is None:
            raise HTTPException(status_code=400, detail="Invalid patient_id")
        query["patient_id"] = oid
    if doctor_id:
        query["doctor_id"] = doctor_id

    cursor = db[PRESCRIPTIONS_COLLECTION].find(query).sort("prescribed_date", -1).skip(skip).limit(limit)
    results: List[dict] = []
    async for doc in cursor:
        results.append(serialize_prescription(doc))
    return results

@app.get("/api/v1/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription_detail(prescription_id: str, db = Depends(get_db)):
    """Get details of a specific prescription for doctor/pharmacist/patient view"""
    oid = try_parse_object_id(prescription_id)
    if oid is None:
        raise HTTPException(status_code=400, detail="Invalid prescription id")

    doc = await db[PRESCRIPTIONS_COLLECTION].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return serialize_prescription(doc)

@app.put("/api/v1/prescriptions/{prescription_id}/status", response_model=PrescriptionResponse)
async def update_prescription_status(
    prescription_id: str,
    body: PrescriptionStatusUpdate,
    db = Depends(get_db)
):
    """Update prescription status (for pharmacist)
    Valid transitions (simple policy):
    - draft -> issued | canceled
    - issued -> dispensed | canceled
    - dispensed -> (no further transitions)
    - canceled -> (no further transitions)
    """
    oid = try_parse_object_id(prescription_id)
    if oid is None:
        raise HTTPException(status_code=400, detail="Invalid prescription id")

    current = await db[PRESCRIPTIONS_COLLECTION].find_one({"_id": oid})
    if not current:
        raise HTTPException(status_code=404, detail="Prescription not found")

    current_status = current.get("status", "draft")
    target_status = body.status

    allowed: dict = {
        "draft": {"issued", "canceled"},
        "issued": {"dispensed", "canceled"},
        "dispensed": set(),
        "canceled": set(),
    }

    if target_status == current_status:
        return serialize_prescription(current)

    if target_status not in allowed.get(current_status, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {current_status} -> {target_status}"
        )

    now = datetime.utcnow()
    await db[PRESCRIPTIONS_COLLECTION].update_one(
        {"_id": oid},
        {"$set": {"status": target_status, "updated_at": now}}
    )

    updated = await db[PRESCRIPTIONS_COLLECTION].find_one({"_id": oid})
    return serialize_prescription(updated)

# -----------------------------
# Drug CRUD Endpoints
# -----------------------------

@app.get("/api/v1/drugs")
async def list_drugs(
    name: Optional[str] = Query(None, description="Lọc theo tên thuốc"),
    code: Optional[str] = Query(None, description="Lọc theo mã thuốc"),
    active: Optional[bool] = Query(None, description="Lọc trạng thái hoạt động"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))
):
    query: dict = {}
    if name:
        query["drug_name"] = {"$regex": name, "$options": "i"}
    if code:
        query["drug_code"] = {"$regex": code, "$options": "i"}
    if active is not None:
        query["is_active"] = active

    cursor = db[DRUGS_COLLECTION].find(query).sort("drug_name", 1).skip(skip).limit(limit)
    results: List[dict] = []
    async for doc in cursor:
        results.append(serialize_drug(doc))
    return results

@app.get("/api/v1/drugs/{drug_id}")
async def get_drug(drug_id: str, db = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    oid = try_parse_object_id(drug_id)
    if oid is None:
        raise HTTPException(status_code=400, detail="Invalid drug id")
    doc = await db[DRUGS_COLLECTION].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Drug not found")
    return serialize_drug(doc)

@app.post("/api/v1/drugs")
async def create_drug(body: DrugCreate, db = Depends(get_db), current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))):
    exists = await db[DRUGS_COLLECTION].find_one({"drug_code": body.drug_code})
    if exists:
        raise HTTPException(status_code=400, detail="Drug code already exists")
    now = datetime.utcnow()
    doc = body.model_dump()
    doc["created_at"], doc["updated_at"] = now, now
    result = await db[DRUGS_COLLECTION].insert_one(doc)
    created = await db[DRUGS_COLLECTION].find_one({"_id": result.inserted_id})
    return serialize_drug(created)

@app.put("/api/v1/drugs/{drug_id}")
async def update_drug(drug_id: str, body: DrugUpdate, db = Depends(get_db), current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))):
    oid = try_parse_object_id(drug_id)
    if oid is None:
        raise HTTPException(status_code=400, detail="Invalid drug id")
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        doc = await db[DRUGS_COLLECTION].find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=404, detail="Drug not found")
        return serialize_drug(doc)
    if "drug_code" in update_data:
        conflict = await db[DRUGS_COLLECTION].find_one({"drug_code": update_data["drug_code"], "_id": {"$ne": oid}})
        if conflict:
            raise HTTPException(status_code=400, detail="Drug code already exists")
    update_data["updated_at"] = datetime.utcnow()
    await db[DRUGS_COLLECTION].update_one({"_id": oid}, {"$set": update_data})
    updated = await db[DRUGS_COLLECTION].find_one({"_id": oid})
    if not updated:
        raise HTTPException(status_code=404, detail="Drug not found")
    return serialize_drug(updated)

# --------------------------------------
# CLS Endpoints
# --------------------------------------

def serialize_order(doc: dict) -> dict:
    r = doc.copy()
    if isinstance(r.get("_id"), ObjectId):
        r["_id"] = str(r["_id"])
    if isinstance(r.get("patient_id"), ObjectId):
        r["patient_id"] = str(r["patient_id"])
    return r

def serialize_result(doc: dict) -> dict:
    r = doc.copy()
    if isinstance(r.get("_id"), ObjectId):
        r["_id"] = str(r["_id"])
    if isinstance(r.get("order_id"), ObjectId):
        r["order_id"] = str(r["order_id"])
    return r

@app.post("/api/v1/cls/orders", response_model=ServiceOrderResponse)
async def create_service_order(order: ServiceOrderCreate, db = Depends(get_db), current_user: dict = Depends(require_role([UserRole.DOCTOR]))):
    # Ensure patient exists
    patient = await get_patient_by_id(db, order.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    now = datetime.utcnow()
    doc = order.model_dump()
    doc["patient_id"] = ObjectId(order.patient_id)
    doc["created_at"] = now
    doc["updated_at"] = now
    result = await db[CLS_ORDERS_COLLECTION].insert_one(doc)
    created = await db[CLS_ORDERS_COLLECTION].find_one({"_id": result.inserted_id})
    return serialize_order(created)

@app.get("/api/v1/cls/orders", response_model=List[ServiceOrderResponse])
async def list_service_orders(
    patient_id: Optional[str] = Query(None),
    doctor_id: Optional[str] = Query(None),
    status: Optional[Literal["ordered", "in_progress", "completed", "canceled"]] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    query: dict = {}
    if patient_id:
        oid = try_parse_object_id(patient_id)
        if oid is None:
            raise HTTPException(status_code=400, detail="Invalid patient_id")
        query["patient_id"] = oid
    if doctor_id:
        query["doctor_id"] = doctor_id
    if status:
        query["status"] = status
    cursor = db[CLS_ORDERS_COLLECTION].find(query).sort("order_date", -1).skip(skip).limit(limit)
    results: List[dict] = []
    async for doc in cursor:
        results.append(serialize_order(doc))
    return results

@app.put("/api/v1/cls/orders/{order_id}", response_model=ServiceOrderResponse)
async def update_service_order(order_id: str, body: ServiceOrderUpdate, db = Depends(get_db), current_user: dict = Depends(require_role([UserRole.DOCTOR]))):
    oid = try_parse_object_id(order_id)
    if oid is None:
        raise HTTPException(status_code=400, detail="Invalid order id")
    data = body.model_dump(exclude_unset=True)
    data["updated_at"] = datetime.utcnow()
    await db[CLS_ORDERS_COLLECTION].update_one({"_id": oid}, {"$set": data})
    updated = await db[CLS_ORDERS_COLLECTION].find_one({"_id": oid})
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_order(updated)

@app.post("/api/v1/cls/results", response_model=ServiceResultResponse)
async def create_service_result(result: ServiceResultCreate, db = Depends(get_db), current_user: dict = Depends(require_role([UserRole.DOCTOR]))):
    oid = try_parse_object_id(result.order_id)
    if oid is None:
        raise HTTPException(status_code=400, detail="Invalid order id")
    order = await db[CLS_ORDERS_COLLECTION].find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    now = datetime.utcnow()
    doc = result.model_dump()
    doc["order_id"] = oid
    doc["created_at"], doc["updated_at"] = now, now
    ins = await db[CLS_RESULTS_COLLECTION].insert_one(doc)
    created = await db[CLS_RESULTS_COLLECTION].find_one({"_id": ins.inserted_id})
    # Auto mark order completed if not already
    await db[CLS_ORDERS_COLLECTION].update_one({"_id": oid}, {"$set": {"status": "completed", "updated_at": datetime.utcnow()}})
    return serialize_result(created)

@app.get("/api/v1/cls/results", response_model=List[ServiceResultResponse])
async def list_service_results(order_id: Optional[str] = Query(None), patient_id: Optional[str] = Query(None), db = Depends(get_db), current_user: dict = Depends(get_current_active_user)):
    query: dict = {}
    if order_id:
        oid = try_parse_object_id(order_id)
        if oid is None:
            raise HTTPException(status_code=400, detail="Invalid order id")
        query["order_id"] = oid
    if patient_id:
        poid = try_parse_object_id(patient_id)
        if poid is None:
            raise HTTPException(status_code=400, detail="Invalid patient id")
        # Join-like by first finding orders
        order_ids: List[ObjectId] = []
        cursor = db[CLS_ORDERS_COLLECTION].find({"patient_id": poid}, {"_id": 1})
        async for o in cursor:
            order_ids.append(o["_id"])
        if not order_ids:
            return []
        query["order_id"] = {"$in": order_ids}
    cursor = db[CLS_RESULTS_COLLECTION].find(query).sort("result_date", -1)
    results: List[dict] = []
    async for doc in cursor:
        results.append(serialize_result(doc))
    return results

# --------------------------------------
# LAB Orders listing for technicians
# --------------------------------------

def _map_public_status_to_internal(status: str) -> Optional[str]:
    mapping = {
        "waiting": "ordered",
        "in_progress": "in_progress",
        "completed": "completed",
    }
    return mapping.get(status)

def _build_test_type_filter(test_type: str) -> Optional[dict]:
    # Heuristics by service_code or service_name
    if test_type == "hematology":
        regex = {"$regex": "^(LAB-)?(CBC|HEM|HB|WBC)|(huyet|huyết|CBC|bạch cầu|hồng cầu)", "$options": "i"}
        return {"$or": [{"service_code": regex}, {"service_name": regex}]}
    if test_type == "biochemistry":
        regex = {"$regex": "^(LAB-)?(BIO|GLU|AST|ALT|CHO|UREA)|(sinh hoa|sinh hóa|glucose|AST|ALT)", "$options": "i"}
        return {"$or": [{"service_code": regex}, {"service_name": regex}]}
    if test_type == "imaging":
        regex = {"$regex": "^(XQ|CT|MRI|USG)|(x-quang|chup|siêu âm|ct|mri)", "$options": "i"}
        return {"$or": [{"service_code": regex}, {"service_name": regex}]}
    return None

@app.get("/lab/orders", response_model=List[ServiceOrderResponse])
async def list_lab_orders(
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD hoặc ISO date"),
    date_to: Optional[str] = Query(None, description="YYYY-MM-DD hoặc ISO date"),
    status: Optional[Literal["waiting", "in_progress", "completed"]] = Query(None),
    test_type: Optional[Literal["hematology", "biochemistry", "imaging"]] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.TECHNICIAN, UserRole.DOCTOR]))
):
    query: dict = {}

    # Date filters on order_date
    def _parse_date(s: str) -> Optional[datetime]:
        try:
            # Try date-only first
            return datetime.fromisoformat(s)
        except Exception:
            try:
                return datetime.strptime(s, "%Y-%m-%d")
            except Exception:
                return None

    if date_from:
        df = _parse_date(date_from)
        if df:
            query.setdefault("order_date", {})["$gte"] = df
        else:
            raise HTTPException(status_code=400, detail="Invalid date_from format")
    if date_to:
        dt_ = _parse_date(date_to)
        if dt_:
            query.setdefault("order_date", {})["$lte"] = dt_
        else:
            raise HTTPException(status_code=400, detail="Invalid date_to format")

    # Status mapping
    if status:
        internal = _map_public_status_to_internal(status)
        if not internal:
            raise HTTPException(status_code=400, detail="Invalid status")
        query["status"] = internal

    # Test type filter via $elemMatch on items
    if test_type:
        item_filter = _build_test_type_filter(test_type)
        if not item_filter:
            raise HTTPException(status_code=400, detail="Invalid test_type")
        query["items"] = {"$elemMatch": item_filter}

    cursor = db[CLS_ORDERS_COLLECTION].find(query).sort("order_date", -1).skip(skip).limit(limit)
    results: List[dict] = []
    async for doc in cursor:
        results.append(serialize_order(doc))
    return results

@app.post("/lab/orders/{order_id}/results", response_model=ServiceResultResponse)
async def upload_lab_results(
    order_id: str,
    modality: Optional[str] = Form(None),
    conclusion: Optional[str] = Form(None),
    text_results: Optional[str] = Form(None, description="JSON list of text results"),
    files: Optional[List[UploadFile]] = File(None),
    db = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.TECHNICIAN, UserRole.DOCTOR]))
):
    oid = try_parse_object_id(order_id)
    if oid is None:
        raise HTTPException(status_code=400, detail="Invalid order id")

    order = await db[CLS_ORDERS_COLLECTION].find_one({"_id": oid})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Parse text_results JSON if provided
    parsed_text_results: List[dict] = []
    if text_results:
        try:
            import json
            data = json.loads(text_results)
            if isinstance(data, list):
                parsed_text_results = data
            else:
                raise ValueError("text_results must be a JSON array")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid text_results JSON: {e}")

    # Save uploaded files
    saved_paths: List[str] = []
    if files:
        upload_root = os.getenv("UPLOAD_ROOT", "uploads")
        dest_dir = os.path.join(upload_root, "cls", str(order_id))
        os.makedirs(dest_dir, exist_ok=True)

        for f in files:
            try:
                original_name = f.filename or "file"
                safe_name = original_name.replace("..", "").replace("/", "_").replace("\\", "_")
                unique_name = f"{int(datetime.utcnow().timestamp()*1000)}_{safe_name}"
                dest_path = os.path.join(dest_dir, unique_name)
                with open(dest_path, "wb") as out:
                    out.write(await f.read())
                saved_paths.append(dest_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed saving file {f.filename}: {e}")

    now = datetime.utcnow()
    existing = await db[CLS_RESULTS_COLLECTION].find_one({"order_id": oid})
    if existing:
        update_doc: dict = {"updated_at": now}
        if modality is not None:
            update_doc["modality"] = modality
        if conclusion is not None:
            update_doc["conclusion"] = conclusion
        if parsed_text_results:
            update_doc["text_results"] = parsed_text_results
        if saved_paths:
            await db[CLS_RESULTS_COLLECTION].update_one({"_id": existing["_id"]}, {"$push": {"attachments": {"$each": saved_paths}}})
        await db[CLS_RESULTS_COLLECTION].update_one({"_id": existing["_id"]}, {"$set": update_doc})
        updated = await db[CLS_RESULTS_COLLECTION].find_one({"_id": existing["_id"]})
        # Mark order completed
        await db[CLS_ORDERS_COLLECTION].update_one({"_id": oid}, {"$set": {"status": "completed", "updated_at": datetime.utcnow()}})
        return serialize_result(updated)
    else:
        doc = {
            "order_id": oid,
            "result_date": now,
            "modality": modality,
            "text_results": parsed_text_results,
            "attachments": saved_paths,
            "conclusion": conclusion,
            "created_at": now,
            "updated_at": now,
        }
        ins = await db[CLS_RESULTS_COLLECTION].insert_one(doc)
        created = await db[CLS_RESULTS_COLLECTION].find_one({"_id": ins.inserted_id})
        await db[CLS_ORDERS_COLLECTION].update_one({"_id": oid}, {"$set": {"status": "completed", "updated_at": datetime.utcnow()}})
        return serialize_result(created)
@app.delete("/api/v1/drugs/{drug_id}")
async def delete_drug(drug_id: str, db = Depends(get_db), current_user: dict = Depends(require_role([UserRole.RECEPTIONIST, UserRole.DOCTOR]))):
    """Soft delete: set is_active = False"""
    oid = try_parse_object_id(drug_id)
    if oid is None:
        raise HTTPException(status_code=400, detail="Invalid drug id")
    result = await db[DRUGS_COLLECTION].update_one({"_id": oid}, {"$set": {"is_active": False, "updated_at": datetime.utcnow()}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Drug not found")
    updated = await db[DRUGS_COLLECTION].find_one({"_id": oid})
    return serialize_drug(updated)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)