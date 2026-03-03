"""
Training script for the FeedbackClassifier.

Trains two TF-IDF + Logistic Regression models:
  • Negative sub-model  → classifies issue category + Severity Score
  • Positive sub-model  → classifies satisfaction category + Goodwill Score

Training data: training_data/feedback_training_data.csv
  Columns: customer_feedback, sentiment, category
"""
import os
import sys
import logging
from pathlib import Path

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.nlp.classifier import FeedbackClassifier, NEGATIVE_CATEGORIES, POSITIVE_CATEGORIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
TRAINING_DATA_PATH = Path(__file__).parent / "training_data" / "feedback_training_data.csv"
MODEL_DIR          = Path(__file__).parent / "app" / "models"

NEG_MODEL_PATH      = MODEL_DIR / "neg_model.pkl"
NEG_VECTORIZER_PATH = MODEL_DIR / "neg_tfidf.pkl"
POS_MODEL_PATH      = MODEL_DIR / "pos_model.pkl"
POS_VECTORIZER_PATH = MODEL_DIR / "pos_tfidf.pkl"


def load_training_data(data_path: Path):
    """
    Load training data from the feedback CSV.

    Expected columns: customer_feedback, sentiment, category

    Returns
    -------
    (texts, sentiments, categories) – three parallel lists
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Training data not found: {data_path}")

    logger.info(f"Loading training data from: {data_path}")
    df = pd.read_csv(data_path)

    required = {"customer_feedback", "sentiment", "category"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. "
            f"Found: {df.columns.tolist()}"
        )

    df = df.dropna()

    texts      = df["customer_feedback"].tolist()
    sentiments = df["sentiment"].tolist()
    categories = df["category"].tolist()

    logger.info(f"Loaded {len(texts)} training samples")
    logger.info(f"Sentiment distribution:\n{df['sentiment'].value_counts()}")
    logger.info(f"Category distribution:\n{df['category'].value_counts()}")

    return texts, sentiments, categories


def validate_categories(sentiments: list, categories: list) -> bool:
    """Validate that all labels belong to the expected sets."""
    valid_neg = set(NEGATIVE_CATEGORIES)
    valid_pos = set(POSITIVE_CATEGORIES)
    errors = []
    for sent, cat in zip(sentiments, categories):
        if sent == "Negative" and cat not in valid_neg:
            errors.append(f"Unknown negative category: '{cat}'")
        elif sent == "Positive" and cat not in valid_pos and cat != "General Positive":
            errors.append(f"Unknown positive category: '{cat}'")
    if errors:
        for e in set(errors):
            logger.warning(e)
    return True  # warnings only – training can still proceed


def train_model(texts: list, sentiments: list, categories: list) -> FeedbackClassifier:
    """Instantiate and train the FeedbackClassifier."""
    logger.info("Initializing FeedbackClassifier...")
    classifier = FeedbackClassifier(max_features=1000, ngram_range=(1, 2))

    logger.info("Starting training...")
    metrics = classifier.train(
        texts=texts,
        sentiments=sentiments,
        categories=categories,
        test_size=0.2,
        random_state=42,
    )

    logger.info("\nTraining Metrics:")
    for key, value in metrics.items():
        logger.info(f"  {key}: {value}")

    return classifier


def test_predictions(classifier: FeedbackClassifier):
    """Smoke-test the trained classifier."""
    test_cases = [
        ("Excellent product quality and very useful in daily life.", 5),
        ("Battery life is impressive and long-lasting.", 4),
        ("Delivery was fast and product works perfectly.", 5),
        ("Highly recommended to others.", 5),
        ("Product arrived completely broken and unusable.", 1),
        ("Received a completely wrong item.", 2),
        ("Packaging was torn and item was damaged.", 2),
        ("Got an expired product.", 1),
        ("I changed my mind, no longer need this.", 2),
        ("Average experience, could be improved.", 3),
        ("no reason", None),
    ]

    logger.info("\n" + "=" * 65)
    logger.info("Smoke-test predictions:")
    logger.info("=" * 65)

    for feedback, rating in test_cases:
        result = classifier.predict(feedback, rating)
        logger.info(f"\nFeedback : {feedback}")
        logger.info(f"Rating   : {rating}")
        logger.info(f"Sentiment: {result['sentiment_type']}")
        if result["issue_category"]:
            logger.info(f"Issue    : {result['issue_category']}  (Severity {result['severity_score']})")
        if result["satisfaction_category"]:
            logger.info(f"Satisfaction: {result['satisfaction_category']}  (Goodwill {result['goodwill_score']})")
        if result["is_spam"]:
            logger.info("→ Detected as spam / insufficient input")


def main():
    """Main training entry point."""
    try:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

        texts, sentiments, categories = load_training_data(TRAINING_DATA_PATH)
        validate_categories(sentiments, categories)

        classifier = train_model(texts, sentiments, categories)

        logger.info(f"\nSaving models to: {MODEL_DIR}")
        classifier.save_models(
            neg_model_path      = str(NEG_MODEL_PATH),
            neg_vectorizer_path = str(NEG_VECTORIZER_PATH),
            pos_model_path      = str(POS_MODEL_PATH),
            pos_vectorizer_path = str(POS_VECTORIZER_PATH),
        )

        test_predictions(classifier)

        logger.info("\n" + "=" * 65)
        logger.info("✓ Training complete!")
        logger.info("=" * 65)
        logger.info(f"Negative model     : {NEG_MODEL_PATH}")
        logger.info(f"Negative vectorizer: {NEG_VECTORIZER_PATH}")
        logger.info(f"Positive model     : {POS_MODEL_PATH}")
        logger.info(f"Positive vectorizer: {POS_VECTORIZER_PATH}")
        logger.info("\nStart the API server with:")
        logger.info("  python -m uvicorn app.main:app --reload")

    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
