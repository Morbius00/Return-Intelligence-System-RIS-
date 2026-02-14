# Run the Server + Use the API (Simple Guide)

This project exposes a small FastAPI server that classifies a customer “return reason” text.

## 1) Start the server

### Option A (easiest): use the script

```powershell
cd "D:\My Projects\NLP-Project"
.\run_api.ps1
```

### Option B: run Uvicorn directly (no activation needed)

```powershell
cd "D:\My Projects\NLP-Project"
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Option C: activate the venv, then run

```powershell
cd "D:\My Projects\NLP-Project"
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

When it’s running, open:
- Docs (Swagger UI): http://127.0.0.1:8000/docs
- API root: http://127.0.0.1:8000/

Stop the server with Ctrl+C in the terminal.

## 2) What the endpoints do

Base URL: `http://127.0.0.1:8000`

### GET / (root)

What it does: quick “is the server up?” info.

Example response:
```json
{
  "message": "NLP Return Reason Classifier API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### GET /health

What it does: tells you if the ML model is loaded.

Example response (model loaded):
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

Example response (model missing/not loaded):
```json
{
  "status": "model_not_loaded",
  "model_loaded": false,
  "version": "1.0.0"
}
```

### GET /categories

What it does: returns the list of categories and the severity score mapping.

Example response:
```json
{
  "categories": [
    "Product Quality Issue",
    "Expiry Issue",
    "Packaging Issue",
    "Wrong Item",
    "Customer Preference",
    "Other"
  ],
  "severity_mapping": {
    "Product Quality Issue": 0.9,
    "Expiry Issue": 0.9,
    "Packaging Issue": 0.6,
    "Wrong Item": 0.6,
    "Customer Preference": 0.3,
    "Other": 0.2
  }
}
```

### POST /predict

What it does: classifies one return reason.

Request body:
```json
{
  "return_reason": "item arrived broken"
}
```

Example response:
```json
{
  "is_spam": false,
  "reason_category": "Product Quality Issue",
  "severity_score": 0.9,
  "confidence": 0.85
}
```

Notes:
- `is_spam` is a rule-based flag for meaningless inputs.
- `confidence` may be `null` depending on the model implementation.

### POST /predict/batch

What it does: classifies multiple return reasons in one request.

Request body:
```json
{
  "return_reasons": [
    "item arrived broken",
    "wrong product sent",
    "no reason"
  ]
}
```

Example response:
```json
{
  "predictions": [
    {
      "is_spam": false,
      "reason_category": "Product Quality Issue",
      "severity_score": 0.9,
      "confidence": 0.85
    },
    {
      "is_spam": false,
      "reason_category": "Wrong Item",
      "severity_score": 0.6,
      "confidence": 0.78
    },
    {
      "is_spam": true,
      "reason_category": "Other",
      "severity_score": 0.0,
      "confidence": null
    }
  ],
  "total": 3
}
```

### POST /preprocess

What it does: shows how the text is cleaned/tokenized internally (debug endpoint).

Call it with a query parameter:
```text
POST /preprocess?text=Item%20was%20BROKEN!!!
```

Example response:
```json
{
  "original": "Item was BROKEN!!!",
  "preprocessed": "item broken",
  "is_spam": false
}
```

## 3) Try endpoints from PowerShell

### Health check

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET
```

### Single prediction

```powershell
$body = @{ return_reason = "item arrived broken" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method POST -ContentType "application/json" -Body $body
```

### Batch prediction

```powershell
$body = @{ return_reasons = @("item arrived broken", "wrong product sent", "no reason") } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict/batch" -Method POST -ContentType "application/json" -Body $body
```

## 4) Common errors (and what they mean)

### 503: “Model not loaded. Please train the model first.”

Meaning: the model files are missing in `app/models/`.

Fix:
```powershell
.\venv\Scripts\python.exe train.py
```

Then restart the server.

### Port already in use

Fix (use a different port):
```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```
