-- MediManager - PostgreSQL / Supabase schema
--
-- Generated from src/core/schema.py, which is the single source of truth.
-- The application creates these tables automatically on first run; this file
-- is for setting them up by hand in the Supabase SQL editor.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Keeps updated_at current on every UPDATE
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';


-- staff
CREATE TABLE IF NOT EXISTS staff (
    staff_id VARCHAR(10) PRIMARY KEY,
    staff_psw TEXT NOT NULL,
    staff_name TEXT,
    staff_position TEXT DEFAULT 'staff',
    staff_phone TEXT,
    staff_email TEXT,
    staff_salary DECIMAL(12,2),
    hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_staff_updated_at ON staff;
CREATE TRIGGER update_staff_updated_at BEFORE UPDATE ON staff
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- category
CREATE TABLE IF NOT EXISTS category (
    category_id SERIAL PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_category_updated_at ON category;
CREATE TRIGGER update_category_updated_at BEFORE UPDATE ON category
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- payment_method
CREATE TABLE IF NOT EXISTS payment_method (
    payment_method_id SERIAL PRIMARY KEY,
    payment_name TEXT NOT NULL UNIQUE,
    method_type TEXT NOT NULL DEFAULT 'sale',
    description TEXT
);

-- supplier
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

DROP TRIGGER IF EXISTS update_supplier_updated_at ON supplier;
CREATE TRIGGER update_supplier_updated_at BEFORE UPDATE ON supplier
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- customer
CREATE TABLE IF NOT EXISTS customer (
    customer_id SERIAL PRIMARY KEY,
    customer_name TEXT,
    customer_phone VARCHAR(11),
    customer_email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_customer_updated_at ON customer;
CREATE TRIGGER update_customer_updated_at BEFORE UPDATE ON customer
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- medicine
CREATE TABLE IF NOT EXISTS medicine (
    medicine_id SERIAL PRIMARY KEY,
    medicine_name TEXT,
    generic_name TEXT,
    brand_name TEXT,
    supplier_id INT REFERENCES supplier(supplier_id),
    category_id INT REFERENCES category(category_id),
    unit_price DECIMAL(12,2),
    sale_price DECIMAL(12,2),
    stock_quantity INT DEFAULT 0,
    expiration_date TIMESTAMP,
    batch_number TEXT,
    unit TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_medicine_updated_at ON medicine;
CREATE TRIGGER update_medicine_updated_at BEFORE UPDATE ON medicine
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- stock
CREATE TABLE IF NOT EXISTS stock (
    stock_id SERIAL PRIMARY KEY,
    supplier_id INT REFERENCES supplier(supplier_id),
    staff_id VARCHAR(10) REFERENCES staff(staff_id),
    payment_method_id INT REFERENCES payment_method(payment_method_id),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_stock_updated_at ON stock;
CREATE TRIGGER update_stock_updated_at BEFORE UPDATE ON stock
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- stock_detail
CREATE TABLE IF NOT EXISTS stock_detail (
    stock_detail_id SERIAL PRIMARY KEY,
    stock_id INT REFERENCES stock(stock_id),
    medicine_id INT REFERENCES medicine(medicine_id),
    quantity INT DEFAULT 0,
    price DECIMAL(12,2) DEFAULT 0,
    batch_number TEXT,
    expiration_date TIMESTAMP,
    note TEXT
);

-- invoice
CREATE TABLE IF NOT EXISTS invoice (
    invoice_id SERIAL PRIMARY KEY,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_id INT REFERENCES customer(customer_id),
    staff_id VARCHAR(10) REFERENCES staff(staff_id),
    payment_method_id INT REFERENCES payment_method(payment_method_id),
    total_amount DECIMAL(12,2) DEFAULT 0,
    payment_status TEXT DEFAULT 'pending',
    due_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS update_invoice_updated_at ON invoice;
CREATE TRIGGER update_invoice_updated_at BEFORE UPDATE ON invoice
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- invoice_detail
CREATE TABLE IF NOT EXISTS invoice_detail (
    invoice_detail_id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES invoice(invoice_id),
    medicine_id INT REFERENCES medicine(medicine_id),
    quantity INT DEFAULT 0,
    sale_price DECIMAL(12,2) DEFAULT 0,
    total_price DECIMAL(12,2) DEFAULT 0
);

-- activity_log
CREATE TABLE IF NOT EXISTS activity_log (
    log_id SERIAL PRIMARY KEY,
    staff_id VARCHAR(10) REFERENCES staff(staff_id),
    action TEXT,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_medicine_supplier ON medicine(supplier_id);
CREATE INDEX IF NOT EXISTS idx_medicine_category ON medicine(category_id);
CREATE INDEX IF NOT EXISTS idx_medicine_expiration ON medicine(expiration_date);
CREATE INDEX IF NOT EXISTS idx_stock_detail_stock ON stock_detail(stock_id);
CREATE INDEX IF NOT EXISTS idx_stock_detail_medicine ON stock_detail(medicine_id);
CREATE INDEX IF NOT EXISTS idx_invoice_customer ON invoice(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoice_staff ON invoice(staff_id);
CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(invoice_date);
CREATE INDEX IF NOT EXISTS idx_invoice_detail_invoice ON invoice_detail(invoice_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_staff ON activity_log(staff_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_time ON activity_log(log_time);

-- Reference data
INSERT INTO payment_method (payment_name, method_type, description)
VALUES
    ('COD', 'purchase', 'Thanh toán khi nhận hàng'),
    ('prepayment', 'purchase', 'Thanh toán trước cho nhà cung cấp'),
    ('Tiền mặt', 'sale', 'Khách thanh toán bằng tiền mặt'),
    ('Chuyển khoản', 'sale', 'Khách thanh toán bằng chuyển khoản')
ON CONFLICT (payment_name) DO NOTHING;

INSERT INTO category (category_name, description)
VALUES
    ('Thuốc giảm đau', 'Thuốc giảm đau, hạ sốt'),
    ('Thuốc kháng sinh', 'Thuốc điều trị nhiễm khuẩn'),
    ('Thuốc kháng viêm', 'Thuốc chống viêm'),
    ('Vitamin & Khoáng chất', 'Thực phẩm bổ sung vi chất'),
    ('Thuốc tiêu hóa', 'Thuốc điều trị đường tiêu hóa'),
    ('Thuốc hô hấp', 'Thuốc điều trị đường hô hấp'),
    ('Thuốc tim mạch', 'Thuốc điều trị tim mạch, huyết áp'),
    ('Dụng cụ y tế', 'Vật tư và dụng cụ y tế'),
    ('Khác', 'Các mặt hàng khác')
ON CONFLICT (category_name) DO NOTHING;

-- Default admin account.
-- The application replaces this placeholder with a real bcrypt hash on first
-- run (username: admin / password: admin). Change the password after logging in.
INSERT INTO staff (staff_id, staff_psw, staff_name, staff_position, staff_phone, staff_email)
VALUES ('admin', '$2b$12$placeholder', 'Administrator', 'admin', '0000000000', 'admin@example.com')
ON CONFLICT (staff_id) DO NOTHING;
