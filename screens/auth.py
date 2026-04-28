from PyQt6.QtWidgets import QDialog, QMessageBox, QToolButton, QLineEdit, QInputDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
import os
import bcrypt

from utils.helpers import load_ui_file
from constants import ICON_PATH


class AuthDialog(QDialog):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'login.ui')
        self.setWindowTitle("MediManager - Đăng nhập")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setFixedSize(250, 110)

        self.register_label.linkActivated.connect(self.goto_register)
        self.login_button.clicked.connect(self.login)
        self.login_button.setDefault(True)

        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.toggle_pw_button = QToolButton(self.login_password)
        self.toggle_pw_button.setIcon(QIcon("icon/eye_closed.png"))
        self.toggle_pw_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_pw_button.setStyleSheet("border: none; padding: 0px;")
        self.toggle_pw_button.setFixedSize(20, 20)
        self.toggle_pw_button.move(self.login_password.rect().right() - 24, 0)
        self.toggle_pw_button.clicked.connect(self.show_password_temporarily)

        self.hide_pw_timer = QTimer(self)
        self.hide_pw_timer.setSingleShot(True)
        self.hide_pw_timer.timeout.connect(self.hide_password)

    def login(self):
        username = self.login_user.text()
        password = self.login_password.text()
        try:
            db = self.context.db_manager
            db.execute("SELECT staff_id, staff_psw FROM staff WHERE staff_id = %s", (username,))
            result = db.fetchone()

            if result:
                stored_pw = result[1]
                if bcrypt.checkpw(password.encode('utf-8'), stored_pw.encode('utf-8')):
                    login_success = True
                elif password == stored_pw:
                    new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    db.execute("UPDATE staff SET staff_psw = %s WHERE staff_id = %s", (new_hash, username))
                    db.commit()
                    login_success = True
                else:
                    login_success = False

                if login_success:
                    self.context.staff_id = result[0]
                    db.log_action(self.context.staff_id, "Đăng nhập hệ thống")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Login Failed", "Sai tài khoản hoặc mật khẩu.")
            else:
                QMessageBox.warning(self, "Login Failed", "Không tìm thấy tài khoản.")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Lỗi kết nối: {str(e)}")

    def show_password_temporarily(self):
        self.login_password.setEchoMode(QLineEdit.EchoMode.Normal)
        self.toggle_pw_button.setIcon(QIcon("icon/eye_open.png"))
        self.hide_pw_timer.start(1000)

    def hide_password(self):
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.toggle_pw_button.setIcon(QIcon("icon/eye_closed.png"))

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.login()

    def goto_register(self):
        dialog = RegisterDialog(self.context)
        dialog.exec()


class RegisterDialog(QDialog):
    def __init__(self, context):
        super().__init__()
        self.context = context
        load_ui_file(self, 'register.ui')
        self.setWindowTitle("MediManager - Đăng ký")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setFixedSize(250, 220)

        self.register_button.clicked.connect(self.register)
        self.login_label.linkActivated.connect(self.goto_login)
        self.register_button.setDefault(True)

    def register(self):
        staff_id = self.staff_id.text()
        raw_pw = self.staff_psw.text()
        name = self.staff_name.text()
        phone = self.staff_phone.text()
        email = self.staff_email.text()
        hashed_pw = bcrypt.hashpw(raw_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            db = self.context.db_manager
            db.execute("SELECT staff_id FROM staff WHERE staff_id = %s", (staff_id,))
            if db.fetchone():
                QMessageBox.warning(self, "Lỗi", "Mã nhân viên đã tồn tại.")
                return

            db.execute("""
                INSERT INTO staff (staff_id, staff_psw, staff_name, staff_phone, staff_email)
                VALUES (%s, %s, %s, %s, %s)
            """, (staff_id, hashed_pw, name, phone, email))
            db.commit()
            db.log_action(self.context.staff_id, f"Thêm nhân viên: {staff_id}")

            QMessageBox.information(self, "Đăng ký thành công", "Tài khoản đã được tạo.")
            self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể đăng ký: {e}")

    def goto_login(self):
        self.close()
        dialog = AuthDialog(self.context)
        dialog.exec()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.register()
