"""STORY-04: optional risk level in the explanation request (AC-04.1 to AC-04.5)."""
import unittest

from ap_forecast import build_explanation_request
from ap_forecast.explain import load_config

CFG = {"provider": "p", "model": "m", "max_tokens": 10}
BASE = "Explain in one sentence why vendor Synthetic Vendor A is predicted to be paid 12 days late."


class ExplanationRiskTest(unittest.TestCase):
    def test_risk_appended_to_prompt(self):  # AC-04.1
        for level in ("high", "medium", "low"):
            req = build_explanation_request("Synthetic Vendor A", 12, CFG, risk=level)
            content = req["messages"][0]["content"]
            self.assertEqual(content, BASE + f" Risk level: {level}.")
            self.assertTrue(content.endswith(f" Risk level: {level}."))

    def test_risk_positional_fourth_argument(self):  # AC-04.1: risk is the last parameter
        req = build_explanation_request("Synthetic Vendor A", 12, CFG, "high")
        self.assertEqual(req["messages"][0]["content"], BASE + " Risk level: high.")

    def test_without_risk_request_is_unchanged(self):  # AC-04.2
        expected = {"provider": "p", "model": "m", "max_tokens": 10,
                    "messages": [{"role": "user", "content": BASE}]}
        self.assertEqual(build_explanation_request("Synthetic Vendor A", 12, CFG), expected)

    def test_explicit_none_is_not_given(self):  # AC-04.5 [Pending TQ-4]
        self.assertEqual(build_explanation_request("Synthetic Vendor A", 12, CFG, risk=None),
                         build_explanation_request("Synthetic Vendor A", 12, CFG))
        self.assertNotIn("Risk level", build_explanation_request("Synthetic Vendor A", 12, CFG, None)["messages"][0]["content"])

    def test_existing_positional_config_call(self):  # AC-04.3
        req = build_explanation_request("Synthetic Vendor A", 12, CFG)
        self.assertEqual((req["provider"], req["model"], req["max_tokens"]), ("p", "m", 10))

    def test_provider_model_tokens_from_config_with_risk(self):  # AC-04.4 (explicit config)
        req = build_explanation_request("Synthetic Vendor A", 12, CFG, risk="high")
        self.assertEqual((req["provider"], req["model"], req["max_tokens"]), ("p", "m", 10))
        self.assertEqual(len(req["messages"]), 1)
        self.assertEqual(req["messages"][0]["role"], "user")

    def test_provider_model_tokens_from_models_json_with_risk(self):  # AC-04.4 (models.json)
        cfg = load_config()
        req = build_explanation_request("Synthetic Vendor A", 12, risk="medium")
        self.assertEqual((req["provider"], req["model"], req["max_tokens"]),
                         (cfg["provider"], cfg["model"], cfg["max_tokens"]))
        self.assertTrue(req["messages"][0]["content"].endswith(" Risk level: medium."))


if __name__ == "__main__":
    unittest.main()
