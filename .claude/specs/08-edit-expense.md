# Spec: Step 8 — Edit Expense

## Overview

- Lets a logged-in user edit any of their own expenses through a pre-populated form at `/expenses/<id>/edit`.
- The GET handler loads the existing expense from the database and renders the form with its current values.
- The POST handler validates the submission and updates the row in place.
- Ownership is enforced: a user can only edit expenses that belong to them.
- Two new query helpers are added to `database/queries.py`: `get_expense_by_id` and `update_expense`.
- The transactions table in `profile.html` gains an "Edit" action link per row. This requires `get_recent_transactions` to also return the expense id.

## Depends on

- Step 01 — Database Setup. The `expenses` table exists with all required columns.
- Step 03 — Login and Logout. `session["user_id"]` is set and enforced.
- Step 05 — Profile page. The profile page renders transactions, and the edit link lives there.
- Step 07 — Add Expense. This step establishes the form pattern that this step follows.

## Routes

- `GET /expenses/<int:id>/edit` — renders the edit form, pre-populated with the existing expense values. Logged-in only.
- `POST /expenses/<int:id>/edit` — validates and saves the updated expense. Logged-in only.

## Database changes

- No new tables or columns.
- All required columns already exist in `expenses`: `id`, `user_id`, `amount`, `category`, `date`, and `description`.

## Templates

- Create `templates/edit_expense.html`:
  - Extends `base.html`.
  - Contains a form with `method="POST"` and an action of `/expenses/{{ expense.id }}/edit`.
  - Fields, identical to `add_expense.html`, all pre-filled with the current values:
    - `amount` — a number input with `step="0.01"`, `min="0.01"`, and `required`, pre-filled.
    - `category` — a `<select>` with exactly seven fixed options, with the current value pre-selected.
    - `date` — a `<input type="date">`, `required`, pre-filled with the current value.
    - `description` — an optional text input with a maximum of 200 characters, pre-filled.
  - A "Save Changes" submit button, and a cancel link back to `/profile`.
  - An error message block. On a validation failure it re-populates the submitted values, not the original ones.
- Modify `templates/profile.html`:
  - Add an "Actions" column header to the transactions table `<thead>`.
  - Add an "Edit" link cell per row, pointing to `/expenses/{{ tx.id }}/edit`.

## Files to change

- `database/queries.py`:
  - Add `get_expense_by_id(expense_id, user_id)`:
    - Fetches a single expense row only if it belongs to the given user.
    - Returns `None` if the expense is not found or if `user_id` does not match.
    - The query is scoped to `id = ? AND user_id = ?`.
  - Add `update_expense(expense_id, user_id, amount, category, date, description)`:
    - Issues a parameterised `UPDATE` scoped to `id = ? AND user_id = ?` for ownership safety.
  - Modify `get_recent_transactions`:
    - Add `id` to the `SELECT` column list, so templates can build edit links.
- `app.py`:
  - Import `get_expense_by_id` and `update_expense` from `database.queries`.
  - Replace the GET-only placeholder at `/expenses/<int:id>/edit` with a full GET and POST handler:
    - GET calls `get_expense_by_id`. It returns 404 if the expense is not found or not owned by the user. Otherwise it renders `edit_expense.html` with the expense and the categories list.
    - POST reads the form fields and validates them with the same rules as Step 07. It calls `update_expense`, then redirects to `url_for("profile")` on success. Otherwise it re-renders the form with errors.
    - The route decorator must accept both methods: `methods=["GET", "POST"]`.
- `templates/profile.html`:
  - Add `<th>Actions</th>` to the table header.
  - Add an "Edit" link cell per transaction row.

## Files to create

- `templates/edit_expense.html`
- `tests/test_edit_expense.py`

## New dependencies

- None.

## Rules for implementation

- No SQLAlchemy or ORMs. Raw `sqlite3` only, via `get_db()`.
- Parameterised queries only. Never string-format values into SQL.
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()`).
- `get_expense_by_id` must scope its query to `id = ? AND user_id = ?`. It returns `None` if the expense is not found or the ownership check fails.
- `update_expense` must also include `user_id = ?` in its `WHERE` clause, as a second ownership guard.
- Unauthenticated access to both `GET` and `POST` must redirect to `/login`.
- If the expense does not exist or belongs to another user, return 404.
- Validation rules for `POST`, identical to Step 07, applied in this order:
  1. `amount`: required. Must parse as a positive float greater than 0. Parse with `float()` and catch `ValueError`.
  2. `category`: required. Must be one of the seven fixed categories. Reject anything else.
  3. `date`: required. Must be a valid `YYYY-MM-DD` string. Parse with `datetime.strptime`.
  4. `description`: optional. Strip whitespace. Store `None` if blank.
- On any validation error, re-render the form with the error message and the submitted values pre-filled, not the original ones.
- After a successful update, redirect to `url_for("profile")`. Do not render the form again.
- Currency must always display as ₹. Never £ or $.
- Use CSS variables. Never hardcode hex values.
- No inline styles.
- All templates extend `base.html`.
- Use `url_for()` for every internal link. Never hardcode paths.

## Tests to write

- File: `tests/test_edit_expense.py`.
- Unit tests:

| Function | Input | Expected output |
|---|---|---|
| `get_expense_by_id` | Valid `expense_id` and correct `user_id` | Returns the matching row as a dict-like object |
| `get_expense_by_id` | Valid `expense_id` and wrong `user_id` | Returns `None` |
| `get_expense_by_id` | Non-existent `expense_id` | Returns `None` |
| `update_expense` | Valid `expense_id`, correct `user_id`, `amount=99.0` | The row in the database reflects the updated amount |
| `update_expense` | Valid `expense_id`, wrong `user_id` | The row in the database is unchanged (0 rows affected, no error raised) |

- Route tests:
  - `GET /expenses/<id>/edit` unauthenticated redirects to `/login` (302).
  - `GET /expenses/<id>/edit` authenticated, own expense, returns 200. The response contains the form pre-filled with current values, and the `<select>` has the correct category pre-selected.
  - `GET /expenses/<id>/edit` authenticated, other user's expense, returns 404.
  - `GET /expenses/<id>/edit` authenticated, non-existent id, returns 404.
  - `POST /expenses/<id>/edit` unauthenticated redirects to `/login` (302).
  - `POST /expenses/<id>/edit` authenticated, valid data, redirects to `/profile` (302), and the updated values are reflected in the database.
  - `POST /expenses/<id>/edit` authenticated, other user's expense, returns 404.
  - `POST /expenses/<id>/edit` authenticated, missing amount, returns 200 and the response contains an error message.
  - `POST /expenses/<id>/edit` authenticated, `amount = 0`, returns 200 and the response contains an error message.
  - `POST /expenses/<id>/edit` authenticated, non-numeric amount, returns 200 and the response contains an error message.
  - `POST /expenses/<id>/edit` authenticated, invalid category, returns 200 and the response contains an error message.
  - `POST /expenses/<id>/edit` authenticated, invalid date string, returns 200 and the response contains an error message.
  - `POST /expenses/<id>/edit` authenticated, no description, redirects to `/profile` (302), and the row is updated with `description = NULL`.

## Definition of done

- [ ] Visiting `/expenses/<id>/edit` while logged out redirects to `/login`.
- [ ] Visiting `/expenses/<id>/edit` for a non-existent expense, or another user's expense, returns 404.
- [ ] Visiting `/expenses/<id>/edit` while logged in shows a form pre-filled with the expense's current values.
- [ ] The category dropdown has the correct category pre-selected.
- [ ] Submitting valid changes redirects to `/profile`, and the updated values appear in the transaction list.
- [ ] Submitting with a missing or zero amount re-renders the form with an error, and the submitted values are retained.
- [ ] Submitting with an invalid category re-renders the form with an error.
- [ ] Submitting with an invalid date re-renders the form with an error.
- [ ] Submitting without a description saves the expense with no error.
- [ ] Each row in the profile transaction table has an "Edit" link pointing to the correct URL.
