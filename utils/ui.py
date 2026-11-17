import streamlit as st
from utils.i18n import pick_language, t, lang as _lang, translate_text

DISCLAIMER = 'This educational model estimates a self-reported survey label. It does not diagnose diabetes or predict future disease. Discuss testing and routine screening with a healthcare professional.'


def tr(vi, en):
    target = _lang()
    if target == "vi":
        return vi
    if target == "en":
        return en
    return translate_text(vi, target)


def html(s):
    st.markdown('\n'.join(l.strip() for l in s.splitlines() if l.strip()), unsafe_allow_html=True)


def style():
    st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{--g:#1F5C46;--gd:#174836;--mint:#E6F2EA;--mint2:#F3F9F5;--ink:#14281F;--muted:#62756A;--line:#D5E7DC;--amber:#E58A1F;--red:#C8452D;--ok:#2E8B57}
.stApp,.stApp p,.stApp label,.stApp li,.stApp button,.stApp input,.stApp h1,.stApp h2,.stApp h3,.stApp h4{font-family:'Plus Jakarta Sans','Inter',sans-serif}

/* Nền toàn trang đúng tông xanh mint như ảnh */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"]{
    background:linear-gradient(135deg,#FFFFFF 0%,#EEF7F1 55%,#CDE6D6 100%)!important;
    background-attachment:fixed!important;
    color:var(--ink);
}
header[data-testid="stHeader"]{background:transparent!important}
.block-container{max-width:1040px;padding-top:1.5rem;padding-bottom:2.5rem}
h1,h2,h3{color:var(--ink)!important;letter-spacing:-.5px}
.stCaption,[data-testid="stCaptionContainer"]{color:var(--muted)}

/* Sidebar đồng bộ cùng tông & pill xanh ngọc */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div{
    background:linear-gradient(180deg,#FFFFFF 0%,#EEF7F1 68%,#CDE6D6 100%)!important;
    border-right:1px solid var(--line);
}
[data-testid="stSidebarNavLink"]{
    border-radius:12px!important;
    font-weight:500!important;
    color:#3A4F43!important;
    padding:.55rem .85rem!important;
    margin-bottom:3px;
}
[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebarNavLink"] svg{
    color:#526B5D!important;
}
[data-testid="stSidebarNavLink"][aria-current="page"]{
    background:#E3F2E8!important;
    color:#1A503C!important;
    font-weight:700!important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] span,
[data-testid="stSidebarNavLink"][aria-current="page"] svg{
    color:#1A503C!important;
}
.sb-note{
    display:flex;
    gap:9px;
    align-items:flex-start;
    background:rgba(255,255,255,.78);
    border:1px solid #DCEAE1;
    border-radius:14px;
    padding:12px 14px;
    color:#4A6254;
    font-size:.78rem;
    line-height:1.45;
    margin-top:.5rem;
}
section[data-testid="stSidebar"] [data-testid="stAlert"]{
    background:rgba(255,255,255,.78)!important;
    border:1px solid var(--line)!important;
    color:var(--muted)!important;
    font-size:.78rem;
    border-radius:14px;
}

/* Nút bấm */
div.stButton>button[kind="primary"]{background:var(--g);color:#fff;border:0;border-radius:12px;min-height:46px;font-weight:700;padding:0 1.4rem;transition:background .15s}
div.stButton>button[kind="primary"]:hover{background:var(--gd);color:#fff}
div.stButton>button[kind="secondary"]{background:#FFFFFF;border:1px solid var(--line);border-radius:12px;min-height:46px;color:var(--ink);font-weight:600;padding:0 1.2rem}
div.stButton>button[kind="secondary"]:hover{border-color:var(--g);color:var(--g);background:#F8FCF9}

/* Inputs & Radio gọn gàng như mockup */
div[data-baseweb="input"], div[data-baseweb="select"]>div{
    background:#FAFCFB!important;
    border:1px solid #DCE7E0!important;
    border-radius:10px!important;
    min-height:40px!important;
}
button[data-testid="stNumberInputStepDown"],
button[data-testid="stNumberInputStepUp"]{display:none!important}
div[data-testid="stRadio"] > div{gap:.9rem}
div[data-testid="stRadio"] label{font-size:.92rem;color:var(--ink)}
input[type="radio"]{accent-color:var(--g)!important}

/* Outer sheets & cards */
.st-key-hero{
    background:linear-gradient(120deg,#FFFFFF 0%,#EEF7F1 55%,#CDE6D6 100%)!important;
    border:1px solid var(--line);
    border-radius:28px;
    padding:2.2rem 2.4rem;
    box-shadow:0 8px 28px rgba(31,92,70,.05);
}
.st-key-assess_sheet{
    background:#FFFFFF;
    border:1px solid var(--line);
    border-radius:24px;
    padding:1.8rem 2rem;
    box-shadow:0 8px 28px rgba(31,92,70,.06);
}
.st-key-result_sheet{
    background:linear-gradient(120deg,#FFFFFF 0%,#EEF7F1 55%,#CDE6D6 100%)!important;
    border:1px solid var(--line);
    border-radius:24px;
    padding:1.8rem 2rem;
    box-shadow:0 8px 28px rgba(31,92,70,.06);
}
[class*="st-key-qcard_"]{
    background:#FFFFFF;
    border:1px solid #E6EFE9;
    border-radius:16px;
    padding:14px 16px 12px 16px;
    box-shadow:0 2px 8px rgba(31,92,70,.03);
    min-height:112px;
}
div[data-testid="stAlert"]{border-radius:14px}

/* Hero + features */
.brand-h1{font-size:3.3rem;font-weight:800;color:var(--ink);letter-spacing:-1.6px;line-height:1.05;margin:0}
.hero-sub{font-size:1.55rem;font-weight:800;line-height:1.25;color:var(--ink);margin:.9rem 0 .7rem}
.hero-p{color:var(--muted);font-size:1rem;line-height:1.65;max-width:30rem;margin-bottom:1.2rem}
.feat{text-align:center;padding:.6rem .4rem}
.feat .ic{width:46px;height:46px;border-radius:50%;background:#FFFFFF;border:1px solid var(--line);display:inline-flex;align-items:center;justify-content:center;font-size:1.3rem}
.feat .tt{font-weight:600;color:var(--ink);font-size:.92rem;margin-top:.55rem;line-height:1.35}

/* Page header + stepper */
.ph{display:flex;gap:14px;align-items:center}
.ph .ico{width:44px;height:44px;border-radius:12px;background:var(--mint);display:flex;align-items:center;justify-content:center;font-size:1.35rem;flex:0 0 44px}
.ph .tt{font-size:1.5rem;font-weight:800;color:var(--ink);letter-spacing:-.5px;line-height:1.15}
.ph .ss{font-size:.86rem;color:var(--muted);margin-top:2px}
.stp{display:flex;align-items:flex-start;justify-content:flex-end}
.stp .st{display:flex;flex-direction:column;align-items:center;gap:5px;font-size:.73rem;color:var(--muted);width:84px;text-align:center}
.stp .n{width:28px;height:28px;border-radius:50%;background:#E3ECE6;color:#7C8E83;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.82rem}
.stp .on .n,.stp .done .n{background:var(--g);color:#fff}
.stp .on{color:var(--ink);font-weight:600}
.stp .ln{flex:0 0 24px;height:2px;background:#DCE7E0;margin-top:13px}
.stp .ln.done{background:var(--g)}
.fl{font-weight:700;color:var(--ink);font-size:.9rem;display:flex;gap:7px;align-items:center;margin-bottom:.35rem}

/* BMI box giống ô có unit ở bên phải */
.bmi-row{display:flex;align-items:center;justify-content:space-between;background:#FAFCFB;border:1px solid #DCE7E0;border-radius:10px;overflow:hidden;min-height:40px}
.bmi-row .val{padding:6px 12px;font-size:1.05rem;font-weight:700;color:var(--ink)}
.bmi-row .badge{font-size:.78rem;font-weight:600;color:var(--g);background:var(--mint);padding:3px 9px;border-radius:999px;margin-right:8px}
.bmi-row .unit{background:#F1F6F3;border-left:1px solid #DCE7E0;padding:8px 12px;font-size:.82rem;font-weight:600;color:var(--muted)}

/* Results */
.ring-card{background:#FFFFFF;border-radius:50%;width:190px;height:190px;margin:0 auto;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 20px rgba(31,92,70,.07)}
.cat{background:#E8F4EC;border-radius:16px;padding:18px 20px;position:relative}
.cat .info-i{position:absolute;top:14px;right:16px;width:20px;height:20px;border-radius:50%;border:1px solid #9CB9A7;color:#5D7F6B;font-size:.72rem;font-weight:700;display:flex;align-items:center;justify-content:center}
.cat .k{font-size:.82rem;color:#334A3D;font-weight:700}
.cat .v{font-size:1.75rem;font-weight:800;margin:.25rem 0 .45rem;line-height:1.15}
.cat .d{font-size:.85rem;color:#3A5043;line-height:1.45}
.tipbar{display:flex;gap:12px;align-items:center;background:#F4F8F2;border:1px solid #DFECE3;border-radius:14px;padding:13px 16px;color:var(--ink);font-size:.9rem;line-height:1.45;margin-top:14px}
.chk{list-style:none;padding:0;margin:.5rem 0 0}
.chk li{display:flex;gap:10px;align-items:center;margin:.48rem 0;color:var(--ink);font-size:.92rem}
.chk li:before{content:"\\2714";color:#fff;background:var(--ok);border-radius:50%;width:18px;height:18px;display:inline-flex;align-items:center;justify-content:center;font-size:.6rem;flex:0 0 18px}
.sec{font-size:1.05rem;font-weight:800;color:var(--ink);margin:0 0 .25rem}

/* Understanding bars */
.bar-row{display:flex;align-items:center;gap:12px;margin:.7rem 0}
.bar-name{flex:0 0 165px;font-size:.9rem;color:var(--ink);font-weight:500}
.bar-track{flex:1;height:16px;background:#EEF4F0;border-radius:8px;overflow:hidden}
.bar-fill{height:100%;border-radius:8px}
.bar-val{flex:0 0 70px;text-align:right;font-weight:700;font-size:.88rem;color:var(--ink)}
.callout{display:flex;gap:10px;background:#EAF3FB;border-radius:14px;padding:14px 18px;color:#1F3A5F;font-size:.9rem;line-height:1.5}

@media(max-width:700px){.brand-h1{font-size:2.4rem}.stp .st{width:62px}.bar-name{flex-basis:110px}}
</style>''', unsafe_allow_html=True)


def page_header(icon, title, sub=''):
    sub_html = f'<div class="ss">{sub}</div>' if sub else ''
    html(f'<div class="ph"><div class="ico">{icon}</div><div><div class="tt">{title}</div>{sub_html}</div></div>')


def stepper(current, labels):
    parts = []
    for k, label in enumerate(labels):
        cls = 'done' if k < current else 'on' if k == current else ''
        mark = '✓' if k < current else k + 1
        parts.append(f'<div class="st {cls}"><div class="n">{mark}</div>{label}</div>')
        if k < len(labels) - 1:
            parts.append(f'<div class="ln {"done" if k < current else ""}"></div>')
    html('<div class="stp">' + ''.join(parts) + '</div>')


def field(icon, label):
    html(f'<div class="fl"><span>{icon}</span><span>{label}</span></div>')


def ring(frac, text, color, sub):
    r = 68
    c = 6.28318 * r
    d = c * max(0.05, min(1.0, frac))
    return (
        f'<div class="ring-card">'
        f'<svg viewBox="0 0 180 180" width="176" height="176">'
        f'<circle cx="90" cy="90" r="{r}" fill="none" stroke="#DCEFE3" stroke-width="14"/>'
        f'<circle cx="90" cy="90" r="{r}" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" '
        f'stroke-dasharray="{d:.1f} {c:.1f}" transform="rotate(-90 90 90)"/>'
        f'<text x="90" y="92" text-anchor="middle" font-size="30" font-weight="800" fill="#14281F" font-family="Plus Jakarta Sans,sans-serif">{text}</text>'
        f'<text x="90" y="114" text-anchor="middle" font-size="11.5" fill="#62756A" font-family="Plus Jakarta Sans,sans-serif">{sub}</text>'
        f'</svg></div>'
    )


GLUCOMETER_SVG = '''<svg viewBox="0 0 330 290" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:340px">
<path d="M210 78c-24-44-90-32-90 20 0 44 58 76 90 108 32-32 90-64 90-108 0-52-66-64-90-20z" fill="none" stroke="#fff" stroke-width="9" stroke-linejoin="round"/>
<ellipse cx="262" cy="196" rx="30" ry="14" fill="#7DBE8A" transform="rotate(-35 262 196)"/>
<ellipse cx="288" cy="214" rx="24" ry="11" fill="#5FA872" transform="rotate(20 288 214)"/>
<rect x="60" y="262" width="240" height="16" rx="8" fill="#D9B88F"/>
<g transform="rotate(-8 170 160)">
<rect x="116" y="70" width="122" height="190" rx="24" fill="#26365C"/>
<rect x="128" y="84" width="98" height="66" rx="10" fill="#E9F1F6"/>
<text x="188" y="132" text-anchor="middle" font-size="38" font-weight="800" fill="#1B2A40" font-family="Arial,sans-serif">98</text>
<circle cx="142" cy="102" r="5" fill="#D9473A"/>
<text x="188" y="145" text-anchor="middle" font-size="9" fill="#52627A" font-family="Arial,sans-serif">mg/dL</text>
<circle cx="177" cy="196" r="15" fill="#E8EEF5"/>
<circle cx="145" cy="196" r="8" fill="#5C6F94"/><circle cx="209" cy="196" r="8" fill="#5C6F94"/>
<rect x="157" y="258" width="40" height="40" rx="3" fill="#fff" stroke="#D5DEE6"/>
</g></svg>'''

DOCTOR_SVG = '''<svg viewBox="0 0 220 270" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:215px">
<circle cx="42" cy="52" r="4" fill="#F2B84B"/><path d="M56 32l3 8 8 3-8 3-3 8-3-8-8-3 8-3z" fill="#F2B84B"/>
<path d="M38 270v-88c0-30 28-46 72-46s72 16 72 46v88z" fill="#FFFFFF" stroke="#D4E4DA" stroke-width="2.5"/>
<path d="M84 138l26 48 26-48z" fill="#DDF0E4"/>
<path d="M96 138l14 34 14-34" fill="#63A882"/>
<rect x="97" y="114" width="26" height="28" rx="10" fill="#F5CFB0"/>
<path d="M62 110c-8-58 26-84 52-84 32 0 58 28 44 92-12-8-22-14-48-14s-36 6-48 6z" fill="#5C3A28"/>
<circle cx="110" cy="92" r="37" fill="#FBE0C8"/>
<path d="M72 86c6-34 30-46 48-44 18 2 30 16 28 42-12-16-24-22-38-22-14 0-26 8-38 24z" fill="#5C3A28"/>
<circle cx="94" cy="94" r="3.4" fill="#2F211B"/><circle cx="126" cy="94" r="3.4" fill="#2F211B"/>
<ellipse cx="85" cy="103" rx="6" ry="3.2" fill="#F3A69E" opacity=".55"/><ellipse cx="135" cy="103" rx="6" ry="3.2" fill="#F3A69E" opacity=".55"/>
<path d="M98 109q12 11 24 0" stroke="#B8564B" stroke-width="2.8" fill="none" stroke-linecap="round"/>
<path d="M82 140c-12 34-2 58 28 58s38-26 26-58" stroke="#31415A" stroke-width="5" fill="none" stroke-linecap="round"/>
<circle cx="110" cy="198" r="9" fill="#31415A"/><circle cx="110" cy="198" r="4" fill="#DCE6F2"/>
</svg>'''


def disclaimer():
    st.info(t('disclaimer'))


def simulator(m, key='sim'):
    import numpy as np
    import plotly.express as px
    from utils.data_loader import ROOT
    from utils.threshold import threshold_table, choose_threshold
    st.subheader('Explore the decision threshold')
    st.write('The threshold is the point where the app changes its testing suggestion. Lowering it usually catches more positive survey labels but also flags more negative ones. Your score stays the same.')
    st.caption('Illustrative relative penalty units only — these are not actual medical costs. Defaults: false alarm 1, missed positive label 5.')
    a, b = st.columns(2)
    cfp = a.number_input('Penalty for a false alarm (FP)', min_value=0., max_value=1000., value=1., step=1., key=key + 'fp')
    cfn = b.number_input('Penalty for a missed positive label (FN)', min_value=0., max_value=1000., value=5., step=1., key=key + 'fn')
    if cfp + cfn == 0:
        st.warning('Give at least one error a positive penalty.')
        return
    with np.load(ROOT / 'models/validation_predictions.npz') as saved:
        best, table = choose_threshold(threshold_table(saved['y'], saved['p']), cfp, cfn)
    label = 'No alerts' if best.threshold > 1 else f'{best.threshold:.1%}'
    a, b, c = st.columns(3)
    a.metric('Cost-selected threshold', label)
    b.metric('Validation penalty / person', f'{best.cost_per_person:.3f}')
    c.metric('Total validation penalty', f'{best.total_cost:,.0f}')
    st.caption('Expected penalty estimated as (FP × false-alarm penalty + FN × missed-label penalty) / validation sample size.')
    chosen = st.slider('Try a threshold yourself', 0., 1., min(float(best.threshold), 1.), .01, key=key + 'threshold')
    with np.load(ROOT / 'models/validation_predictions.npz') as saved:
        y, p = saved['y'], saved['p']
        pred = p >= chosen
        tp = int(((y == 1) & pred).sum())
        fp = int(((y == 0) & pred).sum())
        fn = int(((y == 1) & ~pred).sum())
        tn = int(((y == 0) & ~pred).sum())
    precision = tp / (tp + fp) if tp + fp else 0.
    recall = tp / (tp + fn)
    f1 = 2 * tp / (2 * tp + fp + fn)
    st.dataframe([dict(Threshold=chosen, FP=fp, FN=fn, Precision=precision, Recall=recall, F1=f1, FPR=fp / (fp + tn), FDR=fp / (tp + fp) if tp + fp else None, Penalty=cfp * fp + cfn * fn)], hide_index=True)
    plot = table[table.threshold <= 1].sort_values('threshold')
    plot = plot.iloc[::max(1, len(plot) // 600)]
    fig = px.line(plot, x='threshold', y=['recall', 'precision', 'FPR'], labels={'value': 'Rate', 'variable': 'Measure'}, color_discrete_sequence=['#1F5C46', '#2563eb', '#f59e0b'])
    fig.add_vline(x=chosen, line_dash='dot')
    st.plotly_chart(fig, use_container_width=True)
    fig = px.line(plot, x='threshold', y='cost_per_person', labels={'cost_per_person': 'Validation penalty per person'})
    fig.add_vline(x=min(float(best.threshold), 1.), line_dash='dot')
    st.plotly_chart(fig, use_container_width=True)
    if 'probability' in st.session_state:
        p = st.session_state.probability
        st.info(f'Your score stays {p:.1%}. At your trial threshold {chosen:.1%}: ' + ('the model flags your answers for a testing discussion.' if p >= chosen else 'the model does not flag your answers; this does not rule out diabetes.'))
    if st.button('Use cost-selected threshold for my results', key=key + 'apply'):
        st.session_state.active_threshold = float(best.threshold)
        st.session_state.active_costs = {'FP': cfp, 'FN': cfn}
        st.success('Saved for this session. Return to My Results to see the updated decision.')