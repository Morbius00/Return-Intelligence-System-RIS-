Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "NLP Project Setup (Windows)" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

function Assert-NativeSuccess {
    param(
        [Parameter(Mandatory = $true)][string]$Step
    )
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed (exit code $LASTEXITCODE)"
    }
}

function Get-PythonVersionTuple {
    param(
        [Parameter(Mandatory = $true)][string]$PythonExe
    )
    $versionText = & $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
    Assert-NativeSuccess "Python version check"
    return $versionText.Trim().Split('.') | ForEach-Object { [int]$_ }
}

Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $pythonCmd) {
    Write-Host "Python not found on PATH. Install Python 3.11+ and retry." -ForegroundColor Red
    exit 1
}
$pythonExe = $pythonCmd.Source

$versionTuple = Get-PythonVersionTuple -PythonExe $pythonExe
if (($versionTuple[0] -ne 3) -or ($versionTuple[1] -lt 11)) {
    Write-Host "Python 3.11+ required. Found: $(& $pythonExe --version 2>&1)" -ForegroundColor Red
    exit 1
}
Write-Host ("Python OK: " + (& $pythonExe --version 2>&1)) -ForegroundColor Green

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
$venvDir = Join-Path $PSScriptRoot 'venv'
$venvPython = Join-Path $venvDir 'Scripts\python.exe'
if (Test-Path $venvPython) {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
} else {
    & $pythonExe -m venv $venvDir
    Assert-NativeSuccess "Create venv"
    if (-not (Test-Path $venvPython)) {
        throw "venv creation succeeded but $venvPython not found"
    }
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Upgrade packaging tooling + install deps (prefer wheels on Windows)
Write-Host "`nUpgrading pip/setuptools/wheel..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip setuptools wheel
Assert-NativeSuccess "Upgrade pip tooling"

Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install --prefer-binary -r (Join-Path $PSScriptRoot 'requirements.txt')
Assert-NativeSuccess "Install requirements"
Write-Host "Dependencies installed" -ForegroundColor Green

# Download NLTK resources
Write-Host "`nDownloading NLTK resources..." -ForegroundColor Yellow
& $venvPython -c "import nltk; [nltk.download(r, quiet=True) for r in ['punkt','punkt_tab','stopwords','wordnet','omw-1.4','averaged_perceptron_tagger']]"
Assert-NativeSuccess "Download NLTK resources"
Write-Host "NLTK resources downloaded" -ForegroundColor Green

# Create .env file if template exists
Write-Host "`nSetting up environment file..." -ForegroundColor Yellow
$envFile = Join-Path $PSScriptRoot '.env'
$envExample = Join-Path $PSScriptRoot '.env.example'
if (Test-Path $envFile) {
    Write-Host ".env already exists" -ForegroundColor Green
} elseif (Test-Path $envExample) {
    Copy-Item $envExample $envFile
    Write-Host ".env created from .env.example" -ForegroundColor Green
} else {
    Write-Host "Skipping .env (no .env.example found)" -ForegroundColor Yellow
}

# Train the model
Write-Host "`nTraining the model..." -ForegroundColor Yellow
& $venvPython (Join-Path $PSScriptRoot 'train.py')
Assert-NativeSuccess "Train model"
Write-Host "Model trained successfully" -ForegroundColor Green

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "Setup Complete" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. (Optional) Review .env file and configure if needed"
Write-Host "2. Run the API: .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload"
Write-Host "3. Visit http://localhost:8000/docs for API documentation"
Write-Host ""
