-- Hospital Management System Database Initialization
-- This file will be executed when PostgreSQL container starts

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS hospital;

-- Set default search path
ALTER DATABASE hospital_management SET search_path TO hospital, public;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE hospital_management TO hospital_admin;
GRANT ALL PRIVILEGES ON SCHEMA hospital TO hospital_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hospital TO hospital_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hospital TO hospital_admin;