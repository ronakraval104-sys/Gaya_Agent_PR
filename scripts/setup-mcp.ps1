#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Install and configure MCP (Model Context Protocol) servers for Gaya AI agent.
.DESCRIPTION
    Installs the 4 standard MCP server packages globally via npm:
    - filesystem: Read/write access to project directory
    - playwright: Headless browser automation
    - browsermcp: Real Chrome browser integration
    - github: GitHub API access (requires token)

    Also installs Playwright Chromium browser binary and generates
    opencode.json config file with platform-correct commands.
.PARAMETER ProjectDir
    Path to the project directory for filesystem access sandbox.
    Default: current working directory
.PARAMETER NoGitHub
    Skip GitHub MCP server setup.
.PARAMETER ForceReinstall
    Reinstall packages even if already installed.
.EXAMPLE
    .\setup-mcp.ps1
    Installs all MCP servers for current directory.

    .\setup-mcp.ps1 -ProjectDir "D:\MyProject" -NoGitHub
    Installs MCP servers without GitHub, sandboxed to D:\MyProject.
#>

param(
    [string]$ProjectDir = (Get-Location).Path,
    [switch]$NoGitHub,
    [switch]$ForceReinstall
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message, [string]$Status = "info")
    $icon = @{ info = "ℹ️ "; ok = "✅ "; warn = "⚠️ "; err = "❌ " }
    Write-Host ("{0}{1}" -f $icon[$Status], $Message)
}

function Install-MCPPackage {
    param([string]$PackageName)
    
    $check = npm.cmd list -g --depth=0 $PackageName 2>$null
    if ($LASTEXITCODE -eq 0 -and -not $ForceReinstall) {
        Write-Step "$PackageName already installed" "ok"
        return
    }
    
    Write-Step "Installing $PackageName..."
    npm.cmd install -g $PackageName
    if ($LASTEXITCODE -ne 0) { throw "Failed to install $PackageName" }
    Write-Step "$PackageName installed" "ok"
}

# Resolve npm global bin path
function Get-NpmBinPath {
    $prefix = npm.cmd config get prefix 2>$null
    if (-not $prefix) { $prefix = "$env:APPDATA\npm" }
    return $prefix
}

# --- MAIN ---
Write-Host ""
Write-Host "╔═══════════════════════════════════════╗"
Write-Host "║   Gaya MCP Server Setup              ║"
Write-Host "╚═══════════════════════════════════════╝"
Write-Host ""

# 1. Check Node.js
Write-Step "Checking Node.js..."
try {
    $nodeVer = node --version
    Write-Step "Node.js $nodeVer" "ok"
} catch {
    Write-Step "Node.js not found. Install from https://nodejs.org/" "err"
    exit 1
}

# 2. Install MCP packages
Write-Step "Installing MCP server packages..." "info"

Install-MCPPackage -PackageName "@modelcontextprotocol/server-filesystem"
Install-MCPPackage -PackageName "@playwright/mcp"
Install-MCPPackage -PackageName "@browsermcp/mcp"
if (-not $NoGitHub) {
    Install-MCPPackage -PackageName "@imenam/mcp-github"
}

# 3. Install Playwright Chromium browser
Write-Step "Checking Playwright Chromium browser..."
try {
    $testBrowser = npx.cmd playwright install --dry-run chromium 2>&1 | Out-String
    if ($testBrowser -match "already") {
        Write-Step "Chromium browser already installed" "ok"
    } else {
        Write-Step "Installing Chromium browser (this may take a minute)..."
        npx.cmd playwright install chromium
        Write-Step "Chromium installed" "ok"
    }
} catch {
    Write-Step "Could not verify Playwright browser. Run 'npx playwright install chromium' manually" "warn"
}

# 4. Generate opencode.json
$npmBin = Get-NpmBinPath
$isWindows = $env:OS -match "Windows"

# Determine platform-correct command prefix
if ($isWindows) {
    # Windows: use .cmd binaries explicitly (PowerShell blocks npm.ps1)
    $cmdExt = ".cmd"
    $sep = "\\"
} else {
    # Linux/Mac: use npx
    $cmdExt = ""
    $sep = "/"
}

$filesystemCmd = if ($isWindows) {
    @("${npmBin}${sep}mcp-server-filesystem.cmd", $ProjectDir)
} else {
    @("npx", "-y", "@modelcontextprotocol/server-filesystem", $ProjectDir)
}

$playwrightCmd = if ($isWindows) {
    @("${npmBin}${sep}playwright-mcp.cmd")
} else {
    @("npx", "-y", "@playwright/mcp")
}

$browsermcpCmd = if ($isWindows) {
    @("${npmBin}${sep}mcp-server-browsermcp.cmd")
} else {
    @("npx", "-y", "@browsermcp/mcp")
}

$githubCmd = if ($isWindows) {
    @("${npmBin}${sep}mcp-github.cmd")
} else {
    @("npx", "-y", "@imenam/mcp-github")
}

# Escape paths for JSON
$escapedProjectDir = $ProjectDir -replace '\\', '\\'

$config = @"
{
  `"\$schema`": `"https://opencode.ai/config.json`",
  `"mcp`": {
    `"filesystem`": {
      `"type`": `"local`",
      `"command`": $(
        if ($isWindows) {
          '[ "' + ($filesystemCmd -join '", "') + '" ]'
        } else {
          '[ "' + ($filesystemCmd -join '", "') + '" ]'
        }
      ),
      `"enabled`": true
    },
    `"playwright`": {
      `"type`": `"local`",
      `"command`": $(
        if ($isWindows) {
          '[ "' + ($playwrightCmd -join '", "') + '" ]'
        } else {
          '[ "' + ($playwrightCmd -join '", "') + '" ]'
        }
      ),
      `"enabled`": true
    },
    `"browsermcp`": {
      `"type`": `"local`",
      `"command`": $(
        if ($isWindows) {
          '[ "' + ($browsermcpCmd -join '", "') + '" ]'
        } else {
          '[ "' + ($browsermcpCmd -join '", "') + '" ]'
        }
      ),
      `"enabled`": true
    },
    `"github`": {
      `"type`": `"local`",
      `"command`": $(
        if ($isWindows) {
          '[ "' + ($githubCmd[0]) + '" ]'
        } else {
          '[ "' + ($githubCmd -join '", "') + '" ]'
        }
      ),
      `"enabled`": false
    }
  }
}
"@

$configPath = Join-Path -Path $ProjectDir -ChildPath "opencode.json"
$config | Out-File -FilePath $configPath -Encoding utf8
Write-Step "Config written to $configPath" "ok"

# 5. Post-install notes
Write-Host ""
Write-Host "╔═══════════════════════════════════════╗"
Write-Host "║   Setup Complete                     ║"
Write-Host "╚═══════════════════════════════════════╝"
Write-Host ""
Write-Step "MCP servers installed:" "ok"
Write-Step "  @modelcontextprotocol/server-filesystem" "ok"
Write-Step "  @playwright/mcp" "ok"
Write-Step "  @browsermcp/mcp" "ok"
if (-not $NoGitHub) { Write-Step "  @imenam/mcp-github (disabled — add GITHUB_TOKEN)" "ok" }

Write-Host ""
Write-Step "NEXT STEPS:" "info"
Write-Host "  1. Restart opencode to load the new config"
Write-Host "  2. For browsermcp (real Chrome): install Chrome extension"
Write-Host "     https://browsermcp.dev/extension"
Write-Host "  3. For GitHub MCP: set GITHUB_TOKEN env var, then"
Write-Host "     change 'enabled': false → true in opencode.json"
Write-Host "  4. Test with: 'check mcp servers' in opencode chat"
Write-Host ""
