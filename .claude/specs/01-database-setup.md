# Spec: Step 1 — Database Setup

## 1. Overview

This step replaces the stub in `database/db.py` with a working SQLite implementation for Spendly. It defines the two tables the application is built on (`users` and `expenses`), a connection helper, a schema initializer, and a development seed routine, and it wires them into app startup.

This is the foundational step of the project. Authentication (registration, login, logout), the profile page, and all expense tracking features (add, edit, delete, date filtering) read from and write to these tables, so none of them can be built until this step is complete.

## 2. Depends on

- Nothing. This is the first step and has no prerequisites.

## 3. Routes

- No new routes.
- The existing placeholder routes in `app.py` remain unchanged.

## 4. Database Schema

### Table A: `users`

| Column | SQLite Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | NOT NULL, DEFAULT current timestamp |

### Table B: `expenses`

| Column | SQLite Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, FOREIGN KEY referencing users(id) |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL — must be stored in YYYY-MM-DD format |
| description | TEXT | Nullable |
| created_at | TEXT | NOT NULL, DEFAULT current timestamp |

## 5. Functions to Implement (database/db.py)

| Function | Behavior |
|---|---|
| `get_db()` | Opens the `spendly.db` SQLite file located in the project root. Sets `row_factory` to `sqlite3.Row`. Enables `PRAGMA foreign_keys = ON`. Returns the connection. |
| `init_db()` | Creates both tables using `CREATE TABLE IF NOT EXISTS`. Safe to call multiple times. |
| `seed_db()` | Checks whether the `users` table already has rows; if yes, returns early without changes. Otherwise inserts one demo user (name: Demo User, email: demo@spendly.com, password: demo123, hashed with werkzeug) and 8 sample expenses linked to that user. The expenses cover all 7 categories, with dates spread across the current month. |

## 6. Changes to app.py

- Import `get_db`, `init_db`, and `seed_db` from `database.db`.
- Call `init_db()` and `seed_db()` inside `app.app_context()` on startup.
- The database must be ready before any route is served.

## 7. Files to Change

- `database/db.py`
- `app.py`

## 8. Files to Create

- None.

## 9. Dependencies

- No new pip packages.
- Use `sqlite3` (standard library) and `werkzeug.security` (already installed and listed in `requirements.txt`).

## 10. Categories (Fixed List)

These are the only valid expense category values:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

## 11. Rules for Implementation

- No ORM and no SQLAlchemy.
- Parameterized queries only — never string formatting in SQL.
- `PRAGMA foreign_keys = ON` on every connection.
- Store `amount` as REAL, not INTEGER.
- Hash passwords with `generate_password_hash` from `werkzeug.security`.
- `seed_db()` must be idempotent (safe to call multiple times).
- Dates must always be YYYY-MM-DD.

## 12. Expected Behavior

### Function behavior

| Function | When called correctly |
|---|---|
| `get_db()` | Returns an open connection to `spendly.db` in the project root. Rows are accessible by column name. Foreign key enforcement is active on the connection. |
| `init_db()` | After the first call, both tables exist with the schema in section 4. Repeated calls change nothing and raise no errors. |
| `seed_db()` | On an empty `users` table, creates the demo user with a hashed password and 8 expenses covering all 7 categories. On later calls, does nothing. |

### Database-level constraints

| Constraint | Enforced behavior |
|---|---|
| `users.email` UNIQUE | Two users cannot share an email address. |
| `users` NOT NULL columns | Inserts missing `name`, `email`, or `password_hash` are rejected. |
| `expenses.user_id` FOREIGN KEY | An expense can only reference an existing user. |
| `expenses` NOT NULL columns | Inserts missing `user_id`, `amount`, `category`, or `date` are rejected. |

## 13. Error Handling Expectations

| Situation | Expected result |
|---|---|
| Insert a user with a duplicate email | UNIQUE constraint failure |
| Insert an expense with a `user_id` that does not exist | Foreign key constraint failure |
| Invalid query or schema error | Raise a clear error so the problem is easy to debug; errors must not be silently swallowed |

## 14. Definition of Done

- [ ] Database file is created on app startup
- [ ] Both tables exist with the correct schema and constraints
- [ ] Demo user exists with a hashed password
- [ ] 8 sample expenses exist across all 7 categories
- [ ] No duplicate seed data on repeated runs
- [ ] App starts without errors
- [ ] Foreign key enforcement works
- [ ] All queries use parameterized SQL
