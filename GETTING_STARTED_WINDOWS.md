# Getting Started on Windows

## Prerequisites
- Windows 10 or 11
- Python 3.11+ installed
- PowerShell or Command Prompt

## Installation

### Option 1: Automated Setup (Recommended)

1. Open PowerShell in the project directory:
```powershell
cd "d:\My Projects\NLP-Project"
```

2. Run the setup script:
```powershell
.\setup.ps1
```

This will:
- Create virtual environment
- Install all dependencies
- Download NLTK resources
- Train the model
- Setup environment file

### Option 2: Manual Setup

1. Create virtual environment:
```powershell
python -m venv venv
```

2. Activate virtual environment:
```powershell
venv\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Download NLTK resources:
```powershell
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

5. Train the model:
```powershell
python train.py
```

## Running the API

### Option 1: Using Run Script
```powershell
.\run_api.ps1
```

### Option 2: Manual Start
```powershell
# Activate venv first
venv\Scripts\Activate.ps1

# Start server
python -m uvicorn app.main:app --reload
```

The API will be available at:
- **Main**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## Testing

### Test the API
```powershell
python test_api.py
```

### Test via Browser
Open: http://localhost:8000/docs

Click "Try it out" on any endpoint!

### Test via PowerShell
```powershell
# Single prediction
Invoke-RestMethod -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"return_reason": "item arrived broken"}'

# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

## Batch Processing

### Process Local CSV
```powershell
python batch_processor.py --mode csv --csv-input training_data\test_input.csv --csv-output results.csv
```

### Process Google Sheets
```powershell
# First, setup Google credentials (see README.md)
python batch_processor.py --mode sheets --spreadsheet-id YOUR_SPREADSHEET_ID
```

## Common Issues

### Python Not Found
Make sure Python is in your PATH:
```powershell
python --version
```

If not found, reinstall Python and check "Add to PATH" during installation.

### Execution Policy Error
Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Virtual Environment Not Activating
Try using Command Prompt instead:
```cmd
venv\Scripts\activate.bat
```

### Port Already in Use
Change the port:
```powershell
python -m uvicorn app.main:app --reload --port 8001
```

### Module Not Found Errors
Ensure virtual environment is activated:
```powershell
# You should see (venv) in your prompt
venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

## Google Sheets Setup (Optional)

### 1. Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Google Sheets API and Google Drive API

### 2. Create Service Account
1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Download JSON credentials

### 3. Setup Credentials
```powershell
# Create credentials folder
mkdir credentials

# Copy your downloaded JSON file to:
# credentials\service_account.json

# Update .env file
Add-Content .env "GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json"
```

### 4. Share Your Sheet
1. Open your Google Sheet
2. Click "Share"
3. Add the service account email (from JSON file)
4. Give "Editor" permission

## Next Steps

1. ✅ API is running at http://localhost:8000
2. ✅ Visit http://localhost:8000/docs for interactive API docs
3. ✅ Try the test script: `python test_api.py`
4. ✅ Process a CSV: `python batch_processor.py --mode csv --csv-input training_data\test_input.csv --csv-output results.csv`
5. ✅ Read the documentation:
   - README.md - Complete guide
   - QUICK_REFERENCE.md - Command reference
   - PROJECT_OVERVIEW.md - System overview

## Quick Commands Reference

```powershell
# Activate virtual environment
venv\Scripts\Activate.ps1

# Train model
python train.py

# Start API
python -m uvicorn app.main:app --reload

# Test API
python test_api.py

# Process CSV
python batch_processor.py --mode csv --csv-input input.csv --csv-output output.csv

# Deactivate virtual environment
deactivate
```

## Help

If you encounter any issues:
1. Check that virtual environment is activated
2. Ensure all dependencies are installed
3. Verify model files exist in `app\models\`
4. Check the logs for error messages
5. Refer to README.md for detailed documentation

---

**Ready to classify!** 🚀
