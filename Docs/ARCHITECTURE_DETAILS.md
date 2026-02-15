# System Architecture & Component Details

## 📐 Complete Architecture Overview

This document provides detailed architectural views of the NLP Return Reason Classifier system.

---

## 1. Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  Web Browser   │  │  REST Client   │  │ Google Sheets  │   │
│  │  (index.html)  │  │  (curl/Python) │  │  Integration   │   │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘   │
└───────────┼──────────────────┼──────────────────────┼───────────┘
            │                  │                      │
            └──────────────────┼──────────────────────┘
                               │ HTTP/JSON
┌─────────────────────────────▼─────────────────────────────────┐
│                      APPLICATION LAYER                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │            FastAPI Application (app/main.py)             │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │  Endpoints:                                       │   │ │
│  │  │  • GET  /                  - Root info            │   │ │
│  │  │  • GET  /health            - Health check         │   │ │
│  │  │  • POST /predict           - Single prediction    │   │ │
│  │  │  • POST /predict/batch     - Batch predictions    │   │ │
│  │  │  • POST /sheets/update     - Update sheets        │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │  Middleware:                                      │   │ │
│  │  │  • CORS                    - Cross-origin         │   │ │
│  │  │  • Request Validation      - Pydantic models      │   │ │
│  │  │  • Error Handling          - Exception handlers   │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Core Services:                                          │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │  NLPClassifier (app/nlp/classifier.py)         │    │ │
│  │  │  • Main classification orchestration            │    │ │
│  │  │  • Model loading and inference                  │    │ │
│  │  │  • Batch processing logic                       │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │  SpamDetector (app/nlp/spam_detector.py)       │    │ │
│  │  │  • Rule-based spam detection                    │    │ │
│  │  │  • Pattern matching                             │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │  TextPreprocessor (app/nlp/preprocess.py)      │    │ │
│  │  │  • NLTK-based text cleaning                     │    │ │
│  │  │  • Tokenization, lemmatization                  │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │  GoogleSheetsService (services/sheets_service)  │    │ │
│  │  │  • gspread client wrapper                       │    │ │
│  │  │  • CRUD operations on sheets                    │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│                    MACHINE LEARNING LAYER                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  ML Components (scikit-learn):                           │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │  TfidfVectorizer                                │    │ │
│  │  │  • max_features: 1000                           │    │ │
│  │  │  • ngram_range: (1, 2)                          │    │ │
│  │  │  • min_df: 2, max_df: 0.8                       │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │  LogisticRegression                             │    │ │
│  │  │  • 6 binary classifiers (One-vs-Rest)           │    │ │
│  │  │  • solver: lbfgs                                │    │ │
│  │  │  • class_weight: balanced                       │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  │                                                          │ │
│  │  ┌────────────────────────────────────────────────┐    │ │
│  │  │  NLTK Components                                │    │ │
│  │  │  • WordNetLemmatizer                            │    │ │
│  │  │  • word_tokenize                                │    │ │
│  │  │  • stopwords (English)                          │    │ │
│  │  └────────────────────────────────────────────────┘    │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────┬────────────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────────┐
│                        DATA LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────┐ │ │
│  │  │ Trained Models │  │ Training Data  │  │  Google   │ │ │
│  │  │                │  │                │  │  Sheets   │ │ │
│  │  │ • model.pkl    │  │ • sample_data  │  │    API    │ │ │
│  │  │ • tfidf.pkl    │  │   .csv         │  │           │ │ │
│  │  │                │  │ • test files   │  │           │ │ │
│  │  │ (~500KB total) │  │                │  │           │ │ │
│  │  └────────────────┘  └────────────────┘  └───────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Interaction Diagram

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Client    │         │  FastAPI    │         │ Classifier  │
│             │         │   Server    │         │   Service   │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │ POST /predict         │                       │
       │ {"return_reason":...} │                       │
       ├──────────────────────►│                       │
       │                       │                       │
       │                       │ classifier.predict()  │
       │                       ├──────────────────────►│
       │                       │                       │
       │                       │                       │ is_spam()?
       │                       │                       ├──────────┐
       │                       │                       │          │
       │                       │                       │◄─────────┘
       │                       │                       │ False
       │                       │                       │
       │                       │                       │ preprocess_text()
       │                       │                       ├──────────┐
       │                       │                       │          │
       │                       │                       │◄─────────┘
       │                       │                       │"item broken"
       │                       │                       │
       │                       │                       │ vectorizer.transform()
       │                       │                       ├──────────┐
       │                       │                       │          │
       │                       │                       │◄─────────┘
       │                       │                       │[vector]
       │                       │                       │
       │                       │                       │ model.predict()
       │                       │                       ├──────────┐
       │                       │                       │          │
       │                       │                       │◄─────────┘
       │                       │                       │category
       │                       │                       │
       │                       │                       │ get_severity()
       │                       │                       ├──────────┐
       │                       │                       │          │
       │                       │                       │◄─────────┘
       │                       │                       │0.9
       │                       │                       │
       │                       │   Return result       │
       │                       │◄──────────────────────┤
       │                       │                       │
       │  200 OK               │                       │
       │  {                    │                       │
       │    "is_spam": false,  │                       │
       │    "category": "...", │                       │
       │    "severity": 0.9    │                       │
       │  }                    │                       │
       │◄──────────────────────┤                       │
       │                       │                       │
```

---

## 3. Data Flow Architecture

```
INPUT TEXT: "Item arrived broken and damaged"
     │
     ▼
┌─────────────────────────────────────┐
│  1. SPAM DETECTION                  │
│  ────────────────────────────────── │
│  Function: is_spam(text)            │
│  Location: spam_detector.py         │
│  Purpose: Filter garbage inputs     │
│                                     │
│  Checks:                            │
│  ✓ Empty/whitespace                 │
│  ✓ Too short (<3 chars)             │
│  ✓ Known spam phrases               │
│  ✓ Character repetition (>70%)      │
│                                     │
│  Result: False (not spam)           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. TEXT PREPROCESSING              │
│  ────────────────────────────────── │
│  Function: preprocess_text(text)    │
│  Location: preprocess.py            │
│  Purpose: Normalize text            │
│                                     │
│  Steps:                             │
│  1. Lowercase                       │
│     → "item arrived broken..."      │
│  2. Remove punctuation              │
│     → "item arrived broken and..."  │
│  3. Tokenize                        │
│     → ["item","arrived","broken"]   │
│  4. Remove stopwords                │
│     → ["item","broken","damaged"]   │
│  5. Lemmatize                       │
│     → ["item","break","damage"]     │
│  6. Join                            │
│     → "item break damage"           │
│                                     │
│  Result: "item break damage"        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. FEATURE EXTRACTION              │
│  ────────────────────────────────── │
│  Object: TfidfVectorizer            │
│  Location: classifier.py            │
│  Purpose: Convert text to numbers   │
│                                     │
│  Configuration:                     │
│  • max_features: 1000               │
│  • ngram_range: (1, 2)              │
│  • min_df: 2                        │
│  • max_df: 0.8                      │
│                                     │
│  Generated Features:                │
│  Unigrams:                          │
│    "item": 0.42                     │
│    "break": 0.58                    │
│    "damage": 0.53                   │
│  Bigrams:                           │
│    "item break": 0.31               │
│    "break damage": 0.45             │
│  (+ 995 more features = 0)          │
│                                     │
│  Result: [0.42, 0.58, ..., 0] (1000)│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. CLASSIFICATION                  │
│  ────────────────────────────────── │
│  Model: LogisticRegression          │
│  Location: classifier.py            │
│  Purpose: Predict category          │
│                                     │
│  6 Binary Classifiers:              │
│  Classifier 1: Product Quality      │
│    P = sigmoid(w·x + b) = 0.91 ✓    │
│  Classifier 2: Expiry Issue         │
│    P = 0.04                         │
│  Classifier 3: Packaging Issue      │
│    P = 0.23                         │
│  Classifier 4: Wrong Item           │
│    P = 0.06                         │
│  Classifier 5: Customer Preference  │
│    P = 0.02                         │
│  Classifier 6: Other                │
│    P = 0.01                         │
│                                     │
│  Winner: Product Quality Issue      │
│  Confidence: 0.91                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  5. SEVERITY MAPPING                │
│  ────────────────────────────────── │
│  Dictionary: SEVERITY_MAP           │
│  Location: classifier.py            │
│  Purpose: Assign urgency score      │
│                                     │
│  Mapping:                           │
│  "Product Quality Issue" → 0.9 ✓    │
│  "Expiry Issue" → 0.9               │
│  "Packaging Issue" → 0.6            │
│  "Wrong Item" → 0.6                 │
│  "Customer Preference" → 0.3        │
│  "Other" → 0.2                      │
│                                     │
│  Result: 0.9 (High priority)        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  6. RESPONSE FORMATION              │
│  ────────────────────────────────── │
│  Model: PredictionResponse          │
│  Location: main.py                  │
│  Purpose: Format and return         │
│                                     │
│  Output JSON:                       │
│  {                                  │
│    "is_spam": false,                │
│    "reason_category":               │
│      "Product Quality Issue",       │
│    "severity_score": 0.9,           │
│    "confidence": 0.91               │
│  }                                  │
└─────────────────────────────────────┘
```

---

## 4. File Structure Map

```
app/
│
├── main.py (696 lines)
│   ├── FastAPI() initialization
│   ├── CORS middleware setup
│   ├── Pydantic models:
│   │   ├── PredictionRequest
│   │   ├── PredictionResponse
│   │   ├── BatchPredictionRequest
│   │   ├── BatchPredictionResponse
│   │   └── GoogleSheetsUpdateRequest
│   ├── Endpoints:
│   │   ├── GET  /
│   │   ├── GET  /health
│   │   ├── POST /predict
│   │   ├── POST /predict/batch
│   │   └── POST /sheets/update
│   └── Startup event handler
│
├── nlp/
│   │
│   ├── __init__.py
│   │   └── Exports: preprocess_text, is_spam, NLPClassifier
│   │
│   ├── classifier.py (290 lines)
│   │   ├── Class: NLPClassifier
│   │   ├── Methods:
│   │   │   ├── __init__()
│   │   │   ├── train()
│   │   │   ├── predict()
│   │   │   ├── predict_batch()
│   │   │   ├── load_models()
│   │   │   └── save_models()
│   │   └── Constants:
│   │       ├── SEVERITY_MAP
│   │       ├── MIN_CONFIDENCE_THRESHOLD
│   │       └── VALID_CATEGORIES
│   │
│   ├── preprocess.py (229 lines)
│   │   ├── Functions:
│   │   │   ├── download_nltk_resources()
│   │   │   ├── preprocess_text()
│   │   │   ├── remove_punctuation()
│   │   │   ├── remove_numbers()
│   │   │   ├── tokenize()
│   │   │   ├── remove_stopwords()
│   │   │   ├── lemmatize_tokens()
│   │   │   └── filter_short_tokens()
│   │   └── NLTK Setup:
│   │       ├── STOP_WORDS
│   │       └── LEMMATIZER
│   │
│   └── spam_detector.py (234 lines)
│       ├── Functions:
│       │   ├── is_spam()
│       │   ├── is_empty_or_whitespace()
│       │   ├── is_too_short()
│       │   ├── has_too_few_words()
│       │   ├── is_exact_spam_match()
│       │   ├── contains_spam_substring()
│       │   └── has_excessive_character_repetition()
│       └── Constants:
│           ├── SPAM_EXACT_MATCHES
│           ├── SPAM_SUBSTRINGS
│           ├── MIN_TEXT_LENGTH
│           └── MIN_WORD_COUNT
│
├── services/
│   │
│   └── sheets_service.py (265 lines)
│       ├── Class: GoogleSheetsService
│       ├── Methods:
│       │   ├── __init__()
│       │   ├── authenticate()
│       │   ├── get_spreadsheet()
│       │   ├── get_worksheet()
│       │   ├── read_sheet_to_dataframe()
│       │   ├── write_dataframe_to_sheet()
│       │   └── batch_update_rows()
│       └── Constants:
│           └── SCOPES
│
└── models/
    ├── model.pkl (~450KB)
    │   └── Serialized LogisticRegression model
    │
    └── tfidf.pkl (~50KB)
        └── Serialized TfidfVectorizer
```

---

## 5. Technology Stack Details

### Backend Framework
```
FastAPI 0.109.0+
├── Pydantic (data validation)
├── Starlette (ASGI framework)
└── Uvicorn (ASGI server)
```

### NLP & ML Libraries
```
NLTK 3.8.1+
├── punkt (tokenization)
├── stopwords (filtering)
├── wordnet (lemmatization)
└── averaged_perceptron_tagger

scikit-learn 1.4.0+
├── TfidfVectorizer
├── LogisticRegression
├── train_test_split
└── classification_report
```

### Data Processing
```
pandas 2.2.0+
├── DataFrame operations
├── CSV reading/writing
└── Data transformations

numpy 1.26.3+
└── Array operations
```

### Google Integration
```
gspread 5.12.4+
├── google-auth 2.27.0+
├── google-auth-oauthlib 1.2.0+
└── google-auth-httplib2 0.2.0+
```

### Utilities
```
joblib 1.3.2+ (model serialization)
python-dotenv 1.0.1+ (env variables)
openpyxl 3.1.2+ (Excel support)
```

---

## 6. Processing Time Breakdown

```
Single Prediction Pipeline (Total: 5-10ms)
│
├── HTTP Request Parsing ────────── <1ms
├── Input Validation (Pydantic) ─── <1ms
├── Spam Detection ─────────────── <1ms
├── Text Preprocessing ─────────── 2-5ms
│   ├── Lowercase ────────────── <0.1ms
│   ├── Punctuation removal ──── <0.1ms
│   ├── Tokenization ─────────── 1-2ms
│   ├── Stopword removal ─────── <0.5ms
│   └── Lemmatization ────────── 1-2ms
├── TF-IDF Vectorization ───────── 1-2ms
├── Logistic Regression ────────── <1ms
├── Severity Mapping ───────────── <0.1ms
└── Response Serialization ─────── <1ms
```

---

## 7. Memory Usage

```
Component                    Memory Usage
────────────────────────────────────────
FastAPI Application          ~50MB
Loaded Models:
  - model.pkl                ~30MB (in RAM)
  - tfidf.pkl                ~10MB (in RAM)
NLTK Resources               ~20MB
Python Runtime               ~50MB
────────────────────────────────────────
Total (Typical)              ~160MB
Peak (During Training)       ~500MB
```

---

## 8. Scalability Architecture

```
┌────────────────────────────────────────┐
│         Load Balancer (nginx)          │
└────────┬───────────────┬───────────────┘
         │               │
         ▼               ▼
┌─────────────┐   ┌─────────────┐
│  FastAPI    │   │  FastAPI    │   ... (N workers)
│  Worker 1   │   │  Worker 2   │
│  Port 8000  │   │  Port 8001  │
└──────┬──────┘   └──────┬──────┘
       │                 │
       └────────┬────────┘
                │
                ▼
┌────────────────────────────────────────┐
│         Shared Resources               │
│  ┌──────────────┐  ┌──────────────┐  │
│  │  Model Files │  │  Google API  │  │
│  │  (Read-Only) │  │  Credentials │  │
│  └──────────────┘  └──────────────┘  │
└────────────────────────────────────────┘
```

---

## 9. Deployment Options

### Option 1: Single Server
```
Windows/Linux Server
├── Python 3.11+ Virtual Environment
├── Uvicorn ASGI Server
├── Single Worker Process
└── Access: http://localhost:8000
```

### Option 2: Multi-Worker
```
Production Server
├── Uvicorn with 4-8 workers
├── Load distribution across cores
├── Shared model files (read-only)
└── Access: http://0.0.0.0:8000
```

### Option 3: Containerized
```
Docker Container
├── Base Image: python:3.11-slim
├── Copy application code
├── Install dependencies
├── Expose port 8000
└── CMD: uvicorn app.main:app
```

### Option 4: Cloud Deployment
```
Cloud Platform (Azure/AWS/GCP)
├── Container Service (AKS/ECS/GKE)
├── Managed Database (optional)
├── Load Balancer
├── Auto-scaling
└── HTTPS via managed certificates
```

---

## 10. Security Architecture

```
┌─────────────────────────────────────────┐
│         External Access Layer           │
│  ┌───────────────────────────────────┐ │
│  │  HTTPS/TLS (Production)           │ │
│  │  Rate Limiting (optional)         │ │
│  └────────────────┬──────────────────┘ │
└───────────────────┼─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│         Application Layer               │
│  ┌───────────────────────────────────┐ │
│  │  CORS Policy                      │ │
│  │  • Allowed origins                │ │
│  │  • Allowed methods                │ │
│  │  └─────────────────────────────┐ │ │
│  │  Input Validation (Pydantic)    │ │ │
│  │  • Type checking                │ │ │
│  │  • Field validation             │ │ │
│  └───────────────────────────────────┘ │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│         Data Protection Layer           │
│  ┌───────────────────────────────────┐ │
│  │  Environment Variables (.env)     │ │
│  │  • Not committed to Git           │ │
│  │  • Google credentials path        │ │
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  Google Service Account           │ │
│  │  • JSON file gitignored           │ │
│  │  • Limited scope permissions      │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 11. Error Handling Flow

```
Request → Validation → Processing → Response
   │          │            │           │
   │          │            │           └─→ 200 OK (Success)
   │          │            │
   │          │            └─→ Exception Caught
   │          │                    │
   │          │                    ├─→ HTTPException
   │          │                    │   └─→ 40X/50X + detail
   │          │                    │
   │          │                    └─→ Generic Exception
   │          │                        └─→ 500 + logged error
   │          │
   │          └─→ ValidationError
   │                  └─→ 422 Unprocessable Entity
   │
   └─→ Model Not Loaded
           └─→ 503 Service Unavailable
```

---

## 12. Monitoring & Logging

```
Application Logs
├── Level: INFO
├── Format: timestamp - name - level - message
├── Output: stdout/stderr
└── Contents:
    ├── Server startup events
    ├── Model loading status
    ├── Request processing info
    └── Error traces

Metrics (Potential additions):
├── Request count
├── Response times
├── Error rates
├── Predictions per category
└── Spam detection rate
```

---

## 13. Development vs Production

### Development
```
Configuration:
├── --reload enabled
├── Hot reload on code changes
├── Debug mode active
├── Detailed error messages
├── CORS: allow all
└── Single worker

Access:
└── http://localhost:8000
```

### Production
```
Configuration:
├── --reload disabled
├── No hot reload
├── Production mode
├── Generic error messages
├── CORS: specific origins
└── Multiple workers

Access:
├── https://api.yourdomain.com
└── Behind reverse proxy (nginx)
```

---

*This architecture document is part of the complete documentation suite. See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for all documents.*

*Last Updated: February 15, 2026*
