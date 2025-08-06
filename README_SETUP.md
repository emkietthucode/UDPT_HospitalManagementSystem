# Hospital Management System - Setup Guide

## Yêu cầu hệ thống
- Docker và Docker Compose
- Python 3.9+
- Git

## Thiết lập Database

### 1. Khởi động PostgreSQL và Redis với Docker
```bash
# Khởi động services
docker-compose up -d

# Kiểm tra services đang chạy
docker-compose ps

# Xem logs nếu có lỗi
docker-compose logs postgres
docker-compose logs redis
```

### 2. Kết nối test database
```bash
# Kết nối vào PostgreSQL
docker exec -it hospital_postgres psql -U hospital_admin -d hospital_management

# Test commands trong psql:
\dt              # List tables
\l               # List databases  
\q               # Quit
```

### 3. Dừng services
```bash
# Dừng nhưng giữ data
docker-compose stop

# Dừng và xóa containers (giữ data)
docker-compose down

# Dừng và xóa tất cả (bao gồm data volumes)
docker-compose down -v
```

## Database Information
- **Host**: localhost:5432
- **Database**: hospital_management
- **Username**: hospital_admin
- **Password**: hospital_password
- **Connection String**: `postgresql://hospital_admin:hospital_password@localhost:5432/hospital_management`

## Redis Information
- **Host**: localhost:6379
- **Database**: 0

## Environment Setup
1. Copy file môi trường:
```bash
cp .env.example .env
```

2. Chỉnh sửa `.env` nếu cần thiết (thường không cần)

## Next Steps
1. Thiết kế database schema
2. Chọn Python framework (Django/Flask)
3. Tạo models và migrations
4. Implement business logic

## Troubleshooting

### Port đã được sử dụng
```bash
# Kiểm tra port 5432
lsof -i :5432

# Dừng PostgreSQL local nếu có
brew services stop postgresql  # macOS
sudo service postgresql stop   # Linux
```

### Reset database
```bash
docker-compose down -v
docker-compose up -d
```