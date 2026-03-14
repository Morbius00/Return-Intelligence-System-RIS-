# Google Sheets Setup Guide

This guide explains how to configure Google Sheets integration for the current feedback intelligence pipeline.

## What You Get

Google Sheets endpoints can read feedback rows, classify each row, and write enrichment columns:
- sentiment_type
- issue_category
- severity_score
- satisfaction_category
- goodwill_score
- confidence
- is_spam
- processed_at

## Prerequisites

- Google account
- Google Cloud project
- Service account JSON key
- API server running locally or deployed

## 1) Google Cloud Configuration

1. Create or select a project in Google Cloud Console.
2. Enable APIs:
   - Google Sheets API
   - Google Drive API
3. Create a service account.
4. Create and download a JSON key.

## 2) Local Project Configuration

Place credentials file in the repository, for example:
- credentials/service_account.json

Set environment variable in .env:

```env
GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
```

Restart API after updating .env.

## 3) Share Spreadsheet

Share your target Google Sheet with the service account email in the JSON key.
Grant Editor access.

## 4) Endpoints

### POST /sheets/process

Reads an existing worksheet and writes output columns back to that same sheet.

Request body example:

```json
{
  "spreadsheet_id": "YOUR_SPREADSHEET_ID",
  "worksheet_name": "Feedback",
  "feedback_column": "Customer_Feedback",
  "rating_column": "Rating (1-5)"
}
```

### POST /sheets/update

Processes provided data and writes/replaces worksheet content with enriched rows.

Request body example:

```json
{
  "spreadsheet_id": "YOUR_SPREADSHEET_ID",
  "worksheet_name": "Feedback",
  "data": [
    { "order_id": "ORD001", "customer_feedback": "Product arrived broken" },
    { "order_id": "ORD002", "customer_feedback": "Delivery was excellent" }
  ]
}
```

### POST /sheets/append

Processes provided data and appends enriched rows to existing sheet data.

Request body shape is the same as /sheets/update.

## 5) Troubleshooting

- Google Sheets service not configured:
  Verify GOOGLE_CREDENTIALS_PATH and restart server.
- Permission denied:
  Ensure sheet is shared with service account email.
- Spreadsheet not found:
  Verify spreadsheet_id from sheet URL.
- feedback_column not found:
  Use exact column header in request.feedback_column.


