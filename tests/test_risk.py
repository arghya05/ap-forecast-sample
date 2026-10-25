"""STORY-03: rule-based vendor risk level (AC-03.1 to AC-03.8). Boundaries are tested on the rounded prediction (L-007)."""
import ast
import unittest
from pathlib import Path
from unittest import mock

import ap_forecast
from ap_forecast import predict_delay_days, vendor_risk
from ap_forecast import risk as risk_module


class VendorRiskThresholdTest(unittest.TestCase):
    def test_above_30_is_high(self):  # AC-03.1
        self.assertEqual(vendor_risk([31]), "high")
        self.assertEqual(vendor_risk([45, 60]), "high")

    def test_exactly_30_is_medium(self):  # AC-03.2
        self.assertEqual(vendor_risk([30]), "medium")

    def test_between_10_and_30_is_medium(self):  # AC-03.3
        self.assertEqual(vendor_risk([11]), "medium")
        self.assertEqual(vendor_risk([20, 25]), "medium")

    def test_exactly_10_is_low_and_11_is_medium(self):  # AC-03.4
        self.assertEqual(vendor_risk([10]), "low")
        self.assertEqual(vendor_risk([11]), "medium")

    def test_empty_history_is_low(self):  # AC-03.5 [Pending PQ-1]
        self.assertEqual(vendor_risk([]), "low")

    def test_early_payments_only_are_low(self):  # AC-03.6 [Pending TQ-5]
        self.assertEqual(vendor_risk([-5, -20]), "low")

    def test_negative_delays_count_as_zero_not_netted(self):  # AC-03.6 / predict.py: negatives count as 0
        self.assertEqual(predict_delay_days([-100, 62]), 31)
        self.assertEqual(vendor_risk([-100, 62]), "high")

    def test_threshold_applies_to_rounded_prediction(self):  # IF-3.4 via AC-03 preamble
        # Mean 30.33 rounds to 30 and mean 10.33 rounds to 10, so both stay below the next level.
        self.assertEqual(vendor_risk([30, 30, 31]), "medium")
        self.assertEqual(vendor_risk([10, 10, 11]), "low")
        self.assertEqual(vendor_risk([31, 31, 30]), "high")

    def test_generator_history(self):  # history is any Iterable[int]; predicted once
        self.assertEqual(vendor_risk(d for d in [31, 31]), "high")

    def test_constants(self):
        self.assertEqual((risk_module.HIGH_ABOVE_DAYS, risk_module.MEDIUM_ABOVE_DAYS), (30, 10))


class VendorRiskIsolationTest(unittest.TestCase):
    def test_no_config_read_or_llm_request(self):  # AC-03.7
        with mock.patch("ap_forecast.explain.load_config", side_effect=AssertionError("models.json read")), \
                mock.patch("ap_forecast.explain.build_explanation_request",
                           side_effect=AssertionError("LLM request built")):
            for history in ([], [5], [11], [31], [-3]):
                vendor_risk(history)

    def test_module_imports_only_typing_and_predict(self):  # AC-03.7: no explain, network or config import
        tree = ast.parse(Path(risk_module.__file__).read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(("." * node.level) + (node.module or ""))
        self.assertEqual(imported, {"typing", ".predict"})


class VendorRiskExportTest(unittest.TestCase):
    def test_exported_in_all(self):  # AC-03.8
        self.assertIn("vendor_risk", ap_forecast.__all__)
        self.assertIs(ap_forecast.vendor_risk, risk_module.vendor_risk)

    def test_existing_exports_kept(self):  # NFR-4
        for name in ("predict_delay_days", "build_explanation_request"):
            self.assertIn(name, ap_forecast.__all__)

    def test_returns_only_known_levels(self):  # AC-03.8
        levels = {vendor_risk([d]) for d in range(-5, 61)}
        self.assertEqual(levels, {"high", "medium", "low"})


if __name__ == "__main__":
    unittest.main()
