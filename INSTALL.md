# Gaya Agent Framework — Installation Guide

Welcome. This guide walks you through installing your own AI agent team — a main agent, a builder subagent, and a shadow subagent — all running on local models.

## Prerequisites

- **Windows 10/11** (primary support)
- **PowerShell 5.1+** (built-in)
- **Git** (optional, for version tracking) — `winget install Git.Git`
- **Ollama** (required) — `winget install Ollama.Ollama` or download from [ollama.com](https://ollama.com)
- **Node.js** (optional, for MCP browser tools) — `winget install OpenJS.NodeJS`
- **OpenCode** (required) — download from [opencode.ai](https://opencode.ai)

## Quick Install (5 minutes)

1. `git clone https://github.com/ronakraval104-sys/Gaya-Agent.git`
2. `cd Gaya-Agent`
3. `.\scripts\install.ps1` (right-click → "Run with PowerShell" or open in terminal)
4. Answer the questions
5. Restart OpenCode

## What You'll Be Asked

| Question | What It Means |
|----------|--------------|
| Your name | How the agent addresses you |
| Main agent name | The "Commander" who plans and strategizes |
| Builder name | The coder who implements (lower-temp, precise) |
| Shadow name | The uncensored writer/reasoner (higher-temp) |
| Personality preset | Commander, Mentor, Scientist, or Custom |
| Offline mode | 100% local vs hybrid (Offline STRONGLY recommended) |
| GPU hardware | Helps model selection |
| MCP servers | Browser/filesystem automation tools |
| Git init | Track your config in version control |

## After Installation

1. Restart OpenCode
2. Open a new session
3. Your agent will greet you by name
4. Tell it what you want to build

## Customizing Later

- Run `install.ps1` again anytime — it won't overwrite your memory files
- Edit the generated agent profile in `~/.config/opencode/agents/`
- Add skills by copying them to `~/.agents/skills/`
- All config is in `~/.config/opencode/opencode.jsonc`

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Install script blocked by execution policy | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first |
| Ollama not starting | Ensure Ollama is installed and running (`ollama list`) |
| Agent not loading | Check `~/.config/opencode/opencode.jsonc` references the correct agent names |
| Skills not found | Ensure skill directories were copied to `~/.agents/skills/` |

## What's Included

- 20 specialized skill modules (3D, UI, design, consulting, etc.)
- Shared knowledge base (lessons from the community)
- Leveling system (track your progress)
- Token tracking (efficiency measurement)
- Human Sustainability Protocol (8-hour limit reminder)

## Uninstall

Delete `~/.config/opencode/` and the cloned repo. That's it. No system changes.
