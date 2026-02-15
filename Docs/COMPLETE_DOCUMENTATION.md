# NLP Return Reason Classifier - Complete Documentation

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Complete Pipeline Flow](#3-complete-pipeline-flow)
4. [Technology Stack](#4-technology-stack)
5. [Project Structure](#5-project-structure)
6. [Installation & Setup](#6-installation--setup)
7. [Running the System](#7-running-the-system)
8. [Pipeline Processing Details](#8-pipeline-processing-details)
9. [API Documentation](#9-api-documentation)
10. [Google Sheets Integration](#10-google-sheets-integration)
11. [Batch Processing](#11-batch-processing)
12. [Testing Guide](#12-testing-guide)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Project Overview

### 1.1 What is This Project?

The **NLP Return Reason Classifier** is a production-ready, lightweight machine learning system that automatically classifies customer product return reasons into predefined categories. It uses classical NLP techniques and machine learning (no deep learning or LLMs required) to provide fast, accurate, and explainable predictions.

### 1.2 Key Capabilities

- ✅ **Text Classification**: Classifies return reasons into 6 categories
- ✅ **Spam Detection**: Filters out meaningless/spam inputs
- ✅ **Severity Scoring**: Assigns urgency scores (0.0 to 1.0)
- ✅ **REST API**: FastAPI-based HTTP endpoints
- ✅ **Google Sheets Integration**: Real-time sheet updates
- ✅ **Batch Processing**: Process hundreds of records at once
- ✅ **Web Interface**: HTML/JavaScript frontend for testing

### 1.3 Classification Categories

| Category | Severity Score | Description | Examples |
|----------|---------------|-------------|----------|
| **Product Quality Issue** | 0.9 (High) | Defective or broken items | "Item arrived broken", "Poor quality" |
| **Expiry Issue** | 0.9 (High) | Expired products | "Product is expired", "Past expiry date" |
| **Packaging Issue** | 0.6 (Medium) | Damaged packaging | "Package was torn", "Box crushed" |
| **Wrong Item** | 0.6 (Medium) | Incorrect item sent | "Wrong product", "Different color" |
| **Customer Preference** | 0.3 (Low) | Customer changed mind | "Changed my mind", "No longer need" |
| **Other** | 0.2 (Low) | Miscellaneous reasons | Unclassifiable reasons |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Web Browser │  │ REST Client  │  │ Google Sheets│          │
│  │  (HTML/JS)   │  │ (curl/Python)│  │  Integration │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  app/main.py - REST API Endpoints                        │  │
│  │  • POST /predict         - Single prediction              │  │
│  │  • POST /predict/batch   - Batch predictions              │  │
│  │  • POST /sheets/update   - Update Google Sheets           │  │
│  │  • GET  /health          - Health check                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SERVICE LAYER                                │
│  ┌────────────────────┐        ┌────────────────────┐          │
│  │  NLP Classifier     │        │ Sheets Service     │          │
│  │  (classifier.py)    │        │ (sheets_service.py)│          │
│  └────────┬────────────┘        └────────┬───────────┘          │
└───────────┼──────────────────────────────┼──────────────────────┘
            │                              │
            ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │ Spam Detector   │  │  Preprocessor   │  │  TF-IDF +      │ │
│  │ (spam_detector) │  │ (preprocess.py) │  │  Logistic      │ │
│  │                 │  │                 │  │  Regression    │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
            │                              │
            ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │ Trained Models  │  │ Training Data   │  │ Google Sheets  │ │
│  │ • model.pkl     │  │ sample_data.csv │  │  Spreadsheets  │ │
│  │ • tfidf.pkl     │  │                 │  │                │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Breakdown

#### **Frontend Components**
- `index.html`: Web-based testing interface with real-time predictions

#### **Backend Components**
- `app/main.py`: FastAPI application (REST API server)
- `app/nlp/classifier.py`: Main classification logic
- `app/nlp/preprocess.py`: Text preprocessing pipeline
- `app/nlp/spam_detector.py`: Spam detection rules
- `app/services/sheets_service.py`: Google Sheets integration

#### **Training Components**
- `train.py`: Model training script
- `training_data/sample_data.csv`: Labeled training dataset

#### **Batch Processing**
- `batch_processor.py`: CLI tool for batch processing

---

## 3. Complete Pipeline Flow

### 3.1 Single Prediction Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: USER INPUT                                               │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ User submits text: "Item arrived completely broken"          │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: API RECEIVES REQUEST                                     │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ POST /predict                                                 │ │
│ │ {                                                             │ │
│ │   "return_reason": "Item arrived completely broken"          │ │
│ │ }                                                             │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: SPAM DETECTION (First Filter)                            │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Rules Applied:                                               │ │
│ │ • Is text empty or whitespace only? ❌ NO                    │ │
│ │ • Is text too short (< 3 chars)? ❌ NO                        │ │
│ │ • Matches spam phrases ("no reason", "test")? ❌ NO           │ │
│ │ • >70% repeated characters? ❌ NO                             │ │
│ │                                                               │ │
│ │ Result: NOT SPAM ✅ → Continue to preprocessing              │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: TEXT PREPROCESSING PIPELINE                              │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Input: "Item arrived completely broken"                       │ │
│ │                                                               │ │
│ │ Sub-step 4.1: Lowercase                                       │ │
│ │   → "item arrived completely broken"                          │ │
│ │                                                               │ │
│ │ Sub-step 4.2: Remove Punctuation                              │ │
│ │   → "item arrived completely broken"                          │ │
│ │                                                               │ │
│ │ Sub-step 4.3: Remove Numbers                                  │ │
│ │   → "item arrived completely broken"                          │ │
│ │                                                               │ │
│ │ Sub-step 4.4: Tokenization (word_tokenize)                    │ │
│ │   → ["item", "arrived", "completely", "broken"]               │ │
│ │                                                               │ │
│ │ Sub-step 4.5: Remove Stopwords                                │ │
│ │   Stopwords: "completely" is removed                          │ │
│ │   → ["item", "arrived", "broken"]                             │ │
│ │                                                               │ │
│ │ Sub-step 4.6: Lemmatization                                   │ │
│ │   "arrived" → "arrive"                                        │ │
│ │   "broken" → "broken" (already root form)                     │ │
│ │   → ["item", "arrive", "broken"]                              │ │
│ │                                                               │ │
│ │ Sub-step 4.7: Filter Short Tokens (< 2 chars)                 │ │
│ │   → ["item", "arrive", "broken"]                              │ │
│ │                                                               │ │
│ │ Sub-step 4.8: Join Back to String                             │ │
│ │   → "item arrive broken"                                      │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: FEATURE EXTRACTION (TF-IDF)                              │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Input: "item arrive broken"                                   │ │
│ │                                                               │ │
│ │ TF-IDF Vectorizer Parameters:                                 │ │
│ │ • Max Features: 1000                                          │ │
│ │ • N-gram Range: (1, 2) [unigrams + bigrams]                  │ │
│ │ • Min DF: 2 (ignore very rare terms)                          │ │
│ │ • Max DF: 0.8 (ignore very common terms)                      │ │
│ │                                                               │ │
│ │ Extracted Features (example):                                 │ │
│ │ • "item": 0.42                                                │ │
│ │ • "arrive": 0.31                                              │ │
│ │ • "broken": 0.65                                              │ │
│ │ • "item arrive": 0.28 (bigram)                                │ │
│ │ • "arrive broken": 0.53 (bigram)                              │ │
│ │ • ... (995 more features as zeros)                            │ │
│ │                                                               │ │
│ │ Output: 1000-dimensional sparse vector                        │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: CLASSIFICATION (Logistic Regression)                     │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Model: Logistic Regression (One-vs-Rest)                      │ │
│ │ • 6 binary classifiers (one per category)                     │ │
│ │                                                               │ │
│ │ Input: 1000-dimensional TF-IDF vector                         │ │
│ │                                                               │ │
│ │ Computation:                                                  │ │
│ │ For each category:                                            │ │
│ │   probability = sigmoid(weights · features + bias)            │ │
│ │                                                               │ │
│ │ Probability Scores:                                           │ │
│ │ • Product Quality Issue: 0.87  ← HIGHEST ✅                   │ │
│ │ • Expiry Issue: 0.04                                          │ │
│ │ • Packaging Issue: 0.18                                       │ │
│ │ • Wrong Item: 0.05                                            │ │
│ │ • Customer Preference: 0.02                                   │ │
│ │ • Other: 0.01                                                 │ │
│ │                                                               │ │
│ │ Predicted Category: "Product Quality Issue"                   │ │
│ │ Confidence Score: 0.87                                        │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 7: SEVERITY MAPPING                                         │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Severity Map (Hardcoded):                                     │ │
│ │ {                                                             │ │
│ │   "Product Quality Issue": 0.9,  ← Selected                   │ │
│ │   "Expiry Issue": 0.9,                                        │ │
│ │   "Packaging Issue": 0.6,                                     │ │
│ │   "Wrong Item": 0.6,                                          │ │
│ │   "Customer Preference": 0.3,                                 │ │
│ │   "Other": 0.2                                                │ │
│ │ }                                                             │ │
│ │                                                               │ │
│ │ Severity Score: 0.9 (High Priority)                           │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 8: RESPONSE FORMATTING                                      │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ {                                                             │ │
│ │   "is_spam": false,                                           │ │
│ │   "reason_category": "Product Quality Issue",                 │ │
│ │   "severity_score": 0.9,                                      │ │
│ │   "confidence": 0.87                                          │ │
│ │ }                                                             │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 9: RETURN TO CLIENT                                         │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ HTTP 200 OK                                                   │ │
│ │ JSON Response sent back to client                             │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Batch Processing Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ INPUT: CSV File or Google Sheet                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Order ID  | Customer | Return Reason                         │ │
│ │ ORD001    | John     | Item arrived broken                   │ │
│ │ ORD002    | Sarah    | Wrong color sent                      │ │
│ │ ORD003    | Mike     | no reason                             │ │
│ │ ...       | ...      | ...                                   │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ LOAD DATA                                                         │
│ • Read CSV with pandas OR                                         │
│ • Read Google Sheet with gspread                                  │
│ Extract "return_reason" column                                    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ LOOP: Process Each Row                                            │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ For each return reason:                                       │ │
│ │   1. Spam detection                                           │ │
│ │   2. Text preprocessing                                       │ │
│ │   3. TF-IDF vectorization                                     │ │
│ │   4. Classification                                           │ │
│ │   5. Severity mapping                                         │ │
│ │                                                               │ │
│ │ (Same pipeline as single prediction)                          │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ COLLECT RESULTS                                                   │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Order ID  | Reason Category         | Severity | Is Spam     │ │
│ │ ORD001    | Product Quality Issue   | 0.9      | False       │ │
│ │ ORD002    | Wrong Item              | 0.6      | False       │ │
│ │ ORD003    | Other                   | 0.0      | True        │ │
│ │ ...       | ...                     | ...      | ...         │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ OUTPUT: Write Results                                             │
│ • Write to new CSV file OR                                        │
│ • Append new columns to Google Sheet                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Technology Stack

### 4.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Primary programming language |
| **Web Framework** | FastAPI | 0.109.0+ | REST API server |
| **Server** | Uvicorn | 0.27.0+ | ASGI server for FastAPI |
| **NLP Library** | NLTK | 3.8.1+ | Text preprocessing |
| **ML Framework** | scikit-learn | 1.4.0+ | TF-IDF, Logistic Regression |
| **Data Processing** | pandas | 2.2.0+ | Data manipulation |
| **Google Sheets** | gspread | 5.12.4+ | Sheets API client |
| **Serialization** | joblib | 1.3.2+ | Model persistence |
| **Environment** | python-dotenv | 1.0.1+ | Environment variables |

### 4.2 Machine Learning Components

- **Text Preprocessing**: NLTK (tokenization, stopwords, lemmatization)
- **Feature Extraction**: TF-IDF (Term Frequency-Inverse Document Frequency)
- **Classification Algorithm**: Logistic Regression (One-vs-Rest)
- **Model Storage**: Pickle/Joblib serialization

### 4.3 Why These Technologies?

**FastAPI**:
- Fast, modern, automatic API documentation
- Type validation with Pydantic
- Async support for high performance

**NLTK**:
- Mature, well-tested NLP library
- Lightweight compared to spaCy
- Sufficient for classical NLP tasks

**Logistic Regression**:
- Fast inference (sub-millisecond)
- Interpretable results
- Native probability estimates
- Small model size (~500KB)

---

## 5. Project Structure

```
d:\My Projects\NLP-Project/
│
├── 📁 app/                          # Main application package
│   ├── __init__.py                  # Package initializer
│   ├── main.py                      # FastAPI application (REST API)
│   │
│   ├── 📁 nlp/                      # NLP processing modules
│   │   ├── __init__.py              # Exports: preprocess_text, is_spam, NLPClassifier
│   │   ├── preprocess.py            # Text preprocessing pipeline
│   │   ├── spam_detector.py         # Spam detection rules
│   │   └── classifier.py            # TF-IDF + Logistic Regression classifier
│   │
│   ├── 📁 services/                 # External service integrations
│   │   ├── __init__.py
│   │   └── sheets_service.py        # Google Sheets integration
│   │
│   └── 📁 models/                   # Trained model storage
│       ├── model.pkl                # Trained Logistic Regression model
│       └── tfidf.pkl                # Trained TF-IDF vectorizer
│
├── 📁 training_data/                # Training datasets
│   ├── sample_data.csv              # Labeled training data (reason, category)
│   └── test_input.csv               # Test data for batch processing
│
├── 📁 credentials/                  # Google API credentials (gitignored)
│   └── nlp-returns-classifier-*.json
│
├── 📄 train.py                      # Model training script
├── 📄 batch_processor.py            # CLI tool for batch processing
├── 📄 start_server.py               # Server startup script
│
├── 📄 index.html                    # Web-based testing interface
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 setup.ps1                     # Automated setup script (Windows)
├── 📄 run_api.ps1                   # API startup script (Windows)
│
├── 📄 .env                          # Environment variables (local config)
├── 📄 .gitignore                    # Git ignore rules
│
├── 📄 README.md                     # Quick start guide
├── 📄 PROJECT_OVERVIEW.md           # High-level overview
├── 📄 TECHNICAL_SUMMARY.md          # Technical details
├── 📄 GETTING_STARTED_WINDOWS.md    # Windows setup guide
├── 📄 GOOGLE_SHEETS_SETUP.md        # Google Sheets setup guide
├── 📄 RUN_SERVER_AND_API.md         # Server running instructions
└── 📄 COMPLETE_DOCUMENTATION.md     # This file
```

### 5.1 Key Files Explained

#### **Core Application**

**`app/main.py`** (API Server)
- FastAPI application initialization
- CORS middleware configuration
- API endpoint definitions:
  - `POST /predict` - Single prediction
  - `POST /predict/batch` - Batch predictions
  - `POST /sheets/update` - Update Google Sheets
  - `GET /health` - Health check
- Model and service initialization on startup

**`app/nlp/classifier.py`** (Main Classifier)
- `NLPClassifier` class
- Training method with train/test split
- Single prediction (`predict()`)
- Batch prediction (`predict_batch()`)
- Model loading and saving
- Confidence threshold handling

**`app/nlp/preprocess.py`** (Text Preprocessing)
- `preprocess_text()` - Main preprocessing function
- Lowercase conversion
- Punctuation removal
- Number removal
- Tokenization (NLTK)
- Stopword removal (English)
- Lemmatization (WordNet)
- Token filtering

**`app/nlp/spam_detector.py`** (Spam Detection)
- `is_spam()` - Main spam detection function
- Rule-based pattern matching
- Empty/whitespace detection
- Length-based filtering
- Character repetition detection

**`app/services/sheets_service.py`** (Google Sheets)
- `GoogleSheetsService` class
- Service account authentication
- Read Google Sheets to DataFrame
- Write DataFrame to Google Sheets
- Batch update operations

#### **Scripts**

**`train.py`** (Model Training)
- Load training data from CSV
- Validate categories
- Train TF-IDF vectorizer and classifier
- Evaluate on test set
- Save trained models to disk
- Display classification report

**`batch_processor.py`** (Batch Processing)
- `BatchProcessor` class
- Process Google Sheets
- Process local CSV files
- Append classification results
- Generate statistics and logs

**`start_server.py`** (Server Startup)
- Load environment variables
- Start Uvicorn server
- Configure host, port, reload settings

#### **Frontend**

**`index.html`** (Web Interface)
- Single prediction form
- Batch prediction form
- File upload support
- Real-time results display
- Category information
- Styled with modern CSS

---

## 6. Installation & Setup

### 6.1 Prerequisites

Before installation, ensure you have:

- **Operating System**: Windows 10/11, Linux, or macOS
- **Python**: Version 3.11 or higher
- **Internet Connection**: For downloading packages
- **Git** (optional): For version control
- **Google Account** (optional): For Sheets integration

### 6.2 Installation Methods

#### **Method 1: Automated Setup (Windows - Recommended)**

```powershell
# Navigate to project directory
cd "d:\My Projects\NLP-Project"

# Run automated setup script
.\setup.ps1
```

This script will:
1. Create virtual environment
2. Install all dependencies
3. Download NLTK resources
4. Train the model
5. Create .env file

#### **Method 2: Manual Setup (All Platforms)**

##### Step 1: Navigate to Project Directory

```bash
cd "d:\My Projects\NLP-Project"
```

##### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Verify creation
ls .venv  # Should show Scripts/ (Windows) or bin/ (Linux/Mac)
```

##### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

You should see `(.venv)` prefix in your terminal.

##### Step 4: Upgrade pip

```bash
python -m pip install --upgrade pip
```

##### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `nltk` - NLP library
- `scikit-learn` - ML library
- `pandas` - Data processing
- `gspread` - Google Sheets
- And more...

##### Step 6: Download NLTK Resources

```python
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('averaged_perceptron_tagger')"
```

##### Step 7: Train the Model

```bash
python train.py
```

Expected output:
```
Loading training data from: training_data\sample_data.csv
Loaded 150 training samples
Preprocessing texts...
Training TF-IDF vectorizer...
Training Logistic Regression model...
Training complete. Accuracy: 0.9333

Classification Report:
              precision    recall  f1-score   support
...

Saving model to: app\models\model.pkl
Saving vectorizer to: app\models\tfidf.pkl
✓ Model trained and saved successfully!
```

##### Step 8: Create Environment File

```bash
# Copy example file
cp .env.example .env

# Edit .env file (optional - for Google Sheets)
# GOOGLE_CREDENTIALS_PATH=./credentials/your-credentials.json
```

### 6.3 Verify Installation

```bash
# Check Python version
python --version
# Expected: Python 3.11.x or higher

# Check installed packages
pip list

# Verify model files exist
ls app/models/
# Should show: model.pkl, tfidf.pkl
```

---

## 7. Running the System

### 7.1 Starting the Backend Server

#### **Option 1: Using Start Script**

```powershell
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Run the server
python start_server.py
```

#### **Option 2: Using Uvicorn Directly**

```powershell
# Activate venv first
.\.venv\Scripts\Activate.ps1

# Start server with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **Option 3: Using PowerShell Script**

```powershell
.\run_api.ps1
```

#### **Server Output**

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Loading trained model...
INFO:     Model loaded successfully
INFO:     Google Sheets service initialized successfully
INFO:     Application startup complete.
```

### 7.2 Accessing the API

Once the server is running:

- **Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health

### 7.3 Opening the Frontend

#### **Method 1: Simple HTTP Server**

```powershell
# In a new terminal (keep API server running)
python -m http.server 8080
```

Then open: http://localhost:8080/index.html

#### **Method 2: Direct File Open**

Simply open `index.html` in your web browser.

**Note**: Update the API URL in the JavaScript section if needed:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### 7.4 Stopping the Server

Press `CTRL+C` in the terminal running the server.

---

## 8. Pipeline Processing Details

### 8.1 Stage-by-Stage Breakdown

#### **Stage 1: Input Reception**

**What Happens:**
- API receives HTTP POST request
- FastAPI validates JSON schema with Pydantic
- Extracts `return_reason` field

**Example:**
```json
{
  "return_reason": "Product expired before delivery"
}
```

**Technical Details:**
- File: `app/main.py`
- Function: `predict(request: PredictionRequest)`
- Validation: Pydantic model ensures `return_reason` is a string

---

#### **Stage 2: Spam Detection**

**What Happens:**
- First line of defense before expensive processing
- Rule-based pattern matching
- Fast O(1) operations

**Rules Applied:**
1. **Empty Check**: Is text empty or whitespace only?
2. **Length Check**: Is text < 3 characters?
3. **Exact Match**: Does text exactly match spam phrases?
4. **Substring Match**: Does text contain spam keywords?
5. **Repetition Check**: Is >70% the same character?

**Spam Patterns:**
```python
# Exact matches
{"no reason", "none", "n/a", "test", ".", "..."}

# Substrings
{"zzz", "asdf", "qwerty", "testing"}
```

**Example Flow:**
```python
Input: "no reason"
↓
is_exact_spam_match("no reason")?  → YES
↓
Return: is_spam = True
↓
Skip further processing
↓
Return: {
    "is_spam": True,
    "reason_category": "Other",
    "severity_score": 0.0
}
```

**Technical Details:**
- File: `app/nlp/spam_detector.py`
- Function: `is_spam(text: str) -> bool`
- Time Complexity: O(1) to O(n) where n is text length

---

#### **Stage 3: Text Preprocessing**

**What Happens:**
- Converts raw text to clean, normalized format
- Reduces vocabulary and noise
- Prepares text for machine learning

**Sub-stages:**

**3.1 Lowercase Conversion**
```python
Input:  "Item Arrived BROKEN"
Output: "item arrived broken"
```

**3.2 Punctuation Removal**
```python
Input:  "item arrived broken!"
Output: "item arrived broken"
Method: str.translate() with string.punctuation
```

**3.3 Number Removal**
```python
Input:  "order 12345 was broken"
Output: "order  was broken"
Regex:  r"\b\d+\b"
```

**3.4 Tokenization**
```python
Input:  "item arrived broken"
Output: ["item", "arrived", "broken"]
Method: nltk.word_tokenize()
```

**3.5 Stopword Removal**
```python
Input:  ["item", "arrived", "broken"]
Stopwords: {"arrived", "the", "is", "was", ...}
Output: ["item", "broken"]
```

**3.6 Lemmatization**
```python
Input:  ["item", "broken", "arriving", "packages"]
Process:
  - "item" → "item" (no change)
  - "broken" → "broken" (already root form)
  - "arriving" → "arrive"
  - "packages" → "package"
Output: ["item", "broken", "arrive", "package"]
Method: nltk.WordNetLemmatizer()
```

**3.7 Short Token Filtering**
```python
Input:  ["item", "broken", "a", "i"]
Filter: Keep only tokens with length >= 2
Output: ["item", "broken"]
```

**3.8 Join to String**
```python
Input:  ["item", "broken"]
Output: "item broken"
Method: " ".join(tokens)
```

**Complete Example:**
```
Original: "The item arrived completely broken and unusable!"
↓
Lowercase: "the item arrived completely broken and unusable!"
↓
Remove punctuation: "the item arrived completely broken and unusable"
↓
Tokenize: ["the", "item", "arrived", "completely", "broken", "and", "unusable"]
↓
Remove stopwords: ["item", "arrived", "broken", "unusable"]
↓
Lemmatize: ["item", "arrive", "broken", "unusable"]
↓
Join: "item arrive broken unusable"
```

**Technical Details:**
- File: `app/nlp/preprocess.py`
- Function: `preprocess_text(text: str) -> str`
- Time Complexity: O(n) where n is text length

---

#### **Stage 4: Feature Extraction (TF-IDF)**

**What Happens:**
- Converts preprocessed text to numerical vector
- Uses Term Frequency-Inverse Document Frequency
- Creates sparse 1000-dimensional vector

**TF-IDF Parameters:**
```python
TfidfVectorizer(
    max_features=1000,      # Keep top 1000 features
    ngram_range=(1, 2),     # Unigrams and bigrams
    min_df=2,               # Ignore terms in < 2 documents
    max_df=0.8              # Ignore terms in > 80% documents
)
```

**How TF-IDF Works:**

**TF (Term Frequency):**
```
TF(t, d) = (Count of term t in document d) / (Total terms in d)
```

**IDF (Inverse Document Frequency):**
```
IDF(t) = log(Total documents / Documents containing term t)
```

**TF-IDF Score:**
```
TF-IDF(t, d) = TF(t, d) × IDF(t)
```

**Example:**

Input: `"item broken"`

**Generated Features:**
```
Unigrams:
- "item": 0.42
- "broken": 0.65

Bigrams:
- "item broken": 0.58

All other features (997): 0.0
```

**Result:** `[0.42, 0.65, 0.58, 0, 0, 0, ..., 0]` (1000 values)

**Why TF-IDF?**
- Captures word importance
- Penalizes common words (e.g., "product", "order")
- Rewards distinctive words (e.g., "broken", "expired")
- Fast computation and inference

**Technical Details:**
- File: `app/nlp/classifier.py`
- Object: `self.vectorizer.transform([text])`
- Output Shape: (1, 1000) sparse matrix

---

#### **Stage 5: Classification**

**What Happens:**
- 1000-D vector passed to Logistic Regression model
- Model computes probability for each category
- Category with highest probability is selected

**Algorithm: Logistic Regression (One-vs-Rest)**

**Model Structure:**
```
6 binary classifiers:
1. Product Quality Issue vs. All Others
2. Expiry Issue vs. All Others
3. Packaging Issue vs. All Others
4. Wrong Item vs. All Others
5. Customer Preference vs. All Others
6. Other vs. All Others
```

**Mathematical Formula:**
```
For each category i:
  z_i = w_i · x + b_i
  probability_i = sigmoid(z_i) = 1 / (1 + e^(-z_i))

Predicted category = argmax(probability)
```

Where:
- `w_i` = learned weights for category i
- `x` = TF-IDF feature vector
- `b_i` = bias term for category i

**Example Computation:**

Input Vector: `[0.42, 0.65, 0.58, ...]` (1000 values)

**Step 1: Compute logits**
```
For "Product Quality Issue":
  z = (0.42×w1) + (0.65×w2) + ... + bias
  z = 2.3

For "Expiry Issue":
  z = -1.5

For "Packaging Issue":
  z = 0.8
...
```

**Step 2: Apply sigmoid**
```
P(Product Quality) = 1 / (1 + e^(-2.3)) = 0.909
P(Expiry Issue) = 1 / (1 + e^(1.5)) = 0.182
P(Packaging Issue) = 1 / (1 + e^(-0.8)) = 0.689
P(Wrong Item) = 0.156
P(Customer Preference) = 0.045
P(Other) = 0.023
```

**Step 3: Normalize (softmax)**
```
Sum = 0.909 + 0.182 + 0.689 + 0.156 + 0.045 + 0.023 = 2.004

P(Product Quality) = 0.909 / 2.004 = 0.454 → Renormalized
```

**Step 4: Select winner**
```
Predicted Category: "Product Quality Issue"
Confidence: 0.87 (max probability)
```

**Confidence Threshold Check:**
```python
if confidence < 0.4:
    return "Uncertain" category
```

**Technical Details:**
- File: `app/nlp/classifier.py`
- Method: `self.model.predict(X)` and `self.model.predict_proba(X)`
- Time: ~0.3 milliseconds

---

#### **Stage 6: Severity Mapping**

**What Happens:**
- Predicted category is mapped to predefined severity score
- Simple dictionary lookup
- Business rule-based assignment

**Severity Map:**
```python
SEVERITY_MAP = {
    "Product Quality Issue": 0.9,   # Critical - defective product
    "Expiry Issue": 0.9,            # Critical - health/safety
    "Packaging Issue": 0.6,         # Medium - cosmetic damage
    "Wrong Item": 0.6,              # Medium - fulfillment error
    "Customer Preference": 0.3,     # Low - buyer's remorse
    "Other": 0.2,                   # Low - miscellaneous
    "Uncertain": 0.1                # Very low - unclear
}
```

**Example:**
```python
predicted_category = "Product Quality Issue"
severity_score = SEVERITY_MAP[predicted_category]
# severity_score = 0.9
```

**Business Interpretation:**
- **0.9-1.0**: High priority - immediate action required
- **0.6-0.8**: Medium priority - investigate within 24 hours
- **0.3-0.5**: Low priority - standard processing
- **0.0-0.2**: Very low priority - minimal action

**Technical Details:**
- File: `app/nlp/classifier.py`
- Variable: `SEVERITY_MAP`
- Time: O(1) dictionary lookup

---

#### **Stage 7: Response Formatting**

**What Happens:**
- Collect all results
- Format as JSON
- Add metadata

**Response Structure:**
```json
{
    "is_spam": false,
    "reason_category": "Product Quality Issue",
    "severity_score": 0.9,
    "confidence": 0.87
}
```

**Field Descriptions:**
- `is_spam` (bool): Whether input was detected as spam
- `reason_category` (str): Predicted category name
- `severity_score` (float): Urgency score 0.0-1.0
- `confidence` (float): Model confidence 0.0-1.0 (optional)

**Technical Details:**
- File: `app/main.py`
- Model: `PredictionResponse` (Pydantic)
- Serialization: Automatic JSON conversion by FastAPI

---

#### **Stage 8: HTTP Response**

**What Happens:**
- FastAPI serializes response to JSON
- Adds HTTP headers
- Sends response to client

**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 123

{
    "is_spam": false,
    "reason_category": "Product Quality Issue",
    "severity_score": 0.9,
    "confidence": 0.87
}
```

---

### 8.2 Performance Metrics

| Stage | Time (ms) | Description |
|-------|-----------|-------------|
| Input Reception | <1 | HTTP parsing, validation |
| Spam Detection | <1 | Rule-based checks |
| Preprocessing | 2-5 | NLTK operations |
| TF-IDF | 1-2 | Vectorization |
| Classification | <1 | Logistic Regression |
| Severity Mapping | <1 | Dictionary lookup |
| Response | <1 | JSON serialization |
| **Total** | **5-10ms** | **End-to-end** |

---

## 9. API Documentation

### 9.1 Base URL

```
Local: http://localhost:8000
```

### 9.2 Endpoints

#### **GET /**

**Description**: Root endpoint with API information

**Response:**
```json
{
    "message": "NLP Return Reason Classifier API",
    "version": "1.0.0",
    "docs": "/docs",
    "health": "/health"
}
```

---

#### **GET /health**

**Description**: Health check endpoint

**Response:**
```json
{
    "status": "healthy",
    "model_loaded": true,
    "version": "1.0.0"
}
```

---

#### **POST /predict**

**Description**: Classify a single return reason

**Request Body:**
```json
{
    "return_reason": "item arrived broken"
}
```

**Response:**
```json
{
    "is_spam": false,
    "reason_category": "Product Quality Issue",
    "severity_score": 0.9,
    "confidence": 0.87
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"return_reason": "item arrived broken"}'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={"return_reason": "item arrived broken"}
)
print(response.json())
```

**PowerShell Example:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"return_reason": "item arrived broken"}'
```

---

#### **POST /predict/batch**

**Description**: Classify multiple return reasons

**Request Body:**
```json
{
    "return_reasons": [
        "item arrived broken",
        "wrong product sent",
        "no reason"
    ]
}
```

**Response:**
```json
{
    "predictions": [
        {
            "is_spam": false,
            "reason_category": "Product Quality Issue",
            "severity_score": 0.9,
            "confidence": 0.87
        },
        {
            "is_spam": false,
            "reason_category": "Wrong Item",
            "severity_score": 0.6,
            "confidence": 0.92
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

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "return_reasons": [
        "item arrived broken",
        "wrong product sent"
    ]
  }'
```

---

#### **POST /sheets/update** (Requires Google Sheets Setup)

**Description**: Update Google Sheets with classification results

**Request Body:**
```json
{
    "spreadsheet_id": "1ABC123xyz...",
    "worksheet_name": "Returns",
    "data": [
        {"order_id": "ORD001", "reason": "item arrived broken"},
        {"order_id": "ORD002", "reason": "wrong size"}
    ]
}
```

**Response:**
```json
{
    "success": true,
    "rows_processed": 2,
    "message": "Successfully updated 2 rows",
    "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1ABC123xyz..."
}
```

---

### 9.3 Error Responses

**Model Not Loaded (503):**
```json
{
    "detail": "Model not loaded. Please train the model first."
}
```

**Invalid Request (422):**
```json
{
    "detail": [
        {
            "loc": ["body", "return_reason"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

**Internal Server Error (500):**
```json
{
    "detail": "Prediction failed: <error message>"
}
```

---

## 10. Google Sheets Integration

### 10.1 Overview

The system can read from and write to Google Sheets, enabling:
- Automated batch processing
- Real-time result updates
- Collaborative data analysis
- No manual CSV imports/exports

### 10.2 Setup Process

#### **Step 1: Create Google Cloud Project**

1. Go to https://console.cloud.google.com
2. Click **Select Project** → **New Project**
3. Enter name: "NLP-Returns-Classifier"
4. Click **Create**

#### **Step 2: Enable APIs**

1. Navigate to **APIs & Services** → **Library**
2. Search and enable:
   - **Google Sheets API**
   - **Google Drive API**

#### **Step 3: Create Service Account**

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **Service account**
3. Name: "nlp-sheets-service"
4. Click **Create and Continue**
5. Click **Done**

#### **Step 4: Generate Credentials**

1. Click on the service account
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON**
5. Click **Create** (file downloads automatically)

#### **Step 5: Store Credentials**

```powershell
# Create credentials folder
mkdir credentials

# Move downloaded JSON file
mv ~/Downloads/nlp-returns-classifier-*.json ./credentials/service_account.json

# Add to .gitignore
echo "credentials/" >> .gitignore
```

#### **Step 6: Configure Environment**

Edit `.env` file:
```env
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
```

#### **Step 7: Share Sheet with Service Account**

1. Open the JSON file and copy `client_email`
   ```
   Example: nlp-sheets-service@project.iam.gserviceaccount.com
   ```
2. Open your Google Sheet
3. Click **Share** (top right)
4. Paste the service account email
5. Give **Editor** permissions
6. Uncheck "Notify people"
7. Click **Share**

### 10.3 Usage

#### **Using API Endpoint**

```python
import requests

response = requests.post(
    "http://localhost:8000/sheets/update",
    json={
        "spreadsheet_id": "1ABC123xyz...",
        "worksheet_name": "Returns",
        "data": [
            {"order_id": "ORD001", "reason": "item broken"},
            {"order_id": "ORD002", "reason": "wrong item"}
        ]
    }
)
print(response.json())
```

#### **Using Batch Processor**

```powershell
python batch_processor.py \
    --mode sheets \
    --spreadsheet-id "1ABC123xyz..." \
    --worksheet-name "Returns"
```

### 10.4 Sheet Format

**Input Sheet:**
| Order ID | Customer Name | Return Reason |
|----------|--------------|---------------|
| ORD001 | John Doe | Item arrived broken |
| ORD002 | Jane Smith | Wrong color |

**After Processing:**
| Order ID | Customer Name | Return Reason | Reason Category | Severity Score | Is Spam |
|----------|--------------|---------------|----------------|----------------|---------|
| ORD001 | John Doe | Item arrived broken | Product Quality Issue | 0.9 | FALSE |
| ORD002 | Jane Smith | Wrong color | Wrong Item | 0.6 | FALSE |

---

## 11. Batch Processing

### 11.1 Overview

Batch processing allows you to classify hundreds or thousands of return reasons in a single operation.

### 11.2 Local CSV Processing

#### **Input CSV Format**

`input.csv`:
```csv
order_id,customer_name,return_reason
ORD001,John Doe,Item arrived broken
ORD002,Jane Smith,Wrong product sent
ORD003,Bob Johnson,no reason
```

#### **Command**

```powershell
python batch_processor.py \
    --mode csv \
    --csv-input "training_data/test_input.csv" \
    --csv-output "results.csv"
```

#### **Output CSV**

`results.csv`:
```csv
order_id,customer_name,return_reason,reason_category,severity_score,is_spam
ORD001,John Doe,Item arrived broken,Product Quality Issue,0.9,False
ORD002,Jane Smith,Wrong product sent,Wrong Item,0.6,False
ORD003,Bob Johnson,no reason,Other,0.0,True
```

### 11.3 Google Sheets Processing

#### **Command**

```powershell
python batch_processor.py \
    --mode sheets \
    --spreadsheet-id "1ABC123xyz..." \
    --worksheet-name "Returns" \
    --reason-column "return_reason"
```

#### **Options**

- `--mode`: "csv" or "sheets"
- `--csv-input`: Path to input CSV
- `--csv-output`: Path to output CSV
- `--spreadsheet-id`: Google Sheets ID
- `--worksheet-name`: Sheet name (default: first sheet)
- `--reason-column`: Column name containing reasons

### 11.4 Performance

- **Speed**: ~100-200 predictions/second
- **Memory**: Processes in chunks to handle large datasets
- **Logging**: Real-time progress updates

---

## 12. Testing Guide

### 12.1 Unit Testing

```powershell
# Run all tests
pytest

# Run specific test file
pytest tests/test_classifier.py

# Run with coverage
pytest --cov=app tests/
```

### 12.2 Manual Testing

#### **Test Preprocessing**

```python
python -c "from app.nlp import preprocess_text; print(preprocess_text('Item ARRIVED broken!!'))"
# Expected: "item arrive broken"
```

#### **Test Spam Detection**

```python
python -c "from app.nlp import is_spam; print(is_spam('no reason'))"
# Expected: True
```

#### **Test API**

```powershell
# Health check
 curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"return_reason": "item broken"}'
```

### 12.3 Test Scripts

**`test_api.py`**
```powershell
python test_api.py
```

Tests all API endpoints with various inputs.

**`test_process_sheet.py`**
```powershell
python test_process_sheet.py
```

Tests Google Sheets integration (requires credentials).

---

## 13. Troubleshooting

### 13.1 Common Issues

#### **Port Already in Use**

**Error:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution:**
```powershell
# Use different port
python -m uvicorn app.main:app --reload --port 8001

# Or kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### **Model Not Found**

**Error:**
```
Model files not found at app\models
```

**Solution:**
```powershell
# Train the model
python train.py
```

#### **NLTK Resources Missing**

**Error:**
```
LookupError: Resource punkt not found
```

**Solution:**
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

#### **Virtual Environment Not Activating**

**Error:**
```
Activate.ps1 cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Google Sheets Authentication Failed**

**Error:**
```
FileNotFoundError: Credentials file not found
```

**Solution:**
1. Verify credentials path in `.env`
2. Check file exists: `ls credentials/`
3. Verify JSON format is valid

#### **Import Errors**

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt
```

---

## 14. Appendix

### 14.1 Configuration Files

**`.env` (Environment Variables)**
```env
# Google Sheets Integration
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json

# API Configuration (optional)
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

**`.gitignore`**
```
# Virtual Environment
.venv/
venv/

# Python
__pycache__/
*.pyc
*.pyo

# Models
app/models/*.pkl

# Credentials
credentials/
*.json

# Environment
.env

# Outputs
results.csv
*.log
```

### 14.2 Training Data Format

`training_data/sample_data.csv`:
```csv
return_reason,category
Item arrived broken and damaged,Product Quality Issue
Wrong product was shipped,Wrong Item
Product is expired,Expiry Issue
Changed my mind,Customer Preference
Box was crushed during shipping,Packaging Issue
Late delivery,Other
```

### 14.3 Dependencies

See `requirements.txt` for full list:
- `fastapi>=0.109.0`
- `uvicorn[standard]>=0.27.0`
- `nltk>=3.8.1`
- `scikit-learn>=1.4.0`
- `pandas>=2.2.0`
- `gspread>=5.12.4`
- `python-dotenv>=1.0.1`

---

## 15. Conclusion

This documentation provides a complete guide to the NLP Return Reason Classifier project. You should now be able to:

✅ Understand the project architecture
✅ Set up the development environment
✅ Train and deploy models
✅ Run the API server and frontend
✅ Use batch processing
✅ Integrate with Google Sheets
✅ Troubleshoot common issues

For additional help:
- Check README.md for quick start
- See PROJECT_OVERVIEW.md for high-level details
- Read TECHNICAL_SUMMARY.md for ML details

**Project Repository**: https://github.com/Morbius00/Return-Intelligence-System-RIS-

---

*Last Updated: February 15, 2026*
