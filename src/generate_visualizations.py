import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_charts_and_summary(project_dir):
    """
    Generates two key data visualizations and prints a final project summary report.
    """
    raw_file = os.path.join(project_dir, 'sales_data_sample.csv')
    flagged_file = os.path.join(project_dir, 'full_flagged_orders.csv')

    # Verify input files exist
    if not os.path.exists(raw_file) or not os.path.exists(flagged_file):
        print("Error: Required files are missing. Please run previous steps first.")
        return

    # Load data
    df_raw = pd.read_csv(raw_file, encoding='latin1')
    df_flagged = pd.read_csv(flagged_file, encoding='latin1')

    total_rows = len(df_raw)
    total_flagged = len(df_flagged)

    # --- Chart 1: Bar chart of flagged orders by severity_level ---
    severity_order = ['Low', 'Medium', 'High']
    counts = df_flagged['severity_level'].value_counts().reindex(severity_order, fill_value=0)

    plt.figure(figsize=(7, 5))
    # Distinct colors: Blue for Low, Yellow/Orange for Medium, bold Red for High
    colors = ['#3498db', '#f1c40f', '#e74c3c'] 
    
    sns.barplot(x=counts.index, y=counts.values, palette=colors, hue=counts.index, legend=False)
    
    plt.title('Flagged Orders by Severity Level', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Severity Level', fontsize=10)
    plt.ylabel('Number of Orders', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Add values on top of the bars
    for i, val in enumerate(counts.values):
        plt.text(i, val + (max(counts.values) * 0.015), str(val), ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    chart1_path = os.path.join(project_dir, 'flagged_orders_by_severity.png')
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Chart saved: {chart1_path}")


    # --- Chart 2: Bar chart of High + Medium anomalies by PRODUCTLINE ---
    df_high_med = df_flagged[df_flagged['severity_level'].isin(['High', 'Medium'])].copy()
    prod_counts = df_high_med['PRODUCTLINE'].value_counts()

    plt.figure(figsize=(9, 5))
    # Horizontal bar plot for readability of product line labels
    sns.barplot(x=prod_counts.values, y=prod_counts.index, palette='viridis', hue=prod_counts.index, legend=False)
    
    plt.title('High & Medium Severity Anomalies by Product Line', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Number of Anomalies', fontsize=10)
    plt.ylabel('Product Line', fontsize=10)
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    
    # Add values at the end of the horizontal bars
    for i, val in enumerate(prod_counts.values):
        plt.text(val + (max(prod_counts.values) * 0.01), i, str(val), ha='left', va='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    chart2_path = os.path.join(project_dir, 'anomalies_by_productline.png')
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Chart saved: {chart2_path}")


    # --- Print Final Closing Summary ---
    high_priority_count = counts.get('High', 0)
    top_prod_line = prod_counts.idxmax()
    top_prod_count = prod_counts.max()

    print("\n" + "="*50)
    print("             FINAL PROJECT SUMMARY")
    print("="*50)
    print(f"Total Rows Processed                         : {total_rows}")
    print(f"Total Flagged Anomalous Rows                 : {total_flagged} ({(total_flagged/total_rows)*100:.2f}%)")
    print(f"High-Priority Actionable Group Count (High)  : {high_priority_count} ({(high_priority_count/total_flagged)*100:.2f}% of flagged)")
    print(f"Risk Concentration Leader (Product Line)     : {top_prod_line} ({top_prod_count} anomalies)")
    print("="*50)

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    generate_charts_and_summary(dir_path)
