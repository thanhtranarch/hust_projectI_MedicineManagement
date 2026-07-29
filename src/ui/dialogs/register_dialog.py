"""
Register dialog window for new staff registration
"""

from PyQt6.QtCore import Qt

from src.services import AuthService
from src.ui.base import BaseDialog


class RegisterDialog(BaseDialog):
    """Register dialog for creating new staff accounts"""

    def __init__(self, context):
        """
        Initialize register dialog

        Args:
            context: Application context
        """
        super().__init__(context, 'register.ui', 'MediManager - Register')

        self.auth_service = AuthService(context)

        # Setup UI
        self.setFixedSize(250, 220)

        # Connect signals
        self.login_label.linkActivated.connect(self.goto_login)
        self.register_button.clicked.connect(self.register)
        self.register_button.setDefault(True)

    def register(self):
        """Handle register button click"""
        staff_id = self.staff_id.text().strip()

        success, message = self.auth_service.register(
            staff_id=staff_id,
            password=self.staff_psw.text(),
            name=self.staff_name.text().strip(),
            phone=self.staff_phone.text().strip(),
            email=self.staff_email.text().strip(),
        )

        if not success:
            self.show_warning(message)
            return

        if self.context.is_authenticated():
            self.log_action(f"Registered new staff: {staff_id}")

        self.show_success(f"{message}. Bạn có thể đăng nhập ngay.")
        self._clear_form()

    def _clear_form(self):
        """Clear all form fields"""
        for field in (self.staff_id, self.staff_psw, self.staff_name,
                      self.staff_phone, self.staff_email):
            field.clear()

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
