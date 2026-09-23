"""SQLite schema, loading, SQL demonstrations, and pandas equivalence checks."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd

SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL NOT NULL,
    price_inr REAL NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    in_stock INTEGER NOT NULL CHECK (in_stock IN (0, 1)),
    category_id INTEGER NOT NULL,
    detail_url TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
"""

QUERIES: Dict[str, str] = {
    "q1_select_where": """
SELECT title, price_gbp, price_inr, in_stock
FROM books
WHERE in_stock = 1
ORDER BY title;
""".strip(),
    "q2_order_by_limit": """
SELECT title, rating, price_gbp, price_inr
FROM books
ORDER BY rating DESC, price_gbp DESC
LIMIT 10;
""".strip(),
    "q3_distinct": """
SELECT DISTINCT category_name
FROM categories
ORDER BY category_name;
""".strip(),
    "q4_between": """
SELECT title, price_gbp, rating
FROM books
WHERE price_gbp BETWEEN 20 AND 40
ORDER BY price_gbp, title;
""".strip(),
    "q5_in": """
SELECT title, rating, in_stock
FROM books
WHERE rating IN (4, 5)
ORDER BY rating DESC, title;
""".strip(),
    "q6_join": """
SELECT
    c.category_name,
    b.title,
    b.rating,
    b.price_inr
FROM books AS b
INNER JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY b.rating DESC, b.price_inr DESC, b.title
LIMIT 10;
""".strip(),
}


def create_database(db_path: Path, books_df: pd.DataFrame) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)

        categories = (
            books_df[["category"]]
            .drop_duplicates()
            .sort_values("category")
            .reset_index(drop=True)
        )
        for name in categories["category"]:
            conn.execute(
                "INSERT INTO categories(category_name) VALUES (?)",
                (str(name),),
            )

        category_map = {
            category_name: category_id
            for category_name, category_id in conn.execute(
                "SELECT category_name, category_id FROM categories"
            )
        }

        insert_rows = []
        for row in books_df.itertuples(index=False):
            insert_rows.append(
                (
                    row.title,
                    float(row.price_gbp),
                    float(row.price_inr),
                    int(row.rating),
                    int(bool(row.in_stock)),
                    int(category_map[row.category]),
                    row.detail_url,
                )
            )
        conn.executemany(
            """
            INSERT INTO books
                (title, price_gbp, price_inr, rating, in_stock, category_id, detail_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            insert_rows,
        )
        conn.commit()


def execute_queries(db_path: Path) -> dict[str, pd.DataFrame]:
    results: dict[str, pd.DataFrame] = {}
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        for name, query in QUERIES.items():
            results[name] = pd.read_sql_query(query, conn)
    return results


def pandas_equivalent_join(db_path: Path, books_df: pd.DataFrame) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        books_sql = pd.read_sql_query(
            "SELECT book_id, title, price_gbp, price_inr, rating, in_stock, category_id, detail_url FROM books",
            conn,
        )
        categories_sql = pd.read_sql_query(
            "SELECT category_id, category_name FROM categories",
            conn,
        )

    # Pure in-memory JOIN reproduction: both inputs are DataFrames, and no SQL
    # query is used to construct the pandas-side result.
    categories_df = (
        books_df[["category"]]
        .drop_duplicates()
        .rename(columns={"category": "category_name"})
    )
    in_memory_books = books_df.copy().merge(
        categories_df,
        left_on="category",
        right_on="category_name",
        how="inner",
        validate="many_to_one",
    )
    pandas_join = (
        in_memory_books[["category_name", "title", "rating", "price_inr"]]
        .sort_values(["rating", "price_inr", "title"], ascending=[False, False, True])
        .head(10)
        .reset_index(drop=True)
    )

    sql_join = (
        books_sql.merge(categories_sql, on="category_id", how="inner", validate="many_to_one")
        [["category_name", "title", "rating", "price_inr"]]
        .sort_values(["rating", "price_inr", "title"], ascending=[False, False, True])
        .head(10)
        .reset_index(drop=True)
    )

    # Normalize dtypes for a strict equality comparison.
    sql_join["price_inr"] = sql_join["price_inr"].astype(float).round(2)
    pandas_join["price_inr"] = pandas_join["price_inr"].astype(float).round(2)
    sql_join["rating"] = sql_join["rating"].astype(int)
    pandas_join["rating"] = pandas_join["rating"].astype(int)
    return sql_join, pandas_join


def save_query_outputs(
    path: Path,
    results: dict[str, pd.DataFrame],
    sql_queries: dict[str, str],
    sql_join: pd.DataFrame,
    pandas_join: pd.DataFrame,
) -> None:
    lines = ["# SQL Queries and Outputs", ""]
    for name, query in sql_queries.items():
        lines.extend([f"## {name}", "", "```sql", query, "```", ""])
        lines.append("```text")
        lines.append(results[name].to_string(index=False))
        lines.extend(["```", ""])

    lines.extend(["## JOIN equivalence", "", "### SQL JOIN result", "", "```text"])
    lines.append(sql_join.to_string(index=False))
    lines.extend(["```", "", "### pandas.merge result", "", "```text"])
    lines.append(pandas_join.to_string(index=False))
    lines.extend(["```", "", f"Equivalent: `{sql_join.equals(pandas_join)}`", ""])

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
