import os
import pandas as pd

def load_and_summarize(file_path):
    """
    Loads the sales/order dataset and runs a comprehensive data quality check.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        print("Please place the CSV file in the same directory as this script, or specify the correct path.")
        return

    print(f"Attempting to load: {file_path}")
    
    # Step 1 & 2: Load the CSV file and handle encoding
    # European datasets often contain latin1 (ISO-8859-1) characters.
    # We will try loading with UTF-8 first, and fall back to latin1 if it fails.
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        print("Successfully loaded file with UTF-8 encoding.")
    except UnicodeDecodeError:
        print("UTF-8 decoding failed. Retrying with 'latin1' encoding...")
        try:
            df = pd.read_csv(file_path, encoding='latin1')
            print("Successfully loaded file with 'latin1' encoding.")
        except Exception as e:
            print(f"Error loading file: {e}")
            return
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # Step 3: Parse ORDERDATE into a proper datetime column
    # We use errors='coerce' to catch any non-standard date strings and turn them into NaT.
    if 'ORDERDATE' in df.columns:
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')
        print("Successfully parsed 'ORDERDATE' into datetime.")
    else:
        print("Warning: 'ORDERDATE' column not found in the dataset.")

    print("\n" + "="*50)
    print("              DATA QUALITY SUMMARY")
    print("="*50)

    # 4a. Shape of the dataset (rows, columns)
    rows, cols = df.shape
    print(f"1. Dataset Shape: {rows} rows, {cols} columns")

    # 4b. Missing values per column
    print("\n2. Missing Values Per Column:")
    missing_values = df.isnull().sum()
    print(missing_values[missing_values > 0] if missing_values.sum() > 0 else "No missing values found.")

    # 4c. Duplicate order lines (based on ORDERNUMBER + ORDERLINENUMBER)
    print("\n3. Duplicate Order Lines:")
    if 'ORDERNUMBER' in df.columns and 'ORDERLINENUMBER' in df.columns:
        duplicates = df.duplicated(subset=['ORDERNUMBER', 'ORDERLINENUMBER'], keep=False).sum()
        print(f"Found {duplicates} duplicate rows based on (ORDERNUMBER + ORDERLINENUMBER).")
    else:
        print("Warning: 'ORDERNUMBER' or 'ORDERLINENUMBER' columns missing; cannot check duplicates.")

    # 4d. Date range (min/max ORDERDATE)
    print("\n4. Date Range of Orders:")
    if 'ORDERDATE' in df.columns and not df['ORDERDATE'].isnull().all():
        min_date = df['ORDERDATE'].min()
        max_date = df['ORDERDATE'].max()
        print(f"Start Date: {min_date}")
        print(f"End Date:   {max_date}")
    else:
        print("Date range unavailable (ORDERDATE column missing or contains all null values).")

    # 4e. Unique count of CITY
    print("\n5. Unique Cities Count:")
    if 'CITY' in df.columns:
        unique_cities = df['CITY'].nunique()
        print(f"Number of unique cities: {unique_cities}")
    else:
        print("Warning: 'CITY' column not found.")

    # 4f. Value counts of STATUS column
    print("\n6. Status Value Counts:")
    if 'STATUS' in df.columns:
        print(df['STATUS'].value_counts(dropna=False))
    else:
        print("Warning: 'STATUS' column not found.")

    # Step 5: Print the first 5 rows for visual confirmation
    print("\n" + "="*50)
    print("              FIRST 5 ROWS")
    print("="*50)
    print(df.head())

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(dir_path, 'sales_data_sample.csv')
    if not os.path.exists(csv_file):
        csv_file = os.path.join(dir_path, 'sales_data.csv')
    load_and_summarize(csv_file)
