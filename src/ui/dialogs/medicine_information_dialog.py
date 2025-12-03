"""
Medicine information dialog with view/edit capability
"""

from PyQt6.QtWidgets import QPushButton, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal

from src.ui.base import BaseDialog
from src.utils.constants import MSG_SUCCESS_UPDATE, MSG_ERROR_UPDATE, MSG_SUCCESS_DELETE


class MedicineInformationDialog(BaseDialog):
    """Medicine detail dialog with view/edit modes and delete capability"""

    data_updated = pyqtSignal()

    def __init__(self, context, medicine_id, parent=None):
        super().__init__(context, 'medicine_information.ui', 'Medicine Details', parent)

        self.medicine_id_value = medicine_id
        self.edit_mode = False
        self.original_data = {}

        # Setup buttons
        self.pushButton.clicked.connect(self.toggle_edit_mode)
        self.deleteButton.clicked.connect(self.confirm_delete_medicine)
        self.deleteButton.setEnabled(False)

        # Load data
        self.load_medicine_data()

    def load_medicine_data(self):
        """Load medicine data from database"""
        try:
            sql = """
                SELECT m.medicine_id, m.medicine_name, m.generic_name,
                       c.category_name, s.supplier_name,
                       m.batch_number, m.expiration_date, m.stock_quantity,
                       m.unit_price, m.sale_price
                FROM medicine m
                JOIN category c ON m.category_id = c.category_id
                JOIN supplier s ON m.supplier_id = s.supplier_id
                WHERE m.medicine_id = %s
            """
            self.db.execute(sql, (self.medicine_id_value,))
            result = self.db.fetchone()

            if result:
                # Set form fields
                self.medicine_id.setText(str(result[0]))
                self.medicine_id.setReadOnly(True)

                self.medicine_name.setText(result[1] or "")
                self.generic_name.setText(result[2] or "")
                self.category_name.setText(result[3] or "")
                self.supplier_name.setText(result[4] or "")
                self.batch_number.setText(result[5] or "")

                if result[6]:  # expiration_date
                    self.expiration_date.setDate(result[6])

                self.stock_quantity.setValue(result[7] or 0)
                self.unit_price.setValue(float(result[8]) if result[8] else 0.0)
                self.sale_price.setValue(float(result[9]) if result[9] else 0.0)

                # Set all fields to read-only initially
                self.set_fields_editable(False)
            else:
                self.show_warning("Medicine not found")
                self.reject()

        except Exception as e:
            self.show_error(f"Error loading medicine data: {e}")

    def set_fields_editable(self, editable):
        """Set form fields editable state"""
        self.medicine_name.setReadOnly(not editable)
        self.generic_name.setReadOnly(not editable)
        self.category_name.setReadOnly(True)   # Always read-only
        self.supplier_name.setReadOnly(True)   # Always read-only
        self.batch_number.setReadOnly(not editable)

        self.expiration_date.setEnabled(editable)
        self.stock_quantity.setEnabled(editable)
        self.unit_price.setEnabled(editable)
        self.sale_price.setEnabled(editable)

    def toggle_edit_mode(self):
        """Toggle between view and edit modes"""
        self.edit_mode = not self.edit_mode

        if self.edit_mode:
            # Store original data
            self.original_data = {
                "name": self.medicine_name.text(),
                "generic": self.generic_name.text(),
                "category": self.category_name.text(),
                "supplier": self.supplier_name.text(),
                "batch": self.batch_number.text(),
                "exp_date": self.expiration_date.date(),
                "quantity": self.stock_quantity.value(),
                "unit_price": self.unit_price.value(),
                "sale_price": self.sale_price.value()
            }

            # Enable editing
            self.set_fields_editable(True)
            self.pushButton.setText("💾 Save")
            self.deleteButton.setEnabled(True)

            # Change buttonBox to show Cancel button
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel)

            # Connect cancel button
            cancel_btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Cancel)
            if cancel_btn:
                try:
                    cancel_btn.clicked.disconnect()
                except:
                    pass
                cancel_btn.clicked.connect(self.cancel_edit)
        else:
            # Save and switch back to view mode
            self.save_medicine_data()
            self.set_fields_editable(False)
            self.pushButton.setText("Edit...")
            self.deleteButton.setEnabled(False)
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

    def save_medicine_data(self):
        """Save medicine data to database"""
        try:
            sql = """
                UPDATE medicine SET
                    medicine_name = %s,
                    generic_name = %s,
                    batch_number = %s,
                    expiration_date = %s,
                    stock_quantity = %s,
                    unit_price = %s,
                    sale_price = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE medicine_id = %s
            """
            values = (
                self.medicine_name.text().strip(),
                self.generic_name.text().strip(),
                self.batch_number.text().strip(),
                self.expiration_date.date().toString("yyyy-MM-dd"),
                self.stock_quantity.value(),
                self.unit_price.value(),
                self.sale_price.value(),
                self.medicine_id.text()
            )

            self.db.execute(sql, values)
            self.db.commit()

            self.log_action(f"Updated medicine: {self.medicine_id.text()}")
            self.show_success(MSG_SUCCESS_UPDATE)

        except Exception as e:
            self.db.rollback()
            self.show_error(f"{MSG_ERROR_UPDATE}: {e}")
            # Stay in edit mode
            self.edit_mode = True
            self.pushButton.setText("💾 Save")

    def cancel_edit(self):
        """Cancel edit and restore original data"""
        if self.edit_mode:
            # Restore original data
            self.medicine_name.setText(self.original_data["name"])
            self.generic_name.setText(self.original_data["generic"])
            self.category_name.setText(self.original_data["category"])
            self.supplier_name.setText(self.original_data["supplier"])
            self.batch_number.setText(self.original_data["batch"])
            self.expiration_date.setDate(self.original_data["exp_date"])
            self.stock_quantity.setValue(self.original_data["quantity"])
            self.unit_price.setValue(self.original_data["unit_price"])
            self.sale_price.setValue(self.original_data["sale_price"])

            # Switch back to view mode
            self.set_fields_editable(False)
            self.edit_mode = False
            self.pushButton.setText("Edit...")
            self.deleteButton.setEnabled(False)
            self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)
            self.show_success("Changes cancelled")

    def confirm_delete_medicine(self):
        """Confirm before deleting medicine"""
        if self.confirm_action("Delete this medicine?"):
            self.delete_medicine()

    def delete_medicine(self):
        """Delete medicine from database"""
        try:
            sql = "DELETE FROM medicine WHERE medicine_id = %s"
            self.db.execute(sql, (self.medicine_id.text(),))
            self.db.commit()

            self.log_action(f"Deleted medicine: {self.medicine_id.text()}")
            self.show_success(MSG_SUCCESS_DELETE)

            # Emit signal to refresh parent
            self.data_updated.emit()
            self.accept()

        except Exception as e:
            self.db.rollback()
            self.show_error(f"Error deleting medicine: {e}")
