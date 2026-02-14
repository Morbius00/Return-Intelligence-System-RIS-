"""
API Test Script
Demonstrates how to use the NLP API for predictions.
"""
import requests
import json
from typing import Dict, List

# API Configuration
API_BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint."""
    print("\n" + "="*60)
    print("Testing Health Check")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_single_prediction(return_reason: str):
    """Test single prediction endpoint."""
    print("\n" + "="*60)
    print("Testing Single Prediction")
    print("="*60)
    
    data = {"return_reason": return_reason}
    print(f"Input: {return_reason}")
    
    response = requests.post(
        f"{API_BASE_URL}/predict",
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nResults:")
        print(f"  Category: {result['reason_category']}")
        print(f"  Severity: {result['severity_score']}")
        print(f"  Is Spam: {result['is_spam']}")
        if 'confidence' in result:
            print(f"  Confidence: {result['confidence']:.2%}")
    else:
        print(f"Error: {response.text}")


def test_batch_prediction(return_reasons: List[str]):
    """Test batch prediction endpoint."""
    print("\n" + "="*60)
    print("Testing Batch Prediction")
    print("="*60)
    
    data = {"return_reasons": return_reasons}
    print(f"Input: {len(return_reasons)} items")
    
    response = requests.post(
        f"{API_BASE_URL}/predict/batch",
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nTotal Predictions: {result['total']}")
        print("\nResults:")
        for i, (text, pred) in enumerate(zip(return_reasons, result['predictions']), 1):
            print(f"\n{i}. {text}")
            print(f"   → {pred['reason_category']} (Severity: {pred['severity_score']})")
            if pred['is_spam']:
                print(f"   → [SPAM DETECTED]")
    else:
        print(f"Error: {response.text}")


def test_get_categories():
    """Test get categories endpoint."""
    print("\n" + "="*60)
    print("Testing Get Categories")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/categories")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nCategories:")
        for category, severity in result['severity_mapping'].items():
            print(f"  - {category}: {severity}")


def test_preprocess(text: str):
    """Test preprocessing endpoint."""
    print("\n" + "="*60)
    print("Testing Text Preprocessing")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE_URL}/preprocess",
        params={"text": text}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\nOriginal: {result['original']}")
        print(f"Preprocessed: {result['preprocessed']}")
        print(f"Is Spam: {result['is_spam']}")


def main():
    """Run all API tests."""
    print("="*60)
    print("NLP API Test Suite")
    print("="*60)
    print("\nMake sure the API server is running:")
    print("  python -m uvicorn app.main:app --reload")
    print("\nStarting tests...")
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Get categories
        test_get_categories()
        
        # Test 3: Single predictions
        test_cases = [
            "Item arrived completely broken",
            "Wrong product was sent to me",
            "Product is already expired",
            "Package was damaged in transit",
            "I changed my mind about this purchase",
            "no reason",
        ]
        
        for test_case in test_cases:
            test_single_prediction(test_case)
        
        # Test 4: Batch prediction
        batch_cases = [
            "Quality is very poor",
            "Expiry date has passed",
            "Wrong size delivered",
            "Don't need it anymore",
            "test"
        ]
        test_batch_prediction(batch_cases)
        
        # Test 5: Preprocessing
        test_preprocess("Item was BROKEN!!! Completely unusable.")
        
        print("\n" + "="*60)
        print("✓ All Tests Complete!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server.")
        print("Please ensure the server is running on http://localhost:8000")
        print("\nStart the server with:")
        print("  python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
