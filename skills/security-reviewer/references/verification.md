# Finding Claims & Independent Verification

Two rules adapted from cloudflare/security-audit-skill: every finding states a concrete trust-boundary claim, and the agent that confirms a finding is never the agent that found it.

## 1. Claim fields (required for every high/medium `confirmed` or `needs_validation` finding)

| Field | Question it answers | Good | Not acceptable |
|---|---|---|---|
| **Attacker** | Who is the lower-trust principal? | "Unauthenticated internet user", "Logged-in user of tenant A" | "An attacker" |
| **Entry Point** | Which input or action do they control? | "`POST /api/users/[id]` body `role`", "Server Action `deleteItem(id)`" | "User input" |
| **Boundary** | Which control is supposed to stop them, and how is it crossed? | "Ownership check missing: `db.item.delete({where:{id}})` has no `userId` filter" | "No validation" |
| **Impact** | What concrete resource/result does the attacker gain? | "Delete any other user's items", "Read every row of `users` via SQLi" | "Could be dangerous" |

If you cannot fill **Attacker** and **Impact** with something concrete, it is not a vulnerability: reject it or list it under the filter log. A missing best practice, a theoretical input, or self-impact is not a finding.

## 2. Independent verification

**Applies to:** every high/medium finding you intend to mark `confirmed` — automated (`findings.json`) or from the manual audit — before the report is written.

**Who verifies:** a fresh sub-agent (use the platform's delegation mechanism). Give it only:
- the finding record: ID, `file:line`, the four claim fields;
- read access to the repository.

Do **not** pass your triage reasoning, your notes, or the other findings — the verifier must reach its own conclusion from source.

**Verifier prompt** (copy as-is, fill the placeholders):

```
You are verifying one security finding. Your job is to DISPROVE it if you can.
Finding: <ID> at <file:line>
Attacker: <...>   Entry Point: <...>   Boundary: <...>   Impact: <...>

1. Start from the entry point and trace to the sink. Read every file on the path.
2. Look for a control that blocks the attack: auth middleware/matcher, router-level
   dependencies, input validation/schema, ORM parameterization, framework escaping,
   ownership filter, unreachable code, constant input, dev/test-only code.
3. Answer with exactly one verdict:
   - upheld      — the path is reachable and no control blocks it. Give the trace (file:line → file:line).
   - disproved   — cite the file:line of the control that blocks it.
   - unresolved  — name the exact fact outside the source that decides it (proxy, IdP, deploy config).
Do not suggest fixes. Do not report other issues.
```

**Mapping back to the report:**

| Verifier verdict | Final verdict | Report |
|---|---|---|
| `upheld` | `confirmed` | Triage row `Verifier = upheld`; finding goes to Actionable Findings with `**Verification**: upheld` |
| `disproved` | `rejected` | Triage row `Verifier = disproved`, reason = the cited control |
| `unresolved` | `needs_validation` | Triage row `Verifier = unresolved`; finding listed with the missing fact |

**No delegation available:** run the verification as a separate pass that starts from the finding record only and re-reads the code from the entry point. Write `upheld (self)` so the report states the verification was not independent.

**Many findings:** when more than 10 findings need verification, give one verifier per category (it receives all findings of that category) instead of one per finding.
