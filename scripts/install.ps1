# Universal Gaya Installer (Update 0.5.2610)
param(
    [string]$Target = "all",
    [string]$UserName = "",
    [string]$UserPrefix = "",
    [switch]$NonInteractive
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ⚔ Gaya Universal Installer : Update 0.5.2610" -ForegroundColor Yellow
Write-Host "  The Seat of Awakening: Antigravity | OpenCode | Claude | Codex" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$userHome = [System.Environment]::GetFolderPath('UserProfile')
$gayaDir = Join-Path $userHome ".gaya"
$profilePath = Join-Path $gayaDir "user_profile.json"

# 1. Resolve User Identity (Fetch existing if upgrading, ask if fresh install)
$resolvedName = $UserName
$resolvedPrefix = $UserPrefix

if (-not $resolvedPrefix -or -not $resolvedName) {
    # Check ~/.gaya/user_profile.json
    if (Test-Path $profilePath) {
        try {
            $existing = Get-Content $profilePath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($existing.prefix) { $resolvedPrefix = $existing.prefix }
            if ($existing.name) { $resolvedName = $existing.name }
            Write-Host "`n[Upgrade Detected] Found existing Gaya profile: Prefix='$resolvedPrefix', Name='$resolvedName'" -ForegroundColor Green
        } catch {}
    }

    # If not found, check existing AGENTS.md rule file
    if (-not $resolvedPrefix) {
        $legacyPaths = @(
            (Join-Path $userHome ".gemini\config\rules\AGENTS.md"),
            (Join-Path $userHome ".config\opencode\AGENTS.md"),
            (Join-Path $userHome ".claude\CLAUDE.md")
        )
        foreach ($p in $legacyPaths) {
            if (Test-Path $p) {
                $rawText = Get-Content $p -Raw -Encoding UTF8
                if ($rawText -match 'Address the user as \*\*([^*]+)\*\*\s*(?:\(or ([^)]+)\))?') {
                    $resolvedPrefix = $Matches[1].Trim()
                    $resolvedName = if ($Matches[2]) { $Matches[2].Trim() } else { $resolvedPrefix }
                    Write-Host "`n[Upgrade Detected] Fetched identity from existing rule: Prefix='$resolvedPrefix', Name='$resolvedName'" -ForegroundColor Green
                    break
                }
            }
        }
    }

    # If still not found and interactive, ask the user
    if (-not $resolvedPrefix) {
        if ($NonInteractive) {
            $resolvedName = "Ronak"
            $resolvedPrefix = "R0n"
        } else {
            Write-Host "`n[Fresh Install] Personalize how Gaya addresses you:" -ForegroundColor Yellow
            $inputName = Read-Host "Enter your name (e.g. Ronak / Alice) [default: Ronak]"
            if ([string]::IsNullOrWhiteSpace($inputName)) { $inputName = "Ronak" }
            
            $inputPrefix = Read-Host "Enter address title or prefix (e.g. R0n / Ron / Commander) [default: R0n]"
            if ([string]::IsNullOrWhiteSpace($inputPrefix)) { $inputPrefix = "R0n" }

            $resolvedName = $inputName
            $resolvedPrefix = $inputPrefix
        }
    }
}

# Ensure defaults if empty
if (-not $resolvedName) { $resolvedName = "Ronak" }
if (-not $resolvedPrefix) { $resolvedPrefix = "R0n" }

# Save profile
New-Item -ItemType Directory -Path $gayaDir -Force | Out-Null
$profileObj = @{
    name = $resolvedName
    prefix = $resolvedPrefix
    updated_at = (Get-Date).ToString("o")
}
$profileObj | ConvertTo-Json | Set-Content $profilePath -Encoding UTF8
Write-Host "Profile locked in ~/.gaya/user_profile.json : Prefix='$resolvedPrefix', Name='$resolvedName'" -ForegroundColor Gray

# 2. Run target installers
if ($Target -eq "all" -or $Target -eq "antigravity") {
    & "$PSScriptRoot\install_antigravity.ps1" -UserName $resolvedName -UserPrefix $resolvedPrefix
}

if ($Target -eq "all" -or $Target -eq "opencode") {
    & "$PSScriptRoot\install_opencode.ps1" -UserName $resolvedName -UserPrefix $resolvedPrefix
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  All Gaya components installed and configured!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "To share Gaya, share the GitHub repository directly:" -ForegroundColor Yellow
Write-Host "  https://github.com/ronakraval104-sys/Gaya_Agent_PR" -ForegroundColor Cyan
Write-Host "`nQuick Start Commands:" -ForegroundColor Gray
Write-Host "  Council Dashboard : cd council_of_gaya; npm run dev" -ForegroundColor Gray
Write-Host "  Mini Gaya         : cd mini_gaya; python launch_mini_gaya.py" -ForegroundColor Gray
