# One-Click Installer for OpenCode
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Installing Council of Gaya for OpenCode" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$userHome = [System.Environment]::GetFolderPath('UserProfile')
$opencodeDir = Join-Path $userHome ".config\opencode"
$skillsDir = Join-Path $opencodeDir "skills"
$agentsDir = Join-Path $opencodeDir "agents"
$repoRoot = Split-Path -Parent $PSScriptRoot

New-Item -ItemType Directory -Path $opencodeDir -Force | Out-Null
New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
New-Item -ItemType Directory -Path $agentsDir -Force | Out-Null

# 1. Install opencode.jsonc
Copy-Item (Join-Path $repoRoot "config\opencode.jsonc") (Join-Path $opencodeDir "opencode.jsonc") -Force

# 2. Install Persona files
Copy-Item (Join-Path $repoRoot "agents\*") $agentsDir -Recurse -Force

# 3. Install Skills
Copy-Item (Join-Path $repoRoot "skills\*") $skillsDir -Recurse -Force

Write-Host "OpenCode Gaya Council Installation Complete!" -ForegroundColor Cyan
