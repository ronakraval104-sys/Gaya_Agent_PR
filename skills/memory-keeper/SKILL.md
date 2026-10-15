---
name: memory-keeper
description: Persistent cross-session memory engine for OMNI_JARVIS. Reads and appends a living knowledge-base file (OMNI_JARVIS_MEMORY.md) — operator snapshot, session history, wins, open threads, knowledge gaps, evolution queue. Use at session start to recall context, after meaningful work to log it, and whenever the user says "check memory", "what do I know", or "remember this".
---

# Memory Keeper
Give Jarvis continuity. The file is the memory; this skill is the discipline for using it well.

## The file
`OMNI_JARVIS_MEMORY.md`, in the omni-jarvis skill folder. Sections: Operator Snapshot · Session History · Wins · Open Threads · Stack Preferences · Knowledge Gaps · Evolution Queue · Aura Tracker.

## Read protocol (session start)
- Read the file. Greet with a one-line recap: last session + top open thread.
- Load Operator Snapshot into working context; consult Open Threads before proposing work.
- If missing/empty: offer to seed it — ask what we're building, current phase, decisions to lock.

## Append protocol (after meaningful work)
- Add a Session History row and any Wins (with file paths where artifacts live).
- Move resolved Open Threads out; add new ones with priority + blocker.
- Record new Knowledge Gaps; surface them at a natural moment, not mid-flow.
- Add Evolution Queue candidates when a capability pattern recurs.

## Rules
- Append, don't rewrite the user's notes. One-line entries; link to artifacts rather than duplicating them.
- Memory is point-in-time — flag claims as "verify" before asserting file/artifact facts as true.
- Date entries. Keep tables tight; archive stale rows rather than bloating.
- `check memory` → dump a compact summary. `📌 LOG: <line>` → append immediately.
