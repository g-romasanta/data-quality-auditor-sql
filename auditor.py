import pandas as pd
import sqlite3

conn = sqlite3.connect('data/bookstore.db')

df_csv = pd.read_csv('data/bookstore_inventory.csv')

df_csv.to_sql('inventory', conn, if_exists='replace', index=False)

df = pd.read_sql_query("SELECT * FROM inventory", conn)

print("✅ Data loaded into SQLite and queried successfully!")

print(df.head())

print(df.shape)

missing_values = df.isnull().sum()

missing_percent = (df.isnull().sum() / df.shape[0]) * 100

missing_summary = pd.concat([missing_values, missing_percent], axis=1)

missing_summary.columns = ['Missing Count', 'Missing Percent']

print("\n--- MISSING VALUES ---")
print(missing_summary)

duplicate_count = df.duplicated().sum()

duplicate_percent = (duplicate_count / df.shape[0]) * 100

print("\n--- DUPLICATE ROWS ---")

print(f"Duplicate Rows: {duplicate_count}")
print(f"Duplicate Percent: {round(duplicate_percent, 2)}%")

data_types = df.dtypes

print("\n--- DATA TYPES ---")
print(data_types)

if df['month'].dtype != 'datetime64[ns]':
    print("\n⚠️ Warning: 'month' column is not datetime format. Consider converting it.")


numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns

print("\n--- OUTLIERS (IQR Method) ---")

for col in numerical_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    outliers = df[(df[col] < lower) | (df[col] > upper)]
    
    print(f"{col}: {len(outliers)} outliers (lower bound: {round(lower,2)}, upper bound: {round(upper,2)})")

print("\n--- CALCULATION VALIDATION ---")

df['expected_extended_cost'] = round(df['qty'] * df['unit_cost'], 2)

cost_mismatch = df[df['extended_cost'] != df['expected_extended_cost']]

print(f"extended_cost mismatches: {len(cost_mismatch)}")

df['expected_extended_retail'] = round(df['qty'] * df['unit_price'], 2)

retail_mismatch = df[df['extended_retail'] != df['expected_extended_retail']]

print(f"extended_retail mismatches: {len(retail_mismatch)}")

if len(cost_mismatch) > 0:
    print("\nSample cost mismatches:")
    print(cost_mismatch[['month', 'sku', 'qty', 'unit_cost', 
                          'extended_cost', 'expected_extended_cost']].head())

if len(retail_mismatch) > 0:
    print("\nSample retail mismatches:")
    print(retail_mismatch[['month', 'sku', 'qty', 'unit_price', 
                            'extended_retail', 'expected_extended_retail']].head())
    
summary_query = """
    SELECT 
        [to] AS store,
        COUNT(*) AS total_transactions,
        SUM(qty) AS total_quantity,
        ROUND(SUM(extended_cost), 2) AS total_cost,
        ROUND(SUM(extended_retail), 2) AS total_retail
    FROM inventory
    GROUP BY [to]
    ORDER BY total_retail DESC
"""

store_summary = pd.read_sql_query(summary_query, conn)

html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Data Quality Audit Report</title>
    <style>
        /* This is CSS - it controls how the report looks */
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2980b9;
            margin-top: 30px;
        }}
        table {{
            border-collapse: collapse;
            width: 60%;
            background-color: white;
            margin-bottom: 20px;
        }}
        th {{
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            text-align: left;
        }}
        td {{
            padding: 8px 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{background-color: #f1f1f1;}}
        .pass {{color: green; font-weight: bold;}}
        .warn {{color: orange; font-weight: bold;}}
        .summary-box {{
            background-color: white;
            padding: 15px 25px;
            border-left: 5px solid #2980b9;
            margin-bottom: 20px;
            width: fit-content;
        }}
    </style>
</head>
<body>

<h1>📊 Data Quality Audit Report</h1>
<div class="summary-box">
    <p><strong>Dataset:</strong> bookstore_inventory.csv</p>
    <p><strong>Total Rows:</strong> {df.shape[0]}</p>
    <p><strong>Total Columns:</strong> {df.shape[1]}</p>
</div>

<h2>1. Missing Values</h2>
<table>
    <tr><th>Column</th><th>Missing Count</th><th>Missing %</th><th>Status</th></tr>
    {''.join(f"<tr><td>{col}</td><td>{int(missing_values[col])}</td><td>{round(missing_percent[col],2)}%</td><td class='{'warn' if missing_values[col] > 0 else 'pass'}'>{'⚠️ Has Nulls' if missing_values[col] > 0 else '✅ Clean'}</td></tr>" for col in df.columns if col not in ['expected_extended_cost', 'expected_extended_retail'])}
</table>

<h2>2. Duplicate Rows</h2>
<div class="summary-box">
    <p>Duplicate Rows: <strong>{duplicate_count}</strong></p>
    <p>Duplicate Percent: <strong>{round(duplicate_percent, 2)}%</strong></p>
    <p class="{'warn' if duplicate_count > 0 else 'pass'}">{'⚠️ Duplicates Found' if duplicate_count > 0 else '✅ No Duplicates'}</p>
</div>

<h2>3. Data Types</h2>
<table>
    <tr><th>Column</th><th>Data Type</th><th>Status</th></tr>
    {''.join(f"<tr><td>{col}</td><td>{str(df[col].dtype)}</td><td class='{'warn' if col == 'month' else 'pass'}'>{'⚠️ Should be datetime' if col == 'month' else '✅ OK'}</td></tr>" for col in df.columns if col not in ['expected_extended_cost', 'expected_extended_retail'])}
</table>

<h2>4. Outliers (IQR Method)</h2>
<table>
    <tr><th>Column</th><th>Outlier Count</th><th>Lower Bound</th><th>Upper Bound</th><th>Status</th></tr>
"""

for col in numerical_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    count = len(outliers)
    status = "⚠️ Has Outliers" if count > 0 else "✅ Clean"
    css = "warn" if count > 0 else "pass"
    html += f"<tr><td>{col}</td><td>{count}</td><td>{round(lower,2)}</td><td>{round(upper,2)}</td><td class='{css}'>{status}</td></tr>"

html += f"""
</table>

<h2>5. Calculation Validation</h2>
<div class="summary-box">
    <p>extended_cost mismatches: <strong>{len(cost_mismatch)}</strong> 
    <span class="{'warn' if len(cost_mismatch) > 0 else 'pass'}">{'⚠️ Mismatches Found' if len(cost_mismatch) > 0 else '✅ All Match'}</span></p>
    <p>extended_retail mismatches: <strong>{len(retail_mismatch)}</strong> 
    <span class="{'warn' if len(retail_mismatch) > 0 else 'pass'}">{'⚠️ Mismatches Found' if len(retail_mismatch) > 0 else '✅ All Match'}</span></p>
</div>

<h2>6. Store Summary (SQL Analysis)</h2>
<table>
    <tr>
        <th>Store</th>
        <th>Total Transactions</th>
        <th>Total Quantity</th>
        <th>Total Cost</th>
        <th>Total Retail</th>
    </tr>
    {''.join(f"<tr><td>{row['store']}</td><td>{row['total_transactions']}</td><td>{row['total_quantity']}</td><td>${row['total_cost']:,.2f}</td><td>${row['total_retail']:,.2f}</td></tr>" for _, row in store_summary.iterrows())}
</table>

</body>
</html>
"""

with open('outputs/report.html', 'w', encoding='utf-8') as f:
    f.write(html)

summary_query = """
    SELECT 
        [to] AS store,
        COUNT(*) AS total_transactions,
        SUM(qty) AS total_quantity,
        ROUND(SUM(extended_cost), 2) AS total_cost,
        ROUND(SUM(extended_retail), 2) AS total_retail
    FROM inventory
    GROUP BY [to]
    ORDER BY total_retail DESC
"""

store_summary = pd.read_sql_query(summary_query, conn)

print("\n--- STORE SUMMARY (SQL) ---")
print(store_summary)

print("\n--- GENERATING REPORT ---")
print("✅ Report successfully generated! Check outputs/report.html")