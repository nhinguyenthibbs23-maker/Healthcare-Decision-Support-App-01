
"""Offline rebuild. Test data never select features, model, or threshold."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_score,
    recall_score, f1_score, confusion_matrix, brier_score_loss,
    roc_curve, precision_recall_curve
)
from sklearn.inspection import permutation_importance

from utils.data_loader import (
    ROOT, TARGET, SPECS, SHORT, SOURCES, FINAL_ALGORITHM, load_data
)
from utils.threshold import threshold_table, choose_threshold


def evaluate(y, p, t):
    pred = p >= t
    return dict(
        roc_auc=float(roc_auc_score(y, p)),
        average_precision=float(average_precision_score(y, p)),
        brier=float(brier_score_loss(y, p)),
        precision=float(precision_score(y, pred, zero_division=0)),
        recall=float(recall_score(y, pred, zero_division=0)),
        f1=float(f1_score(y, pred, zero_division=0)),
        confusion_matrix=confusion_matrix(y, pred, labels=[0, 1]).tolist(),
        n=len(y),
        positive_count=int(sum(y))
    )


def build(features, algorithm):
    """All preprocessing lives in the pipeline. Original BMI values are retained."""
    other_numeric = [
        c for c in features if c in ['MentHlth', 'PhysHlth']
    ]
    category = [
        c for c in features if c not in other_numeric + ['BMI']
    ]
    parts = []

    if 'BMI' in features:
        parts.append((
            'bmi',
            Pipeline([
                ('impute', SimpleImputer(strategy='median')),
                ('scale', StandardScaler())
            ]),
            ['BMI']
        ))

    if other_numeric:
        parts.append((
            'numeric',
            Pipeline([
                ('impute', SimpleImputer(strategy='median')),
                ('scale', StandardScaler())
            ]),
            other_numeric
        ))

    if category:
        parts.append((
            'category',
            Pipeline([
                ('impute', SimpleImputer(strategy='most_frequent')),
                ('encode', OneHotEncoder(
                    handle_unknown='ignore',
                    sparse_output=False
                ))
            ]),
            category
        ))

    est = (
        LogisticRegression(max_iter=1000, C=1.)
        if algorithm == 'Logistic Regression'
        else HistGradientBoostingClassifier(
            max_depth=3,
            max_iter=300,
            learning_rate=0.05,
            random_state=0
        )
        if algorithm == 'Gradient Boosting'
        else RandomForestClassifier(
            n_estimators=140,
            max_depth=14,
            min_samples_leaf=30,
            max_features='sqrt',
            n_jobs=-1,
            random_state=42
        )
    )

    return Pipeline([
        ('preprocess', ColumnTransformer(parts)),
        ('model', est)
    ])


def feature_selection_report(X, y, train, val, features, reports):
    """Feature-selection evidence: fit on train, score on validation only."""
    Xtr, ytr = X.iloc[train], y.iloc[train]
    Xva, yva = X.iloc[val], y.iloc[val]

    def auc(cols):
        pipe = build(cols, 'Logistic Regression').fit(
            Xtr[cols], ytr
        )
        return float(
            roc_auc_score(
                yva,
                pipe.predict_proba(Xva[cols])[:, 1]
            )
        )

    full, short = auc(features), auc(SHORT)

    rows = [
        dict(
            feature=c,
            in_short=c in SHORT,
            drop_from_full_auc_loss=full - auc(
                [x for x in features if x != c]
            ),
            drop_from_short_auc_loss=(
                short - auc([x for x in SHORT if x != c])
                if c in SHORT else np.nan
            ),
            add_to_short_auc_gain=(
                auc(SHORT + [c]) - short
                if c not in SHORT else np.nan
            )
        )
        for c in features
    ]

    chosen, rest, path = [], list(features), []

    for k in range(1, 9):
        scores = {
            c: auc(chosen + [c])
            for c in rest
        }
        best = max(scores, key=scores.get)
        chosen.append(best)
        rest.remove(best)
        path.append(dict(
            step=k,
            feature=best,
            validation_auc=scores[best]
        ))

    table = pd.DataFrame(rows)
    table['forward_step'] = table.feature.map({
        p['feature']: p['step'] for p in path
    })

    table.sort_values(
        'drop_from_full_auc_loss',
        ascending=False
    ).to_csv(reports / 'feature_selection.csv', index=False)

    pd.DataFrame(path).to_csv(
        reports / 'forward_selection.csv',
        index=False
    )

    return dict(
        full_validation_auc=full,
        short_validation_auc=short,
        forward_top_k=chosen[:len(SHORT)],
        forward_top_k_equals_short=(
            set(chosen[:len(SHORT)]) == set(SHORT)
        )
    )


def main(path):
    out = ROOT / 'models'
    reports = ROOT / 'reports'
    out.mkdir(exist_ok=True)
    reports.mkdir(exist_ok=True)

    df = load_data(path)
    features = list(SPECS)
    X = df[features]
    y = df[TARGET].astype(int)

    groups = pd.util.hash_pandas_object(
        X, index=False
    ).values

    folds = list(
        StratifiedGroupKFold(
            n_splits=5,
            shuffle=True,
            random_state=42
        ).split(X, y, groups)
    )

    test = folds[0][1]
    val = folds[1][1]
    train = np.concatenate([f[1] for f in folds[2:]])

    assert not (
        set(groups[train]) & set(groups[val])
        or set(groups[train]) & set(groups[test])
        or set(groups[val]) & set(groups[test])
    )

    dup = df.duplicated()
    first = ~dup.values

    bins = pd.cut(
        df.BMI,
        [0, 18.5, 25, 30, 35, 40, 50, 60, np.inf]
    )

    audit = dict(
        rows=len(df),
        columns=list(df.columns),
        dtypes=df.dtypes.astype(str).to_dict(),
        missing=df.isna().sum().to_dict(),
        exact_duplicate_rows=int(dup.sum()),
        conflicting_predictor_profiles=int(
            df.groupby(features)[TARGET].nunique().gt(1).sum()
        ),
        class_counts=y.value_counts().to_dict(),
        ranges={
            c: [float(df[c].min()), float(df[c].max())]
            for c in df
        },
        splits={
            name: {
                'n': len(ids),
                'positive_rate': float(y.iloc[ids].mean())
            }
            for name, ids in [
                ('train', train),
                ('validation', val),
                ('test', test)
            ]
        },
        duplicates=dict(
            extra_copies_by_class={
                str(k): int(v)
                for k, v in df[dup][TARGET].astype(int).value_counts().items()
            },
            positive_rate_all_rows=float(y.mean()),
            positive_rate_after_dedup=float(
                df.drop_duplicates()[TARGET].mean()
            )
        ),
        bmi_positive_rate_by_bin={
            str(k): float(v)
            for k, v in y.groupby(bins, observed=True).mean().items()
        },
        bmi_cap=None,
        bmi_handling='Original BMI values retained; no upper cap'
    )

    (reports / 'data_audit.json').write_text(
        json.dumps(audit, indent=2)
    )

    pd.DataFrame([
        dict(
            feature=c,
            label=v[0],
            encoding=v[1],
            decision=v[2]
        )
        for c, v in SPECS.items()
    ]).to_csv(
        reports / 'feature_dictionary.csv',
        index=False
    )

    print(
        'Feature-selection evidence (validation only)',
        flush=True
    )

    fs = feature_selection_report(
        X, y, train, val, features, reports
    )

    if not fs['forward_top_k_equals_short']:
        print(
            'WARNING: forward-selection top-%d %s differs from SHORT %s; '
            'review utils/data_loader.py'
            % (len(SHORT), fs['forward_top_k'], SHORT),
            flush=True
        )

    candidates = []
    fitted = {}

    for name, cols in [
        ('full', features),
        ('short', SHORT)
    ]:
        for alg in [
            'Logistic Regression',
            'Random Forest',
            'Gradient Boosting'
        ]:
            key = name + ' | ' + alg
            print('Training ' + key, flush=True)

            pipe = build(cols, alg)
            pipe.fit(X.iloc[train][cols], y.iloc[train])

            p = pipe.predict_proba(
                X.iloc[val][cols]
            )[:, 1]

            candidates.append(dict(
                candidate=key,
                feature_set=name,
                algorithm=alg,
                n_features=len(cols),
                **evaluate(y.iloc[val], p, .5)
            ))

            fitted[key] = (pipe, cols, p)

    best_auc = max(c['roc_auc'] for c in candidates)

    eligible = [
        c for c in candidates
        if c['feature_set'] == 'short'
        and c['roc_auc'] >= best_auc - .010
    ]

    if not eligible:
        eligible = [
            c for c in candidates
            if c['feature_set'] == 'short'
        ]

    # Select FINAL_ALGORITHM among eligible short-feature candidates.
    chosen = [
        c for c in eligible
        if c['algorithm'] == FINAL_ALGORITHM
    ]

    selected = (
        chosen[0]
        if chosen
        else max(eligible, key=lambda c: c['roc_auc'])
    )

    pipeline, cols, pval = fitted[selected['candidate']]

    # Reference model: age + BMI only. It does not select the final model.
    reference = []

    for key, set_name, alg, ref_cols in [
        (
            'baseline: Age + BMI only | Logistic Regression',
            'baseline',
            'Logistic Regression',
            ['Age', 'BMI']
        )
    ]:
        print('Training ' + key, flush=True)

        ref_pipe = build(ref_cols, alg).fit(
            X.iloc[train][ref_cols],
            y.iloc[train]
        )

        reference.append(dict(
            candidate=key,
            feature_set=set_name,
            algorithm=alg,
            n_features=len(ref_cols),
            **evaluate(
                y.iloc[val],
                ref_pipe.predict_proba(
                    X.iloc[val][ref_cols]
                )[:, 1],
                .5
            )
        ))

    best, _ = choose_threshold(
        threshold_table(y.iloc[val], pval),
        1.,
        5.
    )

    threshold = float(best.threshold)

    ptest = pipeline.predict_proba(
        X.iloc[test][cols]
    )[:, 1]

    test_metrics = evaluate(
        y.iloc[test], ptest, threshold
    )

    # Report-only deduplicated sensitivity analysis.
    test_dedup = evaluate(
        y.iloc[test][first[test]],
        ptest[first[test]],
        threshold
    )

    val_dedup = evaluate(
        y.iloc[val][first[val]],
        pval[first[val]],
        threshold
    )

    joblib.dump(
        pipeline,
        out / 'pipeline.joblib',
        compress=3
    )

    np.savez_compressed(
        out / 'validation_predictions.npz',
        y=y.iloc[val].to_numpy(),
        p=pval
    )

    fairness = []

    for feature in ['Age', 'Sex', 'Income', 'Education']:
        for group, block in (
            df.iloc[test]
            .assign(_p=ptest)
            .groupby(feature)
        ):
            yy = block[TARGET].astype(int)
            pp = block._p.to_numpy()

            if yy.nunique() != 2:
                continue

            mm = evaluate(yy, pp, threshold)
            tn, fp = mm['confusion_matrix'][0]
            fn, tp = mm['confusion_matrix'][1]

            fairness.append(dict(
                feature=feature,
                group=int(group),
                n=len(block),
                positive_rate=float(yy.mean()),
                roc_auc=mm['roc_auc'],
                precision=mm['precision'],
                recall=mm['recall'],
                FPR=fp / (tn + fp) if tn + fp else None,
                FDR=fp / (tp + fp) if tp + fp else None,
                TP=tp,
                FP=fp,
                FN=fn,
                TN=tn
            ))

    pd.DataFrame(fairness).to_csv(
        out / 'fairness.csv',
        index=False
    )

    fpr, tpr, _ = roc_curve(y.iloc[test], ptest)
    prec, rec, _ = precision_recall_curve(
        y.iloc[test], ptest
    )

    ix = np.unique(
        np.linspace(
            0, len(fpr) - 1,
            min(1000, len(fpr))
        ).astype(int)
    )

    jx = np.unique(
        np.linspace(
            0, len(prec) - 1,
            min(1000, len(prec))
        ).astype(int)
    )

    pd.DataFrame({
        'FPR': fpr[ix],
        'Recall': tpr[ix]
    }).to_csv(out / 'roc.csv', index=False)

    pd.DataFrame({
        'Recall': rec[jx],
        'Precision': prec[jx]
    }).to_csv(out / 'pr.csv', index=False)

    imp = permutation_importance(
        pipeline,
        X.iloc[val][cols],
        y.iloc[val],
        scoring='roc_auc',
        n_repeats=3,
        max_samples=5000,
        random_state=42,
        n_jobs=1
    )

    pd.DataFrame({
        'feature': cols,
        'validation_AUC_drop': imp.importances_mean,
        'sd': imp.importances_std
    }).sort_values(
        'validation_AUC_drop',
        ascending=False
    ).to_csv(
        reports / 'permutation_importance.csv',
        index=False
    )

    pd.DataFrame(
        candidates + reference
    ).drop(
        columns='confusion_matrix'
    ).to_csv(
        reports / 'validation_comparison.csv',
        index=False
    )

    background = (
        X.iloc[train][cols]
        .sample(1000, random_state=42)
        .astype(float)
        .to_dict(orient='records')
    )

    m = dict(
        target=TARGET,
        target_meaning={
            '0': 'No self-reported diabetes/prediabetes',
            '1': 'Self-reported diabetes or prediabetes'
        },
        sources=SOURCES,
        rows=len(df),
        features=cols,
        feature_names=cols,
        valid_input_ranges={
            c: audit['ranges'][c] for c in cols
        },
        valid_values={
            c: sorted(df[c].unique().tolist())
            for c in cols if c != 'BMI'
        },
        algorithm=selected['algorithm'],
        selected_candidate=selected['candidate'],
        threshold=threshold,
        cost_assumptions={
            'FP': 1,
            'FN': 5,
            'units': 'illustrative relative units, not medical costs'
        },
        test_metrics=test_metrics,
        test_metrics_deduplicated=test_dedup,
        validation_metrics=evaluate(
            y.iloc[val], pval, threshold
        ),
        validation_metrics_deduplicated=val_dedup,
        validation_candidates=candidates,
        validation_reference_models=reference,
        explanation=dict(
            method=(
                'Exact Shapley values over the questions, on the '
                'probability scale, relative to the average of a '
                '1,000-row training background. Contributions add '
                'up to (your estimate - background average).'
            ),
            background=background
        ),
        feature_selection=fs,
        bmi_cap=None,
        bmi_handling='Original BMI values retained; no upper cap',
        selection_rule=(
            'Use the short questionnaire when its validation ROC-AUC '
            'is within 0.010 of the best full-feature candidate. '
            'Among eligible short-feature candidates, select the '
            'algorithm specified by FINAL_ALGORITHM in '
            'utils/data_loader.py; if it is not eligible, select '
            'the eligible candidate with the highest validation ROC-AUC. '
            'The test set is not used for feature, model, or threshold '
            'selection. Forward-selection results are reported separately.'
        ),
        short_auc_gap=(
            best_auc - max(
                c['roc_auc'] for c in candidates
                if c['feature_set'] == 'short'
            )
        ),
        audit=audit,
        versions={
            'python': platform.python_version(),
            'sklearn': sklearn.__version__
        },
        sha256=hashlib.sha256(
            Path(path).read_bytes()
        ).hexdigest(),
        reference={
            c: float(X.iloc[train][c].median())
            for c in cols
        },
        split_method=(
            'Approximately 60/20/20 stratified group folds; '
            'identical full 21-feature profiles stay in one split. '
            'Original rows retained; no respondent IDs available.'
        ),
        imbalance=(
            'No oversampling or class weights: retain original '
            'prevalence and probability scale. Asymmetric validation '
            'cost selects operating threshold. Report PR-AUC, Brier, '
            'recall and precision; accuracy is not selection criterion.'
        )
    )

    (out / 'model_meta.json').write_text(
        json.dumps(m, indent=2)
    )

    update_readme(m)

    print(
        json.dumps({
            'selected': selected['candidate'],
            'threshold': threshold,
            'test': test_metrics,
            'test_deduplicated': test_dedup,
            'feature_selection': fs
        }, indent=2),
        flush=True
    )


def update_readme(m):
    """Keep README numbers identical to the model just trained."""
    path = ROOT / 'README.md'
    start, end = '<!-- RESULTS:START -->', '<!-- RESULTS:END -->'

    if not path.exists():
        return

    s = path.read_text(encoding='utf-8')

    if start not in s or end not in s:
        return

    tm = m['test_metrics']
    (tn, fp), (fn, tp) = tm['confusion_matrix']
    a = m['audit']

    cc = {
        int(k): v
        for k, v in a['class_counts'].items()
    }

    cands = (
        m['validation_candidates']
        + m['validation_reference_models']
    )

    best_full = max(
        c['roc_auc']
        for c in m['validation_candidates']
        if c['feature_set'] == 'full'
    )

    cur = [
        c for c in cands
        if c['candidate'] == m['selected_candidate']
    ][0]

    lr = [
        c for c in cands
        if c['candidate'] == 'short | Logistic Regression'
    ][0]

    base = [
        c for c in cands
        if c['feature_set'] == 'baseline'
    ][0]

    rows = [
        ('Original records', f"{m['rows']:,}"),
        ('Predictors available', len(a['columns']) - 1),
        ('Class 0 / class 1', f"{cc[0]:,} / {cc[1]:,}"),
        ('Missing cells', sum(a['missing'].values())),
        ('Exact duplicate rows', f"{a['exact_duplicate_rows']:,}"),
        ('Selected input topics', len(m['features'])),
        ('Algorithm', m['algorithm']),
        ('BMI upper cap', 'None; original BMI values retained'),
        ('Validation-selected threshold', f"{m['threshold']:.10f}"),
        (
            'Default illustrative FP / FN penalties',
            f"{m['cost_assumptions']['FP']} / "
            f"{m['cost_assumptions']['FN']}"
        ),
        ('Test records', f"{tm['n']:,}"),
        ('Test ROC-AUC', f"{tm['roc_auc']:.6f}"),
        ('Test average precision', f"{tm['average_precision']:.6f}"),
        ('Test precision', f"{tm['precision']:.6f}"),
        ('Test recall', f"{tm['recall']:.6f}"),
        ('Test F1', f"{tm['f1']:.6f}"),
        ('Test Brier score', f"{tm['brier']:.6f}"),
        (
            'Test ROC-AUC on rows without duplicate copies (report only)',
            f"{m['test_metrics_deduplicated']['roc_auc']:.6f}"
        )
    ]

    out = [
        '| Item | Value |',
        '|---|---:|'
    ] + [
        f'| {k} | {v} |'
        for k, v in rows
    ]

    out += [
        '',
        (
            f"Test confusion matrix: TN {tn:,}; FP {fp:,}; "
            f"FN {fn:,}; TP {tp:,}. Among flagged test records, "
            f"approximately {fp / (fp + tp):.1%} have a negative "
            f"survey label (FDR); this is a real limitation, not "
            f"evidence the app establishes clinical disease status."
        ),
        '',
        (
            'Validation comparison (all rows are fitted on train '
            'and scored on validation; precision/recall in the CSV '
            'use a 0.50 cut-off only for comparison):'
        ),
        '',
        '| Candidate | Inputs | ROC-AUC | Average precision | Brier |',
        '|---|---:|---:|---:|---:|'
    ]

    out += [
        (
            f"| {c['candidate'].replace(' | ', ' / ')} "
            f"| {c['n_features']} "
            f"| {c['roc_auc']:.4f} "
            f"| {c['average_precision']:.4f} "
            f"| {c['brier']:.5f} |"
        )
        for c in cands
    ]

    out += [
        '',
        (
            f"The 5-question model ({m['algorithm']}) costs "
            f"{best_full - cur['roc_auc']:.4f} validation AUC "
            f"compared with the best full-feature model. It is "
            f"{cur['roc_auc'] - lr['roc_auc']:+.4f} AUC and "
            f"{cur['brier'] - lr['brier']:+.5f} Brier versus "
            f"the simple Logistic Regression on the same questions. "
            f"A deliberately simple baseline (age + BMI only) "
            f"reaches {base['roc_auc']:.4f}, so the other three "
            f"questions add about "
            f"{cur['roc_auc'] - base['roc_auc']:.3f}. "
            f"These are rounded values; JSON/CSV retain full precision. "
            f"This small predefined search is not exhaustive optimization."
        ),
        '',
        (
            f"This block is rewritten by `train.py`. Trained with "
            f"Python {m['versions']['python']} and scikit-learn "
            f"{m['versions']['sklearn']}; use the versions in "
            f"`requirements.txt` so the saved pipeline loads without warnings."
        )
    ]

    path.write_text(
        s[:s.index(start) + len(start)]
        + '\n'
        + '\n'.join(out)
        + '\n'
        + s[s.index(end):],
        encoding='utf-8'
    )


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument(
        '--data',
        type=Path,
        default=ROOT / 'data/diabetes_binary_health_indicators_BRFSS2015.csv'
    )
    main(p.parse_args().data)
