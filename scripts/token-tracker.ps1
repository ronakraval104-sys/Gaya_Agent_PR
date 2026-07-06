# Token Tracker — Session Efficacy Meter
# Part of Gaya Agent standard protocol
# Usage: dot-source into session, call Add-TokenLog after each action
#
# . .\scripts\token-tracker.ps1
# Add-TokenLog -InputText "user message" -OutputText "gaya response" -ToolCalls @("read","write") -FilesTouched @("file1.md")

$script:TokenSession = @{
    ActionNumber    = 0
    TotalInput      = 0
    TotalOutput     = 0
    TotalToolCalls  = 0
    TotalFiles      = 0
    ToolBreakdown   = @{}
    StartTime       = Get-Date
    History         = @()
}

function Estimate-Tokens {
    param([string]$Text)
    if ([string]::IsNullOrEmpty($Text)) { return 0 }
    return [math]::Max(1, [int]($Text.Length / 4))
}

function Add-TokenLog {
    param(
        [string]$InputText,
        [string]$OutputText,
        [string[]]$ToolCalls,
        [string[]]$FilesTouched,
        [int]$ExactInputTokens = -1,
        [int]$ExactOutputTokens = -1
    )

    $script:TokenSession.ActionNumber++
    
    $inTok = if ($ExactInputTokens -ge 0) { $ExactInputTokens } else { Estimate-Tokens $InputText }
    $outTok = if ($ExactOutputTokens -ge 0) { $ExactOutputTokens } else { Estimate-Tokens $OutputText }
    
    $script:TokenSession.TotalInput += $inTok
    $script:TokenSession.TotalOutput += $outTok
    $script:TokenSession.TotalToolCalls += $ToolCalls.Count
    $script:TokenSession.TotalFiles += $FilesTouched.Count
    
    foreach ($tool in $ToolCalls) {
        if (-not $script:TokenSession.ToolBreakdown.ContainsKey($tool)) {
            $script:TokenSession.ToolBreakdown[$tool] = 0
        }
        $script:TokenSession.ToolBreakdown[$tool]++
    }

    $entry = @{
        Action = $script:TokenSession.ActionNumber
        InputTokens = $inTok
        OutputTokens = $outTok
        Tools = $ToolCalls
        Files = $FilesTouched
        Timestamp = Get-Date -Format "HH:mm:ss"
    }
    $script:TokenSession.History += $entry

    $runningTotal = $script:TokenSession.TotalInput + $script:TokenSession.TotalOutput

    # Build tool breakdown string
    $toolStr = if ($ToolCalls.Count -gt 0) { 
        $grouped = $ToolCalls | Group-Object | ForEach-Object { "$($_.Count) $($_.Name)" }
        "$($ToolCalls.Count) calls ($($grouped -join ', '))"
    } else { "0" }

    Write-Host ""
    Write-Host "────────────────────────────" -ForegroundColor Cyan
    Write-Host "⚡ TOKEN LOG — Action #$($script:TokenSession.ActionNumber)" -ForegroundColor Cyan
    Write-Host "────────────────────────────" -ForegroundColor Cyan
    Write-Host "  Input:`t`t~$inTok tok"
    Write-Host "  Output:`t`t~$outTok tok"
    Write-Host "  Tools:`t`t$toolStr"
    Write-Host "  Files:`t`t$($FilesTouched.Count)"
    if ($FilesTouched.Count -gt 0) {
        foreach ($f in $FilesTouched) { Write-Host "`t`t`t  $f" }
    }
    Write-Host "  ─────────────────────────"
    Write-Host "  Session total:`t~$runningTotal tok" -ForegroundColor Yellow
    Write-Host "────────────────────────────" -ForegroundColor Cyan
    Write-Host ""

    return @{
        InputTokens = $inTok
        OutputTokens = $outTok
        RunningTotal = $runningTotal
    }
}

function Get-TokenSummary {
    $runningTotal = $script:TokenSession.TotalInput + $script:TokenSession.TotalOutput
    $elapsed = (Get-Date) - $script:TokenSession.StartTime

    Write-Host ""
    Write-Host "────────────────────────────" -ForegroundColor Green
    Write-Host "⚡ SESSION TOKEN SUMMARY" -ForegroundColor Green
    Write-Host "────────────────────────────" -ForegroundColor Green
    Write-Host "  Total exchanges:`t$($script:TokenSession.ActionNumber)"
    Write-Host "  Total input:`t`t~$($script:TokenSession.TotalInput) tok"
    Write-Host "  Total output:`t`t~$($script:TokenSession.TotalOutput) tok"
    Write-Host "  Total tool calls:`t$($script:TokenSession.TotalToolCalls)"
    Write-Host "  Total estimated:`t~$runningTotal tok"
    Write-Host "  Duration:`t`t$($elapsed.Hours)h $($elapsed.Minutes)m $($elapsed.Seconds)s"
    
    if ($script:TokenSession.TotalToolCalls -gt 0) {
        Write-Host ""
        Write-Host "  Tool breakdown:"
        foreach ($kv in $script:TokenSession.ToolBreakdown.GetEnumerator() | Sort-Object Value -Descending) {
            Write-Host "    $($kv.Key): $($kv.Value) calls"
        }
    }
    Write-Host "────────────────────────────" -ForegroundColor Green
    Write-Host ""
}

function Reset-TokenTracker {
    $script:TokenSession = @{
        ActionNumber    = 0
        TotalInput      = 0
        TotalOutput     = 0
        TotalToolCalls  = 0
        TotalFiles      = 0
        ToolBreakdown   = @{}
        StartTime       = Get-Date
        History         = @()
    }
    Write-Host "Token tracker reset." -ForegroundColor Yellow
}

Export-ModuleMember -Function Add-TokenLog, Get-TokenSummary, Reset-TokenTracker
