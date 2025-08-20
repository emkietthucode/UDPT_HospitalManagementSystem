#!/usr/bin/env python3
"""
Script tạo user trực tiếp trong MongoDB Atlas
Dùng khi không thể truy cập API
"""

import os
import sys
import getpass
from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext

# Load environment variables
sys.path.append('services/patient-service/backend')
from dotenv import load_dotenv

# Load .env file
load_dotenv('services/patient-service/backend/.env')

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = "hospital_management"
USERS_COLLECTION = "users"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def create_user_direct():
    """Tạo user trực tiếp trong MongoDB"""
    print("🏥 Tạo tài khoản trực tiếp trong MongoDB")
    print("=" * 50)
    
    if not MONGODB_URL:
        print("❌ Không tìm thấy MONGODB_URL trong .env file")
        return
    
    # Nhập thông tin
    email = input("📧 Email: ")
    full_name = input("👤 Họ và tên: ")
    
    print("\n🔑 Chọn vai trò:")
    print("1. 👤 Bệnh nhân (patient)")
    print("2. 👨‍⚕️ Bác sĩ (doctor)")
    print("3. 👩‍💼 Lễ tân (receptionist)")
    
    role_choice = input("Nhập lựa chọn (1-3): ")
    role_map = {
        "1": "patient",
        "2": "doctor", 
        "3": "receptionist"
    }
    
    if role_choice not in role_map:
        print("❌ Lựa chọn không hợp lệ!")
        return
    
    role = role_map[role_choice]
    password = getpass.getpass("🔒 Mật khẩu: ")
    
    try:
        print("\n⏳ Đang kết nối MongoDB...")
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        users_collection = db[USERS_COLLECTION]
        
        # Kiểm tra email đã tồn tại
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            print("❌ Email đã tồn tại trong hệ thống!")
            return
        
        # Tạo user document
        user_doc = {
            "email": email,
            "full_name": full_name,
            "role": role,
            "hashed_password": hash_password(password),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        print("⏳ Đang tạo tài khoản...")
        result = users_collection.insert_one(user_doc)
        
        print("\n✅ Tạo tài khoản thành công!")
        print(f"📧 Email: {email}")
        print(f"👤 Tên: {full_name}")
        print(f"🔑 Vai trò: {role}")
        print(f"🆔 MongoDB ID: {result.inserted_id}")
        print(f"📅 Tạo lúc: {user_doc['created_at']}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'client' in locals():
            client.close()

def list_users_direct():
    """Liệt kê users từ MongoDB"""
    try:
        print("\n⏳ Đang kết nối MongoDB...")
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        users_collection = db[USERS_COLLECTION]
        
        users = list(users_collection.find({}, {"hashed_password": 0}))
        
        if not users:
            print("📋 Không có user nào trong hệ thống")
            return
        
        print(f"\n📋 Danh sách {len(users)} tài khoản:")
        print("-" * 80)
        
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['email']}")
            print(f"   👤 Tên: {user['full_name']}")
            print(f"   🔑 Vai trò: {user['role']}")
            print(f"   ✅ Kích hoạt: {'Có' if user.get('is_active', True) else 'Không'}")
            print(f"   📅 Tạo: {user['created_at']}")
            print()
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🏥 Hospital Management - Direct MongoDB User Management")
    print("=" * 60)
    
    while True:
        print("\n📋 Menu:")
        print("1. Tạo tài khoản mới (MongoDB)")
        print("2. Xem danh sách tài khoản (MongoDB)")
        print("3. Thoát")
        
        choice = input("\nNhập lựa chọn (1-3): ")
        
        if choice == "1":
            create_user_direct()
        elif choice == "2":
            list_users_direct()
        elif choice == "3":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")
