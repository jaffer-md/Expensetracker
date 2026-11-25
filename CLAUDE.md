# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Spendly — a small Flask + SQLite expense tracker (server-rendered Jinja templates, no JS framework). Features are built incrementally from numbered specs.

## Commands

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py                                  # dev server on http://localhost:5001 (debug on)
pytest                                         # all tests
pytest tests/test_add_expense.py               # one file
pytest tests/test_add_expense.py -k "name"     # one test
```

No linter is configured. Demo login: `demo@spendly.com` / `demo123` (created by `seed_db()` only when the users table is empty).

## Architecture

- `app.py` — all routes, form validation (`_validate_expense_form`, shared by add/edit), and profile date-filter logic (`_preset_ranges`, `_parse_iso_date`). `init_db()` + `seed_db()` run at import time. Constants (`CATEGORIES`, amount/description limits) live here.
- `database/db.py` — connection (`get_db`, Row factory, `PRAGMA foreign_keys=ON`), schema (`init_db`), seeding, and user create/lookup. `DB_PATH` is `spendly.db` at the repo root.
- `database/queries.py` — expense/profile queries (stats, category breakdown, recent transactions, expense CRUD). Every expense query takes `user_id` so users can only touch their own rows; non-owned IDs return 404 from routes.
- `templates/` extend `base.html`; `static/css` (`style.css`, `landing.css`) and `static/js/main.js` (currently a one-line stub).
- Auth is session-based (`session["user_id"]`); routes redirect to `/login` when absent. A context processor injects `nav_user_name` into every template.

## Conventions and gotchas

- Passwords use `pbkdf2:sha256` explicitly (`PASSWORD_HASH_METHOD`) because scrypt is unavailable on the project's Python 3.9 build — don't switch to the Werkzeug default.
- Dates are stored as `YYYY-MM-DD` text; amounts as REAL rounded to 2 decimals.
- Routes use `if request.method != "POST": abort(405)` after the GET branch; validation errors re-render the form with status 200 and a `flash(..., "error")`.
- Tests (`tests/conftest.py`) monkeypatch `database.db.DB_PATH` to a temp DB and pin seeded expense dates to November 2026 — never run tests against `spendly.db`. The `client` fixture imports `app` after the patch. The pinned dates are hardcoded, so tests that depend on "this month" or preset ranges (`tests/test_date_filter.py`) may fail once the real date moves past November 2026 — check there first if they break unexpectedly.
- `app.secret_key` is a hardcoded dev value.
- The "Placeholder routes — students will implement these" comment in `app.py` is stale: `/logout` below it is fully implemented. Login redirects to the landing page, not the profile.

## Spec-driven workflow

Features are specified in `Spec_NN_*.md` (root) and `.claude/specs/`, with plans in `.claude/plans/` and review reports in `.claude/reports/`. Project slash commands in `.claude/commands/`: `/create-spec`, `/test-feature <spec>`, `/code-review-feature <spec>`, `/ship-feature`, `/seed-user`, `/seed-expense`.
