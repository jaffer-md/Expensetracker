# Review: Step 8 — Edit Expense

**Plan reviewed:** `.claude/plans/08-edit-expense.md`
**Spec:** `.claude/specs/08-edit-expense.md`
**Files changed:** `app.py`, `database/queries.py`, `templates/profile.html`, `static/css/style.css`, `tests/conftest.py`, `tests/test_backend_connection.py`
**Files created:** `templates/edit_expense.html`, `tests/test_edit_expense.py`

## Summary

The implementation follows the plan and meets every spec requirement. All 72 tests pass. Ownership is enforced at both the query and the route level, and the Step 7 bugs from the last review are fixed in a shared validator that both Add and Edit now use. My probing found no security or data-integrity problems. The remaining items are UX and consistency points.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| Decision 1: shared `_validate_expense_form()` with hardening | Done | Amount limits, two-decimal rounding, normalized dates. Add Expense now uses it too. |
| Decision 2: 404 for ownership failures, login redirect first | Done | |
| Decision 3: `url_for` for edit links | Done | |
| 1. `get_recent_transactions` returns `id` | Done | |
| 1. `get_expense_by_id` scoped by `id` and `user_id` | Done | |
| 1. `update_expense` scoped by `id` and `user_id`, returns row count | Done | |
| 2. GET/POST route, 404 on missing or foreign expense | Done | Returns 404 if the row vanished between the lookup and the update. |
| 2. Failed POST re-renders with submitted values | Done | |
| 3. `edit_expense.html` with pre-filled fields and Cancel link | Done | Generated from `add_expense.html`, with the form action built by `url_for`. |
| 4. "Actions" column and per-row Edit link | Done | |
| 5. Row action styling from variables | Done | |
| 6. Tests from the spec plus hardening cases | Done | Includes a check that the other user's row is unchanged. |

## Definition of Done (spec)

- [x] Logged-out visit redirects to `/login`.
- [x] Another user's or a missing expense returns 404.
- [x] Logged-in GET shows the pre-filled form.
- [x] The category select has the correct option selected.
- [x] A valid change redirects to `/profile` and appears in the table.
- [x] Missing or zero amount re-renders with an error and keeps the submitted values.
- [x] Invalid category re-renders with an error.
- [x] Invalid date re-renders with an error.
- [x] A blank description saves as NULL without error.
- [x] Each profile row links to its own edit URL.

## Issues

1. **Editing from a filtered profile loses the filter.** A user on `/profile?date_from=…&date_to=…` clicks Edit, saves, and lands on the unfiltered profile. The filter is not carried through the edit link or the redirect. Fix: pass the current filter as query parameters to the edit link, and redirect back with them. This is a UX gap, not a bug in the data.
2. **Deleting is still a placeholder, and the Edit form's failures aren't visible from the table.** `/expenses/<id>/delete` still returns a stub string with status 200. That's correct for this step, but a user following the profile could reach it. This is expected until Step 9.
3. **404 responses use Flask's default page.** Foreign or missing ids get a plain "Not Found" page instead of a styled one. The spec only asks for 404, so this is cosmetic.

## Minor observations

- The edit form does not show the expense's original values anywhere, so a user who has typed over them and submitted an error cannot see what they were. The spec asks for the submitted values, so this is by design.
- The Step 7 `add_expense` error and the Step 8 edit error use the same `auth-error` styling, which is fine but it is a class named for login pages (noted in the Step 6 review).
- The `amount` input `value` is formatted with two decimals in GET but not in the re-render path, so a user who types `12.5` sees `12.5` back. Harmless.
- `tests/conftest.py` now pins seed dates to 2026-11 values. This changes the fixture the Step 5 and 6 tests use. It fixed a real flake (the seed clamps dates to the current day-of-month), but it is a change outside the plan, and it was disclosed in the chat.
- Still open from earlier steps: email case-sensitivity, repeated user lookups per request, mobile username link hidden, badge colours that repeat across categories, and the unused `get_db` import in `app.py`.

## Verification gaps

- The new pages were not viewed in a browser, so the layout of the edit form and the Actions column is unchecked.
- Live-server check was an unauthenticated request only (302).
- `spendly.db` is unchanged: 2 users and 8 expenses totalling 388.49.

## Recommended next actions

1. Carry the date filter through the Edit link and the save redirect (Issue 1).
2. Open `/profile` and `/expenses/<id>/edit` in a browser, desktop and mobile.
3. Leave deletion for Step 9, as planned.
