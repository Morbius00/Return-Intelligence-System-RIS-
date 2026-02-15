# Google Sheets Integration Setup Guide

This guide explains how to set up real-time Google Sheets integration for the NLP Return Reason Classifier.

## Overview

The system can automatically write classification results directly to Google Sheets in real-time, making it easy to:
- Process and classify customer return reasons
- Store results in a centralized, shareable location
- Enable real-time collaboration and review
- Generate reports and analytics from Google Sheets

## Prerequisites

- Google Account
- Google Cloud Project (free tier available)
- Python environment with required packages installed

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **Select a Project** → **New Project**
3. Enter project name (e.g., "NLP-Returns-Classifier")
4. Click **Create**

### 2. Enable Required APIs

1. In your project, go to **APIs & Services** → **Library**
2. Search for and enable:
   - **Google Sheets API**
   - **Google Drive API**

### 3. Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **Service account**
3. Enter a name (e.g., "nlp-sheets-service")
4. Click **Create and Continue**
5. Skip optional steps and click **Done**

### 4. Create and Download Credentials

1. In **Credentials** page, click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON** format
5. Click **Create** - the JSON file will download automatically
6. **IMPORTANT**: Keep this file secure! It contains authentication credentials.

### 5. Set Up Credentials in Your Project

1. Create a `credentials` folder in your project root:
   ```powershell
   mkdir credentials
   ```

2. Move the downloaded JSON file to the credentials folder:
   ```powershell
   mv ~/Downloads/your-project-*.json ./credentials/service_account.json
   ```

3. Add credentials folder to `.gitignore` (if not already):
   ```
   credentials/
   *.json
   ```

4. Create `.env` file from `.env.example`:
   ```powershell
   cp .env.example .env
   ```

5. Update `.env` with your credentials path:
   ```env
   GOOGLE_CREDENTIALS_PATH=./credentials/service_account.json
   ```

### 6. Share Google Sheet with Service Account

1. Open the JSON credentials file and find the `client_email` field
   - It looks like: `nlp-sheets-service@your-project.iam.gserviceaccount.com`

2. Open your Google Sheet

3. Click **Share** button (top right)

4. Paste the service account email

5. Give it **Editor** permissions

6. Uncheck "Notify people" (it's a service account, not a person)

7. Click **Share**

### 7. Get Your Spreadsheet ID

The Spreadsheet ID is in the URL of your Google Sheet:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
```

Example:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                        ↑ This is your Spreadsheet ID
```

## Usage

### API Endpoints

The system provides two endpoints for Google Sheets integration:

#### 1. **POST /sheets/update** - Replace/Update Sheet

Writes data to Google Sheets, replacing existing content.

**Request:**
```json
{
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
  "worksheet_name": "Returns",
  "data": [
    {
      "order_id": "ORD001",
      "customer_name": "John Doe",
      "reason": "item arrived broken"
    },
    {
      "order_id": "ORD002",
      "customer_name": "Jane Smith",
      "reason": "wrong size ordered"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "rows_processed": 2,
  "message": "Successfully processed and updated 2 rows in Google Sheets",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1BxiMVs0X..."
}
```

**Output in Google Sheets:**
| order_id | customer_name | reason | Category | Severity | Confidence | Is_Spam | Processed_At |
|----------|--------------|--------|----------|----------|------------|---------|--------------|
| ORD001 | John Doe | item arrived broken | Product Quality Issue | 0.9 | 85.0% | No | 2024-01-15 14:30:00 |
| ORD002 | Jane Smith | wrong size ordered | Wrong Item Received | 0.7 | 92.3% | No | 2024-01-15 14:30:01 |

#### 2. **POST /sheets/append** - Append to Sheet

Adds new data to the end of existing sheet data.

**Request:** (same format as /sheets/update)

**Use Cases:**
- Continuous monitoring - append new returns as they come in
- Historical tracking - keep all processed data
- Incremental updates - don't overwrite existing data

### Example with cURL

```bash
curl -X POST "http://localhost:8000/sheets/update" \
  -H "Content-Type: application/json" \
  -d '{
    "spreadsheet_id": "YOUR_SPREADSHEET_ID",
    "worksheet_name": "Returns",
    "data": [
      {"order_id": "ORD001", "reason": "item arrived broken"}
    ]
  }'
```

### Example with Python

```python
import requests

url = "http://localhost:8000/sheets/update"
data = {
    "spreadsheet_id": "YOUR_SPREADSHEET_ID",
    "worksheet_name": "Returns",
    "data": [
        {"order_id": "ORD001", "reason": "item arrived broken"},
        {"order_id": "ORD002", "reason": "wrong color"}
    ]
}

response = requests.post(url, json=data)
print(response.json())
```

### Example with JavaScript/Fetch

```javascript
fetch('http://localhost:8000/sheets/update', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    spreadsheet_id: 'YOUR_SPREADSHEET_ID',
    worksheet_name: 'Returns',
    data: [
      { order_id: 'ORD001', reason: 'item arrived broken' },
      { order_id: 'ORD002', reason: 'wrong color' }
    ]
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Testing

1. Start the API server:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```

2. Visit the API docs: http://localhost:8000/docs

3. Try the `/sheets/update` endpoint with your spreadsheet ID

4. Check your Google Sheet - you should see the results appear in real-time!

## Troubleshooting

### Error: "Google Sheets service not configured"

**Solution:** 
- Ensure `.env` file exists with `GOOGLE_CREDENTIALS_PATH` set
- Verify the path points to valid JSON credentials file
- Restart the API server after updating .env

### Error: "Permission denied" or "Forbidden"

**Solution:**
- Make sure you shared the Google Sheet with the service account email
- Give the service account **Editor** permissions
- Double-check the email address from the JSON credentials

### Error: "Spreadsheet not found"

**Solution:**
- Verify the Spreadsheet ID is correct (from the URL)
- Ensure the sheet is shared with the service account
- Check that the service account has access

### Error: "Worksheet not found"

**Solution:**
- Check the worksheet name spelling (case-sensitive)
- Leave `worksheet_name` empty to use the first sheet
- Create the worksheet manually if it doesn't exist

## Security Best Practices

1. **Never commit credentials to git**
   - Add `credentials/` to `.gitignore`
   - Add `.env` to `.gitignore`

2. **Limit service account permissions**
   - Only share specific sheets needed
   - Use Editor only, not Owner

3. **Rotate credentials periodically**
   - Create new keys every 90 days
   - Delete old keys

4. **Secure credential storage**
   - Store JSON files in secure locations
   - Use environment variables in production
   - Consider using secret management tools (Azure Key Vault, AWS Secrets Manager)

## Advanced Usage

### Using Default Spreadsheet

Set default spreadsheet in `.env`:
```env
GOOGLE_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_WORKSHEET_NAME=Returns
```

Then you can omit these values in API requests.

### Processing CSV and Auto-Updating Sheet

Combine file upload with sheets update:
1. Use `/predict/file` endpoint to get predictions
2. Download the result
3. Parse result and send to `/sheets/update`

### Scheduled Updates

Use task scheduler or cron to automatically process and update:
```python
# scheduled_update.py
import requests
import pandas as pd

# Read from your data source
df = pd.read_csv("new_returns.csv")
data = df.to_dict('records')

# Send to API
response = requests.post(
    "http://localhost:8000/sheets/append",
    json={
        "spreadsheet_id": "YOUR_ID",
        "data": data
    }
)
print(response.json())
```

## Next Steps

- Set up automated workflows with the Sheets API
- Create dashboards in Google Sheets with the classification data
- Set up alerts for high-severity returns
- Export data for further analysis

## Support

For issues or questions:
1. Check API logs for detailed error messages
2. Review Google Cloud Console for API quotas and errors
3. Verify service account permissions in Google Sheets

---

**Congratulations!** You now have real-time Google Sheets integration for your NLP classifier. 🎉
