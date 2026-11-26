---
name: frontend-design
description: Designs and builds UI for Spendly, a personal expense tracker on Flask + Jinja2 + vanilla CSS. Extends the app's existing design system (green accent, DM Serif Display / DM Sans, warm paper palette) to produce consistent pages and components - cards, forms, tables, stat tiles, filters. Use this skill whenever the user asks to design, build, create, redesign, improve, or style any Spendly page, screen, section, or component - including phrasings like "design the X page", "create UI for X", "build a component for X", "make the X look better", "redesign X", or any request about Spendly's frontend, layout, CSS, or visual polish - even when Spendly isn't named explicitly if the conversation context is clearly about it.
disable-model-invocation: true
---

# Spendly UI Designer

Design frontend UI that looks like it already belongs in Spendly. The app has an established design system. Extend it; do not replace it.

## Stack

- **Backend:** Flask (`app.py`), SQLite (`database/`).
- **Templates:** Jinja2 in `templates/`, all extending `base.html` (top navbar, `<main class="main-content">`, footer; blocks: `title`, `head`, `content`, `scripts`).
- **Styles:** vanilla CSS. `static/css/style.css` is the app stylesheet; `static/css/landing.css` is landing-page only. No Tailwind, Bootstrap, preprocessors, CSS-in-JS, React or Vue unless the user asks for a migration.
- **Scripts:** `static/js/main.js` is currently a one-line stub, loaded on every page. Page-specific JS goes in `{% block scripts %}`.
- **Icons:** none are loaded today (the brand mark is the text glyph `◈`). See "Icons" below.

## Step 1: read the existing code (always, when inside the repo)

Open `templates/base.html`, `static/css/style.css`, and the template closest to what you're building (e.g. `profile.html`, `add_expense.html`, `login.html`). Do not ask the user for a screenshot when the files are available. To see the result, run the app (`python app.py`, port 5001, demo login `demo@spendly.com` / `demo123`) or use the `/run` skill.

## Step 2: use the project's tokens (source of truth)

These live in `:root` in `style.css`. Use the variables; never hardcode their values.

| Group | Tokens |
|---|---|
| Text | `--ink`, `--ink-soft`, `--ink-muted`, `--ink-faint` |
| Surfaces | `--paper` (page), `--paper-warm`, `--paper-card` (cards, white) |
| Accent (deep green) | `--accent`, `--accent-light` |
| Secondary (amber) | `--accent-2`, `--accent-2-light` |
| Danger | `--danger`, `--danger-light` |
| Borders | `--border`, `--border-soft` |
| Fonts | `--font-display` (DM Serif Display, headings), `--font-body` (DM Sans) |
| Layout | `--max-width` (1200px), `--auth-width` (440px) |
| Radius | `--radius-sm` 6px, `--radius-md` 12px, `--radius-lg` 20px |

If a needed value has no token, add one to `:root` rather than hardcoding it in a rule.

Semantics: Spendly tracks **expenses only. There is no income concept.** Green (`--accent`) is the brand and positive/confirm color, not "income". Red (`--danger`) is for errors and destructive actions. Amber (`--accent-2`) is for warnings or highlights. Do not add income/savings/balance widgets unless the user asks for that feature. The footer copy says "rupee"; if you display currency, match how existing templates already format amounts.

### Reuse existing component classes

Check `style.css` first. Existing classes include: `.profile-container/.profile-card/.profile-section`, `.section-head/.section-title`, `.stats-row/.stat-tile/.stat-label/.stat-value`, `.txn-table/.table-wrap/.row-action/.actions-cell`, `.badge` + `.badge-<category>` (food, transport, bills, health, entertainment, shopping, other), `.bar-track/.bar-fill/.bar-w-0..100` (category bars; width is a class, not an inline style), `.category-list/.category-head/.category-amount`, `.filter-bar/.preset-group/.preset-link/.custom-range/.range-field/.filter-apply`, `.auth-container/.auth-card/.auth-title/.auth-error/.auth-success`, `.form-group/.form-input/.field-optional`, `.btn-primary/.btn-ghost/.btn-submit/.btn-delete/.btn-inline`, `.user-card/.user-avatar`, `.legal-*`. Reuse these before inventing new ones. New classes use a page or component prefix (`.reports-...`) so they don't leak.

## Design language

Warm, editorial and calm: serif display headings, generous whitespace, soft borders instead of heavy shadows, one confident green accent.

- **Spacing:** multiples of 4px/8px. Keep card padding consistent within a page.
- **Shadows:** subtle only (ceiling: `0 1px 2px rgba(0,0,0,.04), 0 1px 3px rgba(0,0,0,.06)`). Prefer a `1px solid var(--border)` over a shadow. No glows, no gradients where a solid color works.
- **Typography:** headings in `--font-display`, everything else in `--font-body`. Amounts use `font-variant-numeric: tabular-nums` and are right-aligned in tables. Match the sizes already used in the nearest template.
- **Layout:** card-based composition, left-aligned content, centered only for auth and empty states. Content width follows `--max-width`.
- **Tables:** row hover, right-aligned numeric columns, wrapped in `.table-wrap` so they scroll horizontally on narrow screens.
- **Forms:** label above input, helper text below, optional fields marked with `.field-optional`.
- **Mobile:** stack cards vertically and make tables scroll below ~768px. Check the layout at narrow widths.

## Project conventions that affect UI

- **Validation errors are flashed.** Routes re-render the form with status 200 and `flash(..., "error")`. Style error states so they work for a flashed message at the top of the form (an `.auth-error` div above the form, as in `add_expense.html` and `profile.html`), not only for per-field messages. Keep the user's submitted values in the inputs.
- **Destructive actions are POST-only forms**, never links (see delete expense in `profile.html`). A delete control must be a `<form method="post">` with a clearly labeled button, and should confirm before submitting.
- **Per-user data:** every query is scoped to the logged-in user. UI must never expose another user's data, and pages redirect to `/login` when logged out.
- **No inline styles** beyond the existing `display:inline` on the delete form. Add a class instead.
- **Dates** are `YYYY-MM-DD` text and use `<input type="date">`. The profile date filter (preset links plus a custom range) already exists; reuse it.
- **Categories** are the fixed list in `app.py` (`CATEGORIES`): Food, Transport, Bills, Health, Entertainment, Shopping, Other. Do not invent new ones in the UI.

## Icons

No icon library is installed. Default to text, the `◈` brand glyph, or small inline SVG. A clearly labeled button beats a mystery icon.

If the user wants an icon set, ask first, then add **Lucide pinned to an exact version** (never `@latest`) in the `head` block of `base.html`, and call `lucide.createIcons()` from `main.js` after DOM ready. Use `<i data-lucide="name">` and size via CSS. Keep icon density low: at most one per button, one per section heading, one per row action.

## Accessibility

- Visible `:focus-visible` outline on every interactive element, using `--accent`.
- Text contrast of at least 4.5:1. Check `--ink-muted` and `--ink-faint` on `--paper-warm` and on tinted badges; use `--ink-soft` where it falls short. `--ink-faint` is for decoration or placeholders only.
- Icon-only controls need `aria-label`. Form inputs need an associated `<label for>`.
- Convey state with text or an icon as well as color (for example "Error:" in addition to red).
- Respect `prefers-reduced-motion` for any transition or animation.

## Output

**In the repo (the normal case):** edit or create the template and CSS files directly, then reply with a short summary: what changed, which files, and any new route or variable the template expects. Do not paste full files into the chat.

**No repo access:** reply with (1) a 2-5 bullet UI plan that states assumptions, (2) each file in its own labeled fenced block (template, CSS, JS only if needed), and (3) a 1-3 line integration note (route, variables, any link to add in `base.html`).

If a request is under-specified, state your assumptions in one line each and proceed. Ask only when the answer changes the output, for example "standalone page or part of the profile page?"

If the page needs a new route or query, say so and leave `app.py` / `database/queries.py` changes to the user's spec workflow (`/create-spec`) unless they ask you to implement it.

## What to avoid

- Introducing a second accent color, font family, or radius scale.
- Hardcoding hex values that already exist as tokens.
- Generic, dated looks: default browser styles, sharp bordered boxes, heavy drop shadows.
- Over-styling. Solid color over gradient, border over shadow.
- Inconsistent spacing (14px here, 18px there).
- Adding a JS or CSS framework, or an external script, without asking.
- Desktop-only layouts.
