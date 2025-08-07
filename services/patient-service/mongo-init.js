// MongoDB initialization script
// This script will be executed when the MongoDB container starts

// Switch to the hospital_management database
use('hospital_management');

// Create the patients collection with some sample data
db.patients.insertMany([
  {
    full_name: "Nguyễn Văn An",
    phone: "0901234567",
    email: "nguyenvanan@email.com",
    address: "123 Lê Lợi, Quận 1, TP.HCM",
    date_of_birth: "1990-01-15",
    gender: "Nam",
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    full_name: "Trần Thị Bình",
    phone: "0987654321",
    email: "tranthibinh@email.com",
    address: "456 Nguyễn Huệ, Quận 1, TP.HCM",
    date_of_birth: "1985-05-20",
    gender: "Nữ",
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    full_name: "Lê Minh Cường",
    phone: "0912345678",
    email: "leminhcuong@email.com",
    address: "789 Trần Hưng Đạo, Quận 5, TP.HCM",
    date_of_birth: "1992-12-10",
    gender: "Nam",
    created_at: new Date(),
    updated_at: new Date()
  }
]);

// Create indexes for better performance
db.patients.createIndex({ "email": 1 }, { unique: true });
db.patients.createIndex({ "phone": 1 }, { unique: true });
db.patients.createIndex({ "full_name": 1 });

print("MongoDB initialization completed successfully!");
