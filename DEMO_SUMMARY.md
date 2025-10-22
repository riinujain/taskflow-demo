# TaskFlow Demo Codebase - Summary

## Overview

TaskFlow is a deliberately imperfect FastAPI-based task management SaaS application designed to showcase semantic search, complexity analysis, and refactoring capabilities.

## Statistics

- **Total Lines of Code**: ~9,648 LOC (including tests)
- **Python Files**: 45 files in `taskflow/` directory
- **Test Files**: 5 comprehensive test suites
- **Architecture**: Layered (API → Services → Models → Utils)

## Project Structure

```
taskflow/
├── api/                    # FastAPI route handlers (7 files, mixed sync/async)
│   ├── users_api.py       # Auth and user endpoints
│   ├── projects_api.py    # Project management
│   ├── tasks_api.py       # Task CRUD (mixed sync/async patterns)
│   ├── reports_api.py     # Report generation
│   ├── analytics_api.py   # Analytics and metrics
│   └── health_api.py      # Health checks
├── services/              # Business logic layer (11 files)
│   ├── auth_service.py    # JWT authentication
│   ├── user_service.py    # User management
│   ├── project_service.py # Project operations (with raw SQL)
│   ├── task_service.py    # Task operations
│   ├── notification_service.py  # DUPLICATE reminder functions
│   ├── report_service.py  # LONG conditional chains (>20 lines)
│   ├── analytics_service.py
│   ├── webhook_service.py
│   ├── comment_service.py
│   ├── export_service.py
│   ├── search_service.py
│   ├── batch_service.py
│   ├── cache_service.py
│   └── scheduler_service.py
├── models/                # SQLAlchemy ORM models (6 files)
│   ├── base.py           # Database setup
│   ├── user.py           # User model
│   ├── project.py        # Project model
│   ├── task.py           # Task model
│   └── repository.py     # Generic CRUD patterns
├── utils/                # Utility modules (11 files)
│   ├── config.py         # Settings (mixed camelCase)
│   ├── logger.py         # Multiple logging patterns
│   ├── helpers.py        # General helpers (duplicate date formatting)
│   ├── date_utils.py     # Date utilities (duplicate date formatting)
│   ├── email_client.py   # Simulated email sending
│   ├── validators.py     # Input validation
│   ├── formatters.py     # Output formatting
│   ├── text_processing.py
│   ├── security.py
│   ├── performance.py
│   └── data_processing.py
├── tests/                # Test suite (5 files)
│   ├── test_users.py     # User/auth tests (with REDUNDANT test)
│   ├── test_projects.py  # Project tests
│   ├── test_tasks.py     # Task tests
│   ├── test_reports.py   # Report tests (FRAGILE string-dependent tests)
│   └── test_analytics.py # Analytics tests
├── scripts/
│   └── seed_data.py      # Database seeding script
└── main.py               # FastAPI application entry point
```

## Deliberate Imperfections (As Specified)

### 1. ✅ Duplicate Reminder Functions
**Location**: `taskflow/services/notification_service.py`
- `send_task_reminder(task, user)` - Lines 27-66
- `remind_task_due(task_obj, user_obj, urgent=False)` - Lines 69-114

These are near-identical functions with slight variations in parameter names, date formatting, and email templates.

### 2. ✅ Long Conditional Chain
**Location**: `taskflow/services/report_service.py:76-172`

The `build_task_summary_string()` function contains 97 lines with deeply nested conditionals for:
- Priority formatting (4 branches)
- Status formatting (4 branches)
- Due date checks (4+ conditions)
- Assignment checks
- Comments count checks

### 3. ✅ Mixed Sync/Async Patterns
**Location**: `taskflow/api/tasks_api.py`
- `create_task()` - async endpoint with unnecessary `asyncio.to_thread()`
- `list_tasks()` - sync endpoint
- `get_task()` - async endpoint with unnecessary `asyncio.to_thread()`
- `update_task()` - sync endpoint
- `delete_task()` - async endpoint with unnecessary `asyncio.to_thread()`

Inconsistent use of sync vs async with pointless async wrappers.

### 4. ✅ Duplicate Date Formatting
**Scattered across**:
- `taskflow/utils/helpers.py`: `format_date()`, `format_date_simple()`, `format_datetime_readable()`
- `taskflow/utils/date_utils.py`: `format_datetime()`, `format_date_pretty()`, `format_time()`
- `taskflow/utils/formatters.py`: `format_datetime_string()`, `formatDateShort()`, `format_date_long()`

Multiple similar functions with slightly different outputs.

### 5. ✅ Raw SQL Query
**Location**: `taskflow/services/project_service.py:79-119`

The `get_project_stats()` method uses raw SQL with a TODO comment instead of SQLAlchemy ORM.

### 6. ✅ Inconsistent Naming
**Mixed snake_case and camelCase throughout**:
- `taskflow/utils/config.py`: `getSecretKey()`, `getDbUrl()`
- `taskflow/utils/helpers.py`: `filterNone()`, `validateEmail()`
- `taskflow/utils/formatters.py`: `formatProjectResponse()`, `formatPercentage()`
- `taskflow/utils/validators.py`: `validatePassword()`, `validateUrl()`
- And many more examples across the codebase

### 7. ✅ Circular Import Smell
**Location**: `taskflow/services/__init__.py`

Defines shared constants that are imported by both:
- `taskflow/services/task_service.py`
- `taskflow/services/report_service.py`

Creating a circular dependency pattern.

### 8. ✅ Missing Type Hints
**Throughout the codebase**:
- Functions with `# type: ignore` comments
- Methods missing return type annotations
- Parameters without type hints
- Mixed use of Optional vs explicit None checks

Examples in: `task_service.py:104`, `user_service.py:85`, `report_service.py`

### 9. ✅ Inconsistent Logging
**Multiple patterns used**:
- `taskflow/utils/logger.py`: `get_logger()` - recommended pattern
- `taskflow/utils/logger.py`: `setup_logger()` - alternative pattern
- `taskflow/services/user_service.py`: Direct `logging.getLogger(__name__)`
- `taskflow/services/task_service.py`: Using `log_info()`, `log_error()` helpers

Different modules use different approaches.

### 10. ✅ Redundant and Fragile Tests
**Redundant Test**: `tests/test_users.py:68-83`
- `test_get_current_user_with_token()` duplicates `test_get_current_user()`

**Fragile Tests**: `tests/test_reports.py:103-136`
- `test_get_task_verbose_summary_format()` - Lines 103-136
- `test_verbose_summary_priority_critical()` - Lines 139-161

Both depend on exact string formatting from `build_task_summary_string()` including:
- Exact emoji characters
- Exact spacing and formatting
- Specific line count expectations

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: SQLite with SQLAlchemy 2.0
- **Authentication**: JWT with PyJWT
- **Password Hashing**: bcrypt via passlib
- **Testing**: pytest with httpx
- **Code Quality**: ruff, black, mypy (configured but lenient)

## Running the Application

### Setup
```bash
# Install dependencies
pip install -e ".[dev]"

# Initialize database
make setup-db

# Seed with test data
make seed
```

### Development
```bash
# Run development server
make dev

# Run tests
make test

# Run linter
make lint

# Format code
make format
```

### API Access
- Base URL: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Sample Credentials (from seed data)
- **Email**: alice@example.com
- **Password**: password123

## Key Features Demonstrated

### 1. Authentication & Authorization
- User registration and login
- JWT token-based auth
- Protected endpoints

### 2. Resource Management
- Projects (CRUD operations)
- Tasks (CRUD with status tracking)
- User profiles

### 3. Analytics & Reporting
- Task completion rates
- Burndown charts
- Team metrics
- Project health scores
- Productivity reports

### 4. Advanced Features
- Search functionality
- Batch operations
- Data export (JSON, CSV, Markdown, HTML)
- Webhook simulation
- Performance monitoring
- Caching layer
- Background job scheduling

### 5. Testing
- Unit tests for all major endpoints
- Integration tests
- Test fixtures and factories
- Database isolation per test

## Code Complexity Examples

### High Cyclomatic Complexity
- `report_service.py:build_task_summary_string()` - Complexity > 15
- `batch_service.py:batch_update_tasks()` - Multiple error paths
- `analytics_service.py:calculate_task_completion_rate()` - Complex filtering

### Long Parameter Lists
- `search_service.py:advanced_search()` - 12 parameters
- `notification_service.py:send_daily_summary()` - 4 list parameters
- `report_service.py:build_task_summary_string()` - 7 boolean flags

### Deep Nesting
- `report_service.py:build_task_summary_string()` - 4-5 levels deep
- `batch_service.py:batch_delete_tasks()` - Nested loops and conditions

## Use Cases for Demo

This codebase is perfect for demonstrating:

1. **Semantic Code Search**
   - Finding duplicate logic (reminder functions)
   - Locating similar date formatting functions
   - Identifying inconsistent naming patterns

2. **Complexity Analysis**
   - Detecting long functions
   - Finding high cyclomatic complexity
   - Identifying code smells

3. **Refactoring Opportunities**
   - Consolidating duplicate functions
   - Breaking up long conditionals
   - Standardizing naming conventions
   - Converting raw SQL to ORM
   - Making async/sync patterns consistent

4. **Type Checking**
   - Adding missing type hints
   - Removing `# type: ignore` comments
   - Improving type safety

5. **Code Quality**
   - Fixing circular dependencies
   - Standardizing logging patterns
   - Improving test robustness

## Known Limitations (Intentional)

- No actual email sending (simulated)
- In-memory cache (would use Redis in production)
- Simplified scheduler (would use Celery)
- No database migrations (would use Alembic)
- Simplified authentication (no OAuth, refresh tokens)
- No rate limiting implementation (stubbed)
- No real encryption (demo XOR cipher only)

## License

MIT - For demonstration purposes only
