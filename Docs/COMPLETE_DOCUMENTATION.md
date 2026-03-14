# Complete Documentation

## 1. Project Summary

Customer Feedback Intelligence API is a classical NLP and machine learning service for feedback triage and enrichment.

Main outcomes per feedback item:
- Spam detection
- Sentiment classification
- Negative issue categorization + severity scoring
- Positive satisfaction categorization + goodwill scoring

API version in app metadata: 2.0.0

## 2. Functional Scope

### Supported input channels
- Single JSON prediction
- Batch JSON prediction
- File upload prediction (CSV, XLSX)
- Google Sheets processing and writeback
- CLI batch processing (CSV or Sheets)

### Supported outputs
- Structured API JSON response
- Enriched downloadable CSV/XLSX
- Enriched Google Sheets rows

## 3. Pipeline Description

### Stage 1: Spam detection
Rule-based checks filter empty, repetitive, and placeholder text.

### Stage 2: Sentiment detection
Text-first keyword strategy with negation handling.
Rating can break ties:
- rating >= 4 -> Positive
- rating <= 2 -> Negative
- otherwise Neutral

### Stage 3: Category prediction
- Negative sentiment uses negative submodel
- Positive sentiment uses positive submodel

### Stage 4: Business score mapping
- issue_category -> severity_score
- satisfaction_category -> goodwill_score

### Stage 5: Response assembly
Produces consistent API response with nullable category fields when not applicable.

## 4. Endpoints

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

## 5. Request Schemas

### /predict

```json
{
  "customer_feedback": "Excellent product quality and useful in daily life.",
  "rating": 5
}
```

### /predict/batch

```json
{
  "customer_feedbacks": ["Delivery was fast", "Wrong item received"],
  "ratings": [5, 2]
}
```

### /sheets/process

```json
{
  "spreadsheet_id": "YOUR_SPREADSHEET_ID",
  "worksheet_name": "Feedback",
  "feedback_column": "Customer_Feedback",
  "rating_column": "Rating (1-5)"
}
```

### /sheets/update and /sheets/append

```json
{
  "spreadsheet_id": "YOUR_SPREADSHEET_ID",
  "worksheet_name": "Feedback",
  "data": [
    {"customer_feedback": "Product arrived broken", "order_id": "ORD001"}
  ]
}
```

## 6. Response Schema

Representative response:

```json
{
  "is_spam": false,
  "sentiment_type": "Negative",
  "issue_category": "Product Quality Issue",
  "severity_score": 0.9,
  "satisfaction_category": null,
  "goodwill_score": null,
  "confidence": 0.88
}
```

## 7. Category Maps

### Negative categories -> severity
- Product Quality Issue: 0.9
- Expiry Issue: 0.9
- Packaging Issue: 0.6
- Wrong Item: 0.6
- Customer Preference: 0.3
- Other: 0.2
- Uncertain: 0.1

### Positive categories -> goodwill
- Product Appreciation: 0.9
- Overall Positive Experience: 0.85
- Service Satisfaction: 0.8
- Packaging Praise: 0.7
- General Positive: 0.6

## 8. Training and Model Files

Train command:

```powershell
python train.py
```

Artifacts:
- app/models/neg_model.pkl
- app/models/neg_tfidf.pkl
- app/models/pos_model.pkl
- app/models/pos_tfidf.pkl

Training CSV columns:
- customer_feedback
- sentiment
- category

## 9. File Processing Details

/predict/file behavior:
- Accepts CSV or Excel
- Requires Customer_Feedback column
- Optionally uses rating-like column names
- Returns same format with enrichment columns appended

## 10. Batch CLI

CSV mode:

```powershell
python batch_processor.py --mode csv --csv-input training_data/test_input.csv --csv-output analyzed.csv --column Customer_Feedback --rating-column "Rating (1-5)"
```

Sheets mode:

```powershell
python batch_processor.py --mode sheets --spreadsheet-id YOUR_SHEET_ID --worksheet-name Sheet1 --column Customer_Feedback --rating-column "Rating (1-5)"
```

## 11. Deployment

### Docker

```powershell
./build_docker_image.ps1 -ImageName ris-api -Tag latest
docker run --rm -p 8000:8000 ris-api:latest
```

### Render Blueprint

Configured in render.yaml:
- web service using Docker runtime
- autoDeploy enabled
- healthCheckPath: /health

Provision steps in Render:
1. New + -> Blueprint
2. Select this repository
3. Confirm settings and create service

## 12. Troubleshooting

- model_not_loaded on /health:
  Run python train.py and restart API.
- /predict/file startup/runtime multipart errors:
  Ensure python-multipart is installed from requirements.txt.
- Google Sheets unavailable:
  Verify GOOGLE_CREDENTIALS_PATH and spreadsheet sharing permissions.

## 13. Security Notes

- Do not commit credentials JSON files.
- Keep credentials/ and *.json ignored by Git.
- Use environment variables for secrets in production.


