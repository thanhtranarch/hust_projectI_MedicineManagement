"""
Application context - manages database connection and user session
"""

from .db_manager import DBManager


class AppContext:
    """
    Application-wide context that manages database connection
    and user session information.
    """

    def __init__(self, staff_id=None):
        """
        Initialize application context

        Args:
            staff_id (str, optional): Current logged-in staff ID
        """
        self.staff_id = staff_id
        self.db_manager = DBManager()
        self.connection = self.db_manager.connect()

        if not self.connection:
            raise ConnectionError("Failed to establish database connection")

    def __del__(self):
        """Cleanup: close database connection when context is destroyed"""
        self.db_manager.close()

    def set_user(self, staff_id):
        """
        Set current logged-in user

        Args:
            staff_id (str): Staff ID of logged-in user
        """
        self.staff_id = staff_id

    def is_authenticated(self):
        """Check if a user is logged in"""
        return self.staff_id is not None

    def log_action(self, action):
        """
        Log user action to activity log

        Args:
            action (str): Description of the action
        """
        if self.staff_id:
            self.db_manager.log_action(self.staff_id, action)
