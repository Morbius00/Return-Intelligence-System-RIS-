# Quick Setup and Operations

## 5-Minute Setup

```powershell
cd "d:\My Projects\NLP-Project"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python train.py
python -m uvicorn app.main:app --reload
```

Open Swagger UI:
- http://localhost:8000/docs

## Day-to-Day Commands

### Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Retrain models

```powershell
python train.py
```

### Start API

```powershell
python -m uvicorn app.main:app --reload
```

### Health check

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"
```

### Single prediction

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -ContentType "application/json" -Body '{"customer_feedback":"Delivery was excellent","rating":5}'
```

## Model Artifacts Checklist

After training, verify:
- app/models/neg_model.pkl
- app/models/neg_tfidf.pkl
- app/models/pos_model.pkl
- app/models/pos_tfidf.pkl

## CSV Batch Workflow

```powershell
python batch_processor.py --mode csv --csv-input training_data/test_input.csv --csv-output analyzed_output.csv --column Customer_Feedback --rating-column "Rating (1-5)"
```

## Google Sheets Workflow

```powershell
python batch_processor.py --mode sheets --spreadsheet-id YOUR_SHEET_ID --worksheet-name Sheet1 --column Customer_Feedback --rating-column "Rating (1-5)"
```

## Docker Workflow

```powershell
./build_docker_image.ps1 -ImageName ris-api -Tag latest
docker run --rm -p 8000:8000 ris-api:latest
```

## Common Issues

- model_not_loaded on /health:
  Run python train.py and restart API.
- Google Sheets unavailable:
  Set GOOGLE_CREDENTIALS_PATH and restart API.
- Upload endpoint errors for multipart:
  Ensure python-multipart is installed from requirements.txt.


