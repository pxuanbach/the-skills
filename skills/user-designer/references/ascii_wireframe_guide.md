# ASCII Wireframe & UI Mockup Guide

This guide provides conventions and code block structures for rendering UI wireframes in Markdown using ASCII box-drawing characters.

---

## 1. Box Drawing Characters Reference

| Type | Characters |
|------|------------|
| Outer Corners | `┌` (Top-Left), `┐` (Top-Right), `└` (Bottom-Left), `┘` (Bottom-Right) |
| T-Junctions | `┬` (Top), `┴` (Bottom), `├` (Left), `┤` (Right), `┼` (Cross) |
| Lines | `─` (Horizontal), `│` (Vertical) |
| UI Elements | `[ Button ]`, `(o) Radio Selected`, `[x] Checkbox Checked`, `[ ] Unchecked` |

---

## 2. Common UI Patterns & Examples

### Pattern A: Upload Modal Dropzone
```text
┌──────────────────────────────────────────────────────┐
│ Upload Document                                [ X ] │
├──────────────────────────────────────────────────────┤
│                                                      │
│ ┌──────────────────────────┐                         │
│ │                          │                         │
│ │ 📄                       │                         │
│ │                          │                         │
│ │ Drag & drop your PDF     │                         │
│ │ or click to browse       │                         │
│ │                          │                         │
│ └──────────────────────────┘                         │
│                                                      │
│ Supported: PDF                                       │
│ Maximum size: 50 MB                                  │
│                                                      │
│                                [ Cancel ] [ Upload ] │
└──────────────────────────────────────────────────────┘
```

### Pattern B: Data Table & Navigation
```text
┌──────────────────────────────────────────────────────────────────┐
│ Task Management Dashboard                       [ + Create Task ]│
├──────────────────────────────────────────────────────────────────┤
│ Filter: [ Status: All ▾ ]  [ Priority: High ▾ ]  [ Search...   ] │
├──────┬─────────────────────────────┬───────────┬─────────────────┤
│ ID   │ Title                       │ Status    │ Action          │
├──────┼─────────────────────────────┼───────────┼─────────────────┤
│ I-01 │ Build Database Schema       │ Completed │ [ View ]        │
│ I-02 │ Implement Auth Middleware   │ In Prog   │ [ Edit ]        │
└──────┴─────────────────────────────┴───────────┴─────────────────┘
```

---

## 3. Mockup Markdown Structure

Every `mockup/*.md` document must follow this layout:

```markdown
---
id: mockup-001
title: Title of Mockup 001
derived_from:
  - req-001
---

# Mockup for <Screen/Feature Title>

## Screen Name: <Screen Name>

```text
<ASCII WIREFRAME HERE>
```

## Components
- **Header**: Title, Close button
- **Content**: Form/List details
- **Footer**: Action buttons

## Interactions
- User clicks "Action" -> triggers processing state.
- Form validation checks empty inputs.

## Related Requirements
- `req-001`: <Requirement Title>

## Codebase Evidence
- Files read: `src/pages/tasks/TaskList.tsx:12-80`, `src/components/DataTable.tsx`
- Existing components reused: `DataTable` (table), `PageHeader` (header)
- NEW components (not in codebase): `BulkActionBar` — <why needed>
- Changed vs current screen: <delta only, or "new screen">
- Assumptions: <none | greenfield / code not found — layout is assumed>
```

Rule: every element in the wireframe must trace to an existing component in `Codebase Evidence` or be marked `NEW`. A wireframe drawn without reading the real UI code is invalid.
