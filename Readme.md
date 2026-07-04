\# Order Anomaly Detector



Automated detection and prioritization of anomalous orders in supply chain/sales data, replacing manual line-by-line review with a rule-based + statistical scoring pipeline.



\## Problem



Manually reviewing thousands of order records to catch pricing errors, cancellations, and unusual transactions doesn't scale — issues get missed, and analysts waste time scanning rows that are actually fine. This project automates the first pass, so human review time is spent only on the highest-risk cases.



\## Approach



The pipeline processes raw order data through four stages:



1\. \*\*Data ingestion \& quality check\*\* — load, clean, and validate the dataset (missing values, duplicates, date 

&#x09;				ranges).

2\. \*\*Anomaly detection\*\* — 		combination of rule-based checks (cancelled/disputed orders, pricing far 					below MSRP,statistically invalid price-to-sales ratios) and statistical 					outlier detection (IQR method on quantity and price, per product line).

3\. \*\*Severity scoring\*\* — 		each flagged order gets a severity score based on how many rules it 						triggers, with confirmed problem statuses (cancelled/disputed) weighted 					higher than statistical flags alone. Orders are bucketed into Low / 						Medium / High priority.

4\. \*\*Visualization\*\* — 			summary charts showing severity distribution and risk concentration by 						product line.



\## Results



\- \*\*2,823\*\* orders processed

\- \*\*538\*\* flagged as anomalous (19.06%)

\- \*\*9\*\* orders identified as High priority — the actual list a human reviewer should look at first

\- \*\*Classic Cars\*\* emerged as the product line with the highest concentration of risk (125 anomalies)



This turns a 2,823-row dataset into a 9-item action list, cutting manual review effort by over 99% for the highest-priority cases.



\## Tools Used



\- Python

\- pandas, numpy (data processing, statistical outlier detection)

\- matplotlib (visualization)



\## Charts



\*\*Severity distribution across all flagged orders:\*\*



!\[Severity Distribution](output/flagged_orders_by_severity.png)



\*\*Risk concentration by product line:\*\*



!\[Risk by Product Line](output/anomalies_by_productline.png)



\## How to Run



```bash

pip install -r requirements.txt

python src/ingest_data.py
python src/detect_anomalies.py
python src/severity_scoring.py
python src/generate_visualizations.py

```



Input data goes in `data/`, outputs (flagged CSVs and charts) are saved to `outputs/`.



\## Project Structure



```

order-anomaly-detector/

├── data/

├── src/

├── outputs/

├── README.md

└── requirements.txt

```

