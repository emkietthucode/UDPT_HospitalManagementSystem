#!/bin/bash

# Hospital Management System - Stop All Services Script
echo "🛑 Stopping Hospital Management Microservices System..."
echo "======================================================="

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kill processes by port
echo -e "${YELLOW}🔄 Stopping services...${NC}"

# Stop Insurance Service (Port 8002)
if lsof -ti:8002 >/dev/null 2>&1; then
    echo "Stopping Insurance Service (Port 8002)..."
    lsof -ti:8002 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Insurance Service stopped${NC}"
else
    echo -e "${YELLOW}⚠️ Insurance Service not running${NC}"
fi

# Stop Patient Service (Port 8001)
if lsof -ti:8001 >/dev/null 2>&1; then
    echo "Stopping Patient Service (Port 8001)..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Patient Service stopped${NC}"
else
    echo -e "${YELLOW}⚠️ Patient Service not running${NC}"
fi

# Stop Frontend Service (Port 5000)
if lsof -ti:5000 >/dev/null 2>&1; then
    echo "Stopping Frontend Service (Port 5000)..."
    lsof -ti:5000 | xargs kill -9 2>/dev/null
    echo -e "${GREEN}✅ Frontend Service stopped${NC}"
else
    echo -e "${YELLOW}⚠️ Frontend Service not running${NC}"
fi

# Kill any remaining Python processes related to our services
echo "Cleaning up remaining Python processes..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

sleep 2

echo -e "\n${GREEN}🎉 All services stopped successfully!${NC}"
echo "You can restart the system with: ./start-all-services.sh"
