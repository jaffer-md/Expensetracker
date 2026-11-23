# Review: Step 6 — Date Filter for Profile Page

**Plan reviewed:** `.claude/plans/06-date-filter-profile.md`
**Spec:** `.claude/specs/06-date-filter-profile.md`
**Files changed:** `database/queries.py`, `app.py`, `templates/profile.html`, `static/css/style.css`, `tests/test_backend_connection.py` (one assertion tightened)
**Files created:** `tests/test_date_filter.py`

## Summary

The implementation follows the plan and meets the spec. All 26 tests pass. I also probed edge cases that the tests do not cover (script injection in the date parameter, same-day ranges, impossible dates, unpadded dates, one-sided ranges, extreme years), and the page handled all of them without errors. The remaining items are small design and coverage gaps, none of them blocking.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| 1. Optional `date_from`/`date_to` on the three helpers, `BETWEEN ? AND ?` | Done | A shared `_date_clause()` builds the fragment. Only parameters carry values, and nothing is formatted into SQL. Both bounds are needed to filter. |
| 1. Unfiltered behavior unchanged | Done | The Step 5 tests pass untouched. |
| 2. Validation with `strptime`, bad or missing value means no filter | Done | `_parse_iso_date()`. A single present bound also falls back to unfiltered. |
| 2. Start after end: flash and fall back | Done | The message renders once and is cleared on the next load. |
| 2. Presets computed in `app.py`, links via `url_for` | Done | "All Time" produces a clean `/profile`. Month arithmetic clamps to month end. |
| 3. Filter bar above stats, active states, pre-filled custom form | Done | Flashed messages are now rendered on the profile page. |
| 4. Filter styles from CSS variables | Done | Added to `style.css`, not `profile.css` (a documented decision in the plan). |
| Tests listed in the plan | Mostly done | One planned case is missing (see Gap 1). |

## Definition of Done (spec)

- [x] No parameters matches Step 5 (all 8 expenses, ₹388.49).
- [x] "This Month" filters all three sections. See Issue 1 on its end date.
- [x] "Last 3 Months" and "Last 6 Months" use windows ending today (from 2026-08-19 and 2026-05-19 on 2026-11-19).
- [x] "All Time" removes the filter (clean URL, shown active when unfiltered).
- [x] A valid custom range filters stats, transactions, and categories (checked: 5 to 10 Nov gives ₹200.00 and three rows).
- [x] Reversed range flashes the error and shows the unfiltered view.
- [x] Malformed dates return 200 and fall back silently.
- [x] The active preset, or the custom form, is highlighted.
- [x] Amounts keep the ₹ symbol.
- [x] An empty range shows ₹0.00, 0 transactions, and no categories.

## Issues

1. **"This Month" ends today, not at month end.** The range is the first of the month to today. Expenses dated later in the current month (possible once Step 7 allows future dates) are hidden by "This Month", even though the spec says "the current calendar month only". Ending at the last day of the month would match the wording. "Last 3/6 Months" correctly end today, per the spec.
2. **Preset highlight goes stale after midnight.** Preset links bake in today's date. A bookmarked "This Month" link opened tomorrow no longer matches the computed range, so the page highlights the custom form instead of the preset. The data shown is still correct.
3. **Transaction table is capped at 10 rows while the stats are not.** A filtered range with 25 expenses shows "Transactions: 25" next to a 10-row table. This predates Step 6 but is more visible with filtering.

## Minor observations

- Filling in only one date and clicking Apply resets the form silently, with no message. That matches the spec's "silent fallback", but it may confuse users.
- `strptime` accepts unpadded dates (`2026-1-5`). They are normalized to `2026-01-05`, which is harmless.
- The profile route is now about 55 lines. The preset and active-state logic could move into a helper.
- The flash on the profile page reuses `.auth-error`, a class named for the login pages.
- `tests/test_date_filter.py` imports `database.db` without using it.
- Still open from earlier steps: username link hidden on phones, badge colours that do not distinguish categories, email case-sensitivity, repeated user lookups per request, and unused `get_db` import in `app.py`.

## Verification gaps

- **Gap 1:** the plan listed "This Month includes all 8 seed rows". No test checks that. The test I wrote only checks that the preset is highlighted, because "this month" depends on the real date.
- **Gap 2:** I never viewed the page in a browser. The filter bar layout, the active styling, and the mobile layout are unseen.
- **Gap 3:** the only live-server check was an unauthenticated request (302). I did not load a filtered page on the running server.
- `spendly.db` is unchanged: 2 users and 8 expenses (the second user, `jaffer`, was created outside these tests).

## Recommended next actions

1. Decide whether "This Month" should run to the end of the month (Issue 1).
2. Open `/profile` in a browser, with and without a range, and check desktop and mobile.
3. Add a test for the "This Month" row count that freezes the date.
4. Consider a note when the table is capped, or a "showing 10 of N" label.
