from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from bson import ObjectId
import uvicorn
import os
import re
import random
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/hospital_management")
# Extract database name from MONGODB_URL (handle query string)
_parsed = urlparse(MONGODB_URL)
_db_path = _parsed.path.lstrip('/') if _parsed and _parsed.path else ""
DATABASE_NAME = _db_path or "insurance_service_db"
COLLECTION_NAME = "insurance_cards"
MONGODB_TIMEOUT_MS = int(os.getenv("MONGODB_TIMEOUT_MS", "2000"))

# Global variables for database
mongo_client: AsyncIOMotorClient = None
database = None

app = FastAPI(
    title="Insurance Service",
    description="Microservice để xác thực thông tin Bảo hiểm Y tế (BHYT)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database startup and shutdown events
@app.on_event("startup")
async def startup_event():
    global mongo_client, database
    # Short server selection timeout to avoid blocking startup when MongoDB is down
    mongo_client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=MONGODB_TIMEOUT_MS)
    database = mongo_client[DATABASE_NAME]

    # Best-effort ping and index creation; do not block service startup
    try:
        await database.command({"ping": 1})
    except Exception as e:
        print(f"[startup] MongoDB ping failed: {e}. Service will start without DB ready.")

    try:
        # Create indexes
        await database[COLLECTION_NAME].create_indexes([
            IndexModel([("card_number", ASCENDING)], unique=True),
            IndexModel([("full_name", ASCENDING)]),
            IndexModel([("date_of_birth", ASCENDING)]),
        ])

        # Insert sample data if collection is empty
        if await database[COLLECTION_NAME].count_documents({}) == 0:
            await insert_sample_data()
    except Exception as e:
        print(f"[startup] Skipping index creation/sample data due to MongoDB error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    if mongo_client:
        mongo_client.close()

# Helper function to convert ObjectId to string
def str_object_id(v):
    return str(v) if isinstance(v, ObjectId) else v

# Pydantic Models
class InsuranceCard(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    card_number: str = Field(..., description="Số thẻ BHYT (15 ký tự)")
    full_name: str = Field(..., description="Họ tên chủ thẻ")
    date_of_birth: date = Field(..., description="Ngày sinh")
    address: str = Field(..., description="Địa chỉ")
    issued_place: str = Field(..., description="Nơi cấp thẻ")
    valid_from: date = Field(..., description="Có hiệu lực từ")
    valid_to: date = Field(..., description="Có hiệu lực đến")
    coverage_percentage: int = Field(..., description="Mức chi trả (%)")
    hospital_level: str = Field(..., description="Hạng bệnh viện")

class InsuranceValidationRequest(BaseModel):
    card_number: str
    date_of_birth: date

class InsuranceValidationResponse(BaseModel):
    is_valid: bool
    message: str
    card_info: Optional[InsuranceCard] = None
    coverage_percentage: Optional[int] = None
    hospital_level: Optional[str] = None

class InsuranceStatus(BaseModel):
    patient_id: str
    card_number: str
    is_validated: bool
    validation_date: datetime
    coverage_percentage: int
    notes: Optional[str] = None

# Sample Data Function
async def insert_sample_data():
    """Insert sample insurance cards into database"""
    sample_cards = [
        {
            "card_number": "HS4010123456789",
            "full_name": "Nguyễn Văn A",
            "date_of_birth": date(1990, 1, 15),
            "address": "123 Nguyễn Huệ, Q1, TP.HCM",
            "issued_place": "BHXH TP. Hồ Chí Minh",
            "valid_from": date(2024, 1, 1),
            "valid_to": date(2025, 12, 31),
            "coverage_percentage": 80,
            "hospital_level": "Hạng I"
        },
        {
            "card_number": "HS4020987654321",
            "full_name": "Khôi Nguyễn Đắc",
            "date_of_birth": date(1985, 5, 20),
            "address": "456 Lê Lợi, Q1, TP.HCM",
            "issued_place": "BHXH TP. Hồ Chí Minh",
            "valid_from": date(2024, 1, 1),
            "valid_to": date(2026, 12, 31),
            "coverage_percentage": 100,
            "hospital_level": "Hạng I"
        },
        {
            "card_number": "HS4031122334455",
            "full_name": "Trần Thị B",
            "date_of_birth": date(1992, 8, 10),
            "address": "789 Võ Văn Tần, Q3, TP.HCM",
            "issued_place": "BHXH TP. Hồ Chí Minh",
            "valid_from": date(2024, 6, 1),
            "valid_to": date(2025, 5, 31),
            "coverage_percentage": 80,
            "hospital_level": "Hạng II"
        },
        {
            "card_number": "HS4045566778899",
            "full_name": "Lê Văn C",
            "date_of_birth": date(1988, 12, 25),
            "address": "321 Cách Mạng Tháng 8, Q10, TP.HCM",
            "issued_place": "BHXH TP. Hồ Chí Minh",
            "valid_from": date(2024, 3, 1),
            "valid_to": date(2025, 2, 28),
            "coverage_percentage": 90,
            "hospital_level": "Hạng I"
        },
        {
            "card_number": "DN5010111222333",
            "full_name": "Phạm Thị D",
            "date_of_birth": date(1995, 4, 18),
            "address": "654 Hùng Vương, Q5, TP.HCM",
            "issued_place": "BHXH Đà Nẵng",
            "valid_from": date(2024, 2, 1),
            "valid_to": date(2025, 1, 31),
            "coverage_percentage": 75,
            "hospital_level": "Hạng II"
        },
        {
            "card_number": "HN6020444555666",
            "full_name": "Vũ Văn E",
            "date_of_birth": date(1987, 11, 3),
            "address": "987 Lý Thái Tổ, Hoàn Kiếm, Hà Nội",
            "issued_place": "BHXH Hà Nội",
            "valid_from": date(2024, 1, 1),
            "valid_to": date(2025, 12, 31),
            "coverage_percentage": 85,
            "hospital_level": "Hạng I"
        },
        {
            "card_number": "CT7030777888999",
            "full_name": "Hoàng Thị F",
            "date_of_birth": date(1993, 7, 22),
            "address": "159 Trần Hưng Đạo, Ninh Kiều, Cần Thơ",
            "issued_place": "BHXH Cần Thơ",
            "valid_from": date(2024, 4, 1),
            "valid_to": date(2025, 3, 31),
            "coverage_percentage": 80,
            "hospital_level": "Hạng II"
        },
        {
            "card_number": "HS4099888777666",
            "full_name": "Ngô Văn G",
            "date_of_birth": date(1980, 9, 14),
            "address": "753 Điện Biên Phủ, Q3, TP.HCM",
            "issued_place": "BHXH TP. Hồ Chí Minh",
            "valid_from": date(2023, 12, 1),
            "valid_to": date(2023, 11, 30),  # Expired card for testing
            "coverage_percentage": 95,
            "hospital_level": "Hạng I"
        }
    ]
    
    # Convert dates to datetime for MongoDB storage
    for card in sample_cards:
        card["date_of_birth"] = datetime.combine(card["date_of_birth"], datetime.min.time())
        card["valid_from"] = datetime.combine(card["valid_from"], datetime.min.time())
        card["valid_to"] = datetime.combine(card["valid_to"], datetime.min.time())
    
    try:
        await database[COLLECTION_NAME].insert_many(sample_cards)
        print(f"✅ Inserted {len(sample_cards)} sample insurance cards")
    except Exception as e:
        print(f"⚠️ Error inserting sample data: {e}")

# Mock Database - In production, this would be MongoDB/PostgreSQL
MOCK_INSURANCE_CARDS = {}

# Helper Functions
def validate_card_number_format(card_number: str) -> bool:
    """Validate BHYT card number format (15 digits)"""
    pattern = r'^[A-Z]{2}\d{13}$'
    return bool(re.match(pattern, card_number))

def is_card_expired(valid_to: datetime) -> bool:
    """Check if card is expired"""
    return valid_to.date() < date.today()

def calculate_coverage(hospital_level: str, card_level: str) -> int:
    """Calculate insurance coverage percentage based on hospital level and card level"""
    coverage_matrix = {
        ("Hạng I", "Hạng I"): 100,
        ("Hạng I", "Hạng II"): 80,
        ("Hạng I", "Hạng III"): 60,
        ("Hạng II", "Hạng I"): 100,
        ("Hạng II", "Hạng II"): 100,
        ("Hạng II", "Hạng III"): 80,
        ("Hạng III", "Hạng I"): 100,
        ("Hạng III", "Hạng II"): 100,
        ("Hạng III", "Hạng III"): 100,
    }
    return coverage_matrix.get((hospital_level, card_level), 60)

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Insurance Service", 
        "version": "1.0.0",
        "description": "BHYT Validation Microservice"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "insurance-service",
        "database": DATABASE_NAME,
        "timestamp": datetime.now()
    }

@app.post("/api/v1/insurance/validate", response_model=InsuranceValidationResponse)
async def validate_insurance_card(request: InsuranceValidationRequest):
    """
    Xác thực thẻ BHYT
    Kết nối với MongoDB để kiểm tra thông tin thẻ
    """
    
    # Validate card number format
    if not validate_card_number_format(request.card_number):
        return InsuranceValidationResponse(
            is_valid=False,
            message="Số thẻ BHYT không đúng định dạng (phải có 15 ký tự: 2 chữ cái + 13 số)"
        )
    
    # Check if card exists in database
    card_doc = await database[COLLECTION_NAME].find_one({"card_number": request.card_number})
    
    if not card_doc:
        return InsuranceValidationResponse(
            is_valid=False,
            message="Thẻ BHYT không tồn tại trong hệ thống"
        )
    
    # Convert datetime back to date for comparison
    card_dob = card_doc["date_of_birth"].date() if isinstance(card_doc["date_of_birth"], datetime) else card_doc["date_of_birth"]
    
    # Validate date of birth only
    if card_dob != request.date_of_birth:
        return InsuranceValidationResponse(
            is_valid=False,
            message="Ngày sinh không khớp với thẻ BHYT"
        )
    
    # Check if card is expired
    if is_card_expired(card_doc["valid_to"]):
        return InsuranceValidationResponse(
            is_valid=False,
            message="Thẻ BHYT đã hết hạn"
        )
    
    # Valid card - convert datetime fields back to dates for response
    card_info = card_doc.copy()
    card_info["_id"] = str(card_info["_id"])
    card_info["date_of_birth"] = card_dob
    card_info["valid_from"] = card_info["valid_from"].date() if isinstance(card_info["valid_from"], datetime) else card_info["valid_from"]
    card_info["valid_to"] = card_info["valid_to"].date() if isinstance(card_info["valid_to"], datetime) else card_info["valid_to"]
    
    insurance_card = InsuranceCard(**card_info)
    # Assume our hospital is level I
    coverage = calculate_coverage("Hạng I", card_doc.get("hospital_level", "Hạng I"))
    
    return InsuranceValidationResponse(
        is_valid=True,
        message="Thẻ BHYT hợp lệ",
        card_info=insurance_card,
        coverage_percentage=coverage,
        hospital_level="Hạng I"
    )

@app.get("/api/v1/insurance/cards", response_model=List[InsuranceCard])
async def get_all_cards():
    """Get all insurance cards from database"""
    try:
        cursor = database[COLLECTION_NAME].find({})
        cards = []
        async for card_doc in cursor:
            # Convert datetime fields back to dates
            card_doc["_id"] = str(card_doc["_id"])
            card_doc["date_of_birth"] = card_doc["date_of_birth"].date() if isinstance(card_doc["date_of_birth"], datetime) else card_doc["date_of_birth"]
            card_doc["valid_from"] = card_doc["valid_from"].date() if isinstance(card_doc["valid_from"], datetime) else card_doc["valid_from"]
            card_doc["valid_to"] = card_doc["valid_to"].date() if isinstance(card_doc["valid_to"], datetime) else card_doc["valid_to"]
            cards.append(InsuranceCard(**card_doc))
        return cards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/v1/insurance/add-card")
async def add_insurance_card(card: InsuranceCard):
    """Add a new insurance card to database"""
    try:
        # Convert dates to datetime for MongoDB storage
        card_data = card.model_dump(exclude={"id"})
        card_data["date_of_birth"] = datetime.combine(card_data["date_of_birth"], datetime.min.time())
        card_data["valid_from"] = datetime.combine(card_data["valid_from"], datetime.min.time())
        card_data["valid_to"] = datetime.combine(card_data["valid_to"], datetime.min.time())
        
        result = await database[COLLECTION_NAME].insert_one(card_data)
        return {
            "message": "Insurance card added successfully", 
            "card_number": card.card_number,
            "id": str(result.inserted_id)
        }
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(status_code=400, detail="Card number already exists")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/insurance/card/{card_number}")
async def get_card_info(card_number: str):
    """Get insurance card information by card number"""
    try:
        card_doc = await database[COLLECTION_NAME].find_one({"card_number": card_number})
        
        if not card_doc:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Convert datetime fields back to dates
        card_doc["_id"] = str(card_doc["_id"])
        card_doc["date_of_birth"] = card_doc["date_of_birth"].date() if isinstance(card_doc["date_of_birth"], datetime) else card_doc["date_of_birth"]
        card_doc["valid_from"] = card_doc["valid_from"].date() if isinstance(card_doc["valid_from"], datetime) else card_doc["valid_from"]
        card_doc["valid_to"] = card_doc["valid_to"].date() if isinstance(card_doc["valid_to"], datetime) else card_doc["valid_to"]
        
        return InsuranceCard(**card_doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/v1/insurance/stats")
async def get_insurance_stats():
    """Get insurance database statistics"""
    try:
        total_cards = await database[COLLECTION_NAME].count_documents({})
        
        # Count valid vs expired cards
        current_date = datetime.now()
        valid_cards = await database[COLLECTION_NAME].count_documents({
            "valid_to": {"$gte": current_date}
        })
        expired_cards = total_cards - valid_cards
        
        # Group by issued place
        pipeline = [
            {"$group": {"_id": "$issued_place", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        issued_places = []
        async for doc in database[COLLECTION_NAME].aggregate(pipeline):
            issued_places.append({"place": doc["_id"], "count": doc["count"]})
        
        return {
            "total_cards": total_cards,
            "valid_cards": valid_cards,
            "expired_cards": expired_cards,
            "issued_places": issued_places
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8002)),
        reload=True
    )
