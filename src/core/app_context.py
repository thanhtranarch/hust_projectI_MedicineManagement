"""
Application context - owns the database connection and the user session
"""

from .db_manager import DBManager


class AppContext:
    """Shared state passed to every window and dialog."""

    def __init__(self, staff_id=None, database=None):
        """
        Args:
            staff_id: Current logged-in staff ID, if any
            database: Path to the SQLite file, overriding the configured one
        """
        self.staff_id = staff_id
        self.db_manager = DBManager(database=database)
        self.connection = self.db_manager.connect()

        if not self.connection:
            raise ConnectionError("Failed to establish database connection")

    def set_user(self, staff_id):
        """Set the currently logged-in user."""
        self.staff_id = staff_id

    def is_authenticated(self):
        """True when a user is logged in."""
        return self.staff_id is not None

    def log_action(self, action):
        """Record an action for the logged-in user."""
        if self.staff_id:
            self.db_manager.log_action(self.staff_id, action)

    def close(self):
        """Release the database connection."""
        self.db_manager.close()

    def __del__(self):
        self.close()
