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
    title="NLP Return Reason Classifier",
    description="Lightweight NLP system for classifying customer return reasons using classical ML",
    version="1.0.0",
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
MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf.pkl"

# Global classifier instance
classifier: Optional[NLPClassifier] = None

# Global Google Sheets service instance
sheets_service: Optional[GoogleSheetsService] = None


# Pydantic models for API
class PredictionRequest(BaseModel):
    """Request model for single prediction."""
    return_reason: str = Field(..., description="Customer return reason text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "return_reason": "item arrived broken"
            }
        }


class PredictionResponse(BaseModel):
    """Response model for single prediction."""
    is_spam: bool = Field(..., description="Whether input is spam/meaningless")
    reason_category: str = Field(..., description="Classified category")
    severity_score: float = Field(..., description="Severity score (0.0 to 1.0)")
    confidence: Optional[float] = Field(None, description="Model confidence score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_spam": False,
                "reason_category": "Product Quality Issue",
                "severity_score": 0.9,
                "confidence": 0.85
            }
        }


class BatchPredictionRequest(BaseModel):
    """Request model for batch prediction."""
    return_reasons: List[str] = Field(..., description="List of return reason texts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "return_reasons": [
                    "item arrived broken",
                    "wrong product sent",
                    "no reason"
                ]
            }
        }


class BatchPredictionResponse(BaseModel):
    """Response model for batch prediction."""
    predictions: List[PredictionResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [
                    {
                        "is_spam": False,
                        "reason_category": "Product Quality Issue",
                        "severity_score": 0.9,
                        "confidence": 0.85
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
    data: List[Dict[str, str]] = Field(..., description="List of data rows with 'reason' field")
    
    class Config:
        json_schema_extra = {
            "example": {
                "spreadsheet_id": "1ABC123xyz...",
                "worksheet_name": "Returns",
                "data": [
                    {"order_id": "ORD001", "reason": "item arrived broken"},
                    {"order_id": "ORD002", "reason": "wrong size"}
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
    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    worksheet_name: Optional[str] = Field(None, description="Worksheet name (default: first sheet)")
    reason_column: str = Field("reason", description="Name of column containing return reasons")
    
    class Config:
        json_schema_extra = {
            "example": {
                "spreadsheet_id": "1ABC123xyz...",
                "worksheet_name": "Returns",
                "reason_column": "reason"
            }
        }


@app.on_event("startup")
async def startup_event():
    """Load model and initialize services on application startup."""
    global classifier, sheets_service
    
    # Load NLP model
    try:
        if MODEL_PATH.exists() and VECTORIZER_PATH.exists():
            logger.info("Loading trained model...")
            classifier = NLPClassifier(
                model_path=str(MODEL_PATH),
                vectorizer_path=str(VECTORIZER_PATH)
            )
            logger.info("Model loaded successfully")
        else:
            logger.warning(f"Model files not found at {MODEL_DIR}")
            logger.warning("Please train the model first using train.py")
            classifier = None
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
        "message": "NLP Return Reason Classifier API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if classifier else "model_not_loaded",
        "model_loaded": classifier is not None,
        "version": "1.0.0"
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Classify a single return reason text.
    
    Args:
        request: PredictionRequest with return_reason text
        
    Returns:
        PredictionResponse with classification results
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first."
        )
    
    try:
        # Get prediction
        result = classifier.predict(request.return_reason)
        
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
    Classify multiple return reason texts in batch.
    
    Args:
        request: BatchPredictionRequest with list of return_reasons
        
    Returns:
        BatchPredictionResponse with all predictions
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first."
        )
    
    try:
        # Get predictions
        results = classifier.predict_batch(request.return_reasons)
        
        predictions = [PredictionResponse(**result) for result in results]
        
        return BatchPredictionResponse(
            predictions=predictions,
            total=len(predictions)
        )
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.post("/predict/file")
async def predict_file(file: UploadFile = File(...)):
    """
    Classify return reasons from an uploaded Excel or CSV file.
    
    The file must contain a 'reason' column.
    
    Args:
        file: Uploaded Excel (.xlsx, .xls) or CSV file
        
    Returns:
        Processed file with added classification columns
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train the model first."
        )
    
    try:
        # Read file content
        contents = await file.read()
        
        # Load into DataFrame based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload CSV or Excel file."
            )
        
        # Check if 'reason' column exists (case-insensitive)
        reason_col = next((col for col in df.columns if col.lower() == 'reason'), None)
        
        if not reason_col:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The file must contain a 'reason' column."
            )
        
        # Get all reasons and run batch prediction
        reasons = df[reason_col].fillna("").astype(str).tolist()
        results = classifier.predict_batch(reasons)
        
        # Add new columns
        df['1. Category'] = [res['reason_category'] for res in results]
        df['2. Severity'] = [round(res['severity_score'], 2) for res in results]
        df['3. Confidence'] = [round(res.get('confidence', 0) * 100, 1) for res in results]
        df['4. Spam'] = ['Yes' if res['is_spam'] else 'No' for res in results]
        
        # Prepare response file
        output = io.BytesIO()
        if file.filename.endswith('.csv'):
            df.to_csv(output, index=False)
            media_type = "text/csv"
            filename = f"analyzed_{file.filename}"
        else:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"analyzed_{file.filename}"
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
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
    """Get list of valid classification categories and their severity scores."""
    from app.nlp.classifier import SEVERITY_MAP
    
    return {
        "categories": list(SEVERITY_MAP.keys()),
        "severity_mapping": SEVERITY_MAP
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
        
        # Check if reason column exists
        if request.reason_column not in df.columns:
            available_columns = ", ".join(df.columns.tolist())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column '{request.reason_column}' not found. Available columns: {available_columns}"
            )
        
        # Extract reasons and run batch prediction
        reasons = df[request.reason_column].fillna("").astype(str).tolist()
        logger.info(f"Processing {len(reasons)} reasons...")
        results = classifier.predict_batch(reasons)
        
        # Prepare column updates
        updates = {
            'return_category': [res['reason_category'] for res in results],
            'return_severity': [round(res['severity_score'], 2) for res in results],
            'return_confidence': [f"{round(res.get('confidence', 0) * 100, 1)}%" for res in results],
            'is_spam': ['Yes' if res['is_spam'] else 'No' for res in results],
            'processed_at': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')] * len(results)
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
            message=f"Successfully processed {len(df)} rows and added classification columns to Google Sheets",
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
        # Extract reasons from data
        reasons = [item.get('reason', '') for item in request.data]
        
        # Run batch prediction
        logger.info(f"Processing {len(reasons)} reasons...")
        results = classifier.predict_batch(reasons)
        
        # Prepare data for Google Sheets update
        updates = []
        for i, (data_item, result) in enumerate(zip(request.data, results)):
            row_data = {
                **data_item,  # Include original data
                'Category': result['reason_category'],
                'Severity': round(result['severity_score'], 2),
                'Confidence': f"{round(result.get('confidence', 0) * 100, 1)}%",
                'Is_Spam': 'Yes' if result['is_spam'] else 'No',
                'Processed_At': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
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
        # Extract reasons from data
        reasons = [item.get('reason', '') for item in request.data]
        
        # Run batch prediction
        logger.info(f"Processing {len(reasons)} reasons...")
        results = classifier.predict_batch(reasons)
        
        # Prepare rows for appending
        updates = []
        for i, (data_item, result) in enumerate(zip(request.data, results)):
            row_data = {
                **data_item,
                'Category': result['reason_category'],
                'Severity': round(result['severity_score'], 2),
                'Confidence': f"{round(result.get('confidence', 0) * 100, 1)}%",
                'Is_Spam': 'Yes' if result['is_spam'] else 'No',
                'Processed_At': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
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
