# Review: Step 7 — Add Expense

**Plan reviewed:** `.claude/plans/07-add-expense.md`
**Spec:** `.claude/specs/07-add-expense.md`
**Files changed:** `app.py`, `database/queries.py`, `templates/profile.html`, `templates/base.html`, `static/css/style.css`
**Files created:** `templates/add_expense.html`, `tests/test_add_expense.py`

## Summary

The implementation follows the plan and meets every spec requirement. All 46 tests pass. However, probing edge cases the spec and tests do not cover turned up **two real bugs**. One lets a user make their own profile page return a 500 error. The other stores dates in a form that breaks date ordering and filtering. Both come from validation gaps in this step, and the first also exposes a weakness in the Step 5 percentage code. I recommend fixing both before moving on.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| 1. `insert_expense()`, parameterized, returns id, NULL description | Done | |
| 2. `CATEGORIES` tuple feeds validation and the select | Done | |
| 2. Login required for GET and POST | Done | Redirects to `/login`. |
| 2. Validation order: amount, category, date, description | Done | Re-renders with values kept, status 200. |
| 2. Reject `inf`/`nan` and descriptions over 200 characters | Done | Both added beyond the spec. |
| 2. Success redirects to `url_for("profile")` | Done | |
| 3. `add_expense.html` with the four fields, cancel link, flash block | Done | |
| 4. "Add Expense" button on the profile page | Done | |
| 5. "Add Expense" navbar link when logged in | Done | |
| 6. CSS from variables only | Done | |
| 7. Tests per the spec plus extras | Done | 20 new tests. |

## Definition of Done (spec)

- [x] Logged-out visit redirects to `/login`.
- [x] Logged-in visit shows amount, category, date, and description fields.
- [x] The dropdown has exactly the seven categories.
- [x] A valid submission redirects to `/profile` and appears in the list.
- [x] Missing or zero amount re-renders with an error and keeps the entered values.
- [x] Invalid category re-renders with an error.
- [x] Invalid date re-renders with an error.
- [x] No description saves without error.
- [x] The profile "Add Expense" button goes to `/expenses/add`.
- [x] The navbar shows "Add Expense" when logged in.

## Issues

1. **One large amount breaks the profile page with a 500 (bug).** There is no upper bound on `amount`. I submitted `1e308` (a finite number, so it passes the `isfinite` check). The expense saved, and every later `/profile` request failed with `OverflowError: cannot convert float infinity to integer`, from the percentage calculation in `get_category_breakdown` (`amount * 100` overflows to infinity). Adding a second huge amount made the total infinite and caused a `TypeError` and a `ValueError` on the same page. The user cannot recover from the UI. This ran against a temporary database. `spendly.db` was not touched. Fix: cap `amount` to a sensible maximum in the route, and make the percentage code tolerate extreme values.
2. **Non-normalized dates are stored as typed (bug).** `strptime` accepts `2026-3-5`, and the route stores the original string. The result is a row dated `2026-3-5`. That breaks the project rule that dates are always `YYYY-MM-DD`, and it sorts and filters wrongly, because dates are compared as text (`2026-3-5` sorts after `2026-11-01`). Browser date pickers send padded dates, so this affects hand-written requests, but the rule is meant to hold at the server. Fix: store `parsed_date.isoformat()`, not the input string. This also resolves year-`0001` and year-`9999` oddities, which are accepted today.
3. **Amounts keep unlimited decimals.** `0.001` passes server validation (the browser's `min="0.01"` is bypassable) and is stored as `0.001`, which displays as ₹0.00. `50.129` is stored unrounded, so displayed rows can disagree with the displayed total by a paisa. Fix: reject below 0.01 and round to two decimals before saving.

## Minor observations

- Double-clicking "Save Expense" (or two quick POSTs) creates duplicate rows. I confirmed two POSTs gave two rows. No protection exists. A disabled-on-submit button would reduce it.
- Future dates are accepted, as planned. This interacts with the Step 6 "This Month" window (it ends today), so future-dated rows are hidden there.
- No CSRF protection (not in the spec).
- `1e3` is accepted as `1000.0`. This is standard `float()` behavior but may surprise users.
- User-supplied descriptions are HTML-escaped on the profile page, as expected.
- Still open from earlier steps: email case-sensitivity, repeated user lookups per request, mobile username link, badge colours, unused `get_db` import in `app.py`.

## Test coverage gaps

- No test for the huge-amount case (Issue 1), for date normalization (Issue 2), or for sub-paisa and over-precise amounts (Issue 3). Each would have caught the bugs above.

## Verification gaps

- The pages were not viewed in a browser, so the new form, the profile heading with its button, and the navbar spacing are unseen.
- `spendly.db` is unchanged: 2 users and 8 expenses.

## Recommended next actions

1. Fix Issue 1: set an upper limit on `amount` and harden the percentage calculation.
2. Fix Issue 2: store the ISO-formatted parsed date.
3. Fix Issue 3: require at least 0.01 and round to two decimals.
4. Add tests for all three.
5. Open `/expenses/add` and `/profile` in a browser, desktop and mobile.
