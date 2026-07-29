"""
Database configuration.

The application stores its data in a single local SQLite file. Nothing has to
be configured; SQLITE_PATH only exists so the location can be moved.
"""

import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'data', 'medimanager.db')


class DatabaseConfig:
    """Database configuration"""

    SQLITE_PATH = os.getenv('SQLITE_PATH') or DEFAULT_DB_PATH

    @classmethod
    def describe(cls):
        """Human-readable summary of the database in use, for startup output."""
        return f"SQLite {cls.SQLITE_PATH}"
