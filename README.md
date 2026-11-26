# Task Management REST API

A backend REST API for managing personal and team tasks, user accounts, due dates, file exports, and productivity statistics. Built with FastAPI, SQLAlchemy, Pydantic, and SQLite.

## Features

- User registration and login (Bearer token & HTTP Basic authentication)
- Full task CRUD (create, list, retrieve, update, complete, delete)
- Task priority levels (`low`, `medium`, `high`, `urgent`) and status tracking (`todo`, `in_progress`, `completed`, `archived`)
- Keyword search, filtering, sorting, and pagination
- Due date tracking and task productivity statistics
- Task export to JSON and CSV files

## Technology Stack

- **Language:** Python 3.10+
- **Web Framework:** FastAPI
- **ORM & Database:** SQLAlchemy + SQLite
- **Validation:** Pydantic
- **Testing:** Pytest & HTTPX

## Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── dependencies.py
│   ├── routers/
│   │   ├── tasks.py
│   │   ├── users.py
│   │   └── statistics.py
│   ├── services/
│   │   ├── task_service.py
│   │   ├── export_service.py
│   │   └── audit_service.py
│   └── utils/
│       ├── validation.py
│       └── date_helpers.py
├── tests/
│   ├── conftest.py
│   ├── test_tasks.py
│   ├── test_users.py
│   ├── test_statistics.py
│   └── test_security.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── requirements.txt
└── README.md
```

## Installation & Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional environment variables:

- `DATABASE_URL`: SQLAlchemy database URL (defaults to `sqlite:///./tasks.db`)
- `EXPORT_DIR`: Directory for exported task files (defaults to `./exports`)

## Running the API

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Running Tests

Execute the test suite with Pytest:

```bash
pytest -v
```

## API Endpoints

### Users
- `POST /users/register` — Register a new user account
- `POST /users/login` — Authenticate and receive a bearer token
- `GET /users/me` — Retrieve the authenticated user's profile
- `GET /users/{user_id}` — Retrieve a user profile by ID

### Tasks
- `POST /tasks` — Create a new task
- `GET /tasks` — List tasks with optional `status`, `priority`, `search`, `sort_by`, `sort_order`, `page`, and `limit` query parameters
- `GET /tasks/search?q=<keyword>` — Search tasks by keyword
- `GET /tasks/{task_id}` — Retrieve a task by ID
- `PUT /tasks/{task_id}` — Update a task
- `PATCH /tasks/{task_id}/complete` — Mark a task as completed
- `DELETE /tasks/{task_id}` — Delete a task
- `POST /tasks/export` — Export tasks to JSON or CSV
- `GET /tasks/export/download?filename=<name>` — Download an exported file

### Statistics
- `GET /statistics` — Retrieve task counts, overdue count, completion rate, and breakdown by priority

## Example Requests

```bash
# Register a user
curl -X POST http://127.0.0.1:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "Password123!"}'

# Login
curl -X POST http://127.0.0.1:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "Password123!"}'

# Create a task
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Prepare release notes", "priority": "high", "status": "todo"}'
```

