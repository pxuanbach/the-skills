# Elearning MVP Proposal Template

## Purpose
Use this as a starting template when the user asks to "write a proposal", "create a project plan", or "spec out" an elearning platform. Populate the sections with findings from research, user decisions, and confirmed tech choices.

---

## Proposal Sections

### 1. Project Overview
- Problem statement (2–3 sentences)
- Solution summary (key differentiating factor)
- Target users
- Monetization model

### 2. Tech Stack
Table format: | Layer | Technology | Cost |

### 3. Feature Mapping
Two-column table: Feature → Implementation (library/method)

Include priority matrix (MVP vs Phase 2 vs Phase 3).

### 4. Database Schema
- ERD summary (text-based)
- Table list with purpose and key columns
- RLS policy summary table

### 5. Page Structure
Next.js App Router file tree

### 6. Mobile-First UI Strategy
- Design principles (touch targets ≥44px, font sizes, breakpoints)
- Navigation diagram (ASCII or Mermaid)

### 7. Certificate Design
- Certificate number format with example
- Auto-issuance logic (trigger flow)
- PDF layout description

### 8. Gamification — Streaks
- Rules table
- DB trigger + cron approach
- UI mockup (text-based)

### 9. Ad Integration
- Placement rules per page type (table)
- Phase-based ad stack

### 10. API Routes
Table: Method | Route | Purpose | Auth

### 11. Email Templates
List with trigger + subject/body description

### 12. Time Estimate
- Per-task breakdown (days)
- Milestone plan (week-by-week)
- Team vs solo comparison

### 13. Open Questions
Numbered list of unconfirmed decisions

---

## Key Decisions to Confirm Before Writing Proposal

| # | Question | Options |
|---|----------|---------|
| 1 | Course code format | Instructor-input vs auto-gen |
| 2 | Video privacy | YouTube unlisted vs public |
| 3 | Lesson completion trigger | Video 80% watched vs explicit button |
| 4 | Admin roles | Single admin vs instructor-level |
| 5 | Certificate format | `{CODE}-{encoded_seq}` |
| 6 | Payment/subscription | Required vs ad-based |

---

## Ad-Based Monetization Notes

When user specifies ad-based (no payment/subscription):
- Remove: Stripe, payment tiers, instructor payouts
- Add: AdSense placement rules, no-ads zones (certificates, quiz pages)
- Increase weight on: engagement features (streaks, certificates) as retention drivers

---

## Output Path
Save final proposal to: `D:\Documents\research_reports\elearning-mvp-proposal_<YYYYMMDD>.md`

---

## Reference Files (from this session)

| File | Content |
|------|---------|
| `D:\Documents\research_reports\elearning-features-survey_20260804.md` | Feature taxonomy |
| `D:\Documents\research_reports\elearning-techstack.md` | Full library + schema reference |
| `D:\Documents\research_reports\elearning-platforms-analysis.md` | OSS landscape |
| `D:\Documents\research_reports\video-embedding-comparison.md` | Video comparison |
| `D:\Documents\research_reports\gamification-elearning-research.md` | Gamification data |
| `D:\Documents\research_reports\lms_analytics_research.md` | LMS analytics |
| `D:\Documents\research_reports\supabase_elearning_schema.md` | Full DDL + RLS |
