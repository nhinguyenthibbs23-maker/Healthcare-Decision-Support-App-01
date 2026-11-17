# Decision Log – Diabetes Risk Screening Decision-Support App

## 1. Project purpose and intended use

The project develops GlucoGuide, a diabetes risk screening decision-support prototype using Python, Scikit-learn, and Streamlit.

### User-decision statement

**An adult using the app at home uses the screening result to decide whether to seek a blood glucose test for themselves.**

This statement identifies the intended user (an adult member of the public), moment (after completing the questionnaire at home), action (considering whether to seek a blood glucose testing), and person concerned (the user). The application provides preliminary decision support; it does not determine whether a test is medically necessary.

The application is designed to provide an educational estimate based on a short set of self-reported health characteristics. It is intended to support preliminary awareness and discussion, not to diagnose diabetes, replace laboratory testing, or provide individualised medical advice.

The target variable is `Diabetes_binary`, representing the dataset's self-reported diabetes-related outcome. The dataset's positive class combines respondents with self-reported diabetes or prediabetes. Class 0 is labelled 'No self-reported diabetes/prediabetes'; class 1 is labelled 'Self-reported diabetes or prediabetes'. This is a survey label, not a laboratory-confirmed diagnosis.

The project uses a US BRFSS-derived dataset. Therefore, model outputs should not be interpreted as calibrated estimates of diabetes prevalence or clinical risk in the Vietnamese population.

---

## 2. Dataset and data preparation decisions

### 2.1 Dataset selection

The project uses a prepared BRFSS-derived dataset containing:

- 253,680 observations.
- 22 columns: 21 predictor variables and one target variable.
- A binary target variable, `Diabetes_binary`.
- An observed positive-class share of approximately 13.9%.

The dataset was selected because it provides a relatively large sample and includes demographic, behavioural, and self-reported health characteristics relevant to diabetes risk screening.

**Limitation:** The dataset does not contain respondent identifiers or survey weights in the prepared file. Consequently, the project cannot establish patient-level independence across data partitions or use survey weights to produce population-representative estimates.

### 2.2 Handling duplicate observations

Duplicate records were investigated before deciding whether to remove them.

The exploratory audit identified approximately 24,206 exact duplicate rows. The duplicate records were not automatically removed.

The main reasons were:

1. Identical records do not necessarily represent the same respondent. Different individuals may report identical combinations of characteristics.
2. The dataset does not provide respondent identifiers that would allow the team to distinguish repeated respondents from different respondents with identical answers.
3. Removing all duplicates would alter the observed class distribution. The positive-class share would increase from approximately 13.9% to 15.3% in the earlier audit.
4. Removing duplicates could therefore change the composition of the dataset rather than simply eliminate repeated measurements from the same person.

The team also examined repeated feature profiles across data partitions. The training procedure uses grouped splitting based on identical full predictor profiles to reduce the risk of the same profile appearing in multiple partitions.

**Limitation:** Grouping identical profiles does not guarantee patient-level independence because respondent IDs are unavailable.

### 2.3 Handling missing values

The modelling pipeline retains imputation steps so that preprocessing is handled consistently within the training pipeline.

For numerical variables, median imputation is used where applicable. For categorical variables, the relevant preprocessing pipeline handles categorical values as specified in the training code.

Even if the current prepared dataset contains few or no missing values in the selected features, retaining the preprocessing steps makes the pipeline more robust to future inputs.

### 2.4 BMI handling: removal of the upper cap

An earlier modelling experiment considered upper-capping BMI values.

Historical grouped cross-validation results from that experiment were:

| BMI treatment | Historical validation ROC-AUC |
|---|---:|
| No upper cap | 0.8168 |
| Cap at 60 | 0.8180 |
| Cap at 50 | 0.8187 |
| Cap at 40 | 0.8198 |

The earlier experiment suggested a small improvement in validation ROC-AUC when BMI was capped at 40. However, the improvement was limited, and the cap would modify respondents' original reported BMI values.

The team therefore reconsidered whether the small performance difference justified changing the input data.

**Current decision:** Remove the BMI upper cap and retain the original observed BMI values. The prepared dataset's observed BMI range is approximately 12–98.

The reasons are:

- Preserve the original information reported in the dataset.
- Avoid treating high BMI observations as if they had the same value as the chosen cap.
- Avoid introducing an arbitrary transformation solely for a small historical validation improvement.
- Keep the application's input handling transparent.

The previous BMI-cap experiment is retained as historical evidence, but its metrics must not be presented as results from the current uncapped model.

---

## 3. Feature selection decisions

### 3.1 Short-questionnaire objective

The application is designed around a short questionnaire rather than requiring users to provide all 21 available predictors.

This is a deliberate usability decision. A shorter questionnaire reduces the amount of information users need to enter and makes the application more accessible for a preliminary screening discussion.

The selected five features are:

| Feature | Description | Reason for inclusion |
|---|---|---|
| Age | Respondent's age | Represents an important demographic characteristic associated with diabetes risk. |
| BMI | Body Mass Index | Represents body-weight status and is relevant to metabolic health. |
| HighBP | History of high blood pressure | Captures an important self-reported health condition. |
| HighChol | History of high cholesterol | Represents another relevant cardiovascular and metabolic health indicator. |
| GenHlth | General self-reported health status | Captures respondents' overall perception of their health. |

The five-feature set was selected to balance predictive usefulness, interpretability, and questionnaire simplicity.

### 3.2 Why not use all 21 predictors?

Although the dataset contains 21 predictors, including all of them would increase the number of questions required from users.

The team therefore prioritised a smaller feature set that could be collected through a practical user interface.

The remaining 16 predictors were not included in the final short questionnaire. This does not mean that they are clinically or statistically irrelevant. Rather, their exclusion reflects the project's intended use as a lightweight screening application.

The project should not claim that the five selected features are the only determinants of diabetes or that the excluded variables have no predictive value.

### 3.3 Historical feature-set comparison

Earlier experiments compared the five-feature questionnaire with a broader feature set.

The historical modelling work reported the following results for the five-feature Logistic Regression setup:

| Experiment | Historical validation ROC-AUC |
|---|---:|
| Age + BMI baseline | 0.7508 |
| Five-feature Logistic Regression | 0.8192 |

These results were reported in the earlier project notes and suggested improved discrimination after adding HighBP, HighChol, and GenHlth. They are historical figures, not values reproduced in the current `model_meta.json`; do not use them as the current validation comparison. The current feature/model selection evidence is the candidate table stored in the current metadata and described in Section 4.

---

## 4. Model development and selection

### 4.1 Models compared in the current training workflow

The current `train.py` workflow compares three algorithm families for both the full 21-feature set and the five-feature short set:

| Model family | Scikit-learn estimator | Role |
|---|---|---|
| Logistic Regression | `LogisticRegression(max_iter=1000, C=1.0)` | Simple benchmark model. |
| Random Forest | `RandomForestClassifier` with the settings defined in `train.py` | Non-linear tree-ensemble comparison. |
| Gradient Boosting | `HistGradientBoostingClassifier(max_depth=3, max_iter=300, learning_rate=0.05, random_state=0)` | Selected candidate family for the short questionnaire. |

The earlier Decision Log listed Decision Tree, KNN, Naive Bayes, and SVM as explored models. These are not part of the current reproducible candidate loop in `train.py` or the current `model_meta.json` validation-candidate record. They are therefore not described here as models tested in the current workflow. Any older experiments with those algorithms should only be reported separately if the team can provide their experiment records.

### 4.2 Current model- and feature-selection rule

The current selection rule is recorded in `models/model_meta.json`:

1. Identify the best validation ROC-AUC among the full-feature candidates.
2. Keep short-questionnaire candidates whose validation ROC-AUC is within 0.010 of that best full-feature score.
3. Among eligible short candidates, select the algorithm specified by `FINAL_ALGORITHM` in `utils/data_loader.py`; if it is not eligible, select the eligible short candidate with the highest validation ROC-AUC.
4. Do not use the test partition for feature selection, model selection, or threshold selection.

In the current metadata, the best full-feature validation ROC-AUC is 0.827472 (full Gradient Boosting), while the selected short Gradient Boosting candidate has validation ROC-AUC 0.819888. The gap is 0.007584, which is within the 0.010 eligibility margin. The selected candidate is `short | Gradient Boosting`.

### 4.3 Why Gradient Boosting was selected

**Current decision:** Gradient Boosting is the final selected algorithm for the five-feature questionnaire. In the implementation, the label `Gradient Boosting` maps to Scikit-learn's `HistGradientBoostingClassifier` with `max_depth=3`, `max_iter=300`, `learning_rate=0.05`, and `random_state=0`.

Logistic Regression remains a benchmark, and Random Forest is included in the current model comparison. The selected algorithm is not claimed to be universally superior; it is the algorithm chosen under the project's documented feature-simplicity and validation eligibility rule.

The earlier Decision Log reported historical Logistic Regression and HistGradientBoosting results (including ROC-AUC values around 0.819–0.821). Those figures are not used as current evidence because they do not match the current metadata's validation-candidate record and test evaluation. Keep them only in a clearly labelled historical experiment record if the original outputs are available.

### 4.4 Current final model artifact

The current metadata identifies:

- Selected candidate: `short | Gradient Boosting`.
- Selected features: `Age`, `BMI`, `HighBP`, `HighChol`, and `GenHlth`.
- Algorithm label: `Gradient Boosting` (implemented as `HistGradientBoostingClassifier`).
- Saved pipeline: `models/pipeline.joblib`.
- Model metadata: `models/model_meta.json`.

The metrics in Section 10 are taken from the current `models/model_meta.json` included in the supplied project archive. They describe the saved model artifact in that archive; if the team retrains the model later, regenerate and update this record from the new metadata.

---

## 5. Data splitting and model evaluation

### 5.1 Data partitioning

The project uses stratified grouped splitting to maintain class representation while reducing the possibility that identical full predictor profiles appear across training, validation, and test partitions.

The grouping approach is particularly relevant because the prepared dataset contains repeated feature profiles but does not provide respondent identifiers.

### 5.2 Avoiding preprocessing leakage

Preprocessing operations, including imputation, encoding, and scaling where applicable, are fitted within the training pipeline.

This prevents information from the validation or test partitions from being used to estimate preprocessing parameters.

The validation partition is used for model selection and threshold-related decisions.

The test partition is reserved for final evaluation after the modelling decisions have been made.

### 5.3 Evaluation metrics

The project considers multiple metrics because the dataset has an imbalanced target distribution.

| Metric | Purpose |
|---|---|
| ROC-AUC | Measures the model's ability to rank positive cases above negative cases across classification thresholds. |
| Average Precision (AP) | Summarises precision-recall performance, which is useful when the positive class is less common. |
| Precision | Measures the proportion of predicted positive cases that are actually positive in the dataset. |
| Recall | Measures the proportion of actual positive cases identified by the model. |
| F1-score | Summarises the balance between precision and recall. |
| Brier score | Evaluates the accuracy of predicted probabilities. |
| Confusion matrix | Shows true positives, true negatives, false positives, and false negatives at the selected threshold. |

No single metric is treated as sufficient to evaluate the model.

### 5.4 Class imbalance

The positive class accounts for approximately 13.9% of the prepared dataset.

The team retains the natural class distribution rather than automatically applying oversampling or class weighting.

This decision avoids changing the training distribution without a demonstrated need. The effects of class imbalance are instead considered through stratified splitting, multiple evaluation metrics, and threshold selection.

The observed class share is a characteristic of the prepared dataset, not a population prevalence estimate.

---

## 6. Classification threshold decision

A probability threshold is required to convert the model's predicted probability into a binary screening flag.

The default threshold is selected using the validation data rather than automatically using 0.50.

The current implementation uses the following illustrative relative-cost assumptions:

- False positive (FP): 1.
- False negative (FN): 5.

For each candidate threshold on the validation predictions, the training workflow calculates `total_cost = 1 × FP + 5 × FN` and selects the threshold with the lowest total cost. Ties are resolved by preferring fewer false negatives and then the higher threshold. The test partition is not used to select the threshold.

The current threshold recorded in `models/model_meta.json` is **0.15901535696129862** (approximately **15.90%**). These cost values are illustrative relative units, not estimates of actual medical, financial, or social costs. The threshold is an operating choice for this educational prototype, not a clinical decision boundary.

A positive screening flag means only that the model's estimated probability is at or above this operational threshold. It is not a diagnosis and does not establish an individual's clinical risk.

A positive screening flag does not indicate a diagnosis. It means that the model's estimate exceeds the selected operational threshold.

---

## 7. Model explanation decision

### 7.1 Why explanations are included

The application is intended to help users understand how their reported answers relate to the model's estimate.

Showing only a probability may make the output difficult to interpret. Therefore, the application provides a short explanation of the features that contribute most to an individual prediction.

### 7.2 Exact Shapley contributions

The project uses an exact Shapley-value implementation in `utils/explanation.py`.

The method evaluates all possible feature coalitions for the five selected features and calculates each feature's average marginal contribution to the model output.

The explanation is calculated on the probability scale.

The contributions satisfy:

`Sum of feature contributions = Individual prediction - Baseline prediction`

The baseline is the average model prediction over the 1,000-row training background sample stored in `models/model_meta.json`.

The application displays the most influential contributions, including whether each feature raises or lowers the model's estimate relative to the baseline.

### 7.3 Why this approach was selected

The selected approach:

- Works with the final Scikit-learn pipeline through `predict_proba`.
- Does not depend on Logistic Regression coefficients.
- Can therefore be retained when the final algorithm is Gradient Boosting.
- Provides a consistent additive explanation on the probability scale.
- Allows the application to display the features with the largest absolute contributions.

The current metadata contains a 1,000-row training background sample. If the model is retrained, regenerate this sample from that run and replace the stored explanation metadata at the same time.

### 7.4 Interpretation limitations

Shapley contributions describe how the model's prediction changes relative to the selected background sample.

They do not demonstrate that a feature causes diabetes or that changing an individual feature would produce the displayed change in real-world health risk.

The application therefore describes these values as model associations or contributions, not causal effects.

---

## 8. Application design and implementation decisions

### 8.1 Short questionnaire

The application collects five inputs:

- Age.
- BMI.
- High blood pressure.
- High cholesterol.
- General health status.

The questionnaire is designed to be short enough for a simple screening interaction.

### 8.2 BMI calculation

Where the user enters height and weight, the application calculates BMI using:

`BMI = Weight (kg) / Height (m)^2`

The resulting BMI is passed to the prediction pipeline without applying the previous upper cap.

The application should preserve valid original BMI values rather than silently replacing high values with a fixed maximum.

### 8.3 Prediction pipeline

The application loads the final trained pipeline rather than independently reimplementing preprocessing in the Streamlit interface.

This ensures that the same preprocessing operations used during training are applied during prediction.

The model pipeline and metadata are stored separately:

- The trained pipeline is stored as a model artifact, such as `models/pipeline.joblib`.
- Model configuration and explanation metadata are stored in `models/model_meta.json`.

The exact file names and paths should remain consistent across the training script, data loader, prediction utility, tests, and application.

### 8.4 User privacy

The application is designed to process questionnaire answers for the current interaction.

The project should not claim that user information is permanently stored, transmitted securely, or deleted automatically unless those behaviours are verified in the implementation and deployment environment.

---

## 9. Historical decisions versus current decisions

The table distinguishes historical notes in earlier drafts from the current implementation represented by the supplied project archive and its `models/model_meta.json`.

| Area | Historical note or earlier draft | Current recorded decision |
|---|---|---|
| User decision | General preliminary risk awareness. | An adult completing the questionnaire at home considers whether to seek a blood glucose test for themselves. |
| Feature set | Broader feature sets and a two-feature Age + BMI baseline were considered. | Five-feature questionnaire: Age, BMI, HighBP, HighChol, GenHlth. |
| Candidate algorithms | An earlier draft listed LR, Decision Tree, KNN, Naive Bayes, SVM, and Gradient Boosting. | Current `train.py` and metadata compare Logistic Regression, Random Forest, and Gradient Boosting. |
| Final algorithm | Logistic Regression was described as an earlier final model. | Gradient Boosting is selected; implemented with `HistGradientBoostingClassifier`. Logistic Regression remains a benchmark. |
| BMI handling | Upper caps of 40, 50, and 60 were tested in a historical experiment. | `bmi_cap` is `null`; original observed BMI values are retained without an upper cap. |
| Duplicate records | Exact duplicates were investigated. | Original rows are retained; identical full 21-feature profiles are grouped into one partition. |
| Data partitioning | Random splitting was considered a potential source of profile overlap. | Approximately 60/20/20 stratified grouped split; identical full predictor profiles stay in one split. |
| Threshold | Illustrative FP/FN cost ratio of 1:5. | Validation-selected threshold = 0.15901535696129862 using FP=1 and FN=5. |
| Explanation | Explanations were initially associated with the Logistic Regression setup. | Exact Shapley contributions on the probability scale using a 1,000-row training background. |
| Performance | Earlier LR and BMI-cap experiment metrics appeared in previous drafts. | Section 10 reports the current saved model's test metrics from `models/model_meta.json`; historical results are not mixed into that table. |

**Historical evidence note:** The BMI-cap validation values and older Logistic Regression comparison values reproduced in earlier versions of this Decision Log are not present as the current model's result fields. They are retained only as historical notes and should not be used to describe the current model. The current project archive does not include a complete reproducible record for every older experiment.

---

## 10. Current model performance record

The following results are copied from the current `models/model_meta.json` in the supplied project archive. They refer to the held-out test partition and the saved five-feature Gradient Boosting pipeline.

### 10.1 Model configuration

| Item | Current value |
|---|---|
| Selected candidate | `short | Gradient Boosting` |
| Algorithm | Gradient Boosting (`HistGradientBoostingClassifier`) |
| Features | Age, BMI, HighBP, HighChol, GenHlth |
| BMI upper cap | None; original BMI values retained |
| Decision threshold | 0.15901535696129862 (15.90%) |
| Illustrative FP cost | 1 |
| Illustrative FN cost | 5 |
| Python version recorded in metadata | 3.13.9 |
| Scikit-learn version recorded in metadata | 1.7.1 |

### 10.2 Held-out test metrics

| Metric | Test result |
|---|---:|
| ROC-AUC | 0.818562 |
| Average Precision (AP) | 0.413721 |
| Brier score | 0.097934 |
| Precision | 0.316011 (31.60%) |
| Recall | 0.732484 (73.25%) |
| F1-score | 0.441534 |
| Test observations | 51,063 |
| Positive observations | 7,065 |

The confusion matrix at the selected threshold is arranged with actual classes as rows and predicted classes as columns:

|  | Predicted negative | Predicted positive |
|---|---:|---:|
| Actual negative | TN = 32,797 | FP = 11,201 |
| Actual positive | FN = 1,890 | TP = 5,175 |

At this operating threshold, the model identifies 5,175 of the 7,065 positive survey labels in the test partition (recall 73.25%). It also produces 11,201 false-positive flags, which is reflected in the relatively low precision (31.60%). These are classification results against the dataset's self-reported survey label, not against a clinical diagnosis.

### 10.3 Interpretation

ROC-AUC and Average Precision describe ranking/discrimination performance, while the Brier score evaluates probability accuracy. Precision and recall describe the selected operating point. The results illustrate a sensitivity-oriented trade-off under the illustrative FN=5 and FP=1 cost assumptions; they do not establish clinical usefulness or suitability for Vietnamese users.

**Reproducibility note:** These values are current for the supplied archive's saved pipeline and metadata. If `train.py` is run again and generates new artifacts, update this section from the newly generated `models/model_meta.json`. Do not mix metrics from different training runs.

---

## 11. Limitations

The project has several limitations that affect how its outputs should be interpreted.

1. **Self-reported outcome:** The target variable is based on self-reported diabetes-related information and combines diabetes and prediabetes.
2. **Potential undiagnosed cases:** Respondents who have diabetes but have not received a diagnosis may be classified differently from their actual clinical status.
3. **Cross-sectional data:** The dataset does not establish temporal or causal relationships between predictors and diabetes.
4. **Geographical transferability:** The dataset is US-based. Its predictions have not been externally validated for Vietnamese users.
5. **No respondent identifiers:** The prepared data does not allow the team to verify individual-level independence across partitions. Grouping identical full predictor profiles reduces profile overlap but cannot prove that each respondent is independent.
6. **No survey weights:** The prepared file does not support survey-weighted population estimates. The observed 13.93% positive share is a property of this prepared dataset and should not be interpreted as a population prevalence estimate.
7. **Prediction errors:** False positives and false negatives remain possible, especially because the outcome is imbalanced.
8. **Limited questionnaire:** The five selected features do not capture every relevant demographic, behavioural, clinical, or socioeconomic factor.
9. **No external clinical validation:** The application has not been established as a clinically validated diagnostic or screening instrument.
10. **Model explanations are not causal:** Shapley contributions describe model behaviour, not biological mechanisms or treatment effects.

---

## 12. Outstanding tasks before final release

The supplied project archive already contains an uncapped-BMI training workflow, a saved pipeline, and a metadata file with the current threshold and test metrics. These items are therefore not listed as unfinished retraining tasks. The remaining work is primarily release verification and consistency checking.

### Confirmed in the supplied project archive

- [x] `train.py` builds the pipeline without applying an upper BMI cap (`bmi_cap=None`).
- [x] `models/model_meta.json` records `bmi_cap: null` and states that original BMI values are retained.
- [x] `models/pipeline.joblib` and the corresponding model metadata are present.
- [x] The metadata contains a validation-selected threshold, illustrative FP/FN costs, held-out test metrics, and the explanation background sample.
- [x] The current candidate record contains Logistic Regression, Random Forest, and Gradient Boosting comparisons.

### Still to verify or complete before release

- [ ] Run the complete test suite in the intended Python environment and record the actual result. Do not describe tests as passing until they have been run successfully.
- [ ] Verify the full user journey in Streamlit: questionnaire submission, result display, action recommendation, threshold/cost simulator, and explanation for an individual case.
- [ ] Confirm that the questionnaire uses `st.form` / `st.form_submit_button` as required by the assignment. The supplied archive's Risk Assessment page does not show an `st.form` implementation, so this remains an implementation check.
- [x] A shared disclaimer is rendered in the `app.py` entrypoint before `st.navigation(...).run()`, so it is intended to appear in the sidebar across the app's navigation pages. Verify this once in the deployed app as a final UI smoke test.
- [ ] Verify that valid BMI values across the documented range (12–98) reach the model without rounding or upper capping.
- [ ] Check dependency completeness. `pages/1_Risk_Assessment.py` imports Matplotlib, but `requirements.txt` in the supplied archive does not list `matplotlib`; add and pin it if that import remains in the final app.
- [ ] Remove notebook checkpoint folders and generated `__pycache__` / `.pyc` files from the repository, and update `.gitignore` to exclude them.
- [ ] Review whether any unused legacy transformer or BMI-cap references remain in tracked source files; distinguish harmless historical/checkpoint references from active prediction logic.
- [ ] Confirm that `README.md`, `DECISION_LOG.md`, `HUONG_DAN_NHOM.md`, `AI_USE_APPENDIX.md`, and the deployed app describe the same user decision, model, threshold, and limitations.
- [ ] Verify the deployed app and public GitHub repository after the final commit.
- [ ] Prepare and time the required demonstration video/presentation, and ensure the decision log and AI-use appendix are included in the submission.

---

## 13. Final decision summary

GlucoGuide is an educational diabetes risk screening decision-support prototype. Its intended user is an adult completing the questionnaire at home and considering whether to seek a blood glucose test for themselves. The application must not be presented as a diagnostic system or as a substitute for professional assessment or laboratory testing.

The current model uses five inputs: Age, BMI, HighBP, HighChol, and GenHlth. The selected algorithm is Gradient Boosting, implemented through Scikit-learn's `HistGradientBoostingClassifier`. Logistic Regression and Random Forest are retained as comparison candidates in the current training workflow. The feature-selection rule keeps the short questionnaire when its validation ROC-AUC is within 0.010 of the best full-feature candidate; the selected short Gradient Boosting candidate meets this rule with a validation AUC gap of 0.007584.

The original BMI values are retained without an upper cap. Duplicate rows are not automatically deleted because respondent identifiers are unavailable; identical full predictor profiles are grouped into the same data partition to reduce profile overlap. The model is evaluated using a stratified grouped train/validation/test split, and preprocessing is fitted within the Scikit-learn pipeline.

The current saved model uses a validation-selected threshold of 0.15901535696129862 based on illustrative relative costs of FP=1 and FN=5. On the held-out test set, it achieves ROC-AUC 0.818562, Average Precision 0.413721, Brier score 0.097934, precision 31.60%, recall 73.25%, and F1-score 0.441534. These metrics measure agreement with the dataset's self-reported survey label; they do not establish clinical validity or performance in Vietnam.

Exact Shapley contributions are used to explain individual model estimates relative to a 1,000-row training background sample. These contributions explain model behaviour and must not be interpreted as causal effects.

Before release, the team must complete the remaining UI, testing, dependency, repository-cleanup, documentation-synchronisation, and deployment checks listed in Section 12. The current model metrics should be updated only if a new training run replaces the saved model artifacts.
