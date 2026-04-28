import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox

def load_ui_file(obj, filename):
    from constants import CURRENT_DIR
    ui_path = os.path.join(CURRENT_DIR, 'ui', filename)
    if not os.path.exists(ui_path):
        raise FileNotFoundError(f"Không tìm thấy UI file: {ui_path}")
    uic.loadUi(ui_path, obj)

def show_error(message):
    QMessageBox.critical(None, "Lỗi", message)
