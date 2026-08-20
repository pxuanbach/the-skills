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
```
