"""
Shared pytest fixtures.

Tests run against a throwaway SQLite database so the suite needs no server
and never touches a real deployment.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import AppContext  # noqa: E402


@pytest.fixture
def context(tmp_path):
    """An AppContext backed by a fresh SQLite file, torn down after the test."""
    ctx = AppContext(backend='sqlite', database=str(tmp_path / "test.db"))
    ctx.set_user('admin')
    yield ctx
    ctx.close()


@pytest.fixture
def db(context):
    """The DBManager of the test context."""
    return context.db_manager


@pytest.fixture
def seeded(context):
    """A context pre-loaded with a supplier, a category and two medicines."""
    from tests.factories import seed_basic_data

    seed_basic_data(context.db_manager)
    return context


@pytest.fixture
def pg_db():
    """
    A DBManager on a real PostgreSQL server.

    Skipped unless TEST_PG_HOST is set. Some behaviour - notably a failed
    statement aborting the whole transaction - only exists on PostgreSQL and
    cannot be reproduced on SQLite, so those tests need a real server.

    Point it at a scratch database; the tables are created on connect.
    """
    if not os.getenv('TEST_PG_HOST'):
        pytest.skip("set TEST_PG_HOST (and TEST_PG_* ) to run PostgreSQL tests")

    pytest.importorskip("psycopg2", reason="psycopg2 is required for PostgreSQL tests")

    from src.config import DatabaseConfig
    from src.core.db_manager import DBManager

    overrides = {
        'DB_HOST': os.getenv('TEST_PG_HOST'),
        'DB_PORT': int(os.getenv('TEST_PG_PORT', 5432)),
        'DB_NAME': os.getenv('TEST_PG_NAME', 'postgres'),
        'DB_USER': os.getenv('TEST_PG_USER', 'postgres'),
        'DB_PASSWORD': os.getenv('TEST_PG_PASSWORD', 'postgres'),
    }
    saved = {key: getattr(DatabaseConfig, key) for key in overrides}
    for key, value in overrides.items():
        setattr(DatabaseConfig, key, value)

    manager = DBManager(backend='postgres')
    try:
        if manager.connect() is None:
            pytest.skip(f"cannot reach PostgreSQL at {overrides['DB_HOST']}")
        yield manager
    finally:
        manager.close()
        for key, value in saved.items():
            setattr(DatabaseConfig, key, value)
