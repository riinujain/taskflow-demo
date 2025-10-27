# TaskFlow

A deliberately imperfect FastAPI-based task management SaaS demo for showcasing semantic search, complexity analysis, and refactoring capabilities.

**Note:** This codebase intentionally contains anti-patterns and code smells for demonstration purposes. See [Known Quirks](#known-quirks) below.

## Features

- User authentication with JWT
- Project and task management
- Automated notifications and reminders
- Daily reports and summaries
- RESTful API with OpenAPI documentation

## Setup

### Requirements

- Python 3.11+
- pip, uv, or your preferred package manager

### Installation

1. Clone the repository and navigate to the directory:
```bash
cd CM_Demo
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
# Using pip
pip install -e ".[dev]"

# Or using uv (faster)
uv pip install -e ".[dev]"

# Or using make
make install
```

### Initialize Database

```bash
# Create database tables
make setup-db

# Seed with sample data (3 users, 3 projects, 20 tasks)
make seed
```

### Run Development Server

```bash
make dev
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Configurable Ports

Both the backend and frontend servers support configurable ports via environment variables.

#### Backend Port Configuration

The backend server port can be configured using the `PORT` environment variable in the root `.env` file:

```bash
# .env
PORT=8000  # Default backend port
```

To run the backend on a custom port:

```bash
# Option 1: Set in .env file
PORT=8080

# Option 2: Set environment variable directly
PORT=8080 python -m taskflow.main

# Option 3: Set environment variable with uvicorn
PORT=8080 uvicorn taskflow.main:app --reload
```

#### Frontend Port Configuration

The frontend dev server port can be configured using the `VITE_PORT` environment variable in `task_client/.env`:

```bash
# task_client/.env
VITE_PORT=3000  # Default frontend port
VITE_API_URL=http://localhost:8000  # Backend API URL
```

To run the frontend on a custom port:

```bash
cd task_client
VITE_PORT=3001 npm run dev
```

**Important:** If you change the backend port, make sure to update `VITE_API_URL` in `task_client/.env` to match the new backend port.

## Example Usage

**Note:** The following examples assume the backend is running on the default port `8000`. If you've configured a different port, replace `8000` with your configured port number.

### Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123", "name": "John Doe"}'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'
```

### Create a Project

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name": "My Project", "description": "A test project"}'
```

### Create a Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"project_id": 1, "title": "Implement feature", "priority": "high", "status": "todo"}'
```

### Get Health Status

```bash
curl http://localhost:8000/health
```

## Development

### Run Tests

```bash
make test
```

### Lint Code

```bash
make lint
```

### Format Code

```bash
make format
```

## Development Commands

```bash
make dev        # Run development server with hot reload
make lint       # Run ruff linter
make fmt        # Format code with ruff and black
make typecheck  # Type check with mypy
make test       # Run tests (quiet mode)
make seed       # Seed database with sample data
make clean      # Clean database and cache files
```

## Known Quirks

This codebase **intentionally** contains the following imperfections for demo purposes:

### Services Layer

1. **Duplicate Reminder Functions**: `send_task_reminder()` and `remind_task_due()` in `notification_service.py` (lines 28-76 and 79-135) are near-duplicates with:
   - Different parameter names (`task` vs `task_obj`, `user` vs `user_obj`)
   - Different date formatting functions
   - Slightly different logging patterns
   - Different email subject formats

2. **Long Conditional Chains**:
   - `report_service.py::build_daily_summary()` (lines 278-432) contains >100 lines of nested if-elif statements
   - `report_service.py::build_task_summary_string()` (lines 96-202) has deeply nested conditionals
   - Both should be refactored into strategy patterns or lookup tables

3. **Duplicate Urgency Functions**: Two nearly identical functions compute task urgency:
   - `task_service.py::compute_urgency_label()` (lines 246-276)
   - `report_service.py::calculate_task_urgency()` (lines 436-470)
   - Different thresholds (24h vs 12h, 3 days vs 2 days) and return values

4. **Raw SQL Query**: `project_service.py::get_project_stats()` (lines 104-126) uses raw SQL via `text()` instead of SQLAlchemy ORM, marked as "temporary optimization"

5. **Circular Import**: `report_service.py` and `task_service.py` both import from `taskflow.services.__init__` creating subtle import tangle

6. **Mixed Sync/Async Patterns**:
   - `report_service.py::async_calculate_completion_rate()` (lines 68-77) is unnecessarily async
   - Called from sync code via `asyncio.run()` for no strong reason (lines 100-104)

7. **Missing Type Hints**:
   - `auth_service.py::login()` (line 59) missing return type
   - `auth_service.py::decode_token()` (line 138) missing return type
   - Several other functions throughout codebase

8. **Inconsistent Naming**: Mix of `snake_case` and `camelCase`:
   - `user_service.py::getUserStats()` uses camelCase (line 161)
   - `utils/config.py::getSecretKey()` uses camelCase

9. **Inconsistent Logging Patterns**:
   - `auth_service.py` uses `setup_logger()` (line 16)
   - `user_service.py` uses direct `logging.getLogger()` (line 12)
   - Most others use `get_logger()`

### API Layer

10. **Inconsistent Docstring Styles**:
    - `users_api.py::register_user()` uses Google-style (Args/Returns)
    - `users_api.py::login()` uses NumPy-style (Parameters/Returns with dashes)
    - `users_api.py::get_current_user_info()` has no docstring
    - `projects_api.py::list_projects()` has no docstring

11. **Mixed Pydantic Models and Manual Dicts**:
    - Some endpoints return Pydantic models with `response_model`
    - Others return manually constructed dicts
    - `users_api.py::login()` returns dict instead of `TokenResponse` (line 138)
    - `users_api.py::get_current_user_info()` returns manual dict (lines 147-152)

12. **Unnecessary Async/Sync Mixing in API**:
    - `tasks_api.py::create_task()` is async but wraps sync code with `to_thread` (lines 52-81)
    - `tasks_api.py::get_project_tasks()` is sync but creates async wrapper with `asyncio.run()` then uses `to_thread` inside (lines 294-350) - triple unnecessary wrapping!
    - `tasks_api.py::update_task()` is sync with no wrapper

### Models/Database

13. **Composite Unique Constraint**: `projects` table has composite unique on `(name, owner_id)` (project.py line 30) - realistic but can cause duplicate name errors

14. **Indexes on Tasks**: `due_date`, `project_id`, `assigned_to` all indexed (task.py) but may be over-indexed for demo DB

15. **TODO Comment**: `models/base.py` (lines 5-6) has TODO about migrating to Alembic instead of `create_all()`

### Tests

16. **Fragile Tests**:
    - `test_reports.py::test_get_task_verbose_summary_format()` (lines 96-130) depends on exact string format including emojis
    - `test_reports.py::test_verbose_summary_priority_critical()` (lines 133-162) checks exact emoji sequence "⚠️ CRITICAL PRIORITY ⚠️"
    - Any change to `build_task_summary_string()` output will break these tests

17. **Redundant Test**:
    - `test_reports.py::test_create_daily_summary_redundant()` (lines 164-202) tests same functionality as `test_get_daily_summary()`
    - Both test daily summary via different endpoints (POST vs GET)
    - Underlying business logic is identical

### Utils

18. **Duplicate Date Formatting**: Date formatting scattered across:
    - `utils/helpers.py::format_date()`
    - `utils/date_utils.py::format_datetime()`
    - `utils/date_utils.py::format_date_pretty()`
    - `utils/helpers.py::format_date_simple()`
    - All produce different formats for the same input

19. **Scattered Type Ignores**: Many `# type: ignore` comments instead of proper typing throughout codebase

## Architecture

```
taskflow/
├── api/          # FastAPI route handlers
├── services/     # Business logic layer
├── models/       # SQLAlchemy models and repository pattern
├── utils/        # Shared utilities and helpers
├── migrations/   # Database migrations (stubbed)
├── tests/        # pytest test suite
└── scripts/      # Utility scripts (seeding, etc.)
```

## License

MIT (Demo purposes only)
