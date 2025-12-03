-- MediManager Database Schema for Supabase (PostgreSQL)
-- This script creates all necessary tables for the MediManager application

-- Enable UUID extension (if needed in the future)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create staff table
CREATE TABLE IF NOT EXISTS staff (
    staff_id VARCHAR(10) PRIMARY KEY,
    staff_psw TEXT NOT NULL,
    staff_name TEXT,
    staff_position TEXT DEFAULT 'staff',
    staff_phone TEXT,
    staff_email TEXT,
    staff_salary DECIMAL(10,0),
    hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger for updated_at on staff
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_staff_updated_at BEFORE UPDATE ON staff
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create supplier table
CREATE TABLE IF NOT EXISTS supplier (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    contact_email TEXT,
    supplier_address TEXT,
    payment_terms TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_supplier_updated_at BEFORE UPDATE ON supplier
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create customer table
CREATE TABLE IF NOT EXISTS customer (
    customer_id SERIAL PRIMARY KEY,
    customer_name TEXT,
    customer_phone VARCHAR(11),
    customer_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_customer_updated_at BEFORE UPDATE ON customer
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create medicine table
CREATE TABLE IF NOT EXISTS medicine (
    medicine_id SERIAL PRIMARY KEY,
    medicine_name TEXT,
    generic_name TEXT,
    brand_name TEXT,
    supplier_id INT REFERENCES supplier(supplier_id) ON DELETE SET NULL,
    category_id INT,
    unit_price DECIMAL(10,0),
    sale_price DECIMAL(10,0),
    stock_quantity INT DEFAULT 0,
    expiration_date TIMESTAMP,
    batch_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unit TEXT
);

CREATE TRIGGER update_medicine_updated_at BEFORE UPDATE ON medicine
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create stock table
CREATE TABLE IF NOT EXISTS stock (
    stock_id SERIAL PRIMARY KEY,
    medicine_id INT REFERENCES medicine(medicine_id) ON DELETE CASCADE,
    supplier_id INT REFERENCES supplier(supplier_id) ON DELETE SET NULL,
    quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_stock_updated_at BEFORE UPDATE ON stock
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create invoice table
CREATE TABLE IF NOT EXISTS invoice (
    invoice_id SERIAL PRIMARY KEY,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_id INT REFERENCES customer(customer_id) ON DELETE SET NULL,
    staff_id VARCHAR(10) REFERENCES staff(staff_id) ON DELETE SET NULL,
    total_amount DECIMAL(10,0) DEFAULT 0,
    payment_status TEXT DEFAULT 'pending',
    due_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_invoice_updated_at BEFORE UPDATE ON invoice
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create invoice_detail table
CREATE TABLE IF NOT EXISTS invoice_detail (
    invoice_detail_id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES invoice(invoice_id) ON DELETE CASCADE,
    medicine_id INT REFERENCES medicine(medicine_id) ON DELETE SET NULL,
    quantity INT DEFAULT 0,
    sale_price DECIMAL(10,0) DEFAULT 0,
    total_price DECIMAL(10,0) DEFAULT 0
);

-- Create activity_log table
CREATE TABLE IF NOT EXISTS activity_log (
    log_id SERIAL PRIMARY KEY,
    staff_id VARCHAR(10) REFERENCES staff(staff_id) ON DELETE SET NULL,
    action TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_medicine_supplier ON medicine(supplier_id);
CREATE INDEX IF NOT EXISTS idx_medicine_category ON medicine(category_id);
CREATE INDEX IF NOT EXISTS idx_medicine_expiration ON medicine(expiration_date);
CREATE INDEX IF NOT EXISTS idx_invoice_customer ON invoice(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoice_staff ON invoice(staff_id);
CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(invoice_date);
CREATE INDEX IF NOT EXISTS idx_activity_log_staff ON activity_log(staff_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_time ON activity_log(log_time);

-- Insert default admin account (password: admin)
-- Note: The actual password hash will be generated by the application
INSERT INTO staff (staff_id, staff_psw, staff_name, staff_position, staff_phone, staff_email)
VALUES ('admin', '$2b$12$placeholder', 'Administrator', 'admin', '0000000000', 'admin@example.com')
ON CONFLICT (staff_id) DO NOTHING;

-- Grant necessary permissions (if using Row Level Security)
-- Uncomment these if you want to enable RLS
-- ALTER TABLE staff ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE supplier ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE customer ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE medicine ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE stock ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE invoice ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE invoice_detail ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your needs)
-- CREATE POLICY "Enable read access for all users" ON staff FOR SELECT USING (true);
-- CREATE POLICY "Enable insert for authenticated users only" ON staff FOR INSERT WITH CHECK (true);
