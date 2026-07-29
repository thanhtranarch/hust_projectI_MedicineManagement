"""
Database configuration.

Two backends are supported:
  * ``postgres`` - Supabase or any PostgreSQL server, configured through .env
  * ``sqlite``   - a local file, used automatically when no server is configured
"""

import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DatabaseConfig:
    """Database connection configuration"""

    # Backend selection: 'postgres', 'sqlite', or unset to auto-detect
    DB_BACKEND = os.getenv('DB_BACKEND', '').strip().lower()

    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # PostgreSQL Connection Parameters
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT') or 5432)
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    # SQLite database file
    SQLITE_PATH = os.getenv('SQLITE_PATH') or os.path.join(BASE_DIR, 'data', 'medimanager.db')

    # Timeout Settings (seconds)
    CONNECTION_TIMEOUT = 30

    @classmethod
    def detect_backend(cls):
        """
        Decide which backend to use.

        An explicit DB_BACKEND wins. Otherwise PostgreSQL is used when server
        credentials are present, and SQLite when they are not - so the app runs
        out of the box with no configuration at all.
        """
        if cls.DB_BACKEND in ('postgres', 'postgresql', 'supabase'):
            return 'postgres'
        if cls.DB_BACKEND == 'sqlite':
            return 'sqlite'
        return 'postgres' if (cls.DB_HOST and cls.DB_PASSWORD) else 'sqlite'

    @classmethod
    def get_connection_params(cls):
        """PostgreSQL connection parameters"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'connect_timeout': cls.CONNECTION_TIMEOUT,
        }

    @classmethod
    def describe(cls):
        """Human-readable summary of the active connection, for startup output."""
        if cls.detect_backend() == 'postgres':
            return f"PostgreSQL {cls.DB_USER}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        return f"SQLite {cls.SQLITE_PATH}"

    @classmethod
    def validate_config(cls):
        """
        Check that the selected backend has everything it needs.

        SQLite needs nothing, so validation only applies to PostgreSQL.
        """
        if cls.detect_backend() == 'sqlite':
            return True

        missing = [var for var in ('DB_HOST', 'DB_PASSWORD') if not getattr(cls, var)]
        if missing:
            raise ValueError(
                f"Missing required database configuration: {', '.join(missing)}\n"
                "Please check your .env file, or unset DB_BACKEND to use SQLite."
            )
        return True
