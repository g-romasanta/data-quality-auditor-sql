# Automated Data Quality Auditor with SQL

A Python project that loads CSV data into a SQLite database, runs SQL queries 
for analysis, checks for common data quality issues, and generates a clean 
HTML report.

## What It Checks
- **Missing Values** — detects null/empty cells per column
- **Duplicate Rows** — flags any repeated rows in the dataset
- **Data Types** — checks if columns have the expected data types
- **Outliers** — uses the IQR method to detect unusual values
- **Calculation Validation** — verifies that computed columns match expected values
- **Store Summary** — SQL-powered breakdown of transactions, quantity, and revenue per store

## Tools Used
- Python
- Pandas
- SQLite (built-in Python library)
- SQL Queries
- HTML/CSS (for report output)

## Project Structure
```
Data Quality Auditor with SQL/
│
├── data/
│   └── bookstore_inventory.csv
│
├── outputs/
│   └── report.html
│
├── auditor.py
└── README.md
```

## How to Run
1. Clone the repository
2. Install dependencies: `pip install pandas`
3. Place your CSV file in the `data/` folder
4. Run: `python auditor.py`
5. Open `outputs/report.html` in your browser

## Data Pipeline
```
CSV → SQLite Database → SQL Query → Pandas → Quality Checks → HTML Report
```

## Sample Output
The report flags data quality issues with clear ✅ and ⚠️ indicators 
across all checks, plus a SQL-generated store performance summary.

## Author
Gerlit Angela Romasanta  
Electronics Engineer | Aspiring Data Engineer