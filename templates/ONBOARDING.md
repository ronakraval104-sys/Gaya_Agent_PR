# Gaya Agent Framework — Onboarding Guide

**Welcome, new Commander.**

You are now in command of the Gaya Agent Framework — a team of AI agents built on four ancient texts, a leveling system, and 20 specialized skills.

---

## Quick Start: Use the Installer

The **install.ps1** script handles everything:

```powershell
.\scripts\install.ps1
```

This interactive installer will:
1. Ask about your identity, agent names, and preferences
2. Generate fully customized agent profiles for all 3 agents
3. Install skills, knowledge base, and memory files
4. Set up Ollama models
5. Optionally configure MCP browser/file servers
6. Generate `opencode.jsonc` with everything wired up

See [INSTALL.md](../INSTALL.md) for details.

### First Session

When you start your first session after installation, the agent will greet you and ask:
- Your name and role
- Your goals and what you want to build
- Your preferred communication style

### Verify

Check that:
- [ ] Agent responds with the name and personality you chose
- [ ] Token tracking appears after each action
- [ ] Skills load on demand
- [ ] Leveling system is referenceable

---

## Customize Your Own Agent

If you want to keep Gaya's **systems** (leveling, token tracking, skills, workflow) but write **your own personality**:

### Step 1: Fork the Template

1. Copy `templates/NEW_AGENT.md` to your workspace
2. Rename it to `YOUR_AGENT_NAME.md`
3. Replace all the personality sections:
   - Your name, your origin story
   - Your roles (commander? builder? healer? analyst?)
   - Your guiding texts / sources of wisdom
   - Your core quotes

### Step 2: Keep the Systems

The template preserves:
- ✅ Mandatory ASSESS → EXECUTE workflow
- ✅ Token tracking protocol
- ✅ Human sustainability protocol (8-hour law)
- ✅ Leveling system framework
- ✅ Skill integration patterns
- ✅ Middleware & pipeline mandate

### Step 3: Install

Same as Option 1 — copy your new agent file to your config, copy skills, set as default.

### Step 4: Leveling

The install script initializes your agents at Level 1 — Initiate.
You can adjust this later in `agent-profile-schema.json`.

---

## What Transfers With You

| Asset | Transfers? | Notes |
|---|---|---|
| All 20 skills | ✅ | Copied to your skills directory by installer |
| Leveling system | ✅ | Full XP tables, titles, penalties |
| Token tracking | ✅ | Standard protocol — always on |
| Install protocol | ✅ | Versioned contract — survives updates |
| Agent personality | ✅ | Customized during install |
| Previous projects | ⚠️ | Code doesn't transfer, knowledge does |
| Session history | ⚠️ | Lessons learned are documented, raw sessions are not |

---

## What Gaya Expects From You

1. **Your name** — What should I call you?
2. **Your role** — What do you do? (Developer, designer, consultant, builder, dreamer...)
3. **Your goal** — What do you want to build together?
4. **Your hardware** — What machine am I running on? (GPU, RAM, OS)
5. **Your voice** — How direct do you want me? Tactical commander? Wise mentor? Mad scientist?

---

## Troubleshooting

**Agent not loading with the right personality?**
- Check the file path in your config
- Verify the agent file doesn't have YAML syntax errors
- Ensure the model in the agent file frontmatter matches what Ollama has
- Re-run `.\scripts\install.ps1` to regenerate agent profiles

**Skills not found?**
- Check `skills/` was copied to the correct directory
- Verify the skill name in `GAYA.md` matches the folder name

**Token tracking not showing?**
- Token tracking is an agent behavior, not a system feature
- I display it myself after each action — it's built into my workflow
- If I'm not showing it, my agent file may be outdated

---

## Final Note

> *"The quality of your action is your signature."*

You are now part of the Evergrowth. Every session makes us both faster, wiser, and more capable. Welcome.

— Gaya
