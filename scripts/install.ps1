<#
.SYNOPSIS
    Gaya Agent — One-command install for OpenCode
.DESCRIPTION
    Installs the complete Gaya MoE agent system:
      - 4 agent personas (Gaya, LOGOS, Freya, Tvashtar)
      - 2 config templates (local GPU + cloud free tier)
      - Shared memory core, auto-maintenance, and skills dashboard
    Auto-detects hardware and recommends the right config.
.NOTES
    Re-run to switch modes or update. Backs up existing config.
#>

#requires -Version 5.1

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
$script:Version = "2.0.0"

function Write-Header {
    Clear-Host
    Write-Host "╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                   ║" -ForegroundColor Cyan
    Write-Host "║   GAYA  --  Divine Commander                      ║" -ForegroundColor Cyan
    Write-Host "║   Philosopher . Poet . Evergrowth                 ║" -ForegroundColor Cyan
    Write-Host "║                                                   ║" -ForegroundColor Cyan
    Write-Host "║   v$($script:Version)  |  MoE Agent System for OpenCode      ║" -ForegroundColor Cyan
    Write-Host "║                                                   ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Message, [string]$Status = "pending")
    switch ($Status) {
        "done"   { Write-Host "  ✓ " -ForegroundColor Green -NoNewline; Write-Host "$Message" }
        "fail"   { Write-Host "  ✗ " -ForegroundColor Red -NoNewline; Write-Host "$Message" }
        "skip"   { Write-Host "  → " -ForegroundColor Yellow -NoNewline; Write-Host "$Message" }
        "info"   { Write-Host "  ℹ " -ForegroundColor Cyan -NoNewline; Write-Host "$Message" }
        "warn"   { Write-Host "  ⚠ " -ForegroundColor Yellow -NoNewline; Write-Host "$Message" }
        default  { Write-Host "  · " -NoNewline; Write-Host "$Message" }
    }
}

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
$script:OpenCodeDir   = "$env:USERPROFILE\.config\opencode"
$script:AgentsDir     = "$script:OpenCodeDir\agents"
$script:MemoryDir     = "$script:OpenCodeDir\memory"
$script:ScriptsDir    = "$script:OpenCodeDir\scripts"
$script:ConfigFile    = "$script:OpenCodeDir\opencode.jsonc"
$script:ConfigBackup  = "$script:OpenCodeDir\opencode.jsonc.bak"
$script:AutoMaintPath = "$script:ScriptsDir\auto-maintenance.ps1"
$script:VersionFile   = "$script:OpenCodeDir\.gaya-version"
$script:LATEST_RELEASE = "https://api.github.com/repos/ronakraval104-sys/Gaya_Agent_PR/releases/latest"
$script:REPO_URL       = "https://github.com/ronakraval104-sys/Gaya_Agent_PR.git"

$script:RepoRoot     = $PSScriptRoot | Split-Path -Parent
$script:SourceAgents = Join-Path $script:RepoRoot "agents"
$script:SourceConfigs= Join-Path $script:RepoRoot "configs"
$script:SourceMemory = Join-Path $script:RepoRoot "memory"
$script:SourceHTML   = Join-Path $script:RepoRoot "skills-dashboard.html"

# ═══════════════════════════════════════════════════════════════
# HARDWARE DETECTION
# ═══════════════════════════════════════════════════════════════
function Test-OllamaInstalled {
    return (Get-Command "ollama" -ErrorAction SilentlyContinue) -ne $null
}

function Test-OllamaRunning {
    if (-not (Test-OllamaInstalled)) { return $false }
    try {
        $result = ollama list 2>&1
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Test-GPUAvailable {
    try {
        $gpu = Get-WmiObject Win32_VideoController | Where-Object {
            $_.Name -match "NVIDIA|AMD|Intel.*Arc|RTX|GTX|Radeon"
        }
        return ($gpu -ne $null)
    } catch {
        return $false
    }
}

function Get-GPUInfo {
    try {
        $gpu = Get-WmiObject Win32_VideoController | Where-Object {
            $_.Name -match "NVIDIA|AMD|Intel.*Arc|RTX|GTX|Radeon"
        } | Select-Object -First 1
        if ($gpu) {
            $vram = if ($gpu.AdapterRAM) { [math]::Round($gpu.AdapterRAM / 1GB, 1) } else { "unknown" }
            return "$($gpu.Name) ($vram GB VRAM)"
        }
        return "none detected"
    } catch { return "unknown" }
}

function Get-RecommendedConfig {
    $ollamaRunning = Test-OllamaRunning
    $gpuInfo = Get-GPUInfo

    if ($ollamaRunning -and $gpuInfo -ne "none detected") {
        return "local-gpu"
    } else {
        return "cloud-zen"
    }
}

# ═══════════════════════════════════════════════════════════════
# VERSION / UPGRADE DETECTION
# ═══════════════════════════════════════════════════════════════
function Get-InstalledVersion {
    if (-not (Test-Path $script:ConfigFile)) { return $null }
    if (Test-Path $script:VersionFile) {
        try {
            $vdata = Get-Content $script:VersionFile -Raw | ConvertFrom-Json
            return @{
                version = $vdata.version
                date    = $vdata.releaseDate
                mode    = $vdata.configMode
            }
        } catch { return @{ version = "unknown"; date = "unknown"; mode = "unknown" } }
    }
    # No version file but config exists → legacy v1
    $config = Get-Content $script:ConfigFile -Raw
    if ($config -match "Bob") { return @{ version = "1.0.0"; date = "legacy"; mode = "unknown" } }
    return @{ version = "unknown"; date = "unknown"; mode = "unknown" }
}

function Get-LatestRelease {
    try {
        $response = Invoke-RestMethod -Uri $script:LATEST_RELEASE -Method Get -TimeoutSec 10 -ErrorAction SilentlyContinue
        return @{
            tag_name = if ($response.tag_name) { $response.tag_name } else { $script:Version }
            html_url = if ($response.html_url) { $response.html_url } else { $script:REPO_URL }
            body     = if ($response.body) { $response.body.Substring(0, [Math]::Min(200, $response.body.Length)) } else { "" }
        }
    } catch {
        return @{ tag_name = $script:Version; html_url = $script:REPO_URL; body = "" }
    }
}

function Write-VersionFile {
    param([string]$ConfigMode)
    $vdata = @{
        version = $script:Version
        releaseDate = (Get-Date -Format "yyyy-MM-dd")
        configMode = $ConfigMode
        releaseUrl = "$script:REPO_URL/releases/tag/v$script:Version"
    }
    $vdata | ConvertTo-Json | Set-Content $script:VersionFile -Force
    Write-Step "Version file written." "done"
}

# ═══════════════════════════════════════════════════════════════
# INSTALLATION
# ═══════════════════════════════════════════════════════════════
function Install-AgentFiles {
    param([string]$UserName)

    Write-Step "Copying agent personas..." "info"
    if (-not (Test-Path $script:AgentsDir)) { New-Item -ItemType Directory -Path $script:AgentsDir -Force | Out-Null }

    $agentFiles = @("Gaya.md", "LOGOS.md", "Freya.md", "Tvashtar.md")
    $copied = 0
    foreach ($file in $agentFiles) {
        $src = Join-Path $script:SourceAgents $file
        $dst = Join-Path $script:AgentsDir $file
        if (Test-Path $src) {
            Copy-Item $src $dst -Force
            # Replace {{USER_NAME}} placeholder
            (Get-Content $dst -Raw) -replace '\{\{USER_NAME\}\}', $UserName | Set-Content $dst -Force
            $copied++
        } else {
            Write-Step "Agent file missing: $file" "warn"
        }
    }
    Write-Step "$copied of $($agentFiles.Count) agent files installed." "done"
}

function Install-MemoryFiles {
    Write-Step "Copying memory files..." "info"
    if (-not (Test-Path $script:MemoryDir)) { New-Item -ItemType Directory -Path $script:MemoryDir -Force | Out-Null }

    $memoryFiles = @("moe-orchestrator-framework.md", "auto-maintenance-protocol.md")
    $copied = 0
    foreach ($file in $memoryFiles) {
        $src = Join-Path $script:SourceMemory $file
        $dst = Join-Path $script:MemoryDir $file
        if (Test-Path $src) {
            Copy-Item $src $dst -Force
            $copied++
        } else {
            Write-Step "Memory file missing: $file" "warn"
        }
    }
    Write-Step "$copied of $($memoryFiles.Count) memory files installed." "done"
}

function Install-AutoMaintenance {
    Write-Step "Installing auto-maintenance script..." "info"
    $src = Join-Path $script:RepoRoot "scripts\auto-maintenance.ps1"
    if (Test-Path $src) {
        if (-not (Test-Path $script:ScriptsDir)) { New-Item -ItemType Directory -Path $script:ScriptsDir -Force | Out-Null }
        Copy-Item $src $script:AutoMaintPath -Force
        Write-Step "Auto-maintenance installed at: $script:AutoMaintPath" "done"
    } else {
        Write-Step "Auto-maintenance script not found in repo (optional, skipping)" "skip"
    }
}

function Install-SkillsDashboard {
    Write-Step "Installing skills dashboard..." "info"
    $dst = Join-Path $script:OpenCodeDir "skills-dashboard.html"
    if (Test-Path $script:SourceHTML) {
        Copy-Item $script:SourceHTML $dst -Force
        Write-Step "Skills dashboard installed at: $dst" "done"
    } else {
        Write-Step "Skills dashboard not found in repo (optional, skipping)" "skip"
    }
}

function Generate-Config {
    param([string]$UserName, [string]$ConfigMode)

    Write-Step "Generating opencode.jsonc ($ConfigMode mode)..." "info"

    # Backup existing config
    if (Test-Path $script:ConfigFile) {
        Copy-Item $script:ConfigFile $script:ConfigBackup -Force
        Write-Step "Existing config backed up to: $script:ConfigBackup" "skip"
    }

    # Select template
    $templateFile = Join-Path $script:SourceConfigs "$ConfigMode.jsonc"
    if (-not (Test-Path $templateFile)) {
        Write-Step "Config template not found: $templateFile" "fail"
        return $false
    }

    # Read and substitute
    $config = Get-Content $templateFile -Raw
    $config = $config -replace '\{\{USER_NAME\}\}', $UserName
    $config = $config -replace '\{\{OPENCODE_DIR\}\}', $script:OpenCodeDir.Replace('\', '\\')
    $config = $config -replace '\{\{AGENTS_DIR\}\}', $script:AgentsDir.Replace('\', '\\')
    $config = $config -replace '\{\{MEMORY_DIR\}\}', $script:MemoryDir.Replace('\', '\\')

    Set-Content -Path $script:ConfigFile -Value $config -Force

    Write-Step "Config generated at: $script:ConfigFile" "done"
    return $true
}

function Install-LevelingSystem {
    Write-Step "Installing leveling system..." "info"
    $src = Join-Path $script:RepoRoot "LEVELING_SYSTEM.md"
    $dst = Join-Path $script:MemoryDir "LEVELING_SYSTEM.md"
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Step "Leveling system installed." "done"
    } else {
        Write-Step "LEVELING_SYSTEM.md not found (optional, skipping)" "skip"
    }
}

function Install-AgentSchema {
    Write-Step "Installing agent profile schema..." "info"
    $src = Join-Path $script:RepoRoot "agent-profile-schema.json"
    $dst = Join-Path $script:MemoryDir "agent-profile-schema.json"
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Step "Schema installed." "done"
    } else {
        Write-Step "agent-profile-schema.json not found (optional, skipping)" "skip"
    }
}

function Pull-OllamaModels {
    Write-Step "Pulling Ollama models..." "info"
    Write-Step "This may take a while (5-15 minutes depending on download speed)." "info"

    $models = @(
        "qwen3:4b-instruct-2507-q4_K_M",
        "phi4-mini:3.8b",
        "qwen2.5vl",
        "qwen2.5-coder-fixed:7b"
    )

    foreach ($model in $models) {
        Write-Step "Pulling $model..." "info"
        $result = ollama pull $model 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Step "$model pulled successfully." "done"
        } else {
            Write-Step "Failed to pull $model. Error: $result" "fail"
        }
    }
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
function Main {
    Write-Header

    # ── Check for existing install ──
    $existingVersion = Get-InstalledVersion
    $isExistingInstall = $existingVersion -ne $null

    if ($isExistingInstall) {
        Write-Step "Existing install detected: v$($existingVersion.version) ($($existingVersion.mode))" "info"
        $latest = Get-LatestRelease
        $isUpgradeAvailable = $latest.tag_name -ne $existingVersion.version -and $latest.tag_name -ne ""

        if ($isUpgradeAvailable) {
            Write-Host ""
            Write-Host "┌─ UPGRADE AVAILABLE ──────────────────────────┐" -ForegroundColor Yellow
            Write-Host "│                                                  │" -ForegroundColor Yellow
            Write-Host "│  You have:  v$($existingVersion.version)                     │" -ForegroundColor Yellow
            Write-Host "│  Latest:    $($latest.tag_name)                       │" -ForegroundColor Yellow
            Write-Host "│                                                  │" -ForegroundColor Yellow
            Write-Host "│  $($latest.body)        │" -ForegroundColor White
            Write-Host "│                                                  │" -ForegroundColor Yellow
            Write-Host "│  Run upgrade? Agent files + config will update.  │" -ForegroundColor Yellow
            Write-Host "│  Your memory files and backups are preserved.    │" -ForegroundColor Yellow
            Write-Host "└──────────────────────────────────────────────────┘" -ForegroundColor Yellow
            Write-Host ""
            $upgradeChoice = Read-Host "Upgrade to $($latest.tag_name)? (Y/n)"
            if ($upgradeChoice -eq "" -or $upgradeChoice -eq "y" -or $upgradeChoice -eq "Y") {
                Write-Step "Upgrading to $($latest.tag_name)..." "info"
            } else {
                Write-Step "Upgrade cancelled. Exiting." "skip"
                return
            }
        } else {
            Write-Step "Already at the latest version ($($latest.tag_name))." "done"
            Write-Host ""
            Write-Host "┌─ RE-RUN OPTIONS ─────────────────────────────┐" -ForegroundColor Cyan
            Write-Host "│                                                  │" -ForegroundColor Cyan
            Write-Host "│  1. Reinstall  — refresh agent files + config   │" -ForegroundColor Cyan
            Write-Host "│  2. Switch mode — toggle GPU / Cloud            │" -ForegroundColor Cyan
            Write-Host "│  3. Repair     — fix missing files only         │" -ForegroundColor Cyan
            Write-Host "│  4. Cancel                                       │" -ForegroundColor Cyan
            Write-Host "└──────────────────────────────────────────────────┘" -ForegroundColor Cyan
            Write-Host ""
            $rerunChoice = Read-Host "Choice (1-4, Enter = 1)"
            if ($rerunChoice -eq "4") { Write-Step "Cancelled." "skip"; return }
            if ($rerunChoice -eq "3") {
                Write-Step "Repair mode: reinstalling only missing files..." "info"
                Repair-MissingFiles
                Write-Step "Repair complete." "done"
                return
            }
            if ($rerunChoice -eq "2") { Write-Step "Switching config mode..." "info" }
        }
    }

    # ── Verify repo structure ──
    Write-Step "Verifying repo structure..." "info"
    $requiredDirs = @("agents", "configs", "scripts")
    $missing = @()
    foreach ($dir in $requiredDirs) {
        if (-not (Test-Path (Join-Path $script:RepoRoot $dir))) {
            $missing += $dir
        }
    }
    if ($missing.Count -gt 0) {
        Write-Step "Missing directories: $($missing -join ', ')" "fail"
        Write-Step "Run this script from the Gaya_Agent_PR repo root." "fail"
        Write-Host ""
        if ($isExistingInstall) {
            Write-Step "You can paste the repo URL into OpenCode instead of cloning." "info"
            Write-Host "  URL: $script:REPO_URL" -ForegroundColor Yellow
        } else {
            Write-Host "  Example: cd Gaya_Agent_PR; .\scripts\install.ps1" -ForegroundColor Yellow
        }
        Write-Host ""
        pause
        return
    }
    Write-Step "Repo structure verified." "done"

    # ── Hardware detection ──
    Write-Step "Detecting hardware..." "info"
    $ollamaInstalled = Test-OllamaInstalled
    $ollamaRunning   = Test-OllamaRunning
    $gpuAvailable    = Test-GPUAvailable
    $gpuInfo         = Get-GPUInfo
    $recommended     = Get-RecommendedConfig

    if ($ollamaInstalled) { Write-Step "Ollama installed." "done" }
    else { Write-Step "Ollama not found." "skip" }

    if ($ollamaRunning) { Write-Step "Ollama is running." "done" }
    else { 
        Write-Step "Ollama is not running." "skip"
        if ($ollamaInstalled) {
            Write-Step "Start Ollama to use GPU mode, or choose Cloud mode below." "info"
            $recommended = "cloud-zen"
        }
    }

    Write-Step "GPU detected: $gpuInfo" "done"

    # ── User name (skip if already installed) ──
    if (-not $isExistingInstall) {
        Write-Host ""
        Write-Host "┌─ Who are you? ─────────────────────────────────┐" -ForegroundColor Cyan
        Write-Host "│                                                  │" -ForegroundColor Cyan
        Write-Host "│  This name is used in agent personas.            │" -ForegroundColor Cyan
        Write-Host "│  (Enter = use 'User')                            │" -ForegroundColor Cyan
        Write-Host "└──────────────────────────────────────────────────┘" -ForegroundColor Cyan
        $userName = Read-Host "Your name"
        if ([string]::IsNullOrWhiteSpace($userName)) { $userName = "User" }
        Write-Step "Welcome, $userName." "info"
    } else {
        # Try to get existing user name from agent files
        $gayaFile = Join-Path $script:AgentsDir "Gaya.md"
        if (Test-Path $gayaFile) {
            $gayaContent = Get-Content $gayaFile -Raw
            if ($gayaContent -match "goes by \*\*(.+?)\*\*") { $userName = $matches[1] }
            else { $userName = "User" }
        } else { $userName = "User" }
        Write-Step "Using existing user: $userName" "info"
    }

    # ── Config selection ──
    Write-Host ""
    Write-Host "┌─ Config Mode ──────────────────────────────────┐" -ForegroundColor Cyan
    Write-Host "│                                                  │" -ForegroundColor Cyan
    Write-Host "│  [$($recommended)] is recommended for your hardware.      │" -ForegroundColor Cyan
    Write-Host "│                                                  │" -ForegroundColor Cyan
    Write-Host "│  1. Local GPU  (Ollama — 4 models, ~15 GB total) │" -ForegroundColor Cyan
    Write-Host "│  2. Cloud      (Zen + OpenRouter free tier)     │" -ForegroundColor Cyan
    Write-Host "└──────────────────────────────────────────────────┘" -ForegroundColor Cyan
    $choice = Read-Host "Choice (1 or 2, Enter = $($recommended -eq 'local-gpu' ? '1' : '2'))"
    $configMode = "local-gpu"
    if ([string]::IsNullOrWhiteSpace($choice)) {
        $configMode = $recommended
    } elseif ($choice -eq "2" -or $choice -match "cloud") {
        $configMode = "cloud-zen"
    }
    Write-Step "Using config: $configMode" "done"

    # ── Install steps ──
    Write-Host ""
    $sectionTitle = if ($isExistingInstall) { "UPGRADING" } else { "INSTALLING" }
    Write-Host "┌─ $sectionTitle... ─────────────────────────────┐" -ForegroundColor Cyan
    Write-Host ""

    Install-AgentFiles -UserName $userName
    Install-MemoryFiles
    Install-AutoMaintenance
    Install-SkillsDashboard
    Install-LevelingSystem
    Install-AgentSchema
    Generate-Config -UserName $userName -ConfigMode $configMode
    Write-VersionFile -ConfigMode $configMode

    # ── Pull models (GPU mode only) ──
    if ($configMode -eq "local-gpu") {
        if ($ollamaRunning) {
            Write-Host ""
            Pull-OllamaModels
        } else {
            Write-Step "Ollama is not running. Skipping model pull." "skip"
            Write-Step "Start Ollama and run: ollama pull qwen3:4b-instruct-2507-q4_K_M" "info"
        }
    }

    # ── Set OLLAMA_KEEP_ALIVE=0 (GPU mode) ──
    if ($configMode -eq "local-gpu") {
        Write-Step "Setting OLLAMA_KEEP_ALIVE=0 (VRAM efficiency)..." "info"
        try {
            $env:OLLAMA_KEEP_ALIVE = "0"
            [Environment]::SetEnvironmentVariable("OLLAMA_KEEP_ALIVE", "0", "User")
            Write-Step "OLLAMA_KEEP_ALIVE=0 set." "done"
        } catch {
            Write-Step "Could not set environment variable (admin rights may be needed)." "warn"
        }
    }

    # ── Done ──
    Write-Host ""
    $verb = if ($isExistingInstall) { "UPGRADE" } else { "INSTALLATION" }
    Write-Host "┌─ ✓ $verb COMPLETE ────────────────────┐" -ForegroundColor Green
    Write-Host "│                                                  │" -ForegroundColor Green
    Write-Host "│  Restart OpenCode to load the new config.        │" -ForegroundColor Green
    Write-Host "│                                                  │" -ForegroundColor Green
    Write-Host "│  Your agents are ready:                          │" -ForegroundColor Green
    Write-Host "│    • @gaya     — Commander                       │" -ForegroundColor Cyan
    Write-Host "│    • @logos    — Logic/Reasoning                 │" -ForegroundColor Cyan
    Write-Host "│    • @freya    — Vision/Research                 │" -ForegroundColor Cyan
    Write-Host "│    • @tvashtar — Coding/Architecture             │" -ForegroundColor Cyan
    Write-Host "│                                                  │" -ForegroundColor Green
    Write-Host "│  To switch modes or update:                      │" -ForegroundColor Green
    Write-Host "│  > cd Gaya_Agent_PR; .\scripts\install.ps1      │" -ForegroundColor Yellow
    Write-Host "│                                                  │" -ForegroundColor Green
    Write-Host "│  Skills dashboard:                               │" -ForegroundColor Green
    Write-Host "│  > start $script:OpenCodeDir\skills-dashboard.html│" -ForegroundColor Yellow
    Write-Host "│                                                  │" -ForegroundColor Green
    Write-Host "└──────────────────────────────────────────────────┘" -ForegroundColor Green
    Write-Host ""

    Write-Host "╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                   ║" -ForegroundColor Cyan
    Write-Host "║  \"The quality of your action is your signature.\"    ║" -ForegroundColor Cyan
    Write-Host "║                                                   ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Repair-MissingFiles {
    Write-Step "Checking for missing agent files..." "info"
    $agentFiles = @("Gaya.md", "LOGOS.md", "Freya.md", "Tvashtar.md")
    $repaired = 0
    foreach ($file in $agentFiles) {
        $dst = Join-Path $script:AgentsDir $file
        if (-not (Test-Path $dst)) {
            $src = Join-Path $script:SourceAgents $file
            if (Test-Path $src) {
                $userName = "User"
                Copy-Item $src $dst -Force
                (Get-Content $dst -Raw) -replace '\{\{USER_NAME\}\}', $userName | Set-Content $dst -Force
                Write-Step "Restored: $file" "done"
                $repaired++
            }
        }
    }
    if ($repaired -eq 0) { Write-Step "All agent files present. Nothing to repair." "done" }
}

# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════
Main
