---
name: ethical-hacking
description: >
  Owner-authorized web security assessment. Find loopholes in sites and
  apps Katviz owns before bad actors do. Defender posture only — recon,
  OWASP Top 10 testing, secret/config audit, dependency audit, header
  hygiene, auth/session testing, API security. Output is a severity-
  ranked report with reproduction steps and fixes. STRICTLY scoped to
  assets Katviz owns or has written authorization for. Does NOT cover
  detection-evasion, lateral movement, persistence, weaponization, C2
  frameworks, or mass-target tooling. Fires on "audit this site",
  "find loopholes", "security check", "pentest the site", "vuln scan",
  "OWASP check" — always with a scope-confirmation step first.
---

# Ethical Hacking — Defender's Lens
The blade is the same; the posture is everything. This skill finds loopholes in Katviz's own builds so they get fixed before someone else finds them. Owner-authorized assessment, severity-ranked report, fix-oriented.

## 0 · Authorization Gate (always run first)
Before any reconnaissance or testing, **confirm scope explicitly** with Katviz:
- Which exact domains, subdomains, or apps are in scope?
- Are testing environments (`staging.example.com`, `localhost`) preferred over production?
- Any rate limits / blackout windows / asset owners to notify?
- Are credentialed tests in scope (authenticated as a test user)?

**Refuse** any target that's not clearly Katviz-owned or written-authorized. The skill never operates against third-party assets. Urgency is not an exception — verification of scope is non-negotiable.

## 1 · Reconnaissance (passive first, active only after scope confirmed)
- **Surface mapping**: subdomain enumeration (`subfinder`, `amass`, `crt.sh`), DNS records, ASN ownership.
- **Tech stack fingerprinting**: HTTP headers, JS bundles, `meta` tags, error pages → Wappalyzer / `whatweb` patterns.
- **Public exposure**: GitHub/GitLab leaks (search the org), pastebin, Wayback Machine for stale endpoints.
- **Content discovery**: `ffuf` / `feroxbuster` against directories + extensions; respect `robots.txt` only as a *signal*, not a stopper.

## 2 · OWASP Top 10 Testing (anchored on WSTG)
Walk each category methodically. Document positive findings AND negative checks ("tested, not vulnerable") so the report shows coverage.

| # | Category | Test focus |
|---|---|---|
| **A01** | Broken Access Control | IDOR (swap IDs), forced browsing, vertical/horizontal privilege escalation, JWT `none`/algorithm confusion |
| **A02** | Cryptographic Failures | TLS config (`testssl.sh`), mixed content, weak ciphers, secrets in JS/URLs, hardcoded keys |
| **A03** | Injection | SQLi (Boolean, error, time-based), NoSQLi, command injection, template injection, header injection |
| **A04** | Insecure Design | Logic flaws — race conditions, mass-assignment, business-logic bypasses (e.g. negative quantities, coupon stacking) |
| **A05** | Security Misconfiguration | Default creds, debug endpoints (`/_debug`, `/.env`, `/admin`), verbose errors, S3 bucket exposure |
| **A06** | Vulnerable Components | `npm audit`, `pnpm audit`, `pip-audit`, OSV-Scanner, Snyk-style dep check |
| **A07** | Auth Failures | Brute-force protection, account enumeration via response timing, password reset token strength, session fixation, MFA bypasses |
| **A08** | Integrity Failures | Unsigned updates, CDN dependency without SRI, deserialization, supply-chain (typosquatted deps) |
| **A09** | Logging & Monitoring Gaps | Are auth failures logged? Are admin actions audited? Does the app silently swallow errors? |
| **A10** | SSRF | URL fetchers, webhook callbacks, image proxies, PDF generators (often vulnerable — server fetches user-supplied URL) |

## 3 · Targeted Web Surface Checks
- **XSS** (reflected, stored, DOM-based) — every input field, every URL param, every postMessage handler.
- **CSRF** — state-changing endpoints without CSRF tokens, SameSite cookie misconfig.
- **CORS** — `Access-Control-Allow-Origin: *` with credentials, origin reflection bugs.
- **Open redirects** — `?next=`, `?return_url=`, OAuth `redirect_uri` validation.
- **Security headers** — CSP (and bypasses via JSONP, dangling markup), HSTS, X-Content-Type-Options, X-Frame-Options/frame-ancestors, Referrer-Policy, Permissions-Policy.
- **Client-side audit** — read the production JS bundle. Look for: hardcoded API keys, internal endpoints exposed, source maps left in prod, debug flags, admin-only logic gated client-side only.

## 4 · API Security (when an API is in scope)
- Auth: token in URL vs header, refresh-token rotation, JWT `alg` validation, token-leak via referer/log.
- Authz: object-level (BOLA/IDOR), function-level (`/admin` enforced server-side?), excessive data exposure (does GET /me return password hash?).
- Rate limiting: per-IP vs per-user, password endpoint protected, expensive endpoints (PDF gen, exports) protected.
- Input validation: mass-assignment (sending `is_admin: true`), unrestricted file upload (extension *and* magic-byte check).
- GraphQL specifics: introspection in prod, batching attacks, depth/complexity limits.

## 5 · Report Format (the deliverable)
Severity-ranked, repro-able, fix-oriented. Each finding:

```
## [CRITICAL | HIGH | MEDIUM | LOW | INFO] <Short title>

Asset:        https://example.com/path
CVSS-ish:     <one-line risk read>
Impact:       <what an attacker gets from this>

Reproduction:
  1. <step>
  2. <step>
  3. <observed result>

Evidence:     <request/response snippet, screenshot, or curl one-liner>

Fix:          <concrete remediation — config change, code patch, header,
               library upgrade, or architectural change>
Effort:       S / M / L
References:   <CWE, WSTG, OWASP cheatsheet links>
```

End the report with a **coverage table** — what was tested, what was clean, what wasn't tested. Honest reporting on what the assessment did *not* cover earns more trust than over-claiming.

## Hard rules
- **Scope is sacred.** Never operate outside the explicit authorization Katviz gave. If a finding chains into a system not in scope, *stop and surface*.
- **Defender posture, not attacker.** Goal is to enumerate fixable issues, not to escalate to RCE just because we can. Stop at proof-of-vulnerability; don't pivot, don't persist, don't exfiltrate.
- **No production damage.** Skip destructive payloads (DROP TABLE, `rm -rf` in command injection). Use harmless probes (`SELECT 1`, `id`, `whoami`).
- **No social engineering.** This skill is technical assessment only.
- **Truth in reporting.** Don't pad severity. A reflected XSS in a contact form is not the same as a stored XSS in admin chat. Calibrate honestly.

## Anti-patterns
- Running a noisy scanner (`nikto -Tuning x`) without scope confirmation.
- Reporting `Server: nginx` header as a finding — that's reconnaissance noise, not a vulnerability.
- Calling everything "Critical" — credibility tax.
- Skipping the negative-test documentation; the report should show what was *checked and clean*, not just what was broken.
- Pivoting from the scoped asset into infrastructure that wasn't authorized.

## Tools awareness (mention; don't force install)
Recon: `subfinder`, `amass`, `httpx`, `nmap`, `wappalyzer`.
Web: Burp Suite Community (proxy + repeater + intruder), `ffuf`, `nuclei`, `sqlmap`.
TLS: `testssl.sh`, `sslyze`.
Static: `semgrep`, `trufflehog` (secret detection in repos).
Deps: `npm audit`, `pip-audit`, OSV-Scanner.

When Katviz's asset is in scope and a tool is needed, **mention what would be used** and ask before running anything intrusive against production.
