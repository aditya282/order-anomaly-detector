import os
import pandas as pd
import numpy as np

def detect_anomalies(file_path):
    """
    Loads dataset, applies updated rule-based and statistical anomaly checks,
    and prints a summary of flagged items.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        return None

    # Load file with latin1 encoding to handle European characters correctly
    try:
        df = pd.read_csv(file_path, encoding='latin1')
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    # Parse ORDERDATE to datetime
    if 'ORDERDATE' in df.columns:
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')

    # --- 1. Rule-Based Anomaly Flags ---
    
    # Flag known-problem orders (STATUS is Cancelled, Disputed, or On Hold)
    problem_statuses = {'Cancelled', 'Disputed', 'On Hold'}
    df['is_cancelled_disputed'] = df['STATUS'].isin(problem_statuses)

    # Calculate price_cap_ratio to analyze database schema price caps ($100 limit)
    # price_cap_ratio = SALES / (QUANTITYORDERED * PRICEEACH)
    df['price_cap_ratio'] = df['SALES'] / (df['QUANTITYORDERED'] * df['PRICEEACH'])
    
    # Flag severe price mismatches where price_cap_ratio is a statistical outlier across the dataset
    q1_ratio = df['price_cap_ratio'].quantile(0.25)
    q3_ratio = df['price_cap_ratio'].quantile(0.75)
    iqr_ratio = q3_ratio - q1_ratio
    lower_bound_ratio = q1_ratio - 1.5 * iqr_ratio
    upper_bound_ratio = q3_ratio + 1.5 * iqr_ratio
    
    df['is_price_mismatch_severe'] = (df['price_cap_ratio'] < lower_bound_ratio) | (df['price_cap_ratio'] > upper_bound_ratio)

    # Flag rows where PRICEEACH is more than 40% below MSRP (pricing anomaly)
    df['is_price_below_msrp'] = df['PRICEEACH'] < (0.60 * df['MSRP'])


    # --- 2. Statistical Anomaly Flags (per PRODUCTLINE using IQR) ---
    
    def get_iqr_outliers(series):
        # Calculate IQR bounds
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        # Return boolean mask for outliers
        return (series < lower_bound) | (series > upper_bound)

    # Group by PRODUCTLINE and apply outlier detection
    df['is_qty_outlier'] = df.groupby('PRODUCTLINE')['QUANTITYORDERED'].transform(get_iqr_outliers)
    df['is_price_outlier'] = df.groupby('PRODUCTLINE')['PRICEEACH'].transform(get_iqr_outliers)


    # --- 3. Combined Flags ---
    
    # List of all anomaly flag columns
    flag_cols = [
        'is_cancelled_disputed', 
        'is_price_mismatch_severe', 
        'is_price_below_msrp', 
        'is_qty_outlier', 
        'is_price_outlier'
    ]
    
    # Count how many rules flagged each row
    df['anomaly_count'] = df[flag_cols].sum(axis=1)
    df['is_any_anomaly'] = df['anomaly_count'] > 0
    df['is_multi_flagged'] = df['anomaly_count'] > 1


    # --- 4. Summary & Reports ---
    
    print("\n" + "="*50)
    print("             UPDATED ANOMALY DETECTION SUMMARY")
    print("="*50)
    print(f"Total rows analyzed: {len(df)}")
    print(f"Price Cap Ratio IQR bounds: [{lower_bound_ratio:.4f}, {upper_bound_ratio:.4f}] (IQR: {iqr_ratio:.4f})")
    print("-" * 50)
    
    print("Flag Counts by Rule:")
    for col in flag_cols:
        count = df[col].sum()
        percentage = (count / len(df)) * 100
        print(f" - {col:25}: {count:4d} rows ({percentage:.2f}%)")
        
    print("-" * 50)
    total_flagged = df['is_any_anomaly'].sum()
    multi_flagged = df['is_multi_flagged'].sum()
    print(f"Total flagged (any rule)     : {total_flagged:4d} rows ({(total_flagged/len(df))*100:.2f}%)")
    print(f"Multi-flagged (highest conf.) : {multi_flagged:4d} rows ({(multi_flagged/len(df))*100:.2f}%)")
    
    if multi_flagged > 0:
        print("\nTop Multi-Flagged Sample Rows:")
        sample_cols = ['ORDERNUMBER', 'PRODUCTLINE', 'STATUS', 'QUANTITYORDERED', 'PRICEEACH', 'SALES', 'MSRP', 'price_cap_ratio', 'anomaly_count']
        # Show some multi-flagged rows
        print(df[df['is_multi_flagged']][sample_cols].head())

    # Save results to a new CSV file for inspection
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sales_data_anomalies.csv')
    df.to_csv(output_path, index=False, encoding='latin1')
    print(f"\nFlagged data saved to: {output_path}")

    return df

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(dir_path, 'sales_data_sample.csv')
    detect_anomalies(csv_file)
