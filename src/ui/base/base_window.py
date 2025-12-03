"""
Base window class for all main windows
"""

import os
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6 import uic

from src.config import Settings


class BaseWindow(QMainWindow):
    """
    Base class for all main application windows

    Provides common functionality:
    - UI file loading
    - Window icon setup
    - Context management
    - Common utility methods
    """

    def __init__(self, context, ui_filename, window_title=None):
        """
        Initialize base window

        Args:
            context: Application context with database connection
            ui_filename: Name of the .ui file (e.g., 'main.ui')
            window_title: Optional window title (defaults to app name)
        """
        super().__init__()

        self.context = context
        self.db = context.db_manager

        # Load UI file
        self._load_ui(ui_filename)

        # Setup window
        self.setWindowTitle(window_title or Settings.WINDOW_TITLE)
        self._setup_window_icon()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def _load_ui(self, ui_filename):
        """Load UI file from forms directory"""
        ui_path = Settings.get_ui_file(ui_filename)

        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"UI file not found: {ui_path}")

        uic.loadUi(ui_path, self)

    def _setup_window_icon(self):
        """Setup window icon based on current theme"""
        from src.utils import get_theme

        theme = get_theme()
        icon_path = Settings.get_icon_path(theme)

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def log_action(self, action):
        """
        Log user action to activity log

        Args:
            action: Description of the action
        """
        self.context.log_action(action)

    def show_success(self, message, title="Success"):
        """Show success message dialog"""
        QMessageBox.information(self, title, message)

    def show_error(self, message, title="Error"):
        """Show error message dialog"""
        QMessageBox.critical(self, title, message)

    def show_warning(self, message, title="Warning"):
        """Show warning message dialog"""
        QMessageBox.warning(self, title, message)

    def confirm_action(self, message, title="Confirm"):
        """
        Show confirmation dialog

        Returns:
            bool: True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def refresh_data(self):
        """
        Refresh window data - to be overridden by subclasses
        """
        pass

    def closeEvent(self, event):
        """Handle window close event"""
        # Can be overridden by subclasses for cleanup
        event.accept()
