# Universal Gaya Installer (Update 0.5.2610)
param(
    [string]$Target = "all"
)

Write-Host "⚔ Gaya Universal Installer — Update 0.5.2610" -ForegroundColor Cyan
Write-Host "The Seat of Awakening: Antigravity · OpenCode · Claude Code · Codex" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------"

if ($Target -eq "all" -or $Target -eq "antigravity") {
    & "$PSScriptRoot\install_antigravity.ps1"
}

if ($Target -eq "all" -or $Target -eq "opencode") {
    & "$PSScriptRoot\install_opencode.ps1"
}

Write-Host "`nAll targets configured successfully!" -ForegroundColor Green
Write-Host "To launch Council Dashboard: cd council_of_gaya; npm run dev" -ForegroundColor Gray
Write-Host "To launch Mini Gaya: cd mini_gaya; python launch_mini_gaya.py" -ForegroundColor Gray
