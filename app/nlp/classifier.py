"""
Text classification module using TF-IDF and Logistic Regression.
Provides classification and severity scoring for return reasons.
"""
import os
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .preprocess import preprocess_text
from .spam_detector import is_spam

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Category to severity mapping
SEVERITY_MAP: Dict[str, float] = {
    "Product Quality Issue": 0.9,
    "Expiry Issue": 0.9,
    "Packaging Issue": 0.6,
    "Wrong Item": 0.6,
    "Customer Preference": 0.3,
    "Other": 0.2,
}

# Valid categories
VALID_CATEGORIES = list(SEVERITY_MAP.keys())


class NLPClassifier:
    """
    NLP Classifier for return reason categorization.
    
    Uses TF-IDF vectorization and Logistic Regression for classification.
    Includes spam detection and severity scoring.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        vectorizer_path: Optional[str] = None,
        max_features: int = 1000,
        ngram_range: Tuple[int, int] = (1, 2)
    ):
        """
        Initialize the NLP classifier.
        
        Args:
            model_path: Path to saved model file
            vectorizer_path: Path to saved vectorizer file
            max_features: Maximum features for TF-IDF (default: 1000)
            ngram_range: N-gram range for TF-IDF (default: (1, 2))
        """
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.max_features = max_features
        self.ngram_range = ngram_range
        
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.model: Optional[LogisticRegression] = None
        self.is_trained = False
        
        # Load models if paths provided
        if model_path and vectorizer_path:
            self.load_models(model_path, vectorizer_path)
    
    def train(
        self,
        texts: list[str],
        labels: list[str],
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        Train the classifier on labeled data.
        
        Args:
            texts: List of text samples
            labels: List of category labels
            test_size: Fraction of data for testing (default: 0.2)
            random_state: Random seed for reproducibility
            
        Returns:
            Dictionary with training metrics
        """
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report
        
        logger.info("Preprocessing texts...")
        processed_texts = [preprocess_text(text) for text in texts]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            processed_texts,
            labels,
            test_size=test_size,
            random_state=random_state,
            stratify=labels
        )
        
        # Initialize and fit vectorizer
        logger.info("Training TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=2,
            max_df=0.8
        )
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        # Train classifier
        logger.info("Training Logistic Regression model...")
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=random_state,
            class_weight="balanced",
            solver="lbfgs"
        )
        self.model.fit(X_train_tfidf, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Training complete. Accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        self.is_trained = True
        
        return {
            "accuracy": accuracy,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "num_features": X_train_tfidf.shape[1]
        }
    
    def predict(self, text: str) -> Dict[str, any]:
        """
        Predict category and severity for a single text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with prediction results:
            {
                "is_spam": bool,
                "reason_category": str,
                "severity_score": float,
                "confidence": float (optional)
            }
        """
        # Check spam first
        if is_spam(text):
            return {
                "is_spam": True,
                "reason_category": "Other",
                "severity_score": 0.0
            }
        
        if not self.is_trained:
            raise ValueError("Model is not trained. Please train or load a model first.")
        
        # Preprocess
        processed_text = preprocess_text(text)
        
        # Handle empty preprocessed text
        if not processed_text or processed_text.strip() == "":
            return {
                "is_spam": True,
                "reason_category": "Other",
                "severity_score": 0.0
            }
        
        # Vectorize
        X = self.vectorizer.transform([processed_text])
        
        # Predict
        category = self.model.predict(X)[0]
        
        # Get confidence scores
        proba = self.model.predict_proba(X)[0]
        confidence = float(np.max(proba))
        
        # Get severity
        severity = SEVERITY_MAP.get(category, 0.2)
        
        return {
            "is_spam": False,
            "reason_category": category,
            "severity_score": severity,
            "confidence": confidence
        }
    
    def predict_batch(self, texts: list[str]) -> list[Dict[str, any]]:
        """
        Predict categories for multiple texts.
        
        Args:
            texts: List of texts to classify
            
        Returns:
            List of prediction dictionaries
        """
        return [self.predict(text) for text in texts]
    
    def save_models(self, model_path: str, vectorizer_path: str):
        """
        Save trained model and vectorizer to disk.
        
        Args:
            model_path: Path to save model
            vectorizer_path: Path to save vectorizer
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        # Create directory if needed
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        Path(vectorizer_path).parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)
        
        logger.info(f"Model saved to: {model_path}")
        logger.info(f"Vectorizer saved to: {vectorizer_path}")
    
    def load_models(self, model_path: str, vectorizer_path: str):
        """
        Load trained model and vectorizer from disk.
        
        Args:
            model_path: Path to saved model
            vectorizer_path: Path to saved vectorizer
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(vectorizer_path):
            raise FileNotFoundError(f"Vectorizer file not found: {vectorizer_path}")
        
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
        self.is_trained = True
        
        logger.info(f"Model loaded from: {model_path}")
        logger.info(f"Vectorizer loaded from: {vectorizer_path}")


def get_severity_score(category: str) -> float:
    """
    Get severity score for a category.
    
    Args:
        category: Category name
        
    Returns:
        Severity score (0.0 to 1.0)
    """
    return SEVERITY_MAP.get(category, 0.2)


if __name__ == "__main__":
    # Test the classifier with sample data
    print("NLP Classifier module loaded successfully.")
    print(f"Valid categories: {VALID_CATEGORIES}")
    print(f"\nSeverity mapping:")
    for category, score in SEVERITY_MAP.items():
        print(f"  {category}: {score}")
