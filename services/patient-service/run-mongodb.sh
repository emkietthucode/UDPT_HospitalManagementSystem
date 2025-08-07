#!/bin/bash

# Script to run the Patient Service with MongoDB
echo "🚀 Starting Patient Service with MongoDB..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Install Python dependencies if needed
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Start MongoDB and backend services
echo "🐳 Starting MongoDB and backend services..."
docker-compose up -d

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
sleep 10

# Check if services are running
echo "✅ Checking service status..."
docker-compose ps

echo ""
echo "🎉 Patient Service is now running!"
echo "📋 MongoDB Admin UI: http://localhost:27017"
echo "🔗 Backend API: http://localhost:8001"
echo "📚 API Documentation: http://localhost:8001/docs"
echo ""
echo "To stop the services: docker-compose down"
