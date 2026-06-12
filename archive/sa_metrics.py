# ARCHIVED: superseded by lib/sa_metrics.py
"""Structural Analysis metric registry and branch naming."""

from __future__ import print_function

import os
import re
from datetime import datetime, timezone

# module_key, abbrev, classification (taxonomy leaf), metric name, tool
SA_METRICS = [
    ("execution_path_integrity", "EPI", "Static Analysis Metric", "Execution Path Integrity", "Crosshair"),
    ("decision_coverage", "DOV", "Decision Coverage", "Decision Outcome Verification", "Coverage.py"),
    ("condition_coverage", "LSV", "Condition Coverage", "Logical Sub-expression Validation", "Pymcdc"),
    ("logic_combinatorial", "TLCC", "Logic Coverage Metric", "Total Logical Combinatorial Coverage", "Crosshair"),
    ("technical_debt", "TDI", "Maintainability Analysis", "Technical Debt Impact", "Radon/Lizard"),
    ("qa_prioritization", "QRA", "Test Prioritization", "QA Resource Allocation", "testmon"),
]

BRANCH_TYPES = ("Bug", "BugFX", "TCC", "CC")

# Fixed branch roles — always generated / executed together per metric
FIXED_BRANCH_TYPES = BRANCH_TYPES

SUPPORTED_LANGUAGES = ("python",)

# Taxonomy report folder for all SA metric branches (Testing Type in Testable)
SA_TESTING_TYPE = "Structural Analysis"

METRIC_ABBREVS = [abbrev for _, abbrev, _, _, _ in SA_METRICS]


def report_output_dir(output_root=None, classification=None):
    """taxonomy_reports/<classification>/<branch>_<timestamp>/…"""
    root = output_root or "taxonomy_reports"
    cls = classification or os.environ.get("REPORT_CLASSIFICATION", SA_TESTING_TYPE)
    return os.path.join(root, cls)


REPORT_TS_SUFFIX_RE = re.compile(r"_(\d{8}T\d{6}Z)$")


def report_timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def report_folder_name(branch_name, collected_at=None):
    """Unique folder per collection: SA_EPI_Bug_2.6_20260611T151913Z"""
    ts = collected_at or report_timestamp()
    return "%s_%s" % (branch_name, ts)


def branch_name_from_report_folder(folder_name):
    """Strip trailing _YYYYMMDDTHHMMSSZ if present."""
    m = REPORT_TS_SUFFIX_RE.search(folder_name)
    return folder_name[:m.start()] if m else folder_name


def infer_metric_from_report_folder(folder_name):
    """Return (abbrev, branch_type) from report folder name."""
    base = branch_name_from_report_folder(folder_name)
    parts = base.split("_")
    if len(parts) >= 3 and parts[0] == "SA":
        return parts[1], parts[2]
    return None, None


def is_sa_branch(branch_name):
    return branch_name.startswith("SA_") or branch_name in (
        "SA_bug_2.6", "SA_bugFX_2.6", "SA_TCC_2.6", "SA_CC_2.6",
    )

ABBREV_TO_MODULE = {abbrev: module for module, abbrev, _, _, _ in SA_METRICS}
ABBREV_TO_CLASSIFICATION = {abbrev: cls for _, abbrev, cls, _, _ in SA_METRICS}
MODULE_TO_ABBREV = {module: abbrev for module, abbrev, _, _, _ in SA_METRICS}


def branch_name(abbrev, branch_type="Bug", version="2.6"):
    return "SA_%s_%s_%s" % (abbrev, branch_type, version)


def parse_metrics_arg(metrics_csv):
    """'all' -> all abbrevs; 'EPI,DOV' -> ['EPI','DOV']; single metric -> ['EPI']."""
    if not metrics_csv or metrics_csv.strip().lower() == "all":
        return list(METRIC_ABBREVS)
    abbrevs = [m.strip().upper() for m in metrics_csv.split(",") if m.strip()]
    unknown = [m for m in abbrevs if m not in METRIC_ABBREVS]
    if unknown:
        raise ValueError("Unknown metric(s): %s (choose from %s)" % (unknown, METRIC_ABBREVS))
    return abbrevs


def branches_for_metrics(metrics_csv, version="2.6", branch_types=None):
    """Branch git names for metrics × branch types (default: all four fixed types)."""
    types = branch_types or FIXED_BRANCH_TYPES
    out = []
    for abbrev in parse_metrics_arg(metrics_csv):
        for bt in types:
            out.append(branch_name(abbrev, bt, version))
    return out


def all_metric_branches(version="2.6", branch_types=None):
    return branches_for_metrics("all", version, branch_types)


def all_bug_branches(version="2.6"):
    return all_metric_branches(version, ("Bug",))


def all_metric_branches_csv(version="2.6", branch_types=None):
    return ",".join(all_metric_branches(version, branch_types))


def module_variant(module_key, target_module_key, branch_type):
    """Map branch type to target-module code variant (non-target modules use stubs)."""
    if module_key != target_module_key:
        return "stub"
    return {
        "Bug": "bug",
        "BugFX": "bugfx",
        "TCC": "tcc",
        "CC": "cc",
    }[branch_type]
