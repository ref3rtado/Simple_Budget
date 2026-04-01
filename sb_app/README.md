# Simple Budget

A full-stack personal budgeting web application built with FastAPI and Python.

## Features

- **User management** — create and manage user accounts
- **Transactions** — log income and expense transactions
- **Budgets** — define and track budgets by category
- **Reports** — view summaries and breakdowns of spending

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Server:** Uvicorn (ASGI)
- **Frontend:** HTML templates with static assets

## Getting Started

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply database migrations:

```bash
alembic upgrade head
```

Run the application:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

The app will be available at `http://localhost:8000`.
