from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import sys

# def resource_path(relative_path):
#     # if hasattr(sys, '_MEIPASS'):
#     #     return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)

# font_path = resource_path("fonts/Arial.ttf")
# pdfmetrics.registerFont(TTFont('Arial', font_path))
current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, "fonts")
pdfmetrics.registerFont(TTFont('Arial', font_path))

def export_stock_report(context, filepath=None):
    if filepath is None:
        filename = f"report_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        folder = "exports"
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

    db = context.db_manager
    sql = """SELECT medicine_name, unit, stock_quantity, batch_number, sale_price FROM medicine"""
    db.execute(sql)
    results = db.fetchall()

    c = canvas.Canvas(filepath, pagesize=A4)
    c.setFont("ArialUnicode", 14)
    c.drawString(50, 800, "BÁO CÁO TỒN KHO")

    c.setFont("ArialUnicode", 10)
    y = 780
    headers = ["Tên thuốc", "Đơn vị", "Tồn kho", "Lô", "Giá bán"]
    for i, header in enumerate(headers):
        c.drawString(50 + i * 100, y, header)

    y -= 20
    for row in results:
        if y < 50:
            c.showPage()
            y = 800
            c.setFont("ArialUnicode", 10)
        for i, value in enumerate(row):
            c.drawString(50 + i * 100, y, str(value))
        y -= 20

    c.save()
    return filepath

def export_invoice_report(context, date, filepath=None):
    if filepath is None:
        filename = f"report_invoice_{date}.pdf"
        folder = "exports"
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

    db = context.db_manager
    sql = """SELECT invoice_id, invoice_date, customer_id, total_amount, staff_id, payment_status 
             FROM invoice WHERE DATE(invoice_date) = %s"""
    db.execute(sql, (date,))
    results = db.fetchall()

    c = canvas.Canvas(filepath, pagesize=A4)
    c.setFont("ArialUnicode", 14)
    c.drawString(50, 800, f"BÁO CÁO HÓA ĐƠN NGÀY {date}")

    c.setFont("ArialUnicode", 10)
    y = 780
    headers = ["ID", "Thời gian", "Khách", "Tổng", "Nhân viên", "Trạng thái"]
    for i, header in enumerate(headers):
        c.drawString(50 + i * 80, y, header)

    y -= 20
    for row in results:
        if y < 50:
            c.showPage()
            y = 800
            c.setFont("ArialUnicode", 10)
        for i, value in enumerate(row):
            c.drawString(50 + i * 80, y, str(value))
        y -= 20

    c.save()
    return filepath

def export_expiry_warning_report(context, filepath=None):
    if filepath is None:
        filename = f"report_expiring_meds_{datetime.now().strftime('%Y%m%d')}.pdf"
        folder = "exports"
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font_path = os.path.join("fonts", "Arial.ttf")
    pdfmetrics.registerFont(TTFont("ArialUnicode", font_path))

    db = context.db_manager
    sql = """
        SELECT medicine_name, stock_quantity, unit, batch_number, expiration_date,
               DATEDIFF(expiration_date, NOW()) AS days_left
        FROM medicine
        WHERE DATEDIFF(expiration_date, NOW()) <= 60
        ORDER BY expiration_date ASC
    """
    db.execute(sql)
    results = db.fetchall()

    c = canvas.Canvas(filepath, pagesize=A4)
    c.setFont("ArialUnicode", 14)
    c.drawString(50, 800, "BÁO CÁO THUỐC SẮP HẾT HẠN")

    c.setFont("ArialUnicode", 10)
    y = 780
    col_x = [50, 150, 200, 270, 370, 500]
    headers = ["Tên thuốc", "SL", "Đơn vị", "Lô", "Hạn dùng", "Còn lại"]
    for i, header in enumerate(headers):
        c.drawString(col_x[i], y, header)

    y -= 20
    for row in results:
        if y < 50:
            c.showPage()
            y = 800
            c.setFont("ArialUnicode", 10)
            for i, header in enumerate(headers):
                c.drawString(col_x[i], y, header)
            y -= 20
        for i, value in enumerate(row):
            c.drawString(col_x[i], y, str(value))
        y -= 20

    c.save()
    return filepath
