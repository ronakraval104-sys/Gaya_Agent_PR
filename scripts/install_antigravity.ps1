# One-Click Installer for Google Antigravity (AGY)
param(
    [string]$UserName = "",
    [string]$UserPrefix = ""
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Installing Council of Gaya for Google Antigravity (AGY)" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$userHome = [System.Environment]::GetFolderPath('UserProfile')
$geminiDir = Join-Path $userHome ".gemini"
$configDir = Join-Path $geminiDir "config"
$rulesDir = Join-Path $configDir "rules"
$skillsDir = Join-Path $configDir "skills"
$repoRoot = Split-Path -Parent $PSScriptRoot

New-Item -ItemType Directory -Path $rulesDir -Force | Out-Null
New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null

# 1. Install AGENTS.md with personalized user identity
Write-Host "Installing AGENTS.md Council Persona..." -ForegroundColor Green
$agentsPath = Join-Path $repoRoot "config\AGENTS.md"
$agentsContent = Get-Content $agentsPath -Raw -Encoding UTF8

if ($UserPrefix) {
    $alt = if ($UserName -and $UserName -ne $UserPrefix) { " (or $UserName)" } else { "" }
    $titleExclusion = if ($UserPrefix -eq "Commander") { "" } else { " Never use generic titles like `"sir`" or `"commander`"." }
    $agentsContent = $agentsContent -replace '(?m)^- Address the user as \*\*.*', "- Address the user as **$UserPrefix**$alt.$titleExclusion"
}
Set-Content -Path (Join-Path $rulesDir "AGENTS.md") -Value $agentsContent -Encoding UTF8

# 2. Install Skills
Write-Host "Installing 83 Skills to ~/.gemini/config/skills/..." -ForegroundColor Green
Copy-Item (Join-Path $repoRoot "skills\*") $skillsDir -Recurse -Force

# 3. Configure MCP
$mcpTarget = Join-Path $configDir "mcp_config.json"
$mcpSrc = Join-Path $repoRoot "config\mcp_config.json"
if (-not (Test-Path $mcpTarget)) {
    Copy-Item $mcpSrc $mcpTarget -Force
    Write-Host "Installed default mcp_config.json" -ForegroundColor Green
} else {
    Write-Host "mcp_config.json already exists. Verify 'rea' server is configured." -ForegroundColor Yellow
}

Write-Host "Gaya Antigravity Installation Complete!" -ForegroundColor Cyan
