"""
Shared pytest fixtures.

Every test runs against a throwaway SQLite file, so the suite needs no setup
and never touches a real database.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import AppContext  # noqa: E402


@pytest.fixture
def context(tmp_path):
    """An AppContext backed by a fresh database file, torn down after the test."""
    ctx = AppContext(database=str(tmp_path / "test.db"))
    ctx.set_user('admin')
    yield ctx
    ctx.close()


@pytest.fixture
def db(context):
    """The DBManager of the test context."""
    return context.db_manager


@pytest.fixture
def seeded(context):
    """A context pre-loaded with a supplier, a customer and two medicines."""
    from tests.factories import seed_basic_data

    seed_basic_data(context.db_manager)
    return context
