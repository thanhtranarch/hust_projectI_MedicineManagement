"""
Database configuration for Supabase PostgreSQL
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """Database connection configuration"""

    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # PostgreSQL Connection Parameters
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')

    # Connection Pool Settings
    MIN_CONNECTIONS = 1
    MAX_CONNECTIONS = 10

    # Timeout Settings (seconds)
    CONNECTION_TIMEOUT = 30
    QUERY_TIMEOUT = 60

    @classmethod
    def get_connection_params(cls):
        """Get database connection parameters as dictionary"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD
        }

    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = ['DB_HOST', 'DB_PASSWORD']
        missing = [var for var in required_vars if not getattr(cls, var)]

        if missing:
            raise ValueError(
                f"Missing required database configuration: {', '.join(missing)}\n"
                "Please check your .env file."
            )

        return True
