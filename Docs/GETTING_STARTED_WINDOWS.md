# Getting Started on Windows

## Prerequisites

- Windows 10 or 11
- Python 3.11+
- PowerShell
- Optional: Docker Desktop

## 1) Environment Setup

```powershell
cd "d:\My Projects\NLP-Project"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 2) Train Models

```powershell
python train.py
```

Expected files:
- app/models/neg_model.pkl
- app/models/neg_tfidf.pkl
- app/models/pos_model.pkl
- app/models/pos_tfidf.pkl

## 3) Run API

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
- http://localhost:8000/docs

## 4) Test API Quickly

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -ContentType "application/json" -Body '{"customer_feedback":"Product arrived broken","rating":1}'
```

## 5) Optional Docker Run

```powershell
./build_docker_image.ps1 -ImageName ris-api -Tag latest
docker run --rm -p 8000:8000 ris-api:latest
```

## Common Problems

- model_not_loaded in /health:
  Run python train.py, then restart server.
- Google Sheets not configured:
  Set GOOGLE_CREDENTIALS_PATH in .env and restart API.
- Upload endpoint failure with multipart:
  Reinstall dependencies from requirements.txt.


