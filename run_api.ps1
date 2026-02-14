# Quick Start API Server Script
# Run this script to start the FastAPI server

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Starting NLP API Server" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
}

# Check if model exists
if (Test-Path "app\models\model.pkl") {
    Write-Host "✓ Model found" -ForegroundColor Green
} else {
    Write-Host "✗ Model not found. Training model first..." -ForegroundColor Red
    python train.py
}

Write-Host "`nStarting server..." -ForegroundColor Yellow
Write-Host "API will be available at:" -ForegroundColor Cyan
Write-Host "  - API: http://localhost:8000" -ForegroundColor White
Write-Host "  - Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
