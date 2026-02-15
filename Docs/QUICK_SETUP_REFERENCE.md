# Quick Setup & Operations Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Environment (2 minutes)
```powershell
# Navigate to project
cd "d:\My Projects\NLP-Project"

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Train Model (2 minutes)
```powershell
python train.py
```

### Step 3: Start Server (1 minute)
```powershell
python -m uvicorn app.main:app --reload
```

### Step 4: Test
Open browser: http://localhost:8000/docs

---

## 📋 Essential Commands

### Virtual Environment

```powershell
# Create
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (Linux/Mac)
source .venv/bin/activate

# Deactivate
deactivate

# Verify activation (should see .venv in prompt)
# (.venv) PS D:\My Projects\NLP-Project>
```

### Package Management

```powershell
# Install all dependencies
pip install -r requirements.txt

# Install single package
pip install <package-name>

# List installed packages
pip list

# Check specific packages
pip list | Select-String "fastapi|nltk|sklearn"

# Upgrade pip
python -m pip install --upgrade pip

# Uninstall package
pip uninstall <package-name>
```

### Model Training

```powershell
# Train model (full process)
python train.py

# Train with custom data
# Edit training_data/sample_data.csv first
python train.py

# Verify model files
ls app/models/
# Should show: model.pkl, tfidf.pkl
```

### Running the Server

```powershell
# Standard startup
python -m uvicorn app.main:app --reload

# Custom host and port
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Without auto-reload (production)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# With worker processes (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using start script
python start_server.py

# Using PowerShell script
.\run_api.ps1
```

### Testing

```powershell
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"return_reason": "item arrived broken"}'

# Batch prediction
curl -X POST http://localhost:8000/predict/batch `
  -H "Content-Type: application/json" `
  -d '{
    "return_reasons": [
      "item broken",
      "wrong product"
    ]
  }'

# Using test script
python test_api.py

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Batch Processing

```powershell
# Process CSV file
python batch_processor.py `
  --mode csv `
  --csv-input "training_data/test_input.csv" `
  --csv-output "results.csv"

# Process Google Sheets
python batch_processor.py `
  --mode sheets `
  --spreadsheet-id "1ABC123xyz..." `
  --worksheet-name "Returns"

# With custom column name
python batch_processor.py `
  --mode sheets `
  --spreadsheet-id "1ABC123xyz..." `
  --reason-column "customer_feedback"
```

### NLTK Resources

```powershell
# Download all required resources
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Download specific resource
python -c "import nltk; nltk.download('punkt')"

# Check available resources
python -c "import nltk; nltk.data.path"
```

---

## 🛠️ Development Workflow

### Daily Development

```powershell
# 1. Navigate to project
cd "d:\My Projects\NLP-Project"

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Pull latest changes (if using Git)
git pull

# 4. Install any new dependencies
pip install -r requirements.txt

# 5. Start development server
python -m uvicorn app.main:app --reload

# 6. Make changes to code
# Server auto-reloads on file changes

# 7. Test changes
curl http://localhost:8000/health

# 8. Stop server (Ctrl+C)
```

### Adding New Training Data

```powershell
# 1. Edit training_data/sample_data.csv
# Add rows with format: return_reason,category

# 2. Retrain model
python train.py

# 3. Restart server
python -m uvicorn app.main:app --reload

# 4. Test new predictions
python test_api.py
```

### Making Code Changes

```powershell
# 1. Activate venv
.\.venv\Scripts\Activate.ps1

# 2. Make changes to code files

# 3. If server is running with --reload, it auto-restarts

# 4. Test changes
curl http://localhost:8000/predict `
  -X POST `
  -H "Content-Type: application/json" `
  -d '{"return_reason": "test input"}'

# 5. Run tests
pytest
```

---

## 🔧 Troubleshooting Commands

### Check Python Version
```powershell
python --version
# Expected: Python 3.11.x or higher
```

### Check Virtual Environment
```powershell
# Should show .venv in prompt
# (.venv) PS D:\My Projects\NLP-Project>

# Verify Python path
python -c "import sys; print(sys.executable)"
# Should point to .venv\Scripts\python.exe
```

### Check Installed Packages
```powershell
pip list | Select-String "fastapi|uvicorn|nltk|sklearn|pandas|gspread"
```

### Check Model Files
```powershell
ls app\models\
# Should show: model.pkl, tfidf.pkl

# Check file sizes
ls app\models\ | Format-Table Name, Length
```

### Check Port Availability
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process using port (if needed)
taskkill /PID <PID> /F
```

### Reset Environment
```powershell
# Deactivate venv
deactivate

# Remove old venv
Remove-Item -Recurse -Force .venv

# Create new venv
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Reinstall packages
pip install -r requirements.txt

# Retrain model
python train.py
```

### Clear Python Cache
```powershell
# Remove all __pycache__ directories
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Remove .pyc files
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
```

---

## 📊 Common API Requests

### Using cURL

```powershell
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000

# Single prediction
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"return_reason": "item arrived broken"}'

# Batch prediction
curl -X POST http://localhost:8000/predict/batch `
  -H "Content-Type: application/json" `
  -d '{
    "return_reasons": [
      "item broken",
      "wrong product",
      "expired",
      "no reason"
    ]
  }'
```

### Using PowerShell Invoke-RestMethod

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Single prediction
$body = @{
    return_reason = "item arrived broken"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

# Batch prediction
$body = @{
    return_reasons = @(
        "item broken",
        "wrong product"
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/predict/batch" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### Using Python Requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Single prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={"return_reason": "item arrived broken"}
)
print(response.json())

# Batch prediction
response = requests.post(
    "http://localhost:8000/predict/batch",
    json={
        "return_reasons": [
            "item broken",
            "wrong product"
        ]
    }
)
print(response.json())
```

---

## 🗂️ File Locations

```
Project Root: d:\My Projects\NLP-Project

Key Files:
├── .venv\                              # Virtual environment
├── app\
│   ├── main.py                         # API server
│   ├── nlp\
│   │   ├── classifier.py              # ML classifier
│   │   ├── preprocess.py              # Text preprocessing
│   │   └── spam_detector.py           # Spam detection
│   ├── services\
│   │   └── sheets_service.py          # Google Sheets
│   └── models\
│       ├── model.pkl                  # Trained model
│       └── tfidf.pkl                  # Trained vectorizer
├── training_data\
│   └── sample_data.csv                # Training dataset
├── credentials\
│   └── service_account.json           # Google credentials
├── requirements.txt                    # Python dependencies
├── train.py                           # Training script
├── batch_processor.py                 # Batch processing
├── index.html                         # Web UI
└── .env                               # Environment variables
```

---

## 🌐 URLs

When server is running on default settings:

- **Base API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root Info**: http://localhost:8000

---

## 📝 Environment Variables (.env)

```env
# Google Sheets Integration
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json

# API Configuration (optional)
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

---

## 🔑 Google Sheets Setup (Quick Reference)

```powershell
# 1. Create Google Cloud Project
# Go to: https://console.cloud.google.com

# 2. Enable APIs
# - Google Sheets API
# - Google Drive API

# 3. Create Service Account
# - Go to Credentials → Create Credentials → Service Account

# 4. Download JSON Key
# - Click on service account → Keys → Add Key → Create new key → JSON

# 5. Store credentials
mkdir credentials
mv ~/Downloads/your-key.json ./credentials/service_account.json

# 6. Update .env
echo "GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json" >> .env

# 7. Share sheet with service account email
# Find email in JSON file: client_email
# Share sheet with this email (Editor permissions)
```

---

## 📚 Documentation Files

- **README.md**: Quick start guide
- **PROJECT_OVERVIEW.md**: High-level overview
- **TECHNICAL_SUMMARY.md**: Technical details
- **COMPLETE_DOCUMENTATION.md**: Comprehensive guide (THIS IS THE MAIN DOC)
- **PIPELINE_FLOW_DIAGRAM.md**: Visual flow diagrams
- **GETTING_STARTED_WINDOWS.md**: Windows-specific setup
- **GOOGLE_SHEETS_SETUP.md**: Google Sheets integration
- **RUN_SERVER_AND_API.md**: Server running guide
- **QUICK_SETUP_REFERENCE.md**: This file

---

## ⚡ Performance Tips

### For Development
- Use `--reload` flag for auto-restart
- Keep only one server instance running
- Use `pytest` for quick testing

### For Production
- Remove `--reload` flag
- Use multiple workers: `--workers 4`
- Set `API_RELOAD=false` in .env
- Use reverse proxy (nginx)
- Enable HTTPS

### For Batch Processing
- Process in chunks for large datasets
- Use Google Sheets API for automatic updates
- Monitor memory usage for very large files

---

## 🎯 Common Tasks Cheatsheet

| Task | Command |
|------|---------|
| Activate venv | `.\.venv\Scripts\Activate.ps1` |
| Start server | `python -m uvicorn app.main:app --reload` |
| Train model | `python train.py` |
| Test API | `python test_api.py` |
| Process CSV | `python batch_processor.py --mode csv --csv-input input.csv --csv-output output.csv` |
| Check health | `curl http://localhost:8000/health` |
| View API docs | Open http://localhost:8000/docs |
| Stop server | `Ctrl+C` |
| Deactivate venv | `deactivate` |

---

## 🆘 Emergency Fixes

### Server Won't Start
```powershell
# Check port
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F

# Restart
python -m uvicorn app.main:app --reload
```

### Model Not Loading
```powershell
# Retrain
python train.py

# Verify files
ls app\models\
```

### Import Errors
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Reinstall
pip install -r requirements.txt
```

### NLTK Errors
```powershell
# Redownload resources
python -c "import nltk; nltk.download('all')"
```

---

*For detailed explanations, see COMPLETE_DOCUMENTATION.md*
*Last Updated: February 15, 2026*
