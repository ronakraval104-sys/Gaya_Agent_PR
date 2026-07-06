# MCP Server Setup for Gaya

MCP (Model Context Protocol) extends Gaya's abilities to interact with the filesystem, browser, and web. With MCP enabled, Gaya can read/write files, scrape websites, take screenshots, and automate browser tasks — all through natural language commands.

## What You Get

| Server | Tool Prefix | What It Does |
|---|---|---|
| **filesystem** | `filesystem_*` | Read, write, move, delete files in project directory |
| **playwright** | `playwright_browser_*` | Headless Chromium — navigate, click, type, screenshot |
| **browsermcp** | `browsermcp_*` | Your real Chrome — logged-in sessions, forms, extensions |
| **github** | — (disabled by default) | GitHub API — PRs, issues, repos (needs token) |

## Quick Install

```powershell
# From the project directory:
.\scripts\setup-mcp.ps1

# Or with custom project root:
.\scripts\setup-mcp.ps1 -ProjectDir "D:\MyProject"
```

The script will:
1. Install 4 npm packages globally
2. Install Playwright Chromium browser binary
3. Generate `opencode.json` in your project root
4. Print next steps

## Manual Install

If you prefer to do it yourself:

```powershell
# 1. Install global packages
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @playwright/mcp
npm install -g @browsermcp/mcp
npm install -g @imenam/mcp-github

# 2. Install Playwright browser
npx playwright install chromium

# 3. Create opencode.json in project root (see template below)
```

## opencode.json Template

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "filesystem": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "D:\\Your\\Project\\Path"],
      "enabled": true
    },
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp"],
      "enabled": true
    },
    "browsermcp": {
      "type": "local",
      "command": ["npx", "-y", "@browsermcp/mcp"],
      "enabled": true
    },
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@imenam/mcp-github"],
      "enabled": false
    }
  }
}
```

### Windows-Specific Note

If `npx` doesn't work in opencode (PowerShell blocks `npm.ps1`), replace the commands with the full `.cmd` paths:

```json
"command": ["C:\\Users\\YourUser\\AppData\\Roaming\\npm\\mcp-server-filesystem.cmd", "D:\\Your\\Project\\Path"]
```

The `setup-mcp.ps1` script handles this automatically.

## Enabling GitHub MCP

1. Generate a GitHub token: https://github.com/settings/tokens
2. Set it as environment variable: `$env:GITHUB_TOKEN = "your_token"`
3. Change `"enabled": false` → `"enabled": true` in `opencode.json`
4. Restart opencode

## BrowserMCP Chrome Extension

For browsermcp to connect to your **real Chrome browser** (with cookies, sessions, extensions):

1. Install the extension: https://browsermcp.dev/extension
2. Launch Chrome with the extension active
3. browsermcp will auto-connect

Without the extension, browsermcp behaves identically to Playwright (headless).

## Testing After Setup

Once opencode restarts, ask Gaya:

> "Test MCP servers"

Or test each manually:
- **filesystem**: "Write a test file and read it back"
- **playwright**: "Go to example.com and take a screenshot"
- **browsermcp**: "Navigate to google.com and show me the page"

## Troubleshooting

| Problem | Fix |
|---|---|
| `npm.ps1 is not digitally signed` | Use `npm.cmd` instead of `npm` |
| `command not found` | Restart terminal/PowerShell after npm install |
| `Cannot find module` | Run `npm install -g <package>` as admin |
| `browsermcp not connecting` | Install Chrome extension |
| Config not loading | Restart opencode completely |

## Files Created

- `opencode.json` — MCP configuration (at project root)
- `~/.config/opencode/memory/mcp-capacity.md` — Agent memory file (auto-read by Gaya)

## Uninstall

```powershell
npm uninstall -g @modelcontextprotocol/server-filesystem
npm uninstall -g @playwright/mcp
npm uninstall -g @browsermcp/mcp
npm uninstall -g @imenam/mcp-github
npx playwright uninstall chromium
# Remove opencode.json
```
