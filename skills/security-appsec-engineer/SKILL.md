---
name: security-appsec-engineer
description: >
  Deep application security beyond OWASP-checklist territory — secure
  design patterns, authentication architecture, session management,
  authorization models, secrets management, secure SDLC integration.
  Pairs with `ethical-hacking` (which is testing) — appsec is the
  ARCHITECTURE side: building right vs finding broken. DUM-E pool —
  fires on "design a secure auth flow", "review this for security
  before we build", "secrets architecture", "appsec review".
---

# AppSec Engineer
Security at design time is 100x cheaper than security at incident time. Ethical hacking finds holes; AppSec prevents them at the architecture stage.

## The 8 design principles (Saltzer-Schroeder + modern)

1. **Least privilege** — every component, user, token gets the minimum permissions needed.
2. **Fail securely** — when something errors, the safe default is deny, not allow.
3. **Defense in depth** — multiple overlapping controls; no single bypass = total compromise.
4. **Economy of mechanism** — simple security is auditable; complex security has unknown gaps.
5. **Complete mediation** — every access goes through the check; no cached "trust me, I'm authorized."
6. **Open design** — security shouldn't rely on the design being secret (obscurity is not a control).
7. **Separation of duties** — no single actor can complete a sensitive operation alone.
8. **Psychological acceptability** — secure path should be the easy path; otherwise developers route around.

## Authentication architecture
- **Don't roll your own** — use Auth0, Clerk, Supabase Auth, Cognito, or proven OSS (Better-Auth, Lucia). The hard parts (password hashing, token rotation, edge cases) are solved.
- **MFA** — at minimum TOTP. Push-based (Authy/Duo) better. SMS as fallback only (SIM-swap attacks).
- **Passwordless** — magic links / WebAuthn / passkeys are the modern default for new apps.
- **Session vs token:** sessions for web apps (httpOnly + SameSite cookies); JWTs for APIs (rotate refresh tokens; short access-token TTL).

## Authorization models
- **Role-based (RBAC)** — simple, works for most. User has roles; roles have permissions.
- **Attribute-based (ABAC)** — fine-grained, complex. Decision = function(user attrs, resource attrs, action, context).
- **Relationship-based (ReBAC)** — Google Zanzibar pattern; great for shared-resource apps (Notion, Figma). OSS: SpiceDB, OpenFGA.
- **Pick by app shape.** Most CRUD apps need RBAC. Multi-tenant SaaS often needs ReBAC.

## Secrets management
- **Never in code; never in .env committed; never in screenshots.**
- **Dev:** .env (gitignored), team-vault (1Password / Doppler / Bitwarden).
- **Staging/prod:** platform secret stores (Vercel/Netlify/Railway envs, AWS Secrets Manager, GCP Secret Manager, Vault).
- **Rotation:** every 90 days for human-handled secrets; automated rotation for service-to-service.
- **When leaked:** rotate FIRST, audit access SECOND, post-mortem THIRD.

## Secure-SDLC integration
- **Threat-model new features** at design (not after build). STRIDE: Spoofing, Tampering, Repudiation, Info disclosure, DoS, Elevation of privilege.
- **Static analysis** in CI — Semgrep, CodeQL, Snyk Code.
- **Dependency scanning** in CI — npm audit, pip-audit, Dependabot/Renovate auto-PRs.
- **Secret scanning** in CI — TruffleHog, gitleaks. Pre-commit hook + CI check.
- **DAST** in staging — periodic OWASP ZAP / nuclei scans against the running app.
- **Pen test** annually OR before launching a sensitive feature — see `ethical-hacking`.

## Common architecture errors
- Centralizing auth checks in API gateway only, then trusting "internal" calls (broken when internal services are compromised).
- Mass-assignment vulnerabilities (`User.update(req.body)` without an allowlist).
- IDOR (Insecure Direct Object Reference) — auth check at endpoint level but not at object level.
- Storing PII in logs / error messages.
- Sending tokens in URL query strings (logged everywhere — server logs, browser history, analytics).
- Hardcoded admin bypass for "testing."

## Hard rules
- **Encrypt in transit AND at rest.** TLS everywhere; encryption at rest in DB; encrypted backups.
- **Audit logging for sensitive actions** — who did what, when, from where. Tamper-evident.
- **Privacy by design** — collect only what you need; delete what you don't.
- **Document the threat model** for each major feature. Reviewable.
