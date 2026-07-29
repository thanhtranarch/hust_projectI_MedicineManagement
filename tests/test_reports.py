"""
Tests for PDF report generation.
"""

import os
from datetime import datetime, timedelta

import pytest

from src.services import ReportService
from src.services.report_service import _money, _text
from tests.factories import add_invoice, add_medicine


@pytest.fixture
def reports(seeded, tmp_path, monkeypatch):
    """A ReportService writing into a temporary exports directory."""
    from src.config import Settings
    monkeypatch.setattr(Settings, "EXPORTS_DIR", str(tmp_path / "exports"))
    return ReportService(seeded)


def assert_is_pdf(filepath):
    assert os.path.exists(filepath), f"report not written: {filepath}"
    assert os.path.getsize(filepath) > 0
    with open(filepath, 'rb') as fh:
        assert fh.read(4) == b'%PDF'


class TestReportGeneration:
    def test_stock_report(self, reports):
        assert_is_pdf(reports.export_stock_report())

    def test_expiry_report(self, reports):
        assert_is_pdf(reports.export_expiry_warning_report())

    def test_invoice_report(self, reports):
        assert_is_pdf(reports.export_invoice_report(datetime.now().strftime("%Y-%m-%d")))

    def test_invoice_report_defaults_to_today(self, reports):
        assert_is_pdf(reports.export_invoice_report())

    def test_revenue_report(self, reports):
        assert_is_pdf(reports.export_revenue_report())

    def test_revenue_report_for_explicit_range(self, reports):
        start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end = datetime.now().strftime("%Y-%m-%d")
        assert_is_pdf(reports.export_revenue_report(start, end))

    def test_reports_work_with_data_present(self, reports, seeded):
        db = seeded.db_manager
        db.execute("SELECT customer_id FROM customer LIMIT 1")
        customer_id = db.fetchone()[0]
        db.execute("SELECT medicine_id FROM medicine LIMIT 1")
        medicine_id = db.fetchone()[0]

        add_invoice(db, customer_id, [(medicine_id, 3, 2000)])
        add_medicine(db, "Sắp hết hạn", expires_in_days=15, batch="LOT-EXP")

        assert_is_pdf(reports.export_stock_report())
        assert_is_pdf(reports.export_revenue_report())
        assert_is_pdf(reports.export_expiry_warning_report())

    def test_reports_work_on_empty_database(self, context, tmp_path, monkeypatch):
        """No rows must still yield a valid PDF, not a crash."""
        from src.config import Settings
        monkeypatch.setattr(Settings, "EXPORTS_DIR", str(tmp_path / "exports"))
        service = ReportService(context)

        assert_is_pdf(service.export_stock_report())
        assert_is_pdf(service.export_revenue_report())
        assert_is_pdf(service.export_expiry_warning_report())
        assert_is_pdf(service.export_invoice_report())

    def test_export_is_recorded_in_activity_log(self, reports, seeded):
        reports.export_stock_report()

        db = seeded.db_manager
        db.execute("SELECT action FROM activity_log WHERE staff_id = 'admin'")
        actions = [row[0] for row in db.fetchall()]
        assert any("tồn kho" in action for action in actions)


class TestFormatting:
    @pytest.mark.parametrize("value,expected", [
        (0, "0"),
        (1000, "1.000"),
        (1234567, "1.234.567"),
        (None, "0"),
        (2500.6, "2.501"),
    ])
    def test_money_formatting(self, value, expected):
        """Vietnamese convention: dot separates thousands."""
        assert _money(value) == expected

    def test_money_matches_ui_currency_formatting(self):
        """Reports and on-screen tables must not disagree on number format."""
        from src.utils.helpers import format_currency
        assert format_currency(1234567).startswith(_money(1234567))

    def test_money_handles_non_numeric(self):
        assert _money("abc") == "abc"

    def test_text_renders_none_as_empty(self):
        assert _text(None) == ""

    def test_text_formats_datetime(self):
        assert _text(datetime(2025, 3, 9)) == "09/03/2025"

    def test_text_passes_through_strings(self):
        assert _text("Paracetamol") == "Paracetamol"


class TestFontFallback:
    def test_font_resolves_to_a_usable_name(self):
        from src.services.report_service import _font
        assert _font() in ("ReportFont", "Helvetica")

    def test_bundled_font_is_present(self):
        from src.config import Settings
        assert os.path.exists(os.path.join(Settings.FONTS_DIR, "arial.ttf")), \
            "the bundled Unicode font is required for Vietnamese report text"
