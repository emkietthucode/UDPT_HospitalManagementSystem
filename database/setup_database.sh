#!/bin/bash

# Hospital Management System - Database Setup Script
# This script sets up the PostgreSQL database with schema and sample data

echo "🏥 Hospital Management System - Database Setup"
echo "=============================================="

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start PostgreSQL and Redis containers
echo "🐳 Starting PostgreSQL and Redis containers..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Test connection
echo "🔗 Testing PostgreSQL connection..."
docker exec hospital_postgres pg_isready -U hospital_admin -d hospital_management

if [ $? -ne 0 ]; then
    echo "❌ PostgreSQL is not ready yet. Please wait and try again."
    exit 1
fi

# Apply database schema
echo "📋 Applying database schema..."
docker exec -i hospital_postgres psql -U hospital_admin -d hospital_management < database/schema.sql

if [ $? -eq 0 ]; then
    echo "✅ Database schema applied successfully!"
else
    echo "❌ Failed to apply database schema."
    exit 1
fi

# Load sample data (optional)
read -p "🤔 Do you want to load sample data? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 Loading sample data..."
    docker exec -i hospital_postgres psql -U hospital_admin -d hospital_management < database/sample_data.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Sample data loaded successfully!"
    else
        echo "❌ Failed to load sample data."
    fi
fi

# Show database information
echo ""
echo "🎉 Database setup completed!"
echo "================================"
echo "📍 Database URL: postgresql://hospital_admin:hospital_password@localhost:5432/hospital_management"
echo "🔧 Redis URL: redis://localhost:6379/0"
echo ""
echo "📊 To connect to the database:"
echo "   docker exec -it hospital_postgres psql -U hospital_admin -d hospital_management"
echo ""
echo "📋 To view tables:"
echo "   \\dt"
echo ""
echo "🛑 To stop containers:"
echo "   docker-compose down"
echo ""

# Test some basic queries
echo "🧪 Running basic tests..."
echo "----------------------------------------"

# Count users
USER_COUNT=$(docker exec hospital_postgres psql -U hospital_admin -d hospital_management -t -c "SELECT COUNT(*) FROM users;")
echo "👥 Total users: $(echo $USER_COUNT | xargs)"

# Count specialties
SPECIALTY_COUNT=$(docker exec hospital_postgres psql -U hospital_admin -d hospital_management -t -c "SELECT COUNT(*) FROM specialties;")
echo "🏥 Total specialties: $(echo $SPECIALTY_COUNT | xargs)"

# Count patients
PATIENT_COUNT=$(docker exec hospital_postgres psql -U hospital_admin -d hospital_management -t -c "SELECT COUNT(*) FROM patients;")
echo "🤒 Total patients: $(echo $PATIENT_COUNT | xargs)"

echo ""
echo "🚀 Ready to start development!"