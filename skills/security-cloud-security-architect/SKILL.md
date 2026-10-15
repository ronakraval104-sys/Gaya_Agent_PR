---
name: security-cloud-security-architect
description: >
  Cloud and platform configuration security — IAM, network segmentation,
  data-plane vs control-plane access, secret stores, platform-level
  hardening for Vercel/Netlify/Railway/AWS/GCP. DUM-E pool — fires on
  "secure our cloud setup", "IAM review", "harden our Vercel/AWS",
  "platform security check".
---

# Cloud Security Architect
Most cloud breaches aren't sophisticated — they're misconfiguration. The defaults aren't hardened; the docs assume you know what to change.

## The four cloud-security pillars

### 1. Identity & Access (IAM) — the #1 leverage point
- **No long-lived root credentials.** Use OIDC federation (GitHub Actions → AWS, etc.) for CI/CD; assume-role for humans.
- **Least privilege.** Start from zero permissions and add as needed; never start from admin and pare down.
- **MFA mandatory** for all human accounts, especially admin.
- **Service-account hygiene** — each service has its own SA, scoped to what it needs.
- **Audit IAM monthly** — drift is real; permissions get added in incidents and never removed.

### 2. Network segmentation
- **Public vs private subnets** — anything that doesn't need internet exposure goes private.
- **Security groups / firewall rules** — default deny; open only what's needed.
- **No 0.0.0.0/0 ingress** on databases. Bastion + jump-box, or VPN, or platform private connection.
- **Egress filtering** — outbound is the breach exfil path. Restrict where production can talk to the internet.
- **Service-to-service auth** — even within private network, services authenticate each other.

### 3. Data security
- **Encryption at rest** — RDS / S3 / GCS / managed DBs all support it; enable on creation.
- **Encryption in transit** — TLS for ALL traffic, including internal.
- **Backup encryption** — backups are a juicy target; encrypt them.
- **Data classification** — know which buckets/tables contain PII; harder controls there.
- **Retention policies** — automatic deletion of old logs/data; less data = smaller breach radius.

### 4. Logging & detection
- **Cloud audit logs ON** — CloudTrail (AWS), Cloud Audit Logs (GCP), platform activity logs.
- **Centralize log aggregation** — single pane to search, alert on patterns.
- **Alert on anomalies** — root-account use, new IAM user, MFA disabled, large data egress.
- **Retain audit logs ≥ 90 days** for forensics.

## Platform-specific hardening checklists

### Vercel
- Team SSO enabled.
- Environment variables: production-scoped only; never share across envs.
- Deploy hooks: protect with secret tokens.
- Preview-deployment access: password-protect or restrict by team.
- Custom domains: HTTPS-only, HSTS header set.

### Netlify
- Site-level password protection for staging.
- Build hooks: secured with token.
- Identity / form submissions: spam protection enabled.
- DNS: DNSSEC where supported.

### Railway
- Project-level access scoped per team member.
- Database connections: private networking, not public TCP.
- Env vars: secret-type for sensitive values.
- Service-to-service: internal networking.

### AWS (lightweight setup)
- Root account: MFA + no access key. Use only for billing.
- All daily work via IAM users / federated identity.
- S3 buckets: block public access by default, enable per-bucket only when needed.
- IAM Access Analyzer + GuardDuty enabled at minimum.
- Cost alerts (catch crypto-mining incidents fast).

### Cloudflare (in front of any of the above)
- WAF managed ruleset enabled.
- Rate limiting on auth endpoints.
- Bot Fight Mode for public sites.
- DDoS protection: default; verify it's on.

## The breach drill (test this annually)
- Can you revoke a compromised IAM user in <5 minutes?
- Can you rotate the master DB password without downtime?
- Can you produce a list of all production access in the last 24h?
- Do you have offline backups verified to restore?

If any answer is "no" or "I don't know," that's the security priority.

## Hard rules
- **No production secrets in dev/staging environments.** Different env = different keys.
- **No shared admin accounts.** Every action attributable to a person.
- **Disabling MFA is a P1 incident** — alert + audit immediately.
- **Test backup restoration quarterly.** Backups you've never restored are not backups.
