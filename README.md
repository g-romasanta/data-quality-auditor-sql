# 📊 Automated Data Quality Auditor

A beginner Python project that automatically checks a CSV dataset for common 
data quality issues and generates a clean HTML report.

## 🔍 What It Checks
- **Missing Values** — detects null/empty cells per column
- **Duplicate Rows** — flags any repeated rows in the dataset
- **Data Types** — checks if columns have the expected data types
- **Outliers** — uses the IQR method to detect unusual values
- **Calculation Validation** — verifies that computed columns match expected values

## 🛠️ Tools Used
- Python
- Pandas
- HTML/CSS (for report output)

## 📁 Project Structure
```
Data Quality Auditor/
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

## 🚀 How to Run
1. Clone the repository
2. Install dependencies: `pip install pandas`
3. Place your CSV file in the `data/` folder
4. Run: `python auditor.py`
5. Open `outputs/report.html` in your browser

## 📌 Sample Output
The report flags data quality issues with clear ✅ and ⚠️ indicators 
across all checks.

## 👩‍💻 Author
Gerlit Angela Romasanta  
Electronics Engineer | Aspiring Data Engineer