<#
.SYNOPSIS
  Auto-Maintenance Protocol -- runs every 15 days.
  Audits DB, project directories, agent configs, and memory files.
  Presents findings -> asks permission -> executes if approved.
  Archives everything, deletes nothing.

.DESCRIPTION
  Designed to prevent OpenCode freeze root causes:
  - DB bloat (VACUUM + session pruning)
  - VCS watcher overload (root .gitignore + archive heavy dirs)
  - Stale agent references (Bob -> Tvashtar detection)
  - Memory file bloat (archive old session debriefs)

.PARAMETER AutoApprove
  Skip user confirmation prompts. Useful for scheduled tasks.

.NOTES
  Author: Gaya Agent System
  Schedule: Every 15 days
  File: ~/.config/opencode/scripts/auto-maintenance.ps1
#>

param(
  [switch]$AutoApprove
)

Write-Host ""
Write-Host "=== GAYA: Auto-Maintenance Protocol (15-Day Cycle) ===" -ForegroundColor Cyan
Write-Host "  Audit first -> Ask permission -> Execute if approved" -ForegroundColor White
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# === CONFIGURATION ===
$ProjectRoot = "D:\Ai_Tools\Open_code\project_folder"
$DbPath = "$env:USERPROFILE\.local\share\opencode\opencode.db"
$MemoryDir = "$env:USERPROFILE\.config\opencode\memory"
$ConfigDir = "$env:USERPROFILE\.config\opencode"
$ArchiveRoot = "D:\Ai_Tools\Open_code\archive"
$BackupDir = "$ConfigDir\backups"
$Timestamp = Get-Date -Format "yyyy-MM-dd"
$ArchiveDir = "$ArchiveRoot\archive_$Timestamp"
$LogFile = "$ArchiveRoot\maintenance-log.txt"

$ArchiveCandidates = @(
  "kiosk-chatbot",
  "Gaya-Agent",
  "god-simulator",
  "node_modules",
  "Ryze studio",
  "Parul Uni",
  "gaya-voice",
  "agent-system",
  "archived",
  "autodesk-bim",
  "Autodesk_automation",
  "max auto",
  "Kho",
  "Visual_chat_bot"
)

# === PHASE 1: AUDIT ===
Write-Host "--- PHASE 1: AUDIT ---" -ForegroundColor Yellow
Write-Host ""

$issues = @()
$findings = @()

# 1A: DB Audit
Write-Host "DB Audit..." -ForegroundColor Green
if (Test-Path $DbPath) {
  $dbFile = Get-Item $DbPath
  $dbSizeMB = [math]::Round($dbFile.Length / 1MB, 2)
  $action = if ($dbSizeMB -gt 200) { "VACUUM needed ($dbSizeMB MB > 200 MB)" } else { "OK" }
  $findings += @{ Category = "DB"; Item = "opencode.db"; Detail = "$dbSizeMB MB"; Action = $action }
  if ($dbSizeMB -gt 200) { $issues += "DB is $dbSizeMB MB -- needs VACUUM" }
  $color = if ($dbSizeMB -gt 200) { "Red" } else { "Green" }
  Write-Host "  Size: $dbSizeMB MB" -ForegroundColor $color
} else {
  Write-Host "  DB not found at $DbPath" -ForegroundColor Yellow
}

# 1B: Project Directory Audit
Write-Host "Project Directory Audit..." -ForegroundColor Green
$largeDirs = @()
Get-ChildItem $ProjectRoot -Directory | Where-Object { $_.Name -notin @('.git', '__pycache__') } | ForEach-Object {
  $d = $_
  $count = (Get-ChildItem $d.FullName -Recurse -ErrorAction SilentlyContinue -File | Measure-Object).Count
  $size = (Get-ChildItem $d.FullName -Recurse -ErrorAction SilentlyContinue -File | Measure-Object -Property Length -Sum).Sum
  $sizeMB = if ($size) { [math]::Round($size / 1MB, 2) } else { 0 }
  if ($count -gt 200 -or $sizeMB -gt 20) {
    $isCandidate = $d.Name -in $ArchiveCandidates
    $status = if ($isCandidate) { "CAN ARCHIVE" } else { "UNKNOWN" }
    $color = if ($isCandidate) { "Yellow" } else { "Red" }
    Write-Host "  $($d.Name): $count files, $sizeMB MB -> $status" -ForegroundColor $color
    if ($isCandidate) {
      $findings += @{ Category = "ProjectDir"; Item = $d.Name; Detail = "$count files, $sizeMB MB"; Action = "Archive to $ArchiveDir" }
    }
  }
}

# 1C: Root .gitignore Audit
Write-Host "Root .gitignore Audit..." -ForegroundColor Green
$hasGitIgnore = Test-Path "$ProjectRoot\.gitignore"
if (-not $hasGitIgnore) {
  $issues += "No root .gitignore -- VCS watcher scans everything"
  $findings += @{ Category = "Config"; Item = ".gitignore"; Detail = "Missing"; Action = "Create with archive dirs excluded" }
  Write-Host "  MISSING -- VCS watcher scans 7,500+ files" -ForegroundColor Red
} else {
  Write-Host "  Exists" -ForegroundColor Green
}

# 1D: Stale Agent References
Write-Host "Stale Reference Audit..." -ForegroundColor Green
$staleRefs = @()
$gayaMdPath = "$ConfigDir\agents\Gaya.md"
if (Test-Path $gayaMdPath) {
  $gayaMd = Get-Content $gayaMdPath -Raw
  if ($gayaMd -match "Bob") {
    $staleRefs += "Gaya.md still references 'Bob' (should be Tvashtar)"
    $findings += @{ Category = "AgentConfig"; Item = "Gaya.md"; Detail = "Contains 'Bob' reference"; Action = "Update to 'Tvashtar'" }
    Write-Host "  Gaya.md has stale 'Bob' reference" -ForegroundColor Red
  }
}

# Check agent files for dead model paths
Get-ChildItem "$ConfigDir\agents" -Filter "*.md" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
  $content = Get-Content $_.FullName -Raw
  if ($content -match "model:\s*ollama/(qwen2\.5:7b|llama3\.1:8b)") {
    $staleRefs += "$($_.Name) references old model: $($matches[0])"
    $findings += @{ Category = "AgentModel"; Item = $_.Name; Detail = $matches[0]; Action = "Update model reference" }
    Write-Host "  $($_.Name): stale model reference" -ForegroundColor Red
  }
}

# 1E: Memory File Audit
Write-Host "Memory File Audit..." -ForegroundColor Green
Get-ChildItem $MemoryDir -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | ForEach-Object {
  $sizeKB = [math]::Round($_.Length / 1KB, 2)
  $findings += @{ Category = "Memory"; Item = $_.Name; Detail = "$sizeKB KB, modified $($_.LastWriteTime.ToString('yyyy-MM-dd'))"; Action = "Archive (>30 days old)" }
  Write-Host "  $($_.Name): $sizeKB KB, $($_.LastWriteTime.ToString('yyyy-MM-dd')) -- OLD" -ForegroundColor Yellow
}

Get-ChildItem $MemoryDir -Filter "_legacy-*" | ForEach-Object {
  $sizeKB = [math]::Round($_.Length / 1KB, 2)
  $findings += @{ Category = "Memory"; Item = $_.Name; Detail = "$sizeKB KB, legacy config"; Action = "Archive (superseded)" }
  Write-Host "  $($_.Name): legacy config -- can archive" -ForegroundColor Yellow
}

# 1F: Backup File Audit
Write-Host "Backup File Audit..." -ForegroundColor Green
if (Test-Path $BackupDir) {
  Get-ChildItem $BackupDir -File -ErrorAction SilentlyContinue | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    $action = if ($sizeMB -gt 500) { "Consider archiving ($sizeMB MB)" } else { "OK" }
    $findings += @{ Category = "Backup"; Item = $_.Name; Detail = "$sizeMB MB"; Action = $action }
    $color = if ($sizeMB -gt 500) { "Yellow" } else { "Green" }
    Write-Host "  $($_.Name): $sizeMB MB" -ForegroundColor $color
  }
}

# === PHASE 2: REPORT ===
Write-Host ""
Write-Host "--- PHASE 2: MAINTENANCE REPORT ---" -ForegroundColor Yellow
Write-Host ""

$needsAction = @($findings | Where-Object { $_.Action -ne "OK" })
Write-Host "Found $($needsAction.Count) items needing action" -ForegroundColor Cyan
Write-Host ""

if ($needsAction.Count -eq 0) {
  Write-Host "Everything is clean. No maintenance needed." -ForegroundColor Green
  exit 0
}

$needsAction | Group-Object Category | ForEach-Object {
  Write-Host "  [$($_.Name)]" -ForegroundColor Cyan
  $_.Group | ForEach-Object {
    Write-Host "    . $($_.Item): $($_.Detail) -> $($_.Action)" -ForegroundColor White
  }
}

# === PHASE 3: APPROVAL ===
Write-Host ""
Write-Host "--- PHASE 3: APPROVAL ---" -ForegroundColor Yellow
Write-Host ""

if (-not $AutoApprove) {
  Write-Host "This will archive $($needsAction.Count) items to: $ArchiveDir" -ForegroundColor Yellow
  Write-Host "Nothing will be deleted -- all files are moved to archive." -ForegroundColor Yellow
  Write-Host ""
  $confirmation = Read-Host "Proceed with maintenance? (y/N)"
  if ($confirmation -ne "y" -and $confirmation -ne "Y") {
    Write-Host ""
    Write-Host "Maintenance aborted by user." -ForegroundColor Red
    Write-Host "Run again with -AutoApprove to skip confirmation."
    exit 1
  }
} else {
  Write-Host "Auto-approve enabled. Executing..." -ForegroundColor Green
}

# === PHASE 4: EXECUTION ===
Write-Host ""
Write-Host "--- PHASE 4: EXECUTION ---" -ForegroundColor Yellow
Write-Host ""

New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null
New-Item -ItemType Directory -Path "$ArchiveDir\project-dirs" -Force | Out-Null
New-Item -ItemType Directory -Path "$ArchiveDir\memory" -Force | Out-Null
New-Item -ItemType Directory -Path "$ArchiveDir\backups" -Force | Out-Null

$executed = @()
$errors = @()

# 4A: VACUUM DB
$dbAction = $needsAction | Where-Object { $_.Category -eq "DB" -and $_.Action -like "VACUUM*" }
if ($dbAction.Count -gt 0) {
  Write-Host "VACUUM DB..." -ForegroundColor Green
  $beforeSize = (Get-Item $DbPath).Length
  try {
    $sqliteCheck = Get-Command "sqlite3" -ErrorAction SilentlyContinue
    if (-not $sqliteCheck) {
      $sqliteCheck = Get-Command "sqlite3.exe" -ErrorAction SilentlyContinue
    }
    if ($sqliteCheck) {
      $result = & $sqliteCheck.Source $DbPath "VACUUM;" 2>&1
      if ($LASTEXITCODE -eq 0) {
        $afterSize = (Get-Item $DbPath).Length
        $freedMB = [math]::Round(($beforeSize - $afterSize) / 1MB, 2)
        $beforeMB = [math]::Round($beforeSize / 1MB, 2)
        $afterMB = [math]::Round($afterSize / 1MB, 2)
        $executed += "DB VACUUM: Freed $freedMB MB (${beforeMB}MB -> ${afterMB}MB)"
        Write-Host "  Freed $freedMB MB" -ForegroundColor Green
      } else {
        $executed += "DB VACUUM: sqlite3 returned exit code $LASTEXITCODE"
        Write-Host "  sqlite3 returned exit code $LASTEXITCODE" -ForegroundColor Yellow
      }
    } else {
      $executed += "DB VACUUM: SKIPPED -- sqlite3 not found in PATH"
      Write-Host "  sqlite3 not available in PATH" -ForegroundColor Yellow
    }
  } catch {
    $errors += "DB VACUUM failed: $_"
    Write-Host "  Failed: $_" -ForegroundColor Red
  }
}

# 4B: Create Root .gitignore
$gitignoreAction = $needsAction | Where-Object { $_.Category -eq "Config" -and $_.Item -eq ".gitignore" }
if ($gitignoreAction.Count -gt 0) {
  Write-Host "Creating root .gitignore..." -ForegroundColor Green
  try {
    $gitignoreContent = @"
# Generated by Gaya Auto-Maintenance on $Timestamp
# Excludes archived/old directories from OpenCode VCS watcher

# Node / dependencies
node_modules/
package-lock.json

# Archive copies of old systems
agent-system/
Gaya-Agent/
gaya-voice/
archived/

# Old projects (not actively worked on)
kiosk-chatbot/
god-simulator/
Ryze studio/
Parul Uni/
autodesk-bim/
Autodesk_automation/
max auto/
Kho/
Visual_chat_bot/

# Build outputs
__pycache__/
*.pyc

# OS junk
Thumbs.db
.DS_Store
"@
    Set-Content -Path "$ProjectRoot\.gitignore" -Value $gitignoreContent -Encoding ASCII
    $executed += "Created root .gitignore"
    Write-Host "  Created" -ForegroundColor Green
  } catch {
    $errors += "Failed to create .gitignore: $_"
    Write-Host "  Failed: $_" -ForegroundColor Red
  }
}

# 4C: Archive Heavy Project Dirs
$dirsToArchive = $needsAction | Where-Object { $_.Category -eq "ProjectDir" }
if ($dirsToArchive.Count -gt 0) {
  Write-Host "Archiving project directories..." -ForegroundColor Green
  foreach ($candidate in $dirsToArchive) {
    $src = "$ProjectRoot\$($candidate.Item)"
    $dst = "$ArchiveDir\project-dirs\$($candidate.Item)"
    if (Test-Path $src) {
      try {
        Write-Host "  Moving $($candidate.Item)..." -ForegroundColor Yellow
        Move-Item -Path $src -Destination $dst -Force
        $executed += "Archived $($candidate.Item)"
        Write-Host "    -> $dst" -ForegroundColor Green
      } catch {
        $errors += "Failed to archive $($candidate.Item): $_"
        Write-Host "    Failed: $_" -ForegroundColor Red
      }
    }
  }
}

# 4D: Fix Stale Bob Reference
if ($staleRefs.Count -gt 0) {
  Write-Host "Fixing stale references..." -ForegroundColor Green
  try {
    $content = Get-Content $gayaMdPath -Raw
    $content = $content -replace "Bob   -> Qwen 3 Coder \(OpenRouter\)", "Tvashtar -> Qwen 2.5 Coder 7B (Ollama, local)"
    $content = $content -replace "## Bob", "## Tvashtar"
    Set-Content -Path $gayaMdPath -Value $content -Encoding UTF8 -NoNewline
    $executed += "Fixed Gaya.md: Bob -> Tvashtar"
    Write-Host "  Updated Gaya.md" -ForegroundColor Green
  } catch {
    $errors += "Failed to fix Gaya.md: $_"
    Write-Host "  Failed: $_" -ForegroundColor Red
  }
}

# 4E: Archive Old Memory Files
$memoryToArchive = $needsAction | Where-Object { $_.Category -eq "Memory" -and $_.Action -like "Archive*" }
if ($memoryToArchive.Count -gt 0) {
  Write-Host "Archiving old memory files..." -ForegroundColor Green
  foreach ($memItem in $memoryToArchive) {
    $src = "$MemoryDir\$($memItem.Item)"
    $dst = "$ArchiveDir\memory\$($memItem.Item)"
    if (Test-Path $src) {
      try {
        Move-Item -Path $src -Destination $dst -Force
        $executed += "Archived memory: $($memItem.Item)"
        Write-Host "  $($memItem.Item) -> archive" -ForegroundColor Green
      } catch {
        $errors += "Failed to archive $($memItem.Item): $_"
        Write-Host "  Failed: $_" -ForegroundColor Red
      }
    }
  }
}

# 4F: Archive massive backups
$backupsToArchive = $needsAction | Where-Object { $_.Category -eq "Backup" -and $_.Action -like "Consider*" }
if ($backupsToArchive.Count -gt 0) {
  Write-Host "Archiving large backups..." -ForegroundColor Green
  foreach ($bkItem in $backupsToArchive) {
    $src = "$BackupDir\$($bkItem.Item)"
    $dst = "$ArchiveDir\backups\$($bkItem.Item)"
    if (Test-Path $src) {
      try {
        Move-Item -Path $src -Destination $dst -Force
        $executed += "Archived backup: $($bkItem.Item)"
        Write-Host "  $($bkItem.Item) -> archive" -ForegroundColor Green
      } catch {
        $errors += "Failed to archive $($bkItem.Item): $_"
        Write-Host "  Failed: $_" -ForegroundColor Red
      }
    }
  }
}

# === PHASE 5: SUMMARY ===
Write-Host ""
Write-Host "--- PHASE 5: MAINTENANCE SUMMARY ---" -ForegroundColor Yellow
Write-Host ""

Write-Host "Archive location: $ArchiveDir" -ForegroundColor Cyan
Write-Host ""

if ($executed.Count -gt 0) {
  Write-Host "Executed ($($executed.Count) actions):" -ForegroundColor Green
  $executed | ForEach-Object { Write-Host "  . $_" -ForegroundColor White }
}

if ($errors.Count -gt 0) {
  Write-Host ""
  Write-Host "Errors ($($errors.Count)):" -ForegroundColor Red
  $errors | ForEach-Object { Write-Host "  . $_" -ForegroundColor Red }
}

Write-Host ""
Write-Host "Log saved to: $LogFile" -ForegroundColor White

$status = if ($errors.Count -eq 0) { "SUCCESS" } else { "PARTIAL -- $($errors.Count) errors" }
$logEntry = @"
[$Timestamp] Gaya Auto-Maintenance
  Status: $status
  Executed: $($executed.Count) actions
  Archive: $ArchiveDir
"@
if ($executed.Count -gt 0) {
  $logEntry += "`n  Actions:`n    " + ($executed -join "`n    ")
}
if ($errors.Count -gt 0) {
  $logEntry += "`n  Errors:`n    " + ($errors -join "`n    ")
}
Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8

Write-Host ""
Write-Host "=== MAINTENANCE COMPLETE ===" -ForegroundColor Cyan
Write-Host "Next scheduled: $(Get-Date (Get-Date).AddDays(15) -Format 'yyyy-MM-dd')" -ForegroundColor Cyan
Write-Host ""
