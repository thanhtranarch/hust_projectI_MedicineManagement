"""
Supplier information detail dialog with edit capability
"""

from PyQt6.QtWidgets import QDialogButtonBox, QMessageBox

from src.ui.base import BaseDialog
from src.utils.constants import MSG_SUCCESS_UPDATE, MSG_ERROR_UPDATE
from src.utils.helpers import validate_email, validate_phone


class SupplierInformationDialog(BaseDialog):
    """Supplier detail dialog with view/edit modes"""

    def __init__(self, context, supplier_id, parent=None):
        super().__init__(context, 'supplier_information.ui', 'Supplier Details', parent)

        self.supplier_id_value = supplier_id
        self.edit_mode = False
        self.original_data = {}

        # Connect buttons
        self.pushButton.clicked.connect(self.toggle_edit_mode)

        # Load supplier data
        self.load_supplier_data()

    def load_supplier_data(self):
        """Load supplier data from database"""
        try:
            sql = """
                SELECT supplier_id, supplier_name, supplier_address,
                       contact_name, contact_phone, contact_email, payment_terms
                FROM supplier
                WHERE supplier_id = %s
            """
            self.db.execute(sql, (self.supplier_id_value,))
            result = self.db.fetchone()

            if result:
                # Populate form fields (read-only initially)
                self.supplier_id.setText(str(result[0]))
                self.supplier_id.setReadOnly(True)

                self.supplier_name.setText(result[1] or "")
                self.supplier_name.setReadOnly(True)

                self.supplier_address.setPlainText(result[2] or "")
                self.supplier_address.setReadOnly(True)

                self.contact_name.setText(result[3] or "")
                self.contact_name.setReadOnly(True)

                self.contact_phone.setText(result[4] or "")
                self.contact_phone.setReadOnly(True)

                self.contact_email.setText(result[5] or "")
                self.contact_email.setReadOnly(True)

                if result[6]:
                    self.comboBox_payment_terms.setCurrentText(result[6])
                self.comboBox_payment_terms.setEnabled(False)
            else:
                self.show_warning("Supplier not found")
                self.reject()

        except Exception as e:
            self.show_error(f"Error loading supplier data: {e}")

    def toggle_edit_mode(self):
        """Toggle between view and edit modes"""
        self.edit_mode = not self.edit_mode

        # Toggle field editability
        self.supplier_name.setReadOnly(not self.edit_mode)
        self.supplier_address.setReadOnly(not self.edit_mode)
        self.contact_name.setReadOnly(not self.edit_mode)
        self.contact_phone.setReadOnly(not self.edit_mode)
        self.contact_email.setReadOnly(not self.edit_mode)
        self.comboBox_payment_terms.setEnabled(self.edit_mode)

        # Change button text
        self.pushButton.setText("💾 Save" if self.edit_mode else "Edit...")

        if self.edit_mode:
            # Entering edit mode - store original data
            self.original_data = {
                "name": self.supplier_name.text(),
                "address": self.supplier_address.toPlainText(),
                "contact": self.contact_name.text(),
                "phone": self.contact_phone.text(),
                "email": self.contact_email.text(),
                "payment": self.comboBox_payment_terms.currentText()
            }

            # Add cancel button
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)
            cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
            if cancel_btn:
                try:
                    cancel_btn.clicked.disconnect()
                except:
                    pass
                cancel_btn.clicked.connect(self.cancel_edit)
        else:
            # Exiting edit mode - save data
            if self.validate_form()[0]:
                self.save_supplier_data()
            else:
                # Validation failed - stay in edit mode
                self.edit_mode = True
                self.pushButton.setText("💾 Save")

            # Remove cancel button
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

    def validate_form(self):
        """Validate form data"""
        email = self.contact_email.text().strip()
        phone = self.contact_phone.text().strip()

        if email and not validate_email(email):
            return False, "Invalid email format"

        if phone and not validate_phone(phone):
            return False, "Invalid phone format (must be 10 digits)"

        return True, ""

    def save_supplier_data(self):
        """Save supplier data to database"""
        try:
            payment = self.comboBox_payment_terms.currentText().strip() or "COD"

            sql = """
                UPDATE supplier SET
                    supplier_name = %s,
                    supplier_address = %s,
                    contact_name = %s,
                    contact_phone = %s,
                    contact_email = %s,
                    payment_terms = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE supplier_id = %s
            """
            values = (
                self.supplier_name.text().strip(),
                self.supplier_address.toPlainText().strip(),
                self.contact_name.text().strip(),
                self.contact_phone.text().strip(),
                self.contact_email.text().strip(),
                payment,
                self.supplier_id.text()
            )

            self.db.execute(sql, values)
            self.db.commit()

            self.log_action(f"Updated supplier: {self.supplier_id.text()}")
            self.show_success(MSG_SUCCESS_UPDATE)

        except Exception as e:
            self.db.rollback()
            self.show_error(f"{MSG_ERROR_UPDATE}: {e}")
            # Revert to edit mode
            self.edit_mode = True
            self.pushButton.setText("💾 Save")

    def cancel_edit(self):
        """Cancel editing and restore original data"""
        if self.edit_mode:
            # Restore original data
            self.supplier_name.setText(self.original_data["name"])
            self.supplier_address.setPlainText(self.original_data["address"])
            self.contact_name.setText(self.original_data["contact"])
            self.contact_phone.setText(self.original_data["phone"])
            self.contact_email.setText(self.original_data["email"])

            idx = self.comboBox_payment_terms.findText(self.original_data["payment"])
            if idx >= 0:
                self.comboBox_payment_terms.setCurrentIndex(idx)

            # Return to view mode
            self.edit_mode = False
            self.supplier_name.setReadOnly(True)
            self.supplier_address.setReadOnly(True)
            self.contact_name.setReadOnly(True)
            self.contact_phone.setReadOnly(True)
            self.contact_email.setReadOnly(True)
            self.comboBox_payment_terms.setEnabled(False)
            self.pushButton.setText("Edit...")
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

            self.log_action(f"Cancelled edit for supplier: {self.supplier_id.text()}")
