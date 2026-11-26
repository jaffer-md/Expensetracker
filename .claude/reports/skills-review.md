# Review: Project skills (`.claude/skills/*/SKILL.md`)

**Date:** 2026-11-25
**Files reviewed:** `.claude/skills/frontend-design/SKILL.md` (name: `spendly-ui-designer`), `.claude/skills/spendly-database/SKILL.md`
**Checked against:** `database/db.py`, `app.py`, `tests/conftest.py`, `templates/base.html`, `static/css/style.css`, `.claude/specs/`

Both skills are untracked (`?? .claude/skills/`). Neither has been committed.

## Summary

| Skill | Verdict |
|---|---|
| `spendly-database` | Accurate and ready to use. Matches `db.py` line for line, with one stale sentence about `app.py` wiring. |
| `frontend-design` | Needs changes before it is reliable. Its default design language contradicts the app's real one, and it assumes things that don't exist (Lucide, sidebar, dashboard, modals). |

---

## 1. `spendly-database`

### What checks out
- Schema tables match `init_db()` exactly (columns, types, `UNIQUE`, FK, `DEFAULT CURRENT_TIMESTAMP`).
- `DB_PATH`, `PASSWORD_HASH_METHOD`, `get_db()` (Row factory, FK pragma per connection) and idempotent `seed_db()` match the code.
- Seed data: 8 expenses, all 7 categories, dates clamped with `min(day, today.day)`.
- Test-suite note (`DB_PATH` monkeypatched, read at call time) matches `tests/conftest.py`.
- The "never delete `spendly.db` without OK" rule is sound. The file is git-ignored, so it is not recoverable from git.
- The verification script uses a temp DB and never touches real data.
- `description` is specific and has good trigger phrases.

### Issues
1. **Stale wiring claim (medium).** The skill says `app.py` "runs them at import time" and does not use `with app.app_context():`. In fact `app.py:24-26` does use `with app.app_context(): init_db(); seed_db()`. That block runs at module level, so it is also at import time. Replace the paragraph with: "`app.py` already calls them inside `with app.app_context():` at module level, which satisfies the spec and also covers `python app.py` and pytest." (`CLAUDE.md` has the same imprecision.)
2. **Imports list is incomplete (low).** The skill says to import `get_db, init_db, seed_db`. The real line also imports `create_user` and `get_user_by_email`. Tell the agent to preserve the existing import line.
3. **Spec dependency (low).** "If the spec conflicts, the spec wins" is fine, but the skill never says which sections of the spec it relies on. It cites "section 6" only once.
4. **Seed edge case (low).** On the 1st of the month every seeded date collapses to the same day because of the clamp. This is harmless, but "spread across the current month" is false on days 1-2. Add a note.
5. **No schema-drift guidance (low).** `CREATE TABLE IF NOT EXISTS` will not alter an existing table. If the schema changes, the skill should say to write an `ALTER TABLE` or ask before resetting.
6. **"Wait for Python 3.9" claim is unverified in the skill.** It could include a one-line check (`python -c "import hashlib; hashlib.scrypt"`) so the reason can be re-tested if the Python version changes.

---

## 2. `frontend-design` (`spendly-ui-designer`)

### Strengths
- Good instruction to inspect `base.html`, the CSS and existing templates before designing, and to reuse tokens and classes.
- Clear stack constraints (no React, Tailwind or Bootstrap) and a sensible "what to avoid" list.
- Tabular numerals, right-aligned numeric columns, label-above-input forms, and a mobile fallback are all correct for a finance UI.
- `disable-model-invocation: true` is appropriate, since it is slash-command only.

### Issues
1. **Default design language conflicts with the app (high).** The skill defaults to indigo accent, Inter/system fonts, 8/12/16px radii and a `#F7F8FA` background. The real app uses a deep green accent (`--accent: #1a472a`), `DM Serif Display` + `DM Sans` loaded in `base.html`, a warm paper palette (`--paper: #f7f6f3`), and radii of 6/12/20px. It says to override the defaults "to match existing", but the instruction is weak. Make the project tokens the *primary* spec and list them (`--ink*`, `--paper*`, `--accent*`, `--danger*`, `--border*`, `--radius-*`, `--font-*`, `--max-width`, `--auth-width`). Demote the fintech palette to a fallback for an empty repo.
2. **Lucide is assumed, but not used (high).** `grep lucide templates static` returns nothing. The skill says to "load Lucide once in `base.html`" using `https://unpkg.com/lucide@latest`. That adds an unpinned third-party script on every page and changes `base.html`. Pin a version, or state that icons are optional and inline SVG is acceptable. Ask before adding the dependency.
3. **Assumes pages that don't exist (medium).** It talks about a sidebar, a dashboard, `dashboard.html`, modals, `base.css`, `components.css` and `partials/`. The app has a top-nav `base.html`, `profile.html`, `add_expense.html`, `edit_expense.html`, auth pages and legal pages, and two stylesheets (`style.css`, `landing.css`). Replace the examples with real file names and tell the agent to extend `style.css` rather than create new files.
4. **Income semantics don't apply (medium).** Spendly is expenses-only (`arrow-up-right`/income, green-for-income). The semantic palette should map to the app's `--danger` and `--accent` tokens, and the skill should say there is no income concept.
5. **Output format doesn't fit an agent in a repo (medium).** It mandates a plan, fenced code blocks for each file, and an integration note. In Claude Code the agent should edit files directly and summarize. Add: "In-repo, write the files; use the three-part format only when no repo is available."
6. **Redundant "ask for a screenshot" step (low).** Inside the repo, the agent can run the app (`python app.py`, port 5001, demo login) or read the templates. Point it to the `/run` flow instead.
7. **Missing project conventions (medium).**
   - Forms: validation errors come back with status 200 plus `flash(..., "error")`, so error styling must work with flashed messages, not only inline field errors.
   - Destructive actions use POST-only forms (delete expense).
   - Profile date-filter and category-breakdown UI already exist and should be reused.
   - `static/js/main.js` is a one-line stub, so nothing is shared yet.
8. **Accessibility is absent (low).** Add focus-visible styles, contrast targets (the muted gray `#6B7280` on tinted surfaces can fall below 4.5:1), `aria-label` on icon-only buttons, and `prefers-reduced-motion`.
9. **Description contains a placeholder (low).** `repo - https://github.com/XXXXXXXX/spendly` is a dummy URL. Remove it or fill it in.
10. **Name mismatch (low).** The frontmatter `name` is `spendly-ui-designer`, but the directory and the slash command are `frontend-design`. Pick one.
11. **Minor internal inconsistency (low).** Radius guidance says 8px inputs, 12px cards and 16px modals, but "8px grid" spacing advice elsewhere allows 4px multiples. The type scale (12/14/16/20/24/32) is never mapped to the existing CSS.

---

## Recommended changes (priority order)

1. `frontend-design`: put the real tokens and fonts first, and make the generic palette a fallback (issue 1).
2. `frontend-design`: remove or pin the Lucide requirement, and ask before adding it (issue 2).
3. `frontend-design`: replace the fictional dashboard/sidebar/modal examples with real files and routes (issues 3, 4).
4. `frontend-design`: add an in-repo output mode that edits files directly (issue 5).
5. `spendly-database`: correct the `app.py` wiring paragraph and preserve the existing import line (issues 1, 2).
6. Fix the placeholder repo URL and the name mismatch.
7. Commit both skills (`git add .claude/skills`) once edited.
