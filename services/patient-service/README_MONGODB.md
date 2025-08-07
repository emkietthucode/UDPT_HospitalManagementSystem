# Patient Service với MongoDB

Patient Service đã được chuyển đổi từ SQLite sang MongoDB để có hiệu suất và khả năng mở rộng tốt hơn.

## 🛠️ Cài đặt và Chạy

### Phương pháp 1: Sử dụng Docker (Khuyên dùng)

1. **Cài đặt Docker và Docker Compose**
   ```bash
   # Kiểm tra Docker đã cài đặt chưa
   docker --version
   docker-compose --version
   ```

2. **Chạy ứng dụng với MongoDB**
   ```bash
   # Cấp quyền thực thi cho script
   chmod +x run-mongodb.sh
   
   # Chạy script
   ./run-mongodb.sh
   ```

   Hoặc chạy trực tiếp với docker-compose:
   ```bash
   docker-compose up -d
   ```

### Phương pháp 2: Chạy thủ công

1. **Cài đặt MongoDB**
   ```bash
   # macOS với Homebrew
   brew install mongodb-community
   brew services start mongodb-community
   
   # Ubuntu/Debian
   sudo apt-get install mongodb
   sudo systemctl start mongodb
   ```

2. **Cài đặt Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Chạy backend**
   ```bash
   python run-be.py
   ```

## 🗄️ Cấu trúc Database

### Collection: patients
```javascript
{
  "_id": ObjectId("..."),
  "full_name": "Nguyễn Văn A",
  "phone": "0901234567",
  "email": "nguyenvana@email.com",
  "address": "123 Lê Lợi, Quận 1, TP.HCM",
  "date_of_birth": "1990-01-15",
  "gender": "Nam",
  "created_at": ISODate("2024-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

### Indexes
- `email`: unique index
- `phone`: unique index  
- `full_name`: regular index for search

## 🔗 API Endpoints

Tất cả endpoints giữ nguyên, chỉ thay đổi:
- `patient_id` từ integer thành MongoDB ObjectId string
- Response model có `id` field thay vì `patient_id`

### Ví dụ:
```bash
# Tạo patient mới
curl -X POST "http://localhost:8001/api/v1/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Nguyễn Văn A",
    "phone": "0901234567", 
    "email": "nguyenvana@email.com",
    "address": "123 Lê Lợi, Quận 1, TP.HCM",
    "date_of_birth": "1990-01-15",
    "gender": "Nam"
  }'

# Lấy patient theo ID (ObjectId)
curl "http://localhost:8001/api/v1/patients/64f7a1234567890abcdef123"
```

## 🌐 Truy cập Services

- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **MongoDB**: mongodb://localhost:27017

## ⚙️ Cấu hình

Chỉnh sửa file `.env` trong thư mục `backend/`:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=hospital_management
COLLECTION_NAME=patients
```

## 🔄 Migration từ SQLite

Nếu bạn có dữ liệu từ SQLite cũ, có thể tạo script migration để chuyển đổi:

```python
# migration_script.py
import sqlite3
import pymongo
from datetime import datetime

# Kết nối SQLite cũ
sqlite_conn = sqlite3.connect('patients.db')
sqlite_cursor = sqlite_conn.cursor()

# Kết nối MongoDB mới
mongo_client = pymongo.MongoClient('mongodb://localhost:27017')
mongo_db = mongo_client['hospital_management']
patients_collection = mongo_db['patients']

# Lấy dữ liệu từ SQLite
sqlite_cursor.execute("SELECT * FROM patients")
patients = sqlite_cursor.fetchall()

# Chuyển đổi và insert vào MongoDB
for patient in patients:
    patient_doc = {
        "full_name": patient[1],
        "phone": patient[2], 
        "email": patient[3],
        "address": patient[4],
        "date_of_birth": patient[5],
        "gender": patient[6],
        "created_at": patient[7] or datetime.utcnow(),
        "updated_at": patient[8] or datetime.utcnow()
    }
    patients_collection.insert_one(patient_doc)
```

## 🚫 Troubleshooting

### MongoDB connection issues
```bash
# Kiểm tra MongoDB đang chạy
docker ps | grep mongo
# hoặc
brew services list | grep mongodb

# Xem logs MongoDB
docker logs patient_service_mongodb
```

### Backend issues
```bash
# Xem logs backend
docker logs patient_backend

# Chạy backend local để debug
cd backend
MONGODB_URL=mongodb://localhost:27017 python main.py
```
