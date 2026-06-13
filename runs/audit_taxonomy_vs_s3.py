"""Audit taxonomy gate HTML reports against downloaded S3 tool outputs (per branch)."""

from __future__ import print_function

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.metrics import branch_name_from_report_folder, infer_from_branch_name
from lib.registry import metric_entry
from lib.sa_metrics import ABBREV_TO_CLASSIFICATION
from lib.sa_qa import parse_sa_results, verify_taxonomy_file
from lib.tool_assert import tool_family

TAXONOMY_ROOT = ROOT / "taxonomy_reports"
S3_ROOT = ROOT / "s3_downloads"
OUT_JSON = ROOT / "runs" / "taxonomy_s3_audit.json"
OUT_MD = ROOT / "runs" / "taxonomy_s3_audit.md"

COVERAGE_FAIL_THRESHOLD = 50.0
EPI_INTEGRITY_FAIL_THRESHOLD = 100.0  # below => path integrity issue


def iter_taxonomy_runs():
    for html in sorted(TAXONOMY_ROOT.rglob("taxonomy-gate.html")):
        run_folder = html.parent.name
        branch = branch_name_from_report_folder(run_folder)
        tech, metric, btype, version = infer_from_branch_name(branch)
        html_text = html.read_text(encoding="utf-8")
        run_id = ""
        commit = ""
        m = re.search(r"Run ID</th><td>([^<]+)", html_text)
        if m:
            run_id = m.group(1).strip()
        m = re.search(r"Commit ID</th><td>([^<]+)", html_text)
        if m:
            commit = m.group(1).strip()
        yield {
            "branch": branch,
            "tech": tech,
            "metric": metric,
            "branch_type": btype,
            "version": version,
            "html_path": html,
            "run_id": run_id,
            "commit": commit,
            "results": parse_sa_results(html_text),
        }


def discover_s3_runs():
    runs = {}
    for path in S3_ROOT.rglob("*"):
        if not path.is_dir():
            continue
        tech, metric, btype, version = infer_from_branch_name(path.name)
        if not tech:
            continue
        for sha_dir in path.iterdir():
            if not sha_dir.is_dir():
                continue
            for run_dir in sha_dir.iterdir():
                if not run_dir.is_dir():
                    continue
                tool_dirs = [d for d in run_dir.iterdir() if d.is_dir()]
                if not tool_dirs:
                    continue
                tool_files = {}
                for tool_dir in tool_dirs:
                    for f in tool_dir.rglob("*"):
                        if f.is_file():
                            tool_files[tool_dir.name] = f
                            break
                runs[path.name] = {
                    "branch": path.name,
                    "tech": tech,
                    "metric": metric,
                    "branch_type": btype,
                    "version": version,
                    "commit": sha_dir.name,
                    "run_uuid": run_dir.name,
                    "root": run_dir,
                    "tool_files": tool_files,
                }
                break
            if path.name in runs:
                break
    return runs


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def outcome_from_bool(violation):
    return "FAIL" if violation else "PASS"


def evaluate_s3_primary_tool(run):
    tech = run["tech"]
    metric = run["metric"]
    _, entry = metric_entry(tech, metric)
    tools = (entry.get("tools") or {}).get("python", {})
    primary = (tools.get("primary") or "").strip()
    family = tool_family(primary, tech)
    tool_files = run["tool_files"]
    module_key = entry["module_key"]
    classification = entry.get("taxonomy_classification") or entry.get("l4_classification")

    detail = {"primary": primary, "family": family, "module_key": module_key}

    if family == "crosshair":
        path = tool_files.get("crosshair")
        if not path:
            return "MISSING", detail, "crosshair report not found"
        data = _read_json(path) or {}
        counterex = float(data.get("functions_with_counterexample") or 0)
        integrity = float(data.get("execution_path_integrity_pct") or 100.0)
        boundary = float(data.get("boundary_issue_ratio") or 0)
        violation = counterex > 0 or boundary > 0 or integrity < EPI_INTEGRITY_FAIL_THRESHOLD
        detail.update({
            "execution_path_integrity_pct": integrity,
            "functions_with_counterexample": counterex,
            "boundary_issue_ratio": boundary,
            "tool_file": str(path),
        })
        return outcome_from_bool(violation), detail, None

    if family == "coverage":
        path = tool_files.get("coverage-py")
        if not path:
            return "MISSING", detail, "coverage-py report not found"
        data = _read_json(path) or {}
        totals = data.get("totals") or {}
        covered = totals.get("covered_lines", 0)
        statements = totals.get("num_statements", 0)
        pct = (100.0 * covered / statements) if statements else 0.0
        violation = statements == 0 or pct < COVERAGE_FAIL_THRESHOLD
        detail.update({
            "covered_lines": covered,
            "num_statements": statements,
            "coverage_pct": round(pct, 1),
            "tool_file": str(path),
        })
        return outcome_from_bool(violation), detail, None

    if family == "complexity":
        for key in ("cognitive-ast", "lizard"):
            path = tool_files.get(key)
            if not path:
                continue
            if key == "lizard":
                text = path.read_text(encoding="utf-8", errors="replace")
                scores = [int(x) for x in re.findall(r"<ccn>(\d+)</ccn>", text)]
                max_cc = max(scores) if scores else 0
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
            violation = max_cc > 15
            detail.update({"tool": key, "max_complexity": max_cc, "tool_file": str(path)})
            return outcome_from_bool(violation), detail, None
        return "MISSING", detail, "complexity report not found"

    return "UNSUPPORTED", detail, "family %s not implemented for S3 audit" % family


def expected_for_branch_type(branch_type, outcome):
    if branch_type == "Bug":
        return outcome == "FAIL"
    if branch_type == "BugFX":
        return outcome in ("PASS", "WARN")
    if branch_type == "TCC":
        return outcome in ("PASS", "WARN")
    return outcome in ("PASS", "WARN")


def taxonomy_target_result(tax_run):
    metric = tax_run["metric"]
    cls = ABBREV_TO_CLASSIFICATION.get(metric)
    if not cls:
        return None
    return tax_run["results"].get(cls)


def audit():
    tax_runs = {r["branch"]: r for r in iter_taxonomy_runs()}
    s3_runs = discover_s3_runs()
    all_branches = sorted(set(tax_runs) | set(s3_runs))

    rows = []
    for branch in all_branches:
        tax = tax_runs.get(branch)
        s3 = s3_runs.get(branch)
        row = {"branch": branch}

        if tax:
            ok, detail = verify_taxonomy_file(str(tax["html_path"]), tax["metric"], tax["branch_type"])
            row["taxonomy"] = {
                "present": True,
                "verify_ok": ok,
                "verify_detail": detail,
                "html_path": str(tax["html_path"]),
                "run_id": tax["run_id"],
                "commit": tax["commit"],
                "target_metric": tax["metric"],
                "target_classification": ABBREV_TO_CLASSIFICATION.get(tax["metric"]),
                "target_result": taxonomy_target_result(tax),
                "all_results": tax["results"],
            }
        else:
            row["taxonomy"] = {"present": False}

        if s3:
            outcome, tool_detail, err = evaluate_s3_primary_tool(s3)
            tool_ok = expected_for_branch_type(s3["branch_type"], outcome) if outcome not in ("MISSING", "UNSUPPORTED") else False
            row["s3_tools"] = {
                "present": True,
                "commit": s3["commit"],
                "run_uuid": s3["run_uuid"],
                "root": str(s3["root"]),
                "tool_count": len(s3["tool_files"]),
                "tools": sorted(s3["tool_files"]),
                "primary_outcome": outcome,
                "primary_detail": tool_detail,
                "primary_ok": tool_ok,
                "error": err,
            }
        else:
            row["s3_tools"] = {"present": False}

        if tax and s3:
            row["pairing"] = "MATCHED"
            tax_result = (row["taxonomy"]["target_result"] or "missing").lower()
            s3_outcome = row["s3_tools"]["primary_outcome"]
            aligned = (
                (tax["branch_type"] == "Bug" and tax_result == "fail" and s3_outcome == "FAIL")
                or (tax["branch_type"] != "Bug" and tax_result in ("pass", "warn") and s3_outcome in ("PASS", "WARN"))
                or (tax_result == "fail" and s3_outcome == "FAIL")
                or (tax_result in ("pass", "warn") and s3_outcome in ("PASS", "WARN"))
            )
            row["cross_check"] = {
                "taxonomy_target": tax_result,
                "s3_primary": s3_outcome,
                "aligned": aligned,
            }
        elif tax:
            row["pairing"] = "TAXONOMY_ONLY"
        elif s3:
            row["pairing"] = "S3_ONLY"
        else:
            row["pairing"] = "NONE"

        rows.append(row)
    return rows


def render_markdown(rows):
    lines = [
        "# Taxonomy vs S3 Tool Reports Audit",
        "",
        "Generated: %s" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "",
        "## Summary",
        "",
    ]
    matched = sum(1 for r in rows if r["pairing"] == "MATCHED")
    tax_only = sum(1 for r in rows if r["pairing"] == "TAXONOMY_ONLY")
    s3_only = sum(1 for r in rows if r["pairing"] == "S3_ONLY")
    tax_pass = sum(1 for r in rows if r.get("taxonomy", {}).get("verify_ok"))
    tax_fail = sum(1 for r in rows if r.get("taxonomy", {}).get("present") and not r["taxonomy"]["verify_ok"])
    s3_pass = sum(1 for r in rows if r.get("s3_tools", {}).get("primary_ok"))
    s3_fail = sum(1 for r in rows if r.get("s3_tools", {}).get("present") and not r["s3_tools"].get("primary_ok"))

    lines += [
        "| Metric | Count |",
        "|--------|-------|",
        "| Branches with taxonomy report | %d |" % (tax_only + matched),
        "| Branches with S3 tool bundle | %d |" % (s3_only + matched),
        "| Matched branch pairs | %d |" % matched,
        "| Taxonomy-only (no S3 bundle) | %d |" % tax_only,
        "| S3-only (no taxonomy report) | %d |" % s3_only,
        "| Taxonomy target verify PASS | %d |" % tax_pass,
        "| Taxonomy target verify FAIL | %d |" % tax_fail,
        "| S3 primary tool verify PASS | %d |" % s3_pass,
        "| S3 primary tool verify FAIL | %d |" % s3_fail,
        "",
        "> **Note:** Taxonomy and S3 bundles must share the same branch name to be cross-checked.",
        "> Unpaired branches are still audited independently.",
        "",
        "## Per-branch results",
        "",
    ]

    for row in rows:
        lines.append("### `%s` (%s)" % (row["branch"], row["pairing"]))
        if row["taxonomy"].get("present"):
            t = row["taxonomy"]
            lines.append("- **Taxonomy:** %s — target `%s` = **%s**" % (
                "PASS" if t["verify_ok"] else "FAIL",
                t["target_metric"],
                (t["target_result"] or "missing").upper(),
            ))
            lines.append("  - HTML: `%s`" % t["html_path"])
            lines.append("  - Commit: `%s` | Run: `%s`" % (t["commit"], t["run_id"]))
        else:
            lines.append("- **Taxonomy:** not found")

        if row["s3_tools"].get("present"):
            s = row["s3_tools"]
            lines.append("- **S3 primary tool:** %s — outcome **%s** (%s)" % (
                "PASS" if s["primary_ok"] else "FAIL",
                s["primary_outcome"],
                s["primary_detail"].get("primary", "?"),
            ))
            lines.append("  - Path: `%s`" % s["root"])
            lines.append("  - Commit: `%s` | Tools: %d" % (s["commit"], s["tool_count"]))
            if s.get("error"):
                lines.append("  - Error: %s" % s["error"])
            pd = s["primary_detail"]
            extras = {k: v for k, v in pd.items() if k not in ("primary", "family", "module_key", "tool_file")}
            if extras:
                lines.append("  - Detail: `%s`" % json.dumps(extras, default=str))
        else:
            lines.append("- **S3 tools:** not found")

        if row.get("cross_check"):
            cc = row["cross_check"]
            lines.append("- **Cross-check:** taxonomy=%s vs s3=%s → %s" % (
                cc["taxonomy_target"].upper(),
                cc["s3_primary"],
                "ALIGNED" if cc["aligned"] else "MISALIGNED",
            ))
        lines.append("")

    return "\n".join(lines)


def main():
    rows = audit()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, default=str)
    md = render_markdown(rows)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)

    print(md)
    print("\nWrote %s" % OUT_JSON)
    print("Wrote %s" % OUT_MD)

    tax_fail = sum(1 for r in rows if r.get("taxonomy", {}).get("present") and not r["taxonomy"]["verify_ok"])
    s3_fail = sum(1 for r in rows if r.get("s3_tools", {}).get("present") and not r["s3_tools"].get("primary_ok"))
    return 1 if tax_fail or s3_fail else 0


if __name__ == "__main__":
    sys.exit(main())
