# register-skills.ps1 - Register all skills from this repo to the global pi agent
# Usage: .\register-skills.ps1

$ErrorActionPreference = "Stop"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}
$SkillsSource = Join-Path $ScriptDir "skills"

# Target directory in pi agent
$SkillsTarget = Join-Path $env:USERPROFILE ".pi\agent\skills"

# Verify source exists
if (-not (Test-Path $SkillsSource)) {
    Write-Error "Skills directory not found at $SkillsSource"
    exit 1
}

# Verify target exists
if (-not (Test-Path $SkillsTarget)) {
    Write-Error "Pi agent skills directory not found at $SkillsTarget"
    Write-Error "Please ensure pi agent is installed"
    exit 1
}

Write-Host "Registering skills from $SkillsSource to $SkillsTarget" -ForegroundColor Cyan

# Get all skill directories
$skillDirs = Get-ChildItem -Path $SkillsSource -Directory

foreach ($skillDir in $skillDirs) {
    $skillName = $skillDir.Name
    $skillMdPath = Join-Path $skillDir.FullName "SKILL.md"
    $targetPath = Join-Path $SkillsTarget $skillName

    if (Test-Path $skillMdPath) {
        if (Test-Path $targetPath) {
            if ((Get-Item $targetPath).LinkType -eq "SymbolicLink") {
                Remove-Item $targetPath -Force
                Write-Host "  Updated: $skillName (symlink)" -ForegroundColor Yellow
            } else {
                Write-Host "  Skipped: $skillName (directory already exists)" -ForegroundColor Yellow
                continue
            }
        }

        # Create symlink using cmd mklink (more reliable on Windows)
        $sourceAbsolute = $skillDir.FullName
        cmd /c "mklink /D `"$targetPath`" `"$sourceAbsolute`"*" | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Registered: $skillName" -ForegroundColor Green
        } else {
            Write-Host "  Failed: $skillName" -ForegroundColor Red
        }
    } else {
        Write-Host "  Skipped: $skillName (no SKILL.md found)" -ForegroundColor Yellow
    }
}

Write-Host "Done!" -ForegroundColor Cyan
