"""Compare taxonomy reports, S3 tool outputs, and local build branches.

Way 1 — Taxonomy vs S3 tool reports (Structural Analysis, per branch type)
Way 2 — Both vs local build/ repos for the branches that were run

Context:
  - taxonomy_reports: SA_DOV_{Bug,BugFX,TCC,CC}_2.6  (notebook scope)
  - s3_downloads:     SA_EPI_{Bug,BugFX,TCC,CC}_2.6  (platform tool bundle)
  - build/:            generated branch checkouts (SA_DOV_* + SA_EPI_*)
"""

from __future__ import print_function

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.metrics import branch_name_from_report_folder, infer_from_branch_name
from lib.registry import metric_entry
from lib.sa_metrics import ABBREV_TO_CLASSIFICATION, SA_METRICS
from lib.sa_qa import parse_sa_results, verify_taxonomy_file

CLASSIFICATION_TO_ABBREV = {cls: abbrev for _, abbrev, cls, _, _ in SA_METRICS}
from lib.tool_assert import tool_assert_branch, tool_family

TAXONOMY_ROOT = ROOT / "taxonomy_reports" / "Structural Analysis"
S3_CELL = ROOT / "s3_downloads" / "afb346d7-6a48-4f19-bdc6-56b77367ded4"
BUILD_ROOT = ROOT / "build"
OUT_JSON = ROOT / "runs" / "compare_taxonomy_s3_build.json"
OUT_MD = ROOT / "runs" / "compare_taxonomy_s3_build.md"

TAXONOMY_METRIC = "DOV"
S3_METRIC = "EPI"
BRANCH_TYPES = ("Bug", "BugFX", "TCC", "CC")
VERSION = "2.6"

COVERAGE_FAIL_THRESHOLD = 50.0
COMPLEXITY_FAIL_THRESHOLD = 15

# SA metric -> S3 tool folder used to derive pass/fail
METRIC_S3_TOOL = {
    "DOV": "coverage-py",
    "EPI": "crosshair",
    "LSV": "coverage-py",
    "TLCC": "crosshair",
    "TDI": "lizard",
    "QRA": "testmon",
}


def branch_name(metric, btype):
    return "SA_%s_%s_%s" % (metric, btype, VERSION)


def load_taxonomy_runs():
    runs = {}
    for html in sorted(TAXONOMY_ROOT.rglob("taxonomy-gate.html")):
        folder = html.parent.name
        branch = branch_name_from_report_folder(folder)
        tech, metric, btype, _ = infer_from_branch_name(branch)
        if tech != "SA" or metric != TAXONOMY_METRIC:
            continue
        text = html.read_text(encoding="utf-8")
        commit = ""
        m = re.search(r"Commit ID</th><td>([^<]+)", text)
        if m:
            commit = m.group(1).strip()
        ok, detail = verify_taxonomy_file(str(html), metric, btype)
        runs[btype] = {
            "branch": branch,
            "branch_type": btype,
            "commit": commit,
            "html_path": str(html),
            "target_verify_ok": ok,
            "target_verify_detail": detail,
            "sa_results": parse_sa_results(text),
        }
    return runs


def discover_s3_runs():
    runs = {}
    if not S3_CELL.is_dir():
        return runs
    for run_uuid_dir in S3_CELL.iterdir():
        if not run_uuid_dir.is_dir():
            continue
        for branch_dir in run_uuid_dir.iterdir():
            if not branch_dir.is_dir():
                continue
            tech, metric, btype, _ = infer_from_branch_name(branch_dir.name)
            if tech != "SA" or metric != S3_METRIC:
                continue
            sha_dir = next((d for d in branch_dir.iterdir() if d.is_dir()), None)
            tool_root = next((d for d in sha_dir.iterdir() if d.is_dir()), None) if sha_dir else None
            if not tool_root:
                continue
            tool_files = {}
            for tool_dir in tool_root.iterdir():
                if tool_dir.is_dir():
                    for f in tool_dir.rglob("*"):
                        if f.is_file():
                            tool_files[tool_dir.name] = f
                            break
            runs[btype] = {
                "branch": branch_dir.name,
                "branch_type": btype,
                "commit": sha_dir.name,
                "run_uuid": tool_root.name,
                "tool_root": str(tool_root),
                "tool_files": {k: str(v) for k, v in tool_files.items()},
            }
    return runs


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None


def normalize_outcome(label):
    if not label:
        return "MISSING"
    s = str(label).strip().upper()
    if s in ("PASS", "WARN", "FAIL", "SKIPPED", "MISSING", "UNSUPPORTED"):
        return s
    return s.lower()


def outcome_to_gate(label):
    s = normalize_outcome(label)
    if s in ("PASS", "WARN", "FAIL"):
        return s.lower()
    return s.lower()


def evaluate_s3_metric(abbrev, tool_files):
  """Derive PASS/FAIL/WARN from S3 tool JSON for one SA metric."""
  tool_key = METRIC_S3_TOOL.get(abbrev)
  path = tool_files.get(tool_key)
  detail = {"tool": tool_key, "file": path}

  if not path:
    return "MISSING", detail

  if abbrev in ("DOV", "LSV"):
    data = _read_json(path) or {}
    totals = data.get("totals") or {}
    covered = totals.get("covered_lines", 0)
    statements = totals.get("num_statements", 0)
    pct = (100.0 * covered / statements) if statements else 0.0
    violation = statements == 0 or pct < COVERAGE_FAIL_THRESHOLD
    detail.update({"covered_lines": covered, "num_statements": statements, "coverage_pct": round(pct, 1)})
    return ("FAIL" if violation else "PASS"), detail

  if abbrev in ("EPI", "TLCC"):
    data = _read_json(path) or {}
    counterex = float(data.get("functions_with_counterexample") or 0)
    integrity = float(data.get("execution_path_integrity_pct") or 100.0)
    boundary = float(data.get("boundary_issue_ratio") or 0)
    violation = counterex > 0 or boundary > 0 or integrity < 100.0
    detail.update({
      "execution_path_integrity_pct": integrity,
      "functions_with_counterexample": counterex,
      "boundary_issue_ratio": boundary,
    })
    return ("FAIL" if violation else "PASS"), detail

  if abbrev == "TDI":
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    if path.endswith(".xml"):
      scores = [int(x) for x in re.findall(r"<ccn>(\d+)</ccn>", text, re.I)]
    else:
      data = _read_json(path) or {}
      items = data if isinstance(data, list) else data.get("functions", [])
      scores = []
      for it in items:
        if isinstance(it, dict):
          for k in ("cyclomatic_complexity", "complexity", "cognitive_complexity"):
            if k in it:
              scores.append(float(it[k]))
    max_cc = max(scores) if scores else 0
    detail.update({"max_complexity": max_cc})
    return ("FAIL" if max_cc > COMPLEXITY_FAIL_THRESHOLD else "PASS"), detail

  if abbrev == "QRA":
    data = _read_json(path) or {}
    tests = int(data.get("tests_total_count") or 0)
    present = bool(data.get("testmondata_present"))
    violation = tests < 2
    detail.update({"tests_total_count": tests, "testmondata_present": present})
    return ("FAIL" if violation else "PASS"), detail

  return "UNSUPPORTED", detail


def load_build_assert(metric, btype):
    path = BUILD_ROOT / branch_name(metric, btype)
    if not path.is_dir():
        return {"present": False, "path": str(path)}
    result = tool_assert_branch(str(path))
    return {
        "present": True,
        "path": str(path),
        "status": result.get("status"),
        "actual_outcome": result.get("actual_outcome"),
        "expected_outcome": result.get("expected_outcome"),
        "tool_used": result.get("tool_used"),
        "raw_metric_value": result.get("raw_metric_value"),
        "message": result.get("message"),
    }


def expected_for_target(btype, outcome):
    o = normalize_outcome(outcome)
    if btype == "Bug":
        return o == "FAIL"
    return o in ("PASS", "WARN")


def compare_taxonomy_vs_s3(tax_runs, s3_runs):
    rows = []
    for btype in BRANCH_TYPES:
        tax = tax_runs.get(btype)
        s3 = s3_runs.get(btype)
        if not tax or not s3:
            rows.append({
                "branch_type": btype,
                "error": "missing taxonomy=%s s3=%s" % (bool(tax), bool(s3)),
            })
            continue

        metric_rows = []
        for classification, abbrev in sorted(CLASSIFICATION_TO_ABBREV.items(), key=lambda x: x[1]):
            tax_result = tax["sa_results"].get(classification, "missing")
            s3_outcome, s3_detail = evaluate_s3_metric(abbrev, s3["tool_files"])
            aligned = outcome_to_gate(tax_result) == outcome_to_gate(s3_outcome)
            metric_rows.append({
                "metric": abbrev,
                "classification": classification,
                "taxonomy": tax_result,
                "s3_tool": s3_outcome,
                "s3_detail": s3_detail,
                "aligned": aligned,
                "is_target": abbrev == TAXONOMY_METRIC,
            })

        target = next(r for r in metric_rows if r["is_target"])
        rows.append({
            "branch_type": btype,
            "taxonomy_branch": tax["branch"],
            "s3_branch": s3["branch"],
            "taxonomy_commit": tax["commit"],
            "s3_commit": s3["commit"],
            "note": "Different metric branches (DOV taxonomy vs EPI S3); compared by branch type",
            "target_taxonomy_verify": tax["target_verify_ok"],
            "metrics": metric_rows,
            "all_aligned": all(m["aligned"] for m in metric_rows if m["s3_tool"] not in ("MISSING", "UNSUPPORTED")),
            "target_aligned": target["aligned"],
        })
    return rows


def compare_three_way(tax_runs, s3_runs):
    rows = []
    for btype in BRANCH_TYPES:
        tax = tax_runs.get(btype)
        s3 = s3_runs.get(btype)
        dov_build = load_build_assert(TAXONOMY_METRIC, btype)
        epi_build = load_build_assert(S3_METRIC, btype)

        # Target metric: DOV — taxonomy + build + s3 coverage-py
        dov_s3_out, dov_s3_detail = "MISSING", {}
        if s3:
            dov_s3_out, dov_s3_detail = evaluate_s3_metric("DOV", s3["tool_files"])

        tax_target = tax["sa_results"].get(ABBREV_TO_CLASSIFICATION[TAXONOMY_METRIC], "missing") if tax else "missing"
        build_target_status = dov_build.get("status", "MISSING")
        build_target_outcome = dov_build.get("actual_outcome", "MISSING")

        # S3 metric: EPI — s3 crosshair + build EPI
        epi_s3_out, epi_s3_detail = "MISSING", {}
        if s3:
            epi_s3_out, epi_s3_detail = evaluate_s3_metric("EPI", s3["tool_files"])
        epi_tax = tax["sa_results"].get(ABBREV_TO_CLASSIFICATION[S3_METRIC], "missing") if tax else "missing"
        epi_build_status = epi_build.get("status", "MISSING")
        epi_build_outcome = epi_build.get("actual_outcome", "MISSING")

        rows.append({
            "branch_type": btype,
            "dov_target": {
                "metric": TAXONOMY_METRIC,
                "taxonomy_branch": tax["branch"] if tax else None,
                "build_branch": branch_name(TAXONOMY_METRIC, btype),
                "taxonomy_result": tax_target,
                "s3_result": dov_s3_out,
                "s3_detail": dov_s3_detail,
                "build_status": build_target_status,
                "build_outcome": build_target_outcome,
                "build_raw": dov_build.get("raw_metric_value"),
                "taxonomy_vs_s3": outcome_to_gate(tax_target) == outcome_to_gate(dov_s3_out),
                "taxonomy_vs_build": outcome_to_gate(tax_target) == outcome_to_gate(build_target_outcome),
                "s3_vs_build": outcome_to_gate(dov_s3_out) == outcome_to_gate(build_target_outcome),
                "expected_ok_taxonomy": expected_for_target(btype, tax_target),
                "expected_ok_s3": expected_for_target(btype, dov_s3_out),
                "expected_ok_build": build_target_status == "PASS",
            },
            "epi_cross": {
                "metric": S3_METRIC,
                "s3_branch": s3["branch"] if s3 else None,
                "build_branch": branch_name(S3_METRIC, btype),
                "taxonomy_epi_row": epi_tax,
                "s3_result": epi_s3_out,
                "s3_detail": epi_s3_detail,
                "build_status": epi_build_status,
                "build_outcome": epi_build_outcome,
                "build_raw": epi_build.get("raw_metric_value"),
                "taxonomy_vs_s3": outcome_to_gate(epi_tax) == outcome_to_gate(epi_s3_out),
                "taxonomy_vs_build": outcome_to_gate(epi_tax) == outcome_to_gate(epi_build_outcome),
                "s3_vs_build": outcome_to_gate(epi_s3_out) == outcome_to_gate(epi_build_outcome),
                "expected_ok_s3": expected_for_target(btype, epi_s3_out),
                "expected_ok_build": epi_build_status == "PASS",
            },
            "build_paths": {
                "dov": dov_build.get("path"),
                "epi": epi_build.get("path"),
            },
        })
    return rows


def render_md(way1, way2, tax_runs, s3_runs):
    lines = [
        "# Taxonomy vs S3 vs Build Comparison",
        "",
        "Generated: %s" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "",
        "## Repo context",
        "",
        "Branches are generated under `build/<TECH>_<METRIC>_<TYPE>_<VERSION>/` with:",
        "- a **target** module (`sa/<module_key>.py`) containing the intentional defect variant",
        "- **stub** modules for sibling metrics",
        "",
        "| Source | Metric | Branches |",
        "|--------|--------|----------|",
        "| `taxonomy_reports/Structural Analysis/` | **DOV** (Decision Coverage) | SA_DOV_{Bug,BugFX,TCC,CC}_2.6 |",
        "| `s3_downloads/.../afb346d7.../` | **EPI** (Execution Path Integrity) | SA_EPI_{Bug,BugFX,TCC,CC}_2.6 |",
        "| `build/` | both DOV + EPI | local generated checkouts |",
        "",
        "> Taxonomy was collected for **DOV** (per notebook). S3 bundle is from **EPI** runs.",
        "> Comparisons use **branch type** (Bug / BugFX / TCC / CC) as the join key.",
        "",
        "---",
        "",
        "## Way 1 — Taxonomy vs S3 tool reports",
        "",
        "For each branch type, every Structural Analysis metric row in the taxonomy HTML",
        "is compared to the pass/fail derived from the matching S3 tool JSON.",
        "",
    ]

    for row in way1:
        if "error" in row:
            lines.append("### %s — ERROR: %s" % (row["branch_type"], row["error"]))
            continue
        lines.append("### %s (`%s` taxonomy vs `%s` s3)" % (
            row["branch_type"], row["taxonomy_branch"], row["s3_branch"]))
        lines.append("")
        lines.append("| Metric | Taxonomy | S3 tool | Aligned |")
        lines.append("|--------|----------|---------|---------|")
        for m in row["metrics"]:
            mark = "yes" if m["aligned"] else "**NO**"
            tgt = " **(target)**" if m["is_target"] else ""
            lines.append("| %s%s | %s | %s | %s |" % (
                m["metric"], tgt, m["taxonomy"].upper(), m["s3_tool"], mark))
        lines.append("")
        lines.append("- Target taxonomy verify: **%s**" % ("PASS" if row["target_taxonomy_verify"] else "FAIL"))
        lines.append("- Target row aligned with S3: **%s**" % ("yes" if row["target_aligned"] else "no"))
        lines.append("- Commits differ: taxonomy `%s` vs s3 `%s`" % (
            row["taxonomy_commit"][:12], row["s3_commit"][:12]))
        lines.append("")

    lines += ["---", "", "## Way 2 — Taxonomy + S3 vs local `build/` repos", ""]
    lines += [
        "### DOV (taxonomy target metric) — triple comparison",
        "",
        "| Type | Taxonomy | S3 (coverage-py) | Build (Coverage.py) | Tax=S3 | Tax=Build | S3=Build | Expected |",
        "|------|----------|------------------|---------------------|--------|-----------|----------|----------|",
    ]
    for row in way2:
        d = row["dov_target"]
        exp = "PASS" if d["expected_ok_taxonomy"] and d["expected_ok_s3"] and d["expected_ok_build"] else "FAIL"
        lines.append("| %s | %s | %s | %s (%s) | %s | %s | %s | %s |" % (
            row["branch_type"],
            d["taxonomy_result"].upper(),
            normalize_outcome(d["s3_result"]),
            normalize_outcome(d["build_outcome"]),
            d["build_status"],
            "yes" if d["taxonomy_vs_s3"] else "no",
            "yes" if d["taxonomy_vs_build"] else "no",
            "yes" if d["s3_vs_build"] else "no",
            exp,
        ))

    lines += [
        "",
        "### EPI (S3 run metric) - taxonomy EPI row vs S3 vs build",
        "",
        "| Type | Taxonomy (EPI row) | S3 (crosshair) | Build (Crosshair) | Tax=S3 | S3=Build | Expected |",
        "|------|-------------------|----------------|-------------------|--------|----------|----------|",
    ]
    for row in way2:
        e = row["epi_cross"]
        exp = "PASS" if e["expected_ok_s3"] and e["expected_ok_build"] else "FAIL"
        lines.append("| %s | %s | %s | %s (%s) | %s | %s | %s |" % (
            row["branch_type"],
            e["taxonomy_epi_row"].upper(),
            normalize_outcome(e["s3_result"]),
            normalize_outcome(e["build_outcome"]),
            e["build_status"],
            "yes" if e["taxonomy_vs_s3"] else "no",
            "yes" if e["s3_vs_build"] else "no",
            exp,
        ))

    lines += ["", "### Build paths", ""]
    for row in way2:
        lines.append("- **%s**: `%s` | `%s`" % (
            row["branch_type"], row["build_paths"]["dov"], row["build_paths"]["epi"]))

    return "\n".join(lines)


def main():
    tax_runs = load_taxonomy_runs()
    s3_runs = discover_s3_runs()

    way1 = compare_taxonomy_vs_s3(tax_runs, s3_runs)
    way2 = compare_three_way(tax_runs, s3_runs)

    report = {
        "taxonomy_metric": TAXONOMY_METRIC,
        "s3_metric": S3_METRIC,
        "taxonomy_branches": {k: v["branch"] for k, v in tax_runs.items()},
        "s3_branches": {k: v["branch"] for k, v in s3_runs.items()},
        "way1_taxonomy_vs_s3": way1,
        "way2_three_way": way2,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, default=str)

    md = render_md(way1, way2, tax_runs, s3_runs)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)

    print(md)
    print("\nWrote %s" % OUT_JSON)
    print("Wrote %s" % OUT_MD)


if __name__ == "__main__":
    main()
