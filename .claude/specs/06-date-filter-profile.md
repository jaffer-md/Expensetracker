# Spec: Step 6 — Date Filter for Profile Page

## Overview

- Adds a date-range filter to the existing `/profile` route, so users can narrow the transaction list, summary stats, and category breakdown to a specific period.
- The filter is driven entirely by query-string parameters, `date_from` and `date_to`, on `GET /profile`. No new routes are required.
- A compact filter bar provides four quick-select preset buttons: "This Month", "Last 3 Months", "Last 6 Months", and "All Time".
- The filter bar also has two `<input type="date">` fields, so users can pick any custom range.
- All three data sections (summary stats, recent transactions, and category breakdown) must respect the active date filter.

## Depends on

- Step 01 — Database Setup. The `expenses` table, with its `date` column, must exist.
- Step 04 — Profile Page UI. The template with all four sections must exist.
- Step 05 — Backend Connection. `get_summary_stats`, `get_recent_transactions`, and `get_category_breakdown` in `database/queries.py` must exist and be wired to the `/profile` route.

## Routes

- No new routes.
- The existing `GET /profile` route is modified to read two optional query parameters:
  - `date_from` — an ISO date string (`YYYY-MM-DD`), inclusive lower bound.
  - `date_to` — an ISO date string (`YYYY-MM-DD`), inclusive upper bound.
- If either parameter is absent or malformed, the route falls back to an unfiltered "All Time" view. It never returns an error because of these parameters.

## Database changes

- No database changes.
- The `expenses.date` column (`TEXT`, `YYYY-MM-DD`) already supports `BETWEEN` comparison in SQLite.

## Templates

- Modify `templates/profile.html`:
  - Add a filter bar section above the summary stats row. It contains:
    - Four quick-select preset buttons: "This Month", "Last 3 Months", "Last 6 Months", and "All Time".
      - Each button is a link to `/profile` with the appropriate `date_from` and `date_to` query parameters, computed in `app.py`.
      - "All Time" passes no query parameters, so it produces a clean `/profile` URL.
    - A custom range sub-form with two `<input type="date">` fields (`date_from` and `date_to`) and an "Apply" submit button.
    - An active state on the currently selected preset button, or on the custom range fields when a custom range is active.
  - No structural changes to any existing section. Only the Jinja variables fed into them change when a filter is active.

## Files to change

- `app.py`:
  - In the `profile()` view, read `date_from` and `date_to` from `request.args`.
  - Validate that both values are well-formed ISO dates using `datetime.strptime(value, "%Y-%m-%d")`. On a `ValueError`, treat the value as absent.
  - If `date_from` is later than `date_to` after validation, treat both as absent and flash "Start date must be before end date."
  - Compute the preset date ranges (for example, the first day of the current month for "This Month") in `app.py`, not in the template.
  - Pass the validated `date_from` and `date_to`, along with the preset URL parameters, to the template, so the filter bar can show the active state.
  - Pass `date_from` and `date_to` to each of the three query helpers.
- `database/queries.py`:
  - `get_summary_stats(user_id, date_from=None, date_to=None)`: when both bounds are provided, add `AND date BETWEEN ? AND ?` to the expense queries. When they are absent, behave exactly as in Step 05 (unfiltered).
  - `get_recent_transactions(user_id, limit=10, date_from=None, date_to=None)`: same pattern. Newest-first ordering and the limit are unchanged.
  - `get_category_breakdown(user_id, date_from=None, date_to=None)`: same pattern. The percentage calculation is unchanged.
- `templates/profile.html`: add the filter bar, as described in "Templates".
- `static/css/profile.css`: add styles for the filter bar and the active-preset button state. Use CSS variables only.

## Files to create

- None.

## New dependencies

- None.

## Rules for implementation

- No SQLAlchemy or ORMs. Raw `sqlite3` only, via `get_db()`.
- Parameterised queries only. Never string-format dates into SQL. Use `?` placeholders for the date-range bounds as well.
- Validate dates in `app.py` with `datetime.strptime(value, "%Y-%m-%d")`. On a `ValueError`, treat the parameter as absent, which means no filter.
- Preset links must be generated with `url_for("profile", ...)`, passing the date parameters. Never hardcode URL strings in the template.
- When `date_from` and `date_to` are both absent, all three query helpers must behave exactly as they did in Step 05 (unfiltered).
- If `date_from` is later than `date_to` after validation, treat both as absent and flash "Start date must be before end date."
- The "All Time" preset passes no query parameters, so it produces a clean `/profile` URL.
- Preset date calculations are done in `app.py`, not in the template.
- Use CSS variables. Never hardcode hex values.
- No inline styles.
- All templates extend `base.html`.
- Use `url_for()` for every internal link. Never hardcode paths.

## Definition of done

- [ ] Visiting `/profile` with no query parameters returns the same data as Step 05 (unfiltered, all expenses).
- [ ] Clicking "This Month" filters all three sections to the current calendar month only.
- [ ] Clicking "Last 3 Months" filters to expenses in the 3-month window ending today.
- [ ] Clicking "Last 6 Months" filters to expenses in the 6-month window ending today.
- [ ] Clicking "All Time" removes any active filter and shows all expenses.
- [ ] Submitting a custom date range with valid `date_from` and `date_to` shows only expenses within that range in all three sections.
- [ ] Submitting a range where `date_from` is later than `date_to` shows a flash error and falls back to the unfiltered view.
- [ ] Submitting a malformed date string (for example, `date_from=not-a-date`) does not crash the app. It silently falls back to the unfiltered view.
- [ ] The active preset button, or the custom range fields, visually indicate which filter is currently applied.
- [ ] All amounts continue to display the ₹ symbol regardless of the active filter.
- [ ] A user with no expenses in the selected range sees ₹0.00 total spent, 0 transactions, and an empty category breakdown, with no errors.
