# GlucoGuide: Diabetes Screening Decision-Support App

**Live app:** []
**Demo video:** []
**Team:** Nguyễn Bảo Ngọc, Nguyễn Thị Yến Nhi, Đỗ Nguyễn Minh Thư, Lê Hoàng Lâm

> Educational project, not for clinical use. GlucoGuide cannot diagnose diabetes.

## 1. Problem

**User-decision statement:** An adult answering questions at home uses the app to decide whether to get a blood sugar test for themselves.

The user answers 6 short questions. The app returns a recommendation ("talk to a health professional about a blood sugar test" or "no test suggested for now") together with the main factors behind the estimate. All 5 inputs are things the user already knows at that moment: age group, height and weight (turned into BMI), ever told they have high blood pressure, ever told they have high cholesterol, and self-rated general health.

## 2. Data

- **Source:** Diabetes Health Indicators, CDC BRFSS 2015 (Kaggle), the original imbalanced file, not the 50/50 one.
- **Size:** 253,680 survey responses, 21 columns. About 13.9% report diabetes or prediabetes.
- **Target:** `Diabetes_binary`. It is a **self-reported survey answer**, not a lab result.
- **Features used:** `Age`, `BMI`, `HighBP`, `HighChol`, `GenHlth`. The short set loses little accuracy compared with all 21 features (validation ROC-AUC 0.816 vs 0.823), and it keeps the questionnaire short.

## 3. Method and leakage checks

- **Split:** about 60/20/20 train/validation/test with `StratifiedGroupKFold`. Rows with identical 21-feature profiles always stay in the same partition, because the file has no respondent ID and duplicates could otherwise leak across splits.
- **Test set** is never used to choose features, model or threshold.
- **Pipeline:** preprocessing and model live in one scikit-learn `Pipeline` (`ColumnTransformer` + `HistGradientBoostingClassifier`), saved with `joblib`. The app does not repeat any preprocessing.
- **Baseline:** logistic regression on Age + BMI only (validation ROC-AUC 0.747). Logistic regression and random forest were also compared.
- **Excluded features:** possible consequences of the disease (stroke, heart disease), US-specific access proxies (health coverage, cost barrier, income), and items that added little accuracy or more questions (smoking, physical activity, heavy drinking, walking difficulty). Sex, education and income are kept for the fairness audit only. See `reports/feature_dictionary.csv`.

## 4. Threshold

The decision threshold is **0.159**, chosen on the validation set from illustrative costs:

| Error | Meaning | Relative cost |
|---|---|---|
| False positive | Someone is told to consider a test but does not have the survey label | 1 |
| False negative | Someone with the label gets no suggestion | 5 |

A glucose test is cheap and quick, while a missed case can be diagnosed years later, so we penalise a miss five times more. These are **relative units, not real money**. The app has a **cost simulator** (About page, tab "Threshold & Costs"): change both costs to see the new threshold, and use it for your own result.

## 5. Results (held-out test set, 51,063 responses, 7,065 positive)

| Metric | Value |
|---|---:|
| ROC-AUC | 0.819 (0.802 on a de-duplicated test set) |
| Average precision | 0.414 |
| Brier score | 0.098 |
| Recall at threshold 0.159 | 73.2% |
| Precision at threshold 0.159 | 31.6% |

Confusion matrix at the threshold: 32,797 true negatives, 11,201 false positives, 1,890 false negatives, 5,175 true positives.

In plain words: the model finds about 3 in 4 positive survey labels, but only about 1 in 3 people it flags has the label. That is acceptable for a "consider a test" nudge, but not for anything more serious. A fairness check by age, sex, income and education is on the About page.

## 6. Limitations

1. **Self-reported survey label**, not a clinical diagnosis.
2. **US 2015 data.** It has not been checked on Vietnamese or any other population.
3. **Training data includes people already diagnosed**, while the app is for people who say they have not been. The percentage shown is therefore a similarity to the survey group, not the chance that you have diabetes.
4. **Blood pressure, cholesterol and general health may partly be effects of diabetes**, not only risk factors. Explanations show associations, not causes.
5. **Costs are illustrative** and do not come from a real health system. Low precision means many false alarms.

## 7. Run it

Python 3.13.9 and scikit-learn 1.7.1 were used for training (see `requirements.txt`).

```bash
pip install -r requirements.txt
python -m streamlit run app.py       # run the app
python train.py                      # rebuild the model from data/ (about 3 minutes)
python tests/test_ui_flow.py -v      # run tests
```

```
app.py, pages/        Streamlit app (Home, Risk Assessment, Results, About)
utils/                prediction, threshold, Shapley explanation, UI helpers
models/               pipeline.joblib, model_meta.json, curves, fairness table
reports/              data audit, feature selection, validation comparison
train.py              rebuilds everything from the raw CSV
DECISION_LOG.md       what we chose, why, and what we rejected
AI_USE_APPENDIX.md    where we used AI and what we changed
```

Data: Kaggle "Diabetes Health Indicators" (BRFSS 2015). Check the license on the Kaggle page before reusing the file.