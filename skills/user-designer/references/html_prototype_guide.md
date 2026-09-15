# Interactive HTML Prototype Guide

This guide defines the conventions for rendering interactive UI prototypes as self-contained HTML files under `wiki/<NNN>-<feature>/mockup/<screen-slug>.html`. It is the HTML counterpart to `ascii_wireframe_guide.md` and is invoked by the `user-designer DESIGN html` sub-command.

---

## 1. When to Use HTML Mode

Use `DESIGN html` (HTML prototypes) instead of `DESIGN` (ASCII wireframes) when:

- The user explicitly asks for an HTML prototype ("tạo prototype bằng HTML", "DESIGN html", "click-through demo").
- The feature has rich UI state (hover, focus, loading, empty, error) that ASCII cannot convey.
- The user needs to share the prototype with stakeholders who cannot read ASCII.
- Multiple screens need to be navigated via `<a>` links for a flow review.

Otherwise, prefer ASCII mode — it is faster to author and equally diffable in markdown.

---

## 2. File Structure

```
wiki/<NNN>-<feature>/
├── design.md
└── mockup/
    ├── <screen-slug>.html        # One HTML file per screen
    ├── <screen-slug>.md          # Optional: component inventory companion
    └── ...
```

Each `<screen-slug>.html` is a single self-contained file — no external CDN, no remote fonts, no remote images. CSS and JS are inlined. Images use data: URIs.

---

## 3. Required HTML Skeleton

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><Screen Name> — <Feature Name> Mockup</title>
  <style>
    /* All styles inlined here. Pull values from wiki/DESIGN.md. */
    :root {
      /* Design tokens (mirror wiki/DESIGN.md) */
      --color-primary: #2563EB;
      --color-primary-hover: #1D4ED8;
      --color-surface: #FFFFFF;
      --color-text: #0F172A;
      --space-1: 4px;
      --space-2: 8px;
      --space-4: 16px;
      --space-6: 24px;
      --radius-md: 8px;
      --font-body: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --color-surface: #1E293B;
        --color-text: #F8FAFC;
      }
    }
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header>...</header>
  <main id="main">...</main>
  <footer>...</footer>
  <script>
    /* Minimal vanilla JS for interactive states. No frameworks. */
  </script>
</body>
</html>
```

---

## 4. Design Token Compliance

**Every** color, spacing, radius, shadow, and font value must come from a CSS variable defined at `:root` that mirrors `wiki/DESIGN.md`. Never hardcode arbitrary hex values in component CSS.

Before writing a component, copy the token block from `wiki/DESIGN.md#2-design-tokens`. If `DESIGN.md` does not define a token you need, add it to `DESIGN.md` first and reference it.

Forbidden:

```css
/* BAD — hardcoded hex */
.button { background: #2563EB; }
```

Required:

```css
/* GOOD — token-driven */
.button { background: var(--color-primary); }
.button:hover { background: var(--color-primary-hover); }
```

---

## 5. Required Component States

Every interactive component (button, input, link, toggle, modal trigger) must demonstrate the following states in the prototype:

| State | Trigger | Visible Behavior |
|-------|---------|------------------|
| Default | none | baseline style |
| Hover | `:hover` | color/elevation shift per DESIGN.md |
| Focus | `:focus-visible` | 2px offset focus ring per DESIGN.md |
| Disabled | `[disabled]` attr | opacity 50%, cursor not-allowed, no pointer events |
| Loading | `.is-loading` class | spinner + disabled state, "Loading..." copy |
| Error | `[aria-invalid="true"]` | red border + inline error message |
| Empty | empty list / no data | empty-state illustration + CTA |

Provide at least one component demonstrating each state. For data lists, render an empty-state row even when the sample data is non-empty (use a commented-out empty variant).

---

## 6. Accessibility Checklist

Each HTML mockup must pass these checks:

- [ ] `<html lang="en">` (or appropriate locale).
- [ ] Single `<h1>` per page; heading levels nest without skipping.
- [ ] All icon-only buttons have `aria-label`.
- [ ] All form inputs have associated `<label>` (use `for=`/`id=` or wrapping).
- [ ] Color contrast ≥ WCAG 2.1 AA (verify primary text on surface, primary button text, error text on surface).
- [ ] Keyboard navigable: `Tab` cycles interactive elements in logical order; `Enter`/`Space` activates.
- [ ] Skip link to `<main>` for screen readers.
- [ ] `prefers-reduced-motion` respected for any animation.
- [ ] `prefers-color-scheme: dark` block defined for dark-mode preview.

---

## 7. Cross-References (Semantic Search Step Output)

After running the semantic-search step in `user-designer SKILL.md` Step 3, list any reused patterns in a hidden HTML comment at the top of `<body>`:

```html
<!--
  Reused patterns from prior modules:
    - 002-task-list: header layout (logo left, nav center, user menu right)
    - 005-settings: settings page side nav
  Adapted components:
    - TaskCard (originally from 002-task-list)
-->
```

This keeps the design lineage traceable when reviewing the prototype later.

---

## 8. Multi-Screen Linking

For features with multiple screens, add a small bottom navigation block linking each screen of the same feature:

```html
<nav class="mockup-nav" aria-label="Mockup navigation">
  <strong>Prototype:</strong>
  <a href="login.html">Login</a> &rarr;
  <a href="dashboard.html">Dashboard</a> &rarr;
  <a href="create-task.html">Create Task</a>
</nav>
```

This lets reviewers click through the flow without leaving the wiki folder.

---

## 9. Companion `*.md` Inventory (Optional but Recommended)

For each `*.html` screen, create a companion `*.md` summarizing components for non-rendered review:

```markdown
# Mockup: <Screen Name>

## Screen HTML
- Path: `mockup/<screen-slug>.html`

## Components
- **Header**: Logo, primary nav, user menu
- **Main**:
  - TaskForm: validated inputs with inline errors
  - SubmitButton: states demonstrated (default, hover, focus, disabled, loading)
- **Footer**: copyright, mockup nav

## Interactions
- Click "Submit" → form validates → on success, redirects to `dashboard.html`.
- Empty list → renders empty-state CTA "Create your first task".

## Related Requirements
- `req-001`: <Requirement Title>
- `req-002`: <Requirement Title>

## Reused From Prior Modules
- `002-task-list`: header layout pattern.
```

This companion file is what `validate_plan_mockup.py` scans — it ensures each HTML mockup has a traceable Markdown summary.

---

## 10. Anti-Patterns

Forbidden in HTML prototypes:

- ❌ Hardcoded hex colors anywhere outside `:root`.
- ❌ External CDN scripts (`<script src="https://cdn...">`).
- ❌ External fonts loaded from `https://fonts.googleapis.com` (fallback stack only).
- ❌ Unused CSS classes left over from auto-generated frameworks.
- ❌ Mock data that contradicts the data model in `design.md`.
- ❌ Links to external sites.
- ❌ `console.log` debugging statements left in production-ready mockups.

If any of these appear, the `validate_html_mockup.py` (to be created in QA #3 follow-up) will flag them.