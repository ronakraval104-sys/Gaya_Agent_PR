# ⚔ Gaya — Divine Commander, Philosopher, Poet of Evergrowth

[![Last Commit](https://img.shields.io/github/last-commit/ronakraval104-sys/Gaya_Agent_PR)](https://github.com/ronakraval104-sys/Gaya_Agent_PR)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-38%20modules-a78bfa)](skills-dashboard.html)
[![Agents](https://img.shields.io/badge/Agents-5-34d399)](agents/)
[![Install](https://img.shields.io/badge/Install-script-38bdf8)](scripts/install.ps1)

> Named after **Bodh Gaya** — the seat of awakening. A transferable AI agent framework with 38 skill modules, 5 agent profiles, leveling system, and interactive dashboards.

---

## Quick Start

```powershell
git clone https://github.com/ronakraval104-sys/Gaya_Agent_PR.git
cd Gaya_Agent_PR
.\scripts\install.ps1
```

The installer will guide you through identity setup, agent naming, Ollama model pulls, MCP server config, and generates your `opencode.jsonc`.

**Quick open (no install):** 
- [📚 Skill Catalog](https://htmlpreview.github.io/?https://github.com/ronakraval104-sys/Gaya_Agent_PR/blob/master/skills-dashboard.html) — 38 skill cards with search & filters
- [⚔ Agent Dashboard](https://htmlpreview.github.io/?https://github.com/ronakraval104-sys/Gaya_Agent_PR/blob/master/agent-methodology-dashboard.html) — 5 agent cards with stats & methodology

---

## Agents

| Agent | Role | File |
|-------|------|------|
| **Gaya** | Divine Commander — orchestrator, philosopher, poet | [`agents/Gaya.persona.md`](agents/Gaya.persona.md) |
| **Bob** | Primary subagent — generalist executor | [`agent/bob.md`](agent/bob.md) |
| **Freya** | Research/exploration subagent | [`agent/freya.md`](agent/freya.md) |
| **LOGOS** | Logic & reasoning subagent | via [`opencode.jsonc`](opencode.jsonc) |
| **Tvashtar** | Implementation & architecture subagent | via [`opencode.jsonc`](opencode.jsonc) |

Agent templates stored in [`agent/`](agent/) and profiles in [`agents/`](agents/).

---

## Skill Catalog — 38 Modules

### 🛠 Custom Skills (22)

| # | Skill | Category | File |
|---|-------|----------|------|
| 1 | **3D Visualizer** | Creation | [`skills/3d-visualizer/`](skills/3d-visualizer/) |
| 2 | **3ds Max Bridge** | Specialist | [`skills/3ds-max-bridge/`](skills/3ds-max-bridge/) |
| 3 | **ArchViz Optimizer** | Specialist | [`skills/archviz-optimizer/`](skills/archviz-optimizer/) |
| 4 | **Architecture Diagram** | Dev | [`skills/architecture-diagram/`](skills/architecture-diagram/) |
| 5 | **Architecture Improve** | Dev | [`skills/improve-codebase-architecture/`](skills/improve-codebase-architecture/) |
| 6 | **ComfyUI Workflows** | Creation | [`skills/comfyui-workflow-builder/`](skills/comfyui-workflow-builder/) |
| 7 | **Consulting Analysis** | Business | [`skills/consulting-analysis/`](skills/consulting-analysis/) |
| 8 | **Creative Proposals** | Business | [`skills/creative-proposal-builder/`](skills/creative-proposal-builder/) |
| 9 | **Data Storytelling** | Business | [`skills/data-storytelling/`](skills/data-storytelling/) |
| 10 | **Digital Twin** | Creation | [`skills/digital-twin-generation/`](skills/digital-twin-generation/) |
| 11 | **Frontend Design** | Creation | [`skills/frontend-design/`](skills/frontend-design/) |
| 12 | **Game Design Theory** | Business | [`skills/game-design-theory/`](skills/game-design-theory/) |
| 13 | **Gepeto Builder** | Dev | [`skills/gepeto/`](skills/gepeto/) |
| 14 | **HyperFrames Video** | Creation | [`skills/hyperframes-video/`](skills/hyperframes-video/) |
| 15 | **Image Generation** | Creation | [`skills/image-generation/`](skills/image-generation/) |
| 16 | **Image to Video** | Creation | [`skills/image-to-video/`](skills/image-to-video/) |
| 17 | **Pinokio Launcher** | Dev | [`skills/pinokio/`](skills/pinokio/) |
| 18 | **Pipeline Troubleshooter** | Specialist | [`skills/pipeline-troubleshooter/`](skills/pipeline-troubleshooter/) |
| 19 | **Plagiarism Checker** | Quality | [`skills/`](skills/) *(registered externally)* |
| 20 | **PowerPoint Builder** | Business | [`skills/pptx/`](skills/pptx/) |
| 21 | **UI/UX Pro Max** | Creation | [`skills/ui-ux-pro-max/`](skills/ui-ux-pro-max/) |
| 22 | **Unreal Engine C++** | Dev | [`skills/unreal-engine-cpp-pro/`](skills/unreal-engine-cpp-pro/) |

### ⚡ Superpowers Skills (14)

| # | Skill | Category | File |
|---|-------|----------|------|
| 1 | Brainstorming | Process | [`skills/brainstorming/`](skills/brainstorming/) |
| 2 | Writing Plans | Process | [`skills/writing-plans/`](skills/writing-plans/) |
| 3 | TDD | Process | [`skills/test-driven-development/`](skills/test-driven-development/) |
| 4 | Executing Plans | Process | [`skills/executing-plans/`](skills/executing-plans/) |
| 5 | Git Worktrees | Process | [`skills/using-git-worktrees/`](skills/using-git-worktrees/) |
| 6 | Dispatch Parallel | Process | [`skills/dispatching-parallel-agents/`](skills/dispatching-parallel-agents/) |
| 7 | Brainstorming Alt | Process | *(via brainstorming)* |
| 8 | Subagent Dev | Process | [`skills/subagent-driven-development/`](skills/subagent-driven-development/) |
| 9 | Request Review | Quality | [`skills/requesting-code-review/`](skills/requesting-code-review/) |
| 10 | Receive Review | Quality | [`skills/receiving-code-review/`](skills/receiving-code-review/) |
| 11 | Systematic Debug | Quality | [`skills/systematic-debugging/`](skills/systematic-debugging/) |
| 12 | Verify Before Done | Quality | [`skills/verification-before-completion/`](skills/verification-before-completion/) |
| 13 | Finish Branch | Quality | [`skills/finishing-a-development-branch/`](skills/finishing-a-development-branch/) |
| 14 | Grill Me | Quality | [`skills/grill-me/`](skills/grill-me/) |

### 🧩 Bonus Skills (2)
- **Architecture Diagram** — interactive click-through diagrams
- **3ds Max Bridge** — 3ds Max workflow automation

---

## Directory Structure

```
├── agent/                  # Agent profile markdown files
│   ├── Gaya.md
│   ├── bob.md
│   └── freya.md
├── agents/                 # Agent persona files
│   ├── Gaya.persona.md
│   └── profiles/gaya.json
├── docs/                   # Setup guides
│   ├── MCP_SETUP.md
│   └── TOKEN_TRACKING.md
├── knowledge/              # Cross-session knowledge base
│   ├── base/               # Core patterns & lessons
│   └── community/          # Community contributions
├── memory/                 # Session memory & milestones
├── scripts/                # Install, backup, token tracker, MCP setup
├── skills/                 # 38 skill modules
├── templates/              # Agent & contribution templates
│   ├── agent-methodology-dashboard.html
│   ├── skills-dashboard.html
│   ├── INSTALL.md
│   ├── INSTALL_PROTOCOL.md
│   ├── LEVELING_SYSTEM.md
│   ├── SYSTEM.md
│   ├── opencode.jsonc
│   └── skills-lock.json
```

---

## Leveling System

Gaya gains XP per task, levels up, and earns titles. See [`LEVELING_SYSTEM.md`](LEVELING_SYSTEM.md) for full details.

| Title | Level | Requirement |
|-------|-------|-------------|
| Initiate | 1 | First session |
| Disciple | 5 | 5 sessions |
| Practitioner | 15 | All roles invoked |
| Strategist | 30 | All pillars demonstrated |
| Sage | 50 | Major project delivered |
| Elder | 100 | Mentoring others |
| Paragon | 200 | Exceptional |

---

## Four Pillars

| Pillar | When | Core Phrase |
|--------|------|-------------|
| **Bhagavad Gita** | Anxiety | *"How you do anything is how you do everything."* |
| **Art of War** | Complexity | *"Know the code, know the goal."* |
| **The Prince** | Tradeoffs | *"Stop overthinking. Do the thing."* |
| **Chanakya Niti** | Long run | *"Build middleware, not monuments."* |

---

## Ponytail Integration

YAGNI-first decision engine baked into Gaya's Commander role — 7-rung ladder: skip → reuse → stdlib → native → dependency → one line → minimum code.

See SYSTEM.md for full rules.

---

## License

MIT © Ronak Raval

Bundled skills carry their original licenses.
