"""One-off inventory scan for S3 + taxonomy."""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(r"d:\Metric_evaluation")
sys.path.insert(0, str(ROOT))

from lib.metrics import infer_from_branch_name, branch_name_from_report_folder
from lib.sa_metrics import get_sa_metrics, ABBREV_TO_CLASSIFICATION
from lib.s3_sync import validate_coverage_json

S3 = ROOT / "s3_downloads"
TAX = ROOT / "taxonomy_reports" / "Structural Analysis"
BUILD = ROOT / "build"

SA_METRICS = {r[1]: {"module": r[0], "classification": r[2], "name": r[3], "tool": r[4]} for r in get_sa_metrics()}


def inventory_s3():
    rows = []
    if not S3.is_dir():
        return rows
    for repo_id in sorted(S3.iterdir()):
        if not repo_id.is_dir():
            continue
        for plat_uuid in sorted(repo_id.iterdir()):
            if not plat_uuid.is_dir():
                continue
            for branch_dir in sorted(plat_uuid.iterdir()):
                if not branch_dir.is_dir():
                    continue
                tech, metric, btype, ver = infer_from_branch_name(branch_dir.name)
                if tech != "SA":
                    continue
                for sha_dir in branch_dir.iterdir():
                    if not sha_dir.is_dir():
                        continue
                    for run_uuid_dir in sha_dir.iterdir():
                        if not run_uuid_dir.is_dir():
                            continue
                        tools = sorted(d.name for d in run_uuid_dir.iterdir() if d.is_dir())
                        exts = set()
                        for t in tools:
                            for f in (run_uuid_dir / t).rglob("*"):
                                if f.is_file():
                                    exts.add(f.suffix.lower())
                        cov_status, cov = validate_coverage_json(run_uuid_dir)
                        primary_tool = SA_METRICS.get(metric, {}).get("tool", "")
                        primary_key = {"Coverage.py": "coverage-py", "Crosshair": "crosshair"}.get(primary_tool.split("/")[0], "")
                        if primary_tool.startswith("Crosshair"):
                            primary_key = "crosshair"
                        has_primary = primary_key in tools if primary_key else False
                        primary_ok = False
                        if primary_key == "coverage-py":
                            primary_ok = cov_status == "OK"
                        elif primary_key == "crosshair":
                            p = run_uuid_dir / "crosshair" / "0" / "crosshair.json"
                            if p.is_file():
                                try:
                                    d = json.loads(p.read_text(encoding="utf-8"))
                                    primary_ok = d.get("execution_path_integrity_pct") is not None
                                except Exception:
                                    pass
                        complete = "Y" if (len(tools) >= 20 and has_primary and primary_ok) else "N"
                        rows.append({
                            "repo_id": repo_id.name,
                            "platform_run_uuid": plat_uuid.name,
                            "branch": branch_dir.name,
                            "metric": metric,
                            "branch_type": btype,
                            "commit": sha_dir.name,
                            "run_uuid": run_uuid_dir.name,
                            "tool_count": len(tools),
                            "tools": tools,
                            "exts": sorted(exts),
                            "coverage_status": cov_status,
                            "coverage_statements": cov.get("num_statements", 0),
                            "has_primary": has_primary,
                            "primary_ok": primary_ok,
                            "complete": complete,
                        })
    return rows


def inventory_taxonomy():
    rows = []
    if not TAX.is_dir():
        return rows
    for branch_parent in sorted(TAX.iterdir()):
        if not branch_parent.is_dir():
            continue
        tech, metric, _, _ = infer_from_branch_name(branch_parent.name)
        if tech != "SA":
            continue
        for run_dir in sorted(branch_parent.iterdir()):
            if not run_dir.is_dir():
                continue
            folder = run_dir.name
            branch = branch_name_from_report_folder(folder)
            _, m, bt, _ = infer_from_branch_name(branch)
            html = run_dir / "taxonomy-gate.html"
            gate_json = run_dir / "taxonomy-gate.json"
            html_ok = html.is_file() and html.stat().st_size > 500
            json_ok = gate_json.is_file() and gate_json.stat().st_size > 100
            commit = run_id = ""
            if html_ok:
                t = html.read_text(encoding="utf-8", errors="replace")
                mc = re.search(r"Commit ID</th><td>([^<]+)", t)
                mr = re.search(r"Run ID</th><td>([^<]+)", t)
                if mc:
                    commit = mc.group(1).strip()
                if mr:
                    run_id = mr.group(1).strip()
            rows.append({
                "folder": folder,
                "branch": branch,
                "metric": m,
                "branch_type": bt,
                "html": html_ok,
                "html_bytes": html.stat().st_size if html.is_file() else 0,
                "json": json_ok,
                "json_bytes": gate_json.stat().st_size if gate_json.is_file() else 0,
                "commit": commit,
                "run_id": run_id,
            })
    return rows


def main():
    s3 = inventory_s3()
    tax = inventory_taxonomy()
    print("S3_ROWS", len(s3))
    print(json.dumps(s3, indent=2))
    print("TAX_ROWS", len(tax))
    print(json.dumps(tax, indent=2))

    # cross ref
    metrics = sorted(set(r["metric"] for r in s3 + tax if r.get("metric")))
    types = ["Bug", "BugFX", "TCC", "CC"]
    s3_set = set((r["metric"], r["branch_type"]) for r in s3)
    tax_set = set((r["metric"], r["branch_type"]) for r in tax)
    cross = []
    for m in metrics:
        for t in types:
            cross.append({
                "metric": m,
                "branch_type": t,
                "in_s3": (m, t) in s3_set,
                "in_taxonomy": (m, t) in tax_set,
                "both": (m, t) in s3_set and (m, t) in tax_set,
            })
    print("CROSS", json.dumps(cross, indent=2))


if __name__ == "__main__":
    main()
