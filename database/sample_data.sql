-- Hospital Management System - Sample Data
-- This file contains sample data for development and testing

-- ============================================================================
-- SAMPLE SPECIALTIES
-- ============================================================================

INSERT INTO specialties (name, description) VALUES
('Khoa Nội Tổng Hợp', 'Khám và điều trị các bệnh nội khoa tổng quát'),
('Khoa Tim Mạch', 'Chuyên về các bệnh lý tim mạch'),
('Khoa Tiêu Hóa', 'Điều trị các bệnh về đường tiêu hóa'),
('Khoa Thận - Tiết Niệu', 'Chuyên về các bệnh thận và tiết niệu'),
('Khoa Tai Mũi Họng', 'Khám và điều trị bệnh tai mũi họng'),
('Khoa Mắt', 'Chuyên khoa mắt'),
('Khoa Da Liễu', 'Điều trị các bệnh về da'),
('Khoa Xương Khớp', 'Chuyên về xương khớp và chấn thương');

-- ============================================================================
-- SAMPLE USERS
-- ============================================================================

-- Admin user
INSERT INTO users (id, username, email, password_hash, role, status) VALUES
('11111111-1111-1111-1111-111111111111', 'admin', 'admin@hospital.com', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla', -- password: admin123
 'admin', 'active');

-- Reception staff
INSERT INTO users (id, username, email, password_hash, role, status) VALUES
('22222222-2222-2222-2222-222222222222', 'reception1', 'reception1@hospital.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla', -- password: admin123
 'reception_staff', 'active'),
('22222222-2222-2222-2222-222222222223', 'reception2', 'reception2@hospital.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla',
 'reception_staff', 'active');

-- Doctors
INSERT INTO users (id, username, email, password_hash, role, status) VALUES
('33333333-3333-3333-3333-333333333331', 'doctor1', 'nguyen.van.a@hospital.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla',
 'doctor', 'active'),
('33333333-3333-3333-3333-333333333332', 'doctor2', 'tran.thi.b@hospital.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla',
 'doctor', 'active'),
('33333333-3333-3333-3333-333333333333', 'doctor3', 'le.van.c@hospital.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla',
 'doctor', 'active');

-- Pharmacists
INSERT INTO users (id, username, email, password_hash, role, status) VALUES
('44444444-4444-4444-4444-444444444444', 'pharmacist1', 'pharmacist1@hospital.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla',
 'pharmacist', 'active');

-- Technicians
INSERT INTO users (id, username, email, password_hash, role, status) VALUES
('55555555-5555-5555-5555-555555555555', 'technician1', 'tech1@hospital.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla',
 'technician', 'active');

-- Patient users (some patients have accounts)
INSERT INTO users (id, username, email, password_hash, role, status) VALUES
('66666666-6666-6666-6666-666666666661', 'patient1', 'patient1@gmail.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla',
 'patient', 'active'),
('66666666-6666-6666-6666-666666666662', 'patient2', 'patient2@gmail.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj.8jOlZ4xla',
 'patient', 'active');

-- ============================================================================
-- SAMPLE DOCTORS
-- ============================================================================

INSERT INTO doctors (id, user_id, doctor_code, full_name, phone_number, email, specialty_id, license_number, consultation_fee) 
SELECT 
    uuid_generate_v4(),
    '33333333-3333-3333-3333-333333333331',
    'BS001',
    'Bác sĩ Nguyễn Văn An',
    '0901234567',
    'nguyen.van.a@hospital.com',
    s.id,
    'BS123456789',
    200000
FROM specialties s WHERE s.name = 'Khoa Tim Mạch';

INSERT INTO doctors (id, user_id, doctor_code, full_name, phone_number, email, specialty_id, license_number, consultation_fee)
SELECT 
    uuid_generate_v4(),
    '33333333-3333-3333-3333-333333333332',
    'BS002',
    'Bác sĩ Trần Thị Bình',
    '0901234568',
    'tran.thi.b@hospital.com',
    s.id,
    'BS123456790',
    180000
FROM specialties s WHERE s.name = 'Khoa Tiêu Hóa';

INSERT INTO doctors (id, user_id, doctor_code, full_name, phone_number, email, specialty_id, license_number, consultation_fee)
SELECT 
    uuid_generate_v4(),
    '33333333-3333-3333-3333-333333333333',
    'BS003',
    'Bác sĩ Lê Văn Cường',
    '0901234569',
    'le.van.c@hospital.com',
    s.id,
    'BS123456791',
    150000
FROM specialties s WHERE s.name = 'Khoa Nội Tổng Hợp';

-- ============================================================================
-- SAMPLE STAFF
-- ============================================================================

INSERT INTO staff (user_id, staff_code, full_name, phone_number, email, department, position) VALUES
('22222222-2222-2222-2222-222222222222', 'NV001', 'Nguyễn Thị Hoa', '0987654321', 'reception1@hospital.com', 'Tiếp đón', 'Nhân viên tiếp đón'),
('22222222-2222-2222-2222-222222222223', 'NV002', 'Trần Văn Nam', '0987654322', 'reception2@hospital.com', 'Tiếp đón', 'Nhân viên tiếp đón'),
('44444444-4444-4444-4444-444444444444', 'DS001', 'Phạm Thị Lan', '0987654323', 'pharmacist1@hospital.com', 'Nhà thuốc', 'Dược sĩ'),
('55555555-5555-5555-5555-555555555555', 'KTV001', 'Lê Quang Minh', '0987654324', 'tech1@hospital.com', 'Xét nghiệm', 'Kỹ thuật viên');

-- ============================================================================
-- SAMPLE PATIENTS
-- ============================================================================

INSERT INTO patients (id, user_id, full_name, date_of_birth, gender, phone_number, email, address, 
                     insurance_number, insurance_valid_from, insurance_valid_to, insurance_hospital_code,
                     created_by) VALUES
('77777777-7777-7777-7777-777777777771', 
 '66666666-6666-6666-6666-666666666661',
 'Nguyễn Văn Bình', 
 '1985-03-15', 
 'male', 
 '0912345678',
 'patient1@gmail.com',
 '123 Đường Nguyễn Văn Cừ, Quận 5, TP.HCM',
 'HS4010001234567',
 '2024-01-01',
 '2024-12-31',
 '79024',
 '22222222-2222-2222-2222-222222222222');

INSERT INTO patients (id, user_id, full_name, date_of_birth, gender, phone_number, email, address,
                     created_by) VALUES
('77777777-7777-7777-7777-777777777772',
 '66666666-6666-6666-6666-666666666662', 
 'Trần Thị Cẩm',
 '1990-07-20',
 'female',
 '0912345679',
 'patient2@gmail.com',
 '456 Đường Lê Văn Sỹ, Quận 3, TP.HCM',
 '22222222-2222-2222-2222-222222222222');

-- Patient without user account (walk-in)
INSERT INTO patients (id, full_name, date_of_birth, gender, phone_number, address,
                     insurance_number, insurance_valid_from, insurance_valid_to, insurance_hospital_code,
                     created_by) VALUES
('77777777-7777-7777-7777-777777777773',
 'Phạm Minh Đức',
 '1975-12-10',
 'male',
 '0912345680',
 '789 Đường Cách Mạng Tháng 8, Quận 10, TP.HCM',
 'HS4010009876543',
 '2024-01-01',
 '2024-12-31', 
 '79024',
 '22222222-2222-2222-2222-222222222222');

-- ============================================================================
-- SAMPLE MEDICATION CATEGORIES
-- ============================================================================

INSERT INTO medication_categories (name, description) VALUES
('Kháng sinh', 'Các loại thuốc kháng sinh điều trị nhiễm khuẩn'),
('Giảm đau', 'Thuốc giảm đau và kháng viêm'),
('Tim mạch', 'Thuốc điều trị các bệnh tim mạch'),
('Tiêu hóa', 'Thuốc điều trị các bệnh tiêu hóa'),
('Vitamin', 'Các loại vitamin và thực phẩm bổ sung'),
('Hô hấp', 'Thuốc điều trị các bệnh về đường hô hấp');

-- ============================================================================
-- SAMPLE MEDICATIONS
-- ============================================================================

INSERT INTO medications (code, name, generic_name, category_id, strength, dosage_form, manufacturer, unit_price, unit)
SELECT 'MED001', 'Paracetamol 500mg', 'Paracetamol', c.id, '500mg', 'Viên nén', 'Pharma ABC', 500, 'viên'
FROM medication_categories c WHERE c.name = 'Giảm đau';

INSERT INTO medications (code, name, generic_name, category_id, strength, dosage_form, manufacturer, unit_price, unit)
SELECT 'MED002', 'Amoxicillin 250mg', 'Amoxicillin', c.id, '250mg', 'Viên con nhộng', 'Pharma XYZ', 1200, 'viên'
FROM medication_categories c WHERE c.name = 'Kháng sinh';

INSERT INTO medications (code, name, generic_name, category_id, strength, dosage_form, manufacturer, unit_price, unit)
SELECT 'MED003', 'Omeprazole 20mg', 'Omeprazole', c.id, '20mg', 'Viên con nhộng', 'Pharma DEF', 2500, 'viên'  
FROM medication_categories c WHERE c.name = 'Tiêu hóa';

INSERT INTO medications (code, name, generic_name, category_id, strength, dosage_form, manufacturer, unit_price, unit)
SELECT 'MED004', 'Vitamin B Complex', 'Vitamin B Complex', c.id, '1 viên', 'Viên nén', 'Pharma GHI', 800, 'viên'
FROM medication_categories c WHERE c.name = 'Vitamin';

-- ============================================================================
-- SAMPLE TEST TYPES
-- ============================================================================

INSERT INTO test_types (code, name, category, description, normal_range, unit, price) VALUES
('XN001', 'Công thức máu toàn phần', 'blood_test', 'Xét nghiệm tổng quát về các chỉ số máu', 'Theo giới tính và tuổi', '', 150000),
('XN002', 'Glucose máu đói', 'blood_test', 'Đường huyết lúc đói', '3.9-5.5', 'mmol/L', 80000),
('XN003', 'Cholesterol toàn phần', 'blood_test', 'Tổng Cholesterol trong máu', '<5.2', 'mmol/L', 120000),
('XN004', 'Chụp X-quang ngực', 'imaging', 'Chụp X-quang lồng ngực', '', '', 200000),
('XN005', 'Siêu âm bụng tổng quát', 'imaging', 'Siêu âm các cơ quan trong ổ bụng', '', '', 300000),
('XN006', 'Xét nghiệm nước tiểu', 'urine_test', 'Xét nghiệm nước tiểu tổng quât', '', '', 100000);

-- ============================================================================
-- SAMPLE SERVICE TYPES
-- ============================================================================

INSERT INTO service_types (code, name, category, base_price, insurance_covered, insurance_coverage_percent) VALUES
('SV001', 'Khám nội tổng hợp', 'consultation', 150000, TRUE, 80),
('SV002', 'Khám tim mạch', 'consultation', 200000, TRUE, 80),
('SV003', 'Khám tiêu hóa', 'consultation', 180000, TRUE, 80),
('SV004', 'Khám tai mũi họng', 'consultation', 160000, TRUE, 80),
('SV005', 'Công thức máu toàn phần', 'lab_test', 150000, TRUE, 100),
('SV006', 'Chụp X-quang ngực', 'lab_test', 200000, TRUE, 100),
('SV007', 'Siêu âm bụng', 'lab_test', 300000, TRUE, 100),
('SV008', 'Phí thuốc', 'medication', 0, TRUE, 80);

-- ============================================================================
-- SAMPLE APPOINTMENTS (for today and upcoming days)
-- ============================================================================

-- Today's appointments
INSERT INTO appointments (patient_id, doctor_id, specialty_id, appointment_date, appointment_time, 
                         status, appointment_type, chief_complaint, created_by)
SELECT 
    '77777777-7777-7777-7777-777777777771',
    d.id,
    d.specialty_id,
    CURRENT_DATE,
    '09:00:00',
    'scheduled',
    'new_patient',
    'Đau ngực, khó thở',
    '22222222-2222-2222-2222-222222222222'
FROM doctors d WHERE d.doctor_code = 'BS001';

INSERT INTO appointments (patient_id, doctor_id, specialty_id, appointment_date, appointment_time,
                         status, appointment_type, chief_complaint, created_by)
SELECT 
    '77777777-7777-7777-7777-777777777772',
    d.id, 
    d.specialty_id,
    CURRENT_DATE,
    '10:30:00',
    'confirmed',
    'consultation',
    'Đau bụng, khó tiêu',
    '22222222-2222-2222-2222-222222222222'
FROM doctors d WHERE d.doctor_code = 'BS002';

-- Tomorrow's appointment
INSERT INTO appointments (patient_id, doctor_id, specialty_id, appointment_date, appointment_time,
                         status, appointment_type, chief_complaint, created_by)
SELECT 
    '77777777-7777-7777-7777-777777777773',
    d.id,
    d.specialty_id,
    CURRENT_DATE + 1,
    '14:00:00',
    'scheduled',
    'follow_up',
    'Tái khám định kỳ',
    '22222222-2222-2222-2222-222222222222'
FROM doctors d WHERE d.doctor_code = 'BS003';