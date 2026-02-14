"""
Google Sheets integration service.
Handles reading and writing data to Google Sheets using service account authentication.
"""
import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


class GoogleSheetsService:
    """
    Service for interacting with Google Sheets.
    
    Provides methods to read and write data using service account authentication.
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Google Sheets service.
        
        Args:
            credentials_path: Path to service account JSON credentials file.
                            If not provided, looks for GOOGLE_CREDENTIALS_PATH env var.
        """
        self.credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.client: Optional[gspread.Client] = None
        
        if self.credentials_path:
            self.authenticate()
    
    def authenticate(self):
        """
        Authenticate with Google Sheets API using service account credentials.
        
        Raises:
            FileNotFoundError: If credentials file is not found
            ValueError: If credentials are invalid
        """
        if not self.credentials_path:
            raise ValueError("Credentials path not provided")
        
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
        
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            logger.info("Successfully authenticated with Google Sheets API")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def get_spreadsheet(self, spreadsheet_id: str) -> gspread.Spreadsheet:
        """
        Get a spreadsheet by ID.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            
        Returns:
            gspread.Spreadsheet object
        """
        if not self.client:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return self.client.open_by_key(spreadsheet_id)
    
    def get_worksheet(
        self,
        spreadsheet_id: str,
        worksheet_name: str = None,
        worksheet_index: int = 0
    ) -> gspread.Worksheet:
        """
        Get a worksheet from a spreadsheet.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            worksheet_name: Name of worksheet (optional)
            worksheet_index: Index of worksheet if name not provided (default: 0)
            
        Returns:
            gspread.Worksheet object
        """
        spreadsheet = self.get_spreadsheet(spreadsheet_id)
        
        if worksheet_name:
            return spreadsheet.worksheet(worksheet_name)
        else:
            return spreadsheet.get_worksheet(worksheet_index)
    
    def read_sheet_to_dataframe(
        self,
        spreadsheet_id: str,
        worksheet_name: str = None,
        worksheet_index: int = 0
    ) -> pd.DataFrame:
        """
        Read a worksheet into a pandas DataFrame.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            worksheet_name: Name of worksheet (optional)
            worksheet_index: Index of worksheet if name not provided (default: 0)
            
        Returns:
            pandas DataFrame with sheet data
        """
        worksheet = self.get_worksheet(spreadsheet_id, worksheet_name, worksheet_index)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        logger.info(f"Read {len(df)} rows from sheet")
        return df
    
    def write_dataframe_to_sheet(
        self,
        df: pd.DataFrame,
        spreadsheet_id: str,
        worksheet_name: str = None,
        worksheet_index: int = 0,
        start_cell: str = "A1",
        include_index: bool = False
    ):
        """
        Write a pandas DataFrame to a worksheet.
        
        Args:
            df: pandas DataFrame to write
            spreadsheet_id: Google Sheets spreadsheet ID
            worksheet_name: Name of worksheet (optional)
            worksheet_index: Index of worksheet if name not provided (default: 0)
            start_cell: Starting cell for writing (default: "A1")
            include_index: Whether to include DataFrame index (default: False)
        """
        worksheet = self.get_worksheet(spreadsheet_id, worksheet_name, worksheet_index)
        
        # Convert DataFrame to list of lists
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Update the sheet
        worksheet.update(start_cell, data)
        logger.info(f"Wrote {len(df)} rows to sheet")
    
    def update_columns(
        self,
        spreadsheet_id: str,
        updates: Dict[str, List[Any]],
        worksheet_name: str = None,
        worksheet_index: int = 0,
        start_row: int = 2
    ):
        """
        Update specific columns in a worksheet.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            updates: Dictionary mapping column names to lists of values
            worksheet_name: Name of worksheet (optional)
            worksheet_index: Index of worksheet if name not provided (default: 0)
            start_row: Starting row for updates (default: 2, to skip header)
        """
        worksheet = self.get_worksheet(spreadsheet_id, worksheet_name, worksheet_index)
        
        # Get header row to find column positions
        headers = worksheet.row_values(1)
        
        for column_name, values in updates.items():
            if column_name not in headers:
                # Add new column header
                col_index = len(headers) + 1
                worksheet.update_cell(1, col_index, column_name)
                headers.append(column_name)
            else:
                col_index = headers.index(column_name) + 1
            
            # Prepare cell range
            end_row = start_row + len(values) - 1
            cell_range = f"{gspread.utils.rowcol_to_a1(start_row, col_index)}:{gspread.utils.rowcol_to_a1(end_row, col_index)}"
            
            # Format values as list of lists for update
            cell_values = [[value] for value in values]
            
            # Update the column
            worksheet.update(cell_range, cell_values)
            logger.info(f"Updated column '{column_name}' with {len(values)} values")
    
    def batch_update_rows(
        self,
        spreadsheet_id: str,
        row_data: List[Dict[str, Any]],
        worksheet_name: str = None,
        worksheet_index: int = 0,
        start_row: int = 2
    ):
        """
        Batch update rows with multiple column values.
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            row_data: List of dictionaries with column updates for each row
            worksheet_name: Name of worksheet (optional)
            worksheet_index: Index of worksheet if name not provided (default: 0)
            start_row: Starting row for updates (default: 2)
        """
        if not row_data:
            return
        
        # Organize data by column
        columns_to_update = {}
        for key in row_data[0].keys():
            columns_to_update[key] = [row.get(key, "") for row in row_data]
        
        # Use update_columns method
        self.update_columns(
            spreadsheet_id,
            columns_to_update,
            worksheet_name,
            worksheet_index,
            start_row
        )


def create_service_from_env() -> GoogleSheetsService:
    """
    Create GoogleSheetsService using environment variable for credentials.
    
    Returns:
        Authenticated GoogleSheetsService instance
    """
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if not credentials_path:
        raise ValueError("GOOGLE_CREDENTIALS_PATH environment variable not set")
    
    return GoogleSheetsService(credentials_path)


if __name__ == "__main__":
    # Test the service
    print("Google Sheets Service module loaded successfully.")
    print("\nTo use this service:")
    print("1. Create a Google Cloud project")
    print("2. Enable Google Sheets API and Google Drive API")
    print("3. Create a service account and download JSON credentials")
    print("4. Set GOOGLE_CREDENTIALS_PATH environment variable")
    print("5. Share your spreadsheet with the service account email")
