"""
FastAPI application for NLP-based return reason classification.
Provides REST API endpoints for text classification and batch processing.
"""
import os
import logging
import io
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import uvicorn
import pandas as pd
from dotenv import load_dotenv

from app.nlp import NLPClassifier, is_spam, preprocess_text
from app.services.sheets_service import GoogleSheetsService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Feedback Intelligence API",
    description=(
        "NLP system that classifies customer feedback into Positive / Negative / Neutral sentiment, "
        "assigns issue categories with Severity Scores for negative feedback, "
        "and satisfaction categories with Goodwill Scores for positive feedback."
    ),
    version="2.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Model paths
MODEL_DIR           = Path(__file__).parent / "models"
NEG_MODEL_PATH      = MODEL_DIR / "neg_model.pkl"
NEG_VECTORIZER_PATH = MODEL_DIR / "neg_tfidf.pkl"
POS_MODEL_PATH      = MODEL_DIR / "pos_model.pkl"
POS_VECTORIZER_PATH = MODEL_DIR / "pos_tfidf.pkl"
TRAINING_DATA_PATH  = Path(__file__).parent.parent / "training_data" / "feedback_training_data.csv"

# Global classifier instance
classifier: Optional[NLPClassifier] = None

# Global Google Sheets service instance
sheets_service: Optional[GoogleSheetsService] = None


def _load_classifier_from_disk() -> Optional[NLPClassifier]:
    """Load persisted classifier artefacts if all required files are present."""
    neg_ok = NEG_MODEL_PATH.exists() and NEG_VECTORIZER_PATH.exists()
    pos_ok = POS_MODEL_PATH.exists() and POS_VECTORIZER_PATH.exists()

    if not (neg_ok and pos_ok):
        return None

    logger.info("Loading trained feedback classifier models...")
    return NLPClassifier(
        neg_model_path=str(NEG_MODEL_PATH),
        neg_vectorizer_path=str(NEG_VECTORIZER_PATH),
        pos_model_path=str(POS_MODEL_PATH),
        pos_vectorizer_path=str(POS_VECTORIZER_PATH),
    )


def _train_models_from_csv() -> bool:
    """Train and persist models from training CSV when artefacts are missing."""
    if not TRAINING_DATA_PATH.exists():
        logger.warning(f"Training data not found at {TRAINING_DATA_PATH}")
        return False

    try:
        # Import lazily to avoid startup overhead when models already exist.
        from train import load_training_data, validate_categories, train_model

        logger.info(f"Model artefacts missing. Training from {TRAINING_DATA_PATH}...")
        texts, sentiments, categories = load_training_data(TRAINING_DATA_PATH)
        validate_categories(sentiments, categories)

        trained_classifier = train_model(texts, sentiments, categories)
        trained_classifier.save_models(
            neg_model_path=str(NEG_MODEL_PATH),
            neg_vectorizer_path=str(NEG_VECTORIZER_PATH),
            pos_model_path=str(POS_MODEL_PATH),
            pos_vectorizer_path=str(POS_VECTORIZER_PATH),
        )
        logger.info("Model training completed and artefacts were saved.")
        return True
    except Exception as e:
        logger.error(f"Automatic model training failed: {e}", exc_info=True)
        return False


# Pydantic models for API
class PredictionRequest(BaseModel):
    """Request model for single feedback prediction."""
    customer_feedback: str = Field(..., description="Customer feedback text")
    rating: Optional[int] = Field(None, description="Optional star rating (1-5)")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_feedback": "Excellent product quality and very useful in daily life.",
                "rating": 5
            }
        }


class PredictionResponse(BaseModel):
    """Response model for a single feedback prediction."""
    is_spam:               bool             = Field(..., description="Whether input is spam/meaningless")
    sentiment_type:        str              = Field(..., description="Positive | Negative | Neutral")
    issue_category:        Optional[str]    = Field(None, description="Issue type (negative feedback only)")
    severity_score:        Optional[float]  = Field(None, description="Operational risk score 0.0-1.0 (negative only)")
    satisfaction_category: Optional[str]    = Field(None, description="Satisfaction type (positive feedback only)")
    goodwill_score:        Optional[float]  = Field(None, description="Customer trust score 0.0-1.0 (positive only)")
    confidence:            Optional[float]  = Field(None, description="Model confidence score")

    class Config:
        json_schema_extra = {
            "example": {
                "is_spam": False,
                "sentiment_type": "Positive",
                "issue_category": None,
                "severity_score": None,
                "satisfaction_category": "Product Appreciation",
                "goodwill_score": 0.9,
                "confidence": 0.87
            }
        }


class BatchPredictionRequest(BaseModel):
    """Request model for batch feedback prediction."""
    customer_feedbacks: List[str]           = Field(..., description="List of customer feedback texts")
    ratings:            Optional[List[Optional[int]]] = Field(None, description="Optional parallel list of ratings (1-5)")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_feedbacks": [
                    "Excellent product quality!",
                    "Product arrived completely broken."
                ],
                "ratings": [5, 1]
            }
        }


class BatchPredictionResponse(BaseModel):
    """Response model for batch feedback prediction."""
    predictions: List[PredictionResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [
                    {
                        "is_spam": False,
                        "sentiment_type": "Positive",
                        "issue_category": None,
                        "severity_score": None,
                        "satisfaction_category": "Product Appreciation",
                        "goodwill_score": 0.9,
                        "confidence": 0.87
                    }
                ],
                "total": 1
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    model_loaded: bool
    version: str


class GoogleSheetsUpdateRequest(BaseModel):
    """Request model for updating Google Sheets with predictions."""
    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    worksheet_name: Optional[str] = Field(None, description="Worksheet name (default: first sheet)")
    data: List[Dict[str, str]] = Field(..., description="List of data rows with 'customer_feedback' field")

    class Config:
        json_schema_extra = {
            "example": {
                "spreadsheet_id": "1ABC123xyz...",
                "worksheet_name": "Customer_Feedback_Data",
                "data": [
                    {"order_id": "ORD001", "customer_feedback": "Excellent product quality!"},
                    {"order_id": "ORD002", "customer_feedback": "Product arrived broken."}
                ]
            }
        }


class GoogleSheetsUpdateResponse(BaseModel):
    """Response model for Google Sheets update."""
    success: bool
    rows_processed: int
    message: str
    spreadsheet_url: Optional[str] = None


class GoogleSheetsProcessRequest(BaseModel):
    """Request model for processing existing Google Sheets data."""
    spreadsheet_id:  str            = Field(..., description="Google Sheets spreadsheet ID")
    worksheet_name:  Optional[str]  = Field(None, description="Worksheet name (default: first sheet)")
    feedback_column: str            = Field("Customer_Feedback", description="Name of column containing customer feedback")
    rating_column:   Optional[str]  = Field(None, description="Optional column name for star ratings")

    class Config:
        json_schema_extra = {
            "example": {
                "spreadsheet_id": "1ABC123xyz...",
                "worksheet_name": "Customer_Feedback_Data",
                "feedback_column": "Customer_Feedback",
                "rating_column": "Rating (1-5)"
            }
        }


@app.on_event("startup")
async def startup_event():
    """Load model and initialize services on application startup."""
    global classifier, sheets_service
    
    # Load NLP model
    try:
        classifier = _load_classifier_from_disk()
        if classifier is None:
            logger.warning(f"One or more model files not found in {MODEL_DIR}")
            if _train_models_from_csv():
                classifier = _load_classifier_from_disk()

        if classifier is not None:
            logger.info("Models loaded successfully")
        else:
            logger.error("No trained models available; prediction endpoints will return 503.")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        classifier = None
    
    # Initialize Google Sheets service
    try:
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        if credentials_path and os.path.exists(credentials_path):
            sheets_service = GoogleSheetsService(credentials_path)
            logger.info("Google Sheets service initialized successfully")
        else:
            logger.warning("Google Sheets credentials not found. Sheets integration will be unavailable.")
            sheets_service = None
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets service: {e}")
        sheets_service = None


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Customer Feedback Intelligence API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if classifier else "model_not_loaded",
        "model_loaded": classifier is not None,
        "version": "2.0.0"
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Classify a single customer feedback entry.

    Returns sentiment type, issue category + severity score (negative),
    or satisfaction category + goodwill score (positive).
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first: python train.py"
        )

    try:
        result = classifier.predict(request.customer_feedback, request.rating)
        return PredictionResponse(**result)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest):
    """
    Classify multiple customer feedback entries in batch.
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first: python train.py"
        )

    try:
        results = classifier.predict_batch(
            request.customer_feedbacks,
            ratings=request.ratings,
        )
        predictions = [PredictionResponse(**r) for r in results]
        return BatchPredictionResponse(predictions=predictions, total=len(predictions))
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.post("/predict/file")
async def predict_file(file: UploadFile = File(...)):
    """
    Classify customer feedback from an uploaded Excel or CSV file.

    The file should contain a 'Customer_Feedback' column (case-insensitive).
    An optional 'Rating (1-5)' column is used when present to improve sentiment detection.
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first: python train.py"
        )

    try:
        contents = await file.read()

        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload CSV or Excel file."
            )

        # Find the feedback column (case-insensitive)
        feedback_col = next(
            (col for col in df.columns if col.lower() == 'customer_feedback'),
            None
        )
        if not feedback_col:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The file must contain a 'Customer_Feedback' column."
            )

        # Find optional rating column
        rating_col = next(
            (col for col in df.columns if 'rating' in col.lower()),
            None
        )

        feedbacks = df[feedback_col].fillna("").astype(str).tolist()
        ratings   = None
        if rating_col:
            ratings = [
                (int(v) if str(v).isdigit() else None)
                for v in df[rating_col].fillna("").astype(str).tolist()
            ]

        results = classifier.predict_batch(feedbacks, ratings=ratings)

        # Add output columns
        df['1. Sentiment']             = [r['sentiment_type']        for r in results]
        df['2. Issue_Category']        = [r['issue_category'] or ""  for r in results]
        df['3. Severity_Score']        = [round(r['severity_score'], 2) if r['severity_score'] is not None else "" for r in results]
        df['4. Satisfaction_Category'] = [r['satisfaction_category'] or "" for r in results]
        df['5. Goodwill_Score']        = [round(r['goodwill_score'], 2) if r['goodwill_score'] is not None else "" for r in results]
        df['6. Confidence']            = [f"{round(r['confidence'] * 100, 1)}%" if r['confidence'] is not None else "" for r in results]
        df['7. Spam']                  = ['Yes' if r['is_spam'] else 'No' for r in results]

        output = io.BytesIO()
        if file.filename.endswith('.csv'):
            df.to_csv(output, index=False)
            media_type = "text/csv"
        else:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        output.seek(0)
        return StreamingResponse(
            output, media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename=analyzed_{file.filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File processing failed: {str(e)}"
        )


@app.post("/preprocess")
async def preprocess(text: str):
    """
    Preprocess text using NLP pipeline.
    
    Useful for debugging and testing preprocessing.
    
    Args:
        text: Text to preprocess
        
    Returns:
        Dictionary with original and preprocessed text
    """
    try:
        processed = preprocess_text(text)
        spam = is_spam(text)
        
        return {
            "original": text,
            "preprocessed": processed,
            "is_spam": spam
        }
    
    except Exception as e:
        logger.error(f"Preprocessing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preprocessing failed: {str(e)}"
        )


@app.get("/categories")
async def get_categories():
    """Get all classification categories, severity mapping, and goodwill mapping."""
    from app.nlp.classifier import SEVERITY_MAP, GOODWILL_MAP

    return {
        "negative_categories": list(SEVERITY_MAP.keys()),
        "positive_categories": list(GOODWILL_MAP.keys()),
        "severity_mapping":  SEVERITY_MAP,
        "goodwill_mapping":  GOODWILL_MAP,
    }


@app.post("/sheets/process", response_model=GoogleSheetsUpdateResponse)
async def process_existing_google_sheet(request: GoogleSheetsProcessRequest):
    """
    Process an existing Google Sheet by reading it, classifying the reason column,
    and adding new columns with classification results.
    
    This endpoint:
    1. Reads the existing sheet data
    2. Finds the specified reason column
    3. Runs NLP classification on each reason
    4. Adds new columns: return_category, return_severity, return_confidence, is_spam
    5. Writes results back to the sheet
    
    Args:
        request: GoogleSheetsProcessRequest with spreadsheet info
        
    Returns:
        GoogleSheetsUpdateResponse with operation results
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first."
        )
    
    if sheets_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Sheets service not configured. Please set GOOGLE_CREDENTIALS_PATH environment variable."
        )
    
    try:
        # Read existing sheet data
        logger.info(f"Reading sheet: {request.spreadsheet_id}")
        df = sheets_service.read_sheet_to_dataframe(
            spreadsheet_id=request.spreadsheet_id,
            worksheet_name=request.worksheet_name
        )
        
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sheet is empty or could not be read"
            )
        
        # Check if feedback column exists
        if request.feedback_column not in df.columns:
            available_columns = ", ".join(df.columns.tolist())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{request.feedback_column}' not found. Available columns: {available_columns}"
            )

        # Extract feedbacks and optional ratings, then run batch prediction
        feedbacks = df[request.feedback_column].fillna("").astype(str).tolist()
        ratings   = None
        if request.rating_column and request.rating_column in df.columns:
            ratings = [
                (int(v) if str(v).isdigit() else None)
                for v in df[request.rating_column].fillna("").astype(str).tolist()
            ]
        logger.info(f"Processing {len(feedbacks)} feedback entries...")
        results = classifier.predict_batch(feedbacks, ratings=ratings)

        # Prepare column updates
        updates = {
            'sentiment_type':        [r['sentiment_type']                  for r in results],
            'issue_category':        [r['issue_category'] or ""            for r in results],
            'severity_score':        [round(r['severity_score'], 2) if r['severity_score'] is not None else "" for r in results],
            'satisfaction_category': [r['satisfaction_category'] or ""     for r in results],
            'goodwill_score':        [round(r['goodwill_score'], 2) if r['goodwill_score'] is not None else "" for r in results],
            'confidence':            [f"{round(r['confidence'] * 100, 1)}%" if r['confidence'] is not None else "" for r in results],
            'is_spam':               ['Yes' if r['is_spam'] else 'No'       for r in results],
            'processed_at':          [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')] * len(results),
        }
        
        # Update columns in sheet
        logger.info(f"Writing classification results to sheet...")
        sheets_service.update_columns(
            spreadsheet_id=request.spreadsheet_id,
            updates=updates,
            worksheet_name=request.worksheet_name,
            start_row=2  # Start from row 2 (after header)
        )
        
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{request.spreadsheet_id}"
        
        return GoogleSheetsUpdateResponse(
            success=True,
            rows_processed=len(df),
            message=f"Successfully processed {len(df)} feedback entries and added classification columns to Google Sheets",
            spreadsheet_url=spreadsheet_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google Sheets processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process Google Sheets: {str(e)}"
        )


@app.post("/sheets/update", response_model=GoogleSheetsUpdateResponse)
async def update_google_sheets(request: GoogleSheetsUpdateRequest):
    """
    Process data and update Google Sheets with predictions in real-time.
    
    This endpoint:
    1. Takes data with 'reason' field
    2. Runs NLP classification on each reason
    3. Writes results back to Google Sheets
    
    Args:
        request: GoogleSheetsUpdateRequest with spreadsheet info and data
        
    Returns:
        GoogleSheetsUpdateResponse with operation results
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first."
        )
    
    if sheets_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Sheets service not configured. Please set GOOGLE_CREDENTIALS_PATH environment variable."
        )
    
    try:
        # Extract feedbacks from data
        feedbacks = [item.get('customer_feedback', '') for item in request.data]

        # Run batch prediction
        logger.info(f"Processing {len(feedbacks)} feedback entries...")
        results = classifier.predict_batch(feedbacks)

        # Prepare data for Google Sheets update
        updates = []
        for data_item, result in zip(request.data, results):
            row_data = {
                **data_item,
                'Sentiment_Type':        result['sentiment_type'],
                'Issue_Category':        result['issue_category']        or "",
                'Severity_Score':        round(result['severity_score'], 2) if result['severity_score'] is not None else "",
                'Satisfaction_Category': result['satisfaction_category'] or "",
                'Goodwill_Score':        round(result['goodwill_score'], 2) if result['goodwill_score'] is not None else "",
                'Confidence':            f"{round(result['confidence'] * 100, 1)}%" if result['confidence'] is not None else "",
                'Is_Spam':               'Yes' if result['is_spam'] else 'No',
                'Processed_At':          pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            updates.append(row_data)
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(updates)
        
        # Write to Google Sheets
        logger.info(f"Writing {len(df)} rows to Google Sheets...")
        sheets_service.write_dataframe_to_sheet(
            df=df,
            spreadsheet_id=request.spreadsheet_id,
            worksheet_name=request.worksheet_name,
            start_cell="A1"
        )
        
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{request.spreadsheet_id}"
        
        return GoogleSheetsUpdateResponse(
            success=True,
            rows_processed=len(df),
            message=f"Successfully processed and updated {len(df)} rows in Google Sheets",
            spreadsheet_url=spreadsheet_url
        )
        
    except Exception as e:
        logger.error(f"Google Sheets update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Google Sheets: {str(e)}"
        )


@app.post("/sheets/append", response_model=GoogleSheetsUpdateResponse)
async def append_to_google_sheets(request: GoogleSheetsUpdateRequest):
    """
    Process data and append predictions to existing Google Sheets data.
    
    Similar to /sheets/update but appends data instead of overwriting.
    
    Args:
        request: GoogleSheetsUpdateRequest with spreadsheet info and data
        
    Returns:
        GoogleSheetsUpdateResponse with operation results
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first."
        )
    
    if sheets_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Sheets service not configured. Please set GOOGLE_CREDENTIALS_PATH environment variable."
        )
    
    try:
        # Extract feedbacks from data
        feedbacks = [item.get('customer_feedback', '') for item in request.data]

        # Run batch prediction
        logger.info(f"Processing {len(feedbacks)} feedback entries...")
        results = classifier.predict_batch(feedbacks)

        # Prepare rows for appending
        updates = []
        for data_item, result in zip(request.data, results):
            row_data = {
                **data_item,
                'Sentiment_Type':        result['sentiment_type'],
                'Issue_Category':        result['issue_category']        or "",
                'Severity_Score':        round(result['severity_score'], 2) if result['severity_score'] is not None else "",
                'Satisfaction_Category': result['satisfaction_category'] or "",
                'Goodwill_Score':        round(result['goodwill_score'], 2) if result['goodwill_score'] is not None else "",
                'Confidence':            f"{round(result['confidence'] * 100, 1)}%" if result['confidence'] is not None else "",
                'Is_Spam':               'Yes' if result['is_spam'] else 'No',
                'Processed_At':          pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            updates.append(row_data)
        
        # Get worksheet
        worksheet = sheets_service.get_worksheet(
            spreadsheet_id=request.spreadsheet_id,
            worksheet_name=request.worksheet_name
        )
        
        # Get existing data to determine where to append
        existing_data = worksheet.get_all_values()
        next_row = len(existing_data) + 1
        
        # If sheet is empty, add headers
        if next_row == 1:
            headers = list(updates[0].keys())
            worksheet.append_row(headers)
            next_row = 2
        
        # Append rows
        logger.info(f"Appending {len(updates)} rows to Google Sheets starting at row {next_row}...")
        for row_data in updates:
            # Get values in order of headers
            headers = worksheet.row_values(1)
            values = [row_data.get(header, '') for header in headers]
            worksheet.append_row(values)
        
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{request.spreadsheet_id}"
        
        return GoogleSheetsUpdateResponse(
            success=True,
            rows_processed=len(updates),
            message=f"Successfully appended {len(updates)} rows to Google Sheets",
            spreadsheet_url=spreadsheet_url
        )
        
    except Exception as e:
        logger.error(f"Google Sheets append error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to append to Google Sheets: {str(e)}"
        )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
