# Spec: Step 4 — Profile Page (Hardcoded UI)

## Overview

- Replaces the `/profile` stub with a fully designed profile page that shows static, hardcoded data.
- The goal is to establish the complete UI layout before any real database queries are wired up in Step 05.
- The page has four sections to build:
  - User info card
  - Summary stats
  - Transaction history table
  - Category breakdown
- Building the UI first lets the team validate the design in isolation and ensures the templates are ready for the backend-connection step.

## Depends on

- Step 01 — Database Setup. The schema must exist.
- Step 02 — Registration. User accounts must be creatable.
- Step 03 — Login and Logout. The session must be set, and `/profile` must be a protected route.

## Routes

- `GET /profile` — renders the profile page. Logged-in only. Redirects to `/login` if the user is not authenticated.

## Database changes

- No database changes.
- The existing `users` and `expenses` tables are sufficient.
- No database queries in this step. All data is hardcoded.

## Templates

- Create `templates/profile.html`, a full profile page that extends `base.html`.
- It must contain four sections, in this order:
  1. User info card: avatar initials, name, email, and member-since date. All values are hardcoded.
  2. Summary stats row: total spent, number of transactions, and top category. All values are hardcoded.
  3. Transaction history table: a list of recent expenses with date, description, category badge, and amount. At least three hardcoded rows.
  4. Category breakdown: per-category totals as a simple list or progress-bar rows. At least three hardcoded categories.

## Files to change

- `app.py` — replace the `/profile` stub with a real view function that:
  - Redirects unauthenticated users to `/login`.
  - Passes hardcoded context variables to `profile.html`: a user dict, a stats dict, an expenses list, and a category breakdown list.

## Files to create

- `templates/profile.html`

## New dependencies

- None.

## Rules for implementation

- No SQLAlchemy or ORMs. Use raw `sqlite3` via `get_db()` if a database call is ever needed.
- Parameterised queries only. Never string-format SQL.
- Authentication guard: check `session.get("user_id")`. If it is absent, call `redirect(url_for("login"))`.
- All data passed to the template must be hardcoded Python dicts and lists in `app.py`. No database queries in this step.
- Use CSS variables. Never hardcode hex values.
- No inline styles anywhere in `profile.html`.
- All templates must extend `base.html`.
- Category badges must use a CSS class, not inline colour styles.
- Use `url_for()` for every internal link. Never hardcode paths.

## Definition of done

- [ ] Visiting `/profile` without being logged in redirects to `/login`.
- [ ] Visiting `/profile` while logged in returns HTTP 200.
- [ ] The page displays a user info card with a name and email.
- [ ] The page displays at least three summary stat values (for example, total spent, transaction count, and top category).
- [ ] The page displays a transaction history table with at least three hardcoded rows.
- [ ] The page displays a category breakdown section with at least three categories.
- [ ] The navbar shows the logged-in state (username and logout link).
- [ ] No hex colour values appear in `profile.html`. Only CSS variables are used.
