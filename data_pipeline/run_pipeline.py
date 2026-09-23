"""End-to-end Module 1 runner."""

from __future__ import annotations

from pathlib import Path

from cleaner import clean_books, write_cleaning_report
from database import QUERIES, create_database, execute_queries, pandas_equivalent_join, save_query_outputs
from scraper import scrape_books

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
DB_DIR = ROOT / "database"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)

    print("STEP 1/5 - Scraping")
    raw_df = scrape_books()
    raw_path = OUTPUT_DIR / "scraped_books_raw.csv"
    raw_df.to_csv(raw_path, index=False)
    print(f"Saved {len(raw_df)} raw rows to {raw_path}")

    print("\nSTEP 2/5 - Cleaning and conversion")
    clean_df, report = clean_books(raw_df)
    clean_path = OUTPUT_DIR / "clean_books.csv"
    clean_df.to_csv(clean_path, index=False)
    write_cleaning_report(report, str(OUTPUT_DIR / "cleaning_report.md"))
    print(clean_df.dtypes)
    print(f"Saved {len(clean_df)} cleaned rows to {clean_path}")

    print("\nSTEP 3/5 - Loading normalized SQLite database")
    db_path = DB_DIR / "zepto_books.db"
    create_database(db_path, clean_df)
    print(f"SQLite database created at {db_path}")

    print("\nSTEP 4/5 - Executing SQL queries")
    results = execute_queries(db_path)
    for name, result in results.items():
        print(f"\n{name}")
        print(result.to_string(index=False))

    print("\nSTEP 5/5 - Reproducing JOIN with pandas.merge")
    sql_join, pandas_join = pandas_equivalent_join(db_path, clean_df)
    equivalent = sql_join.equals(pandas_join)
    print("SQL JOIN:")
    print(sql_join.to_string(index=False))
    print("\npandas.merge:")
    print(pandas_join.to_string(index=False))
    print(f"\nJOIN outputs equivalent: {equivalent}")
    if not equivalent:
        raise RuntimeError("SQL JOIN and pandas.merge results are not equivalent.")

    save_query_outputs(
        OUTPUT_DIR / "sql_queries_and_outputs.md",
        results,
        QUERIES,
        sql_join,
        pandas_join,
    )

    print("\nMODULE 1 COMPLETE")
    print("Required outputs are available under data_pipeline/output/ and data_pipeline/database/.")


if __name__ == "__main__":
    main()
