# NLP Return Reason Classifier

A production-ready lightweight NLP system for classifying customer return reasons using classical machine learning. Built with NLTK, TF-IDF, and Logistic Regression.

## 🎯 Overview

This system classifies customer return reasons into categories, detects spam inputs, assigns severity scores, and integrates with Google Sheets for automated batch processing. It's designed to be fast, explainable, and suitable for real-time API usage.

### Key Features

- ✅ **Classical NLP** - NLTK-based text preprocessing
- ✅ **Fast Classification** - TF-IDF + Logistic Regression (<50ms per request)
- ✅ **Spam Detection** - Rule-based spam filtering
- ✅ **Severity Scoring** - Automatic severity assignment
- ✅ **REST API** - FastAPI endpoints for predictions
- ✅ **Google Sheets Integration** - Automated batch processing
- ✅ **Production Ready** - Clean, modular, well-documented code

## 📊 Classification Categories

| Category | Severity Score | Description |
|----------|---------------|-------------|
| Product Quality Issue | 0.9 (High) | Defects, poor quality, broken items |
| Expiry Issue | 0.9 (High) | Expired products |
| Packaging Issue | 0.6 (Medium) | Damaged or poor packaging |
| Wrong Item | 0.6 (Medium) | Incorrect product sent |
| Customer Preference | 0.3 (Low) | Changed mind, personal reasons |
| Other | 0.2 (Low) | Miscellaneous reasons |

## 🏗️ Architecture

```
project_root/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── preprocess.py       # Text preprocessing
│   │   ├── spam_detector.py    # Spam detection
│   │   └── classifier.py       # TF-IDF + Logistic Regression
│   ├── services/
│   │   ├── __init__.py
│   │   └── sheets_service.py   # Google Sheets integration
│   └── models/
│       ├── model.pkl           # Trained model (generated)
│       └── tfidf.pkl           # Trained vectorizer (generated)
├── training_data/
│   └── sample_data.csv         # Sample training dataset
├── train.py                    # Model training script
├── batch_processor.py          # Batch processing script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. **Clone or create the project directory**

```bash
cd "d:\My Projects\NLP-Project"
```

2. **Create virtual environment**

```bash
python -m venv venv
```

3. **Activate virtual environment**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Download NLTK resources**

The first run will automatically download required NLTK resources (punkt, stopwords, wordnet).

### Training the Model

Train the classifier using the provided sample dataset:

```bash
python train.py
```

This will:
- Load training data from `training_data/sample_data.csv`
- Preprocess text using NLTK
- Train TF-IDF vectorizer and Logistic Regression model
- Save models to `app/models/`
- Display training metrics and test predictions

**Expected output:**
```
Loading training data from: training_data\sample_data.csv
Loaded 75 training samples
...
Training complete. Accuracy: 0.95+
✓ Training complete!
```

### Running the API Server

If you want a short, plain-English guide (run server + endpoints + example responses), see: [RUN_SERVER_AND_API.md](RUN_SERVER_AND_API.md)

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python app/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Usage

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### Single Prediction

```bash
POST /predict
Content-Type: application/json

{
  "return_reason": "item arrived broken"
}
```

Response:
```json
{
  "is_spam": false,
  "reason_category": "Product Quality Issue",
  "severity_score": 0.9,
  "confidence": 0.85
}
```

### Batch Prediction

```bash
POST /predict/batch
Content-Type: application/json

{
  "return_reasons": [
    "item arrived broken",
    "wrong product sent",
    "no reason"
  ]
}
```

Response:
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
      "severity_score": 0.0
    }
  ],
  "total": 3
}
```

### Get Categories

```bash
GET /categories
```

Response:
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

### Preprocess Text (Debug)

```bash
POST /preprocess?text=Item%20was%20BROKEN!!!
```

Response:
```json
{
  "original": "Item was BROKEN!!!",
  "preprocessed": "item broken",
  "is_spam": false
}
```

## 📊 Google Sheets Integration

### Setup Google Sheets API

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project

2. **Enable APIs**
   - Enable Google Sheets API
   - Enable Google Drive API

3. **Create Service Account**
   - Go to "IAM & Admin" > "Service Accounts"
   - Create service account
   - Download JSON credentials file

4. **Configure Credentials**
   - Create `credentials` directory in project root
   - Save JSON file as `credentials/service_account.json`
   - Update `.env` file:
     ```
     GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
     ```

5. **Share Spreadsheet**
   - Open your Google Sheet
   - Click "Share"
   - Add service account email (found in JSON file)
   - Give "Editor" permissions

### Batch Processing

#### Process Google Sheets

```bash
python batch_processor.py --mode sheets --spreadsheet-id YOUR_SPREADSHEET_ID --worksheet-name "Sheet1" --column "return_reason"
```

#### Process Local CSV

```bash
python batch_processor.py --mode csv --csv-input input.csv --csv-output output.csv --column "return_reason"
```

### Expected Sheet Format

**Input:**
| return_reason |
|--------------|
| Item arrived broken |
| Wrong product sent |
| no reason |

**Output:**
| return_reason | reason_category | severity_score | is_spam |
|--------------|----------------|----------------|---------|
| Item arrived broken | Product Quality Issue | 0.9 | FALSE |
| Wrong product sent | Wrong Item | 0.6 | FALSE |
| no reason | Other | 0.0 | TRUE |

## 🧪 Testing

### Test NLP Preprocessing

```bash
python app/nlp/preprocess.py
```

### Test Spam Detection

```bash
python app/nlp/spam_detector.py
```

### Test Classifier

```bash
python app/nlp/classifier.py
```

## 🔧 Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```env
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
API_HOST=0.0.0.0
API_PORT=8000
```

### Model Configuration

Adjust hyperparameters in `train.py` or when initializing `NLPClassifier`:

```python
classifier = NLPClassifier(
    max_features=1000,      # Max TF-IDF features
    ngram_range=(1, 2)      # Unigrams and bigrams
)
```

## 📝 Training with Custom Data

### Prepare Your Dataset

Create a CSV file with two columns:

```csv
return_reason,category
"Product is broken",Product Quality Issue
"Wrong item sent",Wrong Item
"Already expired",Expiry Issue
```

### Update Training Script

Modify `TRAINING_DATA_PATH` in `train.py`:

```python
TRAINING_DATA_PATH = Path("path/to/your/data.csv")
```

### Run Training

```bash
python train.py
```

## 🎯 NLP Pipeline Details

### Preprocessing Steps

1. **Lowercase conversion**
2. **Punctuation removal**
3. **Number removal**
4. **Tokenization** (NLTK word_tokenize)
5. **Stopword removal** (English stopwords)
6. **Lemmatization** (WordNet lemmatizer)
7. **Short token filtering** (min length: 2)

### Spam Detection Rules

- Empty or whitespace only
- Too short text (< 3 chars)
- Exact matches: "no reason", "none", "return", "n/a", etc.
- Spam substrings: "zzz", "asdf", "test", etc.
- Repetitive characters (>70% same char)
- Only special characters (no letters)

### Classification Model

- **Vectorization**: TF-IDF with unigrams and bigrams
- **Algorithm**: Logistic Regression with balanced class weights
- **Features**: Top 1000 TF-IDF features
- **Performance**: ~95% accuracy on sample dataset

## 🚀 Performance

- **Inference Speed**: <50ms per request
- **Memory Usage**: ~100MB (model + dependencies)
- **Scalability**: Can handle 5000+ rows easily
- **No GPU Required**: Runs on CPU efficiently

## 🔌 Integration Examples

### Python Client

```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"return_reason": "item arrived broken"}
)
result = response.json()
print(result)
```

### cURL

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"return_reason": "item arrived broken"}'
```

### n8n Integration

1. Add HTTP Request node
2. Method: POST
3. URL: `http://localhost:8000/predict/batch`
4. Body: JSON with `return_reasons` array
5. Parse response

## 🛠️ Extending the System

### Add New Categories

1. Update `SEVERITY_MAP` in `app/nlp/classifier.py`
2. Add training samples to CSV
3. Retrain model: `python train.py`

### Customize Preprocessing

Modify `preprocess_text()` in `app/nlp/preprocess.py`:

```python
processed = preprocess_text(
    text,
    lowercase=True,
    remove_punct=True,
    remove_nums=True,
    remove_stops=True,
    lemmatize=True,
    min_token_length=2
)
```

### Add Custom Spam Patterns

Update `SPAM_EXACT_MATCHES` or `SPAM_SUBSTRINGS` in `app/nlp/spam_detector.py`.

## 📦 Deployment

### Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download NLTK resources
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t nlp-classifier .
docker run -p 8000:8000 nlp-classifier
```

### Cloud Deployment

Deploy to any platform supporting Python:
- **AWS**: EC2, ECS, Lambda (with API Gateway)
- **Azure**: App Service, Container Instances
- **GCP**: Cloud Run, Compute Engine
- **Heroku**: Web dyno

## 📊 Monitoring

Add logging middleware in `app/main.py`:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {duration:.3f}s")
    return response
```

## 🤝 Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Run black formatter: `black .`

### Testing

```bash
pytest
```

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙋 Support

For issues or questions:
1. Check API docs at `/docs`
2. Review logs for error messages
3. Validate training data format
4. Ensure NLTK resources are downloaded

## 🎓 Technical Details

### Dependencies

- **fastapi**: Modern web framework
- **uvicorn**: ASGI server
- **nltk**: NLP preprocessing
- **scikit-learn**: ML algorithms
- **pandas**: Data manipulation
- **gspread**: Google Sheets API
- **google-auth**: Authentication
- **joblib**: Model persistence

### System Requirements

- **Python**: 3.11+
- **RAM**: 512MB minimum
- **Disk**: 200MB for dependencies + models
- **OS**: Windows, Linux, macOS

## 🔍 Troubleshooting

### NLTK Resources Not Found

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

### Model Not Loading

Ensure you've trained the model:
```bash
python train.py
```

### Google Sheets Authentication Failure

1. Verify credentials path in `.env`
2. Check service account has access to sheet
3. Ensure APIs are enabled in Google Cloud

### Import Errors

Ensure virtual environment is activated:
```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 📈 Future Enhancements

- [ ] Multi-language support
- [ ] Confidence threshold tuning
- [ ] Model versioning
- [ ] A/B testing framework
- [ ] Real-time monitoring dashboard
- [ ] Automated retraining pipeline

---

**Built with ❤️ using Classical NLP + Machine Learning**
