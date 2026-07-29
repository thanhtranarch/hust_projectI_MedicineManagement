#!/usr/bin/env python3
"""
MediManager - Medicine Management System
Main entry point for the application

Author: Trần Tiến Thạnh
Version: 2.0.0
"""

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from src.config import DatabaseConfig, Settings
from src.core import AppContext
from src.ui.dialogs import LoginDialog


def show_error(title, text, detail=""):
    """Display a blocking error dialog."""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle(title)
    msg.setText(text)
    if detail:
        msg.setInformativeText(detail)
    msg.exec()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName(Settings.APP_NAME)
    app.setApplicationVersion(Settings.APP_VERSION)

    print("=" * 60)
    print(f"  {Settings.APP_NAME} v{Settings.APP_VERSION}")
    print(f"  {Settings.APP_AUTHOR}")
    print("=" * 60)
    print(f"Database: {DatabaseConfig.describe()}")

    try:
        context = AppContext()
        print("Connected to database.")

        login_window = LoginDialog(context)
        login_window.show()

        sys.exit(app.exec())

    except ConnectionError as e:
        print(f"Database connection error: {e}")
        show_error(
            "Connection Error",
            "Failed to connect to the database",
            f"{DatabaseConfig.describe()}\n\n{e}",
        )
        sys.exit(1)

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        show_error("Error", "Application failed to start", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
