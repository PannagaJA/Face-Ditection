import pandas as pd

# Path to the Excel file
excel_file = 'attendance.xlsx'

# Load the Excel file
try:
    xls = pd.ExcelFile(excel_file)
    print(f"Available sheets: {xls.sheet_names}")

    # Load the sheets into DataFrames
    present_df = pd.read_excel(excel_file, sheet_name='Present Students')
    absent_df = pd.read_excel(excel_file, sheet_name='Absent Students')

    # Display the contents
    print("\nPresent Students:\n", present_df)
    print("\nAbsent Students:\n", absent_df)
except FileNotFoundError:
    print(f"Error: The file '{excel_file}' was not found.")
except Exception as e:
    print(f"Error reading the Excel file: {e}")
