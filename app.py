from pathlib import Path
import streamlit as st

from utils.i18n import t, pick_language
from utils.ui import style, html, tr, GLUCOMETER_SVG

st.set_page_config(
    page_title="GlucoGuide",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

if Path("assets/logo.svg").exists():
    st.logo("assets/logo.svg", size="large")

style()
pick_language()

# Khung disclaimer sidebar dạng thẻ mint đơn sắc (không dùng st.info màu xanh dương)
st.sidebar.markdown(
    f"""
    <div class="sb-note">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#4D6B59" stroke-width="2" style="flex:0 0 16px;margin-top:2px">
            <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
        </svg>
        <span>{tr("Không phải chẩn đoán y tế. Chỉ dùng cho mục đích học tập.",
                  "Not a medical diagnosis. For educational purposes only.")}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3 icon SVG nét mảnh giống hệt mockup Home
IC_SHIELD = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>'
IC_CHART = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><rect x="7" y="10" width="3" height="7" rx="1"/><rect x="12" y="6" width="3" height="11" rx="1"/><rect x="17" y="13" width="3" height="4" rx="1"/></svg>'
IC_HEART = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#1F5C46" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>'


def home():
    with st.container(key="hero"):
        left, right = st.columns([6, 5], vertical_alignment="center", gap="large")

        with left:
            html(f"""
            <div class="brand-h1">GlucoGuide</div>
            <div class="hero-sub">{tr("Hiểu rõ nguy cơ của bạn.<br>Chủ động bước tiếp theo.",
                                       "Understand your risk.<br>Take informed steps.")}</div>
            <div class="hero-p">{tr("Công cụ đơn giản giúp ước tính nguy cơ tiểu đường và gợi ý bạn có nên cân nhắc xét nghiệm đường huyết hay không.",
                                    "A smart, easy-to-use tool to estimate your diabetes risk and learn how to stay healthier.")}</div>
            """)
            if st.button(tr("Bắt đầu đánh giá", "Start Risk Assessment") + "  →", type="primary"):
                st.switch_page("pages/1_Risk_Assessment.py")

        with right:
            html(f'<div style="text-align:center">{GLUCOMETER_SVG}</div>')

    st.write("")
    feats = [
        (IC_SHIELD, tr("Nhanh &<br>dễ dàng", "Quick & Easy<br>Assessment")),
        (IC_CHART, tr("Hiểu rõ<br>nguy cơ", "Understand<br>Your Risk")),
        (IC_HEART, tr("Nhận gợi ý<br>sức khỏe", "Get Health<br>Recommendations")),
    ]
    for col, (icon, label) in zip(st.columns(3), feats):
        with col:
            html(f'<div class="feat"><div class="ic">{icon}</div><div class="tt">{label}</div></div>')

    st.write("")
    with st.container(border=True):
        st.markdown("**" + tr("Quyền riêng tư của bạn", "Your privacy matters") + "**")
        st.caption(t("home_privacy"))

    st.warning(t("home_diag"))


home_page = st.Page(home, title=tr("Trang chủ", "Home"), icon=":material/home:", default=True)
st.session_state["_home_page"] = home_page

pages = [
    home_page,
    st.Page("pages/1_Risk_Assessment.py", title=tr("Đánh giá nguy cơ", "Risk Assessment"), icon=":material/assignment:"),
    st.Page("pages/2_My_Results.py", title=tr("Kết quả", "Results"), icon=":material/assessment:"),
]
if Path("pages/4_Understanding.py").exists():
    pages.append(st.Page("pages/4_Understanding.py", title=tr("Hiểu kết quả", "Understanding"), icon=":material/lightbulb:"))
pages.append(st.Page("pages/3_About_Model.py", title=tr("Về mô hình (giảng viên)", "About"), icon=":material/info:"))

nav = st.navigation(pages)
nav.run()