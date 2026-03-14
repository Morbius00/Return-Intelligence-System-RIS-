# Technical Summary

## System Type

Customer feedback intelligence API built with FastAPI and classical NLP/ML.

## Model Strategy

The system uses a routed dual-model classifier:
- Negative feedback -> negative model predicts issue_category
- Positive feedback -> positive model predicts satisfaction_category

Each path maps category to a business score:
- severity_score for negative categories
- goodwill_score for positive categories

Neutral sentiment returns no category score fields.

## Processing Pipeline

1. Input validation
2. Spam detection (rule-based)
3. Text preprocessing (NLTK)
4. Sentiment detection using keyword hits and optional rating tiebreaker
5. Route to negative or positive TF-IDF + Logistic Regression model
6. Confidence extraction and response formatting

## Core Libraries

- fastapi, uvicorn
- nltk
- scikit-learn
- pandas
- gspread and google-auth
- python-dotenv
- python-multipart for file upload endpoints

## Training Artifacts

Train script: train.py

Generated model artifacts:
- app/models/neg_model.pkl
- app/models/neg_tfidf.pkl
- app/models/pos_model.pkl
- app/models/pos_tfidf.pkl

Training data source:
- training_data/feedback_training_data.csv

Expected columns:
- customer_feedback
- sentiment
- category

## API Contracts

Single prediction request:
- customer_feedback: string
- rating: optional integer

Single prediction response:
- is_spam: bool
- sentiment_type: Positive | Negative | Neutral
- issue_category: string or null
- severity_score: float or null
- satisfaction_category: string or null
- goodwill_score: float or null
- confidence: float or null

## Category Mappings

Negative categories to severity:
- Product Quality Issue -> 0.9
- Expiry Issue -> 0.9
- Packaging Issue -> 0.6
- Wrong Item -> 0.6
- Customer Preference -> 0.3
- Other -> 0.2
- Uncertain -> 0.1

Positive categories to goodwill:
- Product Appreciation -> 0.9
- Overall Positive Experience -> 0.85
- Service Satisfaction -> 0.8
- Packaging Praise -> 0.7
- General Positive -> 0.6

## Batch Processing

Supported in two modes via batch_processor.py:
- csv: reads CSV or Excel and writes enriched CSV
- sheets: reads and updates Google Sheets

## Deployment

Containerized deployment is supported with:
- Dockerfile
- render.yaml (Render Blueprint)

Health endpoint used for runtime checks:
- GET /health


