#!/usr/bin/env python3
"""
Script tạo tài khoản người dùng cho hệ thống Hospital Management
Sử dụng: python3 create_user.py
"""

import requests
import json
import getpass

# Configuration
PATIENT_SERVICE_URL = "http://localhost:8001"

def create_user():
    print("🏥 Tạo tài khoản người dùng mới")
    print("=" * 40)
    
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
    confirm_password = getpass.getpass("🔒 Xác nhận mật khẩu: ")
    
    if password != confirm_password:
        print("❌ Mật khẩu xác nhận không khớp!")
        return
    
    # Tạo user data
    user_data = {
        "email": email,
        "full_name": full_name,
        "role": role,
        "password": password,
        "is_active": True
    }
    
    try:
        print("\n⏳ Đang tạo tài khoản...")
        response = requests.post(f"{PATIENT_SERVICE_URL}/api/v1/auth/register", json=user_data)
        
        if response.status_code == 200:
            user_info = response.json()
            print("\n✅ Tạo tài khoản thành công!")
            print(f"📧 Email: {user_info['email']}")
            print(f"👤 Tên: {user_info['full_name']}")
            print(f"🔑 Vai trò: {user_info['role']}")
            print(f"🆔 ID: {user_info['_id']}")
            print(f"📅 Tạo lúc: {user_info['created_at']}")
        else:
            error_data = response.json()
            print(f"❌ Lỗi: {error_data.get('detail', 'Lỗi không xác định')}")
            
    except requests.RequestException as e:
        print(f"❌ Lỗi kết nối: {e}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def list_users():
    """Liệt kê danh sách user (cần admin access)"""
    print("\n📋 Danh sách tài khoản hiện có:")
    print("(Cần đăng nhập với quyền admin để xem)")
    
    # Demo: hiển thị các tài khoản mẫu
    demo_accounts = [
        {"email": "doctor@hospital.com", "role": "doctor", "name": "Dr. John Smith"},
        {"email": "receptionist@hospital.com", "role": "receptionist", "name": "Lễ Tân Hospital"},
        {"email": "patient@hospital.com", "role": "patient", "name": "John Patient"},
        {"email": "admin2@hospital.com", "role": "receptionist", "name": "Admin Hệ thống 2"}
    ]
    
    for i, account in enumerate(demo_accounts, 1):
        print(f"{i}. {account['email']} - {account['name']} ({account['role']})")

if __name__ == "__main__":
    print("🏥 Hospital Management - User Management Tool")
    print("=" * 50)
    
    while True:
        print("\n📋 Menu:")
        print("1. Tạo tài khoản mới")
        print("2. Xem danh sách tài khoản")
        print("3. Thoát")
        
        choice = input("\nNhập lựa chọn (1-3): ")
        
        if choice == "1":
            create_user()
        elif choice == "2":
            list_users()
        elif choice == "3":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")
