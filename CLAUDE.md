# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TaskFlow is a deliberately imperfect FastAPI-based task management SaaS demo designed to showcase code analysis, semantic search, and refactoring capabilities. The codebase intentionally contains anti-patterns and inconsistencies for demonstration purposes.

## Common Development Commands

### Setup and Database
```bash
# Install dependencies (use pip or uv)
pip install -e ".[dev]"
# OR
uv pip install -e ".[dev]"

# Initialize database (creates tables)
make setup-db

# Seed database with sample data
make seed
```

### Running the Application
```bash
# Run development server (with hot reload)
make dev
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Testing and Quality
```bash
# Run all tests
make test

# Run a specific test file
pytest tests/test_users.py -v

# Run a specific test function
pytest tests/test_users.py::test_register_user -v

# Lint code (ruff + mypy)
make lint

# Format code (black + ruff autofix)
make format

# Clean build artifacts and database
make clean
```

## High-Level Architecture

TaskFlow follows a layered architecture pattern with deliberate inconsistencies:

### Layer Structure
1. **API Layer** (`taskflow/api/`) - FastAPI route handlers with mixed sync/async patterns
2. **Service Layer** (`taskflow/services/`) - Business logic with some circular dependencies
3. **Repository Layer** (`taskflow/models/repository.py`) - Generic repository pattern (though some services bypass it)
4. **Model Layer** (`taskflow/models/`) - SQLAlchemy ORM models
5. **Utils Layer** (`taskflow/utils/`) - Shared utilities with inconsistent naming conventions

### Key Architectural Patterns

**Repository Pattern**: Generic `Repository[T]` class provides CRUD operations for all models. Specific repositories (`UserRepository`, `ProjectRepository`, `TaskRepository`) extend with custom queries. However, some services (notably `project_service.py`) bypass the repository and use raw SQL for "temporary" reasons.

**Database Session Management**: Two approaches exist:
- `get_db()` - Context manager for manual session handling
- `get_db_session()` - FastAPI dependency injection pattern
Both create sessions from `SessionLocal`, commit on success, and rollback on failure.

**Authentication Flow**:
- JWT tokens created via `AuthService.create_access_token()`
- Token validation through `AuthService.decode_token()` and `get_current_user()`
- Password hashing uses bcrypt via passlib
- Note: Inconsistent logging patterns between `get_logger()` and `setup_logger()`

**Service Dependencies**: Services instantiate with a database session and create their own repository instances. Some services have circular imports (e.g., `report_service.py` and `task_service.py` share constants).

### Database and Models

**Database**: SQLite with SQLAlchemy 2.0 ORM. All models inherit from `Base` (DeclarativeBase).

**Core Models**:
- `User` - Authentication and user management
- `Project` - Projects owned by users
- `Task` - Tasks within projects with assignees, due dates, priorities

**Relationships**: Projects belong to owners (users), tasks belong to projects and can be assigned to users.

### Configuration and Settings

Configuration managed through `taskflow/utils/config.py` using Pydantic settings. Key settings include:
- `DATABASE_URL` - SQLite database location
- `SECRET_KEY` - JWT signing (note: uses both `settings.SECRET_KEY` and `getSecretKey()` function)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration
- `DEBUG` - Debug mode flag

### Testing Infrastructure

Tests use pytest with FastAPI TestClient. Key fixtures:
- `test_db` - Creates isolated test database per test
- `client` - FastAPI test client with overridden DB dependency
- `sample_user` - Pre-created test user
- `auth_headers` - Authorization headers for authenticated requests

Tests are located in `tests/` and mirror the module structure. Note: Some tests have fragile string assertions.

## Intentional Code Quirks

This codebase contains deliberate imperfections (see README.md "Known Quirks" section):
- Duplicate date formatting functions across `utils/helpers.py` and `utils/date_utils.py`
- Near-duplicate notification functions in `notification_service.py`
- Long conditional chains in `report_service.py`
- Mixed sync/async patterns with unnecessary `asyncio.to_thread()` calls
- Raw SQL in `project_service.py` instead of repository pattern
- Inconsistent naming (snake_case vs camelCase)
- Circular import between `report_service.py` and `task_service.py`
- Multiple logging initialization patterns

When working with this codebase, be aware these are intentional for demonstration purposes.

## Important Development Notes

- Python 3.11+ required
- Database automatically initialized via lifespan event in `taskflow/main.py`
- All API routes aggregated in `taskflow/api/__init__.py` via `api_router`
- CORS configured to allow all origins (line 46 in `main.py` - production would restrict)
- Logging inconsistency: some modules use `get_logger()`, others use `setup_logger()`
