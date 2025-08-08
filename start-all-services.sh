#!/bin/bash

# Hospital Management System - Microservices Startup Script
echo "🏥 Starting Hospital Management Microservices System..."
echo "=================================================="

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}Port $port is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}Port $port is available${NC}"
        return 0
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    local use_venv=$4
    
    echo -e "\n${BLUE}🚀 Starting $service_name on port $port...${NC}"
    
    cd "$service_path"
    
    if [ "$use_venv" = "true" ] && [ -f "venv/bin/python" ]; then
        # Use virtual environment Python directly
        ./venv/bin/python main.py &
        local pid=$!
    else
        # Use system Python with PYTHONPATH
        PYTHONPATH="$PYTHON_PATH" python3 main.py &
        local pid=$!
    fi
    
    echo "Started $service_name with PID: $pid"
    sleep 5
    
    # Check if service is running
    if kill -0 $pid 2>/dev/null; then
        echo -e "${GREEN}✅ $service_name started successfully${NC}"
    else
        echo -e "${RED}❌ Failed to start $service_name${NC}"
    fi
}

# Kill existing processes on target ports
echo -e "${YELLOW}🔄 Stopping existing services...${NC}"
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
sleep 2

# Check port availability
echo -e "\n${BLUE}🔍 Checking port availability...${NC}"
check_port 8001
check_port 8002  
check_port 5001

# Set base directory
BASE_DIR="/Users/adriannguyen/Desktop/DEV/HCMUS/UDPT/UDPT_HospitalManagementSystem"
PYTHON_PATH="$BASE_DIR/services/insurance-service/venv/lib/python3.13/site-packages"

# Start Insurance Service (Port 8002)
start_service "Insurance Service" "$BASE_DIR/services/insurance-service" 8002 true

# Wait a bit before starting next service
sleep 2

# Start Patient Service (Port 8001)
start_service "Patient Service" "$BASE_DIR/services/patient-service/backend" 8001 true

# Wait a bit before starting frontend
sleep 2

# Start Frontend Service (Port 5001)
echo -e "\n${BLUE}🚀 Starting Frontend Service on port 5001...${NC}"
cd "$BASE_DIR/services/patient-service/frontend"
./venv/bin/python app.py &
FRONTEND_PID=$!
echo "Started Frontend Service with PID: $FRONTEND_PID"
sleep 5

# Verify all services
echo -e "\n${YELLOW}🔍 Verifying services...${NC}"

# Check Insurance Service
if curl -s http://localhost:8002/health > /dev/null; then
    echo -e "${GREEN}✅ Insurance Service (Port 8002) - RUNNING${NC}"
else
    echo -e "${RED}❌ Insurance Service (Port 8002) - NOT RESPONDING${NC}"
fi

# Check Patient Service  
if curl -s http://localhost:8001/health > /dev/null; then
    echo -e "${GREEN}✅ Patient Service (Port 8001) - RUNNING${NC}"
else
    echo -e "${RED}❌ Patient Service (Port 8001) - NOT RESPONDING${NC}"
fi

# Check Frontend Service
if curl -s http://localhost:5001 > /dev/null; then
    echo -e "${GREEN}✅ Frontend Service (Port 5001) - RUNNING${NC}"
else
    echo -e "${RED}❌ Frontend Service (Port 5001) - NOT RESPONDING${NC}"
fi

echo -e "\n${GREEN}🎉 Hospital Management System Started!${NC}"
echo "=================================================="
echo "📊 Service URLs:"
echo "• Insurance Service API: http://localhost:8002/docs"
echo "• Patient Service API:   http://localhost:8001/docs"
echo "• Web Application:       http://localhost:5001"
echo ""
echo "💾 Databases:"
echo "• Insurance Service:     insurance_service_db (MongoDB)"
echo "• Patient Service:       hospital_management (MongoDB)"
echo ""
echo -e "${YELLOW}💡 To stop all services, run: ./stop-all-services.sh${NC}"
echo "Or press Ctrl+C and run: pkill -f 'python.*main.py'"
