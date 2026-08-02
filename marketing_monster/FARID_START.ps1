# FARID_START.ps1 — one command, from anywhere.
#
#   powershell -ExecutionPolicy Bypass -File "<path>\FARID_START.ps1"
#
# Sets everything up and runs `locate`, which finds candidate data files by
# name, size and header row. It reads no records and writes nothing.

param(
    [string]$SearchPath = $HOME,
    [string]$WorkFolder = "$HOME\FARIDOS\marketing"
)

$ErrorActionPreference = "Stop"
$MonsterHome = Split-Path -Parent $MyInvocation.MyCommand.Path

# find a working python
$python = $null
foreach ($candidate in @("python", "py", "python3")) {
    try {
        & $candidate --version *> $null
        if ($LASTEXITCODE -eq 0) { $python = $candidate; break }
    } catch { }
}
if (-not $python) {
    Write-Host "No Python found. Install Python 3.10+ from python.org, then re-run." -ForegroundColor Red
    exit 1
}

$env:PYTHONPATH = $MonsterHome
New-Item -ItemType Directory -Force -Path $WorkFolder | Out-Null
Set-Location $WorkFolder

Write-Host ""
Write-Host "MARKETING MONSTER" -ForegroundColor Yellow
Write-Host "  code:    $MonsterHome"
Write-Host "  ledgers: $WorkFolder"
Write-Host "  python:  $python"
Write-Host ""
Write-Host "Scanning $SearchPath for candidate data files." -ForegroundColor Cyan
Write-Host "Names, sizes and header rows only - no records are read, nothing is written."
Write-Host "This can take a minute on a large home folder."
Write-Host ""

& $python -m monster locate $SearchPath

Write-Host ""
Write-Host "Next, once you can see the export in that list:" -ForegroundColor Yellow
Write-Host "  cd `"$WorkFolder`""
Write-Host "  `$env:PYTHONPATH = `"$MonsterHome`""
Write-Host "  $python -m monster init    pipes"
Write-Host "  $python -m monster inspect pipes `"<path from the list>`""
Write-Host "  $python -m monster load    pipes `"<path>`""
Write-Host "  $python -m monster dig     pipes --save"
Write-Host ""
