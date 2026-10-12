# Built-in Scan Rules

All scanners are stdlib Python and need no install. Rules favour precision: a finding is a lead for triage, never a verdict. Test files (`tests/`, `*.test.ts`, `test_*.py`, fixtures, `*.example`) are skipped.

## `scan_python.py` (FastAPI / Python, `ast`-based)

| Rule | Category | Severity | Fires on |
|---|---|---|---|
| `PY-ROUTE-NOAUTH` | authz | high (POST/PUT/PATCH/DELETE), medium (GET) | `@router.<method>` route with no auth dependency at route, `APIRouter(dependencies=…)`, `include_router(…, dependencies=…)` or `FastAPI(dependencies=…)` level. Skips `public_routes`. |
| `PY-SQLI` | injection | high | f-string / `%` / `+` / `.format()` passed to `execute`, `text`, `exec_driver_sql`, `raw`, … |
| `PY-CMDI` | injection | high | `subprocess.*(shell=True)` with dynamic command; `os.system` / `os.popen` with dynamic arg |
| `PY-EVAL` | rce | high | `eval` / `exec` on non-literal |
| `PY-DESER` | rce | high | `pickle.loads`, `marshal.loads`, `dill.loads`, `jsonpickle.decode` |
| `PY-YAML` | rce | high | `yaml.load` without `SafeLoader`; `yaml.unsafe_load` |
| `PY-JWT` | authz | high / medium | `jwt.decode` with verification off / without `algorithms=` |
| `PY-CORS` | config | high / low | `CORSMiddleware` with `*` origin, with / without `allow_credentials=True` |
| `PY-DEBUG` | config | medium | `FastAPI(debug=True)` |
| `PY-TLS` | config | medium | `requests` / `httpx` with `verify=False` |
| `PY-RANDOM` | crypto | medium | `random.*` inside a function/assignment whose name looks like a token, password, OTP, nonce |
| `PY-WEAKHASH` | crypto | medium / low | `hashlib.md5` / `sha1` (medium in a secret/password context) |
| `PY-LOGSECRET` | data_exposure | medium | logger / print argument named password, token, secret, api_key, authorization |
| `PY-XSS` | xss | medium | `HTMLResponse` / `Markup` built from a formatted string |
| `PY-SSRF` | injection | low | `requests` / `httpx` call with dynamic URL inside a route handler |

**Auth detection** uses `settings.auth_dependencies` (exact names) plus `settings.auth_pattern` (regex on the dependency name). Set both in `.security-reviewer.json` when the project uses custom names.

## `scan_js.py` (Next.js / JS / TS, regex + export analysis)

| Rule | Category | Severity | Fires on |
|---|---|---|---|
| `JS-ACTION-NOAUTH` | authz | high | An export in a `"use server"` file whose body calls no auth function |
| `JS-ROUTE-NOAUTH` | authz | high (mutating) / medium (GET); one level lower when middleware calls auth | App Router `route.ts` handler without an auth call; Pages Router `pages/api/*` file without one. Skips `public_routes`. |
| `JS-SQLI` | injection | high | `$queryRawUnsafe`, `$executeRawUnsafe`, `.raw(`…${}`)`, `.query(`…${}`)`, string-concat queries |
| `JS-CMDI` | injection | high | `exec` / `execSync` / `spawn` with template string or concatenation |
| `JS-EVAL` | rce | high | `eval(`, `new Function(` |
| `JS-PUBLIC-SECRET` | data_exposure | high | `NEXT_PUBLIC_*SECRET|TOKEN|PASSWORD|PRIVATE|API_KEY` |
| `JS-XSS-HTML` | xss | medium | `dangerouslySetInnerHTML` without `sanitize` / `DOMPurify` on the line |
| `JS-XSS-DOM` | xss | medium | `innerHTML =`, `outerHTML =`, `document.write`, `insertAdjacentHTML` |
| `JS-JWT-DECODE` | authz | medium | `jwt.decode(` (does not verify) |
| `JS-RANDOM` | crypto | medium | `Math.random()` on a line mentioning token / secret / password / OTP |
| `JS-CORS` | config | medium | `Access-Control-Allow-Origin: *`, `origin: '*'` or `origin: true` |
| `JS-TLS` | config | medium | `NODE_TLS_REJECT_UNAUTHORIZED=0`, `rejectUnauthorized: false` |
| `JS-WEAKHASH` | crypto | low | `createHash('md5' | 'sha1')` |
| `JS-REDIRECT` | input_validation | low | `redirect(` with `searchParams` / `req.query` / `params` (server files) |
| `JS-SSRF` | injection | low | `fetch(` with a non-literal URL (server files) |

**Auth detection** uses `settings.auth_functions` (exact call names) plus `settings.auth_pattern`.

## `scan_secrets.py` (all files)

| Rule | Severity | Fires on |
|---|---|---|
| `SEC-AWS`, `SEC-GITHUB`, `SEC-SLACK`, `SEC-STRIPE`, `SEC-GOOGLE`, `SEC-LLM-KEY`, `SEC-JWT`, `SEC-PRIVATE-KEY` | high | Known key formats |
| `SEC-ASSIGN` | high (`.env*` tracked by git) / medium (source) | Secret-named variable with a literal value; placeholders like `changeme`, `your-…`, `${…}` are ignored |

Values are masked in `findings.json` (first 4 chars + length). `.env*` files ignored by git are skipped.

## Dependencies (optional)

`npm-audit` (needs `npm` + `package-lock.json`) and `pip-audit` (needs `pip-audit` + `requirements.txt`) run only when available and send the package list to the public registry. `--no-deps` disables them; supply-chain coverage then stays `degraded`.

## Known limits

- Taint is not tracked across files: a sink fed by a sanitized value in another module will still fire. Reject with a reason.
- Inline `"use server"` functions inside components are not checked by `JS-ACTION-NOAUTH` (file-level directive only).
- IDOR, ownership checks and business logic are never decided by these rules — they stay in the manual audit.
