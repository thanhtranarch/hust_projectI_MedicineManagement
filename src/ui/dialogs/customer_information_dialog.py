"""
Customer information dialog with view/edit capability
"""

from PyQt6.QtWidgets import QPushButton

from src.ui.base import BaseDialog
from src.utils.constants import MSG_SUCCESS_UPDATE, MSG_ERROR_UPDATE, MSG_SUCCESS_DELETE
from src.utils.helpers import validate_email, validate_phone


class CustomerInformationDialog(BaseDialog):
    """Customer detail dialog with view/edit modes"""

    def __init__(self, context, customer_id, parent=None):
        super().__init__(context, 'customer_information.ui', 'Customer Details', parent)

        self.customer_id_value = customer_id
        self.edit_mode = False
        self.original_data = {}

        # Add edit button (if not in UI)
        if not hasattr(self, 'edit_button'):
            self.edit_button = QPushButton("Edit...", self)
            self.edit_button.setGeometry(80, 445, 80, 28)
            self.edit_button.clicked.connect(self.toggle_edit_mode)
            self.edit_button.show()

        # Load data
        self.load_customer_data()
        self.set_fields_editable(False)

    def load_customer_data(self):
        """Load customer data from database"""
        try:
            sql = """
                SELECT customer_id, customer_name, customer_phone, customer_email
                FROM customer
                WHERE customer_id = %s
            """
            self.db.execute(sql, (self.customer_id_value,))
            result = self.db.fetchone()

            if result:
                self.customer_id.setText(str(result[0]))
                self.customer_id.setReadOnly(True)

                self.customer_name.setText(result[1] or "")
                self.customer_phone.setText(result[2] or "")
                self.customer_email.setText(result[3] or "")
            else:
                self.show_warning("Customer not found")
                self.reject()

        except Exception as e:
            self.show_error(f"Error loading customer data: {e}")

    def set_fields_editable(self, editable):
        """Set form fields editable state"""
        self.customer_name.setReadOnly(not editable)
        self.customer_phone.setReadOnly(not editable)
        self.customer_email.setReadOnly(not editable)

    def toggle_edit_mode(self):
        """Toggle between view and edit modes"""
        self.edit_mode = not self.edit_mode

        if self.edit_mode:
            # Store original data
            self.original_data = {
                "name": self.customer_name.text(),
                "phone": self.customer_phone.text(),
                "email": self.customer_email.text()
            }

            # Enable editing
            self.set_fields_editable(True)
            self.edit_button.setText("💾 Save")
        else:
            # Validate and save
            is_valid, error_msg = self.validate_form()
            if is_valid:
                self.save_customer_data()
                self.set_fields_editable(False)
                self.edit_button.setText("Edit...")
            else:
                self.show_warning(error_msg)
                # Stay in edit mode
                self.edit_mode = True

    def validate_form(self):
        """Validate form data"""
        email = self.customer_email.text().strip()
        phone = self.customer_phone.text().strip()

        if email and not validate_email(email):
            return False, "Invalid email format"

        if phone and not validate_phone(phone):
            return False, "Invalid phone format (must be 10 digits)"

        return True, ""

    def save_customer_data(self):
        """Save customer data to database"""
        try:
            sql = """
                UPDATE customer SET
                    customer_name = %s,
                    customer_phone = %s,
                    customer_email = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE customer_id = %s
            """
            values = (
                self.customer_name.text().strip(),
                self.customer_phone.text().strip(),
                self.customer_email.text().strip(),
                self.customer_id.text()
            )

            self.db.execute(sql, values)
            self.db.commit()

            self.log_action(f"Updated customer: {self.customer_id.text()}")
            self.show_success(MSG_SUCCESS_UPDATE)

        except Exception as e:
            self.db.rollback()
            self.show_error(f"{MSG_ERROR_UPDATE}: {e}")
            self.edit_mode = True
            self.edit_button.setText("💾 Save")

    def delete_customer(self):
        """Delete customer (if needed)"""
        if self.confirm_action("Delete this customer?"):
            try:
                sql = "DELETE FROM customer WHERE customer_id = %s"
                self.db.execute(sql, (self.customer_id_value,))
                self.db.commit()

                self.log_action(f"Deleted customer: {self.customer_id_value}")
                self.show_success(MSG_SUCCESS_DELETE)
                self.accept()

            except Exception as e:
                self.db.rollback()
                self.show_error(f"Error deleting customer: {e}")
