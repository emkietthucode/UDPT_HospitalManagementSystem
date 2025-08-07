# Hướng dẫn Setup Hospital Management System

## Yêu cầu hệ thống

- Python 3.9+
- MongoDB Atlas account (hoặc MongoDB local)
- Git

## Bước 1: Clone repository

```bash
git clone <repository-url>
cd UDPT_HospitalManagementSystem
```

## Bước 2: Cấu hình MongoDB

### Option 1: Sử dụng MongoDB Atlas (Khuyến nghị)
1. Tạo tài khoản MongoDB Atlas: https://www.mongodb.com/atlas
2. Tạo cluster mới
3. Lấy connection string có dạng: `mongodb+srv://username:password@cluster.mongodb.net/`

### Option 2: MongoDB Local
1. Cài đặt MongoDB Community: https://www.mongodb.com/try/download/community
2. Khởi động MongoDB service

## Bước 3: Setup Backend Service

```bash
# Di chuyển vào thư mục backend
cd services/patient-service/backend

# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
# MacOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## Bước 4: Cấu hình Database Connection

Tạo file `.env` trong thư mục `services/patient-service/backend/`:

```bash
# services/patient-service/backend/.env
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/hospital_management
```

**Lưu ý:** Thay thế `your-username`, `your-password`, và `your-cluster` bằng thông tin thực tế của bạn.

## Bước 5: Setup Frontend Service

```bash
# Mở terminal mới, di chuyển vào thư mục frontend
cd services/patient-service/frontend

# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
# MacOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## Bước 6: Chạy ứng dụng

### Cách 1: Chạy thủ công (2 terminal riêng biệt)

**Terminal 1 - Backend:**
```bash
cd services/patient-service/backend
source venv/bin/activate  # MacOS/Linux
# venv\Scripts\activate   # Windows
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd services/patient-service/frontend
source venv/bin/activate  # MacOS/Linux
# venv\Scripts\activate   # Windows
python app.py
```

### Cách 2: Sử dụng script tự động

```bash
cd services/patient-service
python run-all.py
```

## Bước 7: Truy cập ứng dụng

- **Frontend (Web UI):** http://127.0.0.1:5000
- **Backend API:** http://127.0.0.1:8001
- **API Documentation:** http://127.0.0.1:8001/docs

## Kiểm tra hoạt động

1. Mở browser và truy cập http://127.0.0.1:5000
2. Thử tạo bệnh nhân mới
3. Kiểm tra danh sách bệnh nhân
4. Test API tại http://127.0.0.1:8001/docs

## Troubleshooting

### Lỗi MongoDB Connection
- Kiểm tra connection string trong file `.env`
- Đảm bảo IP address được whitelist trong MongoDB Atlas
- Kiểm tra username/password chính xác

### Lỗi Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Lỗi Port đã được sử dụng
```bash
# Kiểm tra process đang sử dụng port
lsof -i :8001  # Backend port
lsof -i :5000  # Frontend port

# Kill process nếu cần
kill -9 <PID>
```

### Lỗi Virtual Environment
```bash
# Xóa và tạo lại venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Cấu trúc thư mục

```
services/patient-service/
├── backend/
│   ├── venv/              # Virtual environment
│   ├── main.py           # FastAPI backend
│   ├── requirements.txt  # Python dependencies
│   └── .env              # Database configuration
├── frontend/
│   ├── venv/              # Virtual environment
│   ├── app.py            # Flask frontend
│   ├── requirements.txt  # Python dependencies
│   └── templates/        # HTML templates
└── run-all.py            # Script chạy tự động
```

## Lưu ý quan trọng

1. **Không commit file `.env`** - chứa thông tin nhạy cảm
2. **Virtual environment** - luôn kích hoạt trước khi chạy
3. **MongoDB Atlas** - cần internet để kết nối
4. **Port conflicts** - đảm bảo port 5000 và 8001 không bị chiếm dụng

## Contact

Nếu gặp vấn đề, liên hệ team lead hoặc tạo issue trong repository.
