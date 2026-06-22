"""Tests for local tool runs when branch source is a temp GitHub materialization dir."""

from __future__ import print_function

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from lib.local_tool_runner import run_local_tool_report  # noqa: E402
from lib.tool_assert import tool_assert_branch  # noqa: E402

REAL_BRANCH = "RM_Defect-Probability_Bug_2.6"


class LocalToolBranchNameTests(unittest.TestCase):
    def test_run_local_tool_report_accepts_temp_dir_with_explicit_branch_name(self):
        with tempfile.TemporaryDirectory(prefix="gh_branch_") as tmp:
            with patch("lib.tool_assert.tool_assert_branch") as mock_assert:
                mock_assert.return_value = {
                    "branch_name": REAL_BRANCH,
                    "technique_code": "RM",
                    "metric_code": "DEPR",
                    "branch_type": "Bug",
                    "status": "PASS",
                    "tool_used": "radon",
                    "real_tool": True,
                }
                report = run_local_tool_report(
                    tmp,
                    "RM",
                    "DEPR",
                    "Bug",
                    "2.6",
                    install=False,
                    branch_name=REAL_BRANCH,
                )
        self.assertEqual(report["branch_name"], REAL_BRANCH)
        mock_assert.assert_called_once()
        _, kwargs = mock_assert.call_args
        self.assertEqual(kwargs.get("branch_name"), REAL_BRANCH)

    def test_run_local_tool_report_raises_for_unparseable_temp_dir_without_identity(self):
        with tempfile.TemporaryDirectory(prefix="gh_branch_") as tmp:
            with self.assertRaises(ValueError) as ctx:
                run_local_tool_report(tmp, install=False)
        self.assertIn("unparseable branch folder", str(ctx.exception))

    def test_tool_assert_branch_uses_explicit_branch_name_on_temp_dir(self):
        with tempfile.TemporaryDirectory(prefix="gh_branch_") as tmp:
            result = tool_assert_branch(
                tmp,
                "RM",
                "DEPR",
                "Bug",
                branch_name=REAL_BRANCH,
            )
        self.assertEqual(result.get("branch_name"), REAL_BRANCH)
        self.assertNotEqual(result.get("status"), "SKIPPED")


if __name__ == "__main__":
    unittest.main()
