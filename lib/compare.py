"""Compare S3 and local standard tool reports."""

from __future__ import print_function

import json
import os
from pathlib import Path

from lib.report_schema import SCHEMA_VERSION, load_report, save_report

COMPARE_TOLERANCE = 0.5  # percentage points for float metric values


def _status_compatible(s3_status, local_status):
    if s3_status == local_status:
        return True
    warn_set = {"PASS", "WARN"}
    if s3_status in warn_set and local_status in warn_set:
        return True
    return False


def _metric_diff(key, s3_val, local_val):
    if s3_val is None and local_val is None:
        return None
    if s3_val is None or local_val is None:
        return {"field": key, "s3": s3_val, "local": local_val, "match": False}
    if isinstance(s3_val, (int, float)) and isinstance(local_val, (int, float)):
        match = abs(float(s3_val) - float(local_val)) <= COMPARE_TOLERANCE
        return {"field": key, "s3": s3_val, "local": local_val, "match": match, "delta": float(local_val) - float(s3_val)}
    return {"field": key, "s3": s3_val, "local": local_val, "match": s3_val == local_val}


def compare_reports(s3_report, local_report):
    """Return structured comparison between two standard tool reports."""
    branch = s3_report.get("branch_name") or local_report.get("branch_name", "")
    diffs = []

    if s3_report.get("branch_name") != local_report.get("branch_name"):
        diffs.append({
            "field": "branch_name",
            "s3": s3_report.get("branch_name"),
            "local": local_report.get("branch_name"),
            "match": False,
        })

    s3_status = s3_report.get("status", "ERROR")
    local_status = local_report.get("status", "ERROR")
    status_match = _status_compatible(s3_status, local_status)
    diffs.append({
        "field": "status",
        "s3": s3_status,
        "local": local_status,
        "match": status_match,
    })

    s3_tool = s3_report.get("tool_name", "")
    local_tool = local_report.get("tool_name", "")
    tool_match = _tool_names_compatible(s3_tool, local_tool)
    diffs.append({
        "field": "tool_name",
        "s3": s3_tool,
        "local": local_tool,
        "match": tool_match,
    })

    s3_values = s3_report.get("metric_values") or {}
    local_values = local_report.get("metric_values") or {}
    all_keys = sorted(set(s3_values) | set(local_values))
    metric_diffs = []
    for key in all_keys:
        row = _metric_diff(key, s3_values.get(key), local_values.get(key))
        if row:
            metric_diffs.append(row)
            diffs.append(row)

    hard_mismatches = [d for d in diffs if not d.get("match")]
    if not hard_mismatches:
        verdict = "MATCH"
    elif status_match and not metric_diffs:
        verdict = "PARTIAL"
    elif status_match:
        verdict = "PARTIAL"
    else:
        verdict = "MISMATCH"

    reasons = []
    if not status_match:
        reasons.append("status differs: s3=%s local=%s" % (s3_status, local_status))
    if not tool_match:
        reasons.append("tool differs: s3=%r local=%r" % (s3_tool, local_tool))
    for md in metric_diffs:
        if not md.get("match"):
            reasons.append("%s differs: s3=%s local=%s" % (md["field"], md.get("s3"), md.get("local")))

    return {
        "schema_version": SCHEMA_VERSION,
        "branch_name": branch,
        "verdict": verdict,
        "status_match": status_match,
        "tool_match": tool_match,
        "field_diffs": diffs,
        "metric_diffs": metric_diffs,
        "summary": "; ".join(reasons) if reasons else "S3 and local reports align",
        "s3_report_path": s3_report.get("_path", ""),
        "local_report_path": local_report.get("_path", ""),
    }


def _tool_names_compatible(s3_tool, local_tool):
    if not s3_tool or not local_tool:
        return True
    s3 = s3_tool.lower().replace(" ", "")
    local = local_tool.lower().replace(" ", "")
    if s3 == local:
        return True
    if "coverage" in s3 and "coverage" in local:
        return True
    if s3 in local or local in s3:
        return True
    return False


def compare_report_files(s3_path, local_path):
    s3_report = load_report(s3_path)
    local_report = load_report(local_path)
    s3_report["_path"] = str(s3_path)
    local_report["_path"] = str(local_path)
    return compare_reports(s3_report, local_report)


def compare_batch(proof_root, branches=None):
    """Compare s3_report.json vs local_report.json for branches under proof_root."""
    proof_root = Path(proof_root)
    results = []
    for tech_dir in sorted(proof_root.iterdir()):
        if not tech_dir.is_dir():
            continue
        for branch_dir in sorted(tech_dir.iterdir()):
            if not branch_dir.is_dir():
                continue
            branch_name = branch_dir.name
            if branches and branch_name not in branches:
                continue
            s3_path = branch_dir / "s3_report.json"
            local_path = branch_dir / "local_report.json"
            if not s3_path.is_file() or not local_path.is_file():
                results.append({
                    "branch_name": branch_name,
                    "verdict": "INCOMPLETE",
                    "summary": "missing %s" % (
                        "both reports"
                        if not s3_path.is_file() and not local_path.is_file()
                        else ("s3_report" if not s3_path.is_file() else "local_report")
                    ),
                    "proof_dir": str(branch_dir),
                })
                continue
            comparison = compare_report_files(s3_path, local_path)
            comparison["proof_dir"] = str(branch_dir)
            out_path = branch_dir / "comparison.json"
            save_report(comparison, out_path)
            comparison["comparison_path"] = str(out_path)
            results.append(comparison)
    return results


def compare_three_reports(taxonomy_report, s3_report, local_report):
    """Compare taxonomy, S3, and local standard reports."""
    s3_local = compare_reports(s3_report, local_report)
    tax_status = (taxonomy_report or {}).get("status", "SKIPPED")
    s3_status = (s3_report or {}).get("status", "SKIPPED")
    local_status = (local_report or {}).get("status", "SKIPPED")
    all_match = tax_status == s3_status == local_status or (
        tax_status in ("PASS", "WARN") and s3_status in ("PASS", "WARN") and local_status in ("PASS", "WARN")
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "branch_name": s3_report.get("branch_name") or local_report.get("branch_name", ""),
        "verdict": "MATCH" if all_match and s3_local["verdict"] == "MATCH" else (
            "PARTIAL" if s3_local["verdict"] in ("MATCH", "PARTIAL") else "MISMATCH"
        ),
        "taxonomy_status": tax_status,
        "s3_status": s3_status,
        "local_status": local_status,
        "s3_vs_local": s3_local,
        "summary": "taxonomy=%s s3=%s local=%s; %s" % (
            tax_status, s3_status, local_status, s3_local.get("summary", "")),
    }


def summarize_comparisons(results):
    total = len(results)
    match = sum(1 for r in results if r.get("verdict") == "MATCH")
    partial = sum(1 for r in results if r.get("verdict") == "PARTIAL")
    mismatch = sum(1 for r in results if r.get("verdict") == "MISMATCH")
    incomplete = sum(1 for r in results if r.get("verdict") == "INCOMPLETE")
    return {
        "total": total,
        "match": match,
        "partial": partial,
        "mismatch": mismatch,
        "incomplete": incomplete,
    }
