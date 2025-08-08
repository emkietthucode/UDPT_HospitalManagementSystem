# Hospital Management System - Microservices

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│    Services     │
│   (Port 5000)   │     │   (Port 8000)   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
            ┌───────▼──────┐ ┌──▼──┐ ┌───────▼──────┐
            │ Patient Svc  │ │ ... │ │ Doctor Svc   │
            │   (8001)     │ │     │ │   (8002)     │
            └──────────────┘ └─────┘ └──────────────┘
                    │                        │
                    └──────────┬─────────────┘
                               │
                    ┌─────────▼─────────┐
                    │   MongoDB Atlas   │
                    │   (Cloud DB)      │
                    └───────────────────┘
```

## 📦 Services

### ✅ Implemented
- **Patient Service** (Port 8001) - Quản lý bệnh nhân
- **Web Frontend** (Port 5000) - Giao diện người dùng

### 🚧 Planned (Templates ready)
- **API Gateway** (Port 8000) - Entry point chính
- **Doctor Service** (Port 8002) - Quản lý bác sĩ  
- **Appointment Service** (Port 8003) - Quản lý lịch hẹn
- **Prescription Service** (Port 8004) - Quản lý đơn thuốc
- **Notification Service** (Port 8005) - Thông báo

## 🐳 Deployment Options

### Option 1: Traditional Python (Current)
```bash
./quick-setup.sh
cd services/patient-service
python run-all.py
```

### Option 2: Docker Microservices (Scalable)
```bash
docker compose up --build
```

## 🚀 Getting Started

### Prerequisites
- **Traditional:** Python 3.9+
- **Docker:** Docker Desktop

### Quick Start
1. Choose deployment method above
2. Configure MongoDB in `.env`
3. Access http://localhost:5000

## 📁 Project Structure

```
UDPT_HospitalManagementSystem/
├── services/
│   ├── patient-service/          # ✅ Implemented
│   │   ├── backend/              # FastAPI + MongoDB
│   │   ├── frontend/             # Flask Web UI
│   │   └── run-all.py           
│   ├── doctor-service/           # 🚧 Template ready
│   ├── appointment-service/      # 🚧 Template ready
│   └── api-gateway/             # 🚧 Template ready
├── docker-compose.yml           # Multi-service orchestration
├── SETUP_GUIDE.md              # Python setup
├── DOCKER_GUIDE.md             # Docker setup
└── README_TEAM.md              # Quick start
```

## 🛠️ Tech Stack

- **Backend:** FastAPI, Motor (MongoDB async)
- **Frontend:** Flask, Jinja2
- **Database:** MongoDB Atlas
- **Containerization:** Docker, Docker Compose
- **Communication:** REST APIs (future: RabbitMQ)

## 📋 Next Steps

1. **Current:** Patient management working
2. **Phase 1:** Add Doctor service
3. **Phase 2:** Add Appointment service  
4. **Phase 3:** Add API Gateway
5. **Phase 4:** Add async communication (RabbitMQ)
