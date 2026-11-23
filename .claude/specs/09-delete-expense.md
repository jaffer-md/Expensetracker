# Spec: Step 9 — Delete Expense

## Overview

- Lets a logged-in user permanently delete one of their own expenses directly from the profile transaction table.
- A "Delete" button per row submits a `POST` request to `/expenses/<id>/delete`.
- The handler verifies ownership, removes the row from the database, and redirects back to `/profile`.
- There is no separate confirmation page. A browser-side `confirm()` dialog in the button's `onclick` handler is used to prevent accidental deletions.
- The existing `get_expense_by_id` helper from Step 8 is reused for ownership verification. No new lookup functions are needed.
- Only one new mutation helper is added: `delete_expense` in `database/queries.py`.

## Depends on

- Step 01 — Database Setup. The `expenses` table exists.
- Step 03 — Login and Logout. `session["user_id"]` is set and enforced.
- Step 05 — Profile page. The profile page renders transactions, and the delete button lives there.
- Step 08 — Edit Expense. `get_expense_by_id` is available, and the Actions column already exists in the profile transactions table.

## Routes

- `POST /expenses/<int:id>/delete` — verifies ownership, deletes the expense row, and redirects to `/profile`. Logged-in only.
- There is no `GET` handler. A bare `GET` to this URL must return 405.

## Database changes

- No new tables or columns.
- The `expenses` table already has all required columns.

## Templates

- Modify `templates/profile.html`:
  - Inside the existing "Actions" cell for each transaction row, add a delete form.
  - The form has:
    - `method="POST"` and an action of `/expenses/{{ tx.id }}/delete`.
    - `style="display:inline"`. This is the one permitted exception to the no-inline-styles rule, because it is a layout-utility value only, not a design value.
    - `onsubmit="return confirm('Delete this expense?')"`, to ask for browser-side confirmation before submission.
    - A `<button type="submit">` with `class="btn-delete"` and the label "Delete".
  - The "Edit" link from Step 8 stays alongside the new "Delete" button.

## Files to change

- `database/queries.py`:
  - Add `delete_expense(expense_id, user_id)`.
  - It issues a parameterised `DELETE FROM expenses WHERE id = ? AND user_id = ?`.
  - The dual-column `WHERE` clause is the ownership guard.
  - It commits and closes the connection before returning.
- `app.py`:
  - Import `delete_expense` from `database.queries`.
  - Replace the GET-only placeholder at `/expenses/<int:id>/delete` with a POST-only handler:
    - Guard: redirect to `/login` if the user is not authenticated.
    - Call `get_expense_by_id(id, session["user_id"])`. If it returns `None`, call `abort(404)`.
    - Call `delete_expense(id, session["user_id"])`.
    - Redirect to `url_for("profile")`.
  - The route decorator must be `@app.route("/expenses/<int:id>/delete", methods=["POST"])`.
- `templates/profile.html`: add the delete form inside the existing "Actions" cell.
- `static/css/style.css`: add a `.btn-delete` style that uses a CSS variable for the danger colour, for example a red-toned variable. Never hardcode hex values.

## Files to create

- `tests/test_delete_expense.py`

## New dependencies

- None.

## Rules for implementation

- No SQLAlchemy or ORMs. Raw `sqlite3` only, via `get_db()`.
- Parameterised queries only. Never string-format values into SQL.
- `PRAGMA foreign_keys = ON` must be enabled on every connection (already handled in `get_db()`).
- `delete_expense` must scope its `DELETE` to `id = ? AND user_id = ?`. This is the ownership guard that prevents one user from deleting another user's expense.
- The route accepts only `POST`. A bare `GET` to the URL must return 405.
- Unauthenticated access must redirect to `/login` (302).
- If the expense does not exist or belongs to another user, return 404.
- After a successful deletion, redirect to `url_for("profile")`. Do not render a template.
- The only permitted inline style is `style="display:inline"` on the `<form>` tag. No hex colours or design values may be inlined anywhere.
- Use CSS variables. Never hardcode hex values.
- All templates extend `base.html`.
- Currency must always display as ₹. Never £ or $.
- Use `url_for()` for every internal link. Never hardcode paths.

## Tests to write

- File: `tests/test_delete_expense.py`.
- Unit tests:

| Function | Input | Expected output |
|---|---|---|
| `delete_expense` | Valid `expense_id` and correct `user_id` | The row is removed from the database |
| `delete_expense` | Valid `expense_id` and wrong `user_id` | The row remains in the database (0 rows deleted, no error raised) |
| `delete_expense` | Non-existent `expense_id` | No error raised; the database is unchanged |

- Route tests:
  - `POST /expenses/<id>/delete` unauthenticated redirects to `/login` (302).
  - `POST /expenses/<id>/delete` authenticated, own expense, redirects to `/profile` (302), and the row no longer exists in the database.
  - `POST /expenses/<id>/delete` authenticated, other user's expense, returns 404, and the row still exists in the database.
  - `POST /expenses/<id>/delete` authenticated, non-existent id, returns 404.
  - `GET /expenses/<id>/delete` for any user returns 405 (Method Not Allowed).

## Definition of done

- [ ] `POST /expenses/<id>/delete` while logged out redirects to `/login`.
- [ ] `POST` to `/expenses/<id>/delete` for a non-existent or another user's expense returns 404.
- [ ] `GET /expenses/<id>/delete` returns 405.
- [ ] Clicking "Delete" on a transaction row and confirming in the browser dialog removes that expense from the database.
- [ ] After deletion, the user is redirected to `/profile`, and the deleted expense no longer appears in the transaction list.
- [ ] Cancelling the browser `confirm()` dialog does not submit the form, and leaves the expense intact.
- [ ] Each transaction row in the profile table shows both "Edit" and "Delete" actions.
