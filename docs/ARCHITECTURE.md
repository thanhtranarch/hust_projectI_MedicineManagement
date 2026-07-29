# MediManager Architecture

## Overview

MediManager follows a layered (clean) architecture: the user interface, the
business services and the data access code are separated so each can change
without dragging the others along.

## Architecture Layers

```
┌──────────────────────────────────────────────────────┐
│  Presentation Layer — src/ui/                        │
│  windows/ · dialogs/ · forms/ (.ui) · base/          │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│  Service Layer — src/services/                       │
│  AuthService · ReportService                         │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│  Core Layer — src/core/                              │
│  AppContext · DBManager · schema · sql               │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│  Infrastructure — SQLite (data/medimanager.db)       │
└──────────────────────────────────────────────────────┘
```

Dependencies point downwards only. A window may call a service and the
database; a service never imports a window.

## Project Structure

```
hust_projectI_MedicineManagement/
│
├── run.py                          # Application entry point
├── seed_demo_data.py               # Demo data generator
├── requirements.txt                # Runtime dependencies
├── requirements-dev.txt            # Test/dev dependencies
├── pytest.ini                      # Test configuration
├── .env.example                    # Configuration template
│
├── src/
│   ├── config/
│   │   ├── settings.py             # Paths, app metadata, defaults
│   │   └── database.py             # Database file location
│   │
│   ├── core/
│   │   ├── app_context.py          # Connection + user session
│   │   ├── db_manager.py           # Query execution, transactions, migrations
│   │   ├── schema.py               # Schema definition (single source of truth)
│   │   └── sql.py                  # Reusable SQL fragments
│   │
│   ├── services/
│   │   ├── auth_service.py         # Login, registration, password hashing
│   │   └── report_service.py       # PDF report generation
│   │
│   ├── ui/
│   │   ├── base/                   # BaseWindow, BaseDialog
│   │   ├── windows/                # 8 main windows
│   │   ├── dialogs/                # 12 dialogs
│   │   └── forms/                  # Qt Designer .ui files
│   │
│   └── utils/
│       ├── helpers.py              # Formatting and validation
│       └── constants.py            # Shared constants and messages
│
├── tests/                          # 154 pytest cases
├── assets/                         # Icons and the report font
├── docs/ARCHITECTURE.md            # This file
├── data/                           # medimanager.db (created at runtime)
└── exports/                        # Generated PDFs (created at runtime)
```

## Module Descriptions

### Config (`src/config/`)

| File | Responsibility |
|------|----------------|
| `settings.py` | Application metadata, asset/form/export paths, default admin account |
| `database.py` | Where the SQLite file lives |

There is nothing to configure. `DatabaseConfig.SQLITE_PATH` defaults to
`data/medimanager.db` inside the project and can be pointed elsewhere with the
optional `SQLITE_PATH` environment variable.

### Core (`src/core/`)

| File | Responsibility |
|------|----------------|
| `schema.py` | Table DDL, indexes, migrations, reference data |
| `sql.py` | Reusable SQL fragments (date arithmetic) |
| `db_manager.py` | Connection lifecycle, query execution, transactions, schema setup |
| `app_context.py` | Holds the connection and the logged-in user, passed to every screen |

**`DBManager`** is the only place that talks to `sqlite3`. It:

- opens the database file, creating its directory if needed,
- creates tables and applies migrations on connect,
- translates `%s` placeholders to sqlite3's `?`,
- rolls back on a failed query.

**Transaction handling.** `execute()` rolls back before re-raising, so a failed
statement can never leave a half-open transaction that corrupts later work in
the same session. Multi-step business operations wrap all their statements in
one transaction and commit once at the end.

```python
def execute(self, query, params=None):
    try:
        self.cursor.execute(self._translate(query), params or ())
        return self.cursor
    except Exception as e:
        self.rollback()
        print(f"Query execution error: {e}")
        raise
```

### Services (`src/services/`)

| File | Responsibility |
|------|----------------|
| `auth_service.py` | Authentication, bcrypt hashing, legacy password upgrade, registration rules |
| `report_service.py` | Stock / revenue / invoice / expiry PDF reports |

Services take an `AppContext` and contain no Qt code, which is what makes them
testable without a running application.

### UI (`src/ui/`)

| Directory | Contents |
|-----------|----------|
| `base/` | `BaseWindow` and `BaseDialog`: `.ui` loading, window icon, message helpers |
| `windows/` | Dashboard, medicine, stock, invoice, customer, supplier, staff, logs |
| `dialogs/` | Login, register, create invoice, create stock, detail and report dialogs |
| `forms/` | Qt Designer `.ui` files, loaded at runtime by `uic.loadUi` |

Layout lives in the `.ui` files and behaviour lives in the Python classes, so
the interface can be edited in Qt Designer without touching code.

### Utils (`src/utils/`)

| File | Contents |
|------|----------|
| `helpers.py` | `format_currency`, `format_date`, `format_datetime`, `format_time`, `format_phone`, `validate_email`, `validate_phone`, `get_theme`, `resource_path` |
| `constants.py` | Positions, payment statuses, date formats, expiry thresholds, UI messages |

## SQL Conventions

All data lives in one SQLite file, so there is no dialect abstraction to
maintain. Two conventions keep the queries consistent:

**Placeholders.** Queries are written with `%s` and `DBManager._translate()`
rewrites them to sqlite3's `?`. Keeping one style across the codebase means a
query can be moved between modules without rewriting its parameters.

**Date arithmetic.** SQLite has no date subtraction operator, so "days until
this date" needs a `julianday()` expression that is too noisy to repeat. It
lives in `src/core/sql.py`:

```python
from src.core import sql

days_left = sql.days_until('expiration_date')
self.db.execute(f"""
    SELECT medicine_name, {days_left} AS days_left
    FROM medicine
    WHERE expiration_date IS NOT NULL
      AND {days_left} BETWEEN 0 AND {EXPIRY_WARNING_DAYS}
""")
```

Simple expressions such as `date(col)` are written inline — they are already
clear. Only these fragments are ever interpolated into a query string; user
data always travels as bound parameters.

## Schema Management

`src/core/schema.py` is the single source of truth - there is no separate
`.sql` file to keep in sync. It holds:

- `TABLES` — ordered `CREATE TABLE IF NOT EXISTS` statements
- `INDEXES` — index definitions
- `MIGRATIONS` — `(table, column, type)` triples for columns added after the
  first release
- `PAYMENT_METHODS`, `CATEGORIES` — reference data

### Why migrations are needed

Tables are created with `CREATE TABLE IF NOT EXISTS`, which does nothing when
the table already exists — including when it is missing a newly added column.
`_apply_migrations()` therefore checks the live column list on every startup and
issues `ALTER TABLE ... ADD COLUMN` for anything absent. Databases created by
earlier versions keep working and gain the new columns without losing data.

### Changing the schema

1. Add a table to `TABLES`, or a column to `MIGRATIONS`.
2. Run `pytest tests/test_database.py`.

## Data Model

```
   supplier ──┬──────────────► medicine ◄────────── category
              │                 │    ▲
              │                 │    │
              ▼                 │    │
   staff ──► stock ──► stock_detail  │
     │         ▲                     │
     │         │                     │
     │    payment_method             │
     │         │                     │
     ▼         ▼                     │
   invoice ────┴──► invoice_detail ──┘
     ▲
     │
  customer

   staff ──► activity_log
```

`stock` is the header of a goods-receipt document and `stock_detail` holds its
line items — the same header/detail shape as `invoice` and `invoice_detail`.

`payment_method.method_type` separates purchasing terms (`purchase`: COD,
prepayment) from point-of-sale tenders (`sale`: cash, bank transfer), so each
screen can query the set it needs instead of hard-coding row IDs.

## Data Flow

### Creating an invoice

```
CreateInvoiceDialog.save_invoice()      UI: gather cart, validate customer
        │
        ▼
DBManager.execute(INSERT INTO invoice)  one transaction
DBManager.last_insert_id()
        │
        ▼
for each line:
    INSERT INTO invoice_detail
    UPDATE medicine SET stock_quantity = stock_quantity - qty
        │
        ▼
DBManager.commit()                      invoice, lines and stock together
        │
        ▼
AppContext.log_action()                 audit trail
```

The invoice, its line items and the stock decrements share a single
transaction, so a failure part-way through cannot leave stock reduced for an
invoice that was never saved.

### Exporting a report

```
ReportDialog          picks report type and date range
        │
        ▼
ReportService         queries the database, builds the PDF
        │
        ▼
exports/*.pdf         written to disk, path returned
        │
        ▼
activity_log          the export is recorded
```

## Design Principles

**Separation of concerns.** UI holds no SQL beyond simple reads for its own
tables; authentication and reporting live in services; all driver-level work is
in `DBManager`.

**Single source of truth.** The schema is defined once. Payment methods and
categories are seeded from the same file that creates the tables.

**Fail visibly, recover cleanly.** Errors surface as dialogs rather than silent
no-ops, and a failed query rolls back instead of corrupting the session.

**Run anywhere.** No external service, no server, no credentials. The database
is one file the application creates itself, so the app, its tests and its demo
data all work offline on any machine.

## Security

**Passwords** are hashed with bcrypt and never stored in plain text. Accounts
that predate hashing are verified against their stored plain text once, then
transparently rewritten as a bcrypt hash.

**SQL injection** is prevented by parameterised queries throughout; only fixed
SQL fragments from `src/core/sql.py` are ever interpolated, never user input.

**The database file** holds all the data, so protecting it is a filesystem
concern: keep `data/` on a drive only the pharmacy's users can read, and treat
backups with the same care as the live file.

## Testing Strategy

154 tests run offline. Each one gets its own temporary database file.

| Suite | Scope |
|-------|-------|
| `test_database.py` | Schema creation, migrations, transactions, seed data, date expressions |
| `test_auth.py` | Login, rejection paths, legacy password upgrade, registration rules |
| `test_workflows.py` | Goods receipt, sales, stock movement, expiry window, revenue |
| `test_reports.py` | All four PDF reports, empty-database behaviour, formatting |
| `test_ui.py` | Every window and dialog constructed headless; table/header alignment |
| `test_helpers.py` | Formatting, validation, configuration |

**UI tests** run under Qt's offscreen platform against a real database. They
catch what unit tests cannot: a missing `.ui` file, a renamed widget, or a query
that no longer matches the schema.

## Performance Considerations

Indexes cover the columns the application filters and joins on: supplier and
category on `medicine`, expiration date for the warning query, customer/staff/date
on `invoice`, and the foreign keys of both detail tables.

One connection is reused for the lifetime of the application. SQLite reads are
local file reads, so list screens stay responsive without caching.

Reports stream row by row onto the PDF canvas and start a new page when the
current one fills, so a large export does not build the whole document in memory.

## Future Enhancements

- Role-based access control enforced per screen
- Charts on the dashboard
- Excel export alongside PDF
- In-app backup and restore of the database file
- Barcode scanner support
- Background threads for long-running queries

## Resources

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python sqlite3 module](https://docs.python.org/3/library/sqlite3.html)
- [pytest Documentation](https://docs.pytest.org/)

---

**Version**: 2.0.0
**Author**: Trần Tiến Thạnh
