import pandas as pd
from google.oauth2 import service_account
import gspread
from gspread_dataframe import set_with_dataframe

# Path to the credentials JSON file
CREDENTIALS_FILE = r"C:\Users\Pannaga J A\Downloads\face-ditection-441519-80e9eddd714f.json"

# Authenticate and create the service
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE,
    scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
)

# Authorize gspread with the service account credentials
gc = gspread.authorize(credentials)

# The ID of the Google Sheets file you shared with the service account
spreadsheet_id = '1JZG9DngUoXGBgBh8jybcJG24HB3OPoLbfuS3yc_Pbqs'  # Replace this with your actual Google Sheets ID

# Path to your Excel file
excel_file = 'attendance.xlsx'

# Read the Excel file into DataFrames
present_df = pd.read_excel(excel_file, sheet_name='Present Students')
absent_df = pd.read_excel(excel_file, sheet_name='Absent Students')

# Logging data to verify
print("Present Students DataFrame:")
print(present_df)
print("Absent Students DataFrame:")
print(absent_df)

# Open the existing spreadsheet by its ID
spreadsheet = gc.open_by_key(spreadsheet_id)

# Select the worksheets (or create them if they don't exist)
try:
    present_sheet = spreadsheet.worksheet("Present Students")
except gspread.exceptions.WorksheetNotFound:
    present_sheet = spreadsheet.add_worksheet(title="Present Students", rows=present_df.shape[0]+1, cols=present_df.shape[1])

try:
    absent_sheet = spreadsheet.worksheet("Absent Students")
except gspread.exceptions.WorksheetNotFound:
    absent_sheet = spreadsheet.add_worksheet(title="Absent Students", rows=absent_df.shape[0]+1, cols=absent_df.shape[1])

# Clear the content of the worksheets before writing new data
present_sheet.clear()
absent_sheet.clear()

# Write the DataFrames to the spreadsheet
set_with_dataframe(present_sheet, present_df)
set_with_dataframe(absent_sheet, absent_df)

# Print the URL of the spreadsheet
spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
print(f"Spreadsheet URL: {spreadsheet_url}")
