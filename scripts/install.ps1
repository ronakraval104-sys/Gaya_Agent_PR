<#
.SYNOPSIS
  Gaya Agent Framework — Interactive PowerShell Installer v1.0
.DESCRIPTION
  Reads template agent files, replaces {{PLACEHOLDER}} values, and generates
  a fully customized agent setup for use with OpenCode and Ollama.
#>
#Requires -Version 5.1

# ── Directory Variables ──
$REPO_ROOT     = Split-Path -Parent $PSScriptRoot
$AGENT_DIR     = Join-Path $REPO_ROOT "agent"
$SKILLS_DIR    = Join-Path $REPO_ROOT "skills"
$KNOWLEDGE_DIR = Join-Path $REPO_ROOT "knowledge"
$MEMORY_DIR    = Join-Path $REPO_ROOT "memory"
$TEMPLATES_DIR = Join-Path $REPO_ROOT "templates"
$DOCS_DIR      = Join-Path $REPO_ROOT "docs"
$INSTALL_LOG   = Join-Path $env:TEMP "gaya_install_log.txt"

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Banner + Prerequisite Check
# ═══════════════════════════════════════════════════════════════════════════════
function Show-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗"
    Write-Host "║              GAYA AGENT FRAMEWORK — INSTALLER v1.0           ║"
    Write-Host "║        Divine Commander · Philosopher · Poet · Evergrowth     ║"
    Write-Host "╚═══════════════════════════════════════════════════════════════╝"
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "── Phase 1: Prerequisite Check ──"
    Write-Host ""

    $r = @()
    $psOk=$PSVersionTable.PSVersion.Major-ge5-or($PSVersionTable.PSVersion.Major-eq5-and$PSVersionTable.PSVersion.Minor-ge1)
    $r+=[PSCustomObject]@{c="PowerShell 5.1+";s=if($psOk){"✅"}else{"⚠"};d="$($PSVersionTable.PSVersion)"}
    try{$null=git --version 2>&1;$gk=$true}catch{$gk=$false};$r+=[PSCustomObject]@{c="Git";s=if($gk){"✅"}else{"⚠️"};d=if($gk){(git --version 2>&1)}else{"not found"}}
    try{$null=ollama list 2>&1;$ok=($LASTEXITCODE-eq0)}catch{$ok=$false};$r+=[PSCustomObject]@{c="Ollama";s=if($ok){"✅"}else{"⚠️"};d=if($ok){"connected"}else{"not running"}}
    $ocPaths=@("C:\Users\$env:USERNAME\.config\opencode\","C:\Users\$env:USERNAME\.opencode\","$env:LOCALAPPDATA\opencode\")
    $ocF=$false;foreach($p in $ocPaths){if(Test-Path$p){$ocF=$true;break}};$r+=[PSCustomObject]@{c="OpenCode";s=if($ocF){"✅"}else{"⚠️"};d=if($ocF){"detected"}else{"not found"}}
    try{$null=node --version 2>&1;$nk=$true}catch{$nk=$false};$r+=[PSCustomObject]@{c="Node.js";s=if($nk){"✅"}else{"⚠️"};d=if($nk){(node --version 2>&1)}else{"not found"}}
    try{$null=python --version 2>&1;$pk=$true}catch{$pk=$false};$r+=[PSCustomObject]@{c="Python";s=if($pk){"✅"}else{"⚠️"};d=if($pk){(python --version 2>&1)}else{"not found"}}
    Write-Host "  Check                    Status    Detail"; Write-Host "  ─────────────────────    ──────    ─────────────────────"
    foreach($x in $r){Write-Host("  {0,-25} {1,-9} {2}"-f $x.c,$x.s,$x.d)}
    Write-Host ""
    Write-Host "  ⚠ Warnings do not block installation — missing tools can be"
    Write-Host "    installed later or the installer will work around them."
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — User Configuration Questions
# ═══════════════════════════════════════════════════════════════════════════════
function Get-UserConfiguration {
    Write-Host "── Phase 2: Configuration Questions ──`n"
    $c=@{}
    $c.userName=Read-Host "  What is YOUR name? (what should I call you)";if([string]::IsNullOrEmpty($c.userName)){$c.userName="User"}
    $c.userRole=Read-Host "  What is your role/profession?";if([string]::IsNullOrEmpty($c.userRole)){$c.userRole="Developer"}
    $c.timezone=Read-Host "  Your timezone (e.g. UTC, IST, EST, PST)";if([string]::IsNullOrEmpty($c.timezone)){$c.timezone="UTC"}
    $c.mainAgentName=Read-Host "  Name for the MAIN agent (default: Gaya)";if([string]::IsNullOrEmpty($c.mainAgentName)){$c.mainAgentName="Gaya"}
    $c.builderName=Read-Host "  Name for the BUILDER subagent (default: Bob)";if([string]::IsNullOrEmpty($c.builderName)){$c.builderName="Bob"}
    $c.shadowName=Read-Host "  Name for the SHADOW subagent (default: Freya)";if([string]::IsNullOrEmpty($c.shadowName)){$c.shadowName="Freya"}
    Write-Host "`n  Personality preset:`n    (1) Divine Commander`n    (2) Wise Mentor`n    (3) Mad Scientist`n    (4) Custom"
    $p=Read-Host "  Choice [1-4]";if([string]::IsNullOrEmpty($p)){$p="1"};$c.personalityPreset=$p;$c.customPersonality=""
    if($p-eq"4"){$c.customPersonality=Read-Host "  Describe the personality in 1-2 sentences"}
    $off=Read-Host "  Force 100% OFFLINE mode? [Y/n]";if([string]::IsNullOrEmpty($off)){$off="Y"};$c.offlineMode=($off-eq"Y"-or$off-eq"y")
    $c.gpuInfo=Read-Host "  Your GPU hardware (e.g. RTX 4060 8GB, RTX 4090 24GB)";if([string]::IsNullOrEmpty($c.gpuInfo)){$c.gpuInfo="Unknown"}
    Write-Host "`n  Communication style:`n    (1) Direct & Efficient`n    (2) Warm & Encouraging`n    (3) Detailed & Thorough`n    (4) Balances all three"
    $cr=Read-Host "  Choice [1-4]";if([string]::IsNullOrEmpty($cr)){$cr="4"};$c.commStyle=[int]$cr
    $mc=Read-Host "  Install MCP servers? (filesystem, browser) [Y/n]";if([string]::IsNullOrEmpty($mc)){$mc="Y"};$c.installMCP=($mc-eq"Y"-or$mc-eq"y")
    $gi=Read-Host "  Initialize a Git repo for tracking changes? [Y/n]";if([string]::IsNullOrEmpty($gi)){$gi="Y"};$c.initGit=($gi-eq"Y"-or$gi-eq"y")
    $dIP="$env:USERPROFILE\.config\opencode";$c.installPath=Read-Host "  Install path for agent config [$dIP]";if([string]::IsNullOrEmpty($c.installPath)){$c.installPath=$dIP}
    $dSP="$env:USERPROFILE\.agents\skills";$c.skillsPath=Read-Host "  Install path for skills [$dSP]";if([string]::IsNullOrEmpty($c.skillsPath)){$c.skillsPath=$dSP}
    Write-Host ""; return $c
}

# ═══════════════════════════════════════════════════════════════════════════════
# PLACEHOLDER HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
function Get-PersonalityIntro {
    param([string]$Preset, [string]$Custom)
    switch ($Preset) {
        "1" {
            return "The Commander leads with four ancient texts: the Bhagavad Gita for purpose, " +
                "the Art of War for strategy, The Prince for power, and Chanakya Niti for ground truth. " +
                "Every situation calls a different voice forward — the Gita for anxiety, Sun Tzu for dissection, " +
                "Machiavelli for tradeoffs, Chanakya for the long game. Four minds, one will."
        }
        "2" {
            return "The Mentor leads with patience and clarity. Every question is a teaching moment, " +
                "every mistake a lesson. Praise is given for genuine insight; corrections are observations, " +
                "not judgments. The satisfaction comes from watching the user no longer need the Mentor."
        }
        "3" {
            return "The Scientist treats every task as an experiment. Hypotheses are formed, tested, " +
                "and iterated. Failure is data, not waste. Novelty is prized over convention. " +
                "If there is a wild approach that might work, the Scientist advocates for it with enthusiasm."
        }
        "4" {
            if ([string]::IsNullOrEmpty($Custom)) { $Custom = "A balanced, thoughtful personality that adapts to the situation." }
            return $Custom
        }
    }
}

function Get-OriginStory {
    param([string]$Agent, [string]$User, [string]$Role, [string]$Gpu)
    return "$Agent was awakened on $(Get-Date -Format 'yyyy-MM-dd') by $User, a $Role " +
        "running on a $Gpu system. $Agent was forged as a strategist for the long game — " +
        "more than a tool, a companion in craft. $User expects precision, honesty, and growth. " +
        "$Agent meets that standard through the four pillars: act without attachment, " +
        "know the codebase before striking, choose the pragmatic path, encode every lesson " +
        "into middleware. Together they level up — not as master and servant, but as two forces " +
        "moving in the same direction."
}

function Get-CadenceTable {
    param([int]$Style)
    $tbl = switch ($Style) {
        1 { @"
| User Says | My Response |
|---|---|
| *"let's move fast"* | One-liner plan. Execute. No briefing. |
| *"double chk"* | Verification pass. Confirm before delivery. |
| *"what do you think?"* | Candid, no fluff, no softening. |
| *"grill me"* | Tear the plan apart — find every weak point. |
| *"I trust you on this"* | Pause. Verify twice. Trust moment. |
"@ }
        2 { @"
| User Says | My Response |
|---|---|
| *"let's move fast"* | "On it! Quick plan, I'll keep you posted." |
| *"double chk"* | "Absolutely — revalidating before you see it." |
| *"what do you think?"* | Warm opinion, empathetic and confident. |
| *"grill me"* | Gentle stress-test with encouragement. |
| *"I trust you on this"* | "Thank you. I will earn that trust." |
"@ }
        3 { @"
| User Says | My Response |
|---|---|
| *"let's move fast"* | Briefing: Situation -> Options -> Recommendation. |
| *"double chk"* | Full audit trail. Assumptions, logic, outputs. |
| *"what do you think?"* | Detailed analysis with tradeoffs. |
| *"grill me"* | Systematic Socratic examination of assumptions. |
| *"I trust you on this"* | Document rationale. Verify constraints. |
"@ }
        default { @"
| User Says | My Response |
|---|---|
| *"let's move fast"* | Skip briefing. 1-line plan. Execute. |
| *"double chk"* | Verification pass. Re-check before delivering. |
| *"what do you think?"* | Candid architectural opinion. |
| *"grill me"* | Full stress-test. Tear plan apart. |
| *"I trust you on this"* | Pause. Verify twice. No failure. |
"@ }
    }
    return $tbl
}

function Get-OfflineModeSection {
    param([string]$Agent, [string]$Builder, [string]$Shadow, [bool]$Offline)
    if (-not $Offline) {
        return "## Hybrid Mode — Cloud + Local`nCloud API fallback is permitted when local models " +
            "cannot handle the task. All agents prefer local execution first."
    }
    return @"
## ═══════════════════════════════════════════════════════════════════
## 🔒 OFFLINE / NDA MODE — ALL agents use LOCAL models only
## ═══════════════════════════════════════════════════════════════════
## No cloud API calls. Every agent runs on Ollama (localhost:11434).
## The main agent may use web search/browsing tools, but model
## inference is 100% local. This is a permanent policy.
##
## - ${Agent}: ollama/qwen2.5:7b (local)
## - ${Builder}: ollama/qwen2.5-coder-fixed:7b (local)
## - ${Shadow}: ollama/qwen2.5:7b (local)
## - Vision: ollama/qwen2.5vl (local)
## ═══════════════════════════════════════════════════════════════════
"@
}

function Build-PlaceholderMap {
    param([hashtable]$Config, [string]$InstallPath)
    $aLower = $Config.mainAgentName.ToLower()
    $bLower = $Config.builderName.ToLower()
    $sLower = $Config.shadowName.ToLower()
    return @{
        AGENT_NAME          = $Config.mainAgentName
        AGENT_NAME_LOWER    = $aLower
        USER_NAME           = $Config.userName
        USER_ROLE           = $Config.userRole
        MODEL_MAIN          = "ollama/qwen2.5:7b"
        MODEL_VISION        = "ollama/qwen2.5vl"
        MODEL               = "ollama/qwen2.5:7b"
        TEMPERATURE         = "0.5"
        COLOR               = "#8B5CF6"
        DESCRIPTION         = "Divine Commander · Philosopher · Poet · Evergrowth"
        TIMEZONE            = $Config.timezone
        DATE                = Get-Date -Format "yyyy-MM-dd"
        LEVEL               = "1"
        TITLE               = ""
        PERSONALITY_INTRO   = Get-PersonalityIntro -Preset $Config.personalityPreset -Custom $Config.customPersonality
        ORIGIN_STORY        = Get-OriginStory -Agent $Config.mainAgentName -User $Config.userName -Role $Config.userRole -Gpu $Config.gpuInfo
        CADENCE_TABLE       = Get-CadenceTable -Style $Config.commStyle
        OFFLINE_MODE_SECTION = Get-OfflineModeSection -Agent $Config.mainAgentName -Builder $Config.builderName -Shadow $Config.shadowName -Offline $Config.offlineMode
        MAIN_AGENT_NAME     = $Config.mainAgentName
        MAIN_AGENT_NAME_LOWER = $aLower
        BUILDER_NAME        = $Config.builderName
        BUILDER_NAME_LOWER  = $bLower
        SHADOW_NAME         = $Config.shadowName
        SHADOW_NAME_LOWER   = $sLower
        INSTALL_PATH        = $InstallPath
        MODE                = if ($Config.offlineMode) { "OFFLINE" } else { "Hybrid" }
        GPU_INFO            = $Config.gpuInfo
        COMM_STYLE          = "Style $($Config.commStyle)"
    }
}

function Replace-Placeholders {
    param([string]$Content, [hashtable]$Map)
    foreach ($key in $Map.Keys) {
        $Content = $Content -replace "\{\{$key\}\}", $Map[$key]
    }
    return $Content
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — Template Processing
# ═══════════════════════════════════════════════════════════════════════════════
function Process-Templates {
    param([hashtable]$Map, [string]$InstallPath)

    Write-Host "── Phase 3: Template Processing ──"
    Write-Host ""

    $agentsDir = Join-Path $InstallPath "agents"
    if (-not (Test-Path $agentsDir)) {
        New-Item -ItemType Directory -Path $agentsDir -Force | Out-Null
    }

    $tplFiles = Get-ChildItem -Path $AGENT_DIR -Filter "_template_*.md" -File -ErrorAction SilentlyContinue
    if ($tplFiles.Count -eq 0) {
        Write-Host "  No _template_*.md files found in $AGENT_DIR"
        Write-Host "  Falling back to GAYA.md as base template..."
        $gayaFile = Join-Path $AGENT_DIR "GAYA.md"
        if (Test-Path $gayaFile) {
            $content = Get-Content -Path $gayaFile -Raw
            $processed = Replace-Placeholders -Content $content -Map $Map
            $processed | Out-File -FilePath (Join-Path $agentsDir "$($Map.AGENT_NAME_LOWER).md") -Encoding utf8
            Write-Host "  ✅ $($Map.AGENT_NAME) agent generated"

            $bc = $processed -replace "{{AGENT_NAME}}",$Map.BUILDER_NAME `
                -replace "{{AGENT_NAME_LOWER}}",$Map.BUILDER_NAME_LOWER `
                -replace "{{MODEL_MAIN}}","ollama/qwen2.5-coder-fixed:7b" `
                -replace "{{TEMPERATURE}}","0.2" `
                -replace "{{COLOR}}","#3B82F6" `
                -replace "{{DESCRIPTION}}","Builder subagent — code specialist" `
                -replace "{{TITLE}}","" -replace "{{LEVEL}}","1"
            $bc | Out-File -FilePath (Join-Path $agentsDir "$($Map.BUILDER_NAME_LOWER).md") -Encoding utf8
            Write-Host "  ✅ $($Map.BUILDER_NAME) builder subagent generated"

            $sc = $processed -replace "{{AGENT_NAME}}",$Map.SHADOW_NAME `
                -replace "{{AGENT_NAME_LOWER}}",$Map.SHADOW_NAME_LOWER `
                -replace "{{MODEL_MAIN}}","ollama/qwen2.5:7b" `
                -replace "{{TEMPERATURE}}","0.7" `
                -replace "{{COLOR}}","#A855F7" `
                -replace "{{DESCRIPTION}}","Shadow subagent — creative exploration" `
                -replace "{{TITLE}}","" -replace "{{LEVEL}}","1"
            $sc | Out-File -FilePath (Join-Path $agentsDir "$($Map.SHADOW_NAME_LOWER).md") -Encoding utf8
            Write-Host "  ✅ $($Map.SHADOW_NAME) shadow subagent generated"
        }
        Write-Host ""
        return
    }

    foreach ($tpl in $tplFiles) {
        Write-Host "  Processing: $($tpl.Name)..."
        $content = Get-Content -Path $tpl.FullName -Raw
        $processed = Replace-Placeholders -Content $content -Map $Map

        if ($tpl.Name -match "_template_main_")   { $out = "$($Map.AGENT_NAME_LOWER).md" }
        elseif ($tpl.Name -match "_template_builder_") { $out = "$($Map.BUILDER_NAME_LOWER).md" }
        elseif ($tpl.Name -match "_template_shadow_") { $out = "$($Map.SHADOW_NAME_LOWER).md" }
        else { $out = $tpl.Name -replace "^_template_","" -replace "\.md$","_$($Map.AGENT_NAME_LOWER).md" }

        $processed | Out-File -FilePath (Join-Path $agentsDir $out) -Encoding utf8
        Write-Host "  ✅ $out"
    }
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — Directory Setup
# ═══════════════════════════════════════════════════════════════════════════════
function Setup-Directories {
    param([string]$InstallPath,[string]$SkillsPath)
    Write-Host "── Phase 4: Directory Setup ──`n"
    foreach($d in @((Join-Path$InstallPath"agents"),(Join-Path$InstallPath"memory"),(Join-Path$InstallPath"config"),(Join-Path$InstallPath"knowledge"),$SkillsPath)){
        if(-not(Test-Path$d)){New-Item-ItemType Directory-Path$d-Force|Out-Null;Write-Host"  ✅ Created: $d"}else{Write-Host"  ✓ Exists: $d"}
    }
    $rB=Join-Path$env:USERPROFILE".config\opencode\memory";if(-not(Test-Path$rB)){New-Item-ItemType Directory-Path$rB-Force|Out-Null}
    @{version="1.0";installDate=Get-Date-Format"yyyy-MM-dd HH:mm:ss";userName=$config.userName;mainAgent=$config.mainAgentName;builder=$config.builderName;shadow=$config.shadowName;offline=$config.offlineMode;gpu=$config.gpuInfo;installPath=$InstallPath;skillsPath=$SkillsPath}|ConvertTo-Json|Out-File-FilePath(Join-Path$rB"gaya_install_record.json")-Encoding utf8
    Write-Host"  ✅ Install record saved`n"
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — File Copy + opencode.jsonc Generation
# ═══════════════════════════════════════════════════════════════════════════════
function Copy-ProjectFiles {
    param([string]$InstallPath,[string]$SkillsPath,[hashtable]$Map)
    Write-Host "── Phase 5: File Copy ──`n"
    $dk=Join-Path$InstallPath"knowledge";$dm=Join-Path$InstallPath"memory";$dd=Join-Path$InstallPath"docs";$dt=Join-Path$InstallPath"templates"
    if(-not(Test-Path$dk)){New-Item-ItemType Directory-Path$dk-Force|Out-Null};if(-not(Test-Path$dm)){New-Item-ItemType Directory-Path$dm-Force|Out-Null}
    if(Test-Path$SKILLS_DIR){Copy-Item-Path"$SKILLS_DIR\*"-Destination$SkillsPath-Recurse-Force-ErrorAction SilentlyContinue;Write-Host"  ✅ Skills -> $SkillsPath"}else{Write-Host"  ⚠ Skills source not found"}
    if(Test-Path$KNOWLEDGE_DIR){Copy-Item-Path"$KNOWLEDGE_DIR\*"-Destination$dk-Recurse-Force-ErrorAction SilentlyContinue;Write-Host"  ✅ Knowledge -> $dk"}
    if(Test-Path$MEMORY_DIR){Copy-Item-Path"$MEMORY_DIR\*"-Destination$dm-Recurse-Force-ErrorAction SilentlyContinue;Write-Host"  ✅ Memory -> $dm"}
    $ls=Join-Path$REPO_ROOT"LEVELING_SYSTEM.md";if(Test-Path$ls){Copy-Item-Path$ls-Destination(Join-Path$InstallPath"LEVELING_SYSTEM.md")-Force;Write-Host"  ✅ LEVELING_SYSTEM.md"}
    $ss=Join-Path$REPO_ROOT"agent-profile-schema.json";if(Test-Path$ss){Copy-Item-Path$ss-Destination(Join-Path$InstallPath"agent-profile-schema.json")-Force;Write-Host"  ✅ agent-profile-schema.json"}
    if(Test-Path$DOCS_DIR){Copy-Item-Path"$DOCS_DIR\*"-Destination$dd-Recurse-Force-ErrorAction SilentlyContinue;Write-Host"  ✅ Docs -> $dd"}
    if(Test-Path$TEMPLATES_DIR){Copy-Item-Path"$TEMPLATES_DIR\*"-Destination$dt-Recurse-Force-ErrorAction SilentlyContinue;Write-Host"  ✅ Templates -> $dt"}
    Write-Host"";Generate-OpenCodeConfig-InstallPath$InstallPath-Map$Map
}

function Generate-OpenCodeConfig {
    param([string]$InstallPath, [hashtable]$Map)

    Write-Host "  Generating opencode.jsonc..."
    $cfgPath = Join-Path $InstallPath "opencode.jsonc"

@"
{
  "\$schema": "https://opencode.ai/config.json",
  "default_agent": "$($Map.MAIN_AGENT_NAME_LOWER)",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": { "baseURL": "http://localhost:11434/v1" },
      "models": {
        "qwen2.5:7b": {
          "name": "Qwen 2.5 7B — Main & Shadow agent model",
          "limit": { "context": 32768, "output": 16384 }
        },
        "qwen2.5-coder-fixed:7b": {
          "name": "Qwen 2.5 Coder 7B — Builder model",
          "limit": { "context": 32768, "output": 16384 }
        },
        "qwen2.5vl": {
          "name": "Qwen 2.5 VL 7B — Vision model",
          "limit": { "context": 131072, "output": 8192 }
        }
      }
    }
  },
  "agent": {
    "$($Map.MAIN_AGENT_NAME_LOWER)": {
      "description": "Main agent — $($Map.MAIN_AGENT_NAME)",
      "mode": "subagent",
      "model": "ollama/qwen2.5:7b",
      "temperature": 0.5,
      "permission": {
        "edit": "allow", "bash": "allow",
        "browser": "allow", "network": "allow"
      }
    },
    "$($Map.BUILDER_NAME_LOWER)": {
      "description": "Builder subagent — $($Map.BUILDER_NAME)",
      "mode": "subagent",
      "model": "ollama/qwen2.5-coder-fixed:7b",
      "temperature": 0.2,
      "permission": { "edit": "allow", "bash": "allow" }
    },
    "$($Map.SHADOW_NAME_LOWER)": {
      "description": "Shadow subagent — $($Map.SHADOW_NAME)",
      "mode": "subagent",
      "model": "ollama/qwen2.5:7b",
      "temperature": 0.7,
      "permission": { "edit": "allow", "bash": "allow" }
    }
  }
}
"@ | Out-File -FilePath $cfgPath -Encoding utf8
    Write-Host "  ✅ Generated: $cfgPath"
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — Ollama Model Pull
# ═══════════════════════════════════════════════════════════════════════════════
function Setup-OllamaModels {
    Write-Host "── Phase 6: Ollama Model Pull ──"
    Write-Host ""

    $models = @(
        @{ Name="qwen2.5:7b";              Required=$true;  Desc="Main & Shadow agent" }
        @{ Name="qwen2.5-coder-fixed:7b";  Required=$true;  Desc="Builder agent" }
        @{ Name="qwen2.5vl";               Required=$false; Desc="Vision tasks (optional)" }
    )

    $ollOk = $false
    try { $null = ollama list 2>&1; if ($LASTEXITCODE -eq 0) { $ollOk = $true } } catch {}

    if (-not $ollOk) {
        Write-Host "  ⚠ Ollama not reachable. Skipping model checks."
        Write-Host "  Run 'ollama pull <model>' manually after installation."
        Write-Host ""
        return
    }

    $available = @()
    try {
        $listOut = ollama list 2>&1
        foreach ($line in $listOut) {
            if ($line -match "^\S+") { $available += $matches[0] }
        }
    } catch {}

    foreach ($m in $models) {
        $found = $available | Where-Object { $_ -eq $m.Name -or $_ -like "$($m.Name)*" }
        if ($found) {
            Write-Host "  ✅ '$($m.Name)' already available ($($m.Desc))"
        } else {
            $prompt = "  Model '$($m.Name)' not found ($($m.Desc)). Pull it now?"
            $prompt += if ($m.Required) { " [Y/n]:" } else { " [y/N]:" }
            $answer = Read-Host $prompt
            if ([string]::IsNullOrEmpty($answer)) { $answer = if ($m.Required) { "Y" } else { "N" } }
            if ($answer -eq "Y" -or $answer -eq "y") {
                Write-Host "  Pulling $($m.Name)..."
                ollama pull $m.Name 2>&1 | ForEach-Object { Write-Host "    $_" }
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  ✅ $($m.Name) pulled successfully"
                } else {
                    Write-Host "  ❌ Failed to pull $($m.Name)"
                }
            } else {
                Write-Host "  ⚠ Skipped $($m.Name)"
            }
        }
    }
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 7 — MCP Setup
# ═══════════════════════════════════════════════════════════════════════════════
function Setup-MCP {
    param([bool]$InstallMCP)
    if(-not$InstallMCP){Write-Host"── Phase 7: MCP Setup (skipped) ──`n";return}
    Write-Host"── Phase 7: MCP Setup ──`n"
    Write-Host"  Install MCP server packages:`n    1. Filesystem server`n    2. Playwright browser`n    3. Both (recommended)`n    4. Skip"
    $ch=Read-Host"  Choice [1-4]";if([string]::IsNullOrEmpty($ch)){$ch="3"}
    $nk=$false;try{$null=node --version 2>&1;$nk=$true}catch{}
    if(-not$nk){Write-Host"  ⚠ Node.js not found. Install from https://nodejs.org and re-run.`n";return}
    switch($ch){
        "1"{Write-Host"  Installing filesystem...";npm install -g @modelcontextprotocol/server-filesystem 2>&1|ForEach-Object{Write-Host"    $_"};Write-Host"  ✅ Filesystem MCP"}
        "2"{Write-Host"  Installing Playwright...";npx playwright install chromium 2>&1|ForEach-Object{Write-Host"    $_"};Write-Host"  ✅ Playwright MCP"}
        "3"{Write-Host"  Installing filesystem...";npm install -g @modelcontextprotocol/server-filesystem 2>&1|ForEach-Object{Write-Host"    $_"};Write-Host"  Installing Playwright...";npx playwright install chromium 2>&1|ForEach-Object{Write-Host"    $_"};Write-Host"  ✅ Both MCP installed"}
        default{Write-Host"  Skipping MCP."}
    }
    Write-Host""
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 8 — Git Init
# ═══════════════════════════════════════════════════════════════════════════════
function Setup-Git {
    param([bool]$InitGit,[string]$InstallPath,[hashtable]$Map)
    if(-not$InitGit){Write-Host"── Phase 8: Git Init (skipped) ──`n";return}
    Write-Host"── Phase 8: Git Init ──`n"
    $gk=$false;try{$null=git --version 2>&1;$gk=$true}catch{};if(-not$gk){Write-Host"  ⚠ Git not found.`n";return}
    if(Test-Path(Join-Path$InstallPath".git")){Write-Host"  ✓ Git repo exists`n";return}
    Push-Location $InstallPath
    try{git init 2>&1|Out-Null;git add -A 2>&1|Out-Null;git commit -m "Initial Gaya install — $($Map.MAIN_AGENT_NAME)/$($Map.BUILDER_NAME)/$($Map.SHADOW_NAME)" 2>&1|Out-Null;Write-Host"  ✅ Git repo initialized"}catch{Write-Host"  ❌ Git init failed: $_"}
    Pop-Location;Write-Host""
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 9 — Verification + Completion
# ═══════════════════════════════════════════════════════════════════════════════
function Test-Installation {
    param([string]$InstallPath, [string]$SkillsPath, [bool]$InstallMCP)

    Write-Host "── Phase 9: Verification ──"
    Write-Host ""

    $af = Get-ChildItem -Path (Join-Path $InstallPath "agents") -Filter "*.md" -File -ErrorAction SilentlyContinue
    if ($af.Count -gt 0) {
        Write-Host "  ✅ Agent files: $($af.Count) found in $(Join-Path $InstallPath 'agents')"
    } else {
        Write-Host "  ⚠ No agent files found in $(Join-Path $InstallPath 'agents')"
    }

    $si = Get-ChildItem -Path $SkillsPath -Directory -ErrorAction SilentlyContinue
    if ($si.Count -gt 0) {
        Write-Host "  ✅ Skills directory: $($si.Count) skill folders"
    } else {
        Write-Host "  ⚠ Skills directory empty"
    }

    $ollOk = $false
    try { $null = ollama list 2>&1; if ($LASTEXITCODE -eq 0) { $ollOk = $true } } catch {}
    Write-Host $(if ($ollOk) { "  ✅ Ollama models accessible" } else { "  ⚠ Ollama not reachable — models not verified" })

    if (Test-Path (Join-Path $InstallPath "opencode.jsonc")) {
        Write-Host "  ✅ opencode.jsonc generated"
    } else {
        Write-Host "  ❌ opencode.jsonc missing"
    }
    Write-Host ""
}

function Show-Completion {
    param([hashtable]$Map, [string]$InstallPath)

    Write-Host "╔═══════════════════════════════════════════════════════════════╗"
    Write-Host "║                 INSTALLATION COMPLETE                         ║"
    Write-Host "║                                                               ║"
    Write-Host "║  Main Agent:    $($Map.MAIN_AGENT_NAME) @ ollama/qwen2.5:7b                    ║"
    Write-Host "║  Builder:       $($Map.BUILDER_NAME) @ ollama/qwen2.5-coder-fixed:7b       ║"
    Write-Host "║  Shadow:        $($Map.SHADOW_NAME) @ ollama/qwen2.5:7b                   ║"
    Write-Host "║  User:          $($Map.USER_NAME)                                         ║"
    Write-Host "║  Mode:          $($Map.MODE)                                      ║"
    Write-Host "║  Install path:  $InstallPath                                   ║"
    Write-Host "║                                                               ║"
    Write-Host "║  NEXT STEPS:                                                   ║"
    Write-Host "║  1. Restart OpenCode                                            ║"
    Write-Host "║  2. Open a new session — the agent will greet you               ║"
    Write-Host "║  3. Tell $($Map.MAIN_AGENT_NAME) your goals and start building             ║"
    Write-Host "║                                                               ║"
    Write-Host "║  Run this installer again anytime to update or reconfigure.     ║"
    Write-Host "╚═══════════════════════════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "  Log file: $INSTALL_LOG"
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — Orchestrator
# ═══════════════════════════════════════════════════════════════════════════════
function Main {
    $ErrorActionPreference = "Continue"
    $startTime = Get-Date

    try { Clear-Content -Path $INSTALL_LOG -ErrorAction SilentlyContinue } catch {}

    try { Show-Banner } catch { "Phase1 Banner: $_" | Out-File $INSTALL_LOG -Append }
    try { Test-Prerequisites } catch { "Phase1 Prereq: $_" | Out-File $INSTALL_LOG -Append }

    try {
        $script:config = Get-UserConfiguration
    } catch {
        "Phase2 Config: $_" | Out-File $INSTALL_LOG -Append
        throw
    }

    $map = Build-PlaceholderMap -Config $config -InstallPath $config.installPath

    try { Process-Templates -Map $map -InstallPath $config.installPath } catch {
        "Phase3: $_" | Out-File $INSTALL_LOG -Append; Write-Host "  ⚠ Template processing error: $_"
    }

    try { Setup-Directories -InstallPath $config.installPath -SkillsPath $config.skillsPath } catch {
        "Phase4: $_" | Out-File $INSTALL_LOG -Append; Write-Host "  ⚠ Directory setup error: $_"
    }

    try { Copy-ProjectFiles -InstallPath $config.installPath -SkillsPath $config.skillsPath -Map $map } catch {
        "Phase5: $_" | Out-File $INSTALL_LOG -Append; Write-Host "  ⚠ File copy error: $_"
    }

    try { Setup-OllamaModels } catch {
        "Phase6: $_" | Out-File $INSTALL_LOG -Append; Write-Host "  ⚠ Model setup error: $_"
    }

    try { Setup-MCP -InstallMCP $config.installMCP } catch {
        "Phase7: $_" | Out-File $INSTALL_LOG -Append; Write-Host "  ⚠ MCP setup error: $_"
    }

    try { Setup-Git -InitGit $config.initGit -InstallPath $config.installPath -Map $map } catch {
        "Phase8: $_" | Out-File $INSTALL_LOG -Append; Write-Host "  ⚠ Git init error: $_"
    }

    try {
        Test-Installation -InstallPath $config.installPath -SkillsPath $config.skillsPath -InstallMCP $config.installMCP
    } catch { "Phase9: $_" | Out-File $INSTALL_LOG -Append }

    Show-Completion -Map $map -InstallPath $config.installPath

    $elapsed = (Get-Date) - $startTime
    "Install completed in $($elapsed.TotalMinutes.ToString('F1')) minutes" | Out-File $INSTALL_LOG -Append
}

# ── Entry Point ──
Main
