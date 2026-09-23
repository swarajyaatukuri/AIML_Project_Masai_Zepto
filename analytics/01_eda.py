"""Module 2 Part A: load, profile, clean, visualize, and report."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme()

from common import strongest_correlation_pairs

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=160, bbox_inches="tight")
    plt.close()


def missing_strategy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_pct = (df.isna().mean() * 100).sort_values(ascending=False)
    affected = missing_pct[missing_pct > 0]
    report_rows = []

    cleaned = df.copy()

    # Very high missingness: deck is not a dependable feature for this project.
    high_cols = affected[affected > 30].index.tolist()
    for col in high_cols:
        cleaned = cleaned.drop(columns=[col])
        report_rows.append(
            {
                "column": col,
                "missing_percent": affected[col],
                "strategy": "drop_column",
                "reason": ">30% missing; imputation would be unreliable",
            }
        )

    # Under 5%: drop rows containing the affected value.
    low_cols = affected[(affected < 5) & (~affected.index.isin(high_cols))].index.tolist()
    if low_cols:
        before = len(cleaned)
        cleaned = cleaned.dropna(subset=low_cols)
        dropped = before - len(cleaned)
        for col in low_cols:
            report_rows.append(
                {
                    "column": col,
                    "missing_percent": affected[col],
                    "strategy": "drop_rows",
                    "reason": f"<5% missing; dropped rows affected by this column (total rows dropped across low-missing columns: {dropped})",
                }
            )

    # 5%–30%: numeric median / categorical mode.
    mid_cols = affected[(affected >= 5) & (affected <= 30)].index.tolist()
    for col in mid_cols:
        if pd.api.types.is_numeric_dtype(cleaned[col]):
            value = cleaned[col].median()
            cleaned[col] = cleaned[col].fillna(value)
            strategy = f"median_impute ({value:.4f})"
        else:
            value = cleaned[col].mode(dropna=True).iloc[0]
            cleaned[col] = cleaned[col].fillna(value)
            strategy = f"mode_impute ({value})"
        report_rows.append(
            {
                "column": col,
                "missing_percent": affected[col],
                "strategy": strategy,
                "reason": "5%–30% missing; imputation required",
            }
        )

    # Any non-target column with residual NA after the above is explicitly handled.
    remaining = cleaned.isna().sum()
    for col, count in remaining[remaining > 0].items():
        if col not in affected.index:
            continue
        if pd.api.types.is_numeric_dtype(cleaned[col]):
            value = cleaned[col].median()
            cleaned[col] = cleaned[col].fillna(value)
            strategy = f"median_impute ({value:.4f})"
        else:
            value = cleaned[col].mode(dropna=True).iloc[0]
            cleaned[col] = cleaned[col].fillna(value)
            strategy = f"mode_impute ({value})"
        report_rows.append(
            {
                "column": col,
                "missing_percent": affected.get(col, 0),
                "strategy": strategy,
                "reason": "defensive final cleanup",
            }
        )

    return cleaned.reset_index(drop=True), pd.DataFrame(report_rows)


def univariate_analysis(df: pd.DataFrame, lines: list[str]) -> None:
    for column in ["age", "fare"]:
        plt.figure(figsize=(7, 4))
        values = df[column].dropna().to_numpy()
        plt.hist(values, bins=25, edgecolor="black", alpha=0.8)
        plt.title(f"Histogram — {column}")
        plt.xlabel(column)
        plt.ylabel("Count")
        savefig(f"hist_{column}.png")

        plt.figure(figsize=(7, 3.5))
        plt.boxplot(values, vert=False)
        plt.title(f"Box plot — {column}")
        plt.xlabel(column)
        savefig(f"box_{column}.png")

    lines.append("## Univariate analysis")
    for column in ["age", "fare"]:
        series = df[column].dropna()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = int(((series < lower) | (series > upper)).sum())
        lines.append(
            f"- `{column}` IQR bounds: [{lower:.3f}, {upper:.3f}]. Outlier count: **{outliers}**."
        )

    mean_fare = float(df["fare"].mean())
    median_fare = float(df["fare"].median())
    mode_fare = float(df["fare"].mode().iloc[0])
    if mean_fare > median_fare > mode_fare:
        skew_text = "right-skewed"
    elif mean_fare < median_fare < mode_fare:
        skew_text = "left-skewed"
    else:
        skew_text = "approximately symmetric / not strongly skewed"
    lines.append(
        f"- Fare mean = **{mean_fare:.3f}**, median = **{median_fare:.3f}**, mode = **{mode_fare:.3f}**. "
        f"Because the ordering is mean {('>' if mean_fare > median_fare else '<=' )} median and median {('>' if median_fare > mode_fare else '<=')} mode, `fare` is interpreted as **{skew_text}**."
    )
    lines.append("")


def bivariate_analysis(df: pd.DataFrame, lines: list[str]) -> None:
    sex_rate = df.groupby("sex", observed=True)["survived"].mean().mul(100).round(2)
    pclass_rate = df.groupby("pclass", observed=True)["survived"].mean().mul(100).round(2)
    sex_class_rate = (
        df.groupby(["sex", "pclass"], observed=True)["survived"].mean().mul(100).round(2)
    )

    lines.append("## Bivariate survival rates")
    lines.append("### By sex")
    lines.append(sex_rate.to_frame("survival_rate_percent").to_markdown())
    lines.append("\n### By pclass")
    lines.append(pclass_rate.to_frame("survival_rate_percent").to_markdown())
    lines.append("\n### By sex and pclass")
    lines.append(sex_class_rate.to_frame("survival_rate_percent").to_markdown())
    lines.append("")

    corr_cols = ["survived", "pclass", "age", "sibsp", "parch", "fare"]
    corr = df[corr_cols].corr(numeric_only=True)
    strongest = strongest_correlation_pairs(corr, top_n=2)

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True)
    plt.title("Correlation Matrix — Required Six Numeric Columns")
    savefig("correlation_heatmap.png")

    lines.append("### Correlation matrix")
    lines.append(corr.round(3).to_markdown())
    lines.append("")
    lines.append("### Two strongest absolute off-diagonal correlations")
    for left, right, value, absolute in strongest:
        direction = "positive" if value > 0 else "negative"
        lines.append(
            f"- **{left} vs {right}: r = {value:.3f}** (|r| = {absolute:.3f}), a {direction} relationship."
        )
    lines.append("")

    # Boolean masking examples required by the task.
    female_mask = (df["sex"] == "female") & (df["pclass"].isin([1, 2, 3]))
    male_mask = (df["sex"] == "male") & (df["pclass"].isin([1, 2, 3]))
    lines.append(
        f"Boolean mask sanity checks: female passenger rows = {int(female_mask.sum())}; male passenger rows = {int(male_mask.sum())}."
    )
    lines.append("")


def multivariate_story(df: pd.DataFrame, lines: list[str]) -> None:
    sex_summary = df.groupby("sex", observed=True)["survived"].mean()
    plt.figure(figsize=(8, 5))
    plt.bar(sex_summary.index.astype(str), sex_summary.values)
    plt.ylabel("Survival rate")
    plt.title("Survival Rate by Sex")
    savefig("story_01_survival_by_sex.png")
    lines.append("## Multivariate data story")
    lines.append(
        "### 1. Survival rate by sex\n\nThe bar chart shows a clear difference in survival rates between female and male passengers. This indicates that sex is strongly associated with the target and should remain in the predictive feature set."
    )

    class_summary = df.groupby("pclass", observed=True)["survived"].mean()
    plt.figure(figsize=(8, 5))
    plt.bar(class_summary.index.astype(str), class_summary.values)
    plt.xlabel("pclass")
    plt.ylabel("Survival rate")
    plt.title("Survival Rate by Passenger Class")
    savefig("story_02_survival_by_class.png")
    lines.append(
        "### 2. Survival rate by passenger class\n\nSurvival rate changes substantially across passenger classes. Passenger class therefore provides a second important signal that complements sex and helps explain differences in outcomes."
    )

    plt.figure(figsize=(9, 5))
    groups = []
    labels = []
    for sex in ["female", "male"]:
        for pclass in [1, 2, 3]:
            values = df.loc[(df["sex"] == sex) & (df["pclass"] == pclass), "fare"].dropna().to_numpy()
            if len(values):
                groups.append(values)
                labels.append(f"{sex}-{pclass}")
    plt.boxplot(groups, tick_labels=labels, vert=True)
    plt.ylabel("Fare")
    plt.title("Fare Distribution by Sex and Passenger Class")
    plt.xticks(rotation=30)
    savefig("story_03_fare_by_sex_class.png")
    lines.append(
        "### 3. Fare distribution by sex and class\n\nFare varies by passenger class, and the class composition differs by sex. This provides a multivariate view of the socioeconomic structure underlying the passenger records and explains why fare can add predictive information beyond the class label alone."
    )

    plt.figure(figsize=(9, 6))
    markers = {"female": "o", "male": "x"}
    for survived in [0, 1]:
        for sex in ["female", "male"]:
            subset = df[(df["survived"] == survived) & (df["sex"] == sex)]
            plt.scatter(
                subset["age"], subset["fare"],
                alpha=0.65, marker=markers[sex],
                label=f"survived={survived}, sex={sex}",
            )
    plt.xlabel("Age")
    plt.ylabel("Fare")
    plt.title("Age vs Fare, Split by Survival and Sex")
    plt.legend(fontsize=8)
    savefig("story_04_age_fare_survival.png")
    lines.append(
        "### 4. Age vs fare with survival and sex\n\nThe scatter plot combines age, fare, survival, and sex to show how several variables interact instead of looking at one pair at a time. Survival observations are distributed differently across the age/fare space, reinforcing the need for a multivariate model rather than a single-rule explanation."
    )
    lines.append("")


def standardization_check(df: pd.DataFrame, lines: list[str]) -> None:
    standardized = df.copy()
    summary_rows = []
    for column in ["age", "fare"]:
        series = df[column].astype(float)
        z = (series - series.mean()) / series.std(ddof=1)
        standardized[column + "_z"] = z
        summary_rows.append(
            {
                "column": column,
                "before_mean": series.mean(),
                "before_std": series.std(ddof=1),
                "after_mean": z.mean(),
                "after_std": z.std(ddof=1),
            }
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "standardization_summary.csv", index=False)
    lines.append("## Exploratory z-score standardization")
    lines.append(
        "The following check is performed on the full cleaned DataFrame only for EDA sanity checking. It is not reused by the modeling pipeline; the modeling pipeline performs its own train-only scaling."
    )
    lines.append(summary.round(6).to_markdown(index=False))
    lines.append("")


def main() -> None:
    print("Loading Titanic dataset exactly once with sns.load_dataset('titanic')...")
    raw_fallback = ROOT / "titanic.csv"
    try:
        df = sns.load_dataset("titanic")
        df.to_csv(raw_fallback, index=False)
        print("Seaborn load succeeded; refreshed titanic.csv from the loaded DataFrame.")
    except Exception as exc:  # noqa: BLE001 - deliberate offline fallback
        if not raw_fallback.exists():
            raise RuntimeError(
                "sns.load_dataset('titanic') could not reach the dataset and no offline titanic.csv fallback exists."
            ) from exc
        print(f"Seaborn loader unavailable ({exc!r}); using committed titanic.csv fallback.")
        df = pd.read_csv(raw_fallback)

    lines: list[str] = [
        "# Titanic EDA Report",
        "",
        "## Dataset profile",
        "",
        "### Shape",
        str(df.shape),
        "",
        "### Info",
        "```text",
    ]
    from io import StringIO

    info_buffer = StringIO()
    df.info(buf=info_buffer)
    lines.append(info_buffer.getvalue())
    lines.extend(["```", "", "### Describe", "```text", df.describe(include="all").to_string(), "```", ""])

    missing = (df.isna().mean() * 100).round(4)
    affected = missing[missing > 0]
    lines.append("## Missing-value percentages before cleaning")
    if affected.empty:
        lines.append("No missing values were found.")
    else:
        lines.append(affected.to_frame("missing_percent").to_markdown())
    lines.append("")

    cleaned, missing_report = missing_strategy(df)
    missing_report.to_csv(OUT / "missing_value_strategy.csv", index=False)
    lines.append("## Cleaning decisions")
    lines.append(missing_report.round(4).to_markdown(index=False))
    lines.append("")

    cleaned.to_csv(ROOT / "titanic_cleaned.csv", index=False)
    lines.append(f"Cleaned dataset shape: **{cleaned.shape}**")
    lines.append("")

    # Keep all required fields and exclude derived/redundant boolean flags only from correlation.
    univariate_analysis(cleaned, lines)
    bivariate_analysis(cleaned, lines)
    multivariate_story(cleaned, lines)
    standardization_check(cleaned, lines)

    lines.extend(
        [
            "## Saved artifacts",
            "",
            "- `titanic.csv` — raw offline fallback created immediately after the one network/cache load.",
            "- `titanic_cleaned.csv` — cleaned continuation dataset consumed by `02_modeling.py`.",
            "- `outputs/` — tables, charts, missingness decisions, and the written EDA interpretation.",
        ]
    )

    (OUT / "eda_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved raw fallback: {raw_fallback}")
    print(f"Saved cleaned continuation: {ROOT / 'titanic_cleaned.csv'}")
    print(f"EDA report: {OUT / 'eda_report.md'}")


if __name__ == "__main__":
    main()
