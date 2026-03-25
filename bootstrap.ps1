$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

function Ensure-Chocolatey {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        throw "Chocolatey is not installed. Install it first, then rerun this script."
    }
}

function Ensure-Git {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        return
    }

    Ensure-Chocolatey
    choco install git -y
}

function Initialize-Repo {
    if (-not (Test-Path ".git")) {
        git init
    }

    git branch -M main
    git config user.name "Codex Agent"
    git config user.email "codex@example.com"
}

function Commit-InitialFiles {
    git add .

    $status = git status --porcelain
    if (-not $status) {
        Write-Host "No changes to commit."
        return
    }

    git commit -m "Initial Tavily quota monitor"
}

function Create-GitHubRepo {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Repository
    )

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI (gh) is not installed. Install it or create the repo manually on GitHub."
    }

    gh auth status | Out-Null
    gh repo create $Repository --public --source . --remote origin --push
}

Ensure-Git
Initialize-Repo
Commit-InitialFiles

Write-Host ""
Write-Host "Local repo is ready."
Write-Host ""
Write-Host "To create and push a GitHub repo after installing gh:"
Write-Host '  gh repo create your-name/tavily-quota-monitor --public --source . --remote origin --push'
Write-Host ""
Write-Host "If you already created the GitHub repo in the browser, run:"
Write-Host '  git remote add origin https://github.com/<your-user>/<your-repo>.git'
Write-Host '  git push -u origin main'
