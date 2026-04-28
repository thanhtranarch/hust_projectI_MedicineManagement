from services.db_service import DBManager

# Connect to DataBase
class AppContext:
    def __init__(self, staff_id = None):
        self.staff_id = staff_id
        self.db_manager = DBManager()
        self.connection = self.db_manager.connect()
        
    def __del__(self):
        self.db_manager.close()