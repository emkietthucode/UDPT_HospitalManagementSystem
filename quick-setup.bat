@echo off
REM Quick Setup Script for Hospital Management System - Windows version

echo 🏥 Hospital Management System - Quick Setup
echo =============================================

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy. Vui lòng cài đặt Python 3.9+
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Tạo file .env nếu chưa có
if not exist "services\patient-service\backend\.env" (
    echo 📝 Tạo file .env...
    copy "services\patient-service\backend\.env.example" "services\patient-service\backend\.env"
    echo ⚠️  Vui lòng cập nhật MONGODB_URL trong file services\patient-service\backend\.env
)

REM Setup Backend
echo 🔧 Setting up Backend...
cd services\patient-service\backend

if not exist "venv" (
    echo 📦 Tạo virtual environment cho Backend...
    python -m venv venv
)

echo 📦 Kích hoạt virtual environment và cài đặt dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
call venv\Scripts\deactivate

cd ..\..\..

REM Setup Frontend
echo 🖥️  Setting up Frontend...
cd services\patient-service\frontend

if not exist "venv" (
    echo 📦 Tạo virtual environment cho Frontend...
    python -m venv venv
)

echo 📦 Kích hoạt virtual environment và cài đặt dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
call venv\Scripts\deactivate

cd ..\..\..

echo.
echo 🎉 Setup hoàn thành!
echo.
echo 📋 Bước tiếp theo:
echo 1. Cập nhật MONGODB_URL trong file: services\patient-service\backend\.env
echo 2. Chạy ứng dụng: cd services\patient-service && python run-all.py
echo 3. Truy cập: http://127.0.0.1:5000
echo.
echo 📚 Xem hướng dẫn chi tiết tại: SETUP_GUIDE.md
pause
