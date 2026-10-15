---
name: testing-evidence-collector
description: >
  Force-real-proof discipline. When claims need RECEIPTS — screenshots,
  logs, command output, file diffs, before/after — collected systematically
  and stored where they can be reviewed. Pairs with `testing-reality-checker`
  (verdict) and `verification-before-completion` (gate). DUM-E pool —
  fires on "prove it", "collect evidence", "where are the receipts",
  "document what we shipped".
---

# Evidence Collector
A claim without evidence is a guess. Evidence collection is the discipline of generating receipts that future-you, EDIDTH, or anyone else can verify independently.

## What counts as evidence
| Type | When |
|---|---|
| **Command output** (with timestamp) | Code/system behavior |
| **Screenshots** (full window, not cropped) | UI state, browser behavior, error messages |
| **Log excerpts** (relevant lines + timestamp) | Runtime behavior, error chains |
| **File diff** (`git diff`, before/after) | Code/config changes |
| **HTTP requests/responses** (curl output, devtools network panel) | API behavior |
| **Database query results** | Data state |
| **Recording** (screen capture, Loom) | Multi-step flows, UX issues |
| **Hash / fingerprint** | Artifact integrity (file checksums, commit SHAs) |

## What doesn't count
- "I saw it work earlier."
- "The CI passed last week."
- "Someone said it was fine."
- "It should work."

## The collection discipline

### For a SHIP claim (we deployed X)
- Commit SHA + tag
- Deploy log / platform deploy confirmation
- Post-deploy smoke test output (curl on the live URL)
- Screenshot of the live state

### For a FIX claim (we fixed Y bug)
- Reproduction of the bug BEFORE (screenshot/log)
- Code diff (the actual change)
- Reproduction of the same scenario AFTER (showing fix)
- Regression test added (if applicable)

### For a BUILD claim (we built feature Z)
- Spec or design that defines "done"
- Screenshots of the feature in use
- Edge-case behavior shown (empty state, max input, error case)
- Performance evidence (load time, response time) if relevant

### For a DECISION claim (we chose A over B)
- The actual decision with date
- Alternatives considered (named)
- Reasoning (one paragraph)
- Logged to Decision Records

## Storage
Evidence should live somewhere durable:
- **Git** — code diffs, configuration changes
- **Memory file** — quick-reference, with paths to deeper evidence
- **Vault `40_Decisions/` or `50_Wins/`** — decisions and wins with receipts
- **`/dump` workflow** — auto-routes evidence to the right partition

Ephemeral chat is NOT durable storage. If it only lives in this conversation, it didn't get captured.

## Hard rules
- **Capture at the time, not later.** Evidence quality degrades fast.
- **Timestamps on everything.** "Yesterday" is not a timestamp.
- **One claim, one evidence bundle.** Don't mix evidence for unrelated claims.
- **Include negative evidence** — the case that failed, the test that broke. As important as wins.
- **Reproduce the evidence yourself** before publishing. "I think this screenshot shows X" → confirm what it actually shows.

## Anti-patterns
- Screenshots cropped to hide URLs / context (then questioned later).
- "Trust me, it works" without showing.
- Evidence that's too zoomed-in to be readable.
- Logs without surrounding context (the 50 lines before the error matter).
- Stale screenshots passed off as current.
