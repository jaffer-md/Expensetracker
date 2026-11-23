# Review: Step 1 — Database Setup

**Plan reviewed:** `.claude/plans/01-database-setup.md`
**Spec:** `.claude/specs/01-database-setup.md`
**Files changed:** `database/db.py`, `app.py`, `.gitignore`

## Summary

The implementation matches the plan and spec. Schema, constraints, seeding, and foreign-key enforcement all behave as specified. There are three deviations from the plan, one design issue in the seed dates, and two verification gaps. None of them block Step 2.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| 1. Save plan to `.claude/plans/01-database-setup.md` | Done | Copied after approval. `.claude/plans/` is gitignored. |
| 2. `DB_PATH` = project root `spendly.db` | Done | Resolved from `__file__`, so it does not depend on the working directory. |
| 2. `get_db()`: `Row` factory, FK on, return conn | Done | `PRAGMA foreign_keys = ON` runs on every connection. |
| 2. `init_db()`: both tables, `IF NOT EXISTS`, commit, close in `finally` | Done | Schema matches spec section 4 column for column. |
| 2. `seed_db()`: idempotent, demo user, 8 expenses, all 7 categories | Done | Parameterized `executemany`. Verified 1 user, 8 expenses, 7 categories. |
| 2. Password hash via `generate_password_hash` | **Deviated** | Hash uses `method="pbkdf2:sha256"`. See Deviation 1. |
| 2. Seed dates in current month | **Partially met** | Dates are clamped to today. See Issue 1. |
| 3. `app.py`: import and run init/seed in app context | Done | Runs at module import, which is the app's startup path. |
| 4. Add `spendly.db` to `.gitignore` | Done | Line 224. |
| Verification: run `python app.py` on port 5001 | **Not done as written** | I used Flask's test client. See Gap 1. |
| Verification: delete generated `spendly.db` afterward | **Not done as written** | The file was kept. See Deviation 2. |

## Spec compliance

Definition of Done (spec section 14):

- [x] Database file is created on app startup. Verified by importing `app`.
- [x] Both tables exist with the correct schema and constraints.
- [x] Demo user exists with a hashed password (`pbkdf2:sha256:...`, not plaintext).
- [x] 8 sample expenses exist across all 7 categories.
- [x] No duplicate seed data on repeated runs. Verified by calling `seed_db()` twice.
- [x] App starts without errors. Verified with the test client, not a live server (Gap 1).
- [x] Foreign key enforcement works. Insert with `user_id=999` fails with `FOREIGN KEY constraint failed`.
- [x] All queries use parameterized SQL. The only non-parameterized SQL is static DDL in `init_db()`.

Error handling (spec section 13): nothing is swallowed. `finally` only closes the connection. Duplicate email raises `UNIQUE constraint failed: users.email`.

## Deviations

1. **Password hashing method.** The plan said to use werkzeug's default `generate_password_hash`. The project venv runs Python 3.9, and its `hashlib` has no `scrypt`. The default raised `AttributeError` in `seed_db()`, so I pinned `method="pbkdf2:sha256"`. The method is stored inside the hash, so `check_password_hash` still works. **Action for Step 2:** registration must use the same explicit method, or it will crash in this environment.

2. **Test database file kept.** The plan said to delete the `spendly.db` created by the test run. I kept it, so the app has demo data on first run. It is gitignored. If you want a clean state, delete `spendly.db` and restart the app.

3. **Unused import.** `app.py` imports `get_db` but does not use it. The spec asks for this import, so I kept it. Linters will flag it.

## Issues

1. **Seed dates collapse early in the month (design issue, in the plan).** `d(day)` clamps each day to today's day number, so the spec's "spread across the current month" only holds from about the 21st onward. Run on 2026-11-05, all eight expenses fall on 2026-11-01, 03, 05, 05, 05, 05, 05, 05. The alternative is to spread across the previous month or to use fixed day offsets, and both put dates in the future or in the previous month. Decide which behavior you want before Step 2 tests depend on the seed data.

2. **Import-time side effect.** `init_db()` and `seed_db()` run when `app.py` is imported. Any test that imports `app` writes to the real `spendly.db`. Once the pytest suite exists, it should point `DB_PATH` at a temp file (for example, with an environment variable or a monkeypatch fixture).

3. **Hashing portability.** Because the default hash method is unavailable here, any environment on this Python build needs the explicit method. This should be a single shared constant, not repeated strings.

## Verification gaps

- **Gap 1:** The plan asked for `python app.py` on port 5001. I only tested through Flask's test client. A live run would confirm the server starts and logs no errors.
- **Gap 2:** The plan's "delete afterward" step was skipped (Deviation 2).

## Recommended next actions

1. Run `.venv/bin/python app.py` and open `http://127.0.0.1:5001/` to close Gap 1.
2. Decide on the seed date behavior (Issue 1).
3. Add a shared password-hash constant before writing registration (Deviation 1, Issue 3).
4. Plan a test database override before adding pytest (Issue 2).
