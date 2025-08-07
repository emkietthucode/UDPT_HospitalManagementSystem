# 🚀 Quick Start Guide - Team Setup

## Chỉ cần 3 bước đơn giản:

### 1️⃣ Pull code và chạy setup
```bash
git clone https://github.com/emkietthucode/UDPT_HospitalManagementSystem.git
cd UDPT_HospitalManagementSystem
./quick-setup.sh  # MacOS/Linux
# hoặc quick-setup.bat  # Windows
```

### 2️⃣ Cấu hình MongoDB
Mở file `services/patient-service/backend/.env` và cập nhật:
```bash
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/hospital_management
```

**Lưu ý:** Thay `your-username`, `your-password`, `your-cluster` bằng thông tin MongoDB Atlas thật của team.

### 3️⃣ Chạy ứng dụng
```bash
cd services/patient-service
python run-all.py
```

## ✅ Kiểm tra kết quả:
- 🌐 **Website:** http://127.0.0.1:5000
- 📡 **API:** http://127.0.0.1:8001/docs

---

## 🆘 Nếu gặp lỗi:

### MongoDB Connection Error:
- Kiểm tra connection string trong `.env`
- Đảm bảo IP được whitelist trong MongoDB Atlas
- Kiểm tra username/password

### Python/Pip Error:
```bash
# Cài lại dependencies
cd services/patient-service/backend
source venv/bin/activate  # MacOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt --force-reinstall
```

### Port đã được sử dụng:
```bash
# Tìm và kill process
lsof -i :5000  # Frontend
lsof -i :8001  # Backend
kill -9 <PID>
```

## 📞 Cần hỗ trợ?
- Xem hướng dẫn chi tiết: `SETUP_GUIDE.md`
- Tạo issue trong repository
- Liên hệ team lead
