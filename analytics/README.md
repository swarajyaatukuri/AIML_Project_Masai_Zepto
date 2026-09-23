# Module 2 — Analytics Pipeline

Run `python 01_eda.py` first and `python 02_modeling.py` second.

## Data-loading rule

`01_eda.py` is the only place that calls `sns.load_dataset("titanic")`. Immediately after that load, it writes `titanic.csv` as the offline raw fallback required by the capstone. It then cleans that one in-memory DataFrame and writes `titanic_cleaned.csv` for the modeling continuation. `02_modeling.py` reads the cleaned continuation file and never calls Seaborn's loader.

## Missing-data strategy

The script reports the measured missing percentage for every affected column. It then follows the project threshold:

- under 5% → drop affected rows;
- 5%–30% → impute;
- above 30% → drop the unreliable column when it is not suitable as a stable modeling feature.

For the standard Titanic dataset, `deck` is expected to have very high missingness, `age` is expected to be in the 5%–30% range, and `embarked`/`embark_town` are expected to be under 5%; the script measures the percentages at runtime rather than hardcoding them.

## Modeling safeguards

The classification split happens before any preprocessing and is stratified by `survived`. The preprocessing pipeline contains the imputation, one-hot encoding, and scaling steps. Therefore each fitted preprocessing object is trained only on the training split. SMOTE is wrapped inside an imbalanced-learn pipeline so oversampling occurs only after the training preprocessing pipeline and only during fitting.
