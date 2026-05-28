# Knowledge Sync — Submit Lessons to Community
# Part of Gaya Agent standard protocol
#
# Usage:
#   .\scripts\knowledge-sync.ps1 -LessonName "stt-pipeline-fix" -UserName "Ron"
#
# This copies a lesson from your user profile to community submissions
# and prepares it for a Pull Request.

param(
    [Parameter(Mandatory=$true)]
    [string]$LessonName,
    
    [Parameter(Mandatory=$true)]
    [string]$UserName,

    [switch]$ListLessons
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$ProfileDir = Join-Path $RepoRoot "knowledge\user_profiles\$UserName"
$LessonFile = Join-Path $ProfileDir "lessons\$LessonName.md"
$SubmissionDir = Join-Path $RepoRoot "knowledge\community\submissions"
$SubmissionFile = Join-Path $SubmissionDir "$LessonName.md"

function List-UserLessons {
    Write-Host "Your lessons:" -ForegroundColor Cyan
    $lessons = Get-ChildItem -Path "$ProfileDir\lessons\*.md" -ErrorAction SilentlyContinue
    if ($lessons.Count -eq 0) {
        Write-Host "  No lessons yet. Create one in $ProfileDir\lessons\" -ForegroundColor Yellow
    } else {
        foreach ($l in $lessons) {
            Write-Host "  - $($l.BaseName)" -ForegroundColor Green
        }
    }
}

if ($ListLessons) {
    List-UserLessons
    exit
}

# Validate
if (-not (Test-Path $LessonFile)) {
    Write-Host "ERROR: Lesson not found: $LessonFile" -ForegroundColor Red
    Write-Host "Available lessons:" -ForegroundColor Yellow
    List-UserLessons
    exit 1
}

if (-not (Test-Path $SubmissionDir)) {
    New-Item -ItemType Directory -Path $SubmissionDir -Force | Out-Null
}

# Copy to submissions
Copy-Item -Path $LessonFile -Destination $SubmissionFile -Force
Write-Host "✅ Lesson copied to community submissions: $SubmissionFile" -ForegroundColor Green

# Update community INDEX.md
$IndexFile = Join-Path $RepoRoot "knowledge\community\INDEX.md"
if (Test-Path $IndexFile) {
    $content = Get-Content $IndexFile -Raw
    $today = Get-Date -Format "dd-MMM-yyyy"
    $entry = "| $LessonName | $UserName | $today | Submitted |"
    
    if ($content -match "(?s)(## Open Submissions.*?)(\n##|\z)") {
        # Insert after the table header
        $newContent = $content -replace "(\| _\(None yet.*?\)_ \|)", "| $LessonName | $UserName | $today | Submitted |`n| _\(None yet — be the first!\)_ |"
        Set-Content -Path $IndexFile -Value $newContent
        Write-Host "✅ Community INDEX.md updated" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "────────────────────────────" -ForegroundColor Cyan
Write-Host "📤 SUBMISSION READY" -ForegroundColor Cyan
Write-Host "────────────────────────────" -ForegroundColor Cyan
Write-Host "Lesson:     $LessonName"
Write-Host "Author:     $UserName"
Write-Host "Location:   $SubmissionFile"
Write-Host ""
Write-Host "Next step:  Open a Pull Request on GitHub"
Write-Host "  git add knowledge/community/"
Write-Host "  git commit -m 'lesson: $LessonName by $UserName'"
Write-Host "  git push origin main"
Write-Host "  → Open PR at https://github.com/ronakraval104-sys/Gaya-Agent"
Write-Host "────────────────────────────" -ForegroundColor Cyan
