# Spec: Step 3 — Login and Logout

## Overview

- Converts the `/login` stub into a functional handler that accepts both `GET` and `POST`.
- On `POST`, the handler:
  - Verifies the submitted credentials against the `users` table.
  - Stores the authenticated user's id in `session["user_id"]`.
  - Redirects to the landing page, until a dashboard route exists.
- Implements `/logout`, which clears the session and redirects to `/`.
- After this step, the app can distinguish logged-in users from guests.
- This step is a prerequisite for all expense features.

## Depends on

- Step 01 — Database Setup. The `users` table must exist.
- Step 02 — Registration. `create_user()` and password hashing must be in place, and a user must exist to log in against.

## Routes

- `GET /login` — renders the login form. Public.
- `POST /login` — validates credentials, sets the session, and redirects. Public.
- `GET /logout` — clears the session and redirects to `/`. Public. No login required.

## Database changes

- No database changes.
- The `users` table from Step 01 already stores `email` and `password_hash`.
- Add one new helper to `database/db.py`: `get_user_by_email(email)`.
  - Queries the `users` table by email.
  - Returns the matching user row, or `None` if not found.
  - Lives in `database/db.py`, not inline in the route.

## Templates

- Modify `templates/login.html`:
  - Add a `POST` form with `email` and `password` fields.
  - Set the form action to `url_for('login')` with `method="post"`.
  - Add a block that displays flashed error messages.
  - Add a link to `/register` for new users.

## Files to change

- `app.py` — implement `login()` as a `GET` and `POST` handler; implement `logout()`.
- `database/db.py` — add the `get_user_by_email()` helper.
- `templates/login.html` — add the `POST` form and flash display.

## Files to create

- None.

## New dependencies

- None. `werkzeug.security.check_password_hash` is already available.

## Rules for implementation

- No SQLAlchemy or ORMs. Use raw `sqlite3` via `get_db()`.
- Parameterised queries only. Never use f-strings in SQL.
- Verify passwords with `werkzeug.security.check_password_hash`.
- The session key for the logged-in user must be `session["user_id"]`, stored as an integer.
- Use `flask.session`. Do not build a custom session mechanism.
- On a failed login, show the generic flash error "Invalid email or password." Do not reveal which field was wrong.
- After a successful login, redirect to `url_for("landing")` until a dashboard exists.
- `logout()` must call `session.clear()`, then redirect to `url_for("landing")`.
- All templates must extend `base.html`.
- Use CSS variables. Never hardcode hex values.
- Use `url_for()` for every internal link. Never hardcode paths.

## Definition of done

- [ ] `GET /login` renders the login form with email and password fields.
- [ ] Submitting valid credentials (`demo@spendly.com` / `demo123`) sets `session["user_id"]` and redirects to `/`.
- [ ] Submitting a wrong password shows the "Invalid email or password." flash and stays on the login page.
- [ ] Submitting an unregistered email shows the same generic error flash.
- [ ] `GET /logout` clears the session and redirects to `/`.
- [ ] After logout, `session["user_id"]` is no longer present.
- [ ] The `/logout` route no longer returns the raw stub string.
