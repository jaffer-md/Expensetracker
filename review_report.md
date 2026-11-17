# Code Review Report — Spendly (Expense Tracker)

**Scope:** Full codebase review of `app.py`, `database/`, `templates/`, `static/css/`, `static/js/`, and project configuration.
**Date:** 2026-11-16
**Commit reviewed:** `5cc9dce` (plus uncommitted changes: hero redesign, video modal, `landing.css`)

---

## 1. Summary

Spendly is at an early stage. The UI shell (landing, login, register, terms, privacy) is in place, and the routing skeleton is set up for the remaining feature steps. The core application logic has **not been implemented yet**:

- The database layer (`database/db.py`) is comments only.
- Login and registration forms have **no POST handlers**.
- The profile, logout, and expense routes return placeholder text.

The review therefore focuses on the code that exists, the gaps that will block the next steps, and issues to fix before real user data is handled.

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High     | 2 |
| Medium   | 5 |
| Low      | 6 |

---

## 2. What Works

- **Routing is clean and readable.** Routes are grouped and labelled, and placeholders are explicit about which step implements them.
- **Templates share a base layout.** `base.html` provides the nav, footer and blocks. Pages extend it consistently.
- **`url_for` is used for internal links** in templates, so routes can be renamed safely.
- **The new pages match the theme.** `terms.html` and `privacy.html` reuse the `legal-*` styles, and the hero and modal use the existing CSS variables for the font family.
- **Video modal behaviour is correct.** It closes on the button, backdrop click and Escape. Clearing `iframe.src` on close stops playback.
- **Forms use `required` and proper input types** (`email`, `password`), which gives basic client-side validation.

---

## 3. Findings

### High

**H1 — Login and register forms cannot be submitted.**
`app.py` registers `/login` and `/register` for GET only. `templates/login.html` and `templates/register.html` post to those same URLs, so a submit returns **HTTP 405 Method Not Allowed**. Verified with `curl -X POST` against the running server for both routes.
*Fix:* Add `methods=["GET", "POST"]` to both routes and handle the form data. This is part of Steps 2 and 3, so it is expected at this stage, but nothing can be tested end-to-end until it is done.

**H2 — No database layer exists.**
`database/db.py` contains only comments. `expense_tracker.db` is in `.gitignore`, but nothing creates it. Every feature from Step 2 onwards depends on `get_db()`, `init_db()` and `seed_db()`.
*Fix:* Implement the functions described in the file's header comment, with `PRAGMA foreign_keys = ON` and `row_factory = sqlite3.Row`.

### Medium

**M1 — Hard-coded `debug=True` in `app.py`.**
`app.run(debug=True, port=5001)` enables the Werkzeug debugger, which allows arbitrary code execution from the browser if the server is reachable from a network. It is acceptable for local development, but it must not be deployed as-is.
*Fix:* Read the debug flag from an environment variable, defaulting to `False`, e.g. `debug=os.environ.get("FLASK_DEBUG") == "1"`.

**M2 — No `SECRET_KEY` configured.**
Flask sessions (needed for login in Step 3) require `app.secret_key`. Nothing sets it, so session features will fail or be insecure.
*Fix:* Load it from an environment variable, e.g. `app.secret_key = os.environ["SECRET_KEY"]`, and document it in the README.

**M3 — Dead CSS left in `style.css`.**
The old hero and mock-card rules (`.hero-title em`, `.mock-card`, `.mock-bar-*`, `.mock-*`, and the old `.hero`, `.hero-badge`, `.hero-title`, `.hero-subtitle`, `.hero-actions`, `.hero-visual` rules) are no longer used by any template, because `landing.css` now overrides them. They add about 100 lines of unused code and make it harder to tell which hero rules are live.
*Fix:* Remove the superseded rules from `style.css` and move the hero rules fully into `landing.css`.

**M4 — Video modal is not fully accessible.**
- No focus trap: Tab can move focus to the page behind the open modal.
- The "See how it works" control is an `<a href="#">` with `role="button"`. Without JavaScript it jumps to the top of the page instead of doing nothing.
- The `<iframe>` is inserted with an empty `src` and only receives a URL on click, which is fine, but there is no `<noscript>` fallback.
*Fix:* Use a `<button>` for the trigger, trap focus while the dialog is open, and keep the modal's `hidden` state consistent with `aria-hidden` if you add it.

**M5 — Placeholder content that will ship by accident.**
- `support@spendly.example` in `privacy.html`.
- `VIDEO_URL` points to a public test video in `landing.html`.
- The "Last updated: November 2026" date in both legal pages is hard-coded.
- Terms and privacy text is generic and has not been reviewed by a lawyer.
*Fix:* Keep these in a tracked TODO list and replace them before any public launch.

### Low

**L1 — `main.js` is empty.** It contains a single comment. This is expected for the starter project, but the modal logic currently lives inline in `landing.html`. Consider moving it to `main.js` once more pages need scripts, so `base.html`'s shared script is used.

**L2 — Template and CSS class reuse.** `terms.html` and `privacy.html` use `class="auth-switch"` for the "Back to home" link. The class is named for the auth pages, so it is misleading here. A shared `back-link` class would be clearer.

**L3 — Inconsistent hero CSS grouping.** `landing.css` defines `.hero-actions` and `.hero-btn`, while `style.css` still defines `.btn-primary`/`.btn-ghost` for the CTA section. Two button systems now coexist on the landing page. Acceptable for now, but worth consolidating when the design is finalised.

**L4 — Hard-coded data in the hero mock dashboard.** The numbers (₹18,240, ₹6,760, 34) and bar widths are static HTML. This is fine for a marketing page, but make sure no one mistakes it for live data once the expense features exist.

**L5 — Fonts loaded from a third party.** `base.html` loads Google Fonts on every page. This is a privacy consideration (the privacy policy already mentions it) and a performance cost. Self-hosting would remove both.

**L6 — No tests.** `requirements.txt` includes `pytest` and `pytest-flask`, but there is no `tests/` directory and no test file. The specs call for tests in later steps; adding a smoke test for each existing route would catch regressions like the 405 issue in H1.

---

## 4. Recommended Order of Work

1. **Implement the database layer** (H2), then wire up registration and login (H1, M2). These unblock all other features.
2. **Lock down configuration** (M1, M2): environment-driven debug flag and secret key, before anything is deployed.
3. **Clean up CSS** (M3, L3) once the hero design is confirmed.
4. **Add route smoke tests** (L6) to lock in current behaviour.
5. **Fix modal accessibility** (M4) and move its script to `main.js` (L1).
6. **Replace placeholder content** (M5) before launch.

---

## 5. Out of Scope / Not Reviewed

- Specification files (`Spec_*.md`) were not checked against the implementation, since most steps are not started.
- No security audit of third-party dependencies beyond the versions pinned in `requirements.txt`.
- Visual regression against `spendly.png` was not run; the hero was matched by inspection only.
