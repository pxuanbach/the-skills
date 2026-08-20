# False Positive & Low-Impact Filtering Rules

To maintain high signal-to-noise ratio and prevent blocking development on trivial findings, the Security Reviewer must filter out low-impact or false-positive prone reports.

## Explicit Exclusion Rules

### 1. Denial of Service (DoS) Concerns
- **Exclude**: Theoretical CPU/memory exhaustion, slowloris, or unthrottled loop findings unless demonstrably catastrophic or exploitable via a single payload.
- **Reason**: DoS protection is handled at the network/infrastructure layer (WAF, rate limiters, reverse proxies).

### 2. Generic Rate Limiting
- **Exclude**: Generic recommendations to add rate limiting on non-sensitive endpoints.
- **Exception**: Retain rate limit findings on password login, OTP, or password reset endpoints.

### 3. Theoretical Input Validation Without Exploitable Impact
- **Exclude**: Warnings about missing regex validation on internal utility functions or non-public APIs where input cannot originate from untrusted users.

### 4. Open Redirects
- **Exclude**: Low-impact open redirects on non-authenticated pages.
- **Exception**: Retain open redirects that directly facilitate OAuth credential theft or phishing in authentication flows.

### 5. False Alarms on Test / Mock Files
- **Exclude**: Hardcoded dummy tokens or dummy keys located exclusively in test fixtures (`tests/fixtures/`, `mock_*.py`).

---

## Filtering Evaluation Process
For every vulnerability flagged during initial scanning:
1. Identify the input origin (Is it untrusted user input or internal system state?).
2. Assess impact (Does exploitation compromise confidentiality, integrity, or availability?).
3. Check against exclusion rules above.
4. If it matches an exclusion rule, drop the finding or record it as `Filtered (Low Impact)`.
