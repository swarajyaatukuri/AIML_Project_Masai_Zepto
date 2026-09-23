# Zepto Data & AI Platform — Capstone Project

This repository implements the three required modules as one connected capstone submission:

- `data_pipeline/` — scrape, clean, convert, normalize, store, and query book data.
- `analytics/` — profile and clean Titanic data, perform EDA, classification, imbalance handling, tuning, regression, and save a complete model pipeline.
- `support_assistant/` — local RAG support assistant using Sentence Transformers + ChromaDB + LangGraph + FastAPI, with deterministic `MOCK_LLM` mode as the required baseline.

The repository deliberately uses Python scripts instead of notebooks. The project specification allows scripts as long as the stages are clearly ordered and the required written interpretations are stored as Markdown inside the repository.

## Recommended environment

Use Python 3.11–3.13. Create a separate virtual environment for each module so dependency upgrades in one module do not interfere with another.

## Module 1 — Data Pipeline

Install:

```powershell
cd data_pipeline
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run_pipeline.py
```

The module scrapes three categories from `books.toscrape.com`, cleans the records, converts GBP to INR using the required fixed project rate `1 GBP = 105.50 INR`, loads SQLite, runs the required SQL queries, and verifies the JOIN result against `pd.merge`.

Generated outputs appear under `data_pipeline/output/` and the SQLite database is generated under `data_pipeline/database/`.

## Module 2 — Analytics

Install:

```powershell
cd analytics
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python 01_eda.py
python 02_modeling.py
```

`01_eda.py` is the only script that loads the raw Titanic dataset through `sns.load_dataset('titanic')`. It immediately saves `analytics/titanic.csv` as the offline raw fallback, then performs profiling, cleaning, EDA, written interpretations, and exploratory standardization. It also saves the cleaned continuation dataset as `analytics/titanic_cleaned.csv`.

`02_modeling.py` reads the saved cleaned continuation dataset and performs the full modeling pipeline. It saves the best fitted preprocessing + model pipeline to `analytics/artifacts/best_classifier_pipeline.joblib` and generates all requested evaluation outputs.

The first Seaborn dataset load requires internet access. Once `titanic.csv` has been created, the raw fallback remains available for grading/offline inspection.

## Module 3 — Support Assistant

Install:

```powershell
cd support_assistant
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python ingest.py
uvicorn main:app --host 127.0.0.1 --port 7860 --reload
```

Leave `MOCK_LLM` unset or set it to `1` for the required deterministic grading mode. No LLM API key is required in this mode.

Test the API from another terminal:

```powershell
curl.exe -X POST http://127.0.0.1:7860/ask `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"What is the delivery policy?\"}"

curl.exe -X POST http://127.0.0.1:7860/ask `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"What is 2 + 2?\"}"
```

A Dockerfile is also provided:

```powershell
docker build -t zepto-support ./support_assistant
docker run --rm -p 7860:7860 zepto-support
```

## Design summary

### Data pipeline

The pipeline separates responsibilities into scraping, cleaning, database loading/querying, and orchestration. Raw HTML values are preserved in a CSV before normalization. Numeric parsing failures are converted to `NaN` and median-imputed for `price_gbp`; malformed rating values are median-imputed using the parsed rating median; rows with missing title/category/availability are dropped because those fields are required for the relational record. SQLite contains normalized `categories` and `books` tables linked by a foreign key.

### Analytics

The EDA stage reports missingness and follows the required threshold rule: less than 5% missing → drop affected rows; 5%–30% → impute; very high missingness → drop the column when it is not reliable. The model stage uses a stratified split before preprocessing and a `ColumnTransformer`/`Pipeline` so imputers, encoders, and scalers are fitted only on training data. The imbalance comparison uses baseline, `class_weight='balanced'`, and SMOTE applied only to the training fold.

### Support assistant

The RAG service performs ingestion → local embedding → ChromaDB retrieval → generation. `classify_intent`, `retrieve_and_answer`, and `direct_answer` are LangGraph nodes. In the default `MOCK_LLM` mode, classification and answer generation are deterministic and make no LLM network calls; embeddings and ChromaDB retrieval still run locally. An optional real-LLM branch is included behind `MOCK_LLM=0`.

## Academic-integrity note

The implementation is written for this project from the supplied specification. Before submission, review the code and generated interpretations, understand each step, and make any wording changes needed so the submitted work reflects your own understanding.
