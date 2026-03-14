# Architecture Details

## Runtime Components

- API layer: app/main.py (FastAPI)
- NLP core: app/nlp/preprocess.py, app/nlp/spam_detector.py, app/nlp/classifier.py
- Integrations: app/services/sheets_service.py
- Training entrypoint: train.py
- Batch CLI: batch_processor.py

## Model Architecture

The classifier module uses a dual-submodel architecture:
- Negative submodel:
  - TF-IDF vectorizer (neg_tfidf.pkl)
  - Logistic Regression model (neg_model.pkl)
  - Output category mapped to severity_score
- Positive submodel:
  - TF-IDF vectorizer (pos_tfidf.pkl)
  - Logistic Regression model (pos_model.pkl)
  - Output category mapped to goodwill_score

Alias used by API code:
- NLPClassifier = FeedbackClassifier

## Inference Pipeline Internals

1. Validate input
2. is_spam(text) short-circuit
3. preprocess_text(text)
4. detect_sentiment(text, rating)
5. Route by sentiment:
   - Negative: negative vectorizer/model path
   - Positive: positive vectorizer/model path
   - Neutral: no category scoring
6. Attach confidence and output fields

## API Startup Behavior

On startup, app/main.py:
- Loads environment variables
- Loads both negative and positive model artifacts
- Initializes GoogleSheetsService when GOOGLE_CREDENTIALS_PATH is valid

If model files are missing:
- /health reports model_not_loaded
- prediction endpoints return HTTP 503

## Output Contract

Prediction outputs include:
- is_spam
- sentiment_type
- issue_category
- severity_score
- satisfaction_category
- goodwill_score
- confidence

## File Processing Contract

/predict/file expects:
- CSV or Excel upload
- Required feedback column: Customer_Feedback (case-insensitive)
- Optional rating column: any column with rating in header

Returned file includes enriched columns:
- 1. Sentiment
- 2. Issue_Category
- 3. Severity_Score
- 4. Satisfaction_Category
- 5. Goodwill_Score
- 6. Confidence
- 7. Spam

## Sheets Enrichment Columns

/sheets/process writes these columns:
- sentiment_type
- issue_category
- severity_score
- satisfaction_category
- goodwill_score
- confidence
- is_spam
- processed_at

## Deployment Artifacts

- Dockerfile: container runtime image
- .dockerignore: build context pruning
- build_docker_image.ps1: local image build helper
- render.yaml: Render Blueprint with auto deploy


