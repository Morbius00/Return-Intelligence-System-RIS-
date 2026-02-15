"""
Quick test for the new /sheets/process endpoint
"""
import requests

API_BASE_URL = "http://localhost:8000"

# Your spreadsheet details
SPREADSHEET_ID = "1qaLtpbxOWbTyfonKmEqCsRYqnvfQp3NZ5Xsk7JlIEcg"
WORKSHEET_NAME = "Sheet1"
REASON_COLUMN = "reason"

print("=" * 60)
print("  Testing Google Sheets Process Endpoint")
print("=" * 60)
print()

# Test health first
print("1. Checking API health...")
try:
    response = requests.get(f"{API_BASE_URL}/health")
    health = response.json()
    print(f"   ✅ API Status: {health['status']}")
    print(f"   ✅ Model Loaded: {health['model_loaded']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Make sure the API server is running!")
    exit(1)

print()
print("2. Processing existing Google Sheet...")
print(f"   Spreadsheet ID: {SPREADSHEET_ID}")
print(f"   Worksheet: {WORKSHEET_NAME}")
print(f"   Reason Column: {REASON_COLUMN}")
print()

try:
    payload = {
        "spreadsheet_id": SPREADSHEET_ID,
        "worksheet_name": WORKSHEET_NAME,
        "reason_column": REASON_COLUMN
    }
    
    response = requests.post(
        f"{API_BASE_URL}/sheets/process",
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print("   ✅ SUCCESS!")
        print(f"   Rows Processed: {result['rows_processed']}")
        print(f"   Message: {result['message']}")
        print()
        print(f"   📊 View your updated sheet:")
        print(f"   {result['spreadsheet_url']}")
        print()
        print("   New columns added:")
        print("   - return_category")
        print("   - return_severity")
        print("   - return_confidence")
        print("   - is_spam")
        print("   - processed_at")
    else:
        error_detail = response.json().get('detail', 'Unknown error')
        print(f"   ❌ Error {response.status_code}: {error_detail}")
        
        if "not found" in error_detail.lower():
            print()
            print("   💡 Possible issues:")
            print("   - Column name might be different (check your sheet)")
            print("   - Sheet not shared with service account email")
            print("   - Worksheet name might be incorrect")
        elif "credentials" in error_detail.lower():
            print()
            print("   💡 Issue: Google Sheets credentials not configured")
            print("   - Check .env file has GOOGLE_CREDENTIALS_PATH set")
            print("   - Make sure credentials JSON file exists")

except requests.exceptions.Timeout:
    print("   ❌ Request timed out (sheet might be very large)")
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to API server")
    print("   Make sure it's running on http://localhost:8000")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

print()
print("=" * 60)
