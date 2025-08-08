#!/bin/bash

# Microservices Setup Script for Hospital Management System
# Chạy script này để setup toàn bộ microservices với Docker

echo "🏥 Hospital Management Microservices - Setup"
echo "============================================="

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker không được tìm thấy. Vui lòng cài đặt Docker Desktop"
    echo "📥 Download: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Kiểm tra Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose không được tìm thấy"
    exit 1
fi

echo "✅ Docker Compose found"

# Tạo file .env nếu chưa có
if [ ! -f ".env" ]; then
    echo "📝 Tạo file .env..."
    cat > .env << 'EOF'
# MongoDB Configuration for Microservices
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/hospital_management

# Service URLs (auto-configured by Docker)
PATIENT_SERVICE_URL=http://patient-backend:8001
INSURANCE_SERVICE_URL=http://insurance-service:8002
EOF
    echo "⚠️  Vui lòng cập nhật MONGODB_URL trong file .env"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
if docker compose version &> /dev/null; then
    docker compose down 2>/dev/null || true
else
    docker-compose down 2>/dev/null || true
fi

# Build và chạy microservices
echo "🔧 Building và starting microservices..."
echo "📦 Đây có thể mất vài phút lần đầu..."

# Pull base images trước
echo "📥 Pulling base images..."
docker pull python:3.11-slim

# Build và start all services
if docker compose version &> /dev/null; then
    # Docker Compose V2
    echo "🏗️  Building services..."
    docker compose build --parallel
    
    echo "🚀 Starting services..."
    docker compose up -d
else
    # Docker Compose V1
    echo "🏗️  Building services..."
    docker-compose build
    
    echo "🚀 Starting services..."
    docker-compose up -d
fi

# Chờ services khởi động
echo "⏳ Đợi services khởi động..."
sleep 45

# Kiểm tra health của từng service
echo "🏥 Kiểm tra health của services..."

check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is healthy"
            return 0
        fi
        echo "⏳ Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    echo "⚠️  $service_name is not responding"
    return 1
}

# Check services
check_service "Insurance Service" "http://localhost:8002/health"
check_service "Patient Backend" "http://localhost:8001/health"
check_service "Patient Frontend" "http://localhost:5000"

echo ""
echo "🎉 Microservices setup hoàn thành!"
echo ""
echo "🌐 Truy cập ứng dụng:"
echo "   • Frontend (Web UI): http://localhost:5000"
echo "   • Patient API: http://localhost:8001/docs"
echo "   • Insurance API: http://localhost:8002/docs"
echo ""
echo "🧪 Test BHYT với thẻ mẫu:"
echo "   • HS4010123456789 - Nguyễn Văn A (15/01/1990)"
echo "   • HS4020987654321 - Khôi Nguyễn Đắc (20/05/1985)"
echo ""
echo "📋 Useful Commands:"
echo "   • Xem logs: docker compose logs -f"
echo "   • Stop: docker compose down"
echo "   • Restart: docker compose restart"
echo "   • Rebuild: docker compose up --build -d"
echo ""
echo "📚 Xem hướng dẫn Docker tại: DOCKER_GUIDE.md"
