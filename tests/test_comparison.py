"""Tests for comparison semantics and export."""

from __future__ import print_function

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from lib.compare import compare_four_reports  # noqa: E402
from lib.compare_export import build_comparison_workbook  # noqa: E402
from lib.proofs import collect_comparison_proof, whitebox_completion  # noqa: E402


def _report(branch, status, tool="Tool"):
    return {
        "branch_name": branch,
        "status": status,
        "tool_name": tool,
        "metric_values": {"score": 10.0},
    }


class CompareSemanticsTests(unittest.TestCase):
    def test_verdict_ignores_taxonomy_status(self):
        tax = _report("B_Bug_2.6", "FAIL")
        s3 = _report("B_Bug_2.6", "PASS")
        local = _report("B_Bug_2.6", "PASS")
        sonar = {"branch_name": "B_Bug_2.6", "status": "SKIPPED"}
        result = compare_four_reports(tax, s3, local, sonar)
        self.assertIn(result["verdict"], ("MATCH", "PARTIAL"))
        self.assertEqual(result["taxonomy_vs_s3"], "DIFFERS")

    def test_local_only_comparison(self):
        tmp = tempfile.mkdtemp()
        proof = os.path.join(tmp, "proofs", "DF", "DF_DU-Path-Validation_Bug_2.6")
        os.makedirs(proof, exist_ok=True)
        local = _report("DF_DU-Path-Validation_Bug_2.6", "PASS", "Beniget")
        with open(os.path.join(proof, "local_report.json"), "w", encoding="utf-8") as fh:
            json.dump(local, fh)
        result = collect_comparison_proof("DF_DU-Path-Validation_Bug_2.6", root=tmp)
        self.assertEqual(result["verdict"], "PARTIAL")
        self.assertIn("s3_report.json", result.get("missing_reports", []))

    def test_excel_workbook_builds(self):
        results = [{
            "branch_name": "DF_DU-Path-Validation_Bug_2.6",
            "verdict": "PARTIAL",
            "taxonomy_status": "PASS",
            "taxonomy_vs_s3": "N/A",
            "s3_status": "SKIPPED",
            "local_status": "PASS",
            "sonar_status": "SKIPPED",
            "s3_vs_local": {"verdict": "N/A", "field_diffs": [], "metric_diffs": []},
            "local_vs_sonar": {"verdict": "N/A", "field_diffs": [], "metric_diffs": []},
            "summary": "test",
        }]
        data = build_comparison_workbook(results)
        self.assertTrue(len(data) > 1000)


class WhiteboxRunHealthTests(unittest.TestCase):
    def test_degraded_run_health_from_summary(self):
        tmp = tempfile.mkdtemp()
        tax_root = os.path.join(tmp, "taxonomy_reports", "Data Flow Testing")
        branch = "DF_DU-Path-Validation_Bug_2.6"
        folder = os.path.join(tax_root, "%s_20260618T120000Z" % branch)
        os.makedirs(folder, exist_ok=True)
        html = os.path.join(folder, "taxonomy-gate-run-001.html")
        with open(html, "w", encoding="utf-8") as fh:
            fh.write(
                "Branch name</th><td>%s</td>Commit ID</th><td>abc</td>Run ID</th><td>run-001</td>"
                % branch
            )
        with open(os.path.join(folder, "run_summary.json"), "w", encoding="utf-8") as fh:
            json.dump({
                "status": "failed",
                "total_tasks": 28,
                "completed_tasks": 27,
                "failed_tasks": 1,
            }, fh)
        result = whitebox_completion([branch], root=tmp)
        info = result[branch]
        self.assertEqual(info["status"], "COMPLETED")
        self.assertEqual(info["run_health"], "DEGRADED")
        self.assertEqual(info["failed_tasks"], 1)


if __name__ == "__main__":
    unittest.main()
