
"""Multilingual text helpers. Vietnamese remains the default language."""

import streamlit as st
from deep_translator import GoogleTranslator

# All languages currently exposed by Google Translate (100+ language options).
# This is the practical translation coverage, not every language spoken worldwide.
_supported = GoogleTranslator.get_supported_languages(as_dict=True)
LANGS = {name.title(): code for name, code in _supported.items()}
LANGS["Tiếng Việt"] = "vi"
LANGS["English"] = "en"
LANGUAGE_OPTIONS = ["Tiếng Việt", "English"] + sorted(
    [name for name in LANGS if name not in ("Tiếng Việt", "English")],
    key=str.casefold,
)

@st.cache_data(show_spinner=False, ttl=86400)
def translate_text(text, target):
    """Translate display text and cache it for one day; preserve source on API failure."""
    if not text or target in ("vi", "en"):
        return text
    try:
        return GoogleTranslator(source="auto", target=target).translate(str(text)) or str(text)
    except Exception:
        return str(text)

AGES_EN = [
    '18–24', '25–29', '30–34', '35–39', '40–44',
    '45–49', '50–54', '55–59', '60–64', '65–69',
    '70–74', '75–79', '80 or older'
]

AGES_VI = [
    '18–24', '25–29', '30–34', '35–39', '40–44',
    '45–49', '50–54', '55–59', '60–64', '65–69',
    '70–74', '75–79', 'Từ 80 tuổi'
]


def lang():
    return st.session_state.get("lang", "vi")


def pick_language():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "vi"

    default_label = next(
        (name for name, code in LANGS.items() if code == st.session_state["lang"]),
        "Tiếng Việt",
    )
    if "lang_label" not in st.session_state:
        st.session_state["lang_label"] = default_label

    st.sidebar.selectbox(
        "Ngôn ngữ / Language",
        options=LANGUAGE_OPTIONS,
        index=LANGUAGE_OPTIONS.index(st.session_state["lang_label"])
        if st.session_state["lang_label"] in LANGUAGE_OPTIONS else 0,
        key="lang_label",
    )
    st.session_state["lang"] = LANGS[st.session_state["lang_label"]]


def t(key, **kw):
    target = lang()
    source_language = target if target in ("vi", "en") else "vi"
    s = TEXT[key][source_language]
    if target not in ("vi", "en"):
        s = translate_text(s, target)
    return s.format(**kw) if kw else s


def age_labels():
    target = lang()
    if target == "vi":
        return AGES_VI
    if target == "en":
        return AGES_EN
    return [translate_text(label, target) for label in AGES_VI]


def health_labels():
    return [t('h1'), t('h2'), t('h3'), t('h4'), t('h5')]


def factor_name(f):
    return t('f_' + f)


TEXT = {
    # ---- common
    'disclaimer': {
        'vi': 'Ứng dụng học tập. Kết quả chỉ là ước tính từ một khảo sát, không phải chẩn đoán và không dự đoán bệnh trong tương lai. Hãy trao đổi với nhân viên y tế về việc xét nghiệm.',
        'en': 'Educational estimate from a survey model. It does not diagnose diabetes or predict future disease. Please discuss testing with a healthcare professional.'
    },
    'yes': {'vi': 'Có', 'en': 'Yes'},
    'no': {'vi': 'Không', 'en': 'No'},
    'unknown': {'vi': 'Tôi không biết', 'en': 'I do not know'},

    'h1': {'vi': 'Rất tốt', 'en': 'Excellent'},
    'h2': {'vi': 'Tốt', 'en': 'Very good'},
    'h3': {'vi': 'Bình thường', 'en': 'Good'},
    'h4': {'vi': 'Hơi yếu', 'en': 'Fair'},
    'h5': {'vi': 'Yếu', 'en': 'Poor'},

    'f_Age': {'vi': 'Độ tuổi', 'en': 'Age group'},
    'f_BMI': {'vi': 'Chỉ số BMI (cân nặng so với chiều cao)', 'en': 'BMI (weight for height)'},
    'f_HighBP': {'vi': 'Huyết áp cao', 'en': 'High blood pressure'},
    'f_HighChol': {'vi': 'Mỡ máu (cholesterol) cao', 'en': 'High cholesterol'},
    'f_GenHlth': {'vi': 'Tự đánh giá sức khỏe', 'en': 'Self-rated health'},

    'start': {'vi': 'Bắt đầu', 'en': 'Start'},

    # ---- home
    'home_kicker': {'vi': 'KIỂM TRA NHANH TẠI NHÀ', 'en': 'QUICK CHECK AT HOME'},
    'home_title': {'vi': 'Có nên đi xét nghiệm đường huyết không?', 'en': 'Should you get a blood sugar test?'},
    'home_intro': {
        'vi': 'Trả lời 5 câu hỏi ngắn về sức khỏe (khoảng 1 phút). GlucoGuide sẽ gợi ý bạn có nên cân nhắc xét nghiệm đường huyết hay không.',
        'en': 'Answer 5 short health questions (about 1 minute). GlucoGuide suggests whether you should consider a blood sugar test.'
    },
    'home_s1': {'vi': '**1 · Trả lời**  \n5 câu hỏi đơn giản', 'en': '**1 · Answer**  \n5 simple questions'},
    'home_s2': {'vi': '**2 · Xem gợi ý**  \nKết quả bằng lời dễ hiểu', 'en': '**2 · See the suggestion**  \nPlain-language result'},
    'home_s3': {'vi': '**3 · Bước tiếp theo**  \nNên làm gì sau đó', 'en': '**3 · Next step**  \nWhat to do afterwards'},
    'home_privacy': {
        'vi': 'Không cần tên hay email. Câu trả lời chỉ nằm trong phiên làm việc này và không được lưu lại.',
        'en': 'No name or email needed. Your answers stay in this session and are not saved.'
    },
    'home_diag': {
        'vi': 'Đã được chẩn đoán tiểu đường hoặc tiền tiểu đường? Ứng dụng này không dành cho bạn. Hãy tiếp tục theo kế hoạch của bác sĩ.',
        'en': 'Already diagnosed with diabetes or prediabetes? This app is not for you. Please continue your existing healthcare plan.'
    },

    # ---- assessment
    'assess_title': {'vi': 'Vài câu hỏi về bạn', 'en': 'A few questions about you'},
    'assess_intro': {
        'vi': 'Chỉ 5 câu, khoảng 1 phút. Hãy trả lời đúng với bạn, đừng đoán. Bạn cần biết chiều cao, cân nặng, và mình đã từng được báo bị huyết áp cao hay mỡ máu cao chưa.',
        'en': 'Just 5 questions, about a minute. Answer for yourself and do not guess. You need your height and weight, and to know whether you were ever told you have high blood pressure or high cholesterol.'
    },
    'assess_step': {'vi': 'Bước 1/2 · Trả lời câu hỏi', 'en': 'Step 1 of 2 · Answer the questions'},
    'about_you': {'vi': 'Về bạn', 'en': 'About you'},
    'adult_check': {
        'vi': 'Tôi từ 18 tuổi trở lên và chưa từng được chẩn đoán tiểu đường hoặc tiền tiểu đường.',
        'en': 'I am 18 or older and have not been diagnosed with diabetes or prediabetes.'
    },
    'age': {'vi': 'Bạn thuộc nhóm tuổi nào?', 'en': 'Which age group are you in?'},
    'age_ph': {'vi': 'Chọn nhóm tuổi', 'en': 'Choose your age group'},
    'height': {'vi': 'Chiều cao (cm)', 'en': 'Height (cm)'},
    'weight': {'vi': 'Cân nặng (kg)', 'en': 'Weight (kg)'},
    'bmi_note': {
        'vi': 'Ứng dụng tự tính chỉ số BMI từ chiều cao và cân nặng của bạn.',
        'en': 'The app works out your BMI from your height and weight.'
    },
    'known_health': {'vi': 'Sức khỏe bạn đã biết', 'en': 'Health you already know about'},
    'bp_q': {
        'vi': 'Bác sĩ hoặc nhân viên y tế đã bao giờ nói bạn bị huyết áp cao chưa?',
        'en': 'Has a doctor or health professional ever told you that you have high blood pressure?'
    },
    'bp_help': {
        'vi': 'Không tính huyết áp cao chỉ khi mang thai, hay lời nói "hơi cao" / "tiền tăng huyết áp".',
        'en': 'Do not count high blood pressure only during pregnancy, or "borderline" / prehypertension.'
    },
    'chol_q': {
        'vi': 'Bác sĩ hoặc nhân viên y tế đã bao giờ nói bạn bị mỡ máu (cholesterol) cao chưa?',
        'en': 'Has a doctor or health professional ever told you that you have high cholesterol?'
    },
    'chol_help': {
        'vi': 'Chỉ chọn "Có" nếu đã được báo như vậy. Nếu chưa từng đo hoặc không chắc, hãy chọn "Tôi không biết".',
        'en': 'Choose "Yes" only if you were told so. If you were never checked or are not sure, choose "I do not know".'
    },
    'health_q': {
        'vi': 'Nhìn chung, bạn thấy sức khỏe của mình như thế nào?',
        'en': 'In general, how would you rate your health?'
    },
    'health_ph': {'vi': 'Chọn một mức', 'en': 'Choose one'},
    'form_note': {
        'vi': 'Ứng dụng chỉ tính khi bạn bấm nút bên dưới. Bạn có thể sửa câu trả lời sau.',
        'en': 'The estimate is only calculated when you press the button. You can change your answers later.'
    },
    'submit': {'vi': 'Xem gợi ý của tôi', 'en': 'See my suggestion'},
    'err_adult': {
        'vi': 'Phần đánh giá này chỉ dành cho người từ 18 tuổi trở lên và chưa được chẩn đoán tiểu đường hoặc tiền tiểu đường.',
        'en': 'This check is only for adults who have not been diagnosed with diabetes or prediabetes.'
    },
    'err_missing': {
        'vi': 'Bạn chưa trả lời hết các câu hỏi. Vui lòng hoàn thành rồi bấm lại.',
        'en': 'Please answer every question and press the button again.'
    },
    'warn_unknown': {
        'vi': 'Chưa đủ thông tin: nếu bạn chưa biết mình có bị huyết áp cao hoặc mỡ máu cao hay không, ứng dụng không thể đưa ra ước tính đáng tin cậy và sẽ không đoán thay bạn. Bạn nên hỏi nhân viên y tế về việc đo huyết áp, mỡ máu và xét nghiệm định kỳ.',
        'en': 'Not enough information: if you do not know whether you have high blood pressure or high cholesterol, the app cannot give a reliable estimate and will not guess for you. Ask a health professional about checking blood pressure, cholesterol and routine testing.'
    },
    'err_range': {
        'vi': 'Chiều cao và cân nặng bạn nhập cho ra chỉ số BMI nằm ngoài phạm vi ứng dụng hỗ trợ. Vui lòng kiểm tra lại số đo.',
        'en': 'The height and weight you entered give a BMI outside the range this app supports. Please check your measurements.'
    },

    # ---- results
    'res_title': {'vi': 'Kết quả của bạn', 'en': 'Your result'},
    'res_empty': {
        'vi': 'Bạn chưa trả lời câu hỏi nào. Hãy làm phần đánh giá để xem kết quả.',
        'en': 'Please answer the questions first to see your result.'
    },
    'res_step': {'vi': 'Bước 2/2 · Xem gợi ý', 'en': 'Step 2 of 2 · Your suggestion'},
    'res_flag_title': {'vi': 'Nên cân nhắc xét nghiệm đường huyết', 'en': 'Consider getting a blood sugar test'},
    'res_flag_text': {
        'vi': 'Câu trả lời của bạn giống nhóm người cần chú ý hơn trong khảo sát. Đây chưa phải chẩn đoán, chỉ là gợi ý nên kiểm tra.',
        'en': 'Your answers look like those of people who needed more attention in the survey. This is not a diagnosis, only a suggestion to get checked.'
    },
    'res_ok_title': {'vi': 'Chưa thấy dấu hiệu nổi bật từ các câu trả lời', 'en': 'No strong warning sign from your answers'},
    'res_ok_text': {
        'vi': 'Điều này không có nghĩa là chắc chắn không bị bệnh. Bạn vẫn nên khám sức khỏe định kỳ, và đừng hoãn xét nghiệm nếu bác sĩ đã dặn.',
        'en': 'This does not mean you are certain to be free of the condition. Keep up routine check-ups, and do not delay a test your doctor has advised.'
    },
    'res_freq_h': {'vi': 'Ước tính cho những người trả lời giống bạn', 'en': 'What this means for people who answered like you'},
    'res_freq': {
        'vi': 'Trong 100 người trả lời giống bạn trong khảo sát, khoảng **{n}** người thuộc nhóm có nhãn "có bệnh" trong dữ liệu.',
        'en': 'Among 100 survey respondents who answered like you, about **{n}** were in the positive group in the survey data.'
    },
    'res_freq_low': {
        'vi': 'Trong 100 người trả lời giống bạn trong khảo sát, **dưới 1** người thuộc nhóm có nhãn "có bệnh" trong dữ liệu.',
        'en': 'Among 100 survey respondents who answered like you, **fewer than 1** was in the positive group in the survey data.'
    },
    'res_freq_note': {
        'vi': 'Mỗi chấm là 1 người. Con số dựa trên khảo sát ở Mỹ năm 2015 nên chỉ mang tính tham khảo, chưa kiểm chứng với người Việt Nam.',
        'en': 'Each dot is one person. Based on a 2015 US survey, so for guidance only and not validated for other populations.'
    },
    'res_why_h': {'vi': 'Điều gì ảnh hưởng đến kết quả của bạn?', 'en': 'What influenced your result?'},
    'res_why_note': {
        'vi': 'So với một người trung bình trong khảo sát (khoảng {base}%), mỗi yếu tố dưới đây làm ước tính của bạn tăng hoặc giảm bao nhiêu điểm phần trăm. Đây là mối liên hệ trong dữ liệu, không phải nguyên nhân.',
        'en': 'Compared with an average person in the survey (about {base}%), how many percentage points each factor adds to or takes from your estimate. These are associations in the data, not causes.'
    },
    'raises': {'vi': 'Làm tăng', 'en': 'Raises'},
    'lowers': {'vi': 'Làm giảm', 'en': 'Lowers'},
    'neutral': {'vi': 'Không đổi', 'en': 'No change'},
    'pts': {'vi': 'điểm %', 'en': 'pts'},
    'axis': {'vi': 'Thay đổi ước tính (điểm phần trăm)', 'en': 'Change in estimate (percentage points)'},
    'res_next_h': {'vi': 'Bước tiếp theo', 'en': 'What you can do next'},
    'res_next': {
        'vi': '- Hẹn gặp bác sĩ hoặc cơ sở y tế để hỏi về **xét nghiệm đường huyết** (đường huyết lúc đói hoặc HbA1c).\n- Mang theo kết quả này nếu bạn muốn, nhưng chỉ bác sĩ mới có thể chẩn đoán.\n- Nếu bạn khát nhiều, đi tiểu nhiều, mệt bất thường hoặc sụt cân không rõ lý do, hãy đi khám sớm, đừng chờ kết quả của ứng dụng.',
        'en': '- Book a visit with a doctor or clinic and ask about a **blood sugar test** (fasting glucose or HbA1c).\n- Bring this result if you like, but only a doctor can diagnose.\n- If you are very thirsty, urinate often, feel unusually tired or lose weight without reason, see a doctor soon instead of waiting for this app.'
    },
    'res_answers': {'vi': 'Xem lại câu trả lời của bạn', 'en': 'Review your answers'},
    'q_age': {'vi': 'Nhóm tuổi', 'en': 'Age group'},
    'q_bmi': {'vi': 'Chỉ số BMI', 'en': 'BMI'},
    'q_bp': {'vi': 'Từng được báo huyết áp cao', 'en': 'Told high blood pressure'},
    'q_chol': {'vi': 'Từng được báo mỡ máu cao', 'en': 'Told high cholesterol'},
    'q_health': {'vi': 'Tự đánh giá sức khỏe', 'en': 'Self-rated health'},
    'q_col': {'vi': 'Câu hỏi', 'en': 'Question'},
    'a_col': {'vi': 'Trả lời của bạn', 'en': 'Your answer'},
    'res_custom': {
        'vi': 'Bạn đang xem kết quả theo ngưỡng tùy chỉnh được đặt ở trang dành cho giảng viên.',
        'en': 'You are viewing this result with a custom threshold set on the reviewer page.'
    },
    'res_reset': {'vi': 'Dùng lại cài đặt mặc định', 'en': 'Back to default settings'},
    'res_edit': {'vi': 'Sửa câu trả lời', 'en': 'Change my answers'},
    'res_clear': {'vi': 'Xóa câu trả lời và làm lại', 'en': 'Clear my answers and start over'},
    'res_teacher': {'vi': 'Dành cho giảng viên: xem chi tiết mô hình', 'en': 'For reviewers: model details'},
}


# ---- wizard and friendly results
TEXT.update({
    'wz_q': {'vi': 'Câu {i}/{n}', 'en': 'Question {i} of {n}'},
    'wz_back': {'vi': '← Quay lại', 'en': '← Back'},
    'wz_next': {'vi': 'Tiếp tục →', 'en': 'Next →'},
    'wz_height_help': {'vi': 'Nhập số, ví dụ 165', 'en': 'Enter a number, e.g. 165'},
    'wz_weight_help': {'vi': 'Nhập số, ví dụ 58', 'en': 'Enter a number, e.g. 58'},
    'wz_need_number': {'vi': 'Vui lòng nhập một con số hợp lệ.', 'en': 'Please enter a valid number.'},
    'wz_height_range': {'vi': 'Chiều cao nên từ 100 đến 230 cm.', 'en': 'Height should be between 100 and 230 cm.'},
    'wz_weight_range': {'vi': 'Cân nặng nên từ 20 đến 350 kg.', 'en': 'Weight should be between 20 and 350 kg.'},
    'wz_restart': {'vi': 'Làm lại từ đầu', 'en': 'Start over'},
    'wz_calc': {'vi': 'Đang tính gợi ý cho bạn…', 'en': 'Working out your suggestion…'},

    'rs_head': {'vi': 'Gợi ý dành cho bạn', 'en': 'Your suggestion'},
    'rs_go_title': {'vi': 'Bạn nên đi khám', 'en': 'You should get checked'},
    'rs_go_text': {
        'vi': 'Hãy hẹn gặp bác sĩ để xét nghiệm đường huyết. Đây chưa phải là chẩn đoán, chỉ là lời khuyên nên kiểm tra sớm.',
        'en': 'Book a visit to have your blood sugar tested. This is not a diagnosis, just advice to get checked early.'
    },
    'rs_ok_title': {'vi': 'Chưa cần lo lắng lúc này', 'en': 'No need to worry right now'},
    'rs_ok_text': {
        'vi': 'Từ các câu trả lời của bạn, chưa thấy dấu hiệu nổi bật. Bạn vẫn nên khám sức khỏe định kỳ.',
        'en': 'Nothing stands out in your answers. Keep up regular health check-ups.'
    },

    'rs_pct': {'vi': '{n}%', 'en': '{n}%'},
    'rs_pct_low': {'vi': 'dưới 1%', 'en': 'under 1%'},

    'rs_pct_label': {
        'vi': 'Nguy cơ mắc bệnh theo dự đoán',
        'en': 'Predicted risk of diabetes'
    },
    'rs_pct_note': {
        'vi': 'Đây là kết quả dự đoán của mô hình, không phải xác suất mắc bệnh thực tế hay chẩn đoán y tế.',
        'en': 'This is a model prediction, not your actual probability of having diabetes or a medical diagnosis.'
    },

    'rs_pct_expl': {
        'vi': 'Nghĩa là: trong 100 người trả lời giống bạn, khoảng **{n}** người có nhãn "tiểu đường" trong dữ liệu khảo sát. Đây là ước tính nguy cơ, không phải kết luận bạn có bệnh.',
        'en': 'This means: out of 100 people who answered like you, about **{n}** have a "diabetes" label in the survey data. It is an estimated risk, not a conclusion that you have the disease.'
    },
    'rs_pct_expl_low': {
        'vi': 'Nghĩa là: trong 100 người trả lời giống bạn, dưới 1 người có nhãn "tiểu đường" trong dữ liệu khảo sát. Đây là ước tính nguy cơ, không phải kết luận.',
        'en': 'This means: out of 100 people who answered like you, fewer than 1 have a "diabetes" label in the survey data. It is an estimated risk, not a conclusion.'
    },

    'rs_bmi_h': {'vi': 'Chỉ số BMI của bạn', 'en': 'Your BMI'},
    'bmi_1': {'vi': 'Hơi gầy', 'en': 'Underweight'},
    'bmi_2': {'vi': 'Bình thường', 'en': 'Healthy weight'},
    'bmi_3': {'vi': 'Thừa cân', 'en': 'Overweight'},
    'bmi_4': {'vi': 'Béo phì', 'en': 'Obese'},
    'bmi_note2': {
        'vi': 'BMI = cân nặng (kg) chia bình phương chiều cao (m). Mốc phổ biến: dưới 18,5 gầy · 18,5–24,9 bình thường · 25–29,9 thừa cân · từ 30 béo phì. BMI chỉ là một chỉ số tham khảo.',
        'en': 'BMI = weight (kg) divided by height (m) squared. Common ranges: under 18.5 underweight · 18.5–24.9 healthy · 25–29.9 overweight · 30 or more obese. BMI is only a rough guide.'
    },

    'rs_why_h': {'vi': 'Vì sao ra kết quả này?', 'en': 'Why this result?'},
    'rs_why_sub': {
        'vi': 'Các yếu tố trong câu trả lời của bạn ảnh hưởng nhiều nhất:',
        'en': 'The answers that affected your result most:'
    },
    'rs_up': {'vi': 'làm nguy cơ cao hơn', 'en': 'raises your risk'},
    'rs_down': {'vi': 'làm nguy cơ thấp hơn', 'en': 'lowers your risk'},
    'rs_flat': {'vi': 'gần như không ảnh hưởng', 'en': 'hardly matters'},
    'rs_big': {'vi': 'nhiều', 'en': 'a lot'},
    'rs_mid': {'vi': 'vừa phải', 'en': 'moderately'},
    'rs_small': {'vi': 'ít', 'en': 'slightly'},
    'rs_why_note': {
        'vi': 'Đây là mối liên hệ trong dữ liệu khảo sát ở Mỹ năm 2015, không chứng minh nguyên nhân.',
        'en': 'These are patterns in a 2015 US survey, not proof of cause.'
    },

    'rs_next_h': {'vi': 'Bạn nên làm gì tiếp?', 'en': 'What should you do next?'},
    'rs_next_go': {
        'vi': '1. Hẹn bác sĩ hoặc cơ sở y tế để **xét nghiệm đường huyết** (đường huyết lúc đói hoặc HbA1c).\n2. Hỏi bác sĩ về huyết áp, mỡ máu và cân nặng của bạn.\n3. Nếu có khát nhiều, tiểu nhiều, mệt, sụt cân không rõ lý do, hãy đi khám sớm.',
        'en': '1. Book a visit for a **blood sugar test** (fasting glucose or HbA1c).\n2. Ask the doctor about your blood pressure, cholesterol and weight.\n3. If you are very thirsty, urinate a lot, feel tired or lose weight without reason, see a doctor soon.'
    },
    'rs_next_ok': {
        'vi': '1. Khám sức khỏe định kỳ, kể cả khi cảm thấy khỏe.\n2. Giữ cân nặng hợp lý, ăn uống cân bằng, vận động đều.\n3. Nếu có khát nhiều, tiểu nhiều, mệt, sụt cân không rõ lý do, hãy đi khám dù kết quả này thế nào.',
        'en': '1. Keep up regular check-ups, even when you feel well.\n2. Keep a healthy weight, eat balanced meals and stay active.\n3. If you are very thirsty, urinate a lot, feel tired or lose weight without reason, see a doctor regardless of this result.'
    },

    'rs_val_age': {'vi': 'Độ tuổi {v}', 'en': 'Age {v}'},
    'rs_val_bmi': {'vi': 'BMI {v}', 'en': 'BMI {v}'},
    'rs_val_bp': {'vi': 'Huyết áp cao: {v}', 'en': 'High blood pressure: {v}'},
    'rs_val_chol': {'vi': 'Mỡ máu cao: {v}', 'en': 'High cholesterol: {v}'},
    'rs_val_health': {'vi': 'Tự thấy sức khỏe: {v}', 'en': 'Own view of health: {v}'},
})
