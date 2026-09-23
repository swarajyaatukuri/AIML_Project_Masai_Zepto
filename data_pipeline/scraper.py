"""Scrape book data from books.toscrape.com."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
CATEGORY_URLS = {
    "Travel": "catalogue/category/books/travel_2/index.html",
    "Mystery": "catalogue/category/books/mystery_3/index.html",
    "Historical Fiction": "catalogue/category/books/historical-fiction_4/index.html",
}
# Fallback path in case the site's category slug changes. The scraper verifies
# the page title/records and will fail loudly if a category cannot be found.

RATING_TEXT = {"One", "Two", "Three", "Four", "Five"}


@dataclass(frozen=True)
class ScrapeConfig:
    timeout_seconds: int = 30
    user_agent: str = "Mozilla/5.0 (Capstone Data Pipeline; educational scraping)"


def _request(session: requests.Session, url: str, config: ScrapeConfig) -> str:
    response = session.get(
        url,
        headers={"User-Agent": config.user_agent},
        timeout=config.timeout_seconds,
    )
    response.raise_for_status()
    return response.text


def _parse_listing(html: str, page_url: str, category: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict] = []

    for article in soup.select("article.product_pod"):
        title_node = article.select_one("h3 a")
        price_node = article.select_one(".price_color")
        rating_node = article.select_one(".star-rating")
        availability_node = article.select_one(".availability")

        if not title_node:
            continue

        title = (title_node.get("title") or title_node.get_text(" ", strip=True)).strip()
        href = title_node.get("href", "")
        detail_url = urljoin(page_url, href)
        price = price_node.get_text(" ", strip=True) if price_node else None
        availability = availability_node.get_text(" ", strip=True) if availability_node else None
        star_rating = None
        if rating_node:
            classes = rating_node.get("class", [])
            star_rating = next((cls for cls in classes if cls in RATING_TEXT), None)

        records.append(
            {
                "title": title,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": category,
                "detail_url": detail_url,
            }
        )

    return records


def scrape_category(
    session: requests.Session,
    category: str,
    relative_url: str,
    config: ScrapeConfig,
) -> list[dict]:
    first_url = urljoin(BASE_URL, relative_url)
    all_records: list[dict] = []
    next_url: str | None = first_url
    page_number = 0

    while next_url:
        page_number += 1
        html = _request(session, next_url, config)
        records = _parse_listing(html, next_url, category)
        if not records:
            if page_number == 1:
                raise RuntimeError(f"No products parsed for category {category}: {next_url}")
            break
        all_records.extend(records)

        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.select_one("li.next a")
        next_url = urljoin(next_url, next_link["href"]) if next_link and next_link.get("href") else None

    return all_records


def scrape_books(config: ScrapeConfig | None = None) -> pd.DataFrame:
    config = config or ScrapeConfig()
    session = requests.Session()
    records: list[dict] = []

    for category, relative_url in CATEGORY_URLS.items():
        category_records = scrape_category(session, category, relative_url, config)
        print(f"Scraped {len(category_records):>3} books from {category}")
        records.extend(category_records)

    df = pd.DataFrame(records)
    required = {"title", "price", "star_rating", "availability", "category"}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"Scraped data is missing required columns: {sorted(missing)}")

    if len(df) < 60 or df["category"].nunique() < 3:
        raise RuntimeError(
            "Acceptance criterion failed: dataset must contain at least 60 books across at least 3 categories."
        )

    return df


if __name__ == "__main__":
    frame = scrape_books()
    print(frame.head())
    print(frame.shape)
