#!/bin/bash

# Quick Setup Script for Hospital Management System
# Chạy script này để setup nhanh cho team

echo "🏥 Hospital Management System - Quick Setup"
echo "============================================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được tìm thấy. Vui lòng cài đặt Python 3.9+"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Tạo file .env nếu chưa có
if [ ! -f "services/patient-service/backend/.env" ]; then
    echo "📝 Tạo file .env..."
    cp services/patient-service/backend/.env.example services/patient-service/backend/.env
    echo "⚠️  Vui lòng cập nhật MONGODB_URL trong file services/patient-service/backend/.env"
fi

# Setup Backend
echo "🔧 Setting up Backend..."
cd services/patient-service/backend

if [ ! -d "venv" ]; then
    echo "📦 Tạo virtual environment cho Backend..."
    python3 -m venv venv
fi

echo "📦 Kích hoạt virtual environment và cài đặt dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

cd ../../..

# Setup Frontend
echo "🖥️  Setting up Frontend..."
cd services/patient-service/frontend

if [ ! -d "venv" ]; then
    echo "📦 Tạo virtual environment cho Frontend..."
    python3 -m venv venv
fi

echo "📦 Kích hoạt virtual environment và cài đặt dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

cd ../../..

echo ""
echo "🎉 Setup hoàn thành!"
echo ""
echo "📋 Bước tiếp theo:"
echo "1. Cập nhật MONGODB_URL trong file: services/patient-service/backend/.env"
echo "   Ví dụ: MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/hospital_management"
echo "2. Chạy ứng dụng: cd services/patient-service && python run-all.py"
echo "3. Truy cập: http://127.0.0.1:5000"
echo ""
echo "📚 Xem hướng dẫn nhanh: README_TEAM.md"
echo "📋 Hướng dẫn chi tiết: SETUP_GUIDE.md"
