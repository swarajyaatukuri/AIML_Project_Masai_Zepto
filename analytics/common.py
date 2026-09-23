"""Shared analytics preprocessing utilities."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CLASSIFICATION_FEATURES = [
    "pclass",
    "sex",
    "age",
    "sibsp",
    "parch",
    "fare",
    "embarked",
]
TARGET = "survived"
NUMERIC_FEATURES = ["pclass", "age", "sibsp", "parch", "fare"]
CATEGORICAL_FEATURES = ["sex", "embarked"]


def make_preprocessor(
    numeric_features: Iterable[str] = NUMERIC_FEATURES,
    categorical_features: Iterable[str] = CATEGORICAL_FEATURES,
) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, list(numeric_features)),
            ("cat", categorical_pipeline, list(categorical_features)),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def adjusted_r2(r2: float, n: int, p: int) -> float:
    if n <= p + 1:
        return float("nan")
    return float(1 - (1 - r2) * (n - 1) / (n - p - 1))


def strongest_correlation_pairs(corr: pd.DataFrame, top_n: int = 2) -> list[tuple[str, str, float, float]]:
    records: list[tuple[str, str, float, float]] = []
    cols = corr.columns.tolist()
    for i, left in enumerate(cols):
        for j in range(i + 1, len(cols)):
            right = cols[j]
            value = float(corr.loc[left, right])
            records.append((left, right, value, abs(value)))
    records.sort(key=lambda item: item[3], reverse=True)
    return records[:top_n]


def as_float_dict(values: dict) -> dict:
    return {key: float(value) if isinstance(value, (np.floating, float)) else value for key, value in values.items()}
