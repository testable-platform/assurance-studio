"""Tests for branch-scoped taxonomy failing sections and S3 active-branch sync."""

import os
import unittest
from unittest.mock import patch

from lib.s3_sync import _branch_allowed
from lib.taxonomy_meta import branch_taxonomy_scope, failing_sections_for_branch


class BranchTaxonomyScopeTests(unittest.TestCase):
    def test_eps_branch_scope(self):
        scope = branch_taxonomy_scope("SX_Entry-Point-Sanitization_Bug_2.6")
        self.assertIn("Input Validation Testing", scope)
        self.assertIn("Entry Point Sanitization", scope)

    def test_scoped_failing_sections_only_metric_labels(self):
        gate = {
            "gate_status": "completed",
            "weighted_breakdown": [
                {
                    "testing_type": "Security Testing",
                    "techniques": [
                        {
                            "technique": "Static Vulnerabilities (SAST)",
                            "classifications": [
                                {"classification": "Input Validation Testing", "normalized_score": 0.0},
                                {"classification": "Secure Coding Validation", "normalized_score": 100.0},
                            ],
                        }
                    ],
                },
                {
                    "testing_type": "Code Quality",
                    "techniques": [
                        {
                            "technique": "Code Duplication",
                            "classifications": [
                                {"classification": "Defect Propagation Risk Detection", "normalized_score": 0.0},
                            ],
                        }
                    ],
                },
            ],
        }
        rows = failing_sections_for_branch(
            gate,
            "SX_Entry-Point-Sanitization_Bug_2.6",
            score_threshold=0.0,
        )
        labels = {row["classification"] for row in rows}
        self.assertIn("Input Validation Testing", labels)
        self.assertNotIn("Defect Propagation Risk Detection", labels)


class S3ActiveBranchTests(unittest.TestCase):
    def test_active_branch_bypasses_prefix_filter(self):
        with patch.dict(
            os.environ,
            {
                "S3_SYNC_BRANCH_PREFIX": "SA_DOV_",
                "S3_SYNC_ACTIVE_BRANCHES": "SX_Entry-Point-Sanitization_Bug_2.6",
            },
            clear=False,
        ):
            self.assertTrue(_branch_allowed("SX_Entry-Point-Sanitization_Bug_2.6"))
            self.assertFalse(_branch_allowed("SX_Other_Bug_2.6"))
