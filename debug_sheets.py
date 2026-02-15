"""Debug script to test Google Sheets processing directly."""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.sheets_service import GoogleSheetsService
from app.nlp.classifier import NLPClassifier
import pandas as pd

def main():
    print("=" * 60)
    print("  Debug Google Sheets Processing")
    print("=" * 60)
    
    # Initialize services
    print("\n1. Initializing Google Sheets Service...")
    try:
        sheets_service = GoogleSheetsService()
        print("   ✅ Sheets service initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize sheets service: {e}")
        return
    
    print("\n2. Loading NLP Classifier...")
    try:
        from pathlib import Path
        model_dir = Path("app/models")
        model_path = model_dir / "model.pkl"
        vectorizer_path = model_dir / "tfidf.pkl"
        
        classifier = NLPClassifier(
            model_path=str(model_path),
            vectorizer_path=str(vectorizer_path)
        )
        print("   ✅ Classifier loaded")
    except Exception as e:
        print(f"   ❌ Failed to load classifier: {e}")
        return
    
    # Test with actual sheet
    spreadsheet_id = "1qaLtpbxOWbTyfonKmEqCsRYqnvfQp3NZ5Xsk7JlIEcg"
    worksheet_name = "Sheet1"
    reason_column = "reason"
    
    print(f"\n3. Checking available worksheets...")
    try:
        spreadsheet = sheets_service.client.open_by_key(spreadsheet_id)
        worksheets = spreadsheet.worksheets()
        print(f"   ✅ Found {len(worksheets)} worksheet(s):")
        for i, ws in enumerate(worksheets):
            print(f"     {i+1}. {ws.title}")
        
        # Check if "Returns" exists
        worksheet_names = [ws.title for ws in worksheets]
        if worksheet_name not in worksheet_names:
            print(f"\n   ⚠️  Worksheet '{worksheet_name}' not found!")
            print(f"   Please specify one of the available worksheets above.")
            return
    except Exception as e:
        print(f"   ❌ Failed to list worksheets: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n4. Reading sheet data...")
    print(f"   Spreadsheet ID: {spreadsheet_id}")
    print(f"   Worksheet: {worksheet_name}")
    try:
        df = sheets_service.read_sheet_to_dataframe(
            spreadsheet_id=spreadsheet_id,
            worksheet_name=worksheet_name
        )
        print(f"   ✅ Read {len(df)} rows")
        print(f"   Columns: {', '.join(df.columns.tolist())}")
        print(f"\n   First few rows:")
        print(df.head())
    except Exception as e:
        print(f"   ❌ Failed to read sheet: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n5. Checking reason column...")
    if reason_column not in df.columns:
        print(f"   ❌ Column '{reason_column}' not found!")
        print(f"   Available columns: {', '.join(df.columns.tolist())}")
        return
    else:
        print(f"   ✅ Found '{reason_column}' column")
    
    print(f"\n6. Processing reasons...")
    try:
        reasons = df[reason_column].fillna("").astype(str).tolist()
        print(f"   Processing {len(reasons)} reasons...")
        print(f"   Sample reasons: {reasons[:3]}")
        
        results = classifier.predict_batch(reasons)
        print(f"   ✅ Classified {len(results)} reasons")
        print(f"   Sample results:")
        for i, res in enumerate(results[:3]):
            print(f"     {i+1}. {reasons[i][:50]}... -> {res['reason_category']} (confidence: {res.get('confidence', 0):.2%})")
    except Exception as e:
        print(f"   ❌ Failed to classify: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n7. Preparing column updates...")
    try:
        updates = {
            'return_category': [res['reason_category'] for res in results],
            'return_severity': [round(res['severity_score'], 2) for res in results],
            'return_confidence': [f"{round(res.get('confidence', 0) * 100, 1)}%" for res in results],
            'is_spam': ['Yes' if res['is_spam'] else 'No' for res in results],
            'processed_at': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')] * len(results)
        }
        print(f"   ✅ Prepared {len(updates)} column updates")
        for col_name, values in updates.items():
            print(f"     - {col_name}: {len(values)} values")
    except Exception as e:
        print(f"   ❌ Failed to prepare updates: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n8. Writing updates to sheet...")
    try:
        sheets_service.update_columns(
            spreadsheet_id=spreadsheet_id,
            updates=updates,
            worksheet_name=worksheet_name,
            start_row=2
        )
        print(f"   ✅ Successfully updated sheet!")
        print(f"\n   View your sheet at:")
        print(f"   https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    except Exception as e:
        print(f"   ❌ Failed to update sheet: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("✅ All steps completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
