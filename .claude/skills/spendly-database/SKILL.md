---
name: spendly-database
description: Creates and verifies Spendly's SQLite data file (spendly.db) - the users and expenses tables, the get_db/init_db/seed_db helpers in database/db.py, and their startup wiring in app.py. Use this skill whenever the user asks to set up, create, initialize, reset, rebuild, seed, or fix the Spendly database, SQLite file, schema, or demo data, or mentions spendly.db, database/db.py, init_db, seed_db, or "database setup" - even if the word "skill" isn't used.
---

# Spendly Database Setup

Builds the SQLite data file for Spendly, a Flask + SQLite expense tracker. Everything else (registration, login, profile, add/edit/delete expense, date filters) reads and writes these tables, so this must be correct first.

Source of truth for requirements: `.claude/specs/01-database-setup.md`. If it conflicts with this skill, the spec wins - read it first. This skill relies on its schema section, the seed-data section, and section 6 (startup wiring).

## Before you start

1. Read `database/db.py` and `app.py` to see what already exists. Extend or fix; don't blindly overwrite a working implementation.
2. Check whether `spendly.db` already exists at the project root. It holds real user data. **Never delete or recreate it without the user's explicit OK.** If a reset is requested, confirm first, then remove only that file and let `init_db()` + `seed_db()` rebuild it.
3. Activate the venv: `source .venv/bin/activate`.

## Rules (non-negotiable)

- `sqlite3` from the standard library only. No ORM, no SQLAlchemy, no new pip packages.
- Parameterized queries only (`?` placeholders). Never f-strings or `%` formatting in SQL.
- `PRAGMA foreign_keys = ON` on **every** connection (SQLite resets it per connection).
- `amount` is `REAL`, rounded to 2 decimals. Dates are `TEXT` in `YYYY-MM-DD`.
- Hash passwords with `generate_password_hash` using the explicit method `pbkdf2:sha256` (constant `PASSWORD_HASH_METHOD`). scrypt, Werkzeug's default, is unavailable on this project's Python 3.9 build - do not switch back to the default. (To re-check after a Python upgrade: `python -c "import hashlib; hashlib.scrypt(b'a', salt=b'b', n=2, r=1, p=1)"` - an `AttributeError` means still unavailable. Only change the method if the user asks.)
- `init_db()` and `seed_db()` must be idempotent: safe to call any number of times.
- Don't swallow errors. Let constraint and schema errors propagate; use `try/finally` to close connections.

## Schema

**users**

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL UNIQUE |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP |

**expenses**

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, FOREIGN KEY -> users(id) |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL (YYYY-MM-DD) |
| description | TEXT | nullable |
| created_at | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP |

Valid categories (fixed list, enforced in `app.py` as `CATEGORIES`, not in SQL): Food, Transport, Bills, Health, Entertainment, Shopping, Other.

## Implementation: `database/db.py`

`DB_PATH` points to `spendly.db` in the project root (parent of `database/`):

```python
import os
import sqlite3
from datetime import date
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spendly.db"
)
PASSWORD_HASH_METHOD = "pbkdf2:sha256"
```

Keep `DB_PATH` a module-level variable that `get_db()` reads at call time - the test suite monkeypatches `database.db.DB_PATH` to a temp file.

| Function | Behavior |
|---|---|
| `get_db()` | `sqlite3.connect(DB_PATH)`, set `row_factory = sqlite3.Row`, run `PRAGMA foreign_keys = ON`, return the connection. |
| `init_db()` | `CREATE TABLE IF NOT EXISTS` for both tables via `executescript`, commit, close in `finally`. |
| `seed_db()` | If `SELECT COUNT(*) FROM users` > 0, return immediately. Otherwise insert the demo user (Demo User / demo@spendly.com / demo123, hashed) and 8 sample expenses linked to `cursor.lastrowid`. Commit, close in `finally`. |

Seed data requirements:
- Exactly 8 expenses, covering **all 7 categories** (so one category appears twice).
- Dates spread across the current month, built from `date.today()` and formatted with `.isoformat()`. Clamp the day (`min(day, today.day)`) so no seeded date lies in the future. Consequence: early in the month (days 1-2) several seeded rows share the same date. That is expected; don't "fix" it by allowing future dates.
- Amounts are floats with 2 decimals; every row has a short description.

**Schema changes:** `CREATE TABLE IF NOT EXISTS` never alters a table that already exists, so editing the `CREATE` statements does not migrate `spendly.db`. For a schema change, add an explicit `ALTER TABLE` migration (idempotent: check `PRAGMA table_info` first) or, only with the user's explicit OK, reset the file as described above. Update the schema tables in this skill and the spec at the same time.

Other modules (`database/queries.py`, user create/lookup helpers) may add functions to this package later - don't remove them when editing `db.py`.

## Wiring: `app.py`

- Keep the existing import line from `database.db` intact. It also imports `create_user` and `get_user_by_email` (used by register/login); it must include at least `get_db, init_db, seed_db`.
- Call `init_db()` then `seed_db()` once at startup. `app.py` already does this in a module-level `with app.app_context():` block (right after `app.secret_key`). That satisfies the spec (section 6) and, because it runs at import time, also covers `python app.py` and the pytest `client` fixture. Leave it as is.
- The database must be ready before any route is served.

## Verify (always do this before reporting done)

Run from the project root with the venv active. Use a throwaway copy so real data is never touched:

```bash
python - <<'PY'
import database.db as db, tempfile, os, sqlite3
db.DB_PATH = os.path.join(tempfile.mkdtemp(), "t.db")
db.init_db(); db.init_db()            # idempotent
db.seed_db(); db.seed_db()            # idempotent
c = db.get_db()
print("users:", c.execute("select count(*) from users").fetchone()[0])          # 1
print("expenses:", c.execute("select count(*) from expenses").fetchone()[0])    # 8
print("categories:", c.execute("select count(distinct category) from expenses").fetchone()[0])  # 7
print("fk pragma:", c.execute("pragma foreign_keys").fetchone()[0])             # 1
print("hash:", c.execute("select password_hash from users").fetchone()[0][:14]) # pbkdf2:sha256
try:
    c.execute("insert into expenses (user_id,amount,category,date) values (999,1,'Food','2026-01-01')")
except sqlite3.IntegrityError as e:
    print("fk enforced:", e)
try:
    c.execute("insert into users (name,email,password_hash) values ('x','demo@spendly.com','h')")
except sqlite3.IntegrityError as e:
    print("unique enforced:", e)
PY
```

Then confirm the app boots (`python app.py`, dev server on port 5001) and, if tests exist, run `pytest`.

## Definition of done

- [ ] `spendly.db` is created on app startup
- [ ] Both tables exist with the exact schema and constraints above
- [ ] Demo user exists with a `pbkdf2:sha256` hashed password
- [ ] 8 sample expenses covering all 7 categories
- [ ] No duplicate seed data after repeated runs
- [ ] Foreign key and UNIQUE violations raise `sqlite3.IntegrityError`
- [ ] All SQL is parameterized
- [ ] App starts without errors

## Final report

Say what changed, the verification output (counts, constraint checks), and whether the existing `spendly.db` was left untouched or rebuilt.
