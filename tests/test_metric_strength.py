"""Tests for metric strength scoring and score display helpers."""

import unittest

from lib.lang_generators.base import scaled_n_functions, scaled_test_count
from lib.metric_strength import score_metric
from lib.score_display import SCORE_CEILING, score_progress_display


def _signals(n_tests, n_functions, **extra):
    out = {"n_tests": n_tests, "n_functions": n_functions}
    out.update(extra)
    return out


class ScoreMetricStrongerCurveTests(unittest.TestCase):
    def _cc_score(self, n_tests, n_functions):
        result = score_metric(
            "security",
            0.0,
            {"expected_threshold": "0 vulnerabilities"},
            "CC",
            technique_code="SX",
            signals=_signals(n_tests, n_functions),
            language="python",
        )
        return result

    def test_cc_score_increases_with_thoroughness(self):
        low = self._cc_score(40, 88)
        high = self._cc_score(80, 88)
        self.assertGreater(high["score"], low["score"])
        self.assertLessEqual(high["score"], 100.0)
        self.assertTrue(low["passed"])
        self.assertTrue(high["passed"])

    def test_early_regen_step_delta_is_substantial(self):
        n_fn_4 = scaled_n_functions(72, 4)
        n_fn_6 = scaled_n_functions(72, 6)
        tests_4 = scaled_test_count(n_fn_4, "CC", 4)
        tests_6 = scaled_test_count(n_fn_6, "CC", 6)
        s4 = self._cc_score(tests_4, n_fn_4)
        s6 = self._cc_score(tests_6, n_fn_6)
        delta = s6["score"] - s4["score"]
        self.assertGreater(delta, 4.0)

    def test_tcc_passed_unchanged_with_steeper_curve(self):
        low = score_metric(
            "security",
            0.0,
            {"expected_threshold": "0 vulnerabilities"},
            "TCC",
            technique_code="SX",
            signals=_signals(40, 88, config_effective=True, outcome="PASS"),
            language="python",
        )
        high = score_metric(
            "security",
            0.0,
            {"expected_threshold": "0 vulnerabilities"},
            "TCC",
            technique_code="SX",
            signals=_signals(80, 88, config_effective=True, outcome="PASS"),
            language="python",
        )
        self.assertTrue(low["passed"])
        self.assertTrue(high["passed"])
        self.assertGreater(high["score"], low["score"])

    def test_bugfx_resolved_score_bounded_and_rises(self):
        low = score_metric(
            "security",
            0.0,
            {"expected_threshold": "0 vulnerabilities"},
            "BugFX",
            technique_code="SX",
            signals=_signals(40, 88, outcome="PASS", defect_marker=False),
            language="python",
        )
        high = score_metric(
            "security",
            0.0,
            {"expected_threshold": "0 vulnerabilities"},
            "BugFX",
            technique_code="SX",
            signals=_signals(80, 88, outcome="PASS", defect_marker=False),
            language="python",
        )
        self.assertTrue(low["passed"])
        self.assertTrue(high["passed"])
        self.assertLessEqual(high["score"], 100.0)
        self.assertGreater(high["score"] - low["score"], 4.0)


class ScoreProgressDisplayTests(unittest.TestCase):
    def test_maxed_at_ceiling(self):
        self.assertEqual(score_progress_display(95.0, 100.0), "maxed")
        self.assertEqual(score_progress_display(100.0, 100.0), "maxed")

    def test_signed_delta(self):
        self.assertEqual(score_progress_display(71.7, 73.2), "+1.5")

    def test_missing_values(self):
        self.assertEqual(score_progress_display(None, 80.0), "—")
        self.assertEqual(score_progress_display(70.0, None), "—")

    def test_ceiling_constant(self):
        self.assertEqual(SCORE_CEILING, 99.5)


if __name__ == "__main__":
    unittest.main()
