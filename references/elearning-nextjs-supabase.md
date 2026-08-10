# Elearning Platform — Next.js + Supabase Techstack Reference

Live-sourced library research (August 2025) for building a minimal full-stack elearning app with Next.js 15 App Router + Supabase (auth + database). Use this as a starting reference for any elearning platform research task.

---

## Minimal Recommended Stack

```
next@15                      # App Router, Server Actions
@supabase/supabase-js        # auth + database client
@supabase/ssr               # Next.js App Router cookie auth helpers
react-player                 # video (YouTube / Vimeo / HLS in one component)
@tiptap/react + starter-kit  # rich text authoring (instructor-facing editor)
dompurify                    # sanitize HTML before dangerouslySetInnerHTML
@react-pdf/renderer         # server-side PDF certificate generation
zod                          # validate all API inputs
react-onesignal              # push notifications (free tier, managed)
```

---

## Auth Library Comparison

| Library | GitHub | License | Notes |
|---------|--------|---------|-------|
| `@supabase/supabase-js` | 4.5k ⭐ (client) | Apache-2.0 | Use with `@supabase/ssr` for Next.js App Router |
| `next-auth` v5 | 28.3k ⭐ | MIT | Use with `@auth/supabase-adapter` if you prefer NextAuth DX over Supabase Auth UI |

**Recommendation:** Use `@supabase/supabase-js` + `@supabase/ssr` directly. Supabase Auth covers email/password, magic link, and OAuth (Google, GitHub, Apple, Azure AD, 20+ more). No separate NextAuth needed unless you want NextAuth's provider ecosystem and `SessionProvider` pattern.

**Key packages:**
```
npm install @supabase/supabase-js @supabase/ssr
```

- **`@supabase/supabase-js`** — Isomorphic client (browser + Node). Auth calls + database queries.
- **`@supabase/ssr`** — Required for Next.js 14/15. `createServerClient` for Server Components/Route Handlers; `createBrowserClient` for Client Components; middleware for session refresh.
- **`@supabase/auth-ui`** (optional) — Pre-built embeddable auth widget. Reduces boilerplate for email/password + OAuth flows.

---

## Video Embed Libraries

| Library | GitHub | License | Best For |
|---------|--------|---------|---------|
| `react-player` | 10.3k ⭐ | MIT | All-in-one: YouTube, Vimeo, HLS, DASH, Facebook, Twitch, SoundCloud, 20+ sources. One component. |
| `hls.js` | 16.9k ⭐ | Apache-2.0 | Native HLS adaptive bitrate streaming with full quality-level control. Does NOT handle YouTube/Vimeo. |

**Recommendation:**
- `react-player` for simplest implementation covering all common video sources (YouTube, Vimeo, HLS via `customHLS`).
- `hls.js` directly only when you need HLS quality-selector UI or fine-grained stream control.

```tsx
// react-player — handles YouTube, Vimeo, HLS via customHLS
import ReactPlayer from 'react-player';
<ReactPlayer url={videoUrl} controls width="100%" height="100%" />
```

```tsx
// hls.js — native HLS only
import Hls from 'hls.js';
useEffect(() => {
  if (Hls.isSupported() && videoRef.current) {
    const hls = new Hls({ startLevel: -1 }); // auto quality
    hls.loadSource(hlsUrl);
    hls.attachMedia(videoRef.current);
  }
}, [hlsUrl]);
```

---

## Rich Text Editor Libraries

| Library | GitHub | License | Notes |
|---------|--------|---------|---------|
| `tiptap` | 37.9k ⭐ | MIT | Headless (no built-in UI — you build toolbar). Most extensible. Best long-term DX. |
| `react-quill` (Quill base) | ~47.3k ⭐ (base editor) | BSD-3 | Batteries-included WYSIWYG. Faster setup, less flexibility. Base editor less actively maintained. |

**Recommendation:** `tiptap` — headless architecture is more maintainable and future-proof. Starter Kit includes Bold, Italic, Strike, Code, H1–H3, Lists, Blockquote, HR, History.

```bash
npm install @tiptap/react @tiptap/pm @tiptap/starter-kit \
  @tiptap/extension-link @tiptap/extension-image @tiptap/extension-placeholder
```

**Security:** Always sanitize editor output with `dompurify` before storing/displaying:
```tsx
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />
```

---

## Quiz / Auto-Grading

No specialized library needed. Pure Supabase + TypeScript:

```typescript
// Grading logic in a Server Action or Route Handler
async function gradeSubmission(quizId: string, answers: number[]) {
  const { data: options } = await supabase
    .from('quiz_options')
    .select('question_index, correct_index')
    .eq('quiz_id', quizId)
    .order('question_index');

  let correct = 0;
  options?.forEach((opt, i) => {
    if (opt.correct_index === answers[i]) correct++;
  });
  const percentage = Math.round((correct / options.length) * 100);
  return { correct, total: options.length, percentage, passed: percentage >= 70 };
}
```

Store quiz submissions in `quiz_submissions` table with RLS so only the owner can read/write them.

---

## PDF Certificate Generation

| Library | GitHub | License | Notes |
|---------|--------|---------|---------|
| `@react-pdf/renderer` | 16.7k ⭐ | MIT | React component model. Server-side capable (Route Handlers, Server Actions). |
| `pdfkit` | 10.7k ⭐ | MIT | Imperative API. More powerful for complex/large PDFs. |
| `puppeteer` | ~93k ⭐ | Apache-2.0 | Full CSS support via headless Chrome. Heavyweight, serverless-unfriendly. |

**Recommendation:** `@react-pdf/renderer` for server-side generation in Next.js.

```typescript
// app/api/certificate/route.ts
import { renderToBuffer } from '@react-pdf/renderer';
import { CertificatePDF } from '@/components/CertificatePDF';

export async function POST(req: Request) {
  const { userName, courseName, certificateNumber, issuedAt } = await req.json();
  const buffer = await renderToBuffer(
    <CertificatePDF userName={userName} courseName={courseName}
                     certificateNumber={certificateNumber} issuedAt={issuedAt} />
  );
  return new Response(buffer, { headers: { 'Content-Type': 'application/pdf' } });
}
```

Fonts: `@react-pdf/renderer` bundles Helvetica by default. Custom fonts (e.g., script font for "Certificate of Completion") require `Font.register()` with a bundled `.ttf`.

---

## Push Notifications

| Provider | GitHub | License | Free Tier | Notes |
|----------|--------|---------|-----------|-------|
| OneSignal (`react-onesignal`) | 86 ⭐ (SDK) | Simplified BSD | 30k web push subscribers/month | SaaS, managed infrastructure, no server needed |
| Supabase Edge Functions | — | — | 500k invocations/month | Programmable. Use for scheduled reminders via cron. Combine with OneSignal API. |

**Recommendation:** `react-onesignal` for simplicity. Supabase Edge Functions as a cron scheduler that calls OneSignal's REST API for streak reminders.

```tsx
// Initialize once in root layout (Client Component)
import { init } from 'react-onesignal';
init({ appId: process.env.NEXT_PUBLIC_ONESIGNAL_APP_ID! });
```

---

## Supabase Schema — Core Tables

```
profiles          -- extends auth.users
courses           -- course metadata
lessons           -- lesson content (HTML or video URL)
quizzes           -- one quiz per lesson
quiz_options      -- MCQ questions + correct answers
lesson_progress   -- per-user per-lesson completion
quiz_submissions  -- graded attempts
streaks           -- daily activity tracking
certificates      -- issued certificates
```

**Key RLS pattern:**
```sql
-- Progress/submissions/streaks: private to owner
alter table public.lesson_progress enable row level security;
create policy "Users manage own progress"
  on public.lesson_progress for all to authenticated
  using (auth.uid() = user_id);
```

---

## All Libraries Summary Table

| Category | Package | GitHub ⭐ | License |
|----------|---------|-----------|---------|
| Video (all-in-one) | `react-player` | 10.3k | MIT |
| Video (HLS native) | `hls.js` | 16.9k | Apache-2.0 |
| Rich text editor | `tiptap` | 37.9k | MIT |
| Rich text (quick) | `react-quill` | ~2.3k (wrapper) | MIT |
| Auth + DB client | `@supabase/supabase-js` | 4.5k | Apache-2.0 |
| Auth SSR helpers | `@supabase/ssr` | — | Apache-2.0 |
| Auth (alt) | `next-auth` | 28.3k | MIT |
| PDF generation | `@react-pdf/renderer` | 16.7k | MIT |
| PDF (imperative) | `pdfkit` | 10.7k | MIT |
| Push notifs | `react-onesignal` | 86 | BSD |
| Schema validation | `zod` | 33k+ | MIT |
| HTML sanitization | `dompurify` | 14k+ | MIT |

---

## Sources (all live-sourced August 2025)

- Supabase: https://github.com/supabase/supabase
- Supabase JS: https://github.com/supabase/supabase-js
- NextAuth: https://github.com/nextauthjs/next-auth
- react-player: https://github.com/cookpete/react-player
- hls.js: https://github.com/video-dev/hls.js
- Tiptap: https://github.com/ueberdosis/tiptap
- Quill: https://github.com/slab/quill
- @react-pdf/renderer: https://github.com/diegomura/react-pdf
- pdfkit: https://github.com/foliojs/pdfkit
- react-onesignal: https://github.com/OneSignal/react-onesignal
