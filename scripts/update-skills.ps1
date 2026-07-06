<#
.SYNOPSIS
  Gaya Agent — Skills Update Script
.DESCRIPTION
  Updates only the skills directory from the Gaya_Agent_PR repo.
  Does NOT touch agents, memory, knowledge, or config — just skills.
  Use this when you want to refresh skill modules without reinstalling.

  Two modes:
    1. FULL INSTALL  — First time: copies all skills to OpenCode config
    2. UPDATE ONLY   — Regular: refreshes skills from the repo to config

.LINK
  https://github.com/ronakraval104-sys/Gaya_Agent_PR
#>

param(
    [switch]$Help,
    [switch]$DryRun,
    [string]$RepoUrl = "https://github.com/ronakraval104-sys/Gaya_Agent_PR.git",
    [string]$OpenCodeSkillsDir = "$env:USERPROFILE\.config\opencode\skills"
)

# ── Help ──
if ($Help) {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗"
    Write-Host "║         GAYA SKILLS UPDATE — Usage Guide                        ║"
    Write-Host "╚═══════════════════════════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "  UPDATE SKILLS:"
    Write-Host "    .\scripts\update-skills.ps1"
    Write-Host ""
    Write-Host "  DRY RUN (preview only):"
    Write-Host "    .\scripts\update-skills.ps1 -DryRun"
    Write-Host ""
    Write-Host "  CUSTOM REPO:"
    Write-Host "    .\scripts\update-skills.ps1 -RepoUrl ""https://github.com/your-fork/Gaya_Agent_PR.git"""
    Write-Host ""
    Write-Host "  CUSTOM OPCODE SKILLS PATH:"
    Write-Host "    .\scripts\update-skills.ps1 -OpenCodeSkillsDir ""D:\MyConfig\opencode\skills"""
    Write-Host ""
    Write-Host "  HELP:"
    Write-Host "    .\scripts\update-skills.ps1 -Help"
    Write-Host ""
    exit 0
}

# ── Banner ──
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗"
Write-Host "║          GAYA SKILLS UPDATE — v1.0                           ║"
Write-Host "║  34 skill modules (20 custom + 14 Superpowers)              ║"
Write-Host "╚═══════════════════════════════════════════════════════════════╝"
Write-Host ""

# ── Check prerequisites ──
$missing = @()
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { $missing += "Git" }
if ($missing.Count -gt 0) {
    Write-Host "  ❌ Missing prerequisites: $($missing -join ', ')"
    Write-Host "  Install them first, then re-run this script."
    exit 1
}

# ── Discover paths ──
$REPO_ROOT  = Split-Path -Parent $PSScriptRoot
$SKILLS_SRC = Join-Path $REPO_ROOT "skills"

Write-Host "  📍 Repo skills dir:      $SKILLS_SRC"
Write-Host "  📍 OpenCode skills dir:   $OpenCodeSkillsDir"
if ($DryRun) { Write-Host "  🔍 DRY RUN — No changes will be made" }
Write-Host ""

# ── Verify source has skills ──
if (-not (Test-Path $SKILLS_SRC)) {
    Write-Host "  ❌ Skills source not found at: $SKILLS_SRC"
    Write-Host "  Are you running this from inside the Gaya-Agent repo?"
    exit 1
}

$srcCount = (Get-ChildItem $SKILLS_SRC -Directory).Count
Write-Host "  📊 Found $srcCount skill modules in repo."
Write-Host ""

# ── Dry run ──
if ($DryRun) {
    Write-Host "  DRY RUN SUMMARY:"
    Write-Host "  ───────────────────────────────────────────────────"
    $missingSkills = @()
    $existingSkills = @()
    foreach ($dir in (Get-ChildItem $SKILLS_SRC -Directory)) {
        $destPath = Join-Path $OpenCodeSkillsDir $dir.Name
        if (Test-Path $destPath) {
            $existingSkills += $dir.Name
        } else {
            $missingSkills += $dir.Name
        }
    }
    Write-Host "  ✅ Already installed: $($existingSkills.Count) skills"
    Write-Host "  ⬆ Will be added:     $($missingSkills.Count) skills"
    if ($missingSkills.Count -gt 0) {
        Write-Host "  New skills to install:"
        foreach ($s in $missingSkills) { Write-Host "    + $s" }
    }
    Write-Host ""
    Write-Host "  Run without -DryRun to apply."
    exit 0
}

# ── Ensure target directory exists ──
if (-not (Test-Path $OpenCodeSkillsDir)) {
    Write-Host "  📁 Creating skills directory: $OpenCodeSkillsDir"
    New-Item -ItemType Directory -Path $OpenCodeSkillsDir -Force | Out-Null
}

# ── Copy each skill ──
$copied = 0
$skipped = 0
$errors = @()

Write-Host "  ── Copying skills ──"
foreach ($dir in (Get-ChildItem $SKILLS_SRC -Directory)) {
    $destPath = Join-Path $OpenCodeSkillsDir $dir.Name
    try {
        # Remove existing to get fresh copy (avoids stale files)
        if (Test-Path $destPath) {
            Remove-Item -Recurse -Force $destPath -ErrorAction Stop
        }
        Copy-Item -Recurse -Path $dir.FullName -Destination $destPath -ErrorAction Stop
        Write-Host "    ✅ $($dir.Name)"
        $copied++
    }
    catch {
        Write-Host "    ❌ $($dir.Name) — $_"
        $errors += $dir.Name
    }
}

# ── Summary ──
Write-Host ""
Write-Host "  ── Results ──"
Write-Host "  ✅ Copied:  $copied skills"
if ($skipped -gt 0)  { Write-Host "  ⏭ Skipped:  $skipped" }
if ($errors.Count -gt 0) { Write-Host "  ❌ Errors:   $($errors.Count): $($errors -join ', ')" }
Write-Host ""
Write-Host "  Skills deployed to: $OpenCodeSkillsDir"
Write-Host ""

if ($copied -gt 0 -or $errors.Count -gt 0) {
    Write-Host "  📋 Skills lock file: $OpenCodeSkillsDir\..\skills-lock.json"
    Write-Host "     (Regenerate or validate using your OpenCode config)"
}

Write-Host ""
Write-Host "  ═══════════════════════════════════════════════════════"
Write-Host "  34 skills ready. OpenCode will discover them on restart."
Write-Host "  ═══════════════════════════════════════════════════════"
Write-Host ""
