"""
PostgreSQL-specific tests.

Skipped unless TEST_PG_HOST points at a scratch PostgreSQL database:

    TEST_PG_HOST=127.0.0.1 TEST_PG_PORT=5432 TEST_PG_NAME=medimanager_test \\
    TEST_PG_USER=postgres TEST_PG_PASSWORD=postgres pytest tests/test_postgres.py

These cover behaviour SQLite cannot reproduce, so they are the only place the
PostgreSQL transaction semantics are actually verified.
"""

import pytest


class TestTransactionAbort:
    def test_connection_recovers_after_failed_query(self, pg_db):
        """
        PostgreSQL aborts the whole transaction on a failed statement, and
        every later query fails with "current transaction is aborted" until a
        rollback. DBManager.execute must roll back so one bad query cannot
        break the rest of the session.
        """
        with pytest.raises(Exception):
            pg_db.execute("SELECT * FROM table_that_does_not_exist")

        pg_db.execute("SELECT COUNT(*) FROM staff")
        assert pg_db.fetchone()[0] >= 1

    def test_many_failures_do_not_break_the_session(self, pg_db):
        for _ in range(3):
            with pytest.raises(Exception):
                pg_db.execute("SELECT nope FROM medicine")

            pg_db.execute("SELECT COUNT(*) FROM medicine")
            assert pg_db.fetchone()[0] >= 0

    def test_write_still_works_after_failed_query(self, pg_db):
        with pytest.raises(Exception):
            pg_db.execute("INSERT INTO nonexistent_table VALUES (1)")

        pg_db.execute(
            "INSERT INTO supplier (supplier_name) VALUES (%s)", ("NCC sau lỗi",)
        )
        supplier_id = pg_db.last_insert_id()
        pg_db.commit()

        pg_db.execute(
            "SELECT supplier_name FROM supplier WHERE supplier_id = %s", (supplier_id,)
        )
        assert pg_db.fetchone()[0] == "NCC sau lỗi"


class TestPostgresSchema:
    def test_all_tables_present(self, pg_db):
        from tests.test_database import EXPECTED_TABLES

        pg_db.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        assert EXPECTED_TABLES <= {row[0] for row in pg_db.fetchall()}

    def test_reference_data_seeded(self, pg_db):
        pg_db.execute("SELECT COUNT(*) FROM payment_method WHERE method_type = 'sale'")
        assert pg_db.fetchone()[0] >= 1

        pg_db.execute("SELECT COUNT(*) FROM category")
        assert pg_db.fetchone()[0] >= 1

    def test_migrations_added_late_columns(self, pg_db):
        assert {'staff_id', 'payment_method_id', 'note'} <= pg_db._existing_columns('stock')
        assert 'payment_method_id' in pg_db._existing_columns('invoice')


class TestPostgresDialect:
    def test_placeholders_are_not_rewritten(self, pg_db):
        assert pg_db._translate("SELECT %s") == "SELECT %s"

    def test_last_insert_id_uses_lastval(self, pg_db):
        pg_db.execute("INSERT INTO customer (customer_name) VALUES (%s)", ("KH test",))
        customer_id = pg_db.last_insert_id()
        pg_db.commit()

        pg_db.execute(
            "SELECT customer_name FROM customer WHERE customer_id = %s", (customer_id,)
        )
        assert pg_db.fetchone()[0] == "KH test"

    def test_days_until_computes_real_dates(self, pg_db):
        from datetime import datetime, timedelta

        expiry = (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d")
        pg_db.execute(
            "INSERT INTO medicine (medicine_name, expiration_date) VALUES (%s, %s)",
            ("Thuốc kiểm thử hạn", expiry)
        )
        medicine_id = pg_db.last_insert_id()
        pg_db.commit()

        pg_db.execute(
            f"SELECT {pg_db.sql.days_until('expiration_date')} FROM medicine "
            "WHERE medicine_id = %s",
            (medicine_id,)
        )
        assert pg_db.fetchone()[0] == 12

    def test_today_expression_matches_current_date(self, pg_db):
        pg_db.execute(f"SELECT {pg_db.sql.today}")
        from datetime import date
        assert pg_db.fetchone()[0] == date.today()
