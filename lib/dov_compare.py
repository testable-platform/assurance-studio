"""DOV comparison: taxonomy vs S3 coverage-py vs build tool_assert."""

from __future__ import print_function

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from lib.metrics import infer_from_branch_name
from lib.sa_metrics import ABBREV_TO_CLASSIFICATION
from lib.sa_qa import parse_sa_results, verify_taxonomy_file
from lib.s3_sync import COVERAGE_REL, DOV_BRANCHES, validate_coverage_json, _s3_config
from lib.taxonomy_meta import latest_taxonomy_by_branch
from lib.tool_assert import COVERAGE_FAIL_THRESHOLD, tool_assert_branch

DOV_CLASSIFICATION = ABBREV_TO_CLASSIFICATION["DOV"]
OUT_MD = ROOT / "runs" / "discrepancy_report.md"
OUT_JSON = ROOT / "runs" / "discrepancy_report.json"

EXPECTED = {
    "Bug": "FAIL",
    "BugFX": "PASS/WARN",
    "TCC": "PASS/WARN",
    "CC": "PASS/WARN",
}


def _normalize_gate(label):
    if not label:
        return "MISSING"
    s = str(label).strip().upper()
    if s in ("PASS", "WARN", "FAIL", "SKIPPED", "MISSING"):
        return s
    return s


def _outcome_from_violation(violation):
    return "FAIL" if violation else "PASS"


def derive_s3_dov_outcome(coverage_detail):
    """PASS/FAIL from coverage-py totals (platform bundle, no local test count)."""
    statements = int((coverage_detail or {}).get("num_statements") or 0)
    covered = int((coverage_detail or {}).get("covered_lines") or 0)
    if statements <= 0:
        return "FAIL", 0.0, {"reason": "empty coverage report"}
    pct = 100.0 * covered / statements
    violation = pct < COVERAGE_FAIL_THRESHOLD
    return _outcome_from_violation(violation), pct, {"coverage_pct": round(pct, 1)}


def expected_for_branch_type(branch_type):
    return EXPECTED.get(branch_type, "PASS/WARN")


def expected_matches_outcome(branch_type, outcome):
    o = _normalize_gate(outcome)
    if branch_type == "Bug":
        return o == "FAIL"
    return o in ("PASS", "WARN")


def find_s3_bundle(branch, commit_sha, run_id):
    """Locate local S3 tool root for branch+commit+run_id."""
    download_root = _s3_config()["download_root"]
    if not commit_sha or not run_id:
        return None
    for cell_dir in download_root.glob("*"):
        if not cell_dir.is_dir():
            continue
        for plat_dir in cell_dir.glob("*"):
            candidate = plat_dir / branch / commit_sha / run_id
            if candidate.is_dir():
                return candidate
    return None


def compare_dov_run(meta, build_root=None):
    """Compare one DOV branch across taxonomy, S3, and build."""
    build_root = Path(build_root or ROOT / "build")
    branch = meta["branch"]
    _, metric, branch_type, _ = infer_from_branch_name(branch)
    html_path = meta.get("html_path", "")

    taxonomy_result = "missing"
    taxonomy_value = ""
    taxonomy_verify_ok = False
    if html_path and Path(html_path).is_file():
        html = Path(html_path).read_text(encoding="utf-8")
        sa = parse_sa_results(html)
        taxonomy_result = sa.get(DOV_CLASSIFICATION, "missing")
        taxonomy_verify_ok, _ = verify_taxonomy_file(html_path, metric, branch_type)
        m = re.search(
            r'Decision Coverage</h3>.*?cls-name">Decision Coverage</div>.*?<strong>([^<]+)</strong>',
            html,
            re.DOTALL,
        )
        if not m:
            m = re.search(
                r'cls-name">Decision Coverage</div>.*?<strong>([^<]+)</strong>',
                html,
                re.DOTALL,
            )
        if m:
            taxonomy_value = m.group(1).strip()

    commit = meta.get("commit_sha", "")
    run_id = meta.get("run_id", "")
    s3_root = find_s3_bundle(branch, commit, run_id)
    s3_status = "MISSING"
    s3_outcome = "MISSING"
    s3_pct = None
    s3_coverage_path = ""
    if s3_root:
        s3_status, cov_detail = validate_coverage_json(s3_root)
        s3_coverage_path = cov_detail.get("path", str(s3_root / COVERAGE_REL))
        s3_outcome, s3_pct, _ = derive_s3_dov_outcome(cov_detail)

    build_path = build_root / branch
    build_status = "MISSING"
    build_outcome = "MISSING"
    build_raw = ""
    if build_path.is_dir():
        tr = tool_assert_branch(str(build_path))
        build_status = tr.get("status", "MISSING")
        build_outcome = _normalize_gate(tr.get("actual_outcome", "MISSING"))
        build_raw = tr.get("raw_metric_value", "")

    expected = expected_for_branch_type(branch_type)
    tax_g = _normalize_gate(taxonomy_result)
    s3_g = _normalize_gate(s3_outcome)
    build_g = _normalize_gate(build_outcome)

    aligned_ab = tax_g == s3_g if tax_g != "MISSING" and s3_g != "MISSING" else False
    aligned_bc = s3_g == build_g if s3_g != "MISSING" and build_g != "MISSING" else False
    aligned_ac = tax_g == build_g if tax_g != "MISSING" and build_g != "MISSING" else False
    meets_expectation = (
        expected_matches_outcome(branch_type, tax_g)
        and expected_matches_outcome(branch_type, s3_g)
        and build_status == "PASS"
    )
    status = "MATCH" if (aligned_ab and aligned_ac and meets_expectation) else "DISCREPANCY"

    return {
        "branch": branch,
        "branch_type": branch_type,
        "commit_sha": commit,
        "run_id": run_id,
        "expected": expected,
        "taxonomy": tax_g,
        "taxonomy_value": taxonomy_value,
        "taxonomy_verify_ok": taxonomy_verify_ok,
        "s3": s3_g,
        "s3_coverage_status": s3_status,
        "s3_coverage_pct": s3_pct,
        "build": build_g,
        "build_status": build_status,
        "build_raw": build_raw,
        "status": status,
        "aligned_taxonomy_s3": aligned_ab,
        "aligned_s3_build": aligned_bc,
        "aligned_taxonomy_build": aligned_ac,
        "paths": {
            "taxonomy_html": html_path,
            "s3_coverage_json": s3_coverage_path,
            "s3_root": str(s3_root) if s3_root else "",
            "build": str(build_path),
        },
    }


def compare_all_dov(classification_dir=None, build_root=None):
    classification_dir = Path(
        classification_dir or ROOT / "taxonomy_reports" / "Structural Analysis")
    metas = latest_taxonomy_by_branch(classification_dir, DOV_BRANCHES)
    rows = []
    for branch in sorted(DOV_BRANCHES):
        if branch not in metas:
            rows.append({
                "branch": branch,
                "status": "DISCREPANCY",
                "expected": expected_for_branch_type(
                    infer_from_branch_name(branch)[2]),
                "taxonomy": "MISSING",
                "s3": "MISSING",
                "build": "MISSING",
                "note": "no taxonomy report on disk",
            })
            continue
        rows.append(compare_dov_run(metas[branch], build_root))
    return rows


def render_discrepancy_report(rows, manual_section=None):
    lines = [
        "# DOV Discrepancy Report",
        "",
        "Generated: %s" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "",
        "## Summary",
        "",
    ]
    n_match = sum(1 for r in rows if r.get("status") == "MATCH")
    n_disc = sum(1 for r in rows if r.get("status") == "DISCREPANCY")
    n_pass = sum(1 for r in rows if r.get("taxonomy_verify_ok"))
    lines.append("- Branches compared: **%d**" % len(rows))
    lines.append("- MATCH: **%d** | DISCREPANCY: **%d**" % (n_match, n_disc))
    lines.append("- Taxonomy target verify PASS: **%d** / **%d**" % (n_pass, len(rows)))
    lines += [
        "",
        "## Comparison A + B — Taxonomy | S3 (coverage-py) | Build (tool_assert)",
        "",
        "| Branch | Expected | Taxonomy | S3 (coverage-py) | Build (tool_assert) | Status |",
        "|--------|----------|----------|------------------|---------------------|--------|",
    ]
    for r in rows:
        lines.append("| %s | %s | %s | %s | %s (%s) | **%s** |" % (
            r.get("branch", "?"),
            r.get("expected", "?"),
            r.get("taxonomy", "?"),
            r.get("s3", "?"),
            r.get("build", "?"),
            r.get("build_status", "?"),
            r.get("status", "?"),
        ))

    disc = [r for r in rows if r.get("status") == "DISCREPANCY"]
    if disc:
        lines += ["", "## Discrepancy notes", ""]
        for r in disc:
            lines.append("### %s" % r.get("branch", "?"))
            paths = r.get("paths") or {}
            lines.append("- Expected: **%s**" % r.get("expected"))
            lines.append("- Taxonomy: **%s** (verify ok: %s)" % (
                r.get("taxonomy"), r.get("taxonomy_verify_ok")))
            if r.get("taxonomy_value"):
                lines.append("- Taxonomy value: `%s`" % r["taxonomy_value"])
            lines.append("- S3: **%s** (coverage file status: %s)" % (
                r.get("s3"), r.get("s3_coverage_status")))
            if r.get("s3_coverage_pct") is not None:
                lines.append("- S3 coverage %%: %s" % r["s3_coverage_pct"])
            lines.append("- Build: **%s** (`%s`)" % (r.get("build"), r.get("build_raw")))
            lines.append("- Taxonomy HTML: `%s`" % paths.get("taxonomy_html", ""))
            lines.append("- S3 coverage.json: `%s`" % paths.get("s3_coverage_json", ""))
            lines.append("- Build path: `%s`" % paths.get("build", ""))
            lines.append("")

    lines += [
        "",
        "## Manual verification",
        "",
        "For each branch, complete the checklist below after automated comparison.",
        "",
    ]
    if manual_section:
        lines.append(manual_section)
    else:
        for r in rows:
            bt = r.get("branch_type") or infer_from_branch_name(r.get("branch", ""))[2]
            lines += [
                "### %s" % r.get("branch", "?"),
                "",
                "- [ ] Checkout commit `%s`" % (r.get("commit_sha") or "?"),
                "- [ ] Confirm seeded marker in `sa/decision_coverage.py` (Bug: `escalated-` + decision_case functions)",
                "- [ ] Run local coverage on `sa/decision_coverage.py`; compare to S3 `coverage.json`",
                "- [ ] Open taxonomy HTML; confirm Decision Coverage row matches local run",
                "- [ ] Confirm `tool_assert_branch(build/%s)` matches manual coverage" % r.get("branch", "?"),
                "- [ ] **Manual result:** confirmed / not confirmed — notes:",
                "",
            ]
    return "\n".join(lines)


def write_discrepancy_report(classification_dir=None, build_root=None):
    rows = compare_all_dov(classification_dir, build_root)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, default=str)
    md = render_discrepancy_report(rows)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)
    return rows, OUT_MD
