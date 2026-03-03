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
MODEL_DIR           = Path(__file__).parent / "app" / "models"
NEG_MODEL_PATH      = MODEL_DIR / "neg_model.pkl"
NEG_VECTORIZER_PATH = MODEL_DIR / "neg_tfidf.pkl"
POS_MODEL_PATH      = MODEL_DIR / "pos_model.pkl"
POS_VECTORIZER_PATH = MODEL_DIR / "pos_tfidf.pkl"


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
        feedback_column: str = "Customer_Feedback",
        rating_column: Optional[str] = None,
    ):
        """
        Process all customer feedback entries in a Google Sheet.

        Args:
            spreadsheet_id : Google Sheets spreadsheet ID
            worksheet_name : Name of worksheet (optional)
            feedback_column: Name of column containing customer feedback
            rating_column  : Optional column name for star ratings
        """
        logger.info(f"Reading data from spreadsheet: {spreadsheet_id}")

        df = self.sheets_service.read_sheet_to_dataframe(
            spreadsheet_id=spreadsheet_id,
            worksheet_name=worksheet_name
        )

        if df.empty:
            logger.warning("Sheet is empty. Nothing to process.")
            return

        if feedback_column not in df.columns:
            raise ValueError(
                f"Column '{feedback_column}' not found. "
                f"Available columns: {df.columns.tolist()}"
            )

        logger.info(f"Processing {len(df)} rows...")

        feedbacks = df[feedback_column].fillna("").astype(str).tolist()
        ratings   = None
        if rating_column and rating_column in df.columns:
            ratings = [
                (int(v) if str(v).isdigit() else None)
                for v in df[rating_column].fillna("").astype(str).tolist()
            ]

        results = self.classifier.predict_batch(feedbacks, ratings=ratings)
        
        # Extract results into separate lists
        sentiments     = [r["sentiment_type"]        for r in results]
        issue_cats     = [r["issue_category"]   or "" for r in results]
        severities     = [r["severity_score"]    if r["severity_score"]  is not None else "" for r in results]
        sat_cats       = [r["satisfaction_category"] or "" for r in results]
        goodwills      = [r["goodwill_score"]    if r["goodwill_score"]   is not None else "" for r in results]
        spam_flags     = [r["is_spam"]               for r in results]

        # Log statistics
        spam_count     = sum(spam_flags)
        pos_count      = sentiments.count("Positive")
        neg_count      = sentiments.count("Negative")
        neutral_count  = sentiments.count("Neutral")
        logger.info(f"Classification complete:")
        logger.info(f"  Total processed : {len(results)}")
        logger.info(f"  Spam detected   : {spam_count}")
        logger.info(f"  Positive        : {pos_count}")
        logger.info(f"  Negative        : {neg_count}")
        logger.info(f"  Neutral         : {neutral_count}")
        
        # Write results back to sheet
        logger.info("\nWriting results back to Google Sheets...")
        self.sheets_service.batch_update_rows(
            spreadsheet_id=spreadsheet_id,
            row_data=[
                {
                    "sentiment_type":        sent,
                    "issue_category":        ic,
                    "severity_score":        sev,
                    "satisfaction_category": sc,
                    "goodwill_score":        gw,
                    "is_spam":               spam,
                }
                for sent, ic, sev, sc, gw, spam in zip(
                    sentiments, issue_cats, severities, sat_cats, goodwills, spam_flags
                )
            ],
            worksheet_name=worksheet_name,
            start_row=2
        )

        logger.info("✓ Batch processing complete!")
    
    def process_local_csv(
        self,
        csv_path: str,
        output_path: str,
        feedback_column: str = "Customer_Feedback",
        rating_column: Optional[str] = None,
    ):
        """
        Process a local CSV or Excel file and save enriched output.

        Args:
            csv_path       : Path to input file (CSV or Excel)
            output_path    : Path to output CSV file
            feedback_column: Name of column containing customer feedback
            rating_column  : Optional column name for star ratings
        """
        logger.info(f"Reading data from: {csv_path}")

        if csv_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(csv_path)
        else:
            df = pd.read_csv(csv_path)

        if df.empty:
            logger.warning("File is empty. Nothing to process.")
            return

        if feedback_column not in df.columns:
            raise ValueError(
                f"Column '{feedback_column}' not found. "
                f"Available columns: {df.columns.tolist()}"
            )

        logger.info(f"Processing {len(df)} rows...")

        feedbacks = df[feedback_column].fillna("").astype(str).tolist()
        ratings   = None
        if rating_column and rating_column in df.columns:
            ratings = [
                (int(v) if str(v).isdigit() else None)
                for v in df[rating_column].fillna("").astype(str).tolist()
            ]

        results = self.classifier.predict_batch(feedbacks, ratings=ratings)

        # Add enriched columns
        df["sentiment_type"]        = [r["sentiment_type"]                  for r in results]
        df["issue_category"]        = [r["issue_category"]   or ""          for r in results]
        df["severity_score"]        = [r["severity_score"]   if r["severity_score"]  is not None else "" for r in results]
        df["satisfaction_category"] = [r["satisfaction_category"] or ""     for r in results]
        df["goodwill_score"]        = [r["goodwill_score"]   if r["goodwill_score"]   is not None else "" for r in results]
        df["is_spam"]               = [r["is_spam"]                         for r in results]

        df.to_csv(output_path, index=False)
        logger.info(f"✓ Results saved to: {output_path}")

        spam_count = sum(r["is_spam"] for r in results)
        pos_count  = sum(1 for r in results if r["sentiment_type"] == "Positive")
        neg_count  = sum(1 for r in results if r["sentiment_type"] == "Negative")
        logger.info(f"\nStatistics:")
        logger.info(f"  Total processed: {len(df)}")
        logger.info(f"  Spam detected  : {spam_count}")
        logger.info(f"  Positive       : {pos_count}")
        logger.info(f"  Negative       : {neg_count}")


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
        default="Customer_Feedback",
        help="Name of column containing customer feedback (default: Customer_Feedback)"
    )
    parser.add_argument(
        "--rating-column",
        default=None,
        help="Optional name of column containing star ratings (e.g. 'Rating (1-5)')"
    )
    
    args = parser.parse_args()
    
    try:
        # Load classifier
        logger.info("Loading trained feedback classifier models...")
        all_exist = (
            NEG_MODEL_PATH.exists() and NEG_VECTORIZER_PATH.exists()
            and POS_MODEL_PATH.exists() and POS_VECTORIZER_PATH.exists()
        )
        if not all_exist:
            logger.error(f"One or more model files not found in {MODEL_DIR}")
            logger.error("Please train the model first using: python train.py")
            sys.exit(1)

        classifier = NLPClassifier(
            neg_model_path      = str(NEG_MODEL_PATH),
            neg_vectorizer_path = str(NEG_VECTORIZER_PATH),
            pos_model_path      = str(POS_MODEL_PATH),
            pos_vectorizer_path = str(POS_VECTORIZER_PATH),
        )
        logger.info("Models loaded successfully")
        
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
                spreadsheet_id  = args.spreadsheet_id,
                worksheet_name  = args.worksheet_name,
                feedback_column = args.column,
                rating_column   = args.rating_column,
            )

        elif args.mode == "csv":
            if not args.csv_input or not args.csv_output:
                logger.error("--csv-input and --csv-output are required for csv mode")
                sys.exit(1)

            processor = BatchProcessor(classifier, None)

            processor.process_local_csv(
                csv_path        = args.csv_input,
                output_path     = args.csv_output,
                feedback_column = args.column,
                rating_column   = getattr(args, 'rating_column', None),
            )
    
    except Exception as e:
        logger.error(f"Batch processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
