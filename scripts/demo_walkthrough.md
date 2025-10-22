# TaskFlow Demo Walkthrough

This guide demonstrates the TaskFlow API and showcases the intentional code smells for analysis.

## Setup and Start

### 1. Initial Setup

```bash
# Install dependencies
make install

# Clean and initialize database
make clean
make setup-db

# Seed database with sample data (3 users, 3 projects, 20 tasks)
make seed
```

### 2. Start Development Server

```bash
# Terminal 1: Start the server
make dev

# Server will be available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

## API Walkthrough

### Step 1: Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "password123",
    "name": "Demo User"
  }'
```

**Expected Response:**
```json
{
  "id": 4,
  "email": "demo@example.com",
  "name": "Demo User",
  "is_active": true
}
```

### Step 2: Login and Get Token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "password123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 4,
    "email": "demo@example.com",
    "name": "Demo User",
    "is_active": true
  }
}
```

**Save the access_token for subsequent requests!**

### Step 3: Create a Project

```bash
# Set your token
TOKEN="YOUR_ACCESS_TOKEN_HERE"

curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Demo Project",
    "description": "A sample project for demonstration"
  }'
```

**Expected Response:**
```json
{
  "id": 4,
  "name": "Demo Project",
  "description": "A sample project for demonstration",
  "owner_id": 4,
  "status": "active"
}
```

### Step 4: Create Tasks in the Project

#### Task 1: High Priority Task (Due Soon)

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "project_id": 4,
    "title": "Implement authentication system",
    "description": "Add JWT-based auth with refresh tokens",
    "priority": "high",
    "status": "todo",
    "due_date": "2025-10-25T18:00:00"
  }'
```

#### Task 2: Critical Task (Overdue)

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "project_id": 4,
    "title": "Fix production bug in payment flow",
    "description": "Users reporting failed transactions",
    "priority": "critical",
    "status": "in_progress",
    "due_date": "2025-10-20T12:00:00"
  }'
```

#### Task 3: Medium Priority Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "project_id": 4,
    "title": "Update documentation",
    "description": "Add API documentation for new endpoints",
    "priority": "medium",
    "status": "todo"
  }'
```

#### Task 4: Task with Assignment

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "project_id": 4,
    "title": "Code review for feature branch",
    "description": "Review PR #123 for new dashboard",
    "priority": "high",
    "status": "todo",
    "assigned_to": 1,
    "due_date": "2025-10-24T17:00:00"
  }'
```

#### Task 5: Completed Task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "project_id": 4,
    "title": "Setup CI/CD pipeline",
    "description": "Configured GitHub Actions for automated testing",
    "priority": "medium",
    "status": "done"
  }'
```

### Step 5: Get Project Tasks

```bash
curl -X GET "http://localhost:8000/tasks/projects/4/tasks" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 6: Update Task Status

```bash
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "status": "in_progress"
  }'
```

### Step 7: Generate Daily Summary Report

```bash
curl -X POST http://localhost:8000/reports/daily_summary \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "project_id": 4,
    "include_overdue": true,
    "include_assignees": true,
    "compact": false
  }'
```

**Response includes:**
- `text_summary`: Large formatted text blob with emojis showing task status
- `metrics`: JSON with task counts and completion rate
- Demonstrates the **long if-elif chain** in `build_daily_summary()`

### Step 8: Get User Statistics

```bash
curl -X GET http://localhost:8000/users/stats \
  -H "Authorization: Bearer $TOKEN"
```

### Step 9: Get Project Report (Uses Raw SQL!)

```bash
curl -X GET http://localhost:8000/reports/project/4 \
  -H "Authorization: Bearer $TOKEN"
```

**Note:** This endpoint uses **raw SQL** instead of the ORM (see `project_service.py::get_project_stats()`)

### Step 10: Get Overdue Tasks Report

```bash
curl -X GET http://localhost:8000/reports/overdue \
  -H "Authorization: Bearer $TOKEN"
```

## Using Seeded Data

The database is seeded with:
- **3 users**: alice@example.com, bob@example.com, carol@example.com
- **Password**: password123 (for all users)
- **3 projects**: Website Redesign, Mobile App Development, API Migration
- **20 tasks**: With varied statuses, priorities, and due dates (some overdue)

### Login as Seeded User

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }'
```

### Get Alice's Projects

```bash
# Use Alice's token
curl -X GET http://localhost:8000/projects \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

---

## Codemender Semantic Search Query Ideas

Use these queries to analyze the TaskFlow codebase and identify code smells:

### 1. Find All Notification/Email Functions

**Query:**
```
"Find all functions that send reminders or email notifications"
```

**Expected Findings:**
- `notification_service.py::send_task_reminder()` (line 28)
- `notification_service.py::remind_task_due()` (line 79)
- `notification_service.py::send_overdue_notification()` (line 137)
- `notification_service.py::send_daily_summary()` (line 162)
- `notification_service.py::send_assignment_notification()` (line 208)
- `notification_service.py::notify_task_completion()` (line 236)
- `notification_service.py::send_bulk_reminders()` (line 255)

**Code Smell to Identify:**
- **Duplicate Functions**: `send_task_reminder()` vs `remind_task_due()` do the same thing with:
  - Different parameter names (`task` vs `task_obj`, `user` vs `user_obj`)
  - Different email subjects
  - Different date formatting functions
  - Different logging patterns

**Recommendation:** Consolidate into single function with consistent interface

---

### 2. Locate All Date Formatting Logic

**Query:**
```
"Locate all date formatting logic and normalize it"
```

**Expected Findings:**

**In `utils/date_utils.py`:**
- `format_datetime()` - Returns "YYYY-MM-DD HH:MM:SS"
- `format_date_pretty()` - Returns "Month DD, YYYY at HH:MM"
- `format_relative_time()` - Returns "X days ago" / "in X days"
- `format_time()` - Returns "HH:MM AM/PM"

**In `utils/helpers.py`:**
- `format_date()` - Returns "YYYY-MM-DD"
- `format_date_simple()` - Returns "MM/DD/YYYY"
- `format_datetime_readable()` - Returns "Mon DD, YYYY HH:MM"

**Code Smell to Identify:**
- **Duplicate Logic**: 7 different functions producing different formats
- **Scattered Responsibility**: Date formatting logic split across two modules
- **Inconsistent Usage**: Different parts of codebase use different formatters

**Recommendation:** Create single `DateFormatter` class with well-defined methods

---

### 3. Find High Complexity Functions

**Query:**
```
"Show functions with cyclomatic complexity > 12"
```

**Expected High-Complexity Findings:**

1. **`report_service.py::build_daily_summary()`** (lines 278-432)
   - **Complexity: ~40+**
   - 155 lines with deeply nested if-elif chains
   - Combines: status, priority, assignees, overdue, comments
   - Should be refactored into strategy pattern

2. **`report_service.py::build_task_summary_string()`** (lines 119-202)
   - **Complexity: ~25+**
   - Multiple nested conditionals based on boolean flags
   - Should be broken into smaller functions

3. **`task_service.py::find_tasks_due_soon()`** (lines 218-243)
   - **Complexity: ~8**
   - Multiple conditions for filtering tasks

**Code Smell to Identify:**
- **Long Method**: Functions exceeding 50 lines
- **Complex Conditional Logic**: Deep nesting and multiple paths
- **God Function**: Doing too many things

**Recommendation:** Apply Extract Method and Strategy Pattern refactorings

---

### 4. Find Overdue Task Logic

**Query:**
```
"Where are overdue tasks computed or inferred?"
```

**Expected Findings:**

1. **`task_service.py::get_overdue_tasks()`** (line 66)
   - Delegates to `TaskRepository.get_overdue_tasks()`

2. **`models/repository.py::TaskRepository.get_overdue_tasks()`** (lines 102-107)
   - Query: `where(Task.due_date < datetime.utcnow(), Task.status != "done")`

3. **`report_service.py::build_daily_summary()`** (lines 394-399)
   - Checks: `time_until_due.total_seconds() < 0 and task.status != TASK_STATUS_DONE`
   - Calculates `days_overdue = abs(time_until_due.days)`

4. **`report_service.py::get_overdue_report()`** (line 204)
   - Uses `task_repo.get_overdue_tasks()`

5. **`utils/date_utils.py::is_past_due()`** (lines 25-29)
   - Helper: `return due_date < datetime.utcnow()`

**Code Smell to Identify:**
- **Duplicate Logic**: Overdue calculation appears in multiple places
- **Magic Logic**: Inconsistent handling (some check status, some don't)

**Recommendation:** Centralize overdue logic in Task model as property or service method

---

### 5. Find Duplicate Reminder Functions

**Query:**
```
"Find duplicate logic between send_task_reminder and remind_task_due"
```

**Expected Findings:**

**Function 1:** `notification_service.py::send_task_reminder(self, task, user)` (lines 28-76)
```python
def send_task_reminder(self, task: Task, user: User) -> bool:
    # Uses format_datetime()
    due_date_str = format_datetime(task.due_date) if task.due_date else "No due date"

    subject = f"Reminder: {task.title}"

    body = f"""
    Hello {user.name},

    This is a reminder about your task:

    Task: {task.title}
    Status: {task.status}
    Priority: {task.priority}
    Due Date: {due_date_str}

    Please complete this task at your earliest convenience.
    """

    # Logging: logger.info(f"Task reminder sent to {user.email} for task {task.id}")
```

**Function 2:** `notification_service.py::remind_task_due(self, task_obj, user_obj, urgent=False)` (lines 79-135)
```python
def remind_task_due(self, task_obj: Task, user_obj: User, urgent: bool = False) -> bool:
    # Uses format_date_pretty()
    if task_obj.due_date:
        due_str = format_date_pretty(task_obj.due_date)
    else:
        due_str = "Not set"

    urgency_prefix = "URGENT: " if urgent else ""
    email_subject = f"{urgency_prefix}Task Reminder: {task_obj.title}"

    email_body = f"""
    Hi {user_obj.name},

    {'⚠️ URGENT REMINDER ⚠️' if urgent else 'Reminder'}

    Task: {task_obj.title}
    Priority: {task_obj.priority.upper()}
    Status: {task_obj.status}
    Due: {due_str}
    """

    # Logging: logger.info(f"Due reminder sent for task {task_obj.id}")
```

**Differences:**
1. **Parameter names**: `task` vs `task_obj`, `user` vs `user_obj`
2. **Subject format**: `"Reminder:"` vs `"Task Reminder:"` (with optional URGENT prefix)
3. **Date formatting**: `format_datetime()` vs `format_date_pretty()`
4. **Greeting**: "Hello" vs "Hi"
5. **Priority display**: Normal case vs `.upper()`
6. **Logging messages**: Different formats
7. **Urgent flag**: Second function has `urgent` parameter

**Code Smell to Identify:**
- **Near Duplicate**: ~90% similar code with minor variations
- **Inconsistent Interface**: Different parameter naming conventions
- **Fragmented Logic**: Should be one function with options

**Recommendation:**
```python
def send_task_reminder(
    self,
    task: Task,
    user: User,
    urgent: bool = False,
    subject_prefix: str = "Reminder"
) -> bool:
    # Single unified implementation
```

---

## Additional Code Smells to Search For

### 6. Find Circular Imports

**Query:**
```
"Find modules that import each other or create circular dependencies"
```

**Finding:** `report_service.py` ↔ `task_service.py`
- Both import from `taskflow.services.__init__` for constants
- `report_service.py` also imports `TaskService` directly

### 7. Find Mixed Async/Sync Patterns

**Query:**
```
"Find functions that unnecessarily wrap sync code with asyncio.to_thread"
```

**Findings:**
- `tasks_api.py::create_task()` - Async wrapping sync service
- `tasks_api.py::get_project_tasks()` - Sync wrapping async wrapping sync (triple wrapper!)
- `report_service.py::async_calculate_completion_rate()` - Unnecessarily async

### 8. Find Raw SQL Queries

**Query:**
```
"Find direct SQL queries using text() or execute() that bypass the ORM"
```

**Finding:** `project_service.py::get_project_stats()` (lines 104-126)
- Uses `text()` with raw SQL SELECT statement
- Has TODO comment: "This should use SQLAlchemy instead of raw SQL"

### 9. Find Missing Type Hints

**Query:**
```
"Find functions without return type annotations"
```

**Findings:**
- `auth_service.py::login()` (line 59)
- `auth_service.py::decode_token()` (line 138)
- `user_service.py::getUserStats()` (line 161) - Also uses camelCase!

### 10. Find Inconsistent Naming

**Query:**
```
"Find functions using camelCase instead of snake_case"
```

**Findings:**
- `user_service.py::getUserStats()` - Should be `get_user_stats()`
- `utils/config.py::getSecretKey()` - Should be `get_secret_key()`

---

## Testing the Code Smells

### Run Tests to See Fragile Tests

```bash
# Run all tests
make test

# Run specific fragile test
pytest tests/test_reports.py::test_get_task_verbose_summary_format -v

# Run redundant test
pytest tests/test_reports.py::test_create_daily_summary_redundant -v
```

### Trigger Type Checking Errors

```bash
# Run mypy to see missing type hints
make typecheck
```

### Check for Linting Issues

```bash
# Run ruff to see style inconsistencies
make lint
```

---

## Summary

This walkthrough demonstrates:
- ✅ All 19 intentional code smells
- ✅ Complete API functionality
- ✅ Database relationships and constraints
- ✅ Authentication and authorization flow
- ✅ Report generation with complex logic
- ✅ Mixed async/sync patterns
- ✅ Duplicate code across modules

Use the semantic search queries to identify these patterns and practice refactoring!
