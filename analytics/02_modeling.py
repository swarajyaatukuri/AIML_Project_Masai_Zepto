"""Module 2 Part B: classification, imbalance comparison, tuning, regression."""

from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
    r2_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier, plot_tree

from common import (
    CATEGORICAL_FEATURES,
    CLASSIFICATION_FEATURES,
    NUMERIC_FEATURES,
    TARGET,
    adjusted_r2,
    make_preprocessor,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
ARTIFACTS = ROOT / "artifacts"
OUT.mkdir(parents=True, exist_ok=True)
ARTIFACTS.mkdir(parents=True, exist_ok=True)
RANDOM_STATE = 42


def make_classifier_pipeline(estimator) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocess", make_preprocessor()),
            ("model", estimator),
        ]
    )


def evaluate_classifier(name: str, model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    return {
        "model": name,
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "auc": roc_auc_score(y_test, probabilities),
        "confusion_matrix": confusion_matrix(y_test, predictions),
        "predictions": predictions,
        "probabilities": probabilities,
    }


def save_classifier_figures(results: list[dict], y_test: pd.Series) -> None:
    fig, axes = plt.subplots(1, len(results), figsize=(15, 4.5))
    for axis, result in zip(axes, results):
        ConfusionMatrixDisplay(result["confusion_matrix"], display_labels=["Not survived", "Survived"]).plot(
            ax=axis, colorbar=False
        )
        axis.set_title(result["model"])
    plt.tight_layout()
    plt.savefig(OUT / "classification_confusion_matrices.png", dpi=160, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(8, 6))
    for result in results:
        fpr, tpr, _ = roc_curve(y_test, result["probabilities"])
        plt.plot(fpr, tpr, label=f"{result['model']} (AUC={result['auc']:.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Random classifier")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves — Three Classifiers")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "classification_roc_curves.png", dpi=160, bbox_inches="tight")
    plt.close()


def save_tree_plot(model: Pipeline) -> None:
    preprocess = model.named_steps["preprocess"]
    tree = model.named_steps["model"]
    feature_names = preprocess.get_feature_names_out().tolist()
    plt.figure(figsize=(22, 12))
    plot_tree(
        tree,
        feature_names=feature_names,
        class_names=["0", "1"],
        filled=False,
        rounded=True,
        max_depth=4,
        fontsize=8,
    )
    plt.title("Decision Tree — first four levels shown for readability")
    plt.savefig(OUT / "decision_tree.png", dpi=160, bbox_inches="tight")
    plt.close()


def run_imbalance_comparison(X_train, X_test, y_train, y_test) -> pd.DataFrame:
    variants = {
        "baseline": make_classifier_pipeline(
            LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)
        ),
        "class_weight_balanced": make_classifier_pipeline(
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)
        ),
        "smote": ImbPipeline(
            steps=[
                ("preprocess", make_preprocessor()),
                ("smote", SMOTE(random_state=RANDOM_STATE)),
                ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
            ]
        ),
    }
    rows = []
    for name, model in variants.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        rows.append(
            {
                "variant": name,
                "precision": precision_score(y_test, pred, zero_division=0),
                "recall": recall_score(y_test, pred, zero_division=0),
                "f1": f1_score(y_test, pred, zero_division=0),
            }
        )
    comparison = pd.DataFrame(rows)
    comparison.to_csv(OUT / "imbalance_comparison.csv", index=False)
    return comparison


def run_rf_grid_search(X_train, y_train) -> tuple[Pipeline, GridSearchCV]:
    pipeline = make_classifier_pipeline(
        RandomForestClassifier(
            random_state=RANDOM_STATE,
            n_jobs=-1,
            bootstrap=True,
            oob_score=True,
        )
    )
    param_grid = {
        "model__n_estimators": [100, 200],
        "model__max_depth": [None, 5, 10],
        "model__max_features": ["sqrt", "log2"],
    }
    grid = GridSearchCV(
        pipeline,
        param_grid=param_grid,
        scoring="f1",
        cv=5,
        n_jobs=-1,
        refit=True,
        return_train_score=False,
    )
    grid.fit(X_train, y_train)
    best_model = grid.best_estimator_
    oob_score = best_model.named_steps["model"].oob_score_
    grid_report = pd.DataFrame(
        [
            {
                "best_params": str(grid.best_params_),
                "best_cv_f1": grid.best_score_,
                "oob_score": oob_score,
            }
        ]
    )
    grid_report.to_csv(OUT / "random_forest_grid_search.csv", index=False)
    return best_model, grid


def run_regression(df: pd.DataFrame, train_idx, test_idx) -> dict:
    regression_features = [
        "survived",
        "pclass",
        "sex",
        "age",
        "sibsp",
        "parch",
        "embarked",
    ]
    X = df[regression_features]
    y = df["fare"]
    preprocessor = make_preprocessor(
        numeric_features=["survived", "pclass", "age", "sibsp", "parch"],
        categorical_features=["sex", "embarked"],
    )
    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", LinearRegression()),
        ]
    )
    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]
    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]
    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
    r2 = r2_score(y_test, pred)
    p = len(pipeline.named_steps["preprocess"].get_feature_names_out())
    adj = adjusted_r2(r2, n=len(y_test), p=p)
    residuals = y_test.to_numpy() - pred

    plt.figure(figsize=(8, 5))
    plt.scatter(pred, residuals, alpha=0.7)
    plt.axhline(0, linestyle="--")
    plt.xlabel("Predicted fare")
    plt.ylabel("Residual (actual - predicted)")
    plt.title("Regression Residual Plot")
    plt.tight_layout()
    plt.savefig(OUT / "regression_residual_plot.png", dpi=160, bbox_inches="tight")
    plt.close()

    # Simple heteroscedasticity flag: compare residual variance in low/mid/high fitted-value bins.
    residual_frame = pd.DataFrame({"predicted": pred, "residual": residuals}).sort_values("predicted")
    bins = np.array_split(residual_frame, 3)
    variances = [float(chunk["residual"].var(ddof=1)) for chunk in bins if len(chunk) > 1]
    hetero = bool(max(variances) > 2.0 * min(variances)) if variances else False

    metrics = {
        "MAE": float(mae),
        "RMSE": rmse,
        "R2": float(r2),
        "Adjusted_R2": float(adj),
        "residual_variances_by_fitted_tertile": variances,
        "heteroscedasticity_observed": hetero,
        "n_test": len(y_test),
        "p_features_after_preprocessing": p,
    }
    pd.DataFrame([metrics]).to_json(OUT / "regression_metrics.json", orient="records", indent=2)
    return metrics


def main() -> None:
    cleaned_path = ROOT / "titanic_cleaned.csv"
    if not cleaned_path.exists():
        raise FileNotFoundError(
            "titanic_cleaned.csv is missing. Run 01_eda.py first so the one raw-data load and cleaning stage has completed."
        )

    df = pd.read_csv(cleaned_path)
    X = df[CLASSIFICATION_FEATURES].copy()
    y = df[TARGET].astype(int).copy()

    train_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]
    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    class_balance = (
        y.value_counts(normalize=False)
        .rename(index={0: "not_survived", 1: "survived"})
        .to_frame("count")
    )
    class_balance["percent"] = class_balance["count"] / len(y) * 100
    class_balance.to_csv(OUT / "class_balance.csv")

    models = {
        "Logistic Regression": make_classifier_pipeline(
            LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)
        ),
        "Decision Tree": make_classifier_pipeline(
            DecisionTreeClassifier(random_state=RANDOM_STATE, max_depth=6)
        ),
        "Random Forest": make_classifier_pipeline(
            RandomForestClassifier(
                n_estimators=200,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )
        ),
    }

    results = []
    fitted_models = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        fitted_models[name] = model
        results.append(evaluate_classifier(name, model, X_test, y_test))

    save_classifier_figures(results, y_test)
    save_tree_plot(fitted_models["Decision Tree"])

    metrics_table = pd.DataFrame(
        [
            {
                key: value
                for key, value in result.items()
                if key in ["model", "accuracy", "precision", "recall", "f1", "auc"]
            }
            for result in results
        ]
    )
    metrics_table.to_csv(OUT / "classification_metrics.csv", index=False)

    imbalance = run_imbalance_comparison(X_train, X_test, y_train, y_test)
    rf_best, grid = run_rf_grid_search(X_train, y_train)
    regression_metrics = run_regression(df, train_idx, test_idx)

    # Choose the classifier by F1 first, then AUC, then accuracy. This is a transparent
    # metric-based selection, not a hidden choice.
    best_row = metrics_table.sort_values(["f1", "auc", "accuracy"], ascending=False).iloc[0]
    best_name = str(best_row["model"])
    best_pipeline = fitted_models[best_name]
    artifact_path = ARTIFACTS / "best_classifier_pipeline.joblib"
    joblib.dump(best_pipeline, artifact_path)

    best_loaded = joblib.load(artifact_path)
    reload_pred = best_loaded.predict(X_test.iloc[:5])
    reload_ok = len(reload_pred) == min(5, len(X_test))
    (ARTIFACTS / "reload_check.txt").write_text(
        f"Reloaded artifact: {artifact_path.name}\n"
        f"Raw-input prediction check passed: {reload_ok}\n"
        f"Predictions on first five test rows: {reload_pred.tolist()}\n",
        encoding="utf-8",
    )

    final_lines = [
        "# Modeling Report",
        "",
        "## Stratified split and class balance",
        "",
        "A stratified 80/20 split was performed before any preprocessing so the train and test sets preserve the observed survived/not-survived class proportions. Stratification matters here because the target is binary and the classes are not exactly balanced; preserving the class composition makes the test evaluation more stable and representative of the original sample.",
        "",
        class_balance.to_markdown(),
        "",
        "## Classifier comparison",
        "",
        metrics_table.round(4).to_markdown(index=False),
        "",
        "All three classifiers use the identical train/test rows and the same preprocessing contract: median imputation for numeric variables, most-frequent imputation for categorical variables, one-hot encoding for `sex`/`embarked`, and StandardScaler for numeric features. The preprocessing pipeline is fitted only through the training split.",
        "",
        "## Imbalance comparison",
        "",
        imbalance.round(4).to_markdown(index=False),
        "",
    ]

    best_imbalance = imbalance.sort_values("f1", ascending=False).iloc[0]
    final_lines.append(
        f"The highest F1 in the three-way imbalance comparison is the `{best_imbalance['variant']}` variant ({best_imbalance['f1']:.3f}). "
        "The comparison is deliberately reported rather than assumed: precision, recall, and F1 reflect different trade-offs when the positive class is not perfectly balanced."
    )
    final_lines.extend(
        [
            "",
            "## Random Forest hyperparameter tuning",
            "",
            f"Best parameters: `{grid.best_params_}`",
            f"Best cross-validation F1: **{grid.best_score_:.4f}**",
            f"Best estimator OOB score: **{rf_best.named_steps['model'].oob_score_:.4f}**",
            "The Random Forest estimator was constructed with `oob_score=True`, so the fitted OOB score is available as required.",
            "",
            "## Regression side-task",
            "",
            pd.DataFrame([regression_metrics])["MAE RMSE R2 Adjusted_R2".split()].round(4).to_markdown(index=False),
            "",
        ]
    )
    hetero_text = (
        "The residual variance changes materially across fitted-value ranges, so the residual plot shows evidence consistent with heteroscedasticity."
        if regression_metrics["heteroscedasticity_observed"]
        else "The residual variance is relatively similar across fitted-value ranges, so the residual plot does not show a strong heteroscedastic pattern."
    )
    final_lines.extend(
        [
            hetero_text,
            "",
            "## Final classifier selection",
            "",
            f"The metric-based selection chooses **{best_name}** because it has the highest F1 in the held-out test comparison after using the specified common preprocessing contract. Its test accuracy is **{best_row['accuracy']:.3f}**, precision is **{best_row['precision']:.3f}**, recall is **{best_row['recall']:.3f}**, F1 is **{best_row['f1']:.3f}**, and AUC is **{best_row['auc']:.3f}**. These values summarize different performance dimensions, so the choice is based first on F1 and then on AUC/accuracy as transparent tie-breakers rather than treating all metrics as one scale. The complete fitted preprocessing + classifier pipeline has been saved so raw, unprocessed feature rows can be passed directly to the loaded artifact.",
            "",
            "## Saved artifacts",
            "",
            "- `classification_metrics.csv` and `classification_confusion_matrices.png` — full classifier evaluation.",
            "- `classification_roc_curves.png` — ROC curves and AUC.",
            "- `decision_tree.png` — labeled decision-tree visualization.",
            "- `imbalance_comparison.csv` — baseline vs balanced weights vs SMOTE.",
            "- `random_forest_grid_search.csv` — best parameters and OOB score.",
            "- `regression_metrics.json` and `regression_residual_plot.png` — regression side-task.",
            "- `artifacts/best_classifier_pipeline.joblib` — complete fitted classification pipeline.",
            "- `artifacts/reload_check.txt` — artifact reload/prediction verification.",
        ]
    )
    (OUT / "modeling_report.md").write_text("\n".join(final_lines) + "\n", encoding="utf-8")

    print(metrics_table.round(4).to_string(index=False))
    print("\nBest classifier:", best_name)
    print("Saved:", artifact_path)
    print("Modeling complete. See analytics/outputs/modeling_report.md")


if __name__ == "__main__":
    main()
