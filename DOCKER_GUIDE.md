# Docker Setup Guide for Microservices

## 🐳 Yêu cầu Docker

### 1. Cài đặt Docker Desktop
- **Windows/Mac:** https://www.docker.com/products/docker-desktop/
- **Linux:** 
  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install docker.io docker-compose-plugin
  
  # CentOS/RHEL
  sudo yum install docker docker-compose
  ```

### 2. Kiểm tra cài đặt
```bash
docker --version
docker compose --version  # Docker Compose V2
```

## 🚀 Chạy với Docker

### Option 1: Docker Compose (Khuyến nghị)
```bash
# Clone repository
git clone <repo-url>
cd UDPT_HospitalManagementSystem

# Tạo file .env với MongoDB URL
cp .env.example .env
# Sửa MONGODB_URL trong file .env

# Build và chạy tất cả services
docker compose up --build

# Hoặc chạy background
docker compose up -d --build
```

### Option 2: Build từng service riêng
```bash
# Build patient backend
docker build -t patient-backend ./services/patient-service/backend

# Build patient frontend  
docker build -t patient-frontend ./services/patient-service/frontend

# Run with network
docker network create hospital-network

docker run -d --name patient-backend \
  --network hospital-network \
  -p 8001:8001 \
  -e MONGODB_URL="your-mongodb-url" \
  patient-backend

docker run -d --name patient-frontend \
  --network hospital-network \
  -p 5000:5000 \
  -e PATIENT_SERVICE_URL="http://patient-backend:8001" \
  patient-frontend
```

## 🌐 Access URLs
- **Frontend:** http://localhost:5000
- **Backend API:** http://localhost:8001/docs

## 🔧 Useful Docker Commands

### Development
```bash
# Xem logs
docker compose logs -f

# Restart services
docker compose restart

# Stop tất cả
docker compose down

# Remove everything
docker compose down -v --rmi all
```

### Debug
```bash
# Vào container
docker exec -it patient-backend bash
docker exec -it patient-frontend bash

# Xem resource usage
docker stats

# Inspect network
docker network inspect hospital-network
```

## 📦 Thêm Services Mới

### 1. Tạo service structure
```bash
mkdir -p services/doctor-service
# Thêm Dockerfile, requirements.txt, main.py...
```

### 2. Uncomment trong docker-compose.yml
```yaml
doctor-service:
  build: ./services/doctor-service
  container_name: doctor-service
  ports:
    - "8002:8002"
  environment:
    - MONGODB_URL=${MONGODB_URL}
  networks:
    - hospital-network
```

### 3. Build và deploy
```bash
docker compose up -d --build doctor-service
```

## 🏗️ Microservices Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │
│   (Port 5000)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────┐    ┌─────▼─────┐    ┌─────▼─────┐
│Patient │    │  Doctor   │    │Appointment│
│Service │    │  Service  │    │  Service  │
│ 8001   │    │   8002    │    │   8003    │
└────────┘    └───────────┘    └───────────┘
    │              │                │
    └──────────────┼────────────────┘
                   │
            ┌─────▼─────┐
            │  MongoDB  │
            │   Atlas   │
            └───────────┘
```

## 🚨 Troubleshooting

### Port conflicts
```bash
# Tìm process sử dụng port
lsof -i :5000
lsof -i :8001

# Hoặc thay đổi port trong docker-compose.yml
ports:
  - "5001:5000"  # Host:Container
```

### Memory issues
```bash
# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory
```

### Build issues
```bash
# Clear cache
docker builder prune

# Rebuild without cache
docker compose build --no-cache
```
