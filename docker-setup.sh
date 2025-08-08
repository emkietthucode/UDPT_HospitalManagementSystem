#!/bin/bash

# Docker Quick Setup for Hospital Management System
# Run này để setup với Docker

echo "🐳 Hospital Management System - Docker Setup"
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
# MongoDB Configuration for Docker
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/hospital_management

# Optional: RabbitMQ (for future services)
# RABBITMQ_URL=amqp://hospital:password@rabbitmq:5672
EOF
    echo "⚠️  Vui lòng cập nhật MONGODB_URL trong file .env"
fi

# Build và chạy với Docker Compose
echo "🔧 Building và starting Docker containers..."
echo "📦 Đây có thể mất vài phút lần đầu..."

# Pull base images trước để nhanh hơn
echo "📥 Pulling base images..."
docker pull python:3.11-slim

# Build và start containers
if docker compose version &> /dev/null; then
    # Docker Compose V2
    docker compose up --build -d
else
    # Docker Compose V1
    docker-compose up --build -d
fi

# Chờ services khởi động
echo "⏳ Đợi services khởi động..."
sleep 30

# Kiểm tra health
echo "🏥 Kiểm tra health của services..."

# Check backend health
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Backend service is healthy"
else
    echo "⚠️  Backend service chưa sẵn sàng, đợi thêm..."
    sleep 15
fi

# Check frontend
if curl -s http://localhost:5000 > /dev/null; then
    echo "✅ Frontend service is healthy"
else
    echo "⚠️  Frontend service chưa sẵn sàng"
fi

echo ""
echo "🎉 Docker setup hoàn thành!"
echo ""
echo "🌐 Truy cập ứng dụng:"
echo "   • Frontend: http://localhost:5000"
echo "   • Backend API: http://localhost:8001/docs"
echo "   • Health Check: http://localhost:8001/health"
echo ""
echo "📋 Useful Commands:"
echo "   • Xem logs: docker compose logs -f"
echo "   • Stop: docker compose down"
echo "   • Restart: docker compose restart"
echo ""
echo "📚 Xem hướng dẫn Docker tại: DOCKER_GUIDE.md"
