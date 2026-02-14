"""
Text preprocessing module using NLTK.
Provides clean, reusable NLP preprocessing pipeline.
"""
import re
import string
from typing import List, Optional
import logging

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure NLTK resources are downloaded
def download_nltk_resources():
    """Download required NLTK resources if not already present."""
    resources = [
        "punkt",
        "punkt_tab",
        "stopwords",
        "wordnet",
        "omw-1.4",
        "averaged_perceptron_tagger"
    ]
    for resource in resources:
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            try:
                nltk.data.find(f"corpora/{resource}")
            except LookupError:
                logger.info(f"Downloading NLTK resource: {resource}")
                nltk.download(resource, quiet=True)

# Download resources on module import
download_nltk_resources()

# Initialize NLTK components
STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


def remove_punctuation(text: str) -> str:
    """
    Remove punctuation from text.
    
    Args:
        text: Input text string
        
    Returns:
        Text with punctuation removed
    """
    return text.translate(str.maketrans("", "", string.punctuation))


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace from text.
    
    Args:
        text: Input text string
        
    Returns:
        Text with normalized whitespace
    """
    return re.sub(r"\s+", " ", text).strip()


def remove_numbers(text: str) -> str:
    """
    Remove standalone numbers from text.
    
    Args:
        text: Input text string
        
    Returns:
        Text with numbers removed
    """
    return re.sub(r"\b\d+\b", "", text)


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words using NLTK.
    
    Args:
        text: Input text string
        
    Returns:
        List of tokens
    """
    return word_tokenize(text)


def remove_stopwords(tokens: List[str]) -> List[str]:
    """
    Remove English stopwords from token list.
    
    Args:
        tokens: List of word tokens
        
    Returns:
        List of tokens without stopwords
    """
    return [token for token in tokens if token.lower() not in STOP_WORDS]


def lemmatize_tokens(tokens: List[str]) -> List[str]:
    """
    Lemmatize tokens using WordNet lemmatizer.
    
    Args:
        tokens: List of word tokens
        
    Returns:
        List of lemmatized tokens
    """
    return [LEMMATIZER.lemmatize(token.lower()) for token in tokens]


def preprocess_text(
    text: str,
    lowercase: bool = True,
    remove_punct: bool = True,
    remove_nums: bool = True,
    remove_stops: bool = True,
    lemmatize: bool = True,
    min_token_length: int = 2
) -> str:
    """
    Complete NLP preprocessing pipeline.
    
    This function applies a series of preprocessing steps:
    1. Lowercase conversion
    2. Remove punctuation
    3. Remove numbers
    4. Remove extra whitespace
    5. Tokenization
    6. Remove stopwords
    7. Lemmatization
    8. Filter short tokens
    
    Args:
        text: Input text to preprocess
        lowercase: Convert to lowercase (default: True)
        remove_punct: Remove punctuation (default: True)
        remove_nums: Remove numbers (default: True)
        remove_stops: Remove stopwords (default: True)
        lemmatize: Apply lemmatization (default: True)
        min_token_length: Minimum token length to keep (default: 2)
        
    Returns:
        Preprocessed text as a single string
        
    Example:
        >>> preprocess_text("Item was BROKEN!!! Arrived damaged.")
        'item broken arrive damaged'
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Lowercase
    if lowercase:
        text = text.lower()
    
    # Remove punctuation
    if remove_punct:
        text = remove_punctuation(text)
    
    # Remove numbers
    if remove_nums:
        text = remove_numbers(text)
    
    # Remove extra whitespace
    text = remove_extra_whitespace(text)
    
    # Tokenization
    tokens = tokenize(text)
    
    # Remove stopwords
    if remove_stops:
        tokens = remove_stopwords(tokens)
    
    # Lemmatization
    if lemmatize:
        tokens = lemmatize_tokens(tokens)
    
    # Filter short tokens
    tokens = [token for token in tokens if len(token) >= min_token_length]
    
    # Join back to string
    return " ".join(tokens)


def preprocess_batch(texts: List[str], **kwargs) -> List[str]:
    """
    Preprocess a batch of texts.
    
    Args:
        texts: List of text strings
        **kwargs: Arguments to pass to preprocess_text
        
    Returns:
        List of preprocessed texts
    """
    return [preprocess_text(text, **kwargs) for text in texts]


if __name__ == "__main__":
    # Test the preprocessing pipeline
    test_texts = [
        "Item was BROKEN!!! Arrived damaged.",
        "Wrong product sent to me",
        "The packaging was torn and product was expired",
        "I just don't like it",
        "no reason"
    ]
    
    print("Testing preprocessing pipeline:\n")
    for text in test_texts:
        processed = preprocess_text(text)
        print(f"Original: {text}")
        print(f"Processed: {processed}\n")
