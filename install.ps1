# install.ps1 - Interactive remote skill installer for coding agents
# Usage:
#   irm https://raw.githubusercontent.com/pxuanbach/the-skills/main/install.ps1 | iex
# Or:
#   .\install.ps1 [-Targets <pi,claude,antigravity,all>] [-Skills <wiki-manager,constructor,all>]

param(
    [string[]]$Targets,
    [string[]]$Skills
)

$ErrorActionPreference = "Stop"
$RepoOwner = "pxuanbach"
$RepoName = "the-skills"
$Branch = "main"

# Predefined fallback list if GitHub API is unavailable
$FallbackSkills = @(
    "constructor",
    "quality-reviewer",
    "requirement-analyzer",
    "research-workflow",
    "review-skill",
    "screenshot",
    "security-reviewer",
    "user-designer",
    "wiki-manager"
)

# Target Agent definitions
$AgentTargets = [ordered]@{
    "pi"          = @{ Name = "Pi Agent"; Path = Join-Path $env:USERPROFILE ".pi\agent\skills" }
    "claude"      = @{ Name = "Claude Code"; Path = Join-Path $env:USERPROFILE ".claude\skills" }
    "antigravity" = @{ Name = "Antigravity / Gemini CLI"; Path = Join-Path $env:USERPROFILE ".gemini\config\skills" }
}

function Show-Header {
    Clear-Host
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "         AI Agent Skills Installer ($RepoName)            " -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host ""
}

# Fetch remote skill list from GitHub
function Get-RemoteSkills {
    Write-Host "Fetching available skills from GitHub..." -ForegroundColor Gray
    $apiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/contents/skills"
    try {
        $headers = @{ "User-Agent" = "PowerShell-Installer" }
        $response = Invoke-RestMethod -Uri $apiUrl -Headers $headers -TimeoutSec 10 -ErrorAction Stop
        $skills = $response | Where-Object { $_.type -eq "dir" } | Select-Object -ExpandProperty name
        if ($skills -and $skills.Count -gt 0) {
            return $skills
        }
    } catch {
        Write-Host "Notice: Using local fallback skill list." -ForegroundColor DarkGray
    }
    return $FallbackSkills
}

# Interactive Checkbox Menu
function Show-CheckboxMenu {
    param(
        [string]$Title,
        [string[]]$Items,
        [string[]]$Descriptions = @()
    )

    $selected = [bool[]]::new($Items.Count)
    $cursor = 0
    $isDone = $false

    # Check if interactive console input is available
    $canReadRaw = $false
    try {
        if ([System.Console]::IsInputRedirected -eq $false -and $Host.UI.RawUI) {
            $canReadRaw = $true
        }
    } catch {
        $canReadRaw = $false
    }

    if (-not $canReadRaw) {
        # Fallback to simple line-based selection for non-interactive / redirected pipelines
        Write-Host "`n$Title" -ForegroundColor Yellow
        for ($i = 0; $i -lt $Items.Count; $i++) {
            $desc = if ($i -lt $Descriptions.Count -and $Descriptions[$i]) { " (" + $Descriptions[$i] + ")" } else { "" }
            Write-Host "  [$($i + 1)] $($Items[$i])$desc"
        }
        Write-Host "  [A] Select All"
        Write-Host ""
        $inputVal = Read-Host "Enter numbers separated by commas (e.g. 1,3) or 'A' for all [default: A]"
        if ([string]::IsNullOrWhiteSpace($inputVal) -or $inputVal.Trim().ToUpper() -eq "A") {
            return $Items
        }
        $chosen = @()
        foreach ($part in ($inputVal -split ",")) {
            $num = 0
            if ([int]::TryParse($part.Trim(), [ref]$num) -and $num -ge 1 -and $num -le $Items.Count) {
                $chosen += $Items[$num - 1]
            }
        }
        return $chosen
    }

    # Hide cursor
    [Console]::CursorVisible = $false

    try {
        while (-not $isDone) {
            Show-Header
            Write-Host "$Title" -ForegroundColor Yellow
            Write-Host "Use [Up/Down] arrows, [Space] to toggle, [A] to toggle all, [Enter] to confirm`n" -ForegroundColor DarkGray

            for ($i = 0; $i -lt $Items.Count; $i++) {
                $check = if ($selected[$i]) { "[x]" } else { "[ ]" }
                $pointer = if ($i -eq $cursor) { ">" } else { " " }
                $desc = if ($i -lt $Descriptions.Count -and $Descriptions[$i]) { " - " + $Descriptions[$i] } else { "" }

                if ($i -eq $cursor) {
                    Write-Host "$pointer $check $($Items[$i])$desc" -ForegroundColor Green
                } else {
                    if ($selected[$i]) {
                        Write-Host "$pointer $check $($Items[$i])$desc" -ForegroundColor White
                    } else {
                        Write-Host "$pointer $check $($Items[$i])$desc" -ForegroundColor Gray
                    }
                }
            }

            $key = [Console]::ReadKey($true)
            switch ($key.Key) {
                ([ConsoleKey]::UpArrow) {
                    if ($cursor -gt 0) { $cursor-- } else { $cursor = $Items.Count - 1 }
                }
                ([ConsoleKey]::DownArrow) {
                    if ($cursor -lt ($Items.Count - 1)) { $cursor++ } else { $cursor = 0 }
                }
                ([ConsoleKey]::Spacebar) {
                    $selected[$cursor] = -not $selected[$cursor]
                }
                ([ConsoleKey]::A) {
                    $allSelected = ($selected -notcontains $false)
                    for ($i = 0; $i -lt $selected.Count; $i++) {
                        $selected[$i] = -not $allSelected
                    }
                }
                ([ConsoleKey]::Enter) {
                    $isDone = $true
                }
            }
        }
    } finally {
        [Console]::CursorVisible = $true
    }

    $result = @()
    for ($i = 0; $i -lt $Items.Count; $i++) {
        if ($selected[$i]) {
            $result += $Items[$i]
        }
    }
    return $result
}

# Fetch directory tree recursively for selected skills
function Download-Skill {
    param(
        [string]$SkillName,
        [string]$DestinationDir
    )

    $targetSkillPath = Join-Path $DestinationDir $SkillName
    if (-not (Test-Path $targetSkillPath)) {
        New-Item -ItemType Directory -Path $targetSkillPath -Force | Out-Null
    }

    Write-Host "  -> Installing '$SkillName'..." -ForegroundColor Cyan

    # Fetch tree of repository to find all files inside skills/<SkillName>
    $treeUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/git/trees/$Branch`?recursive=1"
    $headers = @{ "User-Agent" = "PowerShell-Installer" }
    
    $filePaths = @()
    try {
        $treeResponse = Invoke-RestMethod -Uri $treeUrl -Headers $headers -TimeoutSec 15 -ErrorAction Stop
        $prefix = "skills/$SkillName/"
        $filePaths = $treeResponse.tree | Where-Object { $_.path -like "$prefix*" -and $_.type -eq "blob" } | Select-Object -ExpandProperty path
    } catch {
        # Fallback to standard known files
        $filePaths = @("skills/$SkillName/SKILL.md")
    }

    if ($filePaths.Count -eq 0) {
        $filePaths = @("skills/$SkillName/SKILL.md")
    }

    foreach ($rawPath in $filePaths) {
        $relativeSubPath = $rawPath.Substring("skills/$SkillName/".Length)
        $destFile = Join-Path $targetSkillPath $relativeSubPath
        $destParent = Split-Path -Parent $destFile
        if (-not (Test-Path $destParent)) {
            New-Item -ItemType Directory -Path $destParent -Force | Out-Null
        }

        $rawUrl = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/$Branch/$rawPath"
        try {
            Invoke-WebRequest -Uri $rawUrl -OutFile $destFile -TimeoutSec 15 -UseBasicParsing | Out-Null
        } catch {
            Write-Host "    Warning: Failed to fetch $rawPath" -ForegroundColor Yellow
        }
    }

    Write-Host "    [OK] Installed $SkillName ($($filePaths.Count) file(s))" -ForegroundColor Green
}

# Main Execution Flow
Show-Header

# 1. Determine Target Agents
$selectedTargetKeys = @()
if ($Targets) {
    if ($Targets -contains "all") {
        $selectedTargetKeys = $AgentTargets.Keys
    } else {
        foreach ($t in $Targets) {
            $key = $t.ToLower().Trim()
            if ($AgentTargets.Contains($key)) {
                $selectedTargetKeys += $key
            }
        }
    }
}

if ($selectedTargetKeys.Count -eq 0) {
    $targetNames = @()
    $targetDescs = @()
    foreach ($k in $AgentTargets.Keys) {
        $targetNames += $AgentTargets[$k].Name
        $targetDescs += $AgentTargets[$k].Path
    }

    $chosenNames = Show-CheckboxMenu -Title "1. Select Coding Agent(s) to install skills to:" -Items $targetNames -Descriptions $targetDescs
    if ($chosenNames.Count -eq 0) {
        Write-Host "No agent selected. Exiting." -ForegroundColor Yellow
        exit 0
    }

    foreach ($k in $AgentTargets.Keys) {
        if ($chosenNames -contains $AgentTargets[$k].Name) {
            $selectedTargetKeys += $k
        }
    }
}

# 2. Determine Skills
$availableSkills = Get-RemoteSkills
$selectedSkills = @()

if ($Skills) {
    if ($Skills -contains "all") {
        $selectedSkills = $availableSkills
    } else {
        foreach ($s in $Skills) {
            $matched = $availableSkills | Where-Object { $_ -eq $s.Trim() }
            if ($matched) {
                $selectedSkills += $matched
            }
        }
    }
}

if ($selectedSkills.Count -eq 0) {
    $selectedSkills = Show-CheckboxMenu -Title "2. Select Skill(s) to download and install:" -Items $availableSkills
    if ($selectedSkills.Count -eq 0) {
        Write-Host "No skills selected. Exiting." -ForegroundColor Yellow
        exit 0
    }
}

# 3. Perform Download & Installation
Show-Header
Write-Host "Starting Installation..." -ForegroundColor Yellow
Write-Host "Selected Skills: $($selectedSkills -join ', ')" -ForegroundColor Gray
Write-Host ""

foreach ($targetKey in $selectedTargetKeys) {
    $agentInfo = $AgentTargets[$targetKey]
    Write-Host "==> Target: $($agentInfo.Name) ($($agentInfo.Path))" -ForegroundColor Magenta

    if (-not (Test-Path $agentInfo.Path)) {
        New-Item -ItemType Directory -Path $agentInfo.Path -Force | Out-Null
    }

    foreach ($skill in $selectedSkills) {
        Download-Skill -SkillName $skill -DestinationDir $agentInfo.Path
    }
    Write-Host ""
}

Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "Restart or refresh your coding agent to load the new skills.`n" -ForegroundColor Cyan
