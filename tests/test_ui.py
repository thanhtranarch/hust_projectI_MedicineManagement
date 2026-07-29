"""
UI smoke tests.

Every window and dialog is constructed against a real (temporary) database.
This catches the failures unit tests miss: a missing .ui file, a widget name
that no longer exists, or a query that does not match the schema.

Runs headless via Qt's offscreen platform, so no display is needed.
"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6", reason="PyQt6 is required for UI tests")

from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from src.config import Settings  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    """A single QApplication shared by the whole test session."""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def no_popups(monkeypatch):
    """
    Replace modal message boxes with a recorder.

    Anything a screen reports through QMessageBox is collected instead of
    blocking the test run, so a failure shows up as a captured message.
    """
    captured = []

    def record(kind):
        def handler(parent, title, text, *args, **kwargs):
            captured.append((kind, title, text))
            return QMessageBox.StandardButton.No
        return handler

    for kind in ("information", "critical", "warning", "question", "about"):
        monkeypatch.setattr(QMessageBox, kind, staticmethod(record(kind)))

    return captured


def assert_no_errors(captured):
    """Fail with the reported text if a screen surfaced an error or warning."""
    problems = [c for c in captured if c[0] in ("critical", "warning")]
    assert not problems, "screen reported: " + "; ".join(
        f"{kind}/{title}: {text}" for kind, title, text in problems
    )


class TestForms:
    def test_every_referenced_ui_file_exists(self):
        """Each 'xxx.ui' named in the source must be present in forms/."""
        import re

        referenced = set()
        src_dir = os.path.join(Settings.BASE_DIR, "src")
        for root, _, files in os.walk(src_dir):
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                with open(os.path.join(root, filename), encoding="utf-8") as fh:
                    referenced |= set(re.findall(r"['\"]([a-z_]+\.ui)['\"]", fh.read()))

        missing = [name for name in referenced
                   if not os.path.exists(Settings.get_ui_file(name))]
        assert not missing, f"missing .ui files: {sorted(missing)}"

    def test_no_orphan_ui_files(self):
        """Every form should be loaded by something; strays are dead weight."""
        import re

        referenced = set()
        src_dir = os.path.join(Settings.BASE_DIR, "src")
        for root, _, files in os.walk(src_dir):
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                with open(os.path.join(root, filename), encoding="utf-8") as fh:
                    referenced |= set(re.findall(r"['\"]([a-z_]+\.ui)['\"]", fh.read()))

        on_disk = {f for f in os.listdir(Settings.UI_FORMS_DIR) if f.endswith(".ui")}
        assert on_disk - referenced == set(), \
            f"unused .ui files: {sorted(on_disk - referenced)}"


@pytest.mark.usefixtures("qapp")
class TestWindows:
    @pytest.mark.parametrize("window_name", [
        "MainWindow", "SupplierWindow", "CustomerWindow", "StaffWindow",
        "MedicineWindow", "InvoiceWindow", "StockWindow", "LogsWindow",
    ])
    def test_window_opens_cleanly(self, seeded, no_popups, window_name):
        import src.ui.windows as windows

        window = getattr(windows, window_name)(seeded)
        assert_no_errors(no_popups)
        window.close()

    def test_dashboard_shows_seeded_medicines(self, seeded, no_popups):
        from src.ui.windows import MainWindow

        window = MainWindow(seeded)
        assert_no_errors(no_popups)
        assert window.stock_medicine.rowCount() == 2
        window.close()

    def test_dashboard_expiry_row_aligns_with_its_headers(self, seeded, no_popups):
        """
        Every value must land under the right header.

        The expiry table declares 8 columns; a query returning fewer shifts
        every value one column to the left, which is how this went unnoticed.
        """
        from src.ui.windows import MainWindow
        from src.utils.constants import URGENT_EXPIRY_DAYS
        from tests.factories import add_medicine

        db = seeded.db_manager
        medicine_id = add_medicine(db, "Sắp hết hạn", quantity=42, expires_in_days=15,
                                   batch="LOT-EXP")

        window = MainWindow(seeded)
        assert_no_errors(no_popups)

        rows = [
            [window.outdate_medicine.item(r, c).text()
             for c in range(window.outdate_medicine.columnCount())]
            for r in range(window.outdate_medicine.rowCount())
        ]
        match = [row for row in rows if row[1] == "Sắp hết hạn"]
        assert match, f"expiring medicine not listed; got {rows}"

        row = match[0]
        assert row[0] == str(medicine_id)     # ID
        assert row[2] == "42"                 # Quantity
        assert row[3] == "Viên"               # Unit
        assert row[4] == "LOT-EXP"            # Batch No.
        assert "/" in row[5]                  # Expiry Date, formatted
        assert row[6] == "15"                 # Days Left
        assert row[7] == ('!' if 15 <= URGENT_EXPIRY_DAYS else '⚠')
        window.close()

    def test_dashboard_tables_never_exceed_their_columns(self, seeded, no_popups):
        """A row wider than the table would silently drop trailing values."""
        from src.ui.windows import MainWindow
        from tests.factories import add_invoice, add_medicine

        db = seeded.db_manager
        db.execute("SELECT customer_id FROM customer LIMIT 1")
        customer_id = db.fetchone()[0]
        db.execute("SELECT medicine_id FROM medicine LIMIT 1")
        add_invoice(db, customer_id, [(db.fetchone()[0], 1, 2000)])
        add_medicine(db, "Sắp hết hạn", expires_in_days=15, batch="LOT-EXP2")

        window = MainWindow(seeded)

        for table in (window.stock_medicine, window.outdate_medicine, window.invoice_daily):
            for row in range(table.rowCount()):
                filled = [c for c in range(table.columnCount()) if table.item(row, c)]
                assert filled, f"{table.objectName()} row {row} is empty"
                assert max(filled) < table.columnCount()

        window.close()

    def test_dashboard_lists_todays_invoice_with_customer_name(self, seeded, no_popups):
        from src.ui.windows import MainWindow
        from tests.factories import add_invoice

        db = seeded.db_manager
        db.execute("SELECT customer_id, customer_name FROM customer LIMIT 1")
        customer_id, customer_name = db.fetchone()
        db.execute("SELECT medicine_id FROM medicine LIMIT 1")
        add_invoice(db, customer_id, [(db.fetchone()[0], 2, 2000)])

        window = MainWindow(seeded)
        assert_no_errors(no_popups)

        assert window.invoice_daily.rowCount() == 1
        assert window.invoice_daily.item(0, 2).text() == customer_name
        window.close()

    def test_medicine_window_lists_seeded_rows(self, seeded, no_popups):
        from src.ui.windows import MedicineWindow

        window = MedicineWindow(seeded)
        assert_no_errors(no_popups)
        assert window.tableWidget.rowCount() == 2
        window.close()

    def test_medicine_window_lists_uncategorised_medicine(self, seeded, no_popups):
        """A medicine with no category must not be dropped from the listing."""
        from src.ui.windows import MedicineWindow
        from tests.factories import add_medicine

        add_medicine(seeded.db_manager, "Chưa phân loại", category_id=None,
                     batch="LOT-NC")

        window = MedicineWindow(seeded)
        assert_no_errors(no_popups)

        names = [window.tableWidget.item(row, 1).text()
                 for row in range(window.tableWidget.rowCount())]
        assert "Chưa phân loại" in names
        window.close()

    def test_medicine_search_filters_rows(self, seeded, no_popups):
        from src.ui.windows import MedicineWindow

        window = MedicineWindow(seeded)
        window.search_input.setText("Paracetamol")

        visible = [row for row in range(window.tableWidget.rowCount())
                   if not window.tableWidget.isRowHidden(row)]
        assert len(visible) == 1
        window.close()


@pytest.mark.usefixtures("qapp")
class TestDialogs:
    @pytest.mark.parametrize("dialog_name", [
        "LoginDialog", "RegisterDialog", "CreateInvoiceDialog",
        "CreateStockDialog", "MedicineAddDialog", "ReportDialog",
    ])
    def test_dialog_opens_cleanly(self, seeded, no_popups, dialog_name):
        import src.ui.dialogs as dialogs

        dialog = getattr(dialogs, dialog_name)(seeded)
        assert_no_errors(no_popups)
        dialog.close()

    def test_create_stock_offers_purchase_payment_terms(self, seeded, no_popups):
        from src.ui.dialogs import CreateStockDialog

        dialog = CreateStockDialog(seeded)
        assert_no_errors(no_popups)
        assert dialog.payment_term.count() > 0
        dialog.close()

    def test_create_invoice_offers_sale_payment_terms(self, seeded, no_popups):
        from src.ui.dialogs import CreateInvoiceDialog

        dialog = CreateInvoiceDialog(seeded)
        assert_no_errors(no_popups)
        assert dialog.payment_term.count() > 0
        dialog.close()

    def test_medicine_add_dialog_lists_categories(self, seeded, no_popups):
        from src.ui.dialogs import MedicineAddDialog

        dialog = MedicineAddDialog(seeded)
        assert_no_errors(no_popups)
        assert dialog.comboBox.count() > 0
        dialog.close()

    def test_report_dialog_enables_inputs_per_report_type(self, seeded, no_popups):
        from src.ui.dialogs import ReportDialog

        dialog = ReportDialog(seeded)

        dialog.radio_revenue.setChecked(True)
        assert dialog.date_from.isEnabled()

        dialog.radio_expiry.setChecked(True)
        assert dialog.expiry_days.isEnabled()
        assert not dialog.date_from.isEnabled()

        dialog.close()

    def test_stock_information_dialog_shows_receipt_lines(self, seeded, no_popups):
        from src.ui.dialogs import StockInformationDialog
        from tests.factories import add_stock_entry

        db = seeded.db_manager
        db.execute("SELECT supplier_id FROM supplier LIMIT 1")
        supplier_id = db.fetchone()[0]
        db.execute("SELECT medicine_id FROM medicine LIMIT 1")
        medicine_id = db.fetchone()[0]

        stock_id = add_stock_entry(db, supplier_id, [(medicine_id, 7, 1200)])

        dialog = StockInformationDialog(seeded, stock_id)
        assert_no_errors(no_popups)
        assert dialog.detail_table.rowCount() == 1
        dialog.close()

    def test_medicine_information_dialog_loads_record(self, seeded, no_popups):
        from src.ui.dialogs import MedicineInformationDialog

        db = seeded.db_manager
        db.execute("SELECT medicine_id FROM medicine ORDER BY medicine_id LIMIT 1")
        medicine_id = db.fetchone()[0]

        dialog = MedicineInformationDialog(seeded, medicine_id)
        assert_no_errors(no_popups)
        dialog.close()

    def test_invoice_information_dialog_loads_record(self, seeded, no_popups):
        from src.ui.dialogs import InvoiceInformationDialog
        from tests.factories import add_invoice

        db = seeded.db_manager
        db.execute("SELECT customer_id FROM customer LIMIT 1")
        customer_id = db.fetchone()[0]
        db.execute("SELECT medicine_id FROM medicine LIMIT 1")
        medicine_id = db.fetchone()[0]
        invoice_id, _ = add_invoice(db, customer_id, [(medicine_id, 2, 2000)])

        dialog = InvoiceInformationDialog(seeded, invoice_id)
        assert_no_errors(no_popups)
        dialog.close()
