# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hospital Management System built for the UDPT (Distributed Applications) course at HCMUS. The system manages hospital operations including patient registration, appointment scheduling, prescription management, BHYT integration, and notifications.

**Current Status**: Starting with a Python monolith implementation to develop UI rapidly, then migrate to microservices architecture.

**Implementation Strategy**: 
1. **Phase 1**: Build Python monolith with full functionality and UI
2. **Phase 2**: Migrate to microservices architecture with RabbitMQ

## System Architecture

### Phase 1: Python Monolith Architecture
- **Framework**: Django/Flask with MVC pattern
- **Database**: PostgreSQL for main data, Redis for caching
- **Authentication**: Django/Flask built-in auth with role-based permissions
- **UI**: Server-side rendered templates with minimal JavaScript
- **File Structure**:
```
hospital_system/
├── app/
│   ├── models/          # Database models
│   ├── views/           # View controllers  
│   ├── templates/       # HTML templates
│   ├── services/        # Business logic
│   └── utils/           # Helper functions
├── static/              # CSS/JS files
├── requirements.txt     # Python dependencies
└── manage.py           # Django management
```

### Phase 2: Target Microservices Design
- **Patient Service**: Patient registration, information management, medical records
- **Appointment Service**: Scheduling, doctor assignments, appointment management  
- **Prescription Service**: Medicine prescriptions, dispensing status tracking
- **Notification Service**: Email/SMS reminders for appointments and prescriptions
- **Billing Service**: Payment processing and BHYT integration
- **Testing Service**: Laboratory and diagnostic services
- **Reporting Service**: Patient statistics and prescription reports

### Technology Requirements
- **Backend**: Python (Django/Flask) with MVC framework
- **Frontend**: Server-side templates (Jinja2/Django templates)
- **Database**: PostgreSQL for relational data
- **Message Queue**: RabbitMQ (Phase 2)
- **Communication**: REST API endpoints

### Performance Requirements
- Handle 100+ requests/second during peak hours
- API response time < 1 second
- Database query optimization

## Functional Requirements (Chi tiết từ SRS)

### FR-1: Quản lý Bệnh nhân
- **FR-1.1**: Nhân viên lễ tân đăng ký thông tin cho bệnh nhân mới
- **FR-1.2**: Tra cứu thông tin bệnh nhân qua số điện thoại, mã BN, tên + năm sinh
- **FR-1.3**: Lưu trữ hồ sơ bệnh án và lịch sử khám chữa bệnh  
- **FR-1.4**: Bệnh nhân tự đăng ký thông tin
- **FR-1.5**: Bệnh nhân xem hồ sơ cá nhân, lịch sử khám bệnh

### FR-2: Quản lý Lịch khám
- **FR-2.1**: Đặt lịch khám theo chuyên khoa/bác sĩ/ngày khám
- **FR-2.2**: Bác sĩ xem và xác nhận lịch khám của mình

### FR-3: Quản lý Khám bệnh & Chỉ định Dịch vụ
- **FR-3.1**: Bác sĩ truy cập hồ sơ bệnh án trong quá trình khám
- **FR-3.2**: Bác sĩ tạo phiếu chỉ định dịch vụ CLS

### FR-4: Quản lý Thanh toán & BHYT
- **FR-4.1**: Kết nối Cổng giám định BHYT để xác thực thẻ
- **FR-4.2**: Tính toán chi phí đồng chi trả cho BHYT
- **FR-4.3**: Tính toán 100% chi phí dịch vụ tự trả
- **FR-4.4**: Ghi nhận giao dịch thanh toán và xuất hóa đơn

### FR-5: Quản lý Đơn thuốc
- **FR-5.1**: Bác sĩ tạo đơn thuốc điện tử
- **FR-5.2**: Dược sĩ cập nhật trạng thái đơn thuốc (đã lấy/chưa lấy)

### FR-6: Quản lý Thông báo
- **FR-6.1**: Tự động gửi nhắc nhở lịch khám qua Email/SMS
- **FR-6.2**: Thông báo khi đơn thuốc sẵn sàng

### FR-7: Báo cáo và Thống kê
- **FR-7.1**: Thống kê số lượng bệnh nhân theo tháng
- **FR-7.2**: Báo cáo số lượng đơn thuốc đã cấp

## User Roles (Actors)
- **Bệnh nhân**: Đăng ký, đặt lịch, xem hồ sơ
- **Nhân viên tiếp đón**: Đăng ký BN, kiểm tra BHYT, tạo lịch khám
- **Bác sĩ**: Khám bệnh, chỉ định CLS, kê đơn thuốc
- **Kỹ thuật viên**: Thực hiện xét nghiệm, cập nhật kết quả
- **Dược sĩ**: Soạn thuốc, cập nhật trạng thái đơn thuốc
- **Quản trị viên**: Quản lý hệ thống, xem báo cáo

## Core Workflows

### Luồng BHYT (Có bảo hiểm)
1. **Tiếp đón**: Kiểm tra thẻ BHYT → Đăng ký khám → Tạo phiếu khám
2. **Khám bệnh**: Tra cứu hồ sơ → Khám lâm sàng → Chỉ định CLS (nếu cần)
3. **Xét nghiệm**: Thực hiện CLS → Cập nhật kết quả → Thông báo
4. **Kết luận**: Xem kết quả → Chẩn đoán → Kê đơn thuốc
5. **Lãnh thuốc**: Soạn thuốc → Cấp phát → Cập nhật trạng thái

### Luồng Tự trả (Không bảo hiểm)
1. **Đăng ký**: Tạo hồ sơ → Thanh toán phí khám → Tạo phiếu khám
2. **Các bước tiếp theo**: Tương tự luồng BHYT nhưng thanh toán 100%

## Implementation Guidelines

### Phase 1 Development Commands
- **Setup**: `pip install -r requirements.txt`
- **Migration**: `python manage.py migrate` (Django) hoặc `flask db upgrade` (Flask)
- **Run server**: `python manage.py runserver` hoặc `flask run`
- **Create superuser**: `python manage.py createsuperuser` (Django)

### Database Models cần thiết
- **User**: Authentication + roles
- **Patient**: Thông tin bệnh nhân
- **Doctor**: Thông tin bác sĩ + chuyên khoa  
- **Appointment**: Lịch khám bệnh
- **Prescription**: Đơn thuốc
- **Medicine**: Danh mục thuốc
- **LabTest**: Xét nghiệm CLS
- **Payment**: Thanh toán
- **Notification**: Thông báo

### Security Requirements
- Role-based authentication (Patient/Staff/Doctor/Admin)
- Encrypt sensitive data (phone, email, health records)
- Session management
- CSRF protection
- Healthcare data privacy compliance

### Development Notes
- Start with Django Admin interface for quick CRUD operations
- Use Django/Flask built-in authentication
- Implement responsive UI with Bootstrap/Tailwind
- Add API endpoints for future mobile app
- Use Django ORM/SQLAlchemy for database operations
- Implement proper error handling and logging

## Testing & Quality
- Unit tests for business logic
- Integration tests for workflows
- Test coverage for critical paths
- Manual testing for UI workflows

## Documentation Requirements
1. Use case diagrams và sequence diagrams
2. Database schema documentation  
3. API documentation (for Phase 2)
4. User manual cho từng role
5. Demo video (3-5 phút)