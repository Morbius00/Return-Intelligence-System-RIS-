"""
Test script for Google Sheets integration.
This script tests both update and append endpoints.
"""
import requests
import json
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
SPREADSHEET_ID = ""  # ADD YOUR SPREADSHEET ID HERE
WORKSHEET_NAME = "Returns"  # Optional: change to your worksheet name or leave empty

# Test data
TEST_DATA = [
    {
        "order_id": "TEST001",
        "customer": "Alice Johnson",
        "reason": "Product arrived damaged during shipping"
    },
    {
        "order_id": "TEST002",
        "customer": "Bob Smith",
        "reason": "Received wrong color - ordered blue but got red"
    },
    {
        "order_id": "TEST003",
        "customer": "Carol White",
        "reason": "Item too small, need larger size"
    },
    {
        "order_id": "TEST004",
        "customer": "David Brown",
        "reason": "spam spam spam"
    },
    {
        "order_id": "TEST005",
        "customer": "Emma Davis",
        "reason": "Quality not as expected, material feels cheap"
    }
]


def test_health_check() -> bool:
    """Test if API is running and healthy."""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✅ API is healthy")
            print(f"   Model loaded: {data['model_loaded']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")
        print(f"   Make sure the API is running on {API_BASE_URL}")
        return False


def test_sheets_update() -> bool:
    """Test the /sheets/update endpoint."""
    print("\n🔍 Testing Google Sheets UPDATE endpoint...")
    
    if not SPREADSHEET_ID:
        print("❌ SPREADSHEET_ID not set. Please update the script with your Spreadsheet ID.")
        return False
    
    try:
        payload = {
            "spreadsheet_id": SPREADSHEET_ID,
            "worksheet_name": WORKSHEET_NAME if WORKSHEET_NAME else None,
            "data": TEST_DATA
        }
        
        response = requests.post(
            f"{API_BASE_URL}/sheets/update",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully updated Google Sheets")
            print(f"   Rows processed: {data['rows_processed']}")
            print(f"   Message: {data['message']}")
            print(f"   📊 View sheet: {data.get('spreadsheet_url', 'N/A')}")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_sheets_append() -> bool:
    """Test the /sheets/append endpoint."""
    print("\n🔍 Testing Google Sheets APPEND endpoint...")
    
    if not SPREADSHEET_ID:
        print("❌ SPREADSHEET_ID not set. Please update the script with your Spreadsheet ID.")
        return False
    
    try:
        # Create additional test data
        append_data = [
            {
                "order_id": "TEST006",
                "customer": "Frank Wilson",
                "reason": "Product broke after first use"
            },
            {
                "order_id": "TEST007",
                "customer": "Grace Lee",
                "reason": "Lost package, never received"
            }
        ]
        
        payload = {
            "spreadsheet_id": SPREADSHEET_ID,
            "worksheet_name": WORKSHEET_NAME if WORKSHEET_NAME else None,
            "data": append_data
        }
        
        response = requests.post(
            f"{API_BASE_URL}/sheets/append",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully appended to Google Sheets")
            print(f"   Rows processed: {data['rows_processed']}")
            print(f"   Message: {data['message']}")
            print(f"   📊 View sheet: {data.get('spreadsheet_url', 'N/A')}")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_single_prediction() -> bool:
    """Test single prediction endpoint to verify model is working."""
    print("\n🔍 Testing single prediction...")
    
    try:
        payload = {
            "return_reason": "The product arrived broken and damaged"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction successful")
            print(f"   Category: {data['reason_category']}")
            print(f"   Severity: {data['severity_score']}")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
            print(f"   Is Spam: {data['is_spam']}")
            return True
        else:
            print(f"❌ Prediction failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("   Google Sheets Integration Test Suite")
    print("=" * 60)
    
    # Configuration check
    if not SPREADSHEET_ID:
        print("\n⚠️  WARNING: SPREADSHEET_ID not configured!")
        print("   Please edit this script and add your Spreadsheet ID")
        print("   at the top of the file.\n")
    
    # Run tests
    results = {
        "Health Check": test_health_check(),
        "Single Prediction": test_single_prediction(),
        "Sheets Update": test_sheets_update(),
        "Sheets Append": test_sheets_append()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("   Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your Google Sheets integration is working perfectly!")
    elif SPREADSHEET_ID and results["Health Check"]:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("   Common issues:")
        print("   1. Sheet not shared with service account email")
        print("   2. Invalid Spreadsheet ID")
        print("   3. Google credentials not configured properly")
        print(f"\n   See GOOGLE_SHEETS_SETUP.md for detailed setup instructions.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
