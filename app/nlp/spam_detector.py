"""
Rule-based spam detection module.
Identifies meaningless or low-quality input before classification.
"""
import re
from typing import Set

# Spam patterns - exact matches (case-insensitive)
SPAM_EXACT_MATCHES: Set[str] = {
    "no reason",
    "none",
    "return",
    "n/a",
    "na",
    "nothing",
    "no",
    "idk",
    "don't know",
    "dont know",
    "unknown",
    "not sure",
    ".",
    "-",
    "...",
    "?",
    "??",
}

# Spam patterns - substrings
SPAM_SUBSTRINGS: Set[str] = {
    "zzz",
    "asdf",
    "qwerty",
    "test",
    "testing",
}

# Minimum meaningful text length
MIN_TEXT_LENGTH = 3
MIN_WORD_COUNT = 1


def is_empty_or_whitespace(text: str) -> bool:
    """
    Check if text is empty or contains only whitespace.
    
    Args:
        text: Input text string
        
    Returns:
        True if empty or whitespace only
    """
    return not text or text.strip() == ""


def is_too_short(text: str) -> bool:
    """
    Check if text is too short to be meaningful.
    
    Args:
        text: Input text string
        
    Returns:
        True if text is too short
    """
    cleaned = text.strip()
    return len(cleaned) < MIN_TEXT_LENGTH


def has_too_few_words(text: str) -> bool:
    """
    Check if text has too few words.
    
    Args:
        text: Input text string
        
    Returns:
        True if too few words
    """
    words = re.findall(r"\b\w+\b", text)
    return len(words) < MIN_WORD_COUNT


def is_exact_spam_match(text: str) -> bool:
    """
    Check if text exactly matches known spam patterns.
    
    Args:
        text: Input text string
        
    Returns:
        True if exact spam match
    """
    cleaned = text.strip().lower()
    return cleaned in SPAM_EXACT_MATCHES


def contains_spam_substring(text: str) -> bool:
    """
    Check if text contains spam substrings.
    
    Args:
        text: Input text string
        
    Returns:
        True if contains spam substring
    """
    cleaned = text.strip().lower()
    return any(spam in cleaned for spam in SPAM_SUBSTRINGS)


def is_repetitive_chars(text: str) -> bool:
    """
    Check if text is mostly repetitive characters.
    
    Args:
        text: Input text string
        
    Returns:
        True if mostly repetitive
        
    Example:
        >>> is_repetitive_chars("aaaaaaa")
        True
        >>> is_repetitive_chars("hello world")
        False
    """
    cleaned = text.strip().lower()
    if len(cleaned) < 3:
        return True
    
    # Check if more than 70% of text is the same character
    max_char_count = max((cleaned.count(char) for char in set(cleaned)), default=0)
    return max_char_count / len(cleaned) > 0.7


def is_only_special_chars(text: str) -> bool:
    """
    Check if text contains only special characters and no letters.
    
    Args:
        text: Input text string
        
    Returns:
        True if only special characters
    """
    return not re.search(r"[a-zA-Z]", text)


def is_spam(text: str, verbose: bool = False) -> bool:
    """
    Comprehensive spam detection using multiple rules.
    
    This function checks multiple spam indicators:
    - Empty or whitespace only
    - Too short text
    - Too few words
    - Exact spam matches
    - Spam substrings
    - Repetitive characters
    - Only special characters
    
    Args:
        text: Input text to check
        verbose: If True, print which rule triggered (default: False)
        
    Returns:
        True if text is spam, False otherwise
        
    Example:
        >>> is_spam("no reason")
        True
        >>> is_spam("Item arrived broken")
        False
    """
    if not isinstance(text, str):
        return True
    
    checks = [
        (is_empty_or_whitespace, "Empty or whitespace"),
        (is_too_short, "Too short"),
        (has_too_few_words, "Too few words"),
        (is_exact_spam_match, "Exact spam match"),
        (contains_spam_substring, "Contains spam substring"),
        (is_repetitive_chars, "Repetitive characters"),
        (is_only_special_chars, "Only special characters"),
    ]
    
    for check_func, reason in checks:
        if check_func(text):
            if verbose:
                print(f"Spam detected: {reason} - '{text}'")
            return True
    
    return False


def filter_spam(texts: list[str]) -> list[tuple[str, bool]]:
    """
    Filter a batch of texts for spam.
    
    Args:
        texts: List of text strings
        
    Returns:
        List of tuples (text, is_spam)
    """
    return [(text, is_spam(text)) for text in texts]


if __name__ == "__main__":
    # Test spam detection
    test_cases = [
        ("Item was broken", False),
        ("no reason", True),
        ("", True),
        ("none", True),
        ("return", True),
        ("The packaging was damaged", False),
        (".", True),
        ("zzzzz", True),
        ("test", True),
        ("Product quality is poor", False),
        ("?", True),
        ("a", True),
        ("asdfasdf", True),
    ]
    
    print("Testing spam detection:\n")
    for text, expected_spam in test_cases:
        result = is_spam(text, verbose=False)
        status = "✓" if result == expected_spam else "✗"
        print(f"{status} '{text}' -> Spam: {result} (Expected: {expected_spam})")
