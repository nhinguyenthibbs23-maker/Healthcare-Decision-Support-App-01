"""UI-flow and explanation tests for the user-facing pages.
Run: python -m unittest discover -s tests -v
"""

import json
import unittest
import sys
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PAGE = lambda name: str(ROOT / "pages" / name)

M = json.loads((ROOT / "models" / "model_meta.json").read_text())

HIGH = dict(Age=10, BMI=38, HighBP=1, HighChol=1, GenHlth=4)
LOW = dict(Age=2, BMI=22, HighBP=0, HighChol=0, GenHlth=1)


def page(name, state=None, lang="vi"):
    at = AppTest.from_file(PAGE(name), default_timeout=60)
    at.session_state["lang"] = lang
    for k, v in (state or {}).items():
        at.session_state[k] = v
    return at.run()


def texts(at):
    """Collect visible text from common Streamlit elements."""
    out = []
    for kind in ("markdown", "warning", "info", "success", "error",
                 "caption", "title", "subheader"):
        out.extend(str(e.value) for e in getattr(at, kind))
    return "\n".join(out)


def tap(at, label):
    """Click a button by its exact visible label."""
    matches = [b for b in at.button if b.label == label]
    if not matches:
        raise AssertionError(
            f"Button not found: {label!r}. "
            f"Available buttons: {[b.label for b in at.button]}"
        )
    matches[0].click().run()
    return at


class Explanation(unittest.TestCase):

    def test_contributions_add_up_to_estimate(self):
        from utils.explanation import shapley
        from utils.prediction import load_pipeline

        pipe = (
            load_pipeline.__wrapped__()
            if hasattr(load_pipeline, "__wrapped__")
            else __import__("joblib").load(ROOT / "models" / "pipeline.joblib")
        )

        examples = (HIGH, LOW, dict(Age=9, BMI=98, HighBP=1, HighChol=0, GenHlth=3))

        for answers in examples:
            phi, base, total = shapley(pipe, answers, M)
            probability = pipe.predict_proba(
                pd.DataFrame([answers], columns=M["features"])
            )[0, 1]
            self.assertAlmostEqual(sum(phi.values()), probability - base, places=6)
            self.assertAlmostEqual(total, probability, places=6)

    def test_extreme_bmi_prediction_is_valid(self):
        from utils.prediction import predict

        for bmi in (40, 60, 98):
            probability = predict({**HIGH, "BMI": bmi})
            self.assertTrue(
                0 <= probability <= 1,
                f"Invalid probability for BMI={bmi}: {probability}",
            )


def widget(at, kind, label):
    """Find a widget by its label (radios/selectboxes have no explicit key)."""
    return next(w for w in getattr(at, kind) if w.label == label)


def fill_form(at, adult="yes", age="8", bp="no", chol="no", health="2",
              height=160.0, weight=55.0):
    widget(at, "radio", "Adult").set_value(adult)
    widget(at, "selectbox", "Age").set_value(age)
    widget(at, "radio", "BP").set_value(bp)
    widget(at, "radio", "Chol").set_value(chol)
    widget(at, "radio", "GenHlth").set_value(health)
    at.number_input[0].set_value(height)
    at.number_input[1].set_value(weight)
    return at


def open_form():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    at.switch_page("pages/1_Risk_Assessment.py").run()
    assert not at.exception, at.exception
    return at


def submit(at):
    next(b for b in at.button if "gợi ý" in b.label).click().run()
    return at


class Pages(unittest.TestCase):

    def test_results_without_answers_asks_to_start(self):
        at = page("2_My_Results.py")
        self.assertFalse(at.exception, at.exception)
        self.assertTrue(len(at.button) >= 1)

    def test_results_flagged_and_not_flagged(self):
        from utils.prediction import predict

        # HIGH is above the default threshold -> recommend a test.
        flagged = page("2_My_Results.py", dict(answers=HIGH, probability=predict(HIGH)))
        self.assertFalse(flagged.exception, flagged.exception)
        self.assertIn("trao đổi với nhân viên y tế", texts(flagged))

        # LOW is below the default threshold -> no test recommended.
        low = page("2_My_Results.py", dict(answers=LOW, probability=predict(LOW)))
        self.assertFalse(low.exception, low.exception)
        self.assertIn("Chưa thấy dấu hiệu nổi bật", texts(low))

        # A threshold above 1 can never flag anyone, even HIGH.
        none_flagged = page(
            "2_My_Results.py",
            dict(answers=HIGH, probability=predict(HIGH), active_threshold=1.1),
        )
        self.assertFalse(none_flagged.exception, none_flagged.exception)
        self.assertIn("Chưa thấy dấu hiệu nổi bật", texts(none_flagged))

    def test_results_in_english(self):
        from utils.prediction import predict

        at = page("2_My_Results.py", dict(answers=HIGH, probability=predict(HIGH)), lang="en")
        self.assertFalse(at.exception, at.exception)
        body = texts(at)
        self.assertIn("Your Diabetes Risk Result", body)
        self.assertIn("discussing a blood sugar test", body)

    def test_results_custom_threshold_is_explained_and_resettable(self):
        from utils.prediction import predict

        at = page(
            "2_My_Results.py",
            dict(answers=HIGH, probability=predict(HIGH),
                 active_threshold=0.9, active_costs={"FP": 1, "FN": 5}),
        )
        self.assertFalse(at.exception, at.exception)
        self.assertIn("ngưỡng tùy chỉnh", texts(at))
        self.assertIn("Dùng lại cài đặt mặc định", [b.label for b in at.button])

        tap(at, "Dùng lại cài đặt mặc định")
        self.assertNotIn("active_threshold", at.session_state)
        self.assertNotIn("active_costs", at.session_state)

    def test_form_happy_path_saves_correct_answers(self):
        at = open_form()
        fill_form(at, age="9", bp="yes", chol="yes", health="4", height=160.0, weight=95.0)
        submit(at)
        self.assertFalse(at.exception, at.exception)
        a = at.session_state["answers"]
        self.assertEqual(
            {k: a[k] for k in ("Age", "HighBP", "HighChol", "GenHlth")},
            dict(Age=9, HighBP=1, HighChol=1, GenHlth=4),
        )
        self.assertAlmostEqual(a["BMI"], 95 / 1.6 ** 2, places=6)
        self.assertTrue(0 <= at.session_state["probability"] <= 1)

    def test_form_blocks_non_adult(self):
        at = open_form()
        fill_form(at, adult="no")
        submit(at)
        self.assertTrue(len(at.error) > 0, "Selecting No must show an error.")
        self.assertNotIn("probability", at.session_state)

    def test_form_unknown_answer_shows_warning_and_no_result(self):
        at = open_form()
        fill_form(at, bp="unknown")
        submit(at)
        self.assertTrue(len(at.warning) > 0, "Unknown must show a warning.")
        self.assertNotIn("probability", at.session_state)

    def test_form_empty_submit_does_not_crash(self):
        at = open_form()
        submit(at)
        self.assertFalse(at.exception, at.exception)
        self.assertNotIn("probability", at.session_state)

    def test_language_switch_and_sidebar_disclaimer(self):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
        self.assertFalse(at.exception, at.exception)
        at.radio(key="lang_label").set_value("English").run()
        self.assertFalse(at.exception, at.exception)
        self.assertEqual(at.session_state["lang"], "en")
        sidebar = " ".join(str(m.value) for m in at.sidebar.markdown)
        self.assertIn("Educational project — not for clinical use.", sidebar)

    def test_reviewer_page_loads(self):
        from utils.prediction import predict

        at = page("3_About_Model.py", dict(answers=HIGH, probability=predict(HIGH)))
        self.assertFalse(at.exception, at.exception)
        self.assertTrue(len(texts(at)) > 0)

        # Simulator inputs set to zero must not crash the page.
        for ni in at.number_input:
            ni.set_value(0.0)
        at.run()
        self.assertFalse(at.exception, at.exception)

    def test_home_is_short(self):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
        self.assertFalse(at.exception, at.exception)
        self.assertLessEqual(len(at.expander), 1)


if __name__ == "__main__":
    unittest.main()