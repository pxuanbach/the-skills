# register-skills.ps1 - Register all skills from this repo to global agents
# Usage: .\register-skills.ps1 [-Target <pi|claude|all>]
# Default: all targets

param(
    [ValidateSet("pi", "claude", "all")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}
$SkillsSource = Join-Path $ScriptDir "skills"

# Target directories
$Targets = @{
    "pi"     = @{
        Path   = Join-Path $env:USERPROFILE ".pi\agent\skills"
        Name   = "Pi Agent"
    }
    "claude" = @{
        Path   = Join-Path $env:USERPROFILE ".claude\skills"
        Name   = "Claude Code"
    }
}

# Filter targets based on parameter
if ($Target -eq "all") {
    $ActiveTargets = @("pi", "claude")
} else {
    $ActiveTargets = @($Target)
}

Write-Host "Registering skills from $SkillsSource" -ForegroundColor Cyan

# Get all skill directories
$skillDirs = Get-ChildItem -Path $SkillsSource -Directory

foreach ($target in $ActiveTargets) {
    $SkillsTarget = $Targets[$target].Path
    $AgentName = $Targets[$target].Name

    Write-Host "`n==> Target: $AgentName ($SkillsTarget)" -ForegroundColor Magenta

    # Verify target exists
    if (-not (Test-Path $SkillsTarget)) {
        Write-Host "  Directory not found, creating..." -ForegroundColor Yellow
        try {
            New-Item -ItemType Directory -Path $SkillsTarget -Force | Out-Null
        } catch {
            Write-Host "  Skipped: Cannot create directory" -ForegroundColor Red
            continue
        }
    }

    foreach ($skillDir in $skillDirs) {
        $skillName = $skillDir.Name
        $skillMdPath = Join-Path $skillDir.FullName "SKILL.md"
        $targetPath = Join-Path $SkillsTarget $skillName

        if (Test-Path $skillMdPath) {
            if (Test-Path $targetPath) {
                $item = Get-Item $targetPath -ErrorAction SilentlyContinue
                if ($item.LinkType -eq "SymbolicLink") {
                    # Use cmd rd for reliable symlink removal in NonInteractive mode
                    cmd /c "rd /s /q `"$targetPath`"" 2>$null
                    Write-Host "  Updated: $skillName (symlink)" -ForegroundColor Yellow
                } else {
                    Write-Host "  Skipped: $skillName (directory already exists)" -ForegroundColor Yellow
                    continue
                }
            }

            # Create symlink using cmd mklink (more reliable on Windows)
            $sourceAbsolute = $skillDir.FullName
            cmd /c "mklink /D `"$targetPath`" `"$sourceAbsolute`"" | Out-Null

            if ($LASTEXITCODE -eq 0) {
                Write-Host "  Registered: $skillName" -ForegroundColor Green
            } else {
                Write-Host "  Failed: $skillName" -ForegroundColor Red
            }
        } else {
            Write-Host "  Skipped: $skillName (no SKILL.md found)" -ForegroundColor Yellow
        }
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan
