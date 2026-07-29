"""
Tests for the database layer: schema, migrations and transaction handling.
"""

import pytest

from src.core import schema, sql
from src.core.db_manager import DBManager


EXPECTED_TABLES = {
    'staff', 'category', 'payment_method', 'supplier', 'customer',
    'medicine', 'stock', 'stock_detail', 'invoice', 'invoice_detail',
    'activity_log',
}


def table_names(db):
    db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return {row[0] for row in db.fetchall()}


class TestSchema:
    def test_all_tables_created(self, db):
        assert EXPECTED_TABLES <= table_names(db)

    def test_schema_definition_covers_expected_tables(self):
        assert {name for name, _ in schema.TABLES} == EXPECTED_TABLES

    def test_every_table_ddl_names_its_table(self):
        for name, ddl in schema.TABLES:
            assert f"CREATE TABLE IF NOT EXISTS {name}" in ddl

    def test_payment_methods_seeded_for_both_flows(self, db):
        db.execute("SELECT method_type, COUNT(*) FROM payment_method GROUP BY method_type")
        counts = dict(db.fetchall())
        assert counts.get('purchase', 0) >= 1
        assert counts.get('sale', 0) >= 1

    def test_categories_seeded(self, db):
        db.execute("SELECT COUNT(*) FROM category")
        assert db.fetchone()[0] == len(schema.CATEGORIES)

    def test_seed_data_is_not_duplicated_on_reconnect(self, tmp_path):
        path = str(tmp_path / "reconnect.db")

        counts = []
        for _ in range(2):
            manager = DBManager(database=path)
            manager.connect()
            manager.execute("SELECT COUNT(*) FROM category")
            counts.append(manager.fetchone()[0])
            manager.close()

        assert counts[0] == counts[1]

    def test_admin_account_created_once(self, db):
        db.execute("SELECT COUNT(*) FROM staff WHERE staff_id = 'admin'")
        assert db.fetchone()[0] == 1


class TestMigrations:
    def test_migration_adds_missing_column(self, tmp_path):
        """A database created without a newer column gains it on next connect."""
        path = str(tmp_path / "old.db")

        manager = DBManager(database=path)
        manager.connect()
        manager.execute("ALTER TABLE stock DROP COLUMN note")
        manager.commit()
        assert 'note' not in manager._existing_columns('stock')
        manager.close()

        manager = DBManager(database=path)
        manager.connect()
        assert 'note' in manager._existing_columns('stock')
        manager.close()

    def test_migrations_are_idempotent(self, db):
        before = db._existing_columns('stock')
        db._apply_migrations()
        assert db._existing_columns('stock') == before


class TestTransactions:
    def test_connection_usable_after_failed_query(self, db):
        """A bad query must not poison the session for every later query."""
        with pytest.raises(Exception):
            db.execute("SELECT * FROM table_that_does_not_exist")

        db.execute("SELECT COUNT(*) FROM staff")
        assert db.fetchone()[0] == 1

    def test_failed_query_discards_uncommitted_work(self, db):
        """
        execute() rolls back on error, so a multi-step operation cannot leave
        half its writes behind when a later step fails.

        This is what keeps an invoice from being saved when the stock update
        that follows it blows up.
        """
        db.execute(
            "INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)",
            ("Dở dang", "0900000001")
        )

        with pytest.raises(Exception):
            db.execute("INSERT INTO customer (nonexistent_column) VALUES (%s)", (1,))

        db.execute("SELECT COUNT(*) FROM customer WHERE customer_phone = %s", ("0900000001",))
        assert db.fetchone()[0] == 0, "the earlier insert should have been rolled back"

    def test_committed_work_survives_a_later_failure(self, db):
        """Rolling back on error must not undo anything already committed."""
        db.execute(
            "INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)",
            ("Đã lưu trước", "0900000002")
        )
        db.commit()

        with pytest.raises(Exception):
            db.execute("SELECT * FROM table_that_does_not_exist")

        db.execute("SELECT COUNT(*) FROM customer WHERE customer_phone = %s", ("0900000002",))
        assert db.fetchone()[0] == 1

    def test_rollback_discards_uncommitted_changes(self, db):
        db.execute(
            "INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)",
            ("Tạm thời", "0900000000")
        )
        db.rollback()

        db.execute("SELECT COUNT(*) FROM customer WHERE customer_phone = %s", ("0900000000",))
        assert db.fetchone()[0] == 0

    def test_commit_persists_changes(self, db):
        db.execute(
            "INSERT INTO customer (customer_name, customer_phone) VALUES (%s, %s)",
            ("Đã lưu", "0911111111")
        )
        db.commit()

        db.execute("SELECT customer_name FROM customer WHERE customer_phone = %s", ("0911111111",))
        assert db.fetchone()[0] == "Đã lưu"

    def test_last_insert_id_matches_inserted_row(self, db):
        db.execute("INSERT INTO supplier (supplier_name) VALUES (%s)", ("NCC Test",))
        supplier_id = db.last_insert_id()
        db.commit()

        db.execute("SELECT supplier_name FROM supplier WHERE supplier_id = %s", (supplier_id,))
        assert db.fetchone()[0] == "NCC Test"


class TestSqlFragments:
    def test_placeholders_translated_to_sqlite_style(self, db):
        assert db._translate("SELECT %s WHERE x = %s") == "SELECT ? WHERE x = ?"

    def test_today_matches_current_date(self, db):
        from datetime import date

        db.execute(f"SELECT {sql.TODAY}")
        assert db.fetchone()[0] == date.today().isoformat()

    @pytest.mark.parametrize("offset", [-30, 0, 10, 365])
    def test_days_until_computes_real_dates(self, db, offset):
        from tests.factories import add_medicine

        add_medicine(db, "Thuốc", expires_in_days=offset, batch=f"LOT{offset}")
        db.execute(
            f"SELECT {sql.days_until('expiration_date')} FROM medicine "
            "WHERE batch_number = %s",
            (f"LOT{offset}",)
        )
        assert db.fetchone()[0] == offset


class TestActivityLog:
    def test_log_action_records_entry(self, context):
        context.log_action("Kiểm thử ghi nhật ký")

        context.db_manager.execute(
            "SELECT action FROM activity_log WHERE staff_id = %s", ('admin',)
        )
        actions = [row[0] for row in context.db_manager.fetchall()]
        assert "Kiểm thử ghi nhật ký" in actions

    def test_log_action_ignored_when_not_logged_in(self, db):
        from src.core import AppContext

        # No staff_id set -> nothing should be written
        anonymous = AppContext.__new__(AppContext)
        anonymous.staff_id = None
        anonymous.db_manager = db
        anonymous.log_action("không nên ghi")

        db.execute("SELECT COUNT(*) FROM activity_log WHERE action = %s", ("không nên ghi",))
        assert db.fetchone()[0] == 0
