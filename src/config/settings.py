"""
Application settings and configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application-wide settings"""

    # Application Info
    APP_NAME = "MediManager"
    APP_VERSION = "2.0.0"
    APP_AUTHOR = "Trần Tiến Thạnh"

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
    FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
    UI_FORMS_DIR = os.path.join(BASE_DIR, "src", "ui", "forms")

    # UI Settings
    WINDOW_TITLE = "MediManager - Quản lý nhà thuốc"

    @staticmethod
    def get_icon_path(theme='dark'):
        """Get application icon path based on theme"""
        icon_name = f"app_icon_{theme}.ico"
        return os.path.join(Settings.ICONS_DIR, icon_name)

    @staticmethod
    def get_ui_file(filename):
        """Get UI file path"""
        return os.path.join(Settings.UI_FORMS_DIR, filename)

    @staticmethod
    def ensure_exports_dir():
        """Ensure exports directory exists"""
        os.makedirs(Settings.EXPORTS_DIR, exist_ok=True)
        return Settings.EXPORTS_DIR

    # Default Admin Account
    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin"
    DEFAULT_ADMIN_EMAIL = "admin@example.com"
    DEFAULT_ADMIN_PHONE = "0000000000"
    DEFAULT_ADMIN_NAME = "Administrator"
