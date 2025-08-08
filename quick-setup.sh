#!/bin/bash

# Quick Setup Script # Create .env files with MongoDB connection
echo "📝 Tạo file .env cho Patient Service..."
cat > services/patient-service/backend/.env << EOF
# MongoDB connection string - Replace with your actual MongoDB Atlas connection  
MONGODB_URL=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/hospital_management

# Service configuration
PORT=8001
HOST=0.0.0.0

# Insurance Service URL
INSURANCE_SERVICE_URL=http://localhost:8002
EOFTạo file .env cho Insurance Service..."
cat > services/insurance-service/.env << EOF
# MongoDB connection string - Replace with your actual MongoDB Atlas connection
MONGODB_URL=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/insurance_service_db

# Service configuration
PORT=8002
HOST=0.0.0.0
EOF

echo "⚠️  QUAN TRỌNG: Cập nhật MongoDB connection string trong file .env"al Management Microservices System
# Chạy script này để setup nhanh cho team

echo "🏥 Hospital Management Microservices System - Quick Setup"
echo "=========================================================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được tìm thấy. Vui lòng cài đặt Python 3.9+"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Setup Insurance Service
echo ""
echo "🔧 Setting up Insurance Service..."
cd services/insurance-service

if [ ! -d "venv" ]; then
    echo "� Tạo virtual environment cho Insurance Service..."
    python3 -m venv venv
fi

echo "📦 Kích hoạt virtual environment và cài đặt dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Tạo file .env cho Insurance Service nếu chưa có
if [ ! -f ".env" ]; then
    echo "📝 Tạo file .env cho Insurance Service..."
    cat > .env << EOF
# Environment Configuration for Insurance Service
# Separate database for Insurance Service in microservices architecture
MONGODB_URL=mongodb+srv://.../insurance_service_db

# Optional: Service Configuration
PORT=8002
DEBUG=True
EOF
    echo "✅ File .env đã được tạo cho Insurance Service"
fi

cd ../..

# Setup Patient Service Backend
echo ""
echo "🔧 Setting up Patient Service Backend..."
cd services/patient-service/backend

if [ ! -d "venv" ]; then
    echo "📦 Tạo virtual environment cho Patient Service Backend..."
    python3 -m venv venv
fi

echo "📦 Kích hoạt virtual environment và cài đặt dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn motor pymongo python-dotenv httpx 'pydantic[email]'
deactivate

# Tạo file .env cho Patient Service nếu chưa có
if [ ! -f ".env" ]; then
    echo "📝 Tạo file .env cho Patient Service..."
    cat > .env << EOF
# Environment Configuration for Patient Service
MONGODB_URL=mongodb+srv://.../hospital_management

# Service Configuration
PORT=8001
DEBUG=True
EOF
    echo "✅ File .env đã được tạo cho Patient Service"
fi

cd ../../..

# Setup Frontend
echo ""
echo "🖥️  Setting up Frontend..."
cd services/patient-service/frontend

if [ ! -d "venv" ]; then
    echo "📦 Tạo virtual environment cho Frontend..."
    python3 -m venv venv
fi

echo "📦 Kích hoạt virtual environment và cài đặt dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install flask requests python-dotenv
deactivate

cd ../../..

# Make startup scripts executable
echo ""
echo "🔧 Setting up startup scripts..."
chmod +x start-all-services.sh
chmod +x stop-all-services.sh

echo ""
echo "🎉 Setup hoàn thành!"
echo ""
echo "� HƯỚNG DẪN CHẠY HỆ THỐNG:"
echo "=========================================="
echo ""
echo "1️⃣  CHẠY TẤT CẢ SERVICES:"
echo "   ./start-all-services.sh"
echo ""
echo "2️⃣  DỪNG TẤT CẢ SERVICES:"
echo "   ./stop-all-services.sh"
echo ""
echo "📊 CÁC SERVICE SẼ CHẠY TẠI:"
echo "   • Insurance Service API:  http://localhost:8002/docs"
echo "   • Patient Service API:    http://localhost:8001/docs"
echo "   • Web Application:        http://localhost:5001"
echo ""
echo "💾 KIẾN TRÚC DATABASE:"
echo "   • Insurance Service:      insurance_service_db (MongoDB)"
echo "   • Patient Service:        hospital_management (MongoDB)"
echo ""
echo "📁 TỔ CHỨC MICROSERVICES:"
echo "   ├── services/insurance-service/     (Port 8002)"
echo "   ├── services/patient-service/       (Port 8001 + 5001)"
echo "   └── start-all-services.sh          (Script chạy tất cả)"
echo ""
echo "🔍 KIỂM TRA TRẠNG THÁI:"
echo "   curl http://localhost:8002/health   (Insurance Service)"
echo "   curl http://localhost:8001/health   (Patient Service)"
echo ""
echo "📚 Tài liệu thêm:"
echo "   • README_TEAM.md     - Hướng dẫn team"
echo "   • SETUP_GUIDE.md     - Hướng dẫn chi tiết"
echo "   • MICROSERVICES_GUIDE.md - Kiến trúc microservices"
