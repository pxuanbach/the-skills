# LMS Analytics — Feature Reference

Condensed findings from LMS platform research (Moodle, Canvas, Blackboard/Anthology, SCORM/xAPI). For use in elearning platform evaluation tasks.

---

## Core Metrics Tracked

### Learner Activity / Engagement
- Login frequency, session duration
- Time-on-task per module (xAPI verb: `http://adlnet.gov/expapi/verbs/initialized`)
- Pages/activities accessed
- Discussion forum participation (reads, posts, replies)
- Content completion rates

### Performance / Achievement
- Assessment scores (per item, per course)
- Pass/fail rates
- Time-to-completion vs expected
- Competency framework alignment (e.g., EQF — European Qualifications Framework)
- Certificate issuance

### Administrative / Compliance
- Cohort/enrollment counts
- Compliance training completion status
- Demographic disaggregation (for equity monitoring)
- Instructor workload (time spent grading, engaging)

---

## Dashboards by Role

### Instructor-Facing
- **Gradebook**: per-assignment, per-learner scores
- **Engagement heatmap**: activity by time-of-day / day-of-week
- **At-risk alerts**: learners predicted to fail/drop (ML-based)
- **Late-work tracker**: overdue submissions
- **Assessment item analysis**: difficulty index, discrimination index per question

### Admin-Facing
- **Platform-wide usage**: MAU/DAU, course enrollment funnel
- **Compliance status**: mandatory training completion rates
- **Cohort benchmarking**: cross-team or cross-region comparison
- **Content effectiveness**: completion vs pass-rate by content item
- **ROI metrics**: cost per learner, cost per completion

---

## Standards

### SCORM Runtime Tracking
- `cmi.core.lesson_status` — completed/incomplete/passed/failed
- `cmi.core.score.raw` — numeric score
- `cmi.core.session_time` — time spent
- Limited to packaged content; no cross-LMS portability

### xAPI / Experience API (IEEE 9274.1.1-2023)
Statement structure: `[actor, verb, object, result, context]` stored in an LRS (Learning Record Store).

```
{
  "actor": { "mbox": "mailto: learner@example.com" },
  "verb": { "id": "http://adlnet.gov/expapi/verbs/initialized" },
  "object": { "id": "http://example.com/activities/unit-1" },
  "result": { "score": { "scaled": 0.85 }, "success": true },
  "context": { "extensions": { "http://example.com/time": 3600 } }
}
```

More flexible than SCORM — tracks mobile, offline, VR, simulations, informal learning.

### Related Standards
- **CMI5**: modern profile on top of xAPI for LMS interoperability
- **AICC**: older standard, legacy HACP protocol
- **IMS Caliper**: sensor API for fine-grained behavioral tracking (annotation, forum reads, time-per-sentence)
- **Open Badges 2.0**: backpack-standard portable achievements

---

## Platform Examples

### Moodle
- `logstore_standard` — logs all events to DB
- Live logs (real-time)
- Analytics models (built-in ML for at-risk prediction)
- Competency frameworks + reporting by competency
- Plugin ecosystem for xAPI LRS integration

### Canvas (Instructure)
- Course analytics dashboard
- Predictive risk flags (flags students at risk of failing)
- Canvas Data Portal — exportable analytics (enterprise plan)
- Moderation features for assessments

### Blackboard / Anthology
- Retention Center — at-risk learner alerts
- Performance Dashboard — grade distribution, activity
- Adaptive Learning Dashboard — content recommendations
- SBAC / interoperability integrations

---

## Emerging Trends

- **AI recommendations**: personalized learning path suggestions
- **NLP sentiment analysis**: detect confusion/disengagement from discussion posts
- **Social network analysis**: identify influential learners or isolated students
- **Epistemic network analysis**: model reasoning chains
- **Real-time dashboards**: live learner status monitoring
- **Mobile-first analytics**: session-level mobile vs desktop breakdown

---

## Key Research Citations

- xAPI specification: `https://xapi.com/`
- IEEE 9274.1.1-2023 — Experience API (xAPI)
- Moodle Analytics: `https://docs.moodle.org/` — analytics models
- Canvas Data Portal: `https://community.canvaslms.com/`

---

## Related Skills

- `references/elearning-gamification-data.md` — gamification retention metrics
- `references/software-comparison-patterns.md` — for software/library comparison methodology
