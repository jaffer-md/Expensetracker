# Review: Step 9 — Delete Expense

**Plan reviewed:** `.claude/plans/09-delete-expense.md`
**Spec:** `.claude/specs/09-delete-expense.md`
**Files changed:** `database/queries.py`, `app.py`, `templates/profile.html`, `static/css/style.css`
**Files created:** `tests/test_delete_expense.py`

## Summary

The implementation follows the plan and meets every spec requirement. All 82 tests pass. Ownership is enforced twice (a lookup that returns 404, and a `DELETE` scoped to the owner), and probing found no way to delete another user's row. The main concern is not a spec miss: a destructive, irreversible action is protected by no CSRF token, and the session cookie has no explicit `SameSite` setting.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| Decision 1: view renamed to `delete_expense_route` | Done | No leftover references to the old endpoint name in code or templates. |
| Decision 2: ownership lookup first, then scoped delete | Done | Also returns 404 if the delete removes 0 rows. |
| Decision 3: inline style limited to `display:inline` | Done | One `style=` in the template, on the delete form only. |
| 1. `delete_expense(expense_id, user_id)`, parameterized, returns row count | Done | |
| 2. POST-only route, login redirect, 404, redirect to profile | Done | GET, HEAD, PUT, and DELETE verbs all return 405. |
| 3. Delete form in the Actions cell, `confirm()` on submit | Done | The Edit link stays beside it. |
| 4. `.btn-delete` from the `--danger` variable | Done | No hex values. |
| 5. Tests from the spec plus profile checks | Done | 10 new tests. |

## Definition of Done (spec)

- [x] Logged-out POST redirects to `/login`.
- [x] POST for a missing or foreign expense returns 404.
- [x] GET returns 405.
- [x] Confirmed Delete removes the row from the database.
- [x] After deletion the user lands on `/profile` and the expense is gone from the list.
- [ ] Cancelling the `confirm()` dialog leaves the expense intact. **Not tested**: this is browser behavior, and only the `onsubmit` attribute is asserted.
- [x] Each row shows Edit and Delete.

## Issues

1. **No CSRF protection on an irreversible action.** Any page could submit a cross-site POST to `/expenses/<id>/delete` for a logged-in user. The session cookie is `HttpOnly` but has no `SameSite` attribute (checked in the response header). Modern browsers treat a missing attribute as Lax, which blocks most cross-site POSTs, but that is the browser's default and not something the app guarantees. The spec does not ask for a token. Fix: set `SESSION_COOKIE_SAMESITE = "Lax"` at minimum, and consider CSRF tokens across all forms (register, login, add, edit, delete).
2. **Deleting twice shows a bare 404.** The first delete returns 302, and a repeat (double-click, back button, resubmit) returns Flask's default Not Found page. It is correct per the spec but confusing. A friendly message or a redirect to the profile would be better.

## Minor observations

- Deleting from a filtered profile returns to the unfiltered view. This is the same gap as Step 8 and was left so both can be fixed together.
- With JavaScript disabled, the `confirm()` prompt does not run and the delete goes through immediately. This is inherent to the spec's design.
- When a user deletes every expense, the profile shows ₹0.00, 0, "—", and an empty table with no explanatory message.
- There is no undo, as specified ("permanently delete").
- The delete button is visually small, which may be hard to tap on a phone. This has not been looked at in a browser.
- Still open from earlier steps: email case-sensitivity, repeated user lookups per request, mobile username link hidden, repeated badge colours, unused `get_db` import in `app.py`.

## Verification gaps

- The profile page was not viewed in a browser, so the Actions column layout and the delete button styling are unchecked.
- The `confirm()` behavior (cancel keeps the row) was not exercised.
- Live-server check was limited to a GET returning 405.
- `spendly.db` is unchanged: 2 users and 8 expenses totalling 388.49.

## Recommended next actions

1. Set `SESSION_COOKIE_SAMESITE = "Lax"`, and decide whether to add CSRF tokens to all forms (Issue 1).
2. Make a repeated delete redirect with a message instead of a bare 404 (Issue 2).
3. Carry the date filter through the Edit and Delete flows.
4. Check `/profile` in a browser, desktop and mobile, and try the confirm dialog by hand.
