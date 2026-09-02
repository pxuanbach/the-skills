# register-skills.ps1 - Register all skills from this repo to global agents
# Usage: .\register-skills.ps1 [-Target <pi|claude|antigravity|codex|opencode|all>]
# Default: all targets

param(
    [ValidateSet("pi", "claude", "antigravity", "codex", "opencode", "all")]
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
$OpenCodeSkillsPath = if ($env:XDG_CONFIG_HOME) {
    Join-Path $env:XDG_CONFIG_HOME "opencode\skills"
} else {
    Join-Path $env:USERPROFILE ".config\opencode\skills"
}

$Targets = [ordered]@{
    "pi"          = @{ Name = "Pi Agent"; Path = Join-Path $env:USERPROFILE ".pi\agent\skills" }
    "claude"      = @{ Name = "Claude Code"; Path = Join-Path $env:USERPROFILE ".claude\skills" }
    "antigravity" = @{ Name = "Antigravity / Gemini CLI"; Path = Join-Path $env:USERPROFILE ".gemini\config\skills" }
    "codex"       = @{ Name = "OpenAI Codex CLI"; Path = Join-Path $env:USERPROFILE ".codex\skills" }
    "opencode"    = @{ Name = "OpenCode"; Path = $OpenCodeSkillsPath }
}

# Filter targets based on parameter
if ($Target -eq "all") {
    $ActiveTargets = $Targets.Keys
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
