"""
Database schema definition - single source of truth.

The same table definitions drive both supported backends, so PostgreSQL
(Supabase) and SQLite never drift apart. Dialect differences are expressed as
``{token}`` placeholders that each backend fills in.
"""

# Dialect-specific fragments used inside the DDL templates below
DIALECTS = {
    'postgres': {
        'serial_pk': 'SERIAL PRIMARY KEY',
        'timestamp': 'TIMESTAMP',
        'now': 'CURRENT_TIMESTAMP',
        'money': 'DECIMAL(12,2)',
    },
    'sqlite': {
        'serial_pk': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'timestamp': 'TIMESTAMP',
        'now': 'CURRENT_TIMESTAMP',
        'money': 'NUMERIC',
    },
}

# Ordered so that foreign keys always reference an already-created table
TABLES = [
    ('staff', """
        CREATE TABLE IF NOT EXISTS staff (
            staff_id VARCHAR(10) PRIMARY KEY,
            staff_psw TEXT NOT NULL,
            staff_name TEXT,
            staff_position TEXT DEFAULT 'staff',
            staff_phone TEXT,
            staff_email TEXT,
            staff_salary {money},
            hire_date {timestamp} DEFAULT {now},
            created_at {timestamp} DEFAULT {now},
            updated_at {timestamp} DEFAULT {now}
        )
    """),

    ('category', """
        CREATE TABLE IF NOT EXISTS category (
            category_id {serial_pk},
            category_name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at {timestamp} DEFAULT {now},
            updated_at {timestamp} DEFAULT {now}
        )
    """),

    ('payment_method', """
        CREATE TABLE IF NOT EXISTS payment_method (
            payment_method_id {serial_pk},
            payment_name TEXT NOT NULL UNIQUE,
            method_type TEXT NOT NULL DEFAULT 'sale',
            description TEXT
        )
    """),

    ('supplier', """
        CREATE TABLE IF NOT EXISTS supplier (
            supplier_id {serial_pk},
            supplier_name TEXT,
            contact_name TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            supplier_address TEXT,
            payment_terms TEXT,
            created_at {timestamp} DEFAULT {now},
            updated_at {timestamp} DEFAULT {now}
        )
    """),

    ('customer', """
        CREATE TABLE IF NOT EXISTS customer (
            customer_id {serial_pk},
            customer_name TEXT,
            customer_phone VARCHAR(11),
            customer_email TEXT,
            created_at {timestamp} DEFAULT {now},
            updated_at {timestamp} DEFAULT {now}
        )
    """),

    ('medicine', """
        CREATE TABLE IF NOT EXISTS medicine (
            medicine_id {serial_pk},
            medicine_name TEXT,
            generic_name TEXT,
            brand_name TEXT,
            supplier_id INT REFERENCES supplier(supplier_id),
            category_id INT REFERENCES category(category_id),
            unit_price {money},
            sale_price {money},
            stock_quantity INT DEFAULT 0,
            expiration_date {timestamp},
            batch_number TEXT,
            unit TEXT,
            created_at {timestamp} DEFAULT {now},
            updated_at {timestamp} DEFAULT {now}
        )
    """),

    # A stock row is the header of a goods-receipt (purchase) document;
    # the individual medicine lines live in stock_detail.
    ('stock', """
        CREATE TABLE IF NOT EXISTS stock (
            stock_id {serial_pk},
            supplier_id INT REFERENCES supplier(supplier_id),
            staff_id VARCHAR(10) REFERENCES staff(staff_id),
            payment_method_id INT REFERENCES payment_method(payment_method_id),
            note TEXT,
            created_at {timestamp} DEFAULT {now},
            updated_at {timestamp} DEFAULT {now}
        )
    """),

    ('stock_detail', """
        CREATE TABLE IF NOT EXISTS stock_detail (
            stock_detail_id {serial_pk},
            stock_id INT REFERENCES stock(stock_id),
            medicine_id INT REFERENCES medicine(medicine_id),
            quantity INT DEFAULT 0,
            price {money} DEFAULT 0,
            batch_number TEXT,
            expiration_date {timestamp},
            note TEXT
        )
    """),

    ('invoice', """
        CREATE TABLE IF NOT EXISTS invoice (
            invoice_id {serial_pk},
            invoice_date {timestamp} DEFAULT {now},
            customer_id INT REFERENCES customer(customer_id),
            staff_id VARCHAR(10) REFERENCES staff(staff_id),
            payment_method_id INT REFERENCES payment_method(payment_method_id),
            total_amount {money} DEFAULT 0,
            payment_status TEXT DEFAULT 'pending',
            due_date {timestamp} DEFAULT {now},
            created_at {timestamp} DEFAULT {now},
            updated_at {timestamp} DEFAULT {now}
        )
    """),

    ('invoice_detail', """
        CREATE TABLE IF NOT EXISTS invoice_detail (
            invoice_detail_id {serial_pk},
            invoice_id INT REFERENCES invoice(invoice_id),
            medicine_id INT REFERENCES medicine(medicine_id),
            quantity INT DEFAULT 0,
            sale_price {money} DEFAULT 0,
            total_price {money} DEFAULT 0
        )
    """),

    ('activity_log', """
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id {serial_pk},
            staff_id VARCHAR(10) REFERENCES staff(staff_id),
            action TEXT,
            log_time {timestamp} DEFAULT {now}
        )
    """),
]

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_medicine_supplier ON medicine(supplier_id)",
    "CREATE INDEX IF NOT EXISTS idx_medicine_category ON medicine(category_id)",
    "CREATE INDEX IF NOT EXISTS idx_medicine_expiration ON medicine(expiration_date)",
    "CREATE INDEX IF NOT EXISTS idx_stock_detail_stock ON stock_detail(stock_id)",
    "CREATE INDEX IF NOT EXISTS idx_stock_detail_medicine ON stock_detail(medicine_id)",
    "CREATE INDEX IF NOT EXISTS idx_invoice_customer ON invoice(customer_id)",
    "CREATE INDEX IF NOT EXISTS idx_invoice_staff ON invoice(staff_id)",
    "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(invoice_date)",
    "CREATE INDEX IF NOT EXISTS idx_invoice_detail_invoice ON invoice_detail(invoice_id)",
    "CREATE INDEX IF NOT EXISTS idx_activity_log_staff ON activity_log(staff_id)",
    "CREATE INDEX IF NOT EXISTS idx_activity_log_time ON activity_log(log_time)",
]

# Columns added after the first release. Existing databases are created with
# CREATE TABLE IF NOT EXISTS, which never alters an already-existing table, so
# these are applied separately on every startup.
MIGRATIONS = [
    ('medicine', 'unit', 'TEXT'),
    ('stock', 'staff_id', 'VARCHAR(10)'),
    ('stock', 'payment_method_id', 'INT'),
    ('stock', 'note', 'TEXT'),
    ('invoice', 'payment_method_id', 'INT'),
    ('payment_method', 'method_type', "TEXT DEFAULT 'sale'"),
]

# Reference data the UI depends on.
# method_type separates purchasing terms from point-of-sale tenders.
PAYMENT_METHODS = [
    ('COD', 'purchase', 'Thanh toán khi nhận hàng'),
    ('prepayment', 'purchase', 'Thanh toán trước cho nhà cung cấp'),
    ('Tiền mặt', 'sale', 'Khách thanh toán bằng tiền mặt'),
    ('Chuyển khoản', 'sale', 'Khách thanh toán bằng chuyển khoản'),
]

CATEGORIES = [
    ('Thuốc giảm đau', 'Thuốc giảm đau, hạ sốt'),
    ('Thuốc kháng sinh', 'Thuốc điều trị nhiễm khuẩn'),
    ('Thuốc kháng viêm', 'Thuốc chống viêm'),
    ('Vitamin & Khoáng chất', 'Thực phẩm bổ sung vi chất'),
    ('Thuốc tiêu hóa', 'Thuốc điều trị đường tiêu hóa'),
    ('Thuốc hô hấp', 'Thuốc điều trị đường hô hấp'),
    ('Thuốc tim mạch', 'Thuốc điều trị tim mạch, huyết áp'),
    ('Dụng cụ y tế', 'Vật tư và dụng cụ y tế'),
    ('Khác', 'Các mặt hàng khác'),
]


def render(sql_template, backend):
    """Fill dialect tokens in a DDL template for the given backend."""
    return sql_template.format(**DIALECTS[backend])
