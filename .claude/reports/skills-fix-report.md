# Report: Skill fixes (follow-up to `skills-review.md`)

**Date:** 2026-11-25
**Files changed:** `.claude/skills/frontend-design/SKILL.md` (rewritten), `.claude/skills/spendly-database/SKILL.md` (5 edits)
**Application code changed:** none

Facts used in the rewrite were checked against `templates/base.html`, `static/css/style.css` (tokens and class list), `templates/profile.html` / `add_expense.html` (flash markup, delete form) and `app.py:24-26`.

## `frontend-design`

| # | Issue from review | Fix |
|---|---|---|
| 1 | Default palette/fonts/radii contradicted the app | Project tokens are now the source of truth (table of `--ink*`, `--paper*`, `--accent*`, `--accent-2*`, `--danger*`, `--border*`, fonts, widths, radii 6/12/20). Indigo/Inter defaults removed. Rule added: no hardcoded values that have a token; add a token to `:root` if missing. |
| 2 | Lucide assumed, unpinned `@latest` | No icon library is assumed. Default is text / `◈` / inline SVG. If the user wants icons: ask first, pin an exact version, load in `base.html` `head`, init from `main.js`. |
| 3 | Fictional sidebar, dashboard, modals, `partials/`, extra CSS files | Rewritten around the real stack: top-nav `base.html` with its blocks, `style.css` + `landing.css`, `main.js` stub. Real component classes listed for reuse (stat tiles, txn table, badges, bar classes, filter bar, auth/form classes, buttons). |
| 4 | Income semantics | Stated explicitly: expenses only, no income. Green = brand/confirm, red = error/destructive, amber = warning. No income/savings widgets unless requested. |
| 5 | Output format wrong for an in-repo agent | Two modes: edit files directly and summarize (default); plan + labeled code blocks + integration note only without repo access. |
| 6 | Screenshot request redundant | Replaced with: read the files, run the app on port 5001 with the demo login, or use `/run`. |
| 7 | Project conventions missing | Added: flashed errors (status 200, `.auth-error`), POST-only delete form with confirm, per-user data/login redirect, no inline styles, `YYYY-MM-DD` dates and the existing date filter, fixed `CATEGORIES` list, `main.js` stub. |
| 8 | No accessibility guidance | Added section: `:focus-visible`, 4.5:1 contrast (and `--ink-faint` for decoration only), `aria-label`/`label for`, non-color state cues, `prefers-reduced-motion`. |
| 9 | Placeholder GitHub URL in description | Removed. Description now names the real design system. |
| 10 | `name` mismatch | Frontmatter `name` is now `frontend-design`, matching the directory and slash command. |
| 11 | Spacing/type-scale inconsistency | Spacing rule simplified to 4/8px multiples with "match the nearest template" for type sizes. The radius scale now comes from the tokens. |

Also added: new routes/queries are left to the `/create-spec` workflow unless the user asks.

## `spendly-database`

| # | Issue from review | Fix |
|---|---|---|
| 1 | Stale claim about `app.py` wiring | Now states `app.py` already runs `init_db()` / `seed_db()` in a module-level `with app.app_context():` block, which meets spec section 6 and also covers `python app.py` and pytest. |
| 2 | Incomplete imports | Tells the agent to keep the existing `database.db` import line (it also imports `create_user`, `get_user_by_email`). |
| 3 | Spec dependency unclear | Names the spec parts relied on: schema, seed data, section 6. |
| 4 | Seed edge case | Documented that early-month dates can coincide because of the future-date clamp, and that this is expected. |
| 5 | No schema-drift guidance | Added: `CREATE TABLE IF NOT EXISTS` does not migrate. Use an idempotent `ALTER TABLE` (check `PRAGMA table_info`) or reset only with explicit OK; update skill and spec together. |
| 6 | Unverified Python 3.9 / scrypt claim | Added a re-check one-liner. I ran it: `AttributeError: module 'hashlib' has no attribute 'scrypt'`, so the constraint still holds. |

## Not changed / notes

- `CLAUDE.md` says the DB is initialized "at import time". That is still true, so I left it alone.
- The `frontend-design` skill keeps `disable-model-invocation: true`, so it runs only through `/frontend-design`.
- I did not render any page or run `pytest`, since no application code or templates changed.
- Both skill files are still untracked in git. Commit them with `git add .claude/skills` when you're ready.
