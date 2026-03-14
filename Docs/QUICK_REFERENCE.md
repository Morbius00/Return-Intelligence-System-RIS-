# Quick Reference

## Setup

```powershell
cd "d:\My Projects\NLP-Project"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python train.py
```

## Run API

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Core Endpoints

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/categories
```

```powershell
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"customer_feedback":"Product arrived broken","rating":1}'
```

```powershell
curl -X POST http://localhost:8000/predict/batch -H "Content-Type: application/json" -d '{"customer_feedbacks":["Excellent delivery","Wrong item received"],"ratings":[5,2]}'
```

## File Batch Endpoint

- POST /predict/file
- Input: CSV or Excel
- Required column: Customer_Feedback
- Optional rating column: any header containing rating

## Batch CLI

```powershell
python batch_processor.py --mode csv --csv-input training_data/test_input.csv --csv-output analyzed.csv --column Customer_Feedback --rating-column "Rating (1-5)"
```

```powershell
python batch_processor.py --mode sheets --spreadsheet-id YOUR_ID --worksheet-name Sheet1 --column Customer_Feedback --rating-column "Rating (1-5)"
```

## Docker

```powershell
./build_docker_image.ps1 -ImageName ris-api -Tag latest
docker run --rm -p 8000:8000 ris-api:latest
```

## Render

- Blueprint file: render.yaml
- Deploy path: Render -> New + -> Blueprint -> select repo


