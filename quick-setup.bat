@echo off
setlocal enabledelayedexpansion

:: Hospital Management Microservices System - Quick Setup for Windows
echo 🏥 Hospital Management Microservices System - Quick Setup
echo ==========================================================

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy. Vui lòng cài đặt Python 3.9+
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

:: Create .env files with MongoDB connection
echo.
echo 📝 Tạo file .env cho Patient Service...
(
echo # MongoDB connection string - Replace with your actual MongoDB Atlas connection
echo MONGODB_URL=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/hospital_management
echo.
echo # Service configuration
echo PORT=8001
echo HOST=0.0.0.0
echo.
echo # Insurance Service URL
echo INSURANCE_SERVICE_URL=http://localhost:8002
) > services\patient-service\backend\.env

echo.
echo 📝 Tạo file .env cho Insurance Service...
(
echo # MongoDB connection string - Replace with your actual MongoDB Atlas connection
echo MONGODB_URL=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/insurance_service_db
echo.
echo # Service configuration
echo PORT=8002
echo HOST=0.0.0.0
) > services\insurance-service\.env

echo.
echo ⚠️  QUAN TRỌNG: Cập nhật MongoDB connection string trong file .env

:: Setup Insurance Service
echo.
echo 🔧 Setting up Insurance Service...
cd services\insurance-service

if not exist "venv" (
    echo 📦 Tạo virtual environment cho Insurance Service...
    python -m venv venv
)

echo 📦 Kích hoạt virtual environment và cài đặt dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
call venv\Scripts\deactivate.bat

:: Create .env for Insurance Service if not exists
if not exist ".env" (
    echo 📝 Tạo file .env cho Insurance Service...
    (
    echo # Environment Configuration for Insurance Service
    echo # Separate database for Insurance Service in microservices architecture
    echo MONGODB_URL=mongodb+srv://.../insurance_service_db
    echo.
    echo # Optional: Service Configuration
    echo PORT=8002
    echo DEBUG=True
    ) > .env
    echo ✅ File .env đã được tạo cho Insurance Service
)

cd ..\..

:: Setup Patient Service Backend
echo.
echo 🔧 Setting up Patient Service Backend...
cd services\patient-service\backend

if not exist "venv" (
    echo 📦 Tạo virtual environment cho Patient Service Backend...
    python -m venv venv
)

echo 📦 Kích hoạt virtual environment và cài đặt dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install fastapi uvicorn motor pymongo python-dotenv httpx "pydantic[email]"
call venv\Scripts\deactivate.bat

:: Create .env for Patient Service if not exists
if not exist ".env" (
    echo 📝 Tạo file .env cho Patient Service...
    (
    echo # Environment Configuration for Patient Service
    echo MONGODB_URL=mongodb+srv://.../hospital_management
    echo.
    echo # Service Configuration
    echo PORT=8001
    echo DEBUG=True
    ) > .env
    echo ✅ File .env đã được tạo cho Patient Service
)

cd ..\..\..

:: Setup Frontend
echo.
echo 🖥️  Setting up Frontend...
cd services\patient-service\frontend

if not exist "venv" (
    echo 📦 Tạo virtual environment cho Frontend...
    python -m venv venv
)

echo 📦 Kích hoạt virtual environment và cài đặt dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install flask requests python-dotenv
call venv\Scripts\deactivate.bat

cd ..\..\..

echo.
echo 🎉 Setup hoàn thành!
echo.
echo 📋 HƯỚNG DẪN CHẠY HỆ THỐNG:
echo ==========================================
echo.
echo 1️⃣  CHẠY TẤT CẢ SERVICES:
echo    start-all-services.bat
echo.
echo 2️⃣  DỪNG TẤT CẢ SERVICES:
echo    stop-all-services.bat
echo.
echo 📊 CÁC SERVICE SẼ CHẠY TẠI:
echo    • Insurance Service API:  http://localhost:8002/docs
echo    • Patient Service API:    http://localhost:8001/docs
echo    • Web Application:        http://localhost:5001
echo.
echo 💾 KIẾN TRÚC DATABASE:
echo    • Insurance Service:      insurance_service_db (MongoDB)
echo    • Patient Service:        hospital_management (MongoDB)
echo.
echo 📁 TỔ CHỨC MICROSERVICES:
echo    ├── services\insurance-service\     (Port 8002)
echo    ├── services\patient-service\       (Port 8001 + 5001)
echo    └── start-all-services.bat          (Script chạy tất cả)
echo.
echo 🔍 KIỂM TRA TRẠNG THÁI:
echo    curl http://localhost:8002/health   (Insurance Service)
echo    curl http://localhost:8001/health   (Patient Service)
echo.
echo 📚 Tài liệu thêm:
echo    • README_TEAM.md     - Hướng dẫn team
echo    • SETUP_GUIDE.md     - Hướng dẫn chi tiết
echo    • MICROSERVICES_GUIDE.md - Kiến trúc microservices

pause