# Modeling Report

## Stratified split and class balance

A stratified 80/20 split was performed before any preprocessing so the train and test sets preserve the observed survived/not-survived class proportions. Stratification matters here because the target is binary and the classes are not exactly balanced; preserving the class composition makes the test evaluation more stable and representative of the original sample.

| survived     |   count |   percent |
|:-------------|--------:|----------:|
| not_survived |     549 |   61.7548 |
| survived     |     340 |   38.2452 |

## Classifier comparison

| model               |   accuracy |   precision |   recall |     f1 |    auc |
|:--------------------|-----------:|------------:|---------:|-------:|-------:|
| Logistic Regression |     0.809  |      0.7833 |   0.6912 | 0.7344 | 0.861  |
| Decision Tree       |     0.7472 |      0.6949 |   0.6029 | 0.6457 | 0.8162 |
| Random Forest       |     0.809  |      0.7656 |   0.7206 | 0.7424 | 0.8196 |

All three classifiers use the identical train/test rows and the same preprocessing contract: median imputation for numeric variables, most-frequent imputation for categorical variables, one-hot encoding for `sex`/`embarked`, and StandardScaler for numeric features. The preprocessing pipeline is fitted only through the training split.

## Imbalance comparison

| variant               |   precision |   recall |     f1 |
|:----------------------|------------:|---------:|-------:|
| baseline              |      0.7833 |   0.6912 | 0.7344 |
| class_weight_balanced |      0.7183 |   0.75   | 0.7338 |
| smote                 |      0.7353 |   0.7353 | 0.7353 |

The highest F1 in the three-way imbalance comparison is the `smote` variant (0.735). The comparison is deliberately reported rather than assumed: precision, recall, and F1 reflect different trade-offs when the positive class is not perfectly balanced.

## Random Forest hyperparameter tuning

Best parameters: `{'model__max_depth': 5, 'model__max_features': 'sqrt', 'model__n_estimators': 200}`
Best cross-validation F1: **0.7408**
Best estimator OOB score: **0.8214**
The Random Forest estimator was constructed with `oob_score=True`, so the fitted OOB score is available as required.

## Regression side-task

|     MAE |    RMSE |     R2 |   Adjusted_R2 |
|--------:|--------:|-------:|--------------:|
| 19.7531 | 41.2701 | 0.3471 |        0.3081 |

The residual variance changes materially across fitted-value ranges, so the residual plot shows evidence consistent with heteroscedasticity.

## Final classifier selection

The metric-based selection chooses **Random Forest** because it has the highest F1 in the held-out test comparison after using the specified common preprocessing contract. Its test accuracy is **0.809**, precision is **0.766**, recall is **0.721**, F1 is **0.742**, and AUC is **0.820**. These values summarize different performance dimensions, so the choice is based first on F1 and then on AUC/accuracy as transparent tie-breakers rather than treating all metrics as one scale. The complete fitted preprocessing + classifier pipeline has been saved so raw, unprocessed feature rows can be passed directly to the loaded artifact.

## Saved artifacts

- `classification_metrics.csv` and `classification_confusion_matrices.png` — full classifier evaluation.
- `classification_roc_curves.png` — ROC curves and AUC.
- `decision_tree.png` — labeled decision-tree visualization.
- `imbalance_comparison.csv` — baseline vs balanced weights vs SMOTE.
- `random_forest_grid_search.csv` — best parameters and OOB score.
- `regression_metrics.json` and `regression_residual_plot.png` — regression side-task.
- `artifacts/best_classifier_pipeline.joblib` — complete fitted classification pipeline.
- `artifacts/reload_check.txt` — artifact reload/prediction verification.
