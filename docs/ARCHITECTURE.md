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
│  AppContext · DBManager · SqlDialect · schema        │
└───────────────────────┬──────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────┐
│  Infrastructure                                      │
│  SQLite  ·  PostgreSQL / Supabase                    │
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
├── supabase_schema.sql             # PostgreSQL schema (generated from schema.py)
├── requirements.txt                # Runtime dependencies
├── requirements-dev.txt            # Test/dev dependencies
├── pytest.ini                      # Test configuration
├── .env.example                    # Configuration template
│
├── src/
│   ├── config/
│   │   ├── settings.py             # Paths, app metadata, defaults
│   │   └── database.py             # Backend selection, connection params
│   │
│   ├── core/
│   │   ├── app_context.py          # Connection + user session
│   │   ├── db_manager.py           # Query execution, transactions, migrations
│   │   └── schema.py               # Schema definition (single source of truth)
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
├── tests/                          # 167 pytest cases
├── assets/                         # Icons and the report font
├── docs/ARCHITECTURE.md            # This file
├── data/                           # SQLite database (created at runtime)
└── exports/                        # Generated PDFs (created at runtime)
```

## Module Descriptions

### Config (`src/config/`)

| File | Responsibility |
|------|----------------|
| `settings.py` | Application metadata, asset/form/export paths, default admin account |
| `database.py` | Backend detection, connection parameters, configuration validation |

`DatabaseConfig.detect_backend()` decides which database to use:

1. An explicit `DB_BACKEND` wins (`sqlite` / `postgres`).
2. Otherwise PostgreSQL is used when `DB_HOST` **and** `DB_PASSWORD` are set.
3. Otherwise SQLite — so a fresh checkout runs with no configuration.

### Core (`src/core/`)

| File | Responsibility |
|------|----------------|
| `schema.py` | Table DDL, indexes, migrations, reference data |
| `db_manager.py` | Connection lifecycle, query execution, transactions, schema setup |
| `app_context.py` | Holds the connection and the logged-in user, passed to every screen |

**`DBManager`** is the only place that talks to a database driver. It:

- opens the connection for the selected backend,
- creates tables and applies migrations on connect,
- translates parameter placeholders between drivers,
- rolls back on a failed query,
- exposes `SqlDialect` for the handful of expressions that differ per backend.

**Transaction handling.** `execute()` rolls back before re-raising. This matters
on PostgreSQL: a failed statement aborts the surrounding transaction, and every
later statement fails with *"current transaction is aborted"* until a rollback
happens. Without the rollback a single bad query breaks every unrelated screen
for the rest of the session.

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

## Dual-Backend Support

Business code writes SQL once. `DBManager` absorbs the differences:

| Concern | PostgreSQL | SQLite |
|---------|-----------|--------|
| Placeholders | `%s` | `?` (translated automatically) |
| Auto-increment key | `SERIAL PRIMARY KEY` | `INTEGER PRIMARY KEY AUTOINCREMENT` |
| Last inserted id | `SELECT lastval()` | `cursor.lastrowid` |
| Today | `CURRENT_DATE` | `date('now','localtime')` |
| Truncate to date | `DATE(col)` | `date(col)` |
| Days until a date | `col::date - CURRENT_DATE` | `julianday(...) - julianday(...)` |

Anything beyond placeholders goes through `SqlDialect`, reached as `db.sql`:

```python
days_left = self.context.sql.days_until('expiration_date')
self.db.execute(f"""
    SELECT medicine_name, {days_left} AS days_left
    FROM medicine
    WHERE expiration_date IS NOT NULL
      AND {days_left} BETWEEN 0 AND {EXPIRY_WARNING_DAYS}
""")
```

Only dialect fragments are interpolated into the query string; user data always
travels as bound parameters.

## Schema Management

`src/core/schema.py` is the single source of truth. It holds:

- `TABLES` — ordered DDL templates with `{serial_pk}`, `{timestamp}`, `{now}`,
  `{money}` tokens filled per backend
- `INDEXES` — index definitions
- `MIGRATIONS` — `(table, column, type)` triples for columns added after the
  first release
- `PAYMENT_METHODS`, `CATEGORIES` — reference data

`supabase_schema.sql` is generated from this file for people who prefer to run
the DDL by hand in the Supabase SQL editor.

### Why migrations are needed

Tables are created with `CREATE TABLE IF NOT EXISTS`, which does nothing when
the table already exists — including when it is missing a newly added column.
`_apply_migrations()` therefore checks the live column list on every startup and
issues `ALTER TABLE ... ADD COLUMN` for anything absent. Databases created by
earlier versions keep working and gain the new columns without losing data.

### Changing the schema

1. Add a table to `TABLES`, or a column to `MIGRATIONS`.
2. Update `supabase_schema.sql` to match.
3. Run `pytest tests/test_database.py`.

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

**Run anywhere.** No mandatory external service. SQLite is the default so the
application, its tests and its demo data all work offline.

## Security

**Passwords** are hashed with bcrypt and never stored in plain text. Accounts
that predate hashing are verified against their stored plain text once, then
transparently rewritten as a bcrypt hash.

**SQL injection** is prevented by parameterised queries throughout; only
dialect fragments are ever interpolated into SQL, never user input.

**Credentials** are read from `.env`, which is git-ignored.

## Testing Strategy

167 tests run offline against a temporary SQLite database.

| Suite | Scope |
|-------|-------|
| `test_database.py` | Schema creation, migrations, transactions, seed data, dialect |
| `test_auth.py` | Login, rejection paths, legacy password upgrade, registration rules |
| `test_workflows.py` | Goods receipt, sales, stock movement, expiry window, revenue |
| `test_reports.py` | All four PDF reports, empty-database behaviour, formatting |
| `test_ui.py` | Every window and dialog constructed headless; table/header alignment |
| `test_helpers.py` | Formatting, validation, backend detection |
| `test_postgres.py` | PostgreSQL-only behaviour; skipped without `TEST_PG_HOST` |

**UI tests** run under Qt's offscreen platform against a real database. They
catch what unit tests cannot: a missing `.ui` file, a renamed widget, or a query
that no longer matches the schema.

**PostgreSQL tests** exist because transaction-abort semantics have no SQLite
equivalent. Verifying the rollback fix requires a real server, so those tests
skip unless `TEST_PG_HOST` is set:

```bash
TEST_PG_HOST=127.0.0.1 TEST_PG_NAME=medimanager_test \
TEST_PG_USER=postgres TEST_PG_PASSWORD=postgres pytest tests/test_postgres.py
```

## Performance Considerations

Indexes cover the columns the application filters and joins on: supplier and
category on `medicine`, expiration date for the warning query, customer/staff/date
on `invoice`, and the foreign keys of both detail tables.

One connection is reused for the lifetime of the application. Reports stream
row by row onto the PDF canvas and start a new page when the current one fills,
so a large export does not build the whole document in memory.

## Future Enhancements

- Role-based access control enforced per screen
- Charts on the dashboard
- Excel export alongside PDF
- Backup and restore
- Barcode scanner support
- Background threads for long-running queries

## Resources

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Supabase Documentation](https://supabase.com/docs)
- [pytest Documentation](https://docs.pytest.org/)

---

**Version**: 2.0.0
**Author**: Trần Tiến Thạnh
