import MySQLdb as mysql_db
import bcrypt

class DBManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            # Step 1: Connect to MySQL without selecting a specific database
            self.connection = mysql_db.connect(
                host='localhost',
                user='root',
                passwd='@Thanh070891',
                charset='utf8'
            )
            self.cursor = self.connection.cursor()

            # Step 2: Create the database if it doesn't exist
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS medimanager CHARACTER SET utf8 COLLATE utf8_general_ci;")
            self.connection.select_db("medimanager")

            # Step 3: Create necessary tables
            self.create_tables()
            return self.connection
        except Exception as e:
            print("Database connection failed:", e)
            return None

    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS staff (
                    staff_id VARCHAR(10) PRIMARY KEY,
                    staff_psw TEXT,
                    staff_name TEXT,
                    staff_position TEXT DEFAULT 'staff',
                    staff_phone TEXT,
                    staff_email TEXT,
                    staff_salary DECIMAL(10,0),
                    hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS supplier (
                    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
                    supplier_name TEXT,
                    contact_name TEXT,
                    contact_phone TEXT,
                    contact_email TEXT,
                    supplier_address TEXT,
                    payment_terms TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer (
                    customer_id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_name TEXT,
                    customer_phone VARCHAR(11),
                    customer_email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicine (
                    medicine_id INT PRIMARY KEY AUTO_INCREMENT,
                    medicine_name TEXT,
                    generic_name TEXT,
                    brand_name TEXT,
                    supplier_id INT,
                    category_id INT,
                    unit_price DECIMAL(10,0),
                    sale_price DECIMAL(10,0),
                    stock_quantity INT,
                    expiration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    batch_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    unit TEXT
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock (
                    stock_id INT PRIMARY KEY AUTO_INCREMENT,
                    medicine_id INT,
                    supplier_id INT,
                    quantity INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice (
                    invoice_id INT PRIMARY KEY AUTO_INCREMENT,
                    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    customer_id INT,
                    staff_id VARCHAR(10),
                    total_amount DECIMAL(10,0),
                    payment_status TEXT,
                    due_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoice_detail (
                    invoice_detail_id INT PRIMARY KEY AUTO_INCREMENT,
                    invoice_id INT,
                    medicine_id INT,
                    quantity INT,
                    sale_price DECIMAL(10,0),
                    total_price DECIMAL(10,0)
                );
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    log_id INT AUTO_INCREMENT PRIMARY KEY,
                    staff_id VARCHAR(10),
                    action TEXT,
                    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            self.connection.commit()
            print("✔ Database and tables created successfully.")

        except Exception as e:
            print("❌ Error creating tables:", e)

    def execute(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor

    def executemany(self, query, params_list):
        self.cursor.executemany(query, params_list)
        return self.cursor

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()
    
    def rollback(self):
        if self.connection:
            self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def log_action(self, staff_id, action):
        try:
            sql = "INSERT INTO activity_log (staff_id, action, log_time) VALUES (%s, %s, NOW())"
            self.execute(sql, (staff_id, action))
            self.connection.commit()
        except Exception as e:
            print(f"[LOG ERROR] {e}")
