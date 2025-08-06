-- Hospital Management System Database Schema
-- Designed for Phase 1: Python Monolith Implementation

-- ============================================================================
-- USERS AND AUTHENTICATION
-- ============================================================================

-- User roles enum
CREATE TYPE user_role AS ENUM (
    'patient',
    'reception_staff', 
    'doctor',
    'technician',
    'pharmacist',
    'admin'
);

-- User status enum
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');

-- Main users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    status user_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- PATIENTS
-- ============================================================================

-- Patient gender enum
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other');

-- Patients table
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_code VARCHAR(20) UNIQUE NOT NULL, -- Mã bệnh nhân (auto-generated)
    user_id UUID REFERENCES users(id) ON DELETE SET NULL, -- NULL if patient doesn't have account
    
    -- Personal Information
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender gender_type NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(15),
    
    -- Health Insurance Information
    insurance_number VARCHAR(30), -- Số thẻ BHYT
    insurance_valid_from DATE,
    insurance_valid_to DATE,
    insurance_hospital_code VARCHAR(10), -- Mã bệnh viện đăng ký ban đầu
    
    -- System fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- ============================================================================
-- MEDICAL STAFF
-- ============================================================================

-- Medical specialties
CREATE TABLE specialties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Doctors table
CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_code VARCHAR(20) UNIQUE NOT NULL,
    
    -- Professional Information
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    email VARCHAR(100),
    specialty_id UUID REFERENCES specialties(id),
    license_number VARCHAR(50),
    qualification TEXT,
    
    -- Schedule Information
    is_available BOOLEAN DEFAULT TRUE,
    consultation_fee DECIMAL(10,2) DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Staff table (reception, technicians, pharmacists)
CREATE TABLE staff (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    staff_code VARCHAR(20) UNIQUE NOT NULL,
    
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    email VARCHAR(100),
    department VARCHAR(50),
    position VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- APPOINTMENTS AND EXAMINATIONS
-- ============================================================================

-- Appointment status enum
CREATE TYPE appointment_status AS ENUM (
    'scheduled',    -- Đã đặt lịch
    'confirmed',    -- Đã xác nhận
    'checked_in',   -- Đã check-in
    'in_progress',  -- Đang khám
    'completed',    -- Hoàn thành
    'cancelled',    -- Hủy bỏ
    'no_show'       -- Không đến
);

-- Appointment type enum
CREATE TYPE appointment_type AS ENUM (
    'new_patient',      -- Bệnh nhân mới
    'follow_up',        -- Tái khám
    'emergency',        -- Cấp cứu
    'consultation'      -- Tư vấn
);

-- Appointments table
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_code VARCHAR(20) UNIQUE NOT NULL,
    
    -- Core Information
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID NOT NULL REFERENCES doctors(id),
    specialty_id UUID REFERENCES specialties(id),
    
    -- Schedule Information
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    estimated_duration INTEGER DEFAULT 30, -- minutes
    
    -- Status and Type
    status appointment_status DEFAULT 'scheduled',
    appointment_type appointment_type DEFAULT 'consultation',
    
    -- Notes
    chief_complaint TEXT, -- Lý do khám
    notes TEXT, -- Ghi chú của reception
    
    -- System fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    -- Check-in information
    checked_in_at TIMESTAMP WITH TIME ZONE,
    checked_in_by UUID REFERENCES users(id)
);

-- Medical examinations (chi tiết buổi khám)
CREATE TABLE examinations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    
    -- Vital Signs
    blood_pressure VARCHAR(20), -- e.g., "120/80"
    heart_rate INTEGER,
    temperature DECIMAL(4,1), -- e.g., 36.5
    weight DECIMAL(5,2), -- kg
    height INTEGER, -- cm
    
    -- Clinical Information
    symptoms TEXT, -- Triệu chứng
    clinical_findings TEXT, -- Kết quả khám lâm sàng
    diagnosis TEXT, -- Chẩn đoán
    treatment_plan TEXT, -- Phương án điều trị
    
    -- System fields
    examination_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    examined_by UUID NOT NULL REFERENCES doctors(id),
    notes TEXT
);

-- ============================================================================
-- LABORATORY TESTS AND PROCEDURES
-- ============================================================================

-- Test types
CREATE TABLE test_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50), -- e.g., 'blood_test', 'imaging', 'urine_test'
    description TEXT,
    normal_range TEXT,
    unit VARCHAR(20),
    price DECIMAL(10,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Test status enum
CREATE TYPE test_status AS ENUM (
    'ordered',      -- Đã chỉ định
    'sample_taken', -- Đã lấy mẫu
    'in_progress',  -- Đang thực hiện
    'completed',    -- Hoàn thành
    'cancelled'     -- Hủy bỏ
);

-- Lab test orders
CREATE TABLE lab_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_code VARCHAR(20) UNIQUE NOT NULL,
    
    -- References
    examination_id UUID NOT NULL REFERENCES examinations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    test_type_id UUID NOT NULL REFERENCES test_types(id),
    
    -- Order Information
    ordered_by UUID NOT NULL REFERENCES doctors(id),
    ordered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Execution Information
    status test_status DEFAULT 'ordered',
    sample_taken_at TIMESTAMP WITH TIME ZONE,
    sample_taken_by UUID REFERENCES staff(id),
    
    -- Results
    result_value VARCHAR(500),
    result_notes TEXT,
    is_abnormal BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    completed_by UUID REFERENCES staff(id),
    
    -- System fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PRESCRIPTIONS AND MEDICATIONS
-- ============================================================================

-- Medication categories
CREATE TABLE medication_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Medications master data
CREATE TABLE medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    category_id UUID REFERENCES medication_categories(id),
    
    -- Drug Information
    strength VARCHAR(50), -- e.g., "500mg", "10ml"
    dosage_form VARCHAR(50), -- e.g., "tablet", "syrup", "injection"
    manufacturer VARCHAR(100),
    
    -- Pricing
    unit_price DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(20) DEFAULT 'tablet', -- đơn vị tính
    
    -- System fields
    is_active BOOLEAN DEFAULT TRUE,
    requires_prescription BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Prescription status enum
CREATE TYPE prescription_status AS ENUM (
    'prescribed',   -- Đã kê đơn
    'verified',     -- Đã dược sĩ kiểm tra
    'dispensed',    -- Đã cấp phát
    'cancelled'     -- Hủy bỏ
);

-- Prescriptions
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_code VARCHAR(20) UNIQUE NOT NULL,
    
    -- References
    examination_id UUID NOT NULL REFERENCES examinations(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    
    -- Prescription Information
    prescribed_by UUID NOT NULL REFERENCES doctors(id),
    prescribed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Status
    status prescription_status DEFAULT 'prescribed',
    
    -- Dispensing Information
    dispensed_by UUID REFERENCES staff(id), -- Dược sĩ
    dispensed_at TIMESTAMP WITH TIME ZONE,
    
    -- Notes
    instructions TEXT, -- Hướng dẫn sử dụng chung
    notes TEXT,
    
    -- System fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Prescription items (chi tiết từng thuốc)
CREATE TABLE prescription_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_id UUID NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
    medication_id UUID NOT NULL REFERENCES medications(id),
    
    -- Dosage Information
    quantity INTEGER NOT NULL, -- Số lượng
    dosage VARCHAR(100) NOT NULL, -- Liều dùng, e.g., "1 tablet twice daily"
    duration INTEGER, -- Số ngày dùng
    instructions TEXT, -- Hướng dẫn cụ thể cho thuốc này
    
    -- Pricing
    unit_price DECIMAL(10,2) DEFAULT 0,
    total_price DECIMAL(10,2) DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PAYMENTS AND BILLING
-- ============================================================================

-- Payment method enum
CREATE TYPE payment_method AS ENUM (
    'cash',
    'card',
    'bank_transfer',
    'insurance', -- BHYT
    'mixed'      -- Kết hợp nhiều phương thức
);

-- Payment status enum  
CREATE TYPE payment_status AS ENUM (
    'pending',
    'paid',
    'partially_paid',
    'refunded',
    'cancelled'
);

-- Service types for billing
CREATE TABLE service_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50), -- 'consultation', 'lab_test', 'medication', 'procedure'
    base_price DECIMAL(10,2) DEFAULT 0,
    insurance_covered BOOLEAN DEFAULT TRUE,
    insurance_coverage_percent DECIMAL(5,2) DEFAULT 80, -- % BHYT chi trả
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bills/Invoices
CREATE TABLE bills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_code VARCHAR(20) UNIQUE NOT NULL,
    
    -- References
    patient_id UUID NOT NULL REFERENCES patients(id),
    appointment_id UUID REFERENCES appointments(id),
    
    -- Bill Information
    bill_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    
    -- Amounts
    subtotal DECIMAL(12,2) DEFAULT 0,
    insurance_amount DECIMAL(12,2) DEFAULT 0, -- Số tiền BHYT chi trả
    patient_amount DECIMAL(12,2) DEFAULT 0,   -- Số tiền BN tự trả
    total_amount DECIMAL(12,2) DEFAULT 0,
    
    -- Payment Information
    payment_status payment_status DEFAULT 'pending',
    payment_method payment_method,
    payment_date TIMESTAMP WITH TIME ZONE,
    
    -- Insurance Information
    uses_insurance BOOLEAN DEFAULT FALSE,
    insurance_claim_code VARCHAR(50),
    
    -- Notes
    notes TEXT,
    
    -- System fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bill items
CREATE TABLE bill_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_id UUID NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
    service_type_id UUID REFERENCES service_types(id),
    
    -- Item Information
    description VARCHAR(200) NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    
    -- Insurance coverage
    insurance_covered BOOLEAN DEFAULT FALSE,
    insurance_amount DECIMAL(10,2) DEFAULT 0,
    patient_amount DECIMAL(10,2) DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NOTIFICATIONS
-- ============================================================================

-- Notification type enum
CREATE TYPE notification_type AS ENUM (
    'appointment_reminder',
    'prescription_ready', 
    'test_result_ready',
    'payment_due',
    'general'
);

-- Notification status enum
CREATE TYPE notification_status AS ENUM (
    'pending',
    'sent',
    'delivered',
    'failed',
    'cancelled'
);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Recipients
    patient_id UUID REFERENCES patients(id),
    user_id UUID REFERENCES users(id),
    
    -- Content
    type notification_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    
    -- Delivery Information
    delivery_method VARCHAR(20) NOT NULL, -- 'email', 'sms', 'in_app'
    recipient_address VARCHAR(200), -- email or phone number
    
    -- Status
    status notification_status DEFAULT 'pending',
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    
    -- References (optional)
    appointment_id UUID REFERENCES appointments(id),
    prescription_id UUID REFERENCES prescriptions(id),
    bill_id UUID REFERENCES bills(id),
    
    -- System fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT -- Lỗi nếu gửi không thành công
);

-- ============================================================================
-- SYSTEM AUDIT AND LOGS  
-- ============================================================================

-- Audit log for tracking changes
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- What was changed
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    
    -- Who made the change
    user_id UUID REFERENCES users(id),
    user_ip VARCHAR(45),
    
    -- When
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- What changed (JSON format)
    old_values JSONB,
    new_values JSONB,
    
    -- Additional context
    notes TEXT
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users indexes
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

-- Patients indexes  
CREATE INDEX idx_patients_patient_code ON patients(patient_code);
CREATE INDEX idx_patients_phone ON patients(phone_number);
CREATE INDEX idx_patients_insurance ON patients(insurance_number);

-- Appointments indexes
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_appointments_status ON appointments(status);

-- Prescriptions indexes
CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_status ON prescriptions(status);

-- Bills indexes
CREATE INDEX idx_bills_patient ON bills(patient_id);
CREATE INDEX idx_bills_status ON bills(payment_status);
CREATE INDEX idx_bills_date ON bills(bill_date);

-- Notifications indexes
CREATE INDEX idx_notifications_patient ON notifications(patient_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_scheduled ON notifications(scheduled_at);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_doctors_updated_at BEFORE UPDATE ON doctors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_staff_updated_at BEFORE UPDATE ON staff
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prescriptions_updated_at BEFORE UPDATE ON prescriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bills_updated_at BEFORE UPDATE ON bills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate patient codes
CREATE OR REPLACE FUNCTION generate_patient_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.patient_code IS NULL OR NEW.patient_code = '' THEN
        NEW.patient_code := 'BN' || TO_CHAR(CURRENT_DATE, 'YYYY') || 
                           LPAD(NEXTVAL('patient_code_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create sequence for patient codes
CREATE SEQUENCE patient_code_seq START 1;

-- Create trigger for patient code generation
CREATE TRIGGER generate_patient_code_trigger 
    BEFORE INSERT ON patients
    FOR EACH ROW EXECUTE FUNCTION generate_patient_code();