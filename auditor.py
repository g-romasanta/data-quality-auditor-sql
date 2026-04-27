# Hey self! This is your first small project, Data Quality Auditor.

# 1
# This imports the pandas library and gives it a shorter nickname 'pd'
# pandas is the main tool we use to work with data in Python
import pandas as pd

# pd.read_csv() opens CSV file and loads it into a DataFrame
# A DataFrame is like a table — rows and columns, just like Excel
# We store it in a variable called 'df' (short for DataFrame)
df = pd.read_csv('data/bookstore_inventory.csv')

# df.head() shows the first 5 rows of data
# This is just to confirm the file loaded correctly and see what it looks like
print(df.head())

# df.shape returns two numbers: (number of rows, number of columns)
# This tells you how big the dataset is
print(df.shape)

# 2

# Check for missing/null values in the dataset
# isnull() marks every cell that is empty/missing as True
# sum() counts how many True values exist per column
# This tells us how many missing values each column has
missing_values = df.isnull().sum()

# This calculates the percentage of missing values per column
# Dividing by the total number of rows (df.shape[0]) and multiplying by 100
# gives us a clearer picture of how severe the missing data is
missing_percent = (df.isnull().sum() / df.shape[0]) * 100

# We combine both into one neat table for easier reading
# axis=1 means we're joining them side by side (as columns)
missing_summary = pd.concat([missing_values, missing_percent], axis=1)

# We rename the columns to make the table more readable
missing_summary.columns = ['Missing Count', 'Missing Percent']

print("\n--- MISSING VALUES ---")
print(missing_summary)

# 3
#  duplicate() checks every row and marks it True if it's an exact copy of a previous row
# sum() counts how many duplicated rows exist
duplicate_count = df.duplicated().sum()

# We also calculate what percentage of the dataset is duplicated
duplicate_percent = (duplicate_count / df.shape[0]) * 100

print("\n--- DUPLICATE ROWS ---")

# We print the count and percentage, rounded to 2 decimal places
print(f"Duplicate Rows: {duplicate_count}")
print(f"Duplicate Percent: {round(duplicate_percent, 2)}%")

# 4

# df.dtypes returns the data type of each column
# This tells us what kind of data Python thinks each column contains
# e.g. object = text, int64 = whole numbers, float64 = decimal numbers
data_types = df.dtypes

print("\n--- DATA TYPES ---")
print(data_types)

# The 'month' column should be a date, not plain text
# We check if pandas read it correctly as a datetime type
if df['month'].dtype != 'datetime64[ns]':
    print("\n⚠️ Warning: 'month' column is not datetime format. Consider converting it.")


#5

# We only check outliers on numerical columns
# select_dtypes pulls out only columns with number data types
numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns

print("\n--- OUTLIERS (IQR Method) ---")

# We loop through each numerical column one by one
for col in numerical_cols:
    # Q1 is the 25th percentile, Q3 is the 75th percentile
    # These divide your data into quarters
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    
    # IQR is the range between Q1 and Q3 (the middle 50% of data)
    IQR = Q3 - Q1
    
    # Anything below Q1 - 1.5*IQR or above Q3 + 1.5*IQR is an outlier
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    
    # We count how many rows fall outside the normal range
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    
    print(f"{col}: {len(outliers)} outliers (lower bound: {round(lower,2)}, upper bound: {round(upper,2)})")

# 6

# --- CALCULATION VALIDATION ---
# In a clean dataset, extended_cost should always equal qty x unit_cost
# And extended_retail should always equal qty x unit_price
# If they don't match, something is wrong with the data

print("\n--- CALCULATION VALIDATION ---")

# We calculate what extended_cost SHOULD be
# round() is used to avoid tiny floating point errors (e.g. 0.0000001 differences)
df['expected_extended_cost'] = round(df['qty'] * df['unit_cost'], 2)

# We compare it to what's actually in the dataset
# Any row where they don't match is a data integrity issue
cost_mismatch = df[df['extended_cost'] != df['expected_extended_cost']]

print(f"extended_cost mismatches: {len(cost_mismatch)}")

# We do the same for extended_retail
df['expected_extended_retail'] = round(df['qty'] * df['unit_price'], 2)

retail_mismatch = df[df['extended_retail'] != df['expected_extended_retail']]

print(f"extended_retail mismatches: {len(retail_mismatch)}")

# If mismatches exist, show a sample of the problematic rows
if len(cost_mismatch) > 0:
    print("\nSample cost mismatches:")
    print(cost_mismatch[['month', 'sku', 'qty', 'unit_cost', 
                          'extended_cost', 'expected_extended_cost']].head())

if len(retail_mismatch) > 0:
    print("\nSample retail mismatches:")
    print(retail_mismatch[['month', 'sku', 'qty', 'unit_price', 
                            'extended_retail', 'expected_extended_retail']].head())
    

# OUTPUT

# --- GENERATE HTML REPORT ---
# We build the HTML report as one long string
# Think of it as writing a webpage using Python

print("\n--- GENERATING REPORT ---")

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

# We add outlier rows dynamically for each numerical column
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

</body>
</html>
"""

# We save the HTML string into a file in the outputs folder
with open('outputs/report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Report successfully generated! Check outputs/report.html")