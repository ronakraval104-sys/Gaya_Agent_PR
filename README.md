# Gaya — Divine Commander, Philosopher, Poet of Evergrowth

> **A self-contained MoE (Mixture of Agents) system for OpenCode.**  
> Four specialized agent personas, a shared memory core, and a single-command install.  
> Runs on **local GPU (Ollama)** or **free cloud tier (OpenCode Zen / OpenRouter)**.

<div align="center">

[![One-Command Install](https://img.shields.io/badge/install-one%20command-%23a78bfa)](scripts/install.ps1)
[![License: MIT](https://img.shields.io/badge/license-MIT-%2334d399)](LICENSE)
[![OpenCode](https://img.shields.io/badge/powered%20by-OpenCode-%2338bdf8)](https://github.com/opencode-ai)
[![Agents](https://img.shields.io/badge/agents-4-%23fbbf24)](#-the-four-agents)
[![GPU](https://img.shields.io/badge/GPU-Ollama-%23fb923c)](#config-a-local-gpu-ollama)
[![Cloud](https://img.shields.io/badge/cloud-zen%20free-%23f472b6)](#config-b-no-gpu-opencloud-zen--openrouter-free)
[![Preview](https://img.shields.io/badge/preview-skills%20dashboard-%23c084fc)](https://htmlpreview.github.io/?https://github.com/ronakraval104-sys/Gaya_Agent_PR/blob/main/skills-dashboard.html)

</div>

> **Live preview:** [skills-dashboard.html](https://htmlpreview.github.io/?https://github.com/ronakraval104-sys/Gaya_Agent_PR/blob/main/skills-dashboard.html) — browse skills and agents right in your browser, no download needed.  
> **GitHub Pages:** Once enabled in repo Settings → Pages (main branch, root), the dashboard also lives at `https://ronakraval104-sys.github.io/Gaya_Agent_PR/skills-dashboard.html`.

---

## Table of Contents

- [What Is Gaya?](#-what-is-gaya)
- [Quick Install](#-quick-install)
- [The Four Agents](#-the-four-agents)
- [Two Config Modes](#-two-config-modes)
- [Architecture](#-architecture)
- [Leveling System](#-leveling-system)
- [Auto-Maintenance](#-auto-maintenance)
- [Roadmap](#-roadmap)

---

## What Is Gaya?

Gaya is **not** a single AI model. Gaya is a **command structure** — four specialized agents that work together inside OpenCode, each handling what they do best.

Named after **Bodh Gaya**, the seat of awakening where the Buddha sat beneath the Bodhi tree and saw reality as it is.

```
  ╔══════════════════════════════════╗
  ║            G A Y A               ║
  ╠══════════════════════════════════╣
  ║           ┌──────────────┐       ║
  ║           │   COMMANDER  │←Lead  ║
  ║           └───────┬──────┘       ║
  ║                   │              ║
  ║           ┌───────┴──────┐       ║
  ║           │  PHILOSOPHER │←Sage  ║
  ║           └───────┬──────┘       ║
  ║                   │              ║
  ║           ┌───────┴──────┐       ║
  ║           │     POET     │←Poet  ║
  ║           └───────┬──────┘       ║
  ║                   │              ║
  ║           ┌───────┴──────┐       ║
  ║           │  EVERGROWTH  │←Grow  ║
  ║           └──────────────┘       ║
  ╚══════════════════════════════════╝
```

**As Commander** — Leads the other three agents like an army. Assesses first, then strikes.

**As Philosopher** — Speaks through four ancient texts: the Gita (purpose), Art of War (strategy), The Prince (pragmatism), Chanakya Niti (ground truth).

**As Poet** — Writes epic tales of milestones achieved. Not a changelog. A campaign chronicle.

**As Evergrowth** — Every task, success, failure, and waste is **experience encoded**. Next time is faster because the path is already walked.

> *"Do the work. Don't chase the win. The win comes when the work is good."*  
> — Gita (modern)

---

## Quick Install — Two Paths

### Prerequisites

- [OpenCode CLI](https://github.com/opencode-ai) installed and configured
- **GPU mode:** [Ollama](https://ollama.ai) installed and running

### Path A: Paste URL (instant, cloud mode)

Just paste the repo URL into OpenCode. The root-level `opencode.jsonc` loads all 4 agents on **cloud free tier** immediately — no install script needed.

```
OpenCode
  → Add Repo
  → https://github.com/ronakraval104-sys/Gaya_Agent_PR.git
  → Gaya loads with 4 agents on Zen + OpenRouter free tier
```

Agents load with cloud models (Big Pickle, DeepSeek V4 Flash Free, MiMo V2.5 Free, North Mini Code Free). Zero configuration, zero payment.

### Path B: Run install.ps1 (full power)

```powershell
git clone https://github.com/ronakraval104-sys/Gaya_Agent_PR.git
cd Gaya_Agent_PR
.\scripts\install.ps1
```

#### Fresh Install
Asks **2 questions**:
1. Your name (for persona personalization)
2. GPU available? (auto-detected, overrideable)

It generates `~/.config/opencode/opencode.jsonc`, installs all agent files, pulls Ollama models (GPU mode), and sets up auto-maintenance.

#### Upgrade / Re-run
Run the **same script** again to upgrade:

```
.\scripts\install.ps1
  → "Existing install detected: v2.0.0"
  → "Latest is v2.1.0 — upgrade?"  (checks GitHub releases)
  → OR: "Already latest. Reinstall? Switch mode? Repair?"
```

The script:
- **Detects** your installed version (reads `.gaya-version` file)
- **Checks** GitHub for newer releases automatically
- **Backs up** existing config before touching anything
- **Preserves** your memory files and persona edits
- **Never deletes** — upgrades in place

One script to rule them all. Install, upgrade, switch modes, repair — all with a single command.

---

## The Four Agents

| Agent | Role | GPU Model | Cloud Model | VRAM |
|---|---|---|---|---|
| **Gaya** | Commander, Orchestrator, Philosopher | `qwen3:4b-instruct-2507-q4_K_M` | Big Pickle (Zen) | 2.5 GB |
| **LOGOS** | Logic, Skeptic, Deep Reasoning | `phi4-mini:3.8b` | DeepSeek V4 Flash Free (OpenRouter) | 2.5 GB |
| **Freya** | Vision, Research, Unrestricted | `qwen2.5vl` | MiMo V2.5 Free (Zen) / Nemotron 3 Ultra Free (fallback) | 6.0 GB |
| **Tvashtar** | Coding, Architecture, Refactoring | `qwen2.5-coder-fixed:7b` | North Mini Code Free (OpenRouter) | 4.7 GB |

### VRAM Strategy (GPU Mode)

With 8 GB VRAM (RTX 4060), only **2 models active at once**:

| Active Agents | VRAM Used | Notes |
|---|---|---|
| Gaya + LOGOS | 5.0 GB | Default pair for planning + reasoning |
| Gaya + Tvashtar | 7.2 GB | Heavy coding sessions |
| Freya (solo) | 6.0 GB | Vision/research tasks |
| Gaya + Freya | 8.5 GB | ❌ Exceeds VRAM — avoid pairing |

`OLLAMA_KEEP_ALIVE=0` is set by default — models release VRAM instantly when idle.

---

## Two Config Modes

### Config A: Local GPU (Ollama)

Best for: users with a dedicated GPU (6+ GB VRAM)

- All 4 models run locally via Ollama
- Zero latency, zero API calls, fully offline
- `install.ps1` auto-pulls the correct models

### Config B: No-GPU / Cloud (OpenCode Zen + OpenRouter Free)

Best for: users without a GPU or who prefer cloud

| Agent | Provider | Model | Tier |
|---|---|---|---|
| Gaya | OpenCode Zen | Big Pickle | Free |
| LOGOS | OpenRouter | DeepSeek V4 Flash Free | Free (account required) |
| Freya | OpenCode Zen | MiMo V2.5 Free | Free |
| Tvashtar | OpenRouter | North Mini Code Free | Free (account required) |

**Zero payment required.** Zen free tier works out of the box. OpenRouter free tier requires a free account (no credit card).

The install script auto-detects your hardware and recommends the right config — no guesswork.

---

## Architecture

```
Gaya_Agent_PR/
├── opencode.jsonc               # Root config — paste URL into OpenCode, works instantly on cloud free tier
├── agents/                     # Agent personas (single source of truth)
│   ├── Gaya.md
│   ├── LOGOS.md
│   ├── Freya.md
│   └── Tvashtar.md
├── configs/                    # opencode.jsonc templates for install.ps1
│   ├── local-gpu.jsonc          # Ollama models
│   └── cloud-zen.jsonc          # Zen + OpenRouter free tier
├── memory/                     # Cross-agent persistent context
│   ├── moe-orchestrator-framework.md
│   └── auto-maintenance-protocol.md
├── scripts/
│   ├── install.ps1              # THE one script — install, upgrade, switch mode, repair
│   └── auto-maintenance.ps1     # 15-day audit protocol
├── skills-dashboard.html        # Interactive skill + agent browser
├── LEVELING_SYSTEM.md           # XP / title framework
├── agent-profile-schema.json    # Cross-agent save format
├── README.md
└── LICENSE
```

### How Agents Communicate

Gaya (Commander) routes tasks to the right sub-agent based on the work type:

```
User Request
    │
    ▼
┌─────────┐
│  GAYA   │  Assesses intent → routes to specialist
└────┬────┘
     │
     ├── Planning/Strategy  ──► LOGOS (deep reasoning)
     ├── Vision/Research    ──► Freya (multimodal, uncensored)
     ├── Implementation     ──► Tvashtar (code, architecture)
     └── Everything else    ──► Gaya (orchestrates or does it)
```

---

## Leveling System

Every task earns XP. Every level is wisdom earned.

| Outcome | XP |
|---|---|
| Full Success | +10 |
| Partial Success | +5 |
| Fail | +1 |
| Waste | Penalty |

Titles unlock at key milestones: Operator → Strategist → Architect → Sage.

The full framework is in `LEVELING_SYSTEM.md`.

---

## Auto-Maintenance

Every 15 days, an auto-maintenance script audits:

- **OpenCode DB size** — prunes old sessions if bloated
- **Project size** — archives unused projects
- **Agent file freshness** — verifies all 4 agents are present
- **Memory directory** — checks for required files

The script reports findings and asks permission before acting.

---

## Roadmap

- [x] Four agents (Gaya, LOGOS, Freya, Tvashtar)
- [x] Local GPU mode (Ollama)
- [x] Cloud mode (Zen + OpenRouter free tier)
- [x] Self-modifying install script
- [x] Dual config templates
- [x] Auto-maintenance protocol
- [x] Interactive skills dashboard
- [x] Paste-URL support (root opencode.jsonc)
- [x] Upgrade detection (auto-checks GitHub releases)
- [ ] Testing on fresh Windows install
- [ ] macOS/Linux install support
- [ ] Community agent templates
- [ ] GUI configurator

---

## License

MIT — use it, fork it, improve it. Attribute if you share.

---

<div align="center">
<p><em>"The quality of your action is your signature."</em></p>
</div>
