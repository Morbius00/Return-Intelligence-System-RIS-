# Customer Feedback Intelligence API

Production-ready NLP system for classifying customer feedback using classical machine learning.

It follows a dual-path pipeline:
- Negative sentiment -> issue category + severity score
- Positive sentiment -> satisfaction category + goodwill score

The service also includes spam detection, file-based batch analysis, and Google Sheets integration.

## Overview

Core stack:
- FastAPI
- NLTK preprocessing
- TF-IDF + Logistic Regression
- pandas for batch/file processing
- gspread for Google Sheets

API version: 2.0.0

## Current Pipeline

For each input:
1. Spam detection (rule-based)
2. Sentiment detection (text-first, rating used as tiebreaker)
3. If Negative: predict issue category, map to severity score
4. If Positive: predict satisfaction category, map to goodwill score
5. If Neutral: categories and scores remain null

### Negative categories (severity)
- Product Quality Issue: 0.9
- Expiry Issue: 0.9
- Packaging Issue: 0.6
- Wrong Item: 0.6
- Customer Preference: 0.3
- Other: 0.2
- Uncertain: 0.1

### Positive categories (goodwill)
- Product Appreciation: 0.9
- Overall Positive Experience: 0.85
- Service Satisfaction: 0.8
- Packaging Praise: 0.7
- General Positive: 0.6

## Project Structure

```text
NLP-Project/
  app/
    main.py
    models/
      neg_model.pkl
      neg_tfidf.pkl
      pos_model.pkl
      pos_tfidf.pkl
    nlp/
      classifier.py
      preprocess.py
      spam_detector.py
    services/
      sheets_service.py
  training_data/
    feedback_training_data.csv
  batch_processor.py
  train.py
  start_server.py
  Dockerfile
  render.yaml
```

## Setup

### Prerequisites
- Python 3.11+
- pip
- Optional: Docker Desktop

### Install

```powershell
cd "d:\My Projects\NLP-Project"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Train Models

```powershell
python train.py
```

Expected generated artifacts:
- app/models/neg_model.pkl
- app/models/neg_tfidf.pkl
- app/models/pos_model.pkl
- app/models/pos_tfidf.pkl

### Run API

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```powershell
python start_server.py
```

Available URLs:
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- GET /
- GET /health
- GET /categories
- POST /predict
- POST /predict/batch
- POST /predict/file
- POST /preprocess
- POST /sheets/process
- POST /sheets/update
- POST /sheets/append

## Request and Response Examples

### Health

```http
GET /health
```

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "2.0.0"
}
```

### Single Prediction

```http
POST /predict
Content-Type: application/json
```

```json
{
  "customer_feedback": "Excellent product quality and very useful in daily life.",
  "rating": 5
}
```

```json
{
  "is_spam": false,
  "sentiment_type": "Positive",
  "issue_category": null,
  "severity_score": null,
  "satisfaction_category": "Product Appreciation",
  "goodwill_score": 0.9,
  "confidence": 0.87
}
```

### Batch Prediction

```http
POST /predict/batch
Content-Type: application/json
```

```json
{
  "customer_feedbacks": [
    "Product arrived completely broken.",
    "Delivery was fast and excellent.",
    "no reason"
  ],
  "ratings": [1, 5, null]
}
```

### Categories

```http
GET /categories
```

Response includes:
- negative_categories
- positive_categories
- severity_mapping
- goodwill_mapping

### File Prediction

Upload CSV or Excel to /predict/file.

Required column:
- Customer_Feedback (case-insensitive match)

Optional rating column:
- any column name containing rating (for example Rating (1-5))

Returned file includes these columns:
- 1. Sentiment
- 2. Issue_Category
- 3. Severity_Score
- 4. Satisfaction_Category
- 5. Goodwill_Score
- 6. Confidence
- 7. Spam

## Batch Processor CLI

CSV mode:

```powershell
python batch_processor.py --mode csv --csv-input training_data/test_input.csv --csv-output analyzed.csv --column Customer_Feedback --rating-column "Rating (1-5)"
```

Google Sheets mode:

```powershell
python batch_processor.py --mode sheets --spreadsheet-id YOUR_SHEET_ID --worksheet-name Sheet1 --column Customer_Feedback --rating-column "Rating (1-5)"
```

## Google Sheets

Set credentials path in .env:

```env
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
```

Then use:
- POST /sheets/process to enrich existing rows
- POST /sheets/update to write/replace processed rows
- POST /sheets/append to append processed rows

## Docker

Build image using helper script:

```powershell
./build_docker_image.ps1 -ImageName ris-api -Tag latest
```

Or directly:

```powershell
docker build -t ris-api:latest .
```

Run container:

```powershell
docker run --rm -p 8000:8000 ris-api:latest
```

## Render Auto Deploy

Repository contains a Render Blueprint file: render.yaml.

Current blueprint:
- Web service name: ris-api
- Environment: docker
- Auto deploy: true
- Health check: /health

Setup:
1. Push branch to GitHub.
2. In Render select New + -> Blueprint.
3. Select this repository.
4. Confirm service settings and create.
5. Configure environment variables and secrets in Render.

## Notes

- On startup, the API auto-trains model artefacts from training_data/feedback_training_data.csv if model files are missing.
- Google Sheets features are optional and require valid service account credentials.
- File upload endpoints require python-multipart (already included in requirements.txt).


