# Spec: Step 2 — User Registration

## Overview

- Upgrades the existing stub `GET /register` route into a fully functional form that handles both `GET` and `POST`.
- The form accepts four fields: name, email, password, and confirm_password.
- On success, the user is created, a success message is flashed, and the user is redirected to `/login`.
- On any validation failure, the form is re-rendered with a flashed error message. Nothing is inserted.
- This is the entry point for all authenticated features. Login, profile, and expense tracking all depend on a user existing in the `users` table.

## Depends on

- Step 01 — Database setup (`users` table and `get_db()` in `database/db.py`).

## Routes

- `GET /register` — renders the registration form. Public. Already exists as a stub; upgrade it.
- `POST /register` — processes the form, validates input, inserts the user, and redirects to `/login`. Public.

## Database changes

- No new tables or columns.
- The existing `users` table covers all requirements.
- Add one new helper to `database/db.py`: `create_user(name, email, password)`.
  - Hashes the password with werkzeug.
  - Inserts a row into `users`.
  - Returns the new user's id.
  - Raises `sqlite3.IntegrityError` if the email is already taken (UNIQUE constraint).

## Templates

- Modify `templates/register.html`:
  - Change the form action to `url_for('register')` with `method="post"`.
  - Add a `name` attribute to all inputs: `name`, `email`, `password`, `confirm_password`.
  - Add a block that displays flashed error messages (for example "Email already registered" or "Passwords do not match").
  - Keep all existing visual design unchanged.

## Files to change

- `app.py` — upgrade `register()` to handle `GET` and `POST`; add flash and redirect logic; set `app.secret_key`.
- `database/db.py` — add the `create_user()` helper.
- `templates/register.html` — wire up the form action and method, and display flash messages.

## Files to create

- None.

## New dependencies

- None. Uses `werkzeug.security` (already installed) and Flask's built-in `flash`, `redirect`, and `url_for`.

## Rules for implementation

- No SQLAlchemy or any other ORM.
- Parameterised queries only. Never use f-strings in SQL.
- Hash passwords with `werkzeug.security.generate_password_hash`. Never store plaintext.
- `app.secret_key` must be set in `app.py` for `flash()` to work. Use a hardcoded development string for now.
- Server-side validation must run in this order:
  1. All fields are non-empty.
  2. `password` equals `confirm_password`.
  3. The email is not already registered. Catch `sqlite3.IntegrityError`.
- On any validation failure, re-render the form with a flashed error. Do not redirect.
- On success, flash a success message and redirect to `url_for('login')`.
- Use `abort(405)` if an unsupported HTTP method reaches the route.
- All templates must extend `base.html`.
- Use CSS variables. Never hardcode hex values.
- Use `url_for()` for every internal link. Never hardcode URLs.

## Definition of done

- [ ] `GET /register` renders the registration form without errors.
- [ ] Submitting all valid fields creates a new user in `users` and redirects to `/login`.
- [ ] Submitting mismatched passwords re-renders the form with an error and makes no database insert.
- [ ] Submitting an already-registered email re-renders the form with "Email already registered".
- [ ] Submitting with any empty field re-renders the form with a validation error.
- [ ] The password is stored as a hash, never plaintext, and this can be verified by inspecting `spendly.db`.
- [ ] No duplicate user is created on repeated valid submissions with the same email.
