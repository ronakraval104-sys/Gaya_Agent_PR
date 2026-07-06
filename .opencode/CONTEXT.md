# Project Context — Gaya Dashboard System

**Last updated:** 06-Jul-2026
**Updated by:** Gaya

## Domain
Gaya dashboard system — agent methodology dashboard + interactive skill catalog. Cleaned, focused, Gaya-only.

## Tech Stack
- **Runtime:** None (static HTML)
- **Rendering:** Vanilla HTML/CSS/JS
- **OS:** Windows 11, PowerShell 5.1

## Active Agent System
| Agent | Model | VRAM | Role |
|---|---|---|---|
| GAYA | qwen3:4b-instruct-2507-q4_K_M | 2.5 GB | Commander/Orchestrator |
| LOGOS | phi4-mini:3.8b | 2.5 GB | Logic/Reasoning |
| FREYA | qwen2.5vl:7b | 6.0 GB | Vision/Research |
| TVASHTAR | qwen2.5-coder-fixed:7b | 4.7 GB | Coding/Architecture |

## Repo Contents
- `agent-methodology-dashboard.html` — Gaya Command Center dashboard
- `skills-dashboard.html` — Interactive Gaya skill catalog (37 modules)
- `.opencode/` — Agent handoff protocol, project context
- `docs/gaya-skill.md` — Versioned Gaya skill
- `memory/` — Lessons learned and milestones

## Important Paths
- Global memory: `~/.config/opencode/memory/`
- Per-agent personas: `~/.config/opencode/memory/{agent}-persona.md`
- Session thread: `~/.config/opencode/memory/session-thread.md`
- Project local memory: `./memory/`
- Architecture decisions: `./.opencode/adr/`
- Skills: `~/.agents/skills/`, `~/.config/opencode/skills/`
