# Review: Step 5 — Backend Routes for Profile Page

**Plan reviewed:** `.claude/plans/05-backend-routes-for-profile-page.md`
**Spec:** `.claude/specs/05-backend-routes-for-profile-page.md`
**Files changed:** `app.py`, `templates/profile.html`, `static/css/style.css`
**Files created:** `database/queries.py`, `tests/conftest.py`, `tests/test_backend_connection.py`

## Summary

The implementation follows the plan. The profile page and navbar now read from the database, and all 14 tests pass. One open item is a spec error: it states a total of ₹346.24, but the seed data sums to ₹388.49, so the spec's Definition of Done cannot be met literally. The code is otherwise sound, with a few minor inconsistencies listed below.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| 1. `get_user_by_id` returns `name`, `email`, `member_since` ("Month YYYY") or `None` | Done | Parsed from `created_at`. |
| 1. `get_summary_stats`: total, count, top category, zeros and "—" when empty | Done | Top-category tie-break is alphabetical, so it is deterministic. |
| 1. `get_recent_transactions(user_id, limit=10)` newest first | Done | `ORDER BY date DESC, id DESC`. |
| 1. `get_category_breakdown`, integer `pct` summing to 100 | Done | The largest category absorbs the rounding remainder. |
| 1. Parameterized SQL, connection closed in `finally`, no Flask imports | Done | |
| 2. `app.py`: remove `PROFILE_*`, real data in `profile()` and the nav processor | Done | A stale session (user deleted) clears the session and redirects to `/login`. |
| 3. Template: `₹` with two decimals, `bar-w-{{ c.pct }}` | Done | No hex values or inline styles. |
| 4. CSS `bar-w-0` to `bar-w-100` | Done | Replaced the five Step 4 classes. |
| 5. `tests/conftest.py` with temp DB fixture | Done | Tests never touch `spendly.db`. |
| 6. `tests/test_backend_connection.py` covering the spec table | Done | 14 tests, all passing. |
| Verification: `spendly.db` unchanged | Partly done | I checked row counts (1 user, 8 expenses), not a checksum as planned. |

## Definition of Done (spec)

- [x] Demo login shows "Demo User" and "demo@spendly.com" from the database.
- [ ] Total spent equals ₹346.24. **Not achievable**: the real total is ₹388.49 (see Issue 1).
- [x] Transaction count is 8.
- [x] Top category is "Bills".
- [x] Eight rows, newest date first.
- [x] Seven categories, percentages sum to 100.
- [x] All amounts show ₹.
- [x] A new user sees ₹0.00, 0 transactions, and an empty breakdown without errors.

## Issues

1. **Spec total is wrong, and still uncorrected.** The spec says ₹346.24 (in the route tests and DoD). The seed expenses sum to 388.49. The plan asked you to confirm this, and the spec file was not changed. Anyone checking the DoD literally will see a mismatch. Fix: change the spec to 388.49.
2. **Inconsistent currency formatting.** The "Total spent" tile uses thousands separators (`₹1,234,567.50`), while table rows and category amounts do not (`₹1234567.50`). Verified with a large test expense. Fix: use one format everywhere, for example a shared Jinja filter.
3. **Repeated user lookups.** The nav context processor runs `get_user_by_id` on every template render, and `profile()` calls it again. One profile request opens about six connections. Harmless at this size. A request-scoped cache would remove the repetition.

## Minor observations

- Two route tests are weak. `">8<"` can match unrelated markup, and `"Bills" in html` is already satisfied by the table, so it does not prove the top-category tile.
- `get_user_by_id` assumes `created_at` is exactly `YYYY-MM-DD HH:MM:SS`. A different format would raise `ValueError`. That holds for everything the app writes today.
- `get_db` is still an unused import in `app.py`.
- Edge cases checked and fine: a single-word name gives one initial, user names are HTML-escaped, and a stale session redirects cleanly.

## Carry-overs from earlier reviews

- Resolved: hardcoded demo identity (Step 4 Issue 1) and fixed bar-width classes (Step 4 Issue 4).
- Still open: username link hidden on phones (Step 4 Issue 3), badge colours that do not distinguish categories (Step 4 Issue 5), and email case-sensitivity (Steps 2 and 3).

## Verification gaps

- No browser or live-server check. Rendering of the real-data page and the 101 bar classes is unseen.
- No checksum comparison of `spendly.db`.

## Recommended next actions

1. Correct the spec's expected total to 388.49.
2. Unify currency formatting with one filter.
3. Tighten the two weak route assertions.
4. Look at `/profile` in a browser, including mobile.
