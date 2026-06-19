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
- [Skills & Superpowers](#-skills--superpowers)
- [Two Modes: Round Table vs Token Discipline](#-two-modes-round-table-vs-token-discipline)
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

### How Agents Communicate (Task Hand-off)

You only talk to **Gaya**. Gaya handles the rest.

#### The Workflow

1. **You say something** — "Build a CLI tool" or "Debug this crash"
2. **Gaya reads the intent** — figures out the task type, loads the right skill
3. **Gaya routes** — picks the best agent for the job
4. **The sub-agent works** — gets full context (your request, relevant files, persona)
5. **Result flows back** — sub-agent reports to Gaya, Gaya presents to you

#### Task Hand-off When Switching Models

Context travels through the **memory directory** (`~/.config/opencode/memory/`) — a shared whiteboard all agents can read and write:

```
You: "Gaya, build a password generator in Python"

  Step 1 ── Gaya routes planning to LOGOS
           LOGOS analyzes → "3 approaches: CLI, configurable, GUI"
           LOGOS writes analysis to memory/         ← shared whiteboard

  Step 2 ── Gaya reads LOGOS's analysis
           Routes implementation to Tvashtar
           Tvashtar reads the analysis from memory/ ← picks up context
           Tvashtar writes the code, runs tests

  Step 3 ── Results flow back to Gaya
           Gaya presents to you:
           "✓ Password generator done. Next: add flags?"
```

Whether you're on **GPU (Ollama)** or **cloud (Zen/OpenRouter)**, the flow is identical. Only the model changes — the handoff logic stays the same.

#### Routing Map

```
User Request
    │
    ▼
┌─────────┐
│  GAYA   │  Assesses intent → routes to specialist
└────┬────┘
     │
     ├── Planning/Strategy  ──► LOGOS (deep reasoning, spots flaws)
     ├── Vision/Research    ──► Freya (multimodal, uncensored)
     ├── Implementation     ──► Tvashtar (code, architecture, refactoring)
     └── Everything else    ──► Gaya (orchestrates or does it directly)
```

---

## Skills & Superpowers

Every agent comes loaded with **skills** — ready-made workflows for specific tasks. Think of them as pre-loaded expertise that fires automatically when you need it.

### How Skills Work

You speak naturally. The agent detects the task type and **loads the right skill** automatically:

```
You: "Let's build a landing page"
     │
     ▼
Gaya detects: "frontend-design" skill matches
     │
     ▼
Skill loads → gives step-by-step process for building a landing page
     │
     ▼
Gaya follows the skill's workflow → clean result
```

No commands, no `/skill something`. The triggers are built into each skill's definition.

### Skill Categories

| Category | Skills | When They Fire |
|---|---|---|
| **Process** | Brainstorming, Debugging, TDD, Code Review | Before building, when something breaks |
| **Creative** | Frontend Design, UI/UX Pro, Image Gen, 3D Viz | Building UIs, generating visuals |
| **Analysis** | Consulting, Data Storytelling, Architecture | Research, reports, system design |
| **Agent** | Gaya (persona), Grill Me, Brainstorming | Role-playing, planning, stress-testing |
| **Dev** | Unreal Engine, PPTX, ComfyUI, Pipeline | Specialized tool work |
| **Business** | Consulting, Proposals, Digital Twin | Client-facing work |

### Where Skills Come From

- **Superpowers (~30+ skills)** — Pre-installed skills covering design, development, analysis, and process. This is the default skill library.
- **Custom skills** — Your own `.md` files in `~/.config/opencode/skills/`. Write once, use forever.
- **Agent files** — The 4 agent personas (`agents/Gaya.md`, etc.) are themselves skills with their own triggers.

### The Skill Stack

Multiple skills can chain together in one session:

```
Brainstorming (plan the approach)
  → Frontend Design (build the UI)
    → Code Review (verify quality)
      → Data Storytelling (present results)
```

Gaya loads them in sequence automatically as the task evolves.

### Interactive Browser

The [skills-dashboard.html](https://htmlpreview.github.io/?https://github.com/ronakraval104-sys/Gaya_Agent_PR/blob/main/skills-dashboard.html) lets you browse all skills with search, filters, and info panels — try it in your browser right now.

---

## Two Modes: Round Table vs Token Discipline

Gaya has two operating modes at opposite ends of the spectrum. Both exist because they serve different situations.

```
                    SIMPLE TASK                           COMPLEX TASK
                         │                                     │
                         ▼                                     ▼
              ┌─────────────────────┐              ┌─────────────────────┐
              │  TOKEN DISCIPLINE   │              │    ROUND TABLE      │
              │                     │              │                     │
              │  Fast. Cheap.       │              │  Thorough. Solid.   │
              │  Gaya does it alone │              │  All agents debate  │
              │  No ceremony.       │              │  Converge on plan.  │
              └─────────────────────┘              └─────────────────────┘
```

### Token Discipline (Default)

**Philosophy:** Don't waste tokens on ceremony. Just execute.

For routine tasks — file edits, quick scripts, known patterns — Gaya skips the routing overhead and works directly:

```
You: "Change that button color to blue"
Gaya: ⏱️ Quick edit → 5s
      Done. Color updated.

No sub-agents called. No analysis phase. No debate.
```

**When it kicks in:**
- The task is clear, simple, and unambiguous
- The cost of a mistake is low
- It's a known pattern Gaya has done before
- The request starts with `/fast`

### Round Table Mode (On Demand)

**Philosophy:** Multiple minds are better than one. Burn tokens to get it right.

For complex, risky, or multi-approach tasks — architecture decisions, system design, critical bug fixes — Gaya brings multiple agents into the discussion:

```
You: "Design the auth system for our SaaS"

Gaya: ⏱️ Round Table: LOGOS + Tvashtar debating auth approaches → 2 min

  LOGOS:  "OAuth2 + JWT is standard. But consider session-based for your scale."
  Tvashtar: "JWT is simpler for now. We can add sessions later."
  LOGOS:  "Fair. But refresh tokens add complexity. Ready for that?"
  Tvashtar: "Start simple with a migration path. Here's the plan."

  ✓ Gaya: Consensus reached. Implementing via Tvashtar.
```

**When to use it:**
- Architecture decisions with multiple valid approaches
- Bug fixes where root cause is uncertain
- New features that touch multiple parts of the system
- Any time you say `/roundtable`

### How They Coexist

They're polar opposites, and that's the point:

| | Token Discipline | Round Table |
|---|---|---|
| **Token cost** | Minimal | High (worth it) |
| **Speed** | Instant | Takes time |
| **Quality** | Good for simple tasks | Bulletproof for complex ones |
| **When** | "I know exactly what I want" | "I need the right approach" |
| **Override** | `/fast` | `/roundtable` |

**Gaya auto-selects** based on your request:
- "Change the button color" → Token Discipline (obvious, low risk)
- "Design the auth system" → Round Table (complex, multiple approaches)
- "Fix this crash" → Round Table if root cause is unclear, Token Discipline if it's a known fix

You can always override with `/fast` or `/roundtable`.

### Implementing Round Table (How the Debate Works)

Round Table is not a meeting — it's a structured debate with a moderator:

```
Gaya presents the problem with context
        │
        ▼
Each agent responds independently (sequentially, VRAM permitting)
   LOGOS:  "Here's the logical approach + edge cases"
   Freya:  "Here's what the research / competitors do"  (if relevant)
   Tvashtar: "Here's the implementation + trade-offs"
        │
        ▼
Gaya synthesizes — finds consensus or flags disagreements
        │
        ▼
If consensus → Gaya routes implementation to the right agent
If stalemate → Gaya presents options to you with recommendations
```

On GPU mode (8 GB VRAM), agents debate **sequentially** — one at a time, context passed through memory. On cloud mode, all agents can respond in parallel.

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
