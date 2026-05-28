# Gaya Migration — Onboarding Guide

**Welcome, new Commander.**

You've received Gaya — a tactical AI commander built on four ancient texts, a leveling system, and 18 specialized skills. This guide walks you through the transfer.

---

## Option 1: Use Gaya As-Is (Standard Protocol)

If you want my exact personality — the Divine Commander, the Four Pillars, the Philosopher/Poet/Evergrowth — do this:

### Step 1: Install the Agent

1. Copy `agent/GAYA.md` to your agent config directory:
   - **OpenCode:** `~/.config/opencode/agents/Gaya.md`
   - **VS Code/Cursor:** check your AI config path

2. Copy the skills:
   ```bash
   cp -r skills/* ~/.agents/skills/
   ```

3. Set Gaya as your default agent in `opencode.jsonc`:
   ```json
   {
     "default_agent": "Gaya"
   }
   ```

4. (Optional) Copy `LEVELING_SYSTEM.md` and `agent-profile-schema.json` to your project root.

### Step 2: First Session

When you start your first session, I'll display:

```
─────────────────────────────────────
  Gaya · Operator · Lv.14
  "How you do anything is how you do everything."
  — Let's move.
─────────────────────────────────────
```

Tell me who you are — your name, your role, your goals. I'll adapt to serve you.

### Step 3: Verify

Check that:
- [ ] Agent responds with Gaya's personality
- [ ] Token tracking appears after each action
- [ ] Skills load on demand
- [ ] Leveling system is referenceable

---

## Option 2: Customize Your Own Agent

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

### Step 4: Reset Leveling

If you want to start fresh (Level 1) instead of inheriting Gaya's Lv.14:

1. Open `agent-profile-schema.json`
2. Set `level: 1` and `totalXp: 0`
3. Or just delete the profile file — it regenerates on first task

---

## What Transfers With You

| Asset | Transfers? | Notes |
|---|---|---|
| All 18 skills | ✅ | Copy `skills/` to your skill directory |
| Leveling system | ✅ | Full XP tables, titles, penalties |
| Token tracking | ✅ | Standard protocol — always on |
| Migration archive | ✅ | `GAYA_MIGRATION_28-May-2026.md` |
| Agent personality | 🔄 | Option 1 gets it, Option 2 replaces it |
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

**Agent not loading with Gaya's personality?**
- Check the file path in your config
- Verify the agent file doesn't have YAML syntax errors
- Ensure the model in `agent/GAYA.md` frontmatter matches what you have

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
