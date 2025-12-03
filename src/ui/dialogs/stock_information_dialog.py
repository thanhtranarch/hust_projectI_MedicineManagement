"""
Stock information dialog (view-only)
"""

from src.ui.base import BaseDialog


class StockInformationDialog(BaseDialog):
    """Stock detail dialog - view only"""

    def __init__(self, context, stock_id, parent=None):
        super().__init__(context, 'stock_information.ui', 'Stock Details', parent)

        self.stock_id_value = stock_id

        # Load data
        self.load_stock_data()

    def load_stock_data(self):
        """Load stock data from database"""
        try:
            sql = "SELECT * FROM stock WHERE stock_id = %s"
            self.db.execute(sql, (self.stock_id_value,))
            result = self.db.fetchone()

            if result:
                # Set form fields (assuming basic stock info)
                self.lineEdit_stock_id.setText(str(result[0]))
                self.lineEdit_medicine_id.setText(str(result[1]))
                self.spinBox_quantity.setValue(result[2] or 0)

                if result[3]:  # updated_at
                    self.dateEdit_updated.setDate(result[3])

                # Make all fields read-only
                self.lineEdit_stock_id.setReadOnly(True)
                self.lineEdit_medicine_id.setReadOnly(True)
                self.spinBox_quantity.setReadOnly(True)
                self.dateEdit_updated.setReadOnly(True)
            else:
                self.show_warning("Stock not found")
                self.reject()

        except Exception as e:
            self.show_error(f"Error loading stock data: {e}")
