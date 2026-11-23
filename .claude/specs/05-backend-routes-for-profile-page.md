# Spec: Step 5 — Backend Routes for Profile Page

## Overview

- Replaces all hardcoded data in the `/profile` route with live queries against the SQLite database.
- The profile page currently renders:
  - A static demo user.
  - Fixed summary stats.
  - A hand-typed transaction list.
  - A hardcoded category breakdown.
- This step wires those four sections to real data, so every logged-in user sees their own expenses.
- Three parallel subagents handle the three independent data concerns, before they are integrated into the single `/profile` route:
  - Transaction history.
  - Summary stats.
  - Category breakdown.

## Depends on

- Step 01 — Database Setup. The tables and `get_db()` exist.
- Step 02 — Registration. Users are stored in the database.
- Step 03 — Login and Logout. `session["user_id"]` is set on login.
- Step 04 — Profile Page (static UI). The template already renders all four sections.

## Routes

- No new routes.
- The existing `GET /profile` route is modified in place.

## Database changes

- No database changes.
- The `users` and `expenses` tables already have all required columns: `user_id`, `amount`, `category`, `date`, `description`, and `created_at`.

## Templates

- Modify `templates/profile.html`:
  - Amounts must be rendered with the ₹ symbol (Indian Rupee). Never £ or $.
  - All four dynamic sections are already present in the template. No structural changes are needed. Only the Jinja variables they consume are now real.

## Files to change

- `app.py` — replace the hardcoded data in the `profile()` view with calls to the new query helpers in `database/queries.py`.
- `templates/profile.html` — confirm the ₹ symbol is used for all currency display.

## Files to create

- `database/queries.py` — pure query helpers with no Flask imports, one function per data concern:
  - `get_user_by_id(user_id)`
    - Returns a dict with `name`, `email`, and `member_since`.
  - `get_summary_stats(user_id)`
    - Returns a dict with `total_spent`, `transaction_count`, and `top_category`.
  - `get_recent_transactions(user_id, limit=10)`
    - Returns a list of dicts, each with `date`, `description`, `category`, and `amount`.
    - Ordered newest-first.
  - `get_category_breakdown(user_id)`
    - Returns a list of dicts, each with `name`, `amount`, and `pct`.
    - `pct` is the percentage of the total, rounded to the nearest integer.
    - Ordered by amount descending.
- `tests/test_backend_connection.py` — unit and route tests, described in "Tests to write".

## New dependencies

- None.

## Rules for implementation

- No SQLAlchemy or ORMs. Raw `sqlite3` only, via `get_db()`.
- Parameterised queries only. Never string-format values into SQL.
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()`).
- Currency must always display as ₹. Never £ or $.
- `member_since` must be derived from `users.created_at` and formatted as "Month YYYY" (for example, "January 2026").
- `pct` values in the category breakdown must sum to 100. Use integer rounding and adjust the largest category to absorb any rounding remainder.
- If a user has no expenses, all helpers must return zeros and empty lists. They must never raise exceptions.
- All helpers in `database/queries.py` must call `get_db()` internally and close the connection before returning.
- Use CSS variables. Never hardcode hex values.
- No inline styles.
- All templates extend `base.html`.

## Tests to write

- File: `tests/test_backend_connection.py`.
- Unit tests:

| Function | Input | Expected output |
|---|---|---|
| `get_user_by_id` | Valid `user_id` | Dict with the correct `name`, `email`, and `member_since` |
| `get_user_by_id` | Non-existent id | `None` |
| `get_summary_stats` | `user_id` with expenses | Correct `total_spent`, `transaction_count`, and `top_category` |
| `get_summary_stats` | `user_id` with no expenses | `{"total_spent": 0, "transaction_count": 0, "top_category": "—"}` |
| `get_recent_transactions` | `user_id` with expenses | List ordered newest-first, each item with `date`, `description`, `category`, and `amount` |
| `get_recent_transactions` | `user_id` with no expenses | Empty list |
| `get_category_breakdown` | `user_id` with expenses | List ordered by amount descending; `pct` values are integers summing to 100 |
| `get_category_breakdown` | `user_id` with no expenses | Empty list |

- Route tests:
  - `GET /profile` unauthenticated redirects to `/login` (302).
  - `GET /profile` authenticated as the seed user:
    - Returns 200.
    - The response contains "Demo User".
    - The response contains "demo@spendly.com".
    - The response contains the ₹ symbol.
    - `total_spent` matches the sum of all seed expenses (346.24).
    - `transaction_count` is 8.
    - `top_category` is "Bills" (the highest single-category total).
    - The transaction list appears in newest-first order.
    - The category breakdown contains all 7 categories.

## Definition of done

- [ ] Logging in as `demo@spendly.com` / `demo123` shows "Demo User" and "demo@spendly.com" on the profile page, not the hardcoded strings.
- [ ] Total spent displayed on the profile page equals ₹346.24.
- [ ] Transaction count displayed is 8.
- [ ] Top category displayed is "Bills".
- [ ] The transaction list shows 8 rows, ordered newest date first.
- [ ] The category breakdown shows 7 categories with percentages that add up to 100%.
- [ ] All amounts on the page display the ₹ symbol.
- [ ] Registering a brand-new user and visiting `/profile` shows ₹0.00 total spent, 0 transactions, and an empty category breakdown, with no errors.
