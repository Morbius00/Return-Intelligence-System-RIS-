"""
NLP module for text preprocessing and classification.
"""
from .preprocess import preprocess_text
from .spam_detector import is_spam
from .classifier import NLPClassifier

__all__ = ["preprocess_text", "is_spam", "NLPClassifier"]
