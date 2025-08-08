# 🚀 Quick Start Guide - Hospital Management Microservices

## 🏗️ **Kiến trúc Microservices:**

```
Frontend (Web UI) ──┐
                    ├──► Patient Service (8001)
                    └──► Insurance Service (8002) ──► BHYT Validation
```

## 🚀 **2 cách triển khai:**

### **Option 1: Traditional Python (Đơn giản)**
```bash
git clone <repo-url>
cd UDPT_HospitalManagementSystem
./quick-setup.sh
```

### **Option 2: Microservices với Docker (Professional)**
```bash
git clone <repo-url>
cd UDPT_HospitalManagementSystem
./microservices-setup.sh
```

## ⚙️ **Cấu hình MongoDB:**
Mở file `.env` và cập nhật:
```bash
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/hospital_management
```

## 🌐 **Truy cập Services:**
- **Web UI:** http://localhost:5000
- **Patient API:** http://localhost:8001/docs
- **Insurance API:** http://localhost:8002/docs

## 🧪 **Test BHYT với thẻ mẫu:**
- **HS4010123456789** - Nguyễn Văn A (15/01/1990)
- **HS4020987654321** - Khôi Nguyễn Đắc (20/05/1985)

## 🎯 **Features:**
- ✅ Quản lý bệnh nhân
- ✅ Xác thực thẻ BHYT
- ✅ Microservices architecture
- ✅ Docker containerization
- ✅ Service-to-service communication

---

## 🆘 **Nếu gặp lỗi:**

### **MongoDB Connection Error:**
- Kiểm tra connection string trong `.env`
- Đảm bảo IP được whitelist trong MongoDB Atlas

### **Docker Issues:**
```bash
# Restart services
docker compose down && docker compose up -d

# Rebuild services
docker compose up --build -d

# Check logs
docker compose logs -f
```

### **Python Issues (Traditional):**
```bash
# Reinstall dependencies
cd services/patient-service/backend
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 📞 **Cần hỗ trợ?**
- Xem hướng dẫn chi tiết: `SETUP_GUIDE.md` | `DOCKER_GUIDE.md`
- Microservices guide: `MICROSERVICES_GUIDE.md`
- Tạo issue trong repository
