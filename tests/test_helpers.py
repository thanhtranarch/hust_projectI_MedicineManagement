"""
Tests for utility helpers and configuration.
"""

import pytest

from src.config import DatabaseConfig, Settings
from src.utils.helpers import (
    format_currency, format_date, format_datetime, format_phone, format_time,
    get_theme, validate_email, validate_phone,
)


class TestFormatCurrency:
    @pytest.mark.parametrize("amount,expected", [
        (0, "0 ₫"),
        (1000, "1.000 ₫"),
        (1500000, "1.500.000 ₫"),
        (None, "0 ₫"),
    ])
    def test_formats_vietnamese_currency(self, amount, expected):
        assert format_currency(amount) == expected

    def test_accepts_float_input(self):
        assert format_currency(2500.75) == "2.500 ₫"


class TestFormatPhone:
    def test_groups_ten_digit_number(self):
        assert format_phone("0912345678") == "0912 345 678"

    def test_returns_input_when_not_ten_digits(self):
        assert format_phone("12345") == "12345"

    def test_empty_input(self):
        assert format_phone("") == ""
        assert format_phone(None) == ""


class TestValidateEmail:
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "thanh.tt239253@sis.hust.edu.vn",
        "a+b@domain.co.uk",
    ])
    def test_accepts_valid(self, email):
        assert validate_email(email)

    @pytest.mark.parametrize("email", [
        "", None, "no-at-sign", "@example.com", "user@", "user@domain",
    ])
    def test_rejects_invalid(self, email):
        assert not validate_email(email)


class TestValidatePhone:
    @pytest.mark.parametrize("phone", ["0912345678", "0987654321"])
    def test_accepts_valid(self, phone):
        assert validate_phone(phone)

    @pytest.mark.parametrize("phone", ["", None, "912345678", "091234567890", "1912345678"])
    def test_rejects_invalid(self, phone):
        assert not validate_phone(phone)


class TestFormatDate:
    def test_formats_datetime_as_day_first(self):
        from datetime import datetime
        assert format_date(datetime(2025, 3, 9, 14, 30)) == "09/03/2025"

    def test_formats_date(self):
        from datetime import date
        assert format_date(date(2025, 12, 31)) == "31/12/2025"

    def test_none_becomes_empty_string(self):
        assert format_date(None) == ""

    def test_string_passes_through(self):
        assert format_date("chưa rõ") == "chưa rõ"


class TestFormatDatetime:
    def test_includes_clock_time(self):
        from datetime import datetime
        assert format_datetime(datetime(2025, 3, 9, 14, 30, 5)) == "09/03/2025 14:30:05"

    def test_none_becomes_empty_string(self):
        assert format_datetime(None) == ""


class TestFormatTime:
    def test_returns_hours_and_minutes(self):
        from datetime import datetime
        assert format_time(datetime(2025, 3, 9, 8, 5)) == "08:05"

    def test_none_becomes_empty_string(self):
        assert format_time(None) == ""


class TestTheme:
    def test_returns_known_theme(self):
        assert get_theme() in ('dark', 'light')


class TestSettings:
    def test_icon_path_matches_a_real_asset(self):
        import os
        for theme in ('dark', 'light'):
            assert os.path.exists(Settings.get_icon_path(theme)), \
                f"missing icon asset for {theme} theme"

    def test_ui_form_lookup_resolves(self):
        import os
        assert os.path.exists(Settings.get_ui_file('login.ui'))

    def test_exports_dir_is_created(self, tmp_path, monkeypatch):
        target = str(tmp_path / "exports")
        monkeypatch.setattr(Settings, "EXPORTS_DIR", target)
        assert Settings.ensure_exports_dir() == target
        import os
        assert os.path.isdir(target)


class TestDatabaseConfig:
    def test_default_path_is_inside_the_project(self):
        assert DatabaseConfig.SQLITE_PATH.endswith('.db')

    def test_describe_names_the_database_file(self):
        description = DatabaseConfig.describe()
        assert 'SQLite' in description
        assert DatabaseConfig.SQLITE_PATH in description
