import psycopg2
import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            # Connect to Supabase PostgreSQL database
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT', 5432),
                database=os.getenv('DB_NAME', 'postgres'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD')
            )
            self.cursor = self.connection.cursor()

            # Create necessary tables
            self.create_tables()
            return self.connection
        except Exception as e:
            print("Database connection failed:", e)
            return None

    def create_tables(self):
        try:
            # Create staff table
            self.cursor.execute("""
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
            """)

            # Insert default admin account if it doesn't exist
            self.cursor.execute("SELECT COUNT(*) FROM staff WHERE staff_id = 'admin';")
            if self.cursor.fetchone()[0] == 0:
                hashed_password = bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode('utf-8')
                self.cursor.execute("""
                    INSERT INTO staff (staff_id, staff_psw, staff_name, staff_position, staff_phone, staff_email)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, ('admin', hashed_password, 'Administrator', 'admin', '0000000000', 'admin@example.com'))
                print("✔ Admin account created (username: admin / password: admin)")

            # Create supplier table
            self.cursor.execute("""
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
            """)

            # Create customer table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer (
                    customer_id SERIAL PRIMARY KEY,
                    customer_name TEXT,
                    customer_phone VARCHAR(11),
                    customer_email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create medicine table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicine (
                    medicine_id SERIAL PRIMARY KEY,
                    medicine_name TEXT,
                    generic_name TEXT,
                    brand_name TEXT,
                    supplier_id INT REFERENCES supplier(supplier_id),
                    category_id INT,
                    unit_price DECIMAL(10,0),
                    sale_price DECIMAL(10,0),
                    stock_quantity INT,
                    expiration_date TIMESTAMP,
                    batch_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    unit TEXT
                );
            """)

            # Create stock table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock (
                    stock_id SERIAL PRIMARY KEY,
                    medicine_id INT REFERENCES medicine(medicine_id),
                    supplier_id INT REFERENCES supplier(supplier_id),
                    quantity INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create invoice table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice (
                    invoice_id SERIAL PRIMARY KEY,
                    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    customer_id INT REFERENCES customer(customer_id),
                    staff_id VARCHAR(10) REFERENCES staff(staff_id),
                    total_amount DECIMAL(10,0),
                    payment_status TEXT,
                    due_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create invoice_detail table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice_detail (
                    invoice_detail_id SERIAL PRIMARY KEY,
                    invoice_id INT REFERENCES invoice(invoice_id),
                    medicine_id INT REFERENCES medicine(medicine_id),
                    quantity INT,
                    sale_price DECIMAL(10,0),
                    total_price DECIMAL(10,0)
                );
            """)

            # Create activity_log table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    log_id SERIAL PRIMARY KEY,
                    staff_id VARCHAR(10) REFERENCES staff(staff_id),
                    action TEXT,
                    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            self.connection.commit()
            print("✔ Database and tables created successfully.")

        except Exception as e:
            print("❌ Error creating tables:", e)
            self.connection.rollback()

    def execute(self, query, params=None):
        """Execute a query with optional parameters"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            raise

    def executemany(self, query, params_list):
        """Execute a query with multiple parameter sets"""
        try:
            self.cursor.executemany(query, params_list)
            return self.cursor
        except Exception as e:
            print(f"❌ Batch query execution error: {e}")
            raise

    def fetchall(self):
        """Fetch all rows from the last query"""
        return self.cursor.fetchall()

    def fetchone(self):
        """Fetch one row from the last query"""
        return self.cursor.fetchone()

    def rollback(self):
        """Rollback the current transaction"""
        if self.connection:
            self.connection.rollback()

    def commit(self):
        """Commit the current transaction"""
        if self.connection:
            self.connection.commit()

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def log_action(self, staff_id, action):
        """Log user actions to activity_log table"""
        try:
            sql = "INSERT INTO activity_log (staff_id, action, log_time) VALUES (%s, %s, NOW())"
            self.execute(sql, (staff_id, action))
            self.connection.commit()
        except Exception as e:
            print(f"[LOG ERROR] {e}")
