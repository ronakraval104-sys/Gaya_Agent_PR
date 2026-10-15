---
name: ecc-security-scan
description: Execute AgentShield security audit across workspace files, configurations, MCP servers, and environment variables. Detects leaked secrets, private keys, and high-risk shell commands.
---

# ECC Security Scan & AgentShield Skill

## Overview
Adapted from ECC's `AgentShield` and `security-reviewer` components.
Provides automated static analysis for AI coding environments to catch leaked secrets, unauthorized tokens, destructive shell commands, and insecure MCP server definitions before code is committed or executed.

## When to Run
- Before committing any new code or push to remote.
- When configuring or modifying MCP servers (`.mcp.json`, `mcp_config.json`).
- When touching authentication, environment variables, or `.env` files.
- Periodically via voice command: *"Run security scan"*.

## How It Works

Invoke the local scanner via Python or subagent:
```bash
python -c "from mini_gaya.security.agentshield import scan_text, scan_mcp_config; import json, os; print('Scanning workspace...')"
```

### Risk Categories Checked:
1. **API Keys & Tokens**: Anthropic (`sk-ant-...`), OpenAI (`sk-...`), GitHub PAT (`ghp_...`), Google Gemini (`AIza...`).
2. **Private Key Blocks**: RSA, EC, DSA, and OpenSSH private key PEM headers.
3. **Unsafe Shell Commands**: Pipes from remote URLs into shell interpreters (`curl ... | sh`, `wget ... | bash`), destructive recursive deletions (`rm -rf /`), and fork bombs.
4. **Insecure MCP Definitions**: Executables executing arbitrary shell commands or exposing unrestricted system privileges.

## Resolution Protocol
- If a secret is detected: Immediately remove from code, place in untracked `.env`, and add to `.gitignore`.
- If an unsafe shell command is detected: Replace with explicit, audited subprocess or standard library calls.
