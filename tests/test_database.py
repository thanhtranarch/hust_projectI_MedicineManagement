"""
Tests for the database layer: schema, migrations and transaction handling.
"""

import pytest

from src.core import schema
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

    def test_ddl_renders_for_every_backend(self):
        for backend in schema.DIALECTS:
            for name, ddl in schema.TABLES:
                rendered = schema.render(ddl, backend)
                assert '{' not in rendered, f"unfilled token in {name}/{backend}"

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
            manager = DBManager(backend='sqlite', database=path)
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

        manager = DBManager(backend='sqlite', database=path)
        manager.connect()
        manager.execute("ALTER TABLE stock DROP COLUMN note")
        manager.commit()
        assert 'note' not in manager._existing_columns('stock')
        manager.close()

        manager = DBManager(backend='sqlite', database=path)
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


class TestDialect:
    def test_placeholders_translated_for_sqlite(self, db):
        assert db._translate("SELECT %s") == "SELECT ?"

    def test_placeholders_untouched_for_postgres(self):
        manager = DBManager(backend='postgres')
        assert manager._translate("SELECT %s") == "SELECT %s"

    @pytest.mark.parametrize("backend", ["postgres", "sqlite"])
    def test_dialect_expressions_are_non_empty(self, backend):
        dialect = DBManager(backend=backend).sql
        assert dialect.today
        assert dialect.date_of('col')
        assert dialect.days_until('col')

    def test_days_until_computes_real_dates(self, db):
        from tests.factories import add_medicine

        add_medicine(db, "Sắp hết hạn", expires_in_days=10)
        db.execute(
            f"SELECT {db.sql.days_until('expiration_date')} FROM medicine "
            "WHERE medicine_name = %s",
            ("Sắp hết hạn",)
        )
        assert db.fetchone()[0] == 10


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
