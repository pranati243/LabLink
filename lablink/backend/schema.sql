-- LabLink Database Schema for PostgreSQL
-- This script creates the database schema with all tables, constraints, and indexes

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS requests CASCADE;
DROP TABLE IF EXISTS components CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop types if they exist
DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS request_status CASCADE;
DROP TYPE IF EXISTS action_type CASCADE;
DROP TYPE IF EXISTS entity_type CASCADE;

-- Create enum types
CREATE TYPE user_role AS ENUM ('student', 'faculty');
CREATE TYPE request_status AS ENUM ('Pending', 'Approved', 'Rejected', 'Returned');
CREATE TYPE action_type AS ENUM ('CREATE', 'UPDATE', 'DELETE', 'REQUEST', 'APPROVE', 'REJECT', 'RETURN');
CREATE TYPE entity_type AS ENUM ('Component', 'Request', 'User');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Components table
CREATE TABLE components (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    description TEXT,
    image_url VARCHAR(255),
    location VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Requests table
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    status request_status NOT NULL DEFAULT 'Pending',
    rejection_reason TEXT,
    requested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    processed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    returned_at TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action_type action_type NOT NULL,
    entity_type entity_type NOT NULL,
    entity_id INTEGER NOT NULL,
    details JSONB,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization

-- Users table indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Components table indexes
CREATE INDEX idx_components_name ON components(name);
CREATE INDEX idx_components_type ON components(type);
CREATE INDEX idx_components_name_search ON components USING gin(to_tsvector('english', name));

-- Requests table indexes
CREATE INDEX idx_requests_student_id ON requests(student_id);
CREATE INDEX idx_requests_component_id ON requests(component_id);
CREATE INDEX idx_requests_status ON requests(status);
CREATE INDEX idx_requests_processed_by ON requests(processed_by);
CREATE INDEX idx_requests_requested_at ON requests(requested_at DESC);

-- Transactions table indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_action_type ON transactions(action_type);
CREATE INDEX idx_transactions_entity_type ON transactions(entity_type);
CREATE INDEX idx_transactions_entity_id ON transactions(entity_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp DESC);
CREATE INDEX idx_transactions_composite ON transactions(entity_type, entity_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for components table
CREATE TRIGGER update_components_updated_at
    BEFORE UPDATE ON components
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE users IS 'Stores user accounts for students and faculty';
COMMENT ON TABLE components IS 'Stores laboratory component inventory';
COMMENT ON TABLE requests IS 'Stores component borrowing requests from students';
COMMENT ON TABLE transactions IS 'Audit log for all system actions';

COMMENT ON COLUMN users.role IS 'User role: student or faculty';
COMMENT ON COLUMN components.quantity IS 'Current available quantity';
COMMENT ON COLUMN requests.status IS 'Request status: Pending, Approved, Rejected, or Returned';
COMMENT ON COLUMN transactions.details IS 'JSON object with additional transaction details';
