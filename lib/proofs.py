"""Gather taxonomy, S3, and local proofs per branch."""

from __future__ import print_function

import os
import shutil
from pathlib import Path

from lib.compare import compare_report_files
from lib.local_tool_runner import run_local_tool_report
from lib.metrics import report_group_label
from lib.registry import iter_branches
from lib.report_schema import (
    find_s3_report_path,
    from_s3_tool_root,
    load_report,
    save_report,
)
from lib.s3_sync import sync_from_taxonomy_meta
from lib.taxonomy_meta import latest_taxonomy_by_branch, load_manifest_runs

ROOT = Path(__file__).resolve().parents[1]

REPORT_TAXONOMY = "taxonomy_report.json"
REPORT_S3 = "s3_report.json"
REPORT_LOCAL = "local_report.json"


def _classification_dir_for_branch(branch_name, taxonomy_root="taxonomy_reports", registry=None):
    from lib.metrics import infer_from_branch_name

    tech, _, _, _ = infer_from_branch_name(branch_name, registry)
    if not tech:
        return None
    group = report_group_label(tech, registry)
    return Path(taxonomy_root) / group


def whitebox_completion(branches, taxonomy_root="taxonomy_reports", root=None, registry=None):
    """Per-branch whitebox status from taxonomy HTML + manifest."""
    from lib.registry import load_registry

    reg = registry or load_registry()
    repo_root = Path(root or ROOT)
    tax_root = repo_root / taxonomy_root
    out = {}

    # Index manifest runs by branch (latest batch per classification)
    manifest_by_branch = {}
    manifest_errors = {}
    if tax_root.is_dir():
        for class_dir in tax_root.iterdir():
            if not class_dir.is_dir():
                continue
            for run in load_manifest_runs(class_dir):
                bname = run.get("branch")
                if not bname:
                    continue
                if run.get("error"):
                    manifest_errors[bname] = run.get("error")
                if run.get("run_id"):
                    manifest_by_branch[bname] = run

    for bname in branches:
        class_dir = _classification_dir_for_branch(bname, taxonomy_root, reg)
        meta = {}
        if class_dir and class_dir.is_dir():
            meta = latest_taxonomy_by_branch(class_dir).get(bname, {})

        html_path = meta.get("html_path", "")
        has_taxonomy = bool(html_path and Path(html_path).is_file())
        run_id = meta.get("run_id") or (manifest_by_branch.get(bname) or {}).get("run_id", "")
        gate_score = (manifest_by_branch.get(bname) or {}).get("gate_score")

        if bname in manifest_errors and not has_taxonomy:
            status = "ERROR"
            detail = manifest_errors[bname]
        elif has_taxonomy and run_id:
            status = "COMPLETED"
            detail = "taxonomy report produced"
        elif has_taxonomy:
            status = "COMPLETED"
            detail = "taxonomy HTML present"
        elif bname in manifest_errors:
            status = "ERROR"
            detail = manifest_errors[bname]
        else:
            status = "NOT_COMPLETED"
            detail = "whitebox not run or no taxonomy report"

        out[bname] = {
            "status": status,
            "detail": detail,
            "run_id": run_id,
            "commit_sha": meta.get("commit_sha", ""),
            "gate_score": gate_score,
            "html_path": html_path,
            "meta": meta,
        }
    return out


def compare_readiness(branches, root=None):
    """Check which standard reports exist per branch under proofs/."""
    repo_root = Path(root or ROOT)
    rows = []
    for bname in branches:
        from lib.metrics import infer_from_branch_name

        tech, _, _, _ = infer_from_branch_name(bname)
        if not tech:
            rows.append({
                "branch_name": bname,
                "taxonomy": False,
                "s3": False,
                "local": False,
                "ready": False,
                "missing": ["parse error"],
            })
            continue
        out_dir = proof_dir(repo_root, tech, bname)
        has_tax = (out_dir / REPORT_TAXONOMY).is_file()
        has_s3 = (out_dir / REPORT_S3).is_file()
        has_local = (out_dir / REPORT_LOCAL).is_file()
        missing = []
        if not has_tax:
            missing.append("taxonomy (Page 2)")
        if not has_s3:
            missing.append("S3 (Page 2)")
        if not has_local:
            missing.append("local (Page 3)")
        rows.append({
            "branch_name": bname,
            "taxonomy": has_tax,
            "s3": has_s3,
            "local": has_local,
            "ready": has_tax and has_s3 and has_local,
            "missing": missing,
        })
    return rows


def completed_whitebox_branches(branches, taxonomy_root="taxonomy_reports", root=None, registry=None):
    """Return branch names with COMPLETED whitebox status."""
    status = whitebox_completion(branches, taxonomy_root, root, registry)
    return [b for b in branches if status.get(b, {}).get("status") == "COMPLETED"]


def proof_dir(root, technique_code, branch_name):
    return Path(root) / "proofs" / technique_code / branch_name


def _copy_taxonomy_proof(src_html, dest_dir):
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "taxonomy.html"
    shutil.copy2(src_html, dest)
    return str(dest)


def _find_taxonomy_html(branch_name, taxonomy_root="taxonomy_reports", registry=None):
    from lib.metrics import infer_from_branch_name

    tech, metric, _, _ = infer_from_branch_name(branch_name)
    if not tech:
        return None, {}
    group = report_group_label(tech, registry)
    class_dir = Path(taxonomy_root) / group
    by_branch = latest_taxonomy_by_branch(class_dir)
    meta = by_branch.get(branch_name)
    if not meta:
        return None, {}
    html_path = meta.get("html_path")
    if html_path and Path(html_path).is_file():
        return html_path, meta
    return None, meta


def collect_s3_proof(
    branch_name,
    meta=None,
    taxonomy_root="taxonomy_reports",
    download_root=None,
    dry_run=False,
    root=None,
):
    """Sync S3 bundle (if needed) and write standard s3_report.json."""
    repo_root = Path(root or ROOT)
    from lib.metrics import infer_from_branch_name

    tech, metric, branch_type, version = infer_from_branch_name(branch_name)
    if not tech:
        raise ValueError("cannot parse branch: %s" % branch_name)

    if meta is None:
        _, meta = _find_taxonomy_html(branch_name, taxonomy_root)

    meta = meta or {}
    commit_sha = meta.get("commit_sha", "")
    run_id = meta.get("run_id", "")
    html_path = meta.get("html_path", "")

    out_dir = proof_dir(repo_root, tech, branch_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    if html_path and Path(html_path).is_file():
        _copy_taxonomy_proof(html_path, out_dir)
        from lib.report_schema import from_taxonomy_html, save_report

        tax_report = from_taxonomy_html(
            html_path, tech, metric, branch_name, branch_type, version,
            commit_sha=commit_sha, run_id=run_id,
        )
        save_report(tax_report, out_dir / "taxonomy_report.json")

    if not dry_run and commit_sha and run_id:
        from lib.sa_qa import load_env

        env_file = repo_root / ".env.local"
        if env_file.is_file():
            load_env(str(env_file))
        sync_from_taxonomy_meta(meta, dry_run=False)

    dl_root = download_root or os.environ.get("S3_DOWNLOAD_ROOT", str(repo_root / "s3_downloads"))
    tool_root = find_s3_report_path(dl_root, branch_name, commit_sha, run_id)
    if not tool_root:
        report = from_s3_tool_root(
            str(out_dir),
            tech,
            metric,
            branch_name,
            branch_type,
            version,
            commit_sha=commit_sha,
            run_id=run_id,
        )
        report["status"] = "SKIPPED"
        report["raw_summary"] = "S3 bundle not found"
    else:
        report = from_s3_tool_root(
            tool_root,
            tech,
            metric,
            branch_name,
            branch_type,
            version,
            commit_sha=commit_sha,
            run_id=run_id,
        )

    out_path = out_dir / "s3_report.json"
    save_report(report, out_path)
    report["_path"] = str(out_path)
    return report


def collect_local_proof(
    branch_name,
    build_dir="build",
    install=True,
    root=None,
    meta=None,
):
    """Run local tool and write standard local_report.json."""
    repo_root = Path(root or ROOT)
    from lib.metrics import infer_from_branch_name

    tech, metric, branch_type, version = infer_from_branch_name(branch_name)
    if not tech:
        raise ValueError("cannot parse branch: %s" % branch_name)

    branch_path = repo_root / build_dir / branch_name
    out_dir = proof_dir(repo_root, tech, branch_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    commit_sha = (meta or {}).get("commit_sha", "")
    run_id = (meta or {}).get("run_id", "")

    report = run_local_tool_report(
        str(branch_path),
        tech,
        metric,
        branch_type,
        version,
        commit_sha=commit_sha,
        run_id=run_id,
        install=install,
    )
    out_path = out_dir / "local_report.json"
    save_report(report, out_path)
    report["_path"] = str(out_path)
    return report


def collect_comparison_proof(branch_name, root=None):
    """Compare taxonomy, S3, and local standard reports for one branch."""
    repo_root = Path(root or ROOT)
    from lib.metrics import infer_from_branch_name

    tech, _, _, _ = infer_from_branch_name(branch_name)
    if not tech:
        raise ValueError("cannot parse branch: %s" % branch_name)

    out_dir = proof_dir(repo_root, tech, branch_name)
    tax_path = out_dir / REPORT_TAXONOMY
    s3_path = out_dir / REPORT_S3
    local_path = out_dir / REPORT_LOCAL
    missing = []
    if not tax_path.is_file():
        missing.append("taxonomy_report.json")
    if not s3_path.is_file():
        missing.append("s3_report.json")
    if not local_path.is_file():
        missing.append("local_report.json")
    if missing:
        comparison = {
            "branch_name": branch_name,
            "verdict": "INCOMPLETE",
            "summary": "missing report(s): %s in %s" % (", ".join(missing), out_dir),
            "proof_dir": str(out_dir),
            "missing_reports": missing,
        }
        return comparison

    from lib.compare import compare_three_reports

    tax_report = load_report(tax_path)
    s3_report = load_report(s3_path)
    local_report = load_report(local_path)
    comparison = compare_three_reports(tax_report, s3_report, local_report)
    comparison["proof_dir"] = str(out_dir)
    out_path = out_dir / "comparison.json"
    import json

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(comparison, fh, indent=2)
    comparison["comparison_path"] = str(out_path)
    return comparison


def collect_local_batch(
    branches,
    build_dir="build",
    install=True,
    taxonomy_root="taxonomy_reports",
    root=None,
    progress_callback=None,
):
    """Run local tools for an explicit branch list (whitebox-completed only)."""
    repo_root = Path(root or ROOT)
    results = []
    total = len(branches)
    wb = whitebox_completion(branches, taxonomy_root, repo_root)

    for idx, bname in enumerate(branches, start=1):
        if progress_callback:
            progress_callback("local", idx - 1, total, bname, "starting")
        row = {"branch_name": bname}
        if wb.get(bname, {}).get("status") != "COMPLETED":
            row["status"] = "SKIPPED"
            row["error"] = "whitebox not completed"
            results.append(row)
            if progress_callback:
                progress_callback("local", idx, total, bname, "skipped")
            continue
        try:
            meta = wb[bname].get("meta") or {}
            report = collect_local_proof(
                bname, build_dir=build_dir, install=install, root=repo_root, meta=meta
            )
            row["local_report"] = report
            row["status"] = report.get("status", "OK")
            row["tool"] = report.get("tool_name", "")
            if progress_callback:
                progress_callback("local", idx, total, bname, row["status"])
        except Exception as exc:
            row["status"] = "ERROR"
            row["error"] = str(exc)
            if progress_callback:
                progress_callback("local", idx, total, bname, "error: %s" % exc)
        results.append(row)
    return results


def collect_proofs_batch(
    techniques="all",
    metrics="all",
    types=None,
    version="2.6",
    build_dir="build",
    taxonomy_root="taxonomy_reports",
    root=None,
    install_local=True,
    sync_s3=True,
    run_local=True,
    compare=True,
    progress_callback=None,
):
    """Full proof pipeline for selected branches."""
    repo_root = Path(root or ROOT)
    results = []
    planned = list(iter_branches(techniques, metrics, types, version))
    total = len(planned)

    for idx, (tech, metric, bt, bname) in enumerate(planned, start=1):
        if progress_callback:
            progress_callback("proofs", idx - 1, total, bname, "starting")
        row = {"branch_name": bname, "technique": tech, "metric": metric, "type": bt}
        _, meta = _find_taxonomy_html(bname, taxonomy_root)

        try:
            if sync_s3:
                row["s3_report"] = collect_s3_proof(
                    bname, meta=meta, taxonomy_root=taxonomy_root, root=repo_root
                )
                if progress_callback:
                    progress_callback(
                        "proofs", idx - 1, total, bname,
                        "s3 %s" % (row["s3_report"].get("status", "?")),
                    )
            if run_local:
                row["local_report"] = collect_local_proof(
                    bname, build_dir=build_dir, install=install_local, root=repo_root, meta=meta
                )
                if progress_callback:
                    progress_callback(
                        "proofs", idx - 1, total, bname,
                        "local %s" % (row["local_report"].get("status", "?")),
                    )
            if compare and row.get("s3_report") and row.get("local_report"):
                row["comparison"] = collect_comparison_proof(bname, root=repo_root)
            row["proof_dir"] = str(proof_dir(repo_root, tech, bname))
            row["status"] = "OK"
            if progress_callback:
                progress_callback("proofs", idx, total, bname, "done")
        except Exception as exc:
            row["status"] = "ERROR"
            row["error"] = str(exc)
            if progress_callback:
                progress_callback("proofs", idx, total, bname, "error: %s" % exc)
        results.append(row)

    return results


def list_proof_branches(root=None, techniques=None):
    """List branches that have any proof artifacts."""
    repo_root = Path(root or ROOT)
    proofs_root = repo_root / "proofs"
    if not proofs_root.is_dir():
        return []
    branches = []
    for tech_dir in sorted(proofs_root.iterdir()):
        if not tech_dir.is_dir():
            continue
        if techniques and tech_dir.name not in techniques:
            continue
        for branch_dir in sorted(tech_dir.iterdir()):
            if branch_dir.is_dir():
                branches.append({
                    "technique": tech_dir.name,
                    "branch_name": branch_dir.name,
                    "proof_dir": str(branch_dir),
                    "has_taxonomy": (branch_dir / REPORT_TAXONOMY).is_file()
                    or (branch_dir / "taxonomy.html").is_file(),
                    "has_s3": (branch_dir / REPORT_S3).is_file(),
                    "has_local": (branch_dir / REPORT_LOCAL).is_file(),
                    "has_comparison": (branch_dir / "comparison.json").is_file(),
                })
    return branches


def load_proof_bundle(branch_name, root=None):
    """Load all proof artifacts for a branch."""
    repo_root = Path(root or ROOT)
    from lib.metrics import infer_from_branch_name

    tech, _, _, _ = infer_from_branch_name(branch_name)
    if not tech:
        return None
    out_dir = proof_dir(repo_root, tech, branch_name)
    bundle = {"branch_name": branch_name, "proof_dir": str(out_dir)}
    for key, filename in (
        ("taxonomy_html", "taxonomy.html"),
        ("taxonomy_report", "taxonomy_report.json"),
        ("s3_report", "s3_report.json"),
        ("local_report", "local_report.json"),
        ("comparison", "comparison.json"),
    ):
        path = out_dir / filename
        if path.is_file():
            if filename.endswith(".json"):
                bundle[key] = load_report(path)
                bundle[key]["_path"] = str(path)
            else:
                bundle[key] = str(path)
    return bundle
