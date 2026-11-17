import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import ROOT, meta, SPECS, AGES
from utils.ui import DISCLAIMER, html, simulator, GLUCOMETER_SVG

m = meta()
metrics = m["test_metrics"]
cm_raw = metrics["confusion_matrix"]
tn, fp = int(cm_raw[0][0]), int(cm_raw[0][1])
fn, tp = int(cm_raw[1][0]), int(cm_raw[1][1])

accuracy = (tn + tp) / max(metrics["n"], 1)
prec_0 = tn / (tn + fn) if (tn + fn) else 0.0
rec_0 = tn / (tn + fp) if (tn + fp) else 0.0
f1_0 = 2 * prec_0 * rec_0 / (prec_0 + rec_0) if (prec_0 + rec_0) else 0.0
prec_1 = float(metrics["precision"])
rec_1 = float(metrics["recall"])
f1_1 = float(metrics["f1"])


def svg(path, size=18, color="#1F5C46"):
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'style="display:block;flex:0 0 {size}px">{path}</svg>'
    )


IC_DB = svg('<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>', 20)
IC_CPU = svg('<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"/>', 20)
IC_GEAR = svg('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9c.26.6.77 1.02 1.4 1.1H21a2 2 0 0 1 0 4h-.09c-.63.08-1.14.5-1.51 1.1z"/>', 19)
IC_USER = svg('<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-6 8-6s8 2 8 6"/>', 19)
IC_CHART = svg('<path d="M3 3v18h18"/><rect x="7" y="10" width="3" height="7" rx="1"/><rect x="12" y="6" width="3" height="11" rx="1"/><rect x="17" y="13" width="3" height="4" rx="1"/>', 19)
IC_TARGET = svg('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>', 16)
IC_SCALE = svg('<path d="M12 3v18M5 7h14"/><path d="M5 7l-2.5 6a3 3 0 0 0 5 0L5 7zM19 7l-2.5 6a3 3 0 0 0 5 0L19 7z"/><path d="M8 21h8"/>', 16)
IC_REFRESH = svg('<path d="M21 12a9 9 0 0 0-15.5-6.3L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 15.5 6.3L21 16"/><path d="M21 21v-5h-5"/>', 16)
IC_TREND = svg('<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>', 16)
IC_BULB = svg('<path d="M9 18h6M10 22h4"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>', 19)
IC_INFO = svg('<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>', 17, "#1F3A5F")
IC_SHIELD = svg('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>', 18)
IC_ALERT = svg('<circle cx="12" cy="12" r="10"/><path d="M12 8v5M12 16h.01"/>', 18)
IC_STETH = svg('<path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6 6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6 6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/>', 18)

st.markdown("""
<style>
.st-key-about_hero{
    background:linear-gradient(120deg,#FFFFFF 0%,#EEF7F1 55%,#CDE6D6 100%);
    border:1px solid #DFEBE3;
    border-radius:24px;
    padding:1.8rem 2rem;
}
.st-key-about_works, .st-key-about_card{
    background:#FFFFFF;
    border:1px solid #DFEBE3;
    border-radius:20px;
    padding:1.4rem 1.6rem;
    box-shadow:0 4px 18px rgba(31,92,70,.04);
}
.st-key-about_limits{
    background:linear-gradient(120deg,#EEF7F1 0%,#F5FAF7 65%,#E1F0E6 100%);
    border:1px solid #DFEBE3;
    border-radius:20px;
    padding:1.3rem 1.6rem;
}
.pill-ai{
    display:inline-block;
    background:#84BA99;
    color:#FFFFFF;
    font-size:.72rem;
    font-weight:700;
    letter-spacing:.6px;
    padding:4px 12px;
    border-radius:999px;
    margin-bottom:.6rem;
}
.about-h1{font-size:2.4rem;font-weight:800;color:#14281F;letter-spacing:-1px;line-height:1.1;margin:0 0 .5rem}
.about-sub{font-size:1.08rem;font-weight:700;color:#14281F;margin-bottom:.45rem}
.about-p{font-size:.93rem;color:#4B6054;line-height:1.55;margin-bottom:1rem;max-width:34rem}

.mini-cards{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.mini-card{
    display:flex;gap:12px;align-items:center;
    background:rgba(255,255,255,.82);
    border:1px solid #D7E8DD;
    border-radius:14px;
    padding:12px 14px;
}
.mini-card .mic{
    width:40px;height:40px;border-radius:11px;background:#DDF0E4;
    display:flex;align-items:center;justify-content:center;flex:0 0 40px
}
.mini-card .mt{font-weight:700;font-size:.9rem;color:#14281F;line-height:1.2}
.mini-card .md{font-size:.79rem;color:#62756A;margin-top:2px;line-height:1.35}

.sec-hdr{display:flex;align-items:center;gap:10px;font-size:1.1rem;font-weight:800;color:#14281F;margin-bottom:.3rem}
.sec-sub{font-size:.86rem;color:#62756A;margin-bottom:1rem}

.flow-wrap{display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;gap:10px;align-items:start;margin-top:.7rem}
.flow-step{display:flex;gap:10px;align-items:flex-start}
.flow-num{
    width:24px;height:24px;border-radius:50%;background:#6FA987;color:#fff;
    font-size:.76rem;font-weight:700;display:flex;align-items:center;justify-content:center;flex:0 0 24px;margin-top:2px
}
.flow-ico{margin-bottom:6px}
.flow-tt{font-weight:700;font-size:.88rem;color:#14281F;margin-bottom:2px}
.flow-dd{font-size:.79rem;color:#62756A;line-height:1.4}
.flow-arr{color:#8DB59D;font-size:1.1rem;font-weight:700;padding-top:14px}

.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:1rem}
.kpi-box{background:#F7FBF8;border:1px solid #E3EFE7;border-radius:14px;padding:14px 12px;text-align:center}
.kpi-top{display:flex;align-items:center;justify-content:center;gap:6px;font-size:.84rem;color:#52685B;font-weight:600}
.kpi-val{font-size:1.7rem;font-weight:800;color:#14281F;margin-top:4px;line-height:1.1}

.crep{width:100%;border-collapse:collapse;font-size:.86rem;margin-top:.35rem}
.crep th{color:#52685B;font-weight:700;text-align:center;padding:10px 8px;border-bottom:1px solid #DCE7E0;background:#F7FBF8}
.crep th:first-child{text-align:left}
.crep td{padding:10px 8px;text-align:center;color:#14281F;border-bottom:1px solid #EFF5F1}
.crep td:first-child{text-align:left;font-weight:700}

.lim-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:16px;align-items:start}
.lim-item{display:flex;gap:10px;align-items:flex-start}
.lim-ic{width:34px;height:34px;border-radius:10px;background:#DDF0E4;display:flex;align-items:center;justify-content:center;flex:0 0 34px}
.lim-tt{font-weight:700;font-size:.88rem;color:#14281F;line-height:1.25}
.lim-dd{font-size:.8rem;color:#52685B;line-height:1.4;margin-top:3px}

button[data-baseweb="tab"]{font-size:.93rem;font-weight:600;padding:10px 14px}
button[data-baseweb="tab"][aria-selected="true"]{color:#1F5C46}

@media(max-width:900px){
    .mini-cards,.kpi-grid,.lim-grid{grid-template-columns:1fr 1fr}
    .flow-wrap{grid-template-columns:1fr}
    .flow-arr{display:none}
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 1. HERO BANNER: Behind GlucoGuide
# ==================================================
with st.container(key="about_hero"):
    h_left, h_right = st.columns([6.2, 4.2], vertical_alignment="center", gap="large")
    with h_left:
        html(f"""
        <div class="pill-ai">ABOUT OUR APP</div>
        <div class="about-h1">Behind GlucoGuide</div>
        <div class="about-sub">Understanding the technology behind your risk estimate.</div>
        <div class="about-p">
            GlucoGuide is an educational university prototype trained on {m['rows']:,} US 2015 survey records
            (BRFSS) to analyse 5 health indicators and estimate the likelihood of a positive survey label.
        </div>
        <div class="mini-cards">
            <div class="mini-card">
                <div class="mic">{IC_DB}</div>
                <div>
                    <div class="mt">Training Data</div>
                    <div class="md">US 2015 BRFSS survey ({m['rows']:,} records)</div>
                </div>
            </div>
            <div class="mini-card">
                <div class="mic">{IC_CPU}</div>
                <div>
                    <div class="mt">ML Algorithm</div>
                    <div class="md">{m['algorithm']} (5-feature model)</div>
                </div>
            </div>
        </div>
        """)
    with h_right:
        html(f'<div style="text-align:center">{GLUCOMETER_SVG}</div>')

st.write("")

# ==================================================
# 2. HOW GLUCOGUIDE WORKS (4 bước)
# ==================================================
with st.container(key="about_works"):
    html(f"""
    <div class="sec-hdr">{IC_GEAR}<span>How GlucoGuide works</span></div>
    <div class="flow-wrap">
        <div class="flow-step">
            <div class="flow-num">1</div>
            <div>
                <div class="flow-ico">{IC_USER}</div>
                <div class="flow-tt">User Information</div>
                <div class="flow-dd">You provide selected health characteristics through the form.</div>
            </div>
        </div>
        <div class="flow-arr">→</div>
        <div class="flow-step">
            <div class="flow-num">2</div>
            <div>
                <div class="flow-ico">{IC_DB}</div>
                <div class="flow-tt">Data Preprocessing</div>
                <div class="flow-dd">Height & weight convert to BMI; inputs are cleaned and encoded.</div>
            </div>
        </div>
        <div class="flow-arr">→</div>
        <div class="flow-step">
            <div class="flow-num">3</div>
            <div>
                <div class="flow-ico">{IC_CPU}</div>
                <div class="flow-tt">Machine Learning Prediction</div>
                <div class="flow-dd">The trained model analyses patterns and generates a score.</div>
            </div>
        </div>
        <div class="flow-arr">→</div>
        <div class="flow-step">
            <div class="flow-num">4</div>
            <div>
                <div class="flow-ico">{IC_CHART}</div>
                <div class="flow-tt">Risk Estimation</div>
                <div class="flow-dd">You receive an estimated score, testing suggestion, and explanation.</div>
            </div>
        </div>
    </div>
    """)

st.write("")

# ==================================================
# 3. CÁC MỤC CHỌN (TABS)
# ==================================================
tabs = st.tabs([
    "Performance & Factors",
    "Threshold & Costs",
    "Fairness",
    "Data & Decisions",
    "Full Model Card",
])


# ==================================================
# TAB 1 — PERFORMANCE & FACTORS
# ==================================================
with tabs[0]:
    with st.container(key="about_card"):
        html(f"""
        <div class="sec-hdr">{IC_CHART}<span>Model Performance</span></div>
        <div class="sec-sub">
            Evaluation on an untouched held-out test set of {metrics['n']:,} records.
            Fixed default threshold: <b>{m['threshold']:.4f}</b>.
            Simulator adjustments do not change these test results.
        </div>
        <div class="kpi-grid">
            <div class="kpi-box">
                <div class="kpi-top">{IC_TARGET}<span>Accuracy</span></div>
                <div class="kpi-val">{accuracy:.3f}</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-top">{IC_SCALE}<span>Precision</span></div>
                <div class="kpi-val">{prec_1:.3f}</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-top">{IC_REFRESH}<span>Recall</span></div>
                <div class="kpi-val">{rec_1:.3f}</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-top">{IC_TREND}<span>ROC-AUC</span></div>
                <div class="kpi-val">{metrics['roc_auc']:.3f}</div>
            </div>
        </div>
        """)

        c1, c2, c3 = st.columns(3)
        c1.metric("F1-score", f"{f1_1:.3f}")
        c2.metric("Average precision", f"{metrics['average_precision']:.3f}")
        c3.metric("Brier score (lower is better)", f"{metrics['brier']:.3f}")

        st.write("")

        col_l, col_r = st.columns(2, gap="large")

        with col_l:
            st.markdown("**ROC Curve**")
            roc = pd.read_csv(ROOT / "models/roc.csv")
            fig_roc = px.line(
                roc, x="FPR", y="Recall",
                labels={"FPR": "False positive rate", "Recall": "True positive rate"},
            )
            fig_roc.update_traces(line=dict(color="#1F5C46", width=2.5))
            fig_roc.add_shape(
                type="line", x0=0, y0=0, x1=1, y1=1,
                line=dict(color="#9AA59D", dash="dot", width=1.2),
            )
            fig_roc.update_xaxes(automargin=True, range=[0, 1])
            fig_roc.update_yaxes(automargin=True, range=[0, 1])
            fig_roc.update_layout(template="simple_white", height=320, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_roc, use_container_width=True)

        with col_r:
            st.markdown("**Test Confusion Matrix**")
            cm_df = pd.DataFrame(
                [[tn, fp], [fn, tp]],
                index=["Actual 0", "Actual 1"],
                columns=["Not flagged", "Flagged"],
            )
            fig_cm = px.imshow(
                cm_df,
                text_auto=True,
                color_continuous_scale=["#EEF6F0", "#C4E0CD", "#6BA583", "#1F5C46"],
                aspect="auto",
                labels={"x": "Predicted classification", "y": "Actual label", "color": "Records"},
            )
            fig_cm.update_xaxes(automargin=True)
            fig_cm.update_yaxes(automargin=True)
            fig_cm.update_layout(template="simple_white", height=320, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_cm, use_container_width=True)

        st.write("")

        col_b1, col_b2 = st.columns(2, gap="large")

        with col_b1:
            st.markdown("**Classification Report (Test Set)**")
            html(f"""
            <table class="crep">
                <thead>
                    <tr>
                        <th>Class</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>F1-Score</th>
                        <th>Support</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>No diabetes label (0)</td>
                        <td>{prec_0:.3f}</td>
                        <td>{rec_0:.3f}</td>
                        <td>{f1_0:.3f}</td>
                        <td>{tn + fp:,}</td>
                    </tr>
                    <tr>
                        <td>Diabetes / prediabetes (1)</td>
                        <td>{prec_1:.3f}</td>
                        <td>{rec_1:.3f}</td>
                        <td>{f1_1:.3f}</td>
                        <td>{fn + tp:,}</td>
                    </tr>
                </tbody>
            </table>
            """)
            st.write("")
            st.markdown("**Precision–Recall Curve**")
            pr = pd.read_csv(ROOT / "models/pr.csv")
            fig_pr = px.line(
                pr, x="Recall", y="Precision",
                labels={"Recall": "Recall", "Precision": "Precision"},
            )
            fig_pr.update_traces(line=dict(color="#1F5C46", width=2.5))
            fig_pr.update_xaxes(automargin=True)
            fig_pr.update_yaxes(automargin=True)
            fig_pr.update_layout(template="simple_white", height=250, margin=dict(l=20, r=20, t=15, b=20))
            st.plotly_chart(fig_pr, use_container_width=True)

        with col_b2:
            html(f"""
            <div class="sec-hdr">{IC_BULB}<span>What Factors Does the Model Consider?</span></div>
            <div class="sec-sub">Validation permutation importance (ROC-AUC drop when shuffled):</div>
            """)
            imp = pd.read_csv(ROOT / "reports/permutation_importance.csv")
            feat_col = next((c for c in imp.columns if c.lower() in ("feature", "predictor", "name")), imp.columns[0])
            val_col = next((c for c in imp.columns if pd.api.types.is_numeric_dtype(imp[c])), imp.columns[1])

            sub_imp = imp[imp[feat_col].isin(m["features"])].copy()
            if sub_imp.empty:
                sub_imp = imp.head(5).copy()

            name_map = {
                "Age": "Age",
                "BMI": "BMI",
                "HighBP": "High Blood Pressure",
                "HighChol": "High Cholesterol",
                "GenHlth": "General Health",
            }
            sub_imp["Factor"] = sub_imp[feat_col].map(lambda x: name_map.get(x, str(x)))
            sub_imp = sub_imp.sort_values(val_col, ascending=True)

            fig_imp = px.bar(
                sub_imp,
                x=val_col,
                y="Factor",
                orientation="h",
                text=sub_imp[val_col].map(lambda v: f"{v:.4f}"),
                labels={val_col: "ROC-AUC drop (Feature Importance)", "Factor": ""},
            )
            fig_imp.update_traces(marker_color="#2E7D5B", textposition="outside", cliponaxis=False)
            max_x = max(float(sub_imp[val_col].max()) * 1.32, 0.05)
            fig_imp.update_xaxes(automargin=True, range=[0, max_x])
            fig_imp.update_yaxes(automargin=True)
            fig_imp.update_layout(template="simple_white", height=290, margin=dict(l=10, r=45, t=10, b=20))
            st.plotly_chart(fig_imp, use_container_width=True)

            html(f"""
            <div class="callout" style="padding:12px 14px;font-size:.84rem">
                {IC_INFO}
                <span>Feature importance reflects overall influence on validation ROC-AUC and does not imply causation for an individual case.</span>
            </div>
            """)

        st.divider()
        st.markdown("**Validation model comparison**")
        comparison = pd.read_csv(ROOT / "reports/validation_comparison.csv")
        st.dataframe(comparison, hide_index=True, use_container_width=True)
        st.caption(
            "Candidate precision, recall, and F1 use a threshold of 0.50 for comparison. "
            "The final operating threshold is selected subsequently using validation costs."
        )


# ==================================================
# TAB 2 — THRESHOLD & COSTS
# ==================================================
with tabs[1]:
    st.subheader("Threshold and decision costs")
    st.write(
        "The classification threshold determines when a prediction is flagged. "
        "The cost simulator allows reviewers to examine how different false-positive "
        "and false-negative costs affect the decision."
    )
    simulator(m, "about")


# ==================================================
# TAB 3 — FAIRNESS
# ==================================================
with tabs[2]:
    st.subheader("Group-level performance audit")
    st.write("This section reports descriptive test-set differences across selected demographic and socioeconomic groups.")
    st.caption(
        "These results do not establish equal treatment or fairness. Differences may reflect sampling, "
        "prevalence, access to diagnosis, label bias, and model error."
    )

    fair = pd.read_csv(ROOT / "models/fairness.csv")
    group = st.selectbox("Audit dimension", ["Age", "Sex", "Income", "Education"])
    sub = fair[fair.feature == group].copy()

    def group_label(v):
        if group == "Age":
            return AGES[int(v) - 1]
        if group == "Sex":
            return {0: "Female (source code)", 1: "Male (source code)"}.get(int(v), str(v))
        return str(int(v))

    sub["Group label"] = sub.group.map(group_label)
    st.caption(SPECS[group][1])
    st.dataframe(sub, hide_index=True, use_container_width=True)

    fig_fair = px.bar(
        sub,
        x="Group label",
        y=["recall", "FPR"],
        barmode="group",
        range_y=[0, 1],
        title="Recall and false-positive rate by group",
        labels={"Group label": group, "value": "Rate", "variable": "Metric"},
        color_discrete_map={"recall": "#1F5C46", "FPR": "#E58A1F"},
    )
    fig_fair.update_xaxes(automargin=True)
    fig_fair.update_yaxes(automargin=True)
    fig_fair.update_layout(template="simple_white", height=400, legend_title_text="")
    st.plotly_chart(fig_fair, use_container_width=True)

    for measure in ["recall", "FPR"]:
        gap = sub[measure].max() - sub[measure].min()
        st.caption(f"Observed max–min {measure} gap: {gap:.3f}. Descriptive only; no confidence intervals or significance claims.")


# ==================================================
# TAB 4 — DATA & DECISIONS
# ==================================================
with tabs[3]:
    st.subheader("Data preparation and model decisions")
    st.markdown("**Data splitting**")
    st.write(m["split_method"])
    st.markdown("**Class imbalance**")
    st.write(m["imbalance"])
    st.markdown("**Model selection**")
    st.write(m["selection_rule"])
    st.markdown("**Explanation method**")
    st.write(m["explanation"]["method"])
    st.markdown("**Short vs. full model**")
    st.write(f"Best short vs full validation ROC-AUC gap: {m['short_auc_gap']:.4f}.")

    st.divider()
    st.markdown("**Duplicate and overlap audit**")
    st.write(f"Exact duplicate rows retained: {m['audit']['exact_duplicate_rows']:,}.")
    st.write(f"Conflicting full predictor profiles: {m['audit']['conflicting_predictor_profiles']:,}.")
    st.caption(
        "Identical profiles can belong to different people. Without respondent IDs, duplicate-looking records "
        "cannot automatically be treated as mistakes."
    )

    st.divider()
    st.markdown("**Feature dictionary**")
    feature_dict = pd.read_csv(ROOT / "reports/feature_dictionary.csv")
    st.dataframe(feature_dict, hide_index=True, use_container_width=True)

    st.divider()
    st.markdown("**Validation permutation importance**")
    importance = pd.read_csv(ROOT / "reports/permutation_importance.csv")
    st.dataframe(importance, hide_index=True, use_container_width=True)

    st.divider()
    st.markdown("**Dataset split details**")
    st.json(m["audit"]["splits"])


# ==================================================
# TAB 5 — FULL MODEL CARD
# ==================================================
with tabs[4]:
    st.subheader("GlucoGuide model card")
    st.caption("Structured documentation of the model's intended use, data, development, evaluation, risks, and deployment limitations.")

    st.markdown("### 1. Model details")
    c1, c2, c3 = st.columns(3)
    c1.metric("Algorithm", m["algorithm"])
    c2.metric("Input features", len(m["features"]))
    c3.metric("Training records", f"{m['rows']:,}")
    st.write(f"**Model selection identifier:** `{m['selected_candidate']}`")
    st.write("**Model type:** Supervised binary classification.")
    st.write("**Model output:** Estimated probability of the positive survey label (`Diabetes_binary = 1`), followed by a threshold-based flag.")

    st.divider()
    st.markdown("### 2. Intended use")
    st.write("Educational risk-awareness and decision-support prototype. An adult answering a short questionnaire at home can use the output as a prompt to consider seeking a blood glucose test or professional advice.")
    st.markdown("**Out-of-scope uses**")
    st.markdown(
        "- Diagnosing diabetes or prediabetes.\n"
        "- Predicting future disease onset or an individual's clinical probability.\n"
        "- Replacing laboratory testing, a clinician, or professional medical advice.\n"
        "- Making treatment, medication, insurance, employment, or eligibility decisions.\n"
        "- Clinical or population-wide deployment, including deployment in Vietnam, without independent validation."
    )

    st.divider()
    st.markdown("### 3. Target, labels, and outputs")
    st.write(f"**Target variable:** `{m['target']}`")
    st.write(f"**Class 0:** {m['target_meaning']['0']}.  \n**Class 1:** {m['target_meaning']['1']}.")
    st.warning("The target is a self-reported survey label. It is not a laboratory-confirmed diagnosis, and the model does not estimate future disease onset.")
    st.write(f"**Default classification threshold:** `{m['threshold']:.6f}` ({m['threshold']:.2%}).")

    st.divider()
    st.markdown("### 4. Training and evaluation data")
    st.write(f"Original dataset size: {m['rows']:,} records (BRFSS 2015).")
    st.write(f"Class 0 = {m['audit']['class_counts']['0']:,}; Class 1 = {m['audit']['class_counts']['1']:,} ({m['audit']['class_counts']['1'] / m['rows']:.2%}).")
    for source_name, source_url in m["sources"].items():
        st.markdown(f"- [{source_name}]({source_url})")
    split_df = pd.DataFrame([
        {"Partition": name.capitalize(), "Records": values["n"], "Positive-label rate": f"{values['positive_rate']:.2%}"}
        for name, values in m["audit"]["splits"].items()
    ])
    st.dataframe(split_df, hide_index=True, use_container_width=True)

    st.divider()
    st.markdown("### 5. Input features and requirements")
    range_rows = []
    for feature in m["features"]:
        bounds = m["valid_input_ranges"].get(feature)
        allowed = m["valid_values"].get(feature)
        range_rows.append({
            "Feature": feature,
            "Valid range": f"{bounds[0]:g}–{bounds[1]:g}" if bounds else "Not specified",
            "Allowed values": ", ".join(f"{x:g}" for x in allowed) if allowed is not None else "Continuous within valid range",
        })
    st.dataframe(pd.DataFrame(range_rows), hide_index=True, use_container_width=True)
    st.write(f"**BMI handling:** {m['bmi_handling']}.")

    st.divider()
    st.markdown("### 6. Model development and preprocessing")
    st.write(f"**Selected algorithm:** {m['algorithm']}.")
    st.write(f"**Selection rule:** {m['selection_rule']}")
    st.write(f"**Split method:** {m['split_method']}")
    st.write(f"**Class-imbalance strategy:** {m['imbalance']}")

    st.divider()
    st.markdown("### 7. Evaluation and performance")
    st.dataframe(pd.DataFrame([
        ("ROC-AUC", f"{metrics['roc_auc']:.6f}"),
        ("Average precision", f"{metrics['average_precision']:.6f}"),
        ("Brier score", f"{metrics['brier']:.6f}"),
        ("Precision", f"{metrics['precision']:.4%}"),
        ("Recall", f"{metrics['recall']:.4%}"),
        ("F1-score", f"{metrics['f1']:.6f}"),
    ], columns=["Metric", "Test result"]), hide_index=True, use_container_width=True)

    st.divider()
    st.markdown("### 8. Decision threshold and assumed costs")
    cost = m["cost_assumptions"]
    st.dataframe(pd.DataFrame([
        {"Error type": "False positive", "Relative cost": cost["FP"]},
        {"Error type": "False negative", "Relative cost": cost["FN"]},
    ]), hide_index=True, use_container_width=True)
    st.write(f"Cost units: {cost['units']}.")

    st.divider()
    st.markdown("### 9. Explainability")
    st.write(m["explanation"]["method"])

    st.divider()
    st.markdown("### 10. Fairness and subgroup evaluation")
    st.write("Descriptive test-set recall and false-positive rates across age, sex, income, and education groups. Does not establish absence of bias.")

    st.divider()
    st.markdown("### 11. Known limitations and risks")
    for item in [
        "Self-reported, cross-sectional labels can miss undiagnosed disease.",
        "US adults in 2015 may differ from people in Vietnam today; no Vietnamese or clinical validation is provided.",
        "Survey weights and respondent identifiers are absent.",
        "Unknown medical history is unsupported in the short questionnaire.",
        "Precision is limited at the selected threshold; a positive flag is not confirmation of disease.",
    ]:
        st.markdown(f"- {item}")

    st.divider()
    st.markdown("### 12. Deployment, monitoring, and governance")
    st.write("**Current status:** University prototype. Not a clinically validated or approved medical device.")

    st.divider()
    st.markdown("### 13. Reproducibility and provenance")
    versions = m["versions"]
    st.write(f"**Python:** `{versions['python']}` · **Scikit-learn:** `{versions['sklearn']}`")
    st.write(f"**Source-data SHA-256:** `{m['sha256']}`")

    st.divider()
    st.markdown("### 14. Review before any real-world use")
    st.markdown(
        "- Validate against independent, clinically confirmed outcomes.\n"
        "- Evaluate calibration and subgroup performance in the intended population.\n"
        "- Reassess threshold and error-cost assumptions with clinical stakeholders.\n"
        "- Document privacy, security, consent, and data-retention controls."
    )

st.write("")

# ==================================================
# 4. LIMITATIONS & RESPONSIBLE USE (BANNER ĐÁY NHƯ MOCKUP)
# ==================================================
with st.container(key="about_limits"):
    html(f"""
    <div class="lim-grid">
        <div class="lim-item">
            <div class="lim-ic">{IC_SHIELD}</div>
            <div>
                <div class="lim-tt">Limitations & Responsible Use</div>
                <div class="lim-dd">GlucoGuide is an educational diabetes risk prototype. Predictions are not a medical diagnosis.</div>
            </div>
        </div>
        <div class="lim-item">
            <div class="lim-ic">{IC_ALERT}</div>
            <div>
                <div class="lim-tt">Not a diagnostic tool</div>
                <div class="lim-dd">The model cannot confirm or rule out diabetes.</div>
            </div>
        </div>
        <div class="lim-item">
            <div class="lim-ic">{IC_DB}</div>
            <div>
                <div class="lim-tt">Data limitations</div>
                <div class="lim-dd">Self-reported US 2015 survey; not validated in Vietnam.</div>
            </div>
        </div>
        <div class="lim-item">
            <div class="lim-ic">{IC_STETH}</div>
            <div>
                <div class="lim-tt">Consult professionals</div>
                <div class="lim-dd">Always seek advice from healthcare professionals.</div>
            </div>
        </div>
    </div>
    """)

st.write("")
st.caption(DISCLAIMER)