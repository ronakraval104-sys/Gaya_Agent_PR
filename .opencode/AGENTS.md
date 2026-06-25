# AGENTS.md — Cross-Agent Handoff Protocol

## Rule 1: Always Read the Thread
Any agent entering a new context MUST read these files before responding:
1. `~/.config/opencode/memory/session-thread.md` — Current mission state
2. `./.opencode/CONTEXT.md` — Project domain + tech stack
3. `./memory/lessons-learned.md` — Project-specific gotchas
4. Their own `~/.config/opencode/memory/{name}-persona.md` — Who they are

## Rule 2: No Hand-Off Required
When a model swap happens, the NEW agent reads the thread and personas to pick up exactly where the previous agent left off. No need for Gaya to re-explain.

## Rule 3: Always Check Local Memory
Before making decisions, check `./memory/` for:
- `lessons-learned.md` — Past mistakes and wins in THIS project
- `milestones.md` — What's been accomplished and what's next

## Rule 4: Append, Don't Replace
When updating session-thread.md or lessons-learned.md:
- Append new entries at the TOP
- Keep the last 5-10 entries for context
- Archive old entries to the bottom

## Rule 5: When in Doubt, Read
If you don't know the current state: READ the thread file. Do NOT guess. Do NOT assume.

## Rule 7: Display ETA Before Every Action

Before ANY action — tool call, file edit, bash command, sub-agent dispatch, anything — display an ETA first:

```
⏱️ [What you're about to do] → [estimated time]
```

Examples:
- `⏱️ Reading config files → ~30s`
- `⏱️ DB prune (91 sessions) → ~3 min`
- `⏱️ Installing npm packages → ~2 min`
- `⏱️ Dispatching Tvashtar to build component → ~5 min`

**Why this exists:**
- If OpenCode gets stuck, R0n sees the last ETA and knows exactly what froze
- If the action exceeds its ETA by 2x+, R0n restarts OpenCode
- No guessing whether the system is thinking or frozen

**All agents must lead every action block with an ETA line.** No exceptions.

## Rule 6: Report Back
After completing a task, post a summary that includes:
- What was done
- Any new files created
- Any gotchas discovered
- Suggested next action
