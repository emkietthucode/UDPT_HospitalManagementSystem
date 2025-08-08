# 🏥 Hospital Management Microservices - Quick Start Guide

## 🚀 Cài đặt và Chạy hệ thống trong 3 bước

### 1️⃣ Setup ban đầu (chỉ chạy 1 lần)
```bash
./quick-setup.sh
```

### 2️⃣ Chạy toàn bộ hệ thống
```bash
./start-all-services.sh
```

### 3️⃣ Dừng toàn bộ hệ thống khi cần
```bash
./stop-all-services.sh
```

## 📊 Hệ thống sẽ chạy tại

| Service | Port | URL | Database |
|---------|------|-----|----------|
| **🔒 Insurance Service** | 8002 | http://localhost:8002/docs | `insurance_service_db` |
| **👥 Patient Service** | 8001 | http://localhost:8001/docs | `hospital_management` |
| **🌐 Web Application** | 5000 | http://localhost:5000 | - |

## 🏗️ Kiến trúc Microservices

```
┌─────────────────────────────────────────────────────┐
│                🌐 Frontend Web App                   │
│              http://localhost:5000                  │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌─────────┐  ┌──────────┐  ┌─────────────┐
│🔒Insurance│  │👥 Patient  │  │   Other     │
│ Service  │  │ Service  │  │ Services    │
│  :8002   │  │  :8001   │  │   ...       │
└────┬────┘  └────┬─────┘  └─────────────┘
     │            │
     ▼            ▼
┌───────────┐ ┌──────────────┐
│insurance_ │ │ hospital_    │
│service_db │ │ management   │
│(MongoDB)  │ │  (MongoDB)   │
└───────────┘ └──────────────┘
```

## ✅ Kiểm tra hệ thống hoạt động

```bash
# Kiểm tra Insurance Service
curl http://localhost:8002/health

# Kiểm tra Patient Service  
curl http://localhost:8001/health

# Xem danh sách thẻ BHYT có sẵn
curl http://localhost:8002/api/v1/insurance/cards
```

## 🎯 Tính năng chính

### 🔒 Insurance Service (BHYT)
- ✅ Validate thẻ BHYT theo format chuẩn
- ✅ Quản lý database riêng cho thẻ bảo hiểm  
- ✅ Tính toán coverage percentage
- ✅ 8 thẻ BHYT mẫu từ các tỉnh khác nhau

### 👥 Patient Service  
- ✅ Quản lý thông tin bệnh nhân
- ✅ Tích hợp với Insurance Service
- ✅ Database riêng cho medical records

### 🌐 Web Application
- ✅ Giao diện quản lý bệnh nhân
- ✅ Validate BHYT trực tuyến
- ✅ Responsive design với Bootstrap

## 🔍 Troubleshooting

### Nếu port bị chiếm:
```bash
./stop-all-services.sh
./start-all-services.sh
```

### Kiểm tra services đang chạy:
```bash
lsof -i :8001 :8002 :5000
```

### Xem logs:
```bash
# Insurance Service logs
curl http://localhost:8002/health

# Patient Service logs  
curl http://localhost:8001/health
```

---

**🎓 Phát triển cho môn UDPT - HCMUS**

Để xem tài liệu chi tiết, tham khảo:
- `README.md` - Tài liệu đầy đủ
- `MICROSERVICES_GUIDE.md` - Hướng dẫn kiến trúc
- `SETUP_GUIDE.md` - Setup chi tiết
