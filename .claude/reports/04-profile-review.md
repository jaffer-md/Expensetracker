# Review: Step 4 — Profile Page (Hardcoded UI)

**Plan reviewed:** `.claude/plans/04-profile.md`
**Spec:** `.claude/specs/04-profile.md`
**Files changed:** `app.py`, `templates/base.html`, `templates/profile.html` (new), `static/css/style.css`

## Summary

The implementation follows the plan and meets every spec requirement. Behavior was checked through Flask's test client against a temporary database. **The page was never viewed in a browser**, which matters for a step whose whole purpose is the UI layout. The main correctness risk is that every logged-in user sees the demo user's identity, by design for this step.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| 1. Hardcoded user, stats, transactions (5), categories (5) in `app.py` | Done | Totals are internally consistent: five rows sum to 340.99 and the percentages sum to 100. |
| 1. `inject_nav_user()` context processor, no DB query | Done | Returns the hardcoded name when `session["user_id"]` is set. |
| 1. `profile()` guard: redirect to `/login` if not logged in | Done | |
| 2. `base.html` shows name plus "Sign out" when logged in | Done | Logged-out links are unchanged. |
| 3. `profile.html` extends `base.html`, four sections in order | Done | No hex values, no `style=` attributes, all links via `url_for`. |
| 3. Badges and bar widths via CSS classes | Done | Width classes cover only the five hardcoded percentages. |
| 4. Profile CSS from `:root` variables, mobile rule | Done | No hex values in the appended block. |
| Verification on a temporary DB | Done | `spendly.db` unchanged. |

## Definition of Done (spec)

- [x] `/profile` logged out redirects to `/login` (302).
- [x] `/profile` logged in returns 200.
- [x] User card shows name and email.
- [x] Three summary stats shown (total spent, transactions, top category).
- [x] Transaction table has 5 rows.
- [x] Category breakdown has 5 categories.
- [x] Navbar shows the logged-in state (username and logout link).
- [x] No hex values in `profile.html`.

## Issues

1. **Every logged-in user sees the demo user's profile.** A newly registered user who logs in sees "Demo User", `demo@spendly.com`, and the demo's expenses, both on the page and in the navbar. This follows the spec's hardcoded-data rule, but it must not ship. Step 05 has to replace both `PROFILE_USER` and `inject_nav_user()` with lookups by `session["user_id"]`.
2. **Layout not visually verified.** Tests confirm content and status codes, not appearance. Spacing, badge contrast, the progress bars, and the mobile layout have not been looked at. Open `/profile` in a browser before treating the design as validated.
3. **Username link is hidden on phones.** The existing rule `.nav-links a:not(.nav-cta) { display: none; }` (below 600px) hides the name link, so mobile users see only "Sign out" and have no navbar route to `/profile`.
4. **Progress bars will not carry over to real data.** Bar widths come from fixed classes (`bar-w-35`, `bar-w-25`, ...), which only exist for today's five values. The spec forbids inline styles, so Step 05 needs either a full set of width classes (0–100) or a different approach, and it should be decided up front.
5. **Badge colours do not distinguish categories.** Seven category classes reuse three colour pairs: Food and Health match, Bills and Shopping match, Transport and Entertainment match. This respects the class-per-category rule but gives little visual separation.

## Minor observations

- `member_since` is a fixed string (`2026-11-20`), not the real `created_at`.
- Module-level data sits between routes in `app.py`. It is temporary, but Step 05 should remove it cleanly.
- Pre-existing hex values remain in `style.css` (lines 249, 250, 416). They predate this step and were not touched.
- `get_db` is still an unused import in `app.py`.
- Email case-sensitivity from Steps 2 and 3 is still open.
- No automated tests exist for any step so far.

## Verification gaps

- No browser or screenshot check (Issue 2).
- No live-server run.
- No tests added.

## Recommended next actions

1. Open the page in a browser and check desktop and mobile layouts.
2. In Step 05, derive user, stats, transactions, and categories from the session user, and remove the hardcoded dicts and the nav stub.
3. Pick a bar-width approach for real percentages before Step 05.
4. Decide whether the username link should stay visible on mobile.
