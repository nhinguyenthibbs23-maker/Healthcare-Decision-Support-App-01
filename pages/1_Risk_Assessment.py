import streamlit as st

from utils.i18n import t, age_labels, health_labels
from utils.prediction import predict
from utils.ui import html, tr, page_header, stepper, field

S = st.session_state
F = S.setdefault("form", {})

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
.ph .ss {
    font-size: .96rem !important;
    color: #3D5246 !important;
    font-weight: 500;
}
.fl {
    font-size: .98rem !important;
}
.qnote {
    font-size: .92rem;
    color: #364B3F;
    font-weight: 500;
    line-height: 1.45;
    margin: .1rem 0 .55rem 0;
}
</style>
""", unsafe_allow_html=True)


def note(text):
    html(f'<div class="qnote">{text}</div>')


# --------------------------------------------------
# FORMAL SVG ICONS
# Forest green: #1F5C46
# --------------------------------------------------
IC_CLIPBOARD = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block"><rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 12h6M9 16h4"/></svg>'

IC_USER = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-6 8-6s8 2 8 6"/></svg>'

IC_CALENDAR = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'

IC_RULER = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block"><rect x="3" y="6" width="18" height="12" rx="2"/><path d="M7 6v4M11 6v3M15 6v4M19 6v3"/></svg>'

IC_BP = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block"><path d="M22 12h-4l-3 7-4-14-3 7H2"/></svg>'

IC_CHOL = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block"><path d="M12 2.7l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>'

IC_HEALTH = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:block"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v6M9 11h6"/></svg>'


# --------------------------------------------------
# OPTIONS AND LABEL MAPPING
# --------------------------------------------------
YES_NO_MAP = {
    "yes": t("yes"),
    "no": t("no")
}

UNKNOWN_MAP = {
    "yes": t("yes"),
    "no": t("no"),
    "unknown": t("unknown")
}

age_list = age_labels()
age_values = [str(i + 1) for i in range(len(age_list))]
age_map = {
    str(i + 1): lbl
    for i, lbl in enumerate(age_list)
}

health_list = health_labels()
health_values = [str(i + 1) for i in range(len(health_list))]
health_map = {
    str(i + 1): lbl
    for i, lbl in enumerate(health_list)
}


# --------------------------------------------------
# MIGRATE LEGACY ANSWERS
# --------------------------------------------------
def migrate_legacy_answers():

    if F.get("adult") in ("Có", "Yes"):
        F["adult"] = "yes"
    elif F.get("adult") in ("Không", "No"):
        F["adult"] = "no"

    for k in ("bp", "chol"):

        if F.get(k) in ("Có", "Yes"):
            F[k] = "yes"

        elif F.get(k) in ("Không", "No"):
            F[k] = "no"

        elif F.get(k) in ("Không rõ", "Unknown"):
            F[k] = "unknown"

    if F.get("age") in age_list:
        F["age"] = str(age_list.index(F["age"]) + 1)

    if F.get("health") in health_list:
        F["health"] = str(health_list.index(F["health"]) + 1)


migrate_legacy_answers()


def idx_of(options, val):
    return options.index(val) if val in options else None


unk_opts = ["yes", "no", "unknown"]


# ==================================================
# RISK ASSESSMENT FORM
# ==================================================
with st.container(key="assess_sheet"):

    page_header(
        IC_CLIPBOARD,
        tr("Đánh giá nguy cơ", "Risk Assessment"),
        tr(
            "Trả lời 6 câu hỏi ngắn để nhận gợi ý xét nghiệm đường huyết.",
            "Answer 6 short questions for blood sugar testing guidance."
        ),
    )

    st.write("")

    # --------------------------------------------------
    # ALL QUESTIONS INSIDE STREAMLIT FORM
    # --------------------------------------------------
    with st.form("assess_form", border=False):

        # ROW 1: Adult status | Age
        c1, c2 = st.columns(2, gap="medium")

        with c1:
            with st.container(key="qcard_1"):

                field(IC_USER, t("about_you"))

                note(tr(
                    "Từ 18 tuổi trở lên và chưa từng chẩn đoán tiểu đường.",
                    "18+ and never diagnosed with diabetes or prediabetes."
                ))

                adult = st.radio(
                    "Adult",
                    options=["yes", "no"],
                    index=idx_of(["yes", "no"], F.get("adult")),
                    format_func=lambda v: YES_NO_MAP[v],
                    horizontal=True,
                    label_visibility="collapsed",
                )

        with c2:
            with st.container(key="qcard_2"):

                field(IC_CALENDAR, t("age"))

                note(tr(
                    "Chọn khoảng tuổi hiện tại của bạn.",
                    "Select your current age range."
                ))

                age = st.selectbox(
                    "Age",
                    options=age_values,
                    index=idx_of(age_values, F.get("age")),
                    format_func=lambda v: age_map[v],
                    placeholder=t("age_ph"),
                    label_visibility="collapsed",
                )

        # --------------------------------------------------
        # ROW 2: Height and Weight
        # --------------------------------------------------
        with st.container(key="qcard_3"):

            field(
                IC_RULER,
                tr("Chiều cao và cân nặng", "Height and weight")
            )

            note(tr(
                "BMI sẽ được tính tự động và hiển thị ở trang kết quả.",
                "BMI is calculated automatically and shown on the results page."
            ))

            ch, cw = st.columns(2, gap="medium")

            with ch:
                height = st.number_input(
                    t("height"),
                    min_value=100.0,
                    max_value=230.0,
                    value=float(F.get("height", 160.0)),
                    step=0.5,
                )

            with cw:
                weight = st.number_input(
                    t("weight"),
                    min_value=20.0,
                    max_value=350.0,
                    value=float(F.get("weight", 55.0)),
                    step=0.5,
                )

        # --------------------------------------------------
        # ROW 3: High Blood Pressure | High Cholesterol
        # --------------------------------------------------
        c5, c6 = st.columns(2, gap="medium")

        with c5:
            with st.container(key="qcard_4"):

                field(
                    IC_BP,
                    tr(
                        "Đã từng được báo huyết áp cao?",
                        "Ever told you have high blood pressure?"
                    )
                )

                note(tr(
                    "Không tính lúc mang thai hoặc chỉ hơi cao.",
                    "Exclude pregnancy-only or borderline readings."
                ))

                bp = st.radio(
                    "BP",
                    options=unk_opts,
                    index=idx_of(unk_opts, F.get("bp")),
                    format_func=lambda v: UNKNOWN_MAP[v],
                    horizontal=True,
                    label_visibility="collapsed",
                )

        with c6:
            with st.container(key="qcard_5"):

                field(
                    IC_CHOL,
                    tr(
                        "Đã từng được báo mỡ máu cao?",
                        "Ever told you have high cholesterol?"
                    )
                )

                note(tr(
                    'Chọn "Tôi không biết" nếu chưa đo hoặc không chắc.',
                    "Choose 'I do not know' if unchecked or unsure."
                ))

                chol = st.radio(
                    "Chol",
                    options=unk_opts,
                    index=idx_of(unk_opts, F.get("chol")),
                    format_func=lambda v: UNKNOWN_MAP[v],
                    horizontal=True,
                    label_visibility="collapsed",
                )

        # --------------------------------------------------
        # ROW 4: General Health
        # --------------------------------------------------
        with st.container(key="qcard_6"):

            field(IC_HEALTH, t("health_q"))

            health = st.radio(
                "GenHlth",
                options=health_values,
                index=idx_of(health_values, F.get("health")),
                format_func=lambda v: health_map[v],
                horizontal=True,
                label_visibility="collapsed",
            )

        # --------------------------------------------------
        # SUBMIT BUTTON
        # --------------------------------------------------
        st.write("")

        _, b_right = st.columns([5.5, 2.4])

        with b_right:
            submitted = st.form_submit_button(
                t("submit") + "  →",
                type="primary",
                use_container_width=True,
            )

    # --------------------------------------------------
    # BACK BUTTON (OUTSIDE FORM)
    # --------------------------------------------------
    if st.button("←  " + tr("Quay lại", "Back")):

        if "_home_page" in S:
            st.switch_page(S["_home_page"])


# ==================================================
# PROCESS SUBMISSION
# ==================================================
if submitted:

    # Save answers to session state
    F.update(
        adult=adult,
        age=age,
        bp=bp,
        chol=chol,
        health=health,
        height=float(height),
        weight=float(weight),
    )

    # Calculate BMI
    bmi_val = (
        float(weight) /
        (float(height) / 100.0) ** 2
    )

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------
    if adult == "no":

        st.error(t("err_adult"))

    elif None in (adult, age, bp, chol, health):

        st.error(t("err_missing"))

    elif bp == "unknown" or chol == "unknown":

        st.warning(t("warn_unknown"))

    else:

        # Prepare model input
        answers = {
            "Age": int(age),
            "BMI": float(bmi_val),
            "HighBP": int(bp == "yes"),
            "HighChol": int(chol == "yes"),
            "GenHlth": int(health),
        }

        # --------------------------------------------------
        # PREDICTION
        # --------------------------------------------------
        try:

            with st.spinner(t("wz_calc")):
                p = predict(answers)

            S["answers"] = answers
            S["probability"] = p

            S.pop("active_threshold", None)
            S.pop("active_costs", None)

            st.switch_page("pages/2_My_Results.py")

        except ValueError:

            st.error(t("err_range"))
