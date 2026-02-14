# Quick Reference Guide

## 🚀 Common Commands

### Setup and Installation

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK resources
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Automated setup (Windows PowerShell)
.\setup.ps1
```

### Training

```bash
# Train model with sample data
python train.py

# Model files will be saved to:
# app/models/model.pkl
# app/models/tfidf.pkl
```

### Running the API

```bash
# Start API server
python -m uvicorn app.main:app --reload

# Or use convenience script (Windows)
.\run_api.ps1

# API will be available at:
# http://localhost:8000
# http://localhost:8000/docs (Swagger UI)
```

### Testing

```bash
# Run API test suite
python test_api.py

# Test individual modules
python app/nlp/preprocess.py
python app/nlp/spam_detector.py
python app/nlp/classifier.py
```

### Batch Processing

```bash
# Process Google Sheets
python batch_processor.py --mode sheets --spreadsheet-id YOUR_ID --worksheet-name "Sheet1"

# Process local CSV
python batch_processor.py --mode csv --csv-input input.csv --csv-output output.csv

# Custom column name
python batch_processor.py --mode csv --csv-input data.csv --csv-output results.csv --column "customer_reason"
```

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Single Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"return_reason": "item arrived broken"}'
```

### Batch Prediction
```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"return_reasons": ["item broken", "wrong product", "no reason"]}'
```

### Get Categories
```bash
curl http://localhost:8000/categories
```

### Preprocess Text
```bash
curl -X POST "http://localhost:8000/preprocess?text=Item%20was%20BROKEN!!!"
```

## 🐍 Python Usage

### Single Prediction
```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"return_reason": "item arrived broken"}
)
result = response.json()
print(result)
# Output: {'is_spam': False, 'reason_category': 'Product Quality Issue', 'severity_score': 0.9, ...}
```

### Batch Prediction
```python
import requests

response = requests.post(
    "http://localhost:8000/predict/batch",
    json={
        "return_reasons": [
            "item broken",
            "wrong product sent",
            "no reason"
        ]
    }
)
result = response.json()
print(f"Processed {result['total']} items")
for pred in result['predictions']:
    print(pred)
```

### Using Classifier Directly
```python
from app.nlp.classifier import NLPClassifier

# Load trained model
classifier = NLPClassifier(
    model_path="app/models/model.pkl",
    vectorizer_path="app/models/tfidf.pkl"
)

# Predict
result = classifier.predict("item arrived broken")
print(result)
```

### Using Preprocessing
```python
from app.nlp.preprocess import preprocess_text
from app.nlp.spam_detector import is_spam

text = "Item was BROKEN!!! Completely unusable."
processed = preprocess_text(text)
spam = is_spam(text)

print(f"Original: {text}")
print(f"Processed: {processed}")
print(f"Is Spam: {spam}")
```

## 📊 Google Sheets Setup

### 1. Google Cloud Console
```
1. Go to https://console.cloud.google.com/
2. Create new project
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create Service Account:
   - IAM & Admin > Service Accounts
   - Create account
   - Download JSON credentials
```

### 2. Configure Credentials
```bash
# Create credentials directory
mkdir credentials

# Copy credentials file
# Save as: credentials/service_account.json

# Update .env file
echo "GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json" > .env
```

### 3. Share Spreadsheet
```
1. Open your Google Sheet
2. Click "Share"
3. Add service account email (from JSON file)
4. Give "Editor" permissions
```

### 4. Get Spreadsheet ID
```
From URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
Copy the SPREADSHEET_ID part
```

## 🔧 Configuration

### Environment Variables (.env)
```env
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
API_HOST=0.0.0.0
API_PORT=8000
MODEL_PATH=./app/models/model.pkl
VECTORIZER_PATH=./app/models/tfidf.pkl
```

### Model Hyperparameters
```python
# In train.py or when creating classifier
classifier = NLPClassifier(
    max_features=1000,      # Max TF-IDF features
    ngram_range=(1, 2)      # Unigrams and bigrams
)
```

### Preprocessing Options
```python
from app.nlp.preprocess import preprocess_text

processed = preprocess_text(
    text,
    lowercase=True,         # Convert to lowercase
    remove_punct=True,      # Remove punctuation
    remove_nums=True,       # Remove numbers
    remove_stops=True,      # Remove stopwords
    lemmatize=True,         # Apply lemmatization
    min_token_length=2      # Min token length
)
```

## 🐛 Troubleshooting

### NLTK Resources Not Found
```python
python -c "import nltk; nltk.download('all')"
```

### Model Not Loading
```bash
# Check if model files exist
ls app/models/

# Retrain if missing
python train.py
```

### API Connection Error
```bash
# Check if server is running
curl http://localhost:8000/health

# Start server if not running
python -m uvicorn app.main:app --reload
```

### Google Sheets Authentication Error
```bash
# Verify credentials path in .env
cat .env | grep GOOGLE_CREDENTIALS_PATH

# Check file exists
ls credentials/service_account.json

# Verify service account has access to sheet
```

### Import Errors
```bash
# Ensure virtual environment is activated
which python  # Linux/Mac
where python  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

## 📦 File Structure

```
NLP-Project/
├── app/                        # Application code
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── nlp/                    # NLP modules
│   │   ├── preprocess.py
│   │   ├── spam_detector.py
│   │   └── classifier.py
│   ├── services/               # External services
│   │   └── sheets_service.py
│   └── models/                 # Trained models (generated)
│       ├── model.pkl
│       └── tfidf.pkl
├── training_data/              # Training datasets
│   ├── sample_data.csv         # Sample labeled data
│   └── test_input.csv          # Test data
├── credentials/                # API credentials (not in git)
│   └── service_account.json
├── train.py                    # Training script
├── batch_processor.py          # Batch processing
├── test_api.py                 # API tests
├── requirements.txt            # Dependencies
├── README.md                   # Main documentation
├── TECHNICAL_SUMMARY.md        # Technical details
├── CHANGELOG.md                # Version history
├── QUICK_REFERENCE.md          # This file
├── .env                        # Environment variables (not in git)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── setup.ps1                   # Setup script (Windows)
└── run_api.ps1                 # Run script (Windows)
```

## 🎯 Category Reference

| Category | Severity | Keywords |
|----------|----------|----------|
| Product Quality Issue | 0.9 | broken, damaged, defective, poor quality |
| Expiry Issue | 0.9 | expired, expiration, expiry date |
| Packaging Issue | 0.6 | packaging, box damaged, torn |
| Wrong Item | 0.6 | wrong item, incorrect, different product |
| Customer Preference | 0.3 | don't need, changed mind, don't want |
| Other | 0.2 | late delivery, duplicate order |

## 📈 Performance Tips

### Speed Optimization
- Use batch endpoint for multiple predictions
- Cache frequently predicted texts
- Run on multi-core machine for parallel requests
- Use async client for API calls

### Accuracy Improvement
- Add more training examples (50+ per category)
- Balance category distribution in training data
- Review and correct mislabeled examples
- Add domain-specific stopwords if needed

### Scaling
- Deploy multiple API instances behind load balancer
- Use connection pooling for Google Sheets
- Implement request queuing for batch jobs
- Monitor and optimize bottlenecks

## 📚 Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **NLTK Docs**: https://www.nltk.org/
- **scikit-learn Docs**: https://scikit-learn.org/
- **gspread Docs**: https://docs.gspread.org/
- **Google Sheets API**: https://developers.google.com/sheets/api

---

**Need help?** Check README.md for detailed documentation.
