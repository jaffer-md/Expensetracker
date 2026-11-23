# Spec: Step 7 — Add Expense

## Overview

- Lets a logged-in user submit a new expense through a dedicated form page at `/expenses/add`.
- The route already exists as a GET placeholder. This step upgrades it to a full GET and POST handler.
- Validated data is inserted into the `expenses` table, and the user is redirected to the profile page on success.
- A reusable `insert_expense()` query helper is added to `database/queries.py`.
- An "Add Expense" button is added to `profile.html`, and a nav link is added to `base.html`, so users can reach the form.

## Depends on

- Step 01 — Database Setup. The `expenses` table exists with all required columns.
- Step 03 — Login and Logout. `session["user_id"]` is set and checked.
- Step 04 and Step 05 — Profile page. The profile page exists and is the natural redirect target after saving.

## Routes

- `GET /expenses/add` — renders the add-expense form. Logged-in only.
- `POST /expenses/add` — validates and inserts the new expense. Logged-in only.

## Database changes

- No database changes.
- The `expenses` table already has all required columns: `id`, `user_id`, `amount`, `category`, `date`, `description`, and `created_at`.

## Templates

- Create `templates/add_expense.html`:
  - Extends `base.html`.
  - Contains a form with `method="POST"` and `action="/expenses/add"`.
  - Fields:
    - `amount` — a number input with `step="0.01"`, `min="0.01"`, and `required`.
    - `category` — a `<select>` with exactly seven fixed options: Food, Transport, Bills, Health, Entertainment, Shopping, and Other.
    - `date` — a `<input type="date">`, `required`, defaulting to today's date.
    - `description` — an optional text input with a maximum of 200 characters.
  - A "Save Expense" submit button, and a cancel link back to `/profile`.
  - A flash and error message block that displays validation errors and re-populates previously submitted values on failure.
- Modify `templates/profile.html`:
  - Add an "Add Expense" button or link pointing to `/expenses/add`, placed near the transaction table heading.
- Modify `templates/base.html`:
  - Add an "Add Expense" link in the navbar, shown only when `session.user_id` is set.

## Files to change

- `app.py` — replace the GET-only placeholder at `/expenses/add` with a GET and POST handler:
  - GET renders `add_expense.html`. Redirects to `/login` if the user is not authenticated.
  - POST reads the form fields, validates them, calls `insert_expense()`, and redirects to `url_for("profile")` on success.
- `database/queries.py` — add `insert_expense(user_id, amount, category, date, description)`.
- `templates/profile.html` — add the "Add Expense" button.
- `templates/base.html` — add the "Add Expense" navbar link for logged-in users.

## Files to create

- `templates/add_expense.html`
- `tests/test_add_expense.py`

## New dependencies

- None.

## Rules for implementation

- No SQLAlchemy or ORMs. Raw `sqlite3` only, via `get_db()`.
- Parameterised queries only. Never string-format values into SQL.
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()`).
- Unauthenticated access to both `GET` and `POST /expenses/add` must redirect to `/login`.
- Validation rules for `POST`, applied in this order:
  1. `amount`: required. Must parse as a positive float greater than 0. Parse with `float()` and catch `ValueError`.
  2. `category`: required. Must be one of the seven fixed categories. Reject anything else.
  3. `date`: required. Must be a valid `YYYY-MM-DD` date. Parse with `datetime.strptime`.
  4. `description`: optional. Strip whitespace. Store `None` if blank.
- On any validation error, re-render the form with the error message and the previously submitted values pre-filled.
- After a successful insert, redirect to `url_for("profile")`. Do not render the form again.
- Currency must always display as ₹. Never £ or $.
- Use CSS variables. Never hardcode hex values.
- No inline styles.
- All templates extend `base.html`.
- Use `url_for()` for every internal link. Never hardcode paths.

## Tests to write

- File: `tests/test_add_expense.py`.
- Unit tests:

| Function | Input | Expected output |
|---|---|---|
| `insert_expense` | Valid `user_id`, `amount=50.0`, `category="Food"`, `date="2026-03-20"`, `description="Lunch"` | Row is inserted; querying the database returns the new row |
| `insert_expense` | `description=None` | Row is inserted with `description` stored as NULL |

- Route tests:
  - `GET /expenses/add` unauthenticated redirects to `/login` (302).
  - `GET /expenses/add` authenticated returns 200. The response contains the category `<select>` with all seven options, and a form with `method="POST"`.
  - `POST /expenses/add` unauthenticated redirects to `/login` (302).
  - `POST /expenses/add` authenticated with valid data (`amount=50.0`, `category=Food`, `date=2026-03-20`, `description=Lunch`) redirects to `/profile` (302), and the new expense row exists in the database for the test user.
  - `POST /expenses/add` authenticated with a missing amount returns 200 and the response contains an error message.
  - `POST /expenses/add` authenticated with `amount=0` returns 200 and the response contains an error message.
  - `POST /expenses/add` authenticated with a non-numeric amount returns 200 and the response contains an error message.
  - `POST /expenses/add` authenticated with a category not in the fixed list returns 200 and the response contains an error message.
  - `POST /expenses/add` authenticated with an invalid date string returns 200 and the response contains an error message.
  - `POST /expenses/add` authenticated with no description (optional field) redirects to `/profile` (302), and the row is inserted with `description` = NULL.

## Definition of done

- [ ] Visiting `/expenses/add` while logged out redirects to `/login`.
- [ ] Visiting `/expenses/add` while logged in shows a form with amount, category, date, and description fields.
- [ ] The category dropdown contains exactly: Food, Transport, Bills, Health, Entertainment, Shopping, and Other.
- [ ] Submitting a valid expense redirects to `/profile`, and the new expense appears in the transaction list.
- [ ] Submitting with a missing or zero amount re-renders the form with an error, and the previously entered values are retained.
- [ ] Submitting with an invalid category re-renders the form with an error.
- [ ] Submitting with an invalid date re-renders the form with an error.
- [ ] Submitting without a description saves the expense with no error.
- [ ] The "Add Expense" button on the profile page navigates to `/expenses/add`.
- [ ] The navbar shows an "Add Expense" link when logged in.
