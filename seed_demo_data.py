#!/usr/bin/env python3
"""
Populate the database with realistic demo data.

Useful for trying the application out or preparing a demonstration without
entering everything by hand.

    python seed_demo_data.py            # add demo data
    python seed_demo_data.py --reset    # wipe operational data first

Reference data (categories, payment methods) and the admin account are left
untouched.
"""

import argparse
import random
import sys
from datetime import datetime, timedelta

from src.config import DatabaseConfig
from src.core import AppContext
from src.services.auth_service import hash_password

SUPPLIERS = [
    ("Công ty Dược phẩm Hà Nội", "Nguyễn Văn Minh", "0243825147",
     "contact@duochanoi.vn", "12 Ngô Quyền, Hoàn Kiếm, Hà Nội", "COD"),
    ("Traphaco", "Trần Thị Lan", "0243854321",
     "sales@traphaco.com.vn", "75 Yên Ninh, Ba Đình, Hà Nội", "prepayment"),
    ("Dược Hậu Giang", "Lê Hoàng Nam", "0292891433",
     "info@dhgpharma.com.vn", "288 Bis Nguyễn Văn Cừ, Cần Thơ", "COD"),
    ("Pymepharco", "Phạm Thu Hà", "0257824444",
     "contact@pymepharco.com", "166-170 Nguyễn Huệ, Phú Yên", "prepayment"),
]

STAFF = [
    ("ql001", "Nguyễn Thị Hương", "manager", "0912345001",
     "huong.nt@medimanager.vn", 15000000),
    ("nv001", "Trần Văn Bình", "staff", "0912345002",
     "binh.tv@medimanager.vn", 9000000),
    ("nv002", "Lê Thị Mai", "staff", "0912345003",
     "mai.lt@medimanager.vn", 8500000),
]

CUSTOMERS = [
    ("Nguyễn Văn An", "0987654321", "an.nv@gmail.com"),
    ("Trần Thị Bích", "0976543210", "bich.tt@gmail.com"),
    ("Lê Minh Cường", "0965432109", "cuong.lm@gmail.com"),
    ("Phạm Thị Dung", "0954321098", None),
    ("Hoàng Văn Em", "0943210987", "em.hv@gmail.com"),
]

# (name, generic, brand, category, unit, unit_price, sale_price, qty, expires_in_days)
MEDICINES = [
    ("Paracetamol 500mg", "Paracetamol", "Hapacol", "Thuốc giảm đau",
     "Viên", 800, 1500, 500, 540),
    ("Efferalgan 500mg", "Paracetamol", "Efferalgan", "Thuốc giảm đau",
     "Viên", 2500, 4000, 200, 400),
    ("Amoxicillin 500mg", "Amoxicillin", "Amoxil", "Thuốc kháng sinh",
     "Viên", 1800, 3000, 300, 300),
    ("Augmentin 625mg", "Amoxicillin/Clavulanate", "Augmentin", "Thuốc kháng sinh",
     "Viên", 12000, 18000, 120, 45),
    ("Ibuprofen 400mg", "Ibuprofen", "Brufen", "Thuốc kháng viêm",
     "Viên", 1200, 2200, 250, 365),
    ("Vitamin C 1000mg", "Ascorbic acid", "Cevit", "Vitamin & Khoáng chất",
     "Viên sủi", 3000, 5000, 400, 250),
    ("Vitamin D3 K2", "Cholecalciferol", "Ostelin", "Vitamin & Khoáng chất",
     "Lọ", 145000, 210000, 40, 600),
    ("Smecta 3g", "Diosmectite", "Smecta", "Thuốc tiêu hóa",
     "Gói", 4500, 7000, 180, 20),
    ("Omeprazole 20mg", "Omeprazole", "Losec", "Thuốc tiêu hóa",
     "Viên", 2200, 3800, 220, 330),
    ("Ventolin 100mcg", "Salbutamol", "Ventolin", "Thuốc hô hấp",
     "Bình xịt", 68000, 95000, 35, 420),
    ("Amlodipine 5mg", "Amlodipine", "Normodipine", "Thuốc tim mạch",
     "Viên", 1500, 2800, 260, 480),
    ("Khẩu trang y tế 4 lớp", None, "Nam Anh", "Dụng cụ y tế",
     "Hộp", 25000, 40000, 90, 900),
    ("Nhiệt kế điện tử", None, "Omron", "Dụng cụ y tế",
     "Cái", 95000, 145000, 25, 1200),
    ("Berberin 10mg", "Berberine", "Berberin", "Thuốc tiêu hóa",
     "Viên", 300, 700, 600, 55),
]

OPERATIONAL_TABLES = [
    "invoice_detail", "invoice", "stock_detail", "stock",
    "medicine", "customer", "supplier", "activity_log",
]


def reset(db):
    """Delete operational data, keeping reference data and the admin account."""
    for table in OPERATIONAL_TABLES:
        db.execute(f"DELETE FROM {table}")
    db.execute("DELETE FROM staff WHERE staff_id <> 'admin'")
    db.commit()
    print("Cleared existing operational data.")


def lookup(db, sql, params=()):
    """Run a query and return {name: id}."""
    db.execute(sql, params)
    return {name: row_id for row_id, name in db.fetchall()}


def seed_staff(db):
    for staff_id, name, position, phone, email, salary in STAFF:
        db.execute("SELECT 1 FROM staff WHERE staff_id = %s", (staff_id,))
        if db.fetchone():
            continue
        db.execute(
            """INSERT INTO staff (staff_id, staff_psw, staff_name, staff_position,
                                  staff_phone, staff_email, staff_salary)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (staff_id, hash_password("matkhau123"), name, position, phone, email, salary)
        )
    db.commit()
    print(f"Staff: {len(STAFF)} accounts (password: matkhau123)")


def seed_suppliers(db):
    for name, contact, phone, email, address, terms in SUPPLIERS:
        db.execute(
            """INSERT INTO supplier (supplier_name, contact_name, contact_phone,
                                     contact_email, supplier_address, payment_terms)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, contact, phone, email, address, terms)
        )
    db.commit()
    print(f"Suppliers: {len(SUPPLIERS)}")


def seed_customers(db):
    for name, phone, email in CUSTOMERS:
        db.execute(
            "INSERT INTO customer (customer_name, customer_phone, customer_email) "
            "VALUES (%s, %s, %s)",
            (name, phone, email)
        )
    db.commit()
    print(f"Customers: {len(CUSTOMERS)}")


def seed_medicines(db):
    """Insert medicines and return their ids paired with sale prices."""
    suppliers = lookup(db, "SELECT supplier_id, supplier_name FROM supplier")
    categories = lookup(db, "SELECT category_id, category_name FROM category")
    supplier_ids = list(suppliers.values())

    created = []
    for idx, (name, generic, brand, category, unit,
              unit_price, sale_price, qty, expires_in) in enumerate(MEDICINES):
        expiry = (datetime.now() + timedelta(days=expires_in)).strftime("%Y-%m-%d")
        db.execute(
            """INSERT INTO medicine (medicine_name, generic_name, brand_name,
                                     supplier_id, category_id, unit_price, sale_price,
                                     stock_quantity, expiration_date, batch_number, unit)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, generic, brand, supplier_ids[idx % len(supplier_ids)],
             categories.get(category), unit_price, sale_price, qty, expiry,
             f"LOT{2025000 + idx}", unit)
        )
        created.append((db.last_insert_id(), sale_price, unit_price))

    db.commit()
    expiring = sum(1 for m in MEDICINES if m[8] <= 60)
    print(f"Medicines: {len(MEDICINES)} ({expiring} within the expiry warning window)")
    return created


def seed_stock_entries(db, medicines):
    """Create goods-receipt documents covering the medicines."""
    suppliers = list(lookup(db, "SELECT supplier_id, supplier_name FROM supplier").values())
    methods = lookup(
        db, "SELECT payment_method_id, payment_name FROM payment_method "
            "WHERE method_type = %s", ('purchase',)
    )
    method_ids = list(methods.values()) or [None]

    count = 0
    for batch_start in range(0, len(medicines), 5):
        chunk = medicines[batch_start:batch_start + 5]
        created = (datetime.now() - timedelta(days=30 - count * 7)).strftime("%Y-%m-%d")

        db.execute(
            """INSERT INTO stock (supplier_id, staff_id, payment_method_id, created_at, note)
               VALUES (%s, %s, %s, %s, %s)""",
            (suppliers[count % len(suppliers)], 'admin',
             method_ids[count % len(method_ids)], created, "Nhập hàng định kỳ")
        )
        stock_id = db.last_insert_id()

        for medicine_id, _, unit_price in chunk:
            db.execute(
                """INSERT INTO stock_detail (stock_id, medicine_id, quantity, price)
                   VALUES (%s, %s, %s, %s)""",
                (stock_id, medicine_id, random.randint(50, 200), unit_price)
            )
        count += 1

    db.commit()
    print(f"Stock entries: {count}")


def seed_invoices(db, medicines, days=30):
    """Create sales history spread over the last N days."""
    customers = list(lookup(db, "SELECT customer_id, customer_name FROM customer").values())
    staff_ids = ['admin'] + [s[0] for s in STAFF]
    methods = lookup(
        db, "SELECT payment_method_id, payment_name FROM payment_method "
            "WHERE method_type = %s", ('sale',)
    )
    method_ids = list(methods.values()) or [None]

    invoices = 0
    revenue = 0

    for day_offset in range(days, -1, -1):
        day = datetime.now() - timedelta(days=day_offset)

        for _ in range(random.randint(1, 5)):
            # Spread sales across opening hours so the dashboard shows real times
            invoice_date = day.replace(
                hour=random.randint(8, 20), minute=random.randint(0, 59),
                second=random.randint(0, 59), microsecond=0
            ).strftime("%Y-%m-%d %H:%M:%S")
            lines = random.sample(medicines, random.randint(1, 4))
            cart = [(mid, random.randint(1, 6), price) for mid, price, _ in lines]
            total = sum(qty * price for _, qty, price in cart)

            db.execute(
                """INSERT INTO invoice (invoice_date, customer_id, staff_id,
                                        payment_method_id, total_amount, payment_status)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (invoice_date, random.choice(customers), random.choice(staff_ids),
                 random.choice(method_ids), total, "Đã thanh toán")
            )
            invoice_id = db.last_insert_id()

            for medicine_id, qty, price in cart:
                db.execute(
                    """INSERT INTO invoice_detail (invoice_id, medicine_id, quantity,
                                                   sale_price, total_price)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (invoice_id, medicine_id, qty, price, qty * price)
                )
                db.execute(
                    "UPDATE medicine SET stock_quantity = stock_quantity - %s "
                    "WHERE medicine_id = %s AND stock_quantity >= %s",
                    (qty, medicine_id, qty)
                )

            invoices += 1
            revenue += total

    db.commit()
    print(f"Invoices: {invoices} over {days} days, revenue {revenue:,.0f} VND")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reset', action='store_true',
                        help="delete existing operational data first")
    parser.add_argument('--days', type=int, default=30,
                        help="days of sales history to generate (default: 30)")
    parser.add_argument('--seed', type=int, default=42,
                        help="random seed, for reproducible data (default: 42)")
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Database: {DatabaseConfig.describe()}")
    try:
        context = AppContext(staff_id='admin')
    except ConnectionError as e:
        print(f"Could not connect: {e}")
        sys.exit(1)

    db = context.db_manager

    try:
        if args.reset:
            reset(db)

        db.execute("SELECT COUNT(*) FROM medicine")
        if db.fetchone()[0] and not args.reset:
            print("\nThe database already contains medicines. "
                  "Re-run with --reset to replace the data.")
            return

        seed_staff(db)
        seed_suppliers(db)
        seed_customers(db)
        medicines = seed_medicines(db)
        seed_stock_entries(db, medicines)
        seed_invoices(db, medicines, args.days)

        print("\nDemo data ready. Log in with admin / admin.")
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        sys.exit(1)
    finally:
        context.close()


if __name__ == "__main__":
    main()
