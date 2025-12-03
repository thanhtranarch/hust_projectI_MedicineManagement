# MediManager Architecture Documentation

## Overview

MediManager v2.0 follows a **clean architecture** pattern with clear separation of concerns. The application is organized into layers that promote maintainability, testability, and scalability.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│        (UI Windows & Dialogs)           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Application Layer              │
│      (Services & Business Logic)        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│            Core Layer                   │
│    (Database & Domain Logic)            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Infrastructure                  │
│    (Supabase PostgreSQL Cloud)          │
└─────────────────────────────────────────┘
```

## Project Structure

```
MediManager/
│
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git ignore rules
│
├── src/                            # Source code
│   ├── __init__.py
│   │
│   ├── config/                     # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py             # Application settings
│   │   └── database.py             # Database configuration
│   │
│   ├── core/                       # Core business logic
│   │   ├── __init__.py
│   │   ├── db_manager.py           # Database manager (DAO pattern)
│   │   └── app_context.py          # Application context & session
│   │
│   ├── services/                   # Business services
│   │   ├── __init__.py
│   │   └── report_service.py       # PDF report generation
│   │
│   ├── ui/                         # User interface layer
│   │   ├── __init__.py
│   │   ├── windows/                # Main application windows
│   │   │   └── __init__.py
│   │   ├── dialogs/                # Dialog windows
│   │   │   └── __init__.py
│   │   └── forms/                  # Qt Designer .ui files
│   │       └── __init__.py
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── helpers.py              # Helper functions
│       └── constants.py            # Application constants
│
├── assets/                         # Static resources
│   ├── icons/                      # Application icons
│   └── fonts/                      # Fonts for PDF generation
│
├── exports/                        # Generated reports
│
├── docs/                           # Documentation
│   └── ARCHITECTURE.md             # This file
│
├── MediManager.py                  # Legacy monolithic file (to be refactored)
├── DBManager.py                    # Legacy database file (deprecated)
└── export_reports.py               # Legacy reports (deprecated)
```

## Module Descriptions

### 1. Config Module (`src/config/`)

**Purpose**: Centralized configuration management

**Files**:
- `settings.py`: Application-wide settings (paths, UI settings, defaults)
- `database.py`: Database connection parameters

**Key Features**:
- Environment-based configuration
- Validation of required settings
- Path management for assets and exports

### 2. Core Module (`src/core/`)

**Purpose**: Core business logic and database access

**Files**:
- `db_manager.py`: Database operations (CRUD, queries)
- `app_context.py`: Application context and user session management

**Design Patterns**:
- **DAO (Data Access Object)**: `DBManager` abstracts database operations
- **Singleton**: Single database connection per application instance
- **Context Pattern**: `AppContext` manages application state

### 3. Services Module (`src/services/`)

**Purpose**: Business logic services

**Files**:
- `report_service.py`: PDF report generation

**Future Services**:
- `auth_service.py`: Authentication and authorization
- `medicine_service.py`: Medicine-specific business logic
- `invoice_service.py`: Invoice processing

### 4. UI Module (`src/ui/`)

**Purpose**: User interface layer

**Structure**:
- `windows/`: Main application windows
- `dialogs/`: Modal dialogs
- `forms/`: Qt Designer .ui files

**Design Pattern**:
- **MVC (Model-View-Controller)**: Separation of UI from business logic
- Forms (.ui files) = View
- Window classes = Controller
- Database/Services = Model

### 5. Utils Module (`src/utils/`)

**Purpose**: Shared utility functions

**Files**:
- `helpers.py`: Common helper functions
- `constants.py`: Application-wide constants

**Functions**:
- Resource path resolution
- Theme detection
- Data formatting (currency, phone, dates)
- Validation functions

## Data Flow

### Example: Creating an Invoice

```
1. User Input (UI Layer)
   ↓
   InvoiceWindow.create_invoice()
   ↓
2. Service Layer
   ↓
   InvoiceService.create_invoice()
   ↓
3. Data Access Layer
   ↓
   DBManager.execute("INSERT INTO invoice ...")
   ↓
4. Database (Supabase)
   ↓
   PostgreSQL executes query
   ↓
5. Response flows back up the layers
```

## Design Principles

### 1. Separation of Concerns
- UI logic separate from business logic
- Business logic separate from data access
- Configuration separate from code

### 2. Single Responsibility
- Each module has one primary responsibility
- Each class has one reason to change

### 3. Dependency Inversion
- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces/base classes)

### 4. DRY (Don't Repeat Yourself)
- Common functionality extracted to utils
- Shared configuration in config module
- Reusable services

## Configuration Management

### Environment Variables

The application uses environment variables for sensitive configuration:

```env
# .env file
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGc...
DB_HOST=db.xxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
```

### Settings Hierarchy

1. **Environment Variables** (.env file) - Highest priority
2. **Default Values** (in code) - Fallback

## Database Architecture

### Connection Management

- **Driver**: psycopg2 (PostgreSQL)
- **Connection**: Single connection per application instance
- **Connection Pooling**: Managed by Supabase
- **Transactions**: Auto-commit for simple operations, explicit for complex

### Schema

See `supabase_schema.sql` for complete database schema.

**Main Tables**:
- `staff` - User accounts and authentication
- `medicine` - Medicine inventory
- `supplier` - Supplier information
- `customer` - Customer records
- `invoice` - Sales invoices
- `invoice_detail` - Invoice line items
- `stock` - Stock transactions
- `activity_log` - Audit trail

## Security

### 1. Authentication
- Passwords hashed with bcrypt
- No plain-text passwords stored

### 2. Database Security
- Supabase SSL/TLS encryption
- Environment variables for credentials
- .env file in .gitignore (never committed)

### 3. SQL Injection Prevention
- Parameterized queries
- No string concatenation for SQL

## Error Handling

### Layers

1. **UI Layer**: User-friendly error messages
2. **Service Layer**: Business logic validation
3. **Data Layer**: Database constraint validation

### Strategy

```python
try:
    # Attempt operation
    db.execute(query, params)
    db.commit()
except psycopg2.Error as e:
    db.rollback()
    # Log error
    # Return user-friendly message
```

## Testing Strategy (Future)

### Unit Tests
- Test individual functions in utils
- Test service methods
- Test database operations (with mock DB)

### Integration Tests
- Test service + database integration
- Test UI + service integration

### End-to-End Tests
- Test complete user workflows

## Migration from Legacy Code

### Current Status (v2.0)

✅ **Completed**:
- New project structure created
- Config management implemented
- Core modules separated
- Database migrated to Supabase

⏳ **In Progress**:
- Refactoring MediManager.py into new structure
- Creating separate window/dialog classes
- Implementing service layer

🔜 **Planned**:
- Complete UI refactor
- Add unit tests
- Implement authentication service
- Add API layer (for future mobile app)

### Migration Steps

1. **Phase 1**: Infrastructure (✅ Completed)
   - Set up new structure
   - Migrate to Supabase
   - Create config management

2. **Phase 2**: Core Logic (In Progress)
   - Extract services from MediManager.py
   - Separate UI classes
   - Implement business logic layer

3. **Phase 3**: Polish
   - Add tests
   - Improve error handling
   - Performance optimization

## Performance Considerations

### Database
- Indexes on frequently queried columns
- Connection reuse
- Query optimization

### UI
- Lazy loading of data
- Pagination for large datasets
- Background threads for long operations

## Future Enhancements

### Planned Features
1. **REST API** for mobile app integration
2. **Advanced Reporting** with charts and analytics
3. **Multi-user Support** with role-based access control
4. **Cloud Sync** for offline-first capability
5. **Notifications** for expiring medicines, low stock
6. **Barcode Scanning** for medicines
7. **Integration** with accounting systems

### Technical Improvements
1. **Async Database Operations** for better performance
2. **Caching Layer** (Redis) for frequently accessed data
3. **Message Queue** for background jobs
4. **Microservices** architecture for scalability

## Resources

### Documentation
- [Supabase Docs](https://supabase.com/docs)
- [PyQt6 Docs](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

### Code Style
- PEP 8 for Python code
- Type hints for better IDE support
- Docstrings for all public functions

---

**Version**: 2.0.0
**Last Updated**: December 2025
**Author**: Trần Tiến Thạnh
