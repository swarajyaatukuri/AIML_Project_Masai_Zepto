<<<<<<< HEAD
# AIML_Project_Masai_Zepto
AIML_Project_Masai_Zepto
=======
# Module 1 — Data Pipeline

## Requirements covered

- Scrapes all paginated books from three categories: Travel, Mystery, and Historical Fiction.
- Produces at least 60 books when the live site is in its normal state.
- Cleans price, rating, and availability into typed columns.
- Median-imputes numeric parse failures and drops only rows missing required relational fields.
- Converts GBP to INR using `1 GBP = 105.50 INR`.
- Loads normalized SQLite `categories` and `books` tables connected by a foreign key.
- Runs six SQL queries covering the required clauses and a JOIN.
- Reads query outputs with `pd.read_sql_query`.
- Reproduces the JOIN using `pd.merge` and asserts equality.

## Run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_pipeline.py
```

The scripts require internet access because the source website is live.
>>>>>>> eb4559f (initial commit of all files)
