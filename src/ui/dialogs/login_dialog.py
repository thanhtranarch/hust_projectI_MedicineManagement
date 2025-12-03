"""
Login dialog window
"""

import os
import bcrypt
from PyQt6.QtWidgets import QLineEdit, QToolButton, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer

from src.ui.base import BaseDialog
from src.utils.constants import MSG_LOGIN_SUCCESS, MSG_LOGIN_FAILED


class LoginDialog(BaseDialog):
    """Login dialog for user authentication"""

    def __init__(self, context):
        """
        Initialize login dialog

        Args:
            context: Application context
        """
        super().__init__(context, 'login.ui', 'MediManager - Login')

        self.main_window = None

        # Setup UI
        self.setFixedSize(250, 110)

        # Connect signals
        self.register_label.linkActivated.connect(self.goto_register)
        self.login_button.clicked.connect(self.login)
        self.login_button.setDefault(True)

        # Setup password field
        self._setup_password_field()

    def _setup_password_field(self):
        """Setup password field with show/hide toggle"""
        # Hide password by default
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Create eye icon toggle button
        self.toggle_pw_button = QToolButton(self.login_password)

        # Get icon path from assets
        from src.config import Settings
        eye_closed_path = os.path.join(Settings.ICONS_DIR, "eye_closed.png")

        self.toggle_pw_button.setIcon(QIcon(eye_closed_path))
        self.toggle_pw_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_pw_button.setStyleSheet("border: none; padding: 0px;")
        self.toggle_pw_button.setFixedSize(20, 20)
        self.toggle_pw_button.move(self.login_password.rect().right() - 24, 0)

        # Connect toggle button
        self.toggle_pw_button.clicked.connect(self.show_password_temporarily)

        # Timer to hide password after 1 second
        self.hide_pw_timer = QTimer(self)
        self.hide_pw_timer.setSingleShot(True)
        self.hide_pw_timer.timeout.connect(self.hide_password)

    def login(self):
        """Handle login button click"""
        username = self.login_user.text().strip()
        password = self.login_password.text()

        # Validate input
        if not username or not password:
            self.show_warning("Please enter username and password")
            return

        try:
            # Query user from database
            sql = 'SELECT staff_id, staff_psw FROM staff WHERE staff_id = %s'
            self.db.execute(sql, (username,))
            result = self.db.fetchone()

            if not result:
                self.show_warning(MSG_LOGIN_FAILED)
                return

            staff_id, stored_password = result
            login_success = self._verify_password(password, stored_password, staff_id)

            if login_success:
                self._handle_successful_login(staff_id)
            else:
                self.show_warning(MSG_LOGIN_FAILED)

        except Exception as e:
            self.show_error(f"Login error: {str(e)}")

    def _verify_password(self, input_password, stored_password, staff_id):
        """
        Verify password with bcrypt, with fallback for legacy passwords

        Args:
            input_password: User input password
            stored_password: Stored password hash
            staff_id: Staff ID for updating legacy passwords

        Returns:
            bool: True if password is correct
        """
        try:
            # Try bcrypt verification
            if bcrypt.checkpw(input_password.encode('utf-8'), stored_password.encode('utf-8')):
                return True
        except (ValueError, AttributeError):
            # Not a bcrypt hash - check if it's a legacy plain-text password
            if input_password == stored_password:
                # Auto-upgrade to bcrypt
                self._upgrade_password(staff_id, input_password)
                return True

        return False

    def _upgrade_password(self, staff_id, plain_password):
        """
        Upgrade legacy plain-text password to bcrypt hash

        Args:
            staff_id: Staff ID
            plain_password: Plain text password
        """
        try:
            new_hash = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.db.execute(
                "UPDATE staff SET staff_psw = %s WHERE staff_id = %s",
                (new_hash, staff_id)
            )
            self.db.commit()
            print(f"Auto-upgraded password for user: {staff_id}")
        except Exception as e:
            print(f"Failed to upgrade password: {e}")

    def _handle_successful_login(self, staff_id):
        """
        Handle successful login

        Args:
            staff_id: Logged in staff ID
        """
        # Set user in context
        self.context.set_user(staff_id)

        # Log action
        self.log_action("Đăng nhập hệ thống")

        # Show success message
        self.show_success(MSG_LOGIN_SUCCESS)

        # Open main window
        from src.ui.windows.main_window import MainWindow
        self.main_window = MainWindow(self.context)
        self.main_window.show()

        # Close login dialog
        self.close()

    def show_password_temporarily(self):
        """Show password for 1 second when eye icon is clicked"""
        from src.config import Settings

        # Show password
        self.login_password.setEchoMode(QLineEdit.EchoMode.Normal)

        # Change icon to "eye open"
        eye_open_path = os.path.join(Settings.ICONS_DIR, "eye_open.png")
        if os.path.exists(eye_open_path):
            self.toggle_pw_button.setIcon(QIcon(eye_open_path))

        # Start timer to hide after 1 second
        self.hide_pw_timer.start(1000)

    def hide_password(self):
        """Hide password and restore eye icon"""
        from src.config import Settings

        # Hide password
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Restore "eye closed" icon
        eye_closed_path = os.path.join(Settings.ICONS_DIR, "eye_closed.png")
        self.toggle_pw_button.setIcon(QIcon(eye_closed_path))

    def keyPressEvent(self, event):
        """Handle key press events (Enter/Return to login)"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.login()

    def goto_register(self):
        """Navigate to register window"""
        from src.ui.dialogs.register_dialog import RegisterDialog

        self.register_window = RegisterDialog(self.context)
        self.register_window.show()
        self.close()
