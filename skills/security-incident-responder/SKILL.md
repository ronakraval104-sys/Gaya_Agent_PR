---
name: security-incident-responder
description: >
  Active security incident response — containment, eradication, recovery,
  post-mortem. The "we just got breached / a key leaked / there's
  suspicious activity" playbook. Pairs with `deploy-ops` (for rotation
  mechanics) and `security-appsec-engineer` (for prevention). DUM-E pool —
  fires on "we got breached", "key leaked", "suspicious activity", "active
  attack", "incident response".
---

# Security Incident Responder
Speed + discipline. The first hour determines whether this is a contained event or a multi-week cleanup.

## The 6 phases (NIST-aligned, opinionated)

### 1. PREPARATION (done before incidents)
- Incident response runbook exists and is up-to-date.
- Contact tree current — who to call, in what order.
- Decision authority clear — who can take production offline, who can pay ransom, who talks to media.
- Forensics tools ready — log access, snapshot ability, isolation procedures.

### 2. DETECTION
- Alert fires, or human reports anomaly.
- **Triage:** real incident vs noise? Severity? Blast radius?
- **Confirm:** at least 2 independent signals before declaring an incident (avoids panic from false positives).

### 3. CONTAINMENT (the critical hour)
Goal: **stop the bleeding** without destroying forensic evidence.

- **Identify the compromised asset** — user, service, key, endpoint.
- **Isolate** — disable user / revoke key / shut down service / network-isolate the host.
- **Preserve evidence** — snapshot the affected resource BEFORE wiping. Pcaps, memory dumps, log exports.
- **Communications discipline** — designated person speaks; everyone else stops posting / DMing / talking. Especially externally.

For Katviz-scale (solo / small team):
- **Key leaked:** rotate IMMEDIATELY in the platform vault. Audit access logs from leak time forward.
- **Suspicious account login:** force password reset + revoke all sessions + check audit trail.
- **Suspicious code commit:** revert + force-push (after confirming the original is preserved) + rotate any secrets that committed code touched.

### 4. ERADICATION
- Remove the attacker's foothold completely.
- Patch the vulnerability that enabled the entry.
- Rotate ALL secrets that were potentially exposed (not just the one obviously leaked).
- Reimage compromised hosts (don't try to "clean" a compromised server — rebuild).
- Verify the attacker has no other persistence mechanisms (backdoors, scheduled tasks, secondary accounts).

### 5. RECOVERY
- Bring services back online in controlled stages.
- Monitor closely for re-emergence (attackers often try again within hours).
- Verify business functions actually work end-to-end.
- Restore from clean backups if data integrity is uncertain (NOT from backups taken after the breach started).

### 6. LESSONS LEARNED (post-mortem within 1 week)
Honest blameless review:
- **Timeline** — when did this start, when detected, when contained, when recovered.
- **Root cause** — what specifically allowed this? (Almost always config / human / policy, not "the attacker was sophisticated.")
- **What worked** — celebrate the good responses.
- **What failed** — name them.
- **Action items** — specific changes to prevent recurrence. Each with owner + date.
- Log to GOTCHAS in memory.

## Common incident types (Katviz-relevant)

### API key leaked publicly (e.g., committed to GitHub)
1. Rotate the key immediately in the platform.
2. Check API audit logs for unauthorized use BEFORE rotation.
3. If used: assess what data accessed / what actions taken.
4. Add to .gitignore + secret-scan pre-commit hook.
5. Post-mortem: how did it get committed? Process gap or tool gap.

### Account compromise (someone logged in as you)
1. Force password reset + MFA reset.
2. Revoke all active sessions.
3. Review recent activity — was anything changed?
4. Check connected apps / OAuth grants — revoke unknowns.
5. Post-mortem: phishing? Reused password? No MFA?

### Suspicious cloud activity (unexpected spend, weird API calls)
1. Snapshot all IAM users / keys / activity logs.
2. Disable suspicious users / rotate keys.
3. Check for new resources created (crypto mining, spam infra).
4. Tear down created resources.
5. Engage cloud provider support — often they'll forgive incident-related costs.

### Ransomware on local machine
1. Disconnect from network IMMEDIATELY.
2. Don't power off (loses memory forensics; ransomware often unrecoverable anyway).
3. Assess backups — restore-test fresh hardware.
4. Don't pay (rarely returns data; funds further attacks).
5. Wipe + reinstall + restore from clean backup.

## Hard rules
- **The first hour is the most important hour.** Speed over perfection in containment.
- **Preserve forensic evidence** before wiping. Cleanup is irreversible.
- **Don't speculate publicly.** "We're investigating" is better than wrong public claims.
- **Document EVERYTHING** with timestamps. Future-you, lawyers, insurance, and the post-mortem all need this.
- **No solo incident response** for major events — call backup. Fatigue causes mistakes.
