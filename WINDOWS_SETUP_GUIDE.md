# 🪟 Windows Setup Guide - Hospital Management System

## Đã sửa lỗi cho Windows

Các file script gốc (`.sh`) được thiết kế cho Linux/macOS và không hoạt động trên Windows. Tôi đã tạo các file `.bat` tương ứng cho Windows:

### 📁 Files đã tạo:

| File gốc (Linux/macOS) | File Windows | Mô tả |
|-------------------------|--------------|-------|
| `quick-setup.sh` | `quick-setup.bat` | Cài đặt dependencies và tạo virtual environments |
| `start-all-services.sh` | `start-all-services.bat` | Khởi động tất cả services |
| `stop-all-services.sh` | `stop-all-services.bat` | Dừng tất cả services |
| - | `test-windows-setup.bat` | Kiểm tra hệ thống trước khi chạy |

### 🔧 Các lỗi đã sửa:

#### 1. **Bash Syntax → Batch Syntax**
```bash
# Linux/macOS (không hoạt động trên Windows)
#!/bin/bash
source venv/bin/activate

# Windows (đã sửa)
@echo off
call venv\Scripts\activate.bat
```

#### 2. **Đường dẫn Path Separators**
```bash
# Linux/macOS
services/patient-service/backend

# Windows (đã sửa)
services\patient-service\backend
```

#### 3. **Virtual Environment Activation**
```bash
# Linux/macOS
source venv/bin/activate
./venv/bin/python

# Windows (đã sửa)
call venv\Scripts\activate.bat
venv\Scripts\python.exe
```

#### 4. **Process Management**
```bash
# Linux/macOS
lsof -ti:8001 | xargs kill -9

# Windows (đã sửa)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001 "') do taskkill /F /PID %%a
```

#### 5. **Port Checking**
```bash
# Linux/macOS
lsof -Pi :8001 -sTCP:LISTEN

# Windows (đã sửa)
netstat -an | findstr ":8001 "
```

### 🚀 Hướng dẫn sử dụng trên Windows:

#### Bước 1: Kiểm tra hệ thống
```cmd
test-windows-setup.bat
```

#### Bước 2: Cài đặt dependencies
```cmd
quick-setup.bat
```

#### Bước 3: Cập nhật MongoDB connection
Chỉnh sửa các file `.env` trong:
- `services\insurance-service\.env`
- `services\patient-service\backend\.env`

#### Bước 4: Khởi động hệ thống
```cmd
start-all-services.bat
```

#### Bước 5: Dừng hệ thống (khi cần)
```cmd
stop-all-services.bat
```

### 📊 Services URLs:
- **Insurance Service API**: http://localhost:8002/docs
- **Patient Service API**: http://localhost:8001/docs  
- **Web Application**: http://localhost:5001

### ⚠️ Lưu ý quan trọng:

1. **Python Requirements**: Cần Python 3.9+ đã cài đặt
2. **MongoDB**: Cần cập nhật connection string trong file `.env`
3. **Ports**: Đảm bảo các port 8001, 8002, 5001 không bị sử dụng
4. **curl**: Có thể cần cài đặt curl để test services (hoặc dùng browser)

### 🐛 Troubleshooting:

#### Lỗi "Python not found":
```cmd
# Kiểm tra Python đã cài
python --version
# Hoặc
py --version
```

#### Lỗi "Port already in use":
```cmd
# Dừng tất cả services trước
stop-all-services.bat
# Sau đó khởi động lại
start-all-services.bat
```

#### Services không phản hồi:
1. Kiểm tra MongoDB connection trong file `.env`
2. Xem log trong các cửa sổ command đã mở
3. Kiểm tra Windows Firewall

### 📝 File structure sau khi setup:
```
UDPT_HospitalManagementSystem/
├── quick-setup.bat                     ✅ Windows setup
├── start-all-services.bat             ✅ Windows startup  
├── stop-all-services.bat              ✅ Windows stop
├── test-windows-setup.bat             ✅ Windows test
├── services/
│   ├── insurance-service/
│   │   ├── venv/                       ✅ Virtual env
│   │   ├── .env                        ✅ Config file
│   │   └── main.py
│   └── patient-service/
│       ├── backend/
│       │   ├── venv/                   ✅ Virtual env
│       │   ├── .env                    ✅ Config file
│       │   └── main.py
│       └── frontend/
│           ├── venv/                   ✅ Virtual env
│           └── app.py
```

### 🎯 Ready to go!
Hệ thống đã sẵn sàng chạy trên Windows với các scripts đã được tối ưu!