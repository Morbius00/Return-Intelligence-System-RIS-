import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 1. Setup Mocks for external dependencies
mock_np = MagicMock()
# Configure np.max to return the actual max of the input list
mock_np.max.side_effect = lambda x: max(x)

sys.modules['numpy'] = mock_np
sys.modules['app.nlp.preprocess'] = MagicMock()
sys.modules['app.nlp.spam_detector'] = MagicMock()
sys.modules['nltk'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()
sys.modules['sklearn.linear_model'] = MagicMock()
sys.modules['joblib'] = MagicMock()

# 2. Import module under test
import app.nlp.classifier
from app.nlp.classifier import NLPClassifier

def test_fix():
    print("Testing Confidence Threshold Fix...")
    
    # Create a mock instance for the vectorizer and model
    mock_vectorizer = MagicMock()
    mock_model = MagicMock()
    
    # Setup the mock model to return low confidence
    # predict_proba returns a list of probabilities for each class
    # We want max probability to be < 0.4 (e.g., 0.3)
    mock_model.predict_proba.return_value = [[0.25, 0.3, 0.2, 0.25]]
    mock_model.predict.return_value = ["Customer Preference"]
    
    # Initialize classifier without loading from file
    classifier = NLPClassifier() 
    classifier.vectorizer = mock_vectorizer
    classifier.model = mock_model
    classifier.is_trained = True
    
    # Patch the helper functions used in predict
    with patch('app.nlp.classifier.is_spam', return_value=False), \
         patch('app.nlp.classifier.preprocess_text', return_value="the cow is a bird"):
        
        text = "The Cow is a Bird"
        print(f"Testing input: '{text}'")
        
        # Run prediction
        try:
            result = classifier.predict(text)
            
            print("\nResult:")
            print(f"Category: {result['reason_category']}")
            print(f"Severity: {result['severity_score']}")
            print(f"Confidence: {result['confidence']:.4f}")
            
            # Assertions
            if result['reason_category'] == "Uncertain" and result['severity_score'] == 0.1:
                print("\n✅ SUCCESS: Input correctly classified as Uncertain with 0.1 severity.")
            else:
                print("\n❌ FAILURE: Unexpected result.")
                print(f"   Expected: Category='Uncertain', Severity=0.1")
                print(f"   Got:      Category='{result['reason_category']}', Severity={result['severity_score']}")
                
        except Exception as e:
            print(f"\n❌ ERROR: Validation crashed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_fix()
