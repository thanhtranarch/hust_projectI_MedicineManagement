"""
Staff information dialog (view-only)
"""

from src.ui.base import BaseDialog


class StaffInformationDialog(BaseDialog):
    """Staff detail dialog - view only"""

    def __init__(self, context, staff_id, parent=None):
        super().__init__(context, 'staff_information.ui', 'Staff Details', parent)

        self.staff_id_value = staff_id

        # Load data
        self.load_staff_data()

    def load_staff_data(self):
        """Load staff data from database"""
        try:
            sql = """
                SELECT staff_name, staff_id, staff_position,
                       staff_phone, staff_email, staff_salary, hire_date
                FROM staff
                WHERE staff_id = %s
            """
            self.db.execute(sql, (self.staff_id_value,))
            result = self.db.fetchone()

            if result:
                # Set form fields
                self.staff_id.setText(str(result[1]))
                self.staff_name.setText(result[0] or "")
                self.staff_position.setText(result[2] or "")
                self.staff_phone.setText(result[3] or "")
                self.staff_email.setText(result[4] or "")
                self.staff_salary.setText(str(result[5]) if result[5] else "")
                self.hire_date.setText(str(result[6]) if result[6] else "")

                # Make all fields read-only
                self.staff_id.setReadOnly(True)
                self.staff_name.setReadOnly(True)
                self.staff_position.setReadOnly(True)
                self.staff_phone.setReadOnly(True)
                self.staff_email.setReadOnly(True)
                self.staff_salary.setReadOnly(True)
                self.hire_date.setReadOnly(True)
            else:
                self.show_warning("Staff not found")
                self.reject()

        except Exception as e:
            self.show_error(f"Error loading staff data: {e}")
