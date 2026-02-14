"""
Training script for NLP classifier.
Trains TF-IDF + Logistic Regression model on labeled data and saves to disk.
"""
import os
import sys
import logging
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.nlp.classifier import NLPClassifier, VALID_CATEGORIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
TRAINING_DATA_PATH = Path(__file__).parent / "training_data" / "sample_data.csv"
MODEL_DIR = Path(__file__).parent / "app" / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf.pkl"


def load_training_data(data_path: Path) -> tuple[list[str], list[str]]:
    """
    Load training data from CSV file.
    
    Args:
        data_path: Path to CSV file with columns: return_reason, category
        
    Returns:
        Tuple of (texts, labels)
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Training data not found: {data_path}")
    
    logger.info(f"Loading training data from: {data_path}")
    df = pd.read_csv(data_path)
    
    # Validate columns
    if "return_reason" not in df.columns or "category" not in df.columns:
        raise ValueError("CSV must contain 'return_reason' and 'category' columns")
    
    # Remove any NaN values
    df = df.dropna()
    
    texts = df["return_reason"].tolist()
    labels = df["category"].tolist()
    
    logger.info(f"Loaded {len(texts)} training samples")
    logger.info(f"Categories: {df['category'].unique().tolist()}")
    logger.info(f"Category distribution:\n{df['category'].value_counts()}")
    
    return texts, labels


def validate_categories(labels: list[str]) -> bool:
    """
    Validate that all labels are valid categories.
    
    Args:
        labels: List of category labels
        
    Returns:
        True if all valid
    """
    unique_labels = set(labels)
    invalid = unique_labels - set(VALID_CATEGORIES)
    
    if invalid:
        logger.error(f"Invalid categories found: {invalid}")
        logger.error(f"Valid categories are: {VALID_CATEGORIES}")
        return False
    
    return True


def train_model(
    texts: list[str],
    labels: list[str],
    test_size: float = 0.2,
    random_state: int = 42
) -> NLPClassifier:
    """
    Train the NLP classifier.
    
    Args:
        texts: List of training texts
        labels: List of category labels
        test_size: Fraction for test split
        random_state: Random seed
        
    Returns:
        Trained NLPClassifier
    """
    logger.info("Initializing classifier...")
    classifier = NLPClassifier(
        max_features=1000,
        ngram_range=(1, 2)
    )
    
    logger.info("Starting training...")
    metrics = classifier.train(
        texts=texts,
        labels=labels,
        test_size=test_size,
        random_state=random_state
    )
    
    logger.info("\nTraining Metrics:")
    for key, value in metrics.items():
        logger.info(f"  {key}: {value}")
    
    return classifier


def test_predictions(classifier: NLPClassifier):
    """
    Test the classifier with sample inputs.
    
    Args:
        classifier: Trained classifier
    """
    test_cases = [
        "Item arrived completely broken",
        "Wrong product was sent to me",
        "Product is already expired",
        "Package was torn and damaged",
        "I changed my mind don't need it",
        "no reason",
        "Quality is poor",
        "Late delivery"
    ]
    
    logger.info("\n" + "="*60)
    logger.info("Testing predictions on sample inputs:")
    logger.info("="*60)
    
    for text in test_cases:
        result = classifier.predict(text)
        logger.info(f"\nInput: {text}")
        logger.info(f"Category: {result['reason_category']}")
        logger.info(f"Severity: {result['severity_score']}")
        logger.info(f"Is Spam: {result['is_spam']}")
        if 'confidence' in result:
            logger.info(f"Confidence: {result['confidence']:.2f}")


def main():
    """Main training function."""
    try:
        # Create model directory if it doesn't exist
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load data
        texts, labels = load_training_data(TRAINING_DATA_PATH)
        
        # Validate categories
        if not validate_categories(labels):
            sys.exit(1)
        
        # Train model
        classifier = train_model(texts, labels)
        
        # Save models
        logger.info(f"\nSaving models to: {MODEL_DIR}")
        classifier.save_models(str(MODEL_PATH), str(VECTORIZER_PATH))
        
        # Test predictions
        test_predictions(classifier)
        
        logger.info("\n" + "="*60)
        logger.info("✓ Training complete!")
        logger.info("="*60)
        logger.info(f"Model saved to: {MODEL_PATH}")
        logger.info(f"Vectorizer saved to: {VECTORIZER_PATH}")
        logger.info("\nYou can now run the API server with:")
        logger.info("  python -m uvicorn app.main:app --reload")
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
