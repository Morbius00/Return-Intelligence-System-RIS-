"""
Text classification module using TF-IDF and Logistic Regression.
Classifies customer feedback into sentiment (Positive / Negative / Neutral)
and then assigns an issue category + Severity Score (for negative feedback)
or a satisfaction category + Goodwill Score (for positive feedback).
"""
import os
import logging
from typing import Dict, Optional, Set, Tuple
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

# ---------------------------------------------------------------------------
# Negative feedback: Issue category → Severity Score
# ---------------------------------------------------------------------------
SEVERITY_MAP: Dict[str, float] = {
    "Product Quality Issue": 0.9,
    "Expiry Issue":          0.9,
    "Packaging Issue":       0.6,
    "Wrong Item":            0.6,
    "Customer Preference":   0.3,
    "Other":                 0.2,
    "Uncertain":             0.1,
}

# ---------------------------------------------------------------------------
# Positive feedback: Satisfaction category → Goodwill Score
# ---------------------------------------------------------------------------
GOODWILL_MAP: Dict[str, float] = {
    "Product Appreciation":        0.9,
    "Overall Positive Experience": 0.85,
    "Service Satisfaction":        0.8,
    "Packaging Praise":            0.7,
    "General Positive":            0.6,
}

# ---------------------------------------------------------------------------
# Keyword sets for rule-based sentiment detection
# ---------------------------------------------------------------------------
POSITIVE_KEYWORDS: Set[str] = {
    "excellent", "great", "good", "amazing", "love", "loved", "perfect",
    "outstanding", "happy", "satisfied", "recommended", "recommend",
    "impressed", "impressive", "best", "fantastic", "wonderful", "awesome",
    "brilliant", "superb", "delighted", "pleased", "smooth", "fast",
    "quick", "efficient", "well", "beautiful", "sturdy", "durable",
    "useful", "worth", "value", "premium", "reliable", "comfortable",
    "nice", "fresh", "safe", "top-notch",
}

NEGATIVE_KEYWORDS: Set[str] = {
    "broken", "damaged", "defective", "poor", "terrible", "bad", "wrong",
    "disappointed", "expired", "torn", "crushed", "cheap", "worst",
    "failed", "stopped", "issue", "problem", "defect", "awful",
    "horrible", "useless", "not working", "not satisfied", "unhappy",
    "incorrect", "mismatch", "deteriorated", "rotten", "stale", "leaked",
    "rusted", "faulty",
}

# Words that negate the sentiment of the keyword that follows them
_NEGATION_PREFIXES = (
    "not ", "no ", "never ", "don't ", "doesn't ", "didn't ",
    "wasn't ", "isn't ", "won't ", "can't ", "couldn't ", "shouldn't ",
    "hardly ", "barely ",
)

# Minimum confidence threshold
MIN_CONFIDENCE_THRESHOLD = 0.20

# Exported category lists
NEGATIVE_CATEGORIES = list(SEVERITY_MAP.keys())
POSITIVE_CATEGORIES = list(GOODWILL_MAP.keys())
VALID_CATEGORIES = NEGATIVE_CATEGORIES + POSITIVE_CATEGORIES


# ---------------------------------------------------------------------------
# Sentiment detection (rule-based, optionally assisted by rating)
# ---------------------------------------------------------------------------

def _count_keyword_hits(text_lower: str) -> Tuple[int, int]:
    """
    Count positive and negative keyword hits with basic negation awareness.

    Negation handling
    -----------------
    • "not good"   → the positive hit is flipped to a negative hit.
    • "not broken" → the negative hit is flipped to a positive hit.
    • Multi-word negative keywords (e.g., "not working") are never
      double-flipped because the guard ``' ' not in kw`` skips them.

    Returns (pos_hits, neg_hits).
    """
    pos_hits = 0
    neg_hits = 0

    # -- Count raw keyword hits ----------------------------------------
    for kw in POSITIVE_KEYWORDS:
        if kw in text_lower:
            pos_hits += 1
    for kw in NEGATIVE_KEYWORDS:
        if kw in text_lower:
            neg_hits += 1

    # -- Adjust for negation patterns ----------------------------------
    for prefix in _NEGATION_PREFIXES:
        # "not <positive_word>"  →  flip positive → negative
        for kw in POSITIVE_KEYWORDS:
            if prefix + kw in text_lower:
                pos_hits = max(0, pos_hits - 1)
                neg_hits += 1

        # "not <negative_word>"  →  flip negative → positive
        # (skip multi-word keywords to avoid double-counting)
        for kw in NEGATIVE_KEYWORDS:
            if " " not in kw and prefix + kw in text_lower:
                neg_hits = max(0, neg_hits - 1)
                pos_hits += 1

    return pos_hits, neg_hits


def detect_sentiment(text: str, rating: Optional[int] = None) -> str:
    """
    Detect sentiment of customer feedback.

    Strategy  (text-first approach)
    --------------------------------
    1. **TEXT is the primary signal** — it is the actual feedback content.
       Positive / negative keyword hits (with basic negation awareness)
       determine the sentiment whenever the text gives a clear signal.
    2. **Rating is the tiebreaker** — used only when the text is ambiguous
       (equal positive and negative hits, or no hits at all).
       • 4-5  → Positive
       • 1-2  → Negative
       • 3    → Neutral
    3. If neither text nor rating provides a signal → Neutral.

    Returns
    -------
    "Positive" | "Negative" | "Neutral"
    """
    if not text or not isinstance(text, str):
        return "Neutral"

    text_lower = text.lower()

    # ---- Step 1: Text keyword analysis (PRIMARY signal) ----
    pos_hits, neg_hits = _count_keyword_hits(text_lower)

    if pos_hits > neg_hits:
        return "Positive"
    if neg_hits > pos_hits:
        return "Negative"

    # ---- Step 2: Text is ambiguous → rating as tiebreaker ----
    if rating is not None:
        try:
            r = int(rating)
            if r >= 4:
                return "Positive"
            if r <= 2:
                return "Negative"
        except (ValueError, TypeError):
            pass

    return "Neutral"


# ---------------------------------------------------------------------------
# Main classifier class
# ---------------------------------------------------------------------------

class FeedbackClassifier:
    """
    Dual-model NLP Classifier for customer feedback.

    Pipeline
    --------
    1. Spam detection (rule-based)
    2. Sentiment detection (rule-based, optionally rating-assisted)
    3. Negative path → Logistic Regression → issue category + Severity Score
    4. Positive path → Logistic Regression → satisfaction category + Goodwill Score
    5. Neutral path → scores are None
    """

    def __init__(
        self,
        neg_model_path: Optional[str] = None,
        neg_vectorizer_path: Optional[str] = None,
        pos_model_path: Optional[str] = None,
        pos_vectorizer_path: Optional[str] = None,
        max_features: int = 1000,
        ngram_range: Tuple[int, int] = (1, 2),
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range

        # Negative (issue) sub-model
        self.neg_vectorizer: Optional[TfidfVectorizer] = None
        self.neg_model: Optional[LogisticRegression] = None

        # Positive (satisfaction) sub-model
        self.pos_vectorizer: Optional[TfidfVectorizer] = None
        self.pos_model: Optional[LogisticRegression] = None

        self.is_trained = False

        if neg_model_path and neg_vectorizer_path:
            self.load_negative_model(neg_model_path, neg_vectorizer_path)
        if pos_model_path and pos_vectorizer_path:
            self.load_positive_model(pos_model_path, pos_vectorizer_path)

        if self.neg_model and self.pos_model:
            self.is_trained = True

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def _build_model(self) -> LogisticRegression:
        return LogisticRegression(
            max_iter=1000, random_state=42,
            class_weight="balanced", solver="lbfgs",
        )

    def _build_vectorizer(self) -> TfidfVectorizer:
        return TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=1, max_df=0.95,
        )

    def train(
        self,
        texts: list,
        sentiments: list,
        categories: list,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, object]:
        """
        Train both the negative and positive sub-models.

        Parameters
        ----------
        texts       : list[str]  – customer feedback strings
        sentiments  : list[str]  – "Positive" | "Negative" | "Neutral"
        categories  : list[str]  – issue / satisfaction category labels
        """
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report

        metrics: Dict[str, object] = {}

        # ---- Negative sub-model ----------------------------------------
        neg_mask   = [s == "Negative" for s in sentiments]
        neg_texts  = [t for t, m in zip(texts, neg_mask) if m]
        neg_labels = [c for c, m in zip(categories, neg_mask) if m]
        logger.info(f"Negative training samples: {len(neg_texts)}")
        processed_neg = [preprocess_text(t) for t in neg_texts]

        if len(set(neg_labels)) >= 2:
            X_tr_n, X_te_n, y_tr_n, y_te_n = train_test_split(
                processed_neg, neg_labels,
                test_size=test_size, random_state=random_state,
                stratify=neg_labels,
            )
            self.neg_vectorizer = self._build_vectorizer()
            Xtr = self.neg_vectorizer.fit_transform(X_tr_n)
            Xte = self.neg_vectorizer.transform(X_te_n)
            self.neg_model = self._build_model()
            self.neg_model.fit(Xtr, y_tr_n)
            y_pred = self.neg_model.predict(Xte)
            neg_acc = accuracy_score(y_te_n, y_pred)
            logger.info(f"Negative model accuracy: {neg_acc:.4f}")
            logger.info(classification_report(y_te_n, y_pred))
            metrics["negative_accuracy"]      = neg_acc
            metrics["negative_train_samples"] = len(X_tr_n)
            metrics["negative_test_samples"]  = len(X_te_n)
        else:
            self.neg_vectorizer = self._build_vectorizer()
            self.neg_model = self._build_model()
            self.neg_model.fit(self.neg_vectorizer.fit_transform(processed_neg), neg_labels)
            metrics["negative_accuracy"] = "N/A (no test split)"

        # ---- Positive sub-model ----------------------------------------
        pos_mask   = [s == "Positive" for s in sentiments]
        pos_texts  = [t for t, m in zip(texts, pos_mask) if m]
        pos_labels = [c for c, m in zip(categories, pos_mask) if m]
        logger.info(f"Positive training samples: {len(pos_texts)}")
        processed_pos = [preprocess_text(t) for t in pos_texts]

        if len(set(pos_labels)) >= 2:
            X_tr_p, X_te_p, y_tr_p, y_te_p = train_test_split(
                processed_pos, pos_labels,
                test_size=test_size, random_state=random_state,
                stratify=pos_labels,
            )
            self.pos_vectorizer = self._build_vectorizer()
            Xtr = self.pos_vectorizer.fit_transform(X_tr_p)
            Xte = self.pos_vectorizer.transform(X_te_p)
            self.pos_model = self._build_model()
            self.pos_model.fit(Xtr, y_tr_p)
            y_pred = self.pos_model.predict(Xte)
            pos_acc = accuracy_score(y_te_p, y_pred)
            logger.info(f"Positive model accuracy: {pos_acc:.4f}")
            logger.info(classification_report(y_te_p, y_pred))
            metrics["positive_accuracy"]      = pos_acc
            metrics["positive_train_samples"] = len(X_tr_p)
            metrics["positive_test_samples"]  = len(X_te_p)
        else:
            self.pos_vectorizer = self._build_vectorizer()
            self.pos_model = self._build_model()
            self.pos_model.fit(self.pos_vectorizer.fit_transform(processed_pos), pos_labels)
            metrics["positive_accuracy"] = "N/A (no test split)"

        self.is_trained = True
        return metrics

    # ------------------------------------------------------------------
    # Inference helpers
    # ------------------------------------------------------------------

    def _classify_negative(self, text: str) -> Tuple[str, float]:
        processed = preprocess_text(text)
        if not processed.strip():
            return "Other", 0.0
        X = self.neg_vectorizer.transform([processed])
        category   = self.neg_model.predict(X)[0]
        confidence = float(np.max(self.neg_model.predict_proba(X)[0]))
        if confidence < MIN_CONFIDENCE_THRESHOLD:
            return "Uncertain", confidence
        return category, confidence

    def _classify_positive(self, text: str) -> Tuple[str, float]:
        processed = preprocess_text(text)
        if not processed.strip():
            return "General Positive", 0.0
        X = self.pos_vectorizer.transform([processed])
        category   = self.pos_model.predict(X)[0]
        confidence = float(np.max(self.pos_model.predict_proba(X)[0]))
        if confidence < MIN_CONFIDENCE_THRESHOLD:
            return "General Positive", confidence
        return category, confidence

    # ------------------------------------------------------------------
    # Public prediction API
    # ------------------------------------------------------------------

    def predict(
        self,
        customer_feedback: str,
        rating: Optional[int] = None,
    ) -> Dict[str, object]:
        """
        Classify a single customer feedback entry.

        Returns
        -------
        {
            "is_spam"              : bool,
            "sentiment_type"       : "Positive" | "Negative" | "Neutral",
            "issue_category"       : str | None,
            "severity_score"       : float | None,
            "satisfaction_category": str | None,
            "goodwill_score"       : float | None,
            "confidence"           : float | None,
        }
        """
        if is_spam(customer_feedback):
            return {
                "is_spam": True,
                "sentiment_type": "Neutral",
                "issue_category": None, "severity_score": None,
                "satisfaction_category": None, "goodwill_score": None,
                "confidence": None,
            }

        if not self.is_trained:
            raise ValueError(
                "Models are not trained. Run train.py first."
            )

        sentiment = detect_sentiment(customer_feedback, rating)

        if sentiment == "Negative":
            issue_cat, confidence = self._classify_negative(customer_feedback)
            return {
                "is_spam": False,
                "sentiment_type": "Negative",
                "issue_category": issue_cat,
                "severity_score": SEVERITY_MAP.get(issue_cat, 0.2),
                "satisfaction_category": None,
                "goodwill_score": None,
                "confidence": confidence,
            }

        if sentiment == "Positive":
            sat_cat, confidence = self._classify_positive(customer_feedback)
            return {
                "is_spam": False,
                "sentiment_type": "Positive",
                "issue_category": None,
                "severity_score": None,
                "satisfaction_category": sat_cat,
                "goodwill_score": GOODWILL_MAP.get(sat_cat, 0.6),
                "confidence": confidence,
            }

        # Neutral — run both models and report the higher-confidence result
        # so the user still gets a category even for ambiguous feedback.
        neg_cat, neg_conf = self._classify_negative(customer_feedback)
        pos_cat, pos_conf = self._classify_positive(customer_feedback)

        if neg_conf > pos_conf and neg_conf >= MIN_CONFIDENCE_THRESHOLD:
            return {
                "is_spam": False,
                "sentiment_type": "Neutral",
                "issue_category": neg_cat,
                "severity_score": SEVERITY_MAP.get(neg_cat, 0.2),
                "satisfaction_category": None,
                "goodwill_score": None,
                "confidence": neg_conf,
            }
        if pos_conf >= MIN_CONFIDENCE_THRESHOLD:
            return {
                "is_spam": False,
                "sentiment_type": "Neutral",
                "issue_category": None,
                "severity_score": None,
                "satisfaction_category": pos_cat,
                "goodwill_score": GOODWILL_MAP.get(pos_cat, 0.6),
                "confidence": pos_conf,
            }

        return {
            "is_spam": False,
            "sentiment_type": "Neutral",
            "issue_category": None, "severity_score": None,
            "satisfaction_category": None, "goodwill_score": None,
            "confidence": None,
        }

    def predict_batch(
        self,
        feedbacks: list,
        ratings: Optional[list] = None,
    ) -> list:
        """Classify a batch of customer feedback entries."""
        if ratings is None:
            ratings = [None] * len(feedbacks)
        return [self.predict(fb, r) for fb, r in zip(feedbacks, ratings)]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_models(
        self,
        neg_model_path: str,
        neg_vectorizer_path: str,
        pos_model_path: str,
        pos_vectorizer_path: str,
    ):
        """Persist all four artefacts to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained models.")
        for path in [neg_model_path, neg_vectorizer_path,
                     pos_model_path, pos_vectorizer_path]:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.neg_model,      neg_model_path)
        joblib.dump(self.neg_vectorizer, neg_vectorizer_path)
        joblib.dump(self.pos_model,      pos_model_path)
        joblib.dump(self.pos_vectorizer, pos_vectorizer_path)
        logger.info("All four model artefacts saved.")

    def load_negative_model(self, model_path: str, vectorizer_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        if not os.path.exists(vectorizer_path):
            raise FileNotFoundError(f"Vectorizer not found: {vectorizer_path}")
        self.neg_model      = joblib.load(model_path)
        self.neg_vectorizer = joblib.load(vectorizer_path)
        logger.info(f"Negative model loaded from: {model_path}")

    def load_positive_model(self, model_path: str, vectorizer_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        if not os.path.exists(vectorizer_path):
            raise FileNotFoundError(f"Vectorizer not found: {vectorizer_path}")
        self.pos_model      = joblib.load(model_path)
        self.pos_vectorizer = joblib.load(vectorizer_path)
        logger.info(f"Positive model loaded from: {model_path}")


# ---------------------------------------------------------------------------
# Backward-compatible alias
# ---------------------------------------------------------------------------
NLPClassifier = FeedbackClassifier


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def get_severity_score(category: str) -> float:
    """Return severity score for a negative issue category."""
    return SEVERITY_MAP.get(category, 0.2)


def get_goodwill_score(category: str) -> float:
    """Return goodwill score for a positive satisfaction category."""
    return GOODWILL_MAP.get(category, 0.6)


if __name__ == "__main__":
    print("FeedbackClassifier module loaded successfully.")
    print("\nNegative categories (Severity):")
    for cat, score in SEVERITY_MAP.items():
        print(f"  {cat}: {score}")
    print("\nPositive categories (Goodwill):")
    for cat, score in GOODWILL_MAP.items():
        print(f"  {cat}: {score}")

