import os
import pandas as pd

def score_and_export(anomalies_file):
    """
    Reads flagged anomalies, calculates severity scores using a non-double-counting formula,
    categorizes severity levels, sorts by severity, and exports report files.
    """
    if not os.path.exists(anomalies_file):
        print(f"Error: The file '{anomalies_file}' was not found.")
        print("Please run 'detect_anomalies.py' first to generate the anomaly flags.")
        return

    # Load dataset with latin1 encoding
    try:
        df = pd.read_csv(anomalies_file, encoding='latin1')
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print("Successfully loaded flagged anomalies dataset.")

    # --- Step 1: Create severity_score column ---
    # severity_score = anomaly_count (number of rules triggered) + 1 extra point ONLY if is_cancelled_disputed is True
    # converts boolean is_cancelled_disputed to 1 (True) or 0 (False) to avoid double-counting
    df['severity_score'] = df['anomaly_count'] + df['is_cancelled_disputed'].astype(int)


    # --- Step 2: Create severity_level column ---
    # Bucket the score into: 'Low' (score 1), 'Medium' (score 2), 'High' (score 3+)
    def get_severity_level(score):
        if score == 0:
            return 'None'
        elif score == 1:
            return 'Low'
        elif score == 2:
            return 'Medium'
        else:
            return 'High'

    df['severity_level'] = df['severity_score'].apply(get_severity_level)


    # --- Step 3: Filter and Sort Flagged Dataset ---
    # Filter for flagged rows only (is_any_anomaly is True)
    flagged_df = df[df['is_any_anomaly'] == True].copy()
    
    # Sort by severity_score descending
    flagged_df = flagged_df.sort_values(by='severity_score', ascending=False)


    # --- Step 4: Export Files ---
    dir_path = os.path.dirname(os.path.abspath(__file__))
    full_export_path = os.path.join(dir_path, 'full_flagged_orders.csv')
    top20_export_path = os.path.join(dir_path, 'top_20_priority_review.csv')

    # Export full flagged orders
    flagged_df.to_csv(full_export_path, index=False, encoding='latin1')
    
    # Export top 20 priority review
    top_20_df = flagged_df.head(20)
    top_20_df.to_csv(top20_export_path, index=False, encoding='latin1')

    print(f"Exported: {full_export_path}")
    print(f"Exported: {top20_export_path}")


    # --- Step 5: Summary Report ---
    print("\n" + "="*50)
    print("             UPDATED SEVERITY SCORING SUMMARY")
    print("="*50)
    print(f"Total Flagged Rows: {len(flagged_df)}")
    print("-" * 50)
    
    # Value counts per severity level (ordered High -> Medium -> Low)
    level_order = ['High', 'Medium', 'Low']
    counts = flagged_df['severity_level'].value_counts()
    
    print("Counts per Severity Level:")
    for lvl in level_order:
        cnt = counts.get(lvl, 0)
        pct = (cnt / len(flagged_df)) * 100
        print(f" - {lvl:8}: {cnt:4d} rows ({pct:.2f}% of flagged)")

    print("-" * 50)
    print("\nTop 5 Most Severe Anomalies Preview:")
    preview_cols = ['ORDERNUMBER', 'PRODUCTLINE', 'STATUS', 'severity_score', 'severity_level', 'anomaly_count']
    print(flagged_df[preview_cols].head())

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    anomalies_file = os.path.join(dir_path, 'sales_data_anomalies.csv')
    score_and_export(anomalies_file)
