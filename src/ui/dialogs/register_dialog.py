"""
Register dialog window for new staff registration
"""

import bcrypt
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox

from src.ui.base import BaseDialog
from src.utils.helpers import validate_email, validate_phone


class RegisterDialog(BaseDialog):
    """Register dialog for creating new staff accounts"""

    def __init__(self, context):
        """
        Initialize register dialog

        Args:
            context: Application context
        """
        super().__init__(context, 'register.ui', 'MediManager - Register')

        # Setup UI
        self.setFixedSize(250, 220)

        # Connect signals
        self.login_label.linkActivated.connect(self.goto_login)
        self.register_button.clicked.connect(self.register)
        self.register_button.setDefault(True)

    def register(self):
        """Handle register button click"""
        # Get form data
        staff_id = self.staff_id.text().strip()
        password = self.staff_psw.text()
        name = self.staff_name.text().strip()
        phone = self.staff_phone.text().strip()
        email = self.staff_email.text().strip()

        # Validate input
        is_valid, error_msg = self._validate_registration(staff_id, password, name, phone, email)
        if not is_valid:
            self.show_warning(error_msg)
            return

        try:
            # Check if staff ID already exists
            self.db.execute("SELECT staff_id FROM staff WHERE staff_id = %s", (staff_id,))
            if self.db.fetchone():
                self.show_warning("Staff ID already exists. Please choose another ID.")
                return

            # Hash password with bcrypt
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Insert new staff
            insert_sql = """
                INSERT INTO staff (staff_id, staff_psw, staff_name, staff_phone, staff_email, staff_position)
                VALUES (%s, %s, %s, %s, %s, 'staff')
            """
            self.db.execute(insert_sql, (staff_id, hashed_password, name, phone, email))
            self.db.commit()

            # Log action (if admin is logged in)
            if self.context.is_authenticated():
                self.log_action(f"Registered new staff: {staff_id}")

            # Show success message
            self.show_success("Registration successful! You can now login.")

            # Clear form
            self._clear_form()

            # Optional: Go to login
            # self.goto_login()

        except Exception as e:
            self.db.rollback()
            self.show_error(f"Registration failed: {str(e)}")

    def _validate_registration(self, staff_id, password, name, phone, email):
        """
        Validate registration form data

        Args:
            staff_id: Staff ID
            password: Password
            name: Staff name
            phone: Phone number
            email: Email address

        Returns:
            tuple: (is_valid, error_message)
        """
        if not staff_id:
            return False, "Staff ID is required"

        if len(staff_id) < 3:
            return False, "Staff ID must be at least 3 characters"

        if not password:
            return False, "Password is required"

        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        if not name:
            return False, "Name is required"

        if phone and not validate_phone(phone):
            return False, "Invalid phone number format"

        if email and not validate_email(email):
            return False, "Invalid email format"

        return True, ""

    def _clear_form(self):
        """Clear all form fields"""
        self.staff_id.clear()
        self.staff_psw.clear()
        self.staff_name.clear()
        self.staff_phone.clear()
        self.staff_email.clear()

    def keyPressEvent(self, event):
        """Handle key press events (Enter/Return to register)"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.register()

    def goto_login(self):
        """Navigate to login window"""
        from src.ui.dialogs.login_dialog import LoginDialog

        self.login_window = LoginDialog(self.context)
        self.login_window.show()
        self.close()
