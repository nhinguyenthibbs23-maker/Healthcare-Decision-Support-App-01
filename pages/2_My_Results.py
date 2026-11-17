
from pathlib import Path
import streamlit as st

from utils.data_loader import meta
from utils.prediction import load_pipeline
from utils.explanation import explain
from utils.i18n import t, factor_name
from utils.ui import html, tr, ring, DOCTOR_SVG

S = st.session_state


# --------------------------------------------------
# FORMAL SVG ICONS
# --------------------------------------------------
IC_BULB = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block;flex:0 0 18px"><path d="M9 18h6M10 22h4"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/></svg>'

IC_INFO = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1F3A5F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block;flex:0 0 18px;margin-top:2px"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>'


# ==================================================
# VALIDATE RESULT DATA
# ==================================================
if "probability" not in S or "answers" not in S:

    st.info(t("res_empty"))

    if st.button(t("start") + "  →", type="primary"):
        st.switch_page("pages/1_Risk_Assessment.py")

    st.stop()


# ==================================================
# LOAD RESULT INFORMATION
# ==================================================
m = meta()

p = float(S["probability"])
answers = S["answers"]

threshold = float(S.get("active_threshold", m["threshold"]))

flag = p >= threshold

pct_text = f"{p * 100:.1f}%" if p >= 0.01 else "<1%"


# ==================================================
# RISK CATEGORY
# ==================================================
if not flag:

    cat_title = tr("Nguy cơ thấp", "Low Risk")
    cat_color = "#2E8B57"
    ring_color = "#3B8D66"

    cat_desc = tr(
        f"Mô hình ước tính mức {pct_text} tương đồng với nhóm dương tính trong khảo sát.",
        f"Your model estimates a {pct_text} match with the positive diabetes survey group.",
    )

    tip_text = tr(
        "Chưa thấy dấu hiệu nổi bật! Hãy tiếp tục duy trì lối sống lành mạnh và khám định kỳ.",
        "Nothing stands out right now. Keep up healthy lifestyle choices and routine check-ups.",
    )

elif p < 0.35:

    cat_title = tr("Nguy cơ trung bình", "Moderate Risk")
    cat_color = "#E58A1F"
    ring_color = "#3B8D66"

    cat_desc = tr(
        f"Mô hình ước tính mức {pct_text} tương đồng với nhóm dương tính trong khảo sát.",
        f"Your model estimates a {pct_text} match with the positive diabetes survey group.",
    )

    tip_text = tr(
        "Đừng lo lắng! Với thói quen sống lành mạnh, bạn có thể giảm đáng kể nguy cơ của mình.",
        "With healthy lifestyle choices and timely screening, you can manage your risk effectively.",
    )

else:

    cat_title = tr("Nguy cơ cao hơn ngưỡng", "Elevated Risk")
    cat_color = "#C8452D"
    ring_color = "#E58A1F"

    cat_desc = tr(
        f"Mô hình ước tính mức {pct_text} tương đồng với nhóm dương tính trong khảo sát.",
        f"Your model estimates a {pct_text} match with the positive diabetes survey group.",
    )

    tip_text = tr(
        "Bạn nên trao đổi với nhân viên y tế để cân nhắc xét nghiệm đường huyết sớm.",
        "We recommend discussing a blood sugar test with a healthcare professional.",
    )


# ==================================================
# RESULT HEADER
# ==================================================
CHECK_BADGE = (
    '<div style="display:flex;align-items:center;gap:12px;margin-bottom:1.2rem">'
    '<svg viewBox="0 0 28 28" width="28" height="28" style="display:block;flex:0 0 28px">'
    '<circle cx="14" cy="14" r="13" fill="#2E8B57"/>'
    '<path d="M8.5 14.5l3.5 3.5 7.5-7.5" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
    f'<span style="font-size:1.45rem;font-weight:800;color:#14281F;letter-spacing:-.4px">'
    f'{tr("Kết quả nguy cơ tiểu đường của bạn", "Your Diabetes Risk Result")}'
    f'</span></div>'
)


# ==================================================
# MAIN RESULT SHEET
# ==================================================
with st.container(key="result_sheet"):

    html(CHECK_BADGE)

    # --------------------------------------------------
    # TOP SECTION
    # Left: Risk ring + category + tip
    # Right: Doctor illustration
    # --------------------------------------------------
    col_main, col_doc = st.columns(
        [2.25, 1.0],
        vertical_alignment="center",
        gap="medium"
    )

    with col_main:

        c_ring, c_cat = st.columns(
            [1.0, 1.25],
            vertical_alignment="center",
            gap="medium"
        )

        # Risk ring
        with c_ring:

            html(
                ring(
                    p,
                    pct_text,
                    ring_color,
                    tr("Nguy cơ ước tính", "Estimated Risk")
                )
            )

        # Risk category
        with c_cat:

            html(f"""
            <div class="cat">
                <div class="info-i">i</div>
                <div class="k">{tr("Phân loại nguy cơ", "Risk Category")}</div>
                <div class="v" style="color:{cat_color}">{cat_title}</div>
                <div class="d">{cat_desc}</div>
            </div>
            """)

        # Recommendation tip
        html(
            f'<div class="tipbar">{IC_BULB}<span>{tip_text}</span></div>'
        )

        # --------------------------------------------------
        # BMI INFORMATION
        # --------------------------------------------------
        bmi_val = float(answers["BMI"])

        bmi_cat = (
            t("bmi_1") if bmi_val < 18.5
            else t("bmi_2") if bmi_val < 25
            else t("bmi_3") if bmi_val < 30
            else t("bmi_4")
        )

        html(
            f'<div style="margin-top:.7rem;font-size:.95rem;color:#364B3F;font-weight:500">'
            f'{tr("Chỉ số BMI của bạn", "Your BMI")}: '
            f'<b>{bmi_val:.1f}</b> kg/m² · {bmi_cat}</div>'
        )

    # Doctor illustration
    with col_doc:

        html(
            f'<div style="text-align:center">{DOCTOR_SVG}</div>'
        )

    st.write("")

    # ==================================================
    # WHAT YOU CAN DO
    # ==================================================
    if flag:

        todos = [
            tr("Duy trì cân nặng hợp lý", "Maintain a healthy weight"),
            tr("Vận động đều đặn (≥ 150 phút/tuần)", "Exercise regularly (≥ 150 min/week)"),
            tr("Chọn chế độ ăn uống cân bằng", "Choose a balanced diet"),
            tr("Kiểm tra đường huyết & khám định kỳ", "Get regular health check-ups"),
        ]

    else:

        todos = [
            tr("Duy trì cân nặng hợp lý", "Maintain a healthy weight"),
            tr("Vận động đều đặn (≥ 150 phút/tuần)", "Exercise regularly (≥ 150 min/week)"),
            tr("Ăn uống cân bằng, hạn chế đường", "Choose a balanced diet"),
            tr("Khám sức khỏe định kỳ", "Get regular health check-ups"),
        ]

    b_left, b_right = st.columns(
        [1.45, 1.15],
        vertical_alignment="bottom",
        gap="large"
    )

    with b_left:

        html(
            f'<div class="sec">{tr("Bạn có thể làm gì:", "What You Can Do:")}</div>'
        )

        html(
            '<ul class="chk">'
            + "".join(f"<li>{x}</li>" for x in todos)
            + "</ul>"
        )

    # Assess again button
    with b_right:

        if st.button(
            tr("Làm lại", "Assess Again") + "  →",
            type="primary",
            use_container_width=True
        ):

            st.switch_page("pages/1_Risk_Assessment.py")


# ==================================================
# CUSTOM THRESHOLD NOTICE
# ==================================================
if "active_threshold" in S:

    st.write("")

    c_i, c_r = st.columns(
        [3, 1],
        vertical_alignment="center"
    )

    c_i.info(t("res_custom"))

    if c_r.button(t("res_reset"), use_container_width=True):

        S.pop("active_threshold", None)
        S.pop("active_costs", None)

        st.rerun()


# ==================================================
# TOP CONTRIBUTING FACTORS
# ==================================================
if answers:

    st.write("")

    with st.container(key="assess_sheet"):

        html(
            f'<div class="sec">'
            f'{tr("Các yếu tố đóng góp nhiều nhất", "Top Contributing Factors")}'
            f'</div>'
        )

        # --------------------------------------------------
        # CACHE EXPLANATION
        # --------------------------------------------------
        cache_key = tuple(sorted(answers.items()))

        if S.get("_why_key") != cache_key:

            S["_why"] = explain(
                load_pipeline(),
                answers,
                m
            )[0]

            S["_why_key"] = cache_key

        why = S["_why"].copy()

        # --------------------------------------------------
        # CALCULATE CONTRIBUTION SHARE
        # --------------------------------------------------
        why["Abs"] = why["Contribution"].abs()

        why["Share"] = (
            why["Abs"]
            / max(float(why["Abs"].sum()), 1e-9)
            * 100.0
        )

        why = why.sort_values(
            "Share",
            ascending=False
        )

        max_share = max(
            float(why["Share"].max()),
            1.0
        )

        greens = [
            "#1F5C46",
            "#3E7B61",
            "#6BA288",
            "#94BFA9",
            "#BDD9CA"
        ]

        # --------------------------------------------------
        # GENERATE CONTRIBUTION BARS
        # --------------------------------------------------
        rows = []

        for idx, (_, row) in enumerate(why.iterrows()):

            w = (
                float(row["Share"])
                / max_share
                * 100.0
            )

            c = greens[
                min(idx, len(greens) - 1)
            ]

            sign = (
                tr("tăng nguy cơ", "raises risk")
                if float(row["Contribution"]) >= 0
                else tr("giảm nguy cơ", "lowers risk")
            )

            rows.append(
                f'<div class="bar-row">'
                f'<div class="bar-name">{factor_name(row["Feature"])}</div>'
                f'<div class="bar-track">'
                f'<div class="bar-fill" style="width:{w:.1f}%;background:{c}"></div>'
                f'</div>'
                f'<div class="bar-val">{sign}</div>'
                f'</div>'
            )

        html("".join(rows))

        st.write("")

        # Disclaimer
        html(
            f'<div class="callout">'
            f'{IC_INFO}<span>{t("disclaimer")}</span>'
            f'</div>'
        )
