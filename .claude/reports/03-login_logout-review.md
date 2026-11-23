# Review: Step 3 — Login and Logout

**Plan reviewed:** `.claude/plans/03-login_logout.md`
**Spec:** `.claude/specs/03-login_logout.md`
**Files changed:** `database/db.py`, `app.py`, `templates/login.html`, `templates/register.html`, `static/css/style.css`

## Summary

The implementation follows the plan and meets every spec requirement. The plan's extra follow-up (the Step 2 success-flash bug) is also fixed. The main gap is not a spec miss: nothing in the UI links to `/logout`, and the navbar still looks the same for logged-in users.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| 1. `get_user_by_email()` in `db.py`, parameterized, returns row or `None` | Done | Connection closed in `finally`. The returned `Row` stays readable after close. |
| 2. `login()` GET and POST, generic error for every failure | Done | Missing field, unknown user, and wrong password all flash "Invalid email or password." |
| 2. `session["user_id"] = int(user["id"])`, redirect to `url_for("landing")` | Done | |
| 2. `abort(405)` for other methods | Done | Unreachable branch, kept for consistency with Step 2 and the spec's pattern. |
| 2. `logout()`: `session.clear()` then redirect to landing | Done | Stub string removed. |
| 3. `login.html` uses `url_for('login')`, flash loop, register link | Done | |
| 4. `.auth-success` style using CSS variables | Done | No hex values added. |
| 5. `register.html` renders flash by category | Done | Fixes Step 2 Issue 1. |
| Verification on a temporary DB | Done | `spendly.db` still has only the demo user. |

## Definition of Done (spec)

- [x] `GET /login` renders the form with email and password fields.
- [x] Demo credentials set `session["user_id"]` (int, value 1) and redirect to `/`.
- [x] Wrong password shows "Invalid email or password." and stays on the login page.
- [x] Unregistered email shows the same message.
- [x] `GET /logout` clears the session and redirects to `/`.
- [x] After logout, `user_id` is gone from the session.
- [x] `/logout` no longer returns the stub string.

## Issues

1. **No way to log out from the UI.** `templates/base.html` always shows "Sign in" and "Get started", even when `session["user_id"]` is set, and nothing links to `/logout`. A user can log in, but only by typing `/logout` can they log out. The spec does not list `base.html`, but the feature is not usable without it. Fix: show a "Sign out" link in the navbar when logged in (for example, via a context processor or `session.get("user_id")` in the template).
2. **Email case-sensitivity (carried over from Step 2).** `Demo@Spendly.com` fails to log in, and registration allows `A@x.com` next to `a@x.com`. Lowercasing in `create_user`, `get_user_by_email`, and the routes would fix both. Still open.

## Minor observations

- **Timing:** `check_password_hash` runs only when the user exists, so an unknown email returns slightly faster than a wrong password. This is a mild user-enumeration side channel. Hashing a dummy value for unknown users removes it.
- **Logout is a GET.** The spec requires it, so any page can log a user out with a link or an image tag.
- **Logged-in users can still open `/login` and `/register`.** The spec does not cover redirecting them.
- The flash-category conditional is copied into two templates. A shared macro would remove the duplication.
- `get_db` is still imported but unused in `app.py`.
- Dev-only secret key and no CSRF protection, as in Step 2.

## Verification gaps

- No live-server run. All checks used Flask's test client.
- No automated test file was added. The plan did not call for one.
- Verification did not exercise browser cookies end to end, only the test client's session.

## Recommended next actions

1. Add navbar awareness of the session (Issue 1) so users can sign out.
2. Decide on email normalization (Issue 2) before Step 4 builds on user lookups.
3. Optionally redirect logged-in users away from the auth pages and equalize login timing.
