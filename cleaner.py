"""Clean scraped book data and apply the project currency conversion."""

from __future__ import annotations

import re
from typing import Tuple

import pandas as pd

GBP_TO_INR = 105.50
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def _parse_price(value: object) -> float:
    if pd.isna(value):
        return float("nan")
    text = str(value).strip()
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text.replace(",", ""))
    return float(match.group(1)) if match else float("nan")


def _parse_rating(value: object) -> float:
    if pd.isna(value):
        return float("nan")
    return float(RATING_MAP.get(str(value).strip(), float("nan")))


def _parse_stock(value: object) -> object:
    if pd.isna(value):
        return pd.NA
    text = str(value).strip().lower()
    if "in stock" in text:
        return True
    if "out of stock" in text:
        return False
    return pd.NA


def clean_books(raw: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    df = raw.copy()
    report: dict = {
        "input_rows": int(len(df)),
        "input_columns": list(df.columns),
        "numeric_imputations": {},
        "dropped_rows": {},
    }

    df["price_gbp"] = df["price"].map(_parse_price)
    df["rating"] = df["star_rating"].map(_parse_rating)
    df["in_stock"] = df["availability"].map(_parse_stock).astype("boolean")

    price_bad = int(df["price_gbp"].isna().sum())
    if price_bad:
        median_price = float(df["price_gbp"].median())
        df["price_gbp"] = df["price_gbp"].fillna(median_price)
        report["numeric_imputations"]["price_gbp"] = {
            "count": price_bad,
            "method": "median",
            "value": median_price,
        }

    rating_bad = int(df["rating"].isna().sum())
    if rating_bad:
        median_rating = float(df["rating"].median())
        df["rating"] = df["rating"].fillna(median_rating)
        # Ratings must be integer 1-5 after cleaning.
        df["rating"] = df["rating"].round().clip(1, 5)
        report["numeric_imputations"]["rating"] = {
            "count": rating_bad,
            "method": "median",
            "value": median_rating,
        }

    required_row_fields = ["title", "category", "in_stock"]
    before = len(df)
    df = df.dropna(subset=required_row_fields).copy()
    report["dropped_rows"]["missing_required_fields"] = before - len(df)

    df["price_gbp"] = df["price_gbp"].astype(float).round(2)
    df["rating"] = df["rating"].astype(int)
    df["in_stock"] = df["in_stock"].astype(bool)
    df["price_inr"] = (df["price_gbp"] * GBP_TO_INR).round(2)

    df = df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category",
            "detail_url",
        ]
    ].reset_index(drop=True)

    report["output_rows"] = int(len(df))
    report["rate_gbp_to_inr"] = GBP_TO_INR
    return df, report


def write_cleaning_report(report: dict, path: str) -> None:
    lines = ["# Cleaning Report", ""]
    lines.append(f"Input rows: {report['input_rows']}")
    lines.append(f"Output rows: {report['output_rows']}")
    lines.append(f"Fixed conversion: 1 GBP = {report['rate_gbp_to_inr']:.2f} INR")
    lines.append("")
    lines.append("## Numeric imputations")
    if report["numeric_imputations"]:
        for column, details in report["numeric_imputations"].items():
            lines.append(
                f"- `{column}`: {details['count']} values, method={details['method']}, "
                f"median={details['value']}"
            )
    else:
        lines.append("- None required on this scrape.")
    lines.append("")
    lines.append("## Dropped rows")
    for reason, count in report["dropped_rows"].items():
        lines.append(f"- {reason}: {count}")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
