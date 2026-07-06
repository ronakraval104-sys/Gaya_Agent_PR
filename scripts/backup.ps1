# Gaya Backup — Daily Commit + Push
# Part of Gaya Agent standard protocol
#
# Usage:
#   .\scripts\backup.ps1                    # Backup with auto message
#   .\scripts\backup.ps1 -Message "custom"  # Backup with custom message

param(
    [string]$Message = ""
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$today = Get-Date -Format "yyyy-MM-dd"
$time = Get-Date -Format "HH:mm"

# Default commit message
if ([string]::IsNullOrEmpty($Message)) {
    $CommitMessage = "backup: Gaya agent state — $today $time"
} else {
    $CommitMessage = "$Message — $today $time"
}

Write-Host ""
Write-Host "────────────────────────────" -ForegroundColor Green
Write-Host "📦 GAYA BACKUP" -ForegroundColor Green
Write-Host "────────────────────────────" -ForegroundColor Green
Write-Host "Repo:  $RepoRoot"
Write-Host "Date:  $today $time"
Write-Host ""

Set-Location $RepoRoot

# Check for changes
$status = git status --porcelain
if ([string]::IsNullOrEmpty($status)) {
    Write-Host "✅ Nothing to commit — working tree clean." -ForegroundColor Green
    exit 0
}

# Show what's changing
Write-Host "Changes detected:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Add everything
git add -A
if (-not $?) {
    Write-Host "ERROR: git add failed" -ForegroundColor Red
    exit 1
}

# Commit
git commit -m $CommitMessage
if (-not $?) {
    Write-Host "ERROR: git commit failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Committed: $CommitMessage" -ForegroundColor Green

# Push
Write-Host "Pushing to remote..." -ForegroundColor Yellow
git push origin main 2>&1
if ($?) {
    Write-Host "✅ Pushed to GitHub successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ Push failed. Check remote: git remote -v" -ForegroundColor Red
    Write-Host "  You may need: git push --set-upstream origin main" -ForegroundColor Yellow
}

Write-Host "────────────────────────────" -ForegroundColor Green
Write-Host "Done. $(Get-Date -Format 'HH:mm')" -ForegroundColor Green
Write-Host "────────────────────────────" -ForegroundColor Green
