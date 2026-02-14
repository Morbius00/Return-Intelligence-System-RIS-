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

from app.nlp import NLPClassifier, is_spam, preprocess_text

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


@app.on_event("startup")
async def startup_event():
    """Load model on application startup."""
    global classifier
    
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


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
