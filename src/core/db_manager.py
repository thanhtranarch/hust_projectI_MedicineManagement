"""
Database manager - connection handling and query execution.

Supports two backends:
  * ``postgres`` - Supabase / any PostgreSQL server (production)
  * ``sqlite``   - a local file, needs no configuration (demo, offline, tests)

The backend is chosen automatically from the environment, so application code
never has to care which one is in use.
"""

import os
import sqlite3
import datetime

import bcrypt
from dotenv import load_dotenv

from src.config.database import DatabaseConfig
from src.config.settings import Settings
from src.core import schema

load_dotenv()

POSTGRES = 'postgres'
SQLITE = 'sqlite'


def _register_sqlite_converters():
    """Return TIMESTAMP/DATE columns as datetime objects, like psycopg2 does."""
    def parse_timestamp(raw):
        text = raw.decode()
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(text, fmt)
            except ValueError:
                continue
        return text

    def parse_date(raw):
        try:
            return datetime.date.fromisoformat(raw.decode())
        except ValueError:
            return raw.decode()

    sqlite3.register_converter("TIMESTAMP", parse_timestamp)
    sqlite3.register_converter("DATE", parse_date)
    sqlite3.register_adapter(datetime.date, lambda d: d.isoformat())
    sqlite3.register_adapter(datetime.datetime, lambda d: d.isoformat(sep=' '))


_register_sqlite_converters()


class SqlDialect:
    """SQL fragments that differ between backends."""

    def __init__(self, backend):
        self.backend = backend

    @property
    def today(self):
        """Expression for today's date."""
        return "CURRENT_DATE" if self.backend == POSTGRES else "date('now','localtime')"

    def date_of(self, column):
        """Truncate a timestamp column to a date."""
        return f"DATE({column})" if self.backend == POSTGRES else f"date({column})"

    def days_until(self, column):
        """Whole days from today until the given timestamp column."""
        if self.backend == POSTGRES:
            return f"({column}::date - CURRENT_DATE)"
        return (f"CAST(julianday(date({column})) - "
                f"julianday(date('now','localtime')) AS INTEGER)")


class DBManager:
    """Owns the database connection and executes queries against it."""

    def __init__(self, backend=None, database=None):
        """
        Args:
            backend: 'postgres', 'sqlite' or None to auto-detect.
            database: SQLite file path. Ignored by the postgres backend.
        """
        self.backend = backend or DatabaseConfig.detect_backend()
        self.database = database or DatabaseConfig.SQLITE_PATH
        self.sql = SqlDialect(self.backend)
        self.connection = None
        self.cursor = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def connect(self):
        """Open the connection and make sure the schema is present."""
        try:
            if self.backend == POSTGRES:
                import psycopg2
                self.connection = psycopg2.connect(**DatabaseConfig.get_connection_params())
            else:
                os.makedirs(os.path.dirname(os.path.abspath(self.database)), exist_ok=True)
                self.connection = sqlite3.connect(
                    self.database, detect_types=sqlite3.PARSE_DECLTYPES
                )
                self.connection.execute("PRAGMA foreign_keys = ON")

            self.cursor = self.connection.cursor()
            self.setup_database()
            return self.connection
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.connection = None
            self.cursor = None
            return None

    def close(self):
        """Close cursor and connection, ignoring an already-closed handle."""
        for handle in (self.cursor, self.connection):
            try:
                if handle is not None:
                    handle.close()
            except Exception:
                pass
        self.cursor = None
        self.connection = None

    # ------------------------------------------------------------------
    # Query execution
    # ------------------------------------------------------------------

    def _translate(self, query):
        """psycopg2 uses %s placeholders; sqlite3 uses ?."""
        return query if self.backend == POSTGRES else query.replace('%s', '?')

    def execute(self, query, params=None):
        """
        Run a query.

        On failure the transaction is rolled back before re-raising. Without
        this a single bad query leaves a PostgreSQL connection in an aborted
        state and every later query fails with "current transaction is
        aborted", turning one error into a broken session.
        """
        try:
            self.cursor.execute(self._translate(query), params or ())
            return self.cursor
        except Exception as e:
            self.rollback()
            print(f"Query execution error: {e}")
            raise

    def executemany(self, query, params_list):
        """Run a query once per parameter set."""
        try:
            self.cursor.executemany(self._translate(query), params_list)
            return self.cursor
        except Exception as e:
            self.rollback()
            print(f"Batch query execution error: {e}")
            raise

    def fetchall(self):
        """All rows from the last query."""
        return self.cursor.fetchall()

    def fetchone(self):
        """Next row from the last query."""
        return self.cursor.fetchone()

    def commit(self):
        """Commit the current transaction."""
        if self.connection:
            self.connection.commit()

    def rollback(self):
        """Roll back the current transaction."""
        if self.connection:
            try:
                self.connection.rollback()
            except Exception:
                pass

    def last_insert_id(self):
        """Primary key generated by the most recent INSERT."""
        if self.backend == POSTGRES:
            self.cursor.execute("SELECT lastval()")
            return self.cursor.fetchone()[0]
        return self.cursor.lastrowid

    # ------------------------------------------------------------------
    # Schema setup
    # ------------------------------------------------------------------

    def setup_database(self):
        """Create tables, apply migrations and seed reference data."""
        try:
            for _, ddl in schema.TABLES:
                self.cursor.execute(schema.render(ddl, self.backend))

            self._apply_migrations()

            for index_sql in schema.INDEXES:
                self.cursor.execute(index_sql)

            self._seed_reference_data()
            self._ensure_admin_account()

            self.connection.commit()
        except Exception as e:
            self.rollback()
            print(f"Error preparing database: {e}")
            raise

    def _existing_columns(self, table):
        """Column names currently present on a table."""
        if self.backend == POSTGRES:
            self.cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
                (table,)
            )
        else:
            self.cursor.execute(f"PRAGMA table_info({table})")
            return {row[1] for row in self.cursor.fetchall()}
        return {row[0] for row in self.cursor.fetchall()}

    def _apply_migrations(self):
        """Add columns introduced after a database was first created."""
        for table, column, coltype in schema.MIGRATIONS:
            if column in self._existing_columns(table):
                continue
            self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")

    def _seed_reference_data(self):
        """Insert lookup rows the UI needs, without duplicating them."""
        self.cursor.execute("SELECT COUNT(*) FROM payment_method")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                self._translate(
                    "INSERT INTO payment_method (payment_name, method_type, description) "
                    "VALUES (%s, %s, %s)"
                ),
                schema.PAYMENT_METHODS
            )

        self.cursor.execute("SELECT COUNT(*) FROM category")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                self._translate(
                    "INSERT INTO category (category_name, description) VALUES (%s, %s)"
                ),
                schema.CATEGORIES
            )

    def _ensure_admin_account(self):
        """Create the default admin login on a fresh database."""
        self.cursor.execute(
            self._translate("SELECT COUNT(*) FROM staff WHERE staff_id = %s"),
            (Settings.DEFAULT_ADMIN_USERNAME,)
        )
        if self.cursor.fetchone()[0]:
            return

        hashed = bcrypt.hashpw(
            Settings.DEFAULT_ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')
        self.cursor.execute(
            self._translate(
                "INSERT INTO staff (staff_id, staff_psw, staff_name, staff_position, "
                "staff_phone, staff_email) VALUES (%s, %s, %s, %s, %s, %s)"
            ),
            (Settings.DEFAULT_ADMIN_USERNAME, hashed, Settings.DEFAULT_ADMIN_NAME,
             'admin', Settings.DEFAULT_ADMIN_PHONE, Settings.DEFAULT_ADMIN_EMAIL)
        )
        print(f"Admin account created (username: {Settings.DEFAULT_ADMIN_USERNAME} / "
              f"password: {Settings.DEFAULT_ADMIN_PASSWORD})")

    # ------------------------------------------------------------------
    # Activity log
    # ------------------------------------------------------------------

    def log_action(self, staff_id, action):
        """Record a user action. Never raises - logging must not break a flow."""
        try:
            self.execute(
                "INSERT INTO activity_log (staff_id, action) VALUES (%s, %s)",
                (staff_id, action)
            )
            self.commit()
        except Exception as e:
            print(f"[LOG ERROR] {e}")
