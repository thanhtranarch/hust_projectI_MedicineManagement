#!/usr/bin/env python3
"""
MediManager - Medicine Management System
Main entry point for the application

Author: Trần Tiến Thạnh
Version: 2.0.0
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QMessageBox
from src.config import Settings, DatabaseConfig


def main():
    """Main application entry point"""

    # Validate database configuration
    try:
        DatabaseConfig.validate_config()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📝 Please follow these steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Supabase credentials in .env file")
        print("3. Run the application again")
        sys.exit(1)

    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName(Settings.APP_NAME)
    app.setApplicationVersion(Settings.APP_VERSION)

    # Show startup message
    print("=" * 60)
    print(f"  {Settings.APP_NAME} v{Settings.APP_VERSION}")
    print(f"  {Settings.APP_AUTHOR}")
    print("=" * 60)
    print()

    try:
        # Import and run the legacy application (MediManager.py)
        # TODO: Refactor MediManager.py into new structure
        print("⚠️  Running in legacy mode...")
        print("⚠️  Full refactor to new structure in progress...")
        print()

        # For now, we'll import the old MediManager module
        # In future versions, this will be replaced with new structure
        import MediManager

        # The old MediManager.py should handle the rest
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()

        # Show error dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.setText("Application failed to start")
        msg.setInformativeText(str(e))
        msg.exec()

        sys.exit(1)


if __name__ == "__main__":
    main()
