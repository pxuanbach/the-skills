# Elearning App Techstack Reference (Next.js + Supabase MVP)

## Stack Overview

| Layer | Technology | License | Stars |
|-------|-----------|---------|-------|
| Framework | Next.js 15 (App Router) | MIT | — |
| Auth + DB | Supabase | Apache-2.0 | 108k |
| Video | react-player | MIT | 10.3k |
| Rich text | Tiptap | MIT | 37.9k |
| PDF certs | @react-pdf/renderer | MIT | 16.7k |
| Push | react-onesignal | BSD | 86 |
| Forms | react-hook-form + zod | MIT | — |

**Estimated MVP cost: $0–5/mo** (Supabase free tier + Vercel hobby)

---

## Supabase Schema — 8 Core Tables

```
profiles ────────── auth.users (extends)
  │
courses ────────── lessons (1:N)
  │                │
  │                quizzes (1:1 per lesson) ── quiz_questions (1:N)
  │                                        └─ quiz_options (1:N)
  │
enrollments ────── lesson_progress (N:N user×lesson)
  │
  └─────────────── quiz_submissions
  └─────────────── streaks
  └─────────────── certificates
```

### RLS Quick-Reference

| Table | Select policy | Insert policy | Update/Delete policy |
|-------|---------------|---------------|----------------------|
| profiles | `auth.uid() = id` | Service role only | `auth.uid() = id` |
| courses | `is_published = true` | Service role only | Service role only |
| lessons | Subquery via courses | Service role only | Service role only |
| enrollments | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |
| lesson_progress | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |
| quiz_submissions | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |
| streaks | `auth.uid() = user_id` | `auth.uid() = user_id` | `auth.uid() = user_id` |
| certificates | `auth.uid() = user_id` | DB trigger (auto-issue) | Service role only |

### Key Triggers

1. **Auto-grade quiz** — `plpgsql` function invoked on `quiz_submissions` INSERT
2. **Update streak** — trigger on `lesson_progress.is_completed = true` UPDATE
3. **Issue certificate** — trigger when all lessons in course marked complete

---

## Video Embedding Comparison

| Provider | Cost (free tier) | HLS | Analytics | Best for |
|----------|-------------------|-----|-----------|---------|
| YouTube iframe | Free | ❌ (DASH only) | Basic | Zero-budget MVP |
| Vimeo | $12+/mo | ✅ | Good | Brand-conscious |
| **Mux** | **100K min/mo free** | **✅** | **Events API** | **Growth app (recommended)** |
| Cloudflare Stream | ~$5/1K min | ✅ | Good | Already on Cloudflare |

**MVP recommendation:** YouTube unlisted embed → Mux when needing HLS + video completion tracking.

---

## Library Quick Links

| Library | Install |
|---------|---------|
| `@supabase/supabase-js` + `@supabase/ssr` | `npm install @supabase/supabase-js @supabase/ssr` |
| `react-player` | `npm install react-player` |
| `tiptap` | `npm install @tiptap/react @tiptap/starter-kit` |
| `@react-pdf/renderer` | `npm install @react-pdf/renderer` |
| `react-onesignal` | `npm install react-onesignal` |
| `react-hook-form` + `zod` | `npm install react-hook-form zod @hookform/resolvers` |

---

## Full Research Reports

- Stack detail: `D:\Documents\research_reports\elearning-techstack.md`
- Schema detail: `D:\Documents\research_reports\supabase_elearning_schema.md`
- Video comparison: `D:\Documents\research_reports\video-embedding-comparison.md`
- Gamification data: `D:\Documents\research_reports\gamification-elearning-research.md`
- LMS analytics: `D:\Documents\research_reports\lms_analytics_research.md`
