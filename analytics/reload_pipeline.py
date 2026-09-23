"""Reload the saved full classifier pipeline and predict from raw feature data."""

from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "artifacts" / "best_classifier_pipeline.joblib"

RAW_EXAMPLE = pd.DataFrame(
    [
        {
            "pclass": 1,
            "sex": "female",
            "age": 29,
            "sibsp": 0,
            "parch": 0,
            "fare": 211.3375,
            "embarked": "S",
        }
    ]
)


def main() -> None:
    if not ARTIFACT.exists():
        raise FileNotFoundError("Run 02_modeling.py first so the complete pipeline is saved.")
    pipeline = joblib.load(ARTIFACT)
    prediction = pipeline.predict(RAW_EXAMPLE)
    probability = pipeline.predict_proba(RAW_EXAMPLE)[:, 1]
    print("Raw input:")
    print(RAW_EXAMPLE.to_string(index=False))
    print("Prediction:", prediction.tolist())
    print("Survival probability:", probability.round(4).tolist())


if __name__ == "__main__":
    main()
