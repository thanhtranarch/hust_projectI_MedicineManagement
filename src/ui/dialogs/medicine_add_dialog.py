"""
Medicine add dialog for creating new medicines
"""

from PyQt6.QtWidgets import QDialogButtonBox

from src.ui.base import BaseDialog
from src.utils.constants import MSG_SUCCESS_ADD, MSG_ERROR_ADD


class MedicineAddDialog(BaseDialog):
    """Dialog for adding new medicine"""

    def __init__(self, context, parent=None):
        super().__init__(context, 'medicine_information_add.ui', 'Add New Medicine', parent)

        # Initialize category combo
        self.init_category_combo()

        # Connect save/cancel buttons
        save_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Save)
        cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)

        if save_btn:
            save_btn.clicked.connect(self.save_medicine)
        if cancel_btn:
            cancel_btn.clicked.connect(self.reject)

    def init_category_combo(self):
        """Initialize category combo box with data from database"""
        try:
            sql = "SELECT DISTINCT category_name FROM category ORDER BY category_name"
            self.db.execute(sql)
            results = self.db.fetchall()

            self.comboBox.clear()
            for row in results:
                self.comboBox.addItem(row[0])

        except Exception as e:
            self.show_error(f"Error loading categories: {e}")

    def validate_form(self):
        """Validate form data"""
        name = self.medicine_name.text().strip()

        if not name:
            return False, "Medicine name is required"

        return True, ""

    def save_medicine(self):
        """Save new medicine to database"""
        try:
            # Validate form
            is_valid, error_msg = self.validate_form()
            if not is_valid:
                self.show_warning(error_msg)
                return

            name = self.medicine_name.text().strip()
            generic_name = self.generic_name.text().strip()
            category = self.comboBox.currentText().strip()

            # Get category_id from category name
            sql = "SELECT category_id FROM category WHERE category_name = %s"
            self.db.execute(sql, (category,))
            result = self.db.fetchone()
            category_id = result[0] if result else None

            if not category_id:
                self.show_warning("Invalid category selected")
                return

            # Insert new medicine
            sql_insert = """
                INSERT INTO medicine (medicine_name, generic_name, category_id)
                VALUES (%s, %s, %s)
            """
            self.db.execute(sql_insert, (name, generic_name, category_id))
            self.db.commit()

            self.log_action(f"Added new medicine: {name}")
            self.show_success(MSG_SUCCESS_ADD)
            self.accept()

        except Exception as e:
            self.db.rollback()
            self.show_error(f"{MSG_ERROR_ADD}: {e}")
