"""
Batch processor for Google Sheets integration.
Reads return reasons from Google Sheets, classifies them, and writes results back.
"""
import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.nlp.classifier import NLPClassifier
from app.services.sheets_service import GoogleSheetsService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Model paths
MODEL_DIR = Path(__file__).parent / "app" / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf.pkl"


class BatchProcessor:
    """
    Batch processor for classifying return reasons from Google Sheets.
    """
    
    def __init__(
        self,
        classifier: NLPClassifier,
        sheets_service: GoogleSheetsService
    ):
        """
        Initialize batch processor.
        
        Args:
            classifier: Trained NLPClassifier instance
            sheets_service: Authenticated GoogleSheetsService instance
        """
        self.classifier = classifier
        self.sheets_service = sheets_service
    
    def process_sheet(
        self,
        spreadsheet_id: str,
        worksheet_name: Optional[str] = None,
        return_reason_column: str = "return_reason"
    ):
        """
        Process all return reasons in a Google Sheet.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            worksheet_name: Name of worksheet (optional)
            return_reason_column: Name of column containing return reasons
        """
        logger.info(f"Reading data from spreadsheet: {spreadsheet_id}")
        
        # Read sheet data
        df = self.sheets_service.read_sheet_to_dataframe(
            spreadsheet_id=spreadsheet_id,
            worksheet_name=worksheet_name
        )
        
        if df.empty:
            logger.warning("Sheet is empty. Nothing to process.")
            return
        
        # Validate column exists
        if return_reason_column not in df.columns:
            raise ValueError(
                f"Column '{return_reason_column}' not found. "
                f"Available columns: {df.columns.tolist()}"
            )
        
        logger.info(f"Processing {len(df)} rows...")
        
        # Extract return reasons
        return_reasons = df[return_reason_column].fillna("").astype(str).tolist()
        
        # Classify all reasons
        results = self.classifier.predict_batch(return_reasons)
        
        # Extract results into separate lists
        categories = [r["reason_category"] for r in results]
        severities = [r["severity_score"] for r in results]
        spam_flags = [r["is_spam"] for r in results]
        
        # Log statistics
        spam_count = sum(spam_flags)
        logger.info(f"Classification complete:")
        logger.info(f"  Total processed: {len(results)}")
        logger.info(f"  Spam detected: {spam_count}")
        logger.info(f"  Valid classifications: {len(results) - spam_count}")
        
        # Category distribution
        category_counts = pd.Series(categories).value_counts()
        logger.info("\nCategory distribution:")
        for category, count in category_counts.items():
            logger.info(f"  {category}: {count}")
        
        # Prepare updates
        updates = {
            "reason_category": categories,
            "severity_score": severities,
            "is_spam": spam_flags
        }
        
        # Write results back to sheet
        logger.info("\nWriting results back to Google Sheets...")
        self.sheets_service.batch_update_rows(
            spreadsheet_id=spreadsheet_id,
            row_data=[
                {
                    "reason_category": cat,
                    "severity_score": sev,
                    "is_spam": spam
                }
                for cat, sev, spam in zip(categories, severities, spam_flags)
            ],
            worksheet_name=worksheet_name,
            start_row=2  # Skip header row
        )
        
        logger.info("✓ Batch processing complete!")
    
    def process_local_csv(
        self,
        csv_path: str,
        output_path: str,
        return_reason_column: str = "return_reason"
    ):
        """
        Process a local CSV file instead of Google Sheets.
        
        Args:
            csv_path: Path to input CSV file
            output_path: Path to output CSV file
            return_reason_column: Name of column containing return reasons
        """
        logger.info(f"Reading data from: {csv_path}")
        
        # Read CSV
        df = pd.read_csv(csv_path)
        
        if df.empty:
            logger.warning("CSV is empty. Nothing to process.")
            return
        
        # Validate column exists
        if return_reason_column not in df.columns:
            raise ValueError(
                f"Column '{return_reason_column}' not found. "
                f"Available columns: {df.columns.tolist()}"
            )
        
        logger.info(f"Processing {len(df)} rows...")
        
        # Extract return reasons
        return_reasons = df[return_reason_column].fillna("").astype(str).tolist()
        
        # Classify all reasons
        results = self.classifier.predict_batch(return_reasons)
        
        # Add results to dataframe
        df["reason_category"] = [r["reason_category"] for r in results]
        df["severity_score"] = [r["severity_score"] for r in results]
        df["is_spam"] = [r["is_spam"] for r in results]
        
        # Save to output CSV
        df.to_csv(output_path, index=False)
        
        logger.info(f"✓ Results saved to: {output_path}")
        
        # Log statistics
        spam_count = df["is_spam"].sum()
        logger.info(f"\nStatistics:")
        logger.info(f"  Total processed: {len(df)}")
        logger.info(f"  Spam detected: {spam_count}")
        logger.info(f"  Valid classifications: {len(df) - spam_count}")
        
        # Category distribution
        logger.info("\nCategory distribution:")
        for category, count in df["reason_category"].value_counts().items():
            logger.info(f"  {category}: {count}")


def main():
    """Main batch processing function."""
    parser = argparse.ArgumentParser(
        description="Batch process return reasons from Google Sheets or CSV"
    )
    parser.add_argument(
        "--mode",
        choices=["sheets", "csv"],
        default="sheets",
        help="Processing mode: 'sheets' for Google Sheets or 'csv' for local CSV"
    )
    parser.add_argument(
        "--spreadsheet-id",
        help="Google Sheets spreadsheet ID (required for sheets mode)"
    )
    parser.add_argument(
        "--worksheet-name",
        help="Google Sheets worksheet name (optional)"
    )
    parser.add_argument(
        "--csv-input",
        help="Path to input CSV file (required for csv mode)"
    )
    parser.add_argument(
        "--csv-output",
        help="Path to output CSV file (required for csv mode)"
    )
    parser.add_argument(
        "--column",
        default="return_reason",
        help="Name of column containing return reasons (default: return_reason)"
    )
    
    args = parser.parse_args()
    
    try:
        # Load classifier
        logger.info("Loading trained model...")
        if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
            logger.error(f"Model files not found in {MODEL_DIR}")
            logger.error("Please train the model first using: python train.py")
            sys.exit(1)
        
        classifier = NLPClassifier(
            model_path=str(MODEL_PATH),
            vectorizer_path=str(VECTORIZER_PATH)
        )
        logger.info("Model loaded successfully")
        
        if args.mode == "sheets":
            # Google Sheets mode
            if not args.spreadsheet_id:
                logger.error("--spreadsheet-id is required for sheets mode")
                sys.exit(1)
            
            # Initialize Google Sheets service
            logger.info("Initializing Google Sheets service...")
            sheets_service = GoogleSheetsService()
            
            # Create batch processor
            processor = BatchProcessor(classifier, sheets_service)
            
            # Process sheet
            processor.process_sheet(
                spreadsheet_id=args.spreadsheet_id,
                worksheet_name=args.worksheet_name,
                return_reason_column=args.column
            )
        
        elif args.mode == "csv":
            # Local CSV mode
            if not args.csv_input or not args.csv_output:
                logger.error("--csv-input and --csv-output are required for csv mode")
                sys.exit(1)
            
            # Create batch processor (sheets_service not needed)
            processor = BatchProcessor(classifier, None)
            
            # Process CSV
            processor.process_local_csv(
                csv_path=args.csv_input,
                output_path=args.csv_output,
                return_reason_column=args.column
            )
    
    except Exception as e:
        logger.error(f"Batch processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
