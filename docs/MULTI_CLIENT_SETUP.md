# 🌐 Multi-Platform Setup Guide — Gaya Update 0.5.2610

Gaya runs natively across all major agentic AI environments with unified Council protocols and specialized skills.

---

## 1. Google Antigravity (AGY)

### Automated Setup:
Run the Antigravity setup script:
```powershell
.\scripts\install_antigravity.ps1
```

### Manual Configuration:
1. **Global Persona & Council Rules**:
   Copy `config/AGENTS.md` to `~/.gemini/config/rules/AGENTS.md`.
2. **Global Skills**:
   Copy `skills/` to `~/.gemini/config/skills/`.
3. **MCP Servers**:
   Merge `config/mcp_config.json` into `~/.gemini/config/mcp_config.json`.
   Servers included:
   - `chrome-devtools-mcp`
   - `parallel-search`
   - `canva`
   - `rea` (Reverse Engineer Anything)

---

## 2. OpenCode

### Automated Setup:
```powershell
.\scripts\install_opencode.ps1
```

### Manual Configuration:
1. Copy `config/opencode.jsonc` to `~/.config/opencode/opencode.jsonc` or place it in your workspace root.
2. Ensure `agents/` is accessible or copied to `~/.config/opencode/agents/`.
3. Copy `.opencode/AGENTS.md` to your project's `.opencode/` directory.

---

## 3. Claude Code

Place `CLAUDE.md` in your project root or home directory (`~/.claude/CLAUDE.md`).
Claude Code will automatically adopt Gaya's four pillars, the Subagent Council rules (LOGOS PASS gate), Ponytail's ladder, and the SlopMonster de-slop invariants.

---

## 4. OpenAI Codex & GitHub Copilot CLI

Place `CODEX.md` in your workspace root or configure in `~/.codex/config.toml`.
Codex will follow the 7-step Ponytail ladder, the LOGOS read-only gate, and the designated agent assignments.

---

## 5. Cursor & VS Code

Copy `AGENTS.md` to `.cursorrules` in your project root or configure VS Code MCP settings with `config/mcp_config.json`.

---

## 6. User Identity Setup & Repository Sharing

Gaya personalizes how all agents and voice telemetry address you:
- **Fresh Installation**: Running `.\scripts\install.ps1` (or `./scripts/install.sh`) prompts for your name and preferred address prefix (e.g. `Ronak` and `R0n`). It writes `~/.gaya/user_profile.json` and updates your active rules.
- **Upgrades**: The installer automatically detects and fetches your existing name and prefix from previous installations.
- **Direct Repository Sharing**: Distribute Gaya directly using the Git repository:
  `https://github.com/ronakraval104-sys/Gaya_Agent_PR`

