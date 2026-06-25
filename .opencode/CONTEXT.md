# Project Context — OpenCode Workspace

**Last updated:** 19-Jun-2026
**Updated by:** Gaya

## Domain
General-purpose development workspace for R0n (Ronak). Contains multiple sub-projects:
- `agent-system/` — Agent framework
- `autodesk-bim/` — BIM automation with Autodesk
- `Gaya-Agent/` — Gaya agent skill development (HyperFrames video, skills)
- `god-simulator/` — Game/simulation project
- `kiosk-chatbot/` — Kiosk chatbot app
- `Ryze studio/` — Ryze brand studio work
- `Visual_chat_bot/` — Visual chatbot development
- Various Python scripts, PDF pipelines, HTML infographics

## Tech Stack
- **Runtime:** Node.js, Python 3.x
- **Rendering:** Three.js, GSAP, HyperFrames (HTML-to-video)
- **Local AI:** Ollama (qwen3:4b, phi4-mini, qwen2.5vl, qwen2.5-coder)
- **GPU:** RTX 4060 (8 GB VRAM)
- **OS:** Windows 11, PowerShell 5.1

## Active Agent System
| Agent | Model | VRAM | Role |
|---|---|---|---|
| GAYA | qwen3:4b-instruct-2507-q4_K_M | 2.5 GB | Commander/Orchestrator |
| LOGOS | phi4-mini:3.8b | 2.5 GB | Logic/Reasoning |
| FREYA | qwen2.5vl:7b | 6.0 GB | Vision/Research |
| TVASHTAR | qwen2.5-coder-fixed:7b | 4.7 GB | Coding/Architecture |

## Active Projects History
- **HyperFrames video rendering** — Completed 19-Jun-2026. 8-second GSAP timeline animation rendered at 30fps.
- **MoE framework setup** — Completed 19-Jun-2026. Four-blade local agent formation established.

## Important Paths
- Global memory: `~/.config/opencode/memory/`
- Per-agent personas: `~/.config/opencode/memory/{agent}-persona.md`
- Session thread: `~/.config/opencode/memory/session-thread.md`
- Project local memory: `./memory/`
- Architecture decisions: `./.opencode/adr/`
- Skills: `~/.agents/skills/`, `~/.config/opencode/skills/`
