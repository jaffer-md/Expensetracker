# Review: Step 2 — User Registration

**Plan reviewed:** `.claude/plans/02-registration.md`
**Spec:** `.claude/specs/02-registration.md`
**Files changed:** `database/db.py`, `app.py`, `templates/register.html`

## Summary

The implementation follows the plan and meets every spec requirement. One real bug sits in the success-flash flow, and one gap affects the "no duplicate user" goal. Neither was called out in the plan.

## Plan vs. implementation

| Plan step | Status | Notes |
|---|---|---|
| 1. `create_user()` in `db.py`, parameterized, returns id, lets `IntegrityError` propagate | Done | Connection closed in `finally`. |
| 1. Shared `PASSWORD_HASH_METHOD` constant | Done | Also used by `seed_db()`. |
| 2. `app.secret_key` hardcoded dev string | Done | |
| 2. `register()` handles GET and POST, spec validation order | Done | Empty fields, then password match, then duplicate email via `IntegrityError`. |
| 2. Failures flash and re-render with 200, no redirect, no insert | Done | |
| 2. Success flashes and redirects to `url_for('login')` | Done | |
| 2. `abort(405)` for other methods | Done | The branch is unreachable because Flask rejects other methods first. Kept because the spec asks for it. |
| 3. Form uses `url_for('register')`, `method="post"` | Done | |
| 3. `name` attributes plus `confirm_password` input | Done | |
| 3. Flashed messages in existing `.auth-error` style, no new CSS/hex | Done | No hex values added. |
| Verification on a temporary DB | Done | `DB_PATH` was redirected, so `spendly.db` was untouched. |

## Definition of Done (spec)

- [x] `GET /register` renders without errors (200, all four named inputs).
- [x] Valid submission creates a user and redirects to `/login` (302).
- [x] Mismatched passwords re-render with an error and make no insert.
- [x] Duplicate email re-renders with "Email already registered."
- [x] Any empty field re-renders with a validation error.
- [x] Password stored as a hash (`pbkdf2:sha256...`), verified on the temp DB. `spendly.db` itself has no registered users yet, so I did not inspect a registered row there.
- [x] Repeated valid submissions with the same email create no second row.

## Issues

1. **Success message shows as a red error (bug).** `register.html` renders every flashed message in `.auth-error`, regardless of category. After a successful signup the user lands on `/login`, which does not render flashes yet, so "Account created. Please sign in." stays queued. If the user then clicks "Get started", `/register` displays that message in the red error box. Fix: render by category (for example, a success class) in `register.html`, and show flashes in `login.html` in Step 3.
2. **Email uniqueness is case-sensitive.** `A@x.com` and `a@x.com` are treated as different emails, so one person can register twice. The spec's duplicate rule is met literally, but the intent of "no duplicate user" is not. Fix: lowercase the email before validation and insert, which also helps Step 3 login.

## Minor observations

- Form fields are not repopulated after an error, so the user retypes name and email.
- Password is not stripped, so a whitespace-only password passes the non-empty check.
- No CSRF protection. The spec does not ask for it.
- `get_db` is imported in `app.py` but unused (carried over from Step 1).
- `static/css/style.css` has a hardcoded `#f5c6c2` in `.auth-error`. This predates Step 2 and was not changed.
- The "Min. 8 characters" placeholder is not enforced. The spec does not require it.

## Verification gaps

- No live-server run (`python app.py`). Everything was tested through Flask's test client.
- No automated test file was added. The plan did not call for one.

## Recommended next actions

1. Fix Issue 1 by rendering flash categories in `register.html`, then render flashes in `login.html` during Step 3.
2. Fix Issue 2 by lowercasing the email in the route.
3. Optionally repopulate name and email on validation errors.
