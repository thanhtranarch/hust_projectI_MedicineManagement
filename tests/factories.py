"""
Helpers for building test data.
"""

from datetime import datetime, timedelta


def add_supplier(db, name="Công ty Dược Hà Nội"):
    """Insert a supplier and return its id."""
    db.execute(
        "INSERT INTO supplier (supplier_name, contact_phone) VALUES (%s, %s)",
        (name, "0901234567")
    )
    supplier_id = db.last_insert_id()
    db.commit()
    return supplier_id


def add_customer(db, name="Nguyễn Văn A", phone="0912345678"):
    """Insert a customer and return its id."""
    db.execute(
        "INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)",
        (name, phone)
    )
    customer_id = db.last_insert_id()
    db.commit()
    return customer_id


def add_medicine(db, name="Paracetamol 500mg", quantity=100, sale_price=2000,
                 unit_price=1500, expires_in_days=365, supplier_id=None,
                 category_id=None, batch="LOT-001"):
    """Insert a medicine and return its id."""
    expiry = (datetime.now() + timedelta(days=expires_in_days)).strftime("%Y-%m-%d")
    db.execute(
        """INSERT INTO medicine (medicine_name, supplier_id, category_id, unit_price,
                                 sale_price, stock_quantity, expiration_date,
                                 batch_number, unit)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (name, supplier_id, category_id, unit_price, sale_price, quantity,
         expiry, batch, "Viên")
    )
    medicine_id = db.last_insert_id()
    db.commit()
    return medicine_id


def add_invoice(db, customer_id, medicines, staff_id='admin', when=None):
    """
    Create an invoice with its detail lines and decrement stock.

    Args:
        medicines: list of (medicine_id, quantity, sale_price)
        when: 'YYYY-MM-DD' invoice date, defaults to today

    Returns:
        (invoice_id, total_amount)
    """
    when = when or datetime.now().strftime("%Y-%m-%d")
    total = sum(qty * price for _, qty, price in medicines)

    db.execute(
        """INSERT INTO invoice (invoice_date, customer_id, staff_id,
                                total_amount, payment_status)
           VALUES (%s, %s, %s, %s, %s)""",
        (when, customer_id, staff_id, total, "Đã thanh toán")
    )
    invoice_id = db.last_insert_id()

    for medicine_id, qty, price in medicines:
        db.execute(
            """INSERT INTO invoice_detail (invoice_id, medicine_id, quantity,
                                           sale_price, total_price)
               VALUES (%s, %s, %s, %s, %s)""",
            (invoice_id, medicine_id, qty, price, qty * price)
        )
        db.execute(
            "UPDATE medicine SET stock_quantity = stock_quantity - %s WHERE medicine_id = %s",
            (qty, medicine_id)
        )

    db.commit()
    return invoice_id, total


def add_stock_entry(db, supplier_id, lines, staff_id='admin'):
    """
    Create a goods-receipt document.

    Args:
        lines: list of (medicine_id, quantity, price)

    Returns:
        stock_id
    """
    db.execute(
        "INSERT INTO stock (supplier_id, staff_id) VALUES (%s, %s)",
        (supplier_id, staff_id)
    )
    stock_id = db.last_insert_id()

    for medicine_id, quantity, price in lines:
        db.execute(
            """INSERT INTO stock_detail (stock_id, medicine_id, quantity, price)
               VALUES (%s, %s, %s, %s)""",
            (stock_id, medicine_id, quantity, price)
        )
        db.execute(
            "UPDATE medicine SET stock_quantity = stock_quantity + %s WHERE medicine_id = %s",
            (quantity, medicine_id)
        )

    db.commit()
    return stock_id


def first_category_id(db):
    """Id of the first seeded category."""
    db.execute("SELECT category_id FROM category ORDER BY category_id LIMIT 1")
    return db.fetchone()[0]


def seed_basic_data(db):
    """Populate a supplier, a customer and two medicines. Returns a dict of ids."""
    supplier_id = add_supplier(db)
    customer_id = add_customer(db)
    category_id = first_category_id(db)

    paracetamol = add_medicine(
        db, "Paracetamol 500mg", quantity=100, sale_price=2000,
        supplier_id=supplier_id, category_id=category_id, batch="LOT-001"
    )
    amoxicillin = add_medicine(
        db, "Amoxicillin 500mg", quantity=50, sale_price=5000,
        supplier_id=supplier_id, category_id=category_id, batch="LOT-002"
    )

    return {
        'supplier_id': supplier_id,
        'customer_id': customer_id,
        'category_id': category_id,
        'paracetamol': paracetamol,
        'amoxicillin': amoxicillin,
    }
