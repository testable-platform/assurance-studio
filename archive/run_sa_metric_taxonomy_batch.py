#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_qa.py + notebooks/02_run_qa_and_verify.ipynb
"""
Legacy wrapper — prefer scripts/run_sa_taxonomy.py for metric taxonomy runs.

Usage:
  py -3 scripts/run_sa_metric_taxonomy_batch.py --refresh-branches
  py -3 scripts/run_sa_metric_taxonomy_batch.py --metric all
"""

from __future__ import print_function

import argparse
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from sa_metrics import SA_METRICS, branch_name  # noqa: E402


def verify_html(batch_dir):
    verify_script = os.path.join(ROOT, "scripts", "verify_taxonomy_html.py")
    if not os.path.isfile(verify_script):
        print("  SKIP verify (script not found)", flush=True)
        return 0
    print("\n=== Verify metric differentiation ===", flush=True)
    return subprocess.run(
        [sys.executable, verify_script, "--dir", batch_dir],
        cwd=ROOT,
    ).returncode


def latest_batch_dir(output_root):
    """Report folder keyed by testing type, e.g. taxonomy_reports/Structural Analysis/."""
    from sa_metrics import SA_TESTING_TYPE
    base = os.path.join(ROOT, output_root)
    cls = os.environ.get("REPORT_CLASSIFICATION", SA_TESTING_TYPE)
    path = os.path.join(base, cls)
    return path if os.path.isdir(path) else None


def run_batch(env_file, branches_csv, dry_run, refresh, allow_partial, export_html=True, html_only=True):
    batch_script = os.path.join(ROOT, "scripts", "run_sa_taxonomy_batch.py")
    cmd = [
        sys.executable,
        batch_script,
        "--env-file", env_file,
        "--branches", branches_csv,
    ]
    if dry_run:
        cmd.append("--dry-run")
    if refresh:
        cmd.append("--refresh-branches")
    if allow_partial:
        cmd.append("--allow-partial-branches")
    if export_html:
        cmd.append("--export-html")
    else:
        cmd.append("--no-export-html")
    if html_only:
        cmd.append("--html-only")
    return subprocess.run(cmd, cwd=ROOT)


def pair_validate_metric(env_file, abbrev, version, refresh, allow_partial, skip_html, skip_verify, html_only):
    """Run Bug then BugFX for one metric; validate Bug EPI/target fails before running fix branch."""
    from sa_metrics import branch_name, ABBREV_TO_CLASSIFICATION

    bug_branch = branch_name(abbrev, "Bug", version)
    fix_branch = branch_name(abbrev, "BugFX", version)
    target_cls = ABBREV_TO_CLASSIFICATION[abbrev]

    print("\n=== Pair validation: %s ===" % abbrev, flush=True)
    print("  [1/2] %s (expect %s FAIL)" % (bug_branch, target_cls), flush=True)
    rc = run_batch(env_file, bug_branch, False, refresh, allow_partial,
                   export_html=not skip_html, html_only=html_only)
    if rc.returncode != 0:
        return rc.returncode

    batch_dir = latest_batch_dir(os.environ.get("OUTPUT_DIR", "taxonomy_reports"))
    if batch_dir:
        bug_html = glob_html(batch_dir, bug_branch)
        if bug_html:
            ok, detail = verify_one(bug_html, abbrev, "Bug")
            print(detail)
            if not ok:
                print("STOP: Bug branch did not fail target metric — fix branch code before BugFX run.", flush=True)
                return 1
        else:
            print("WARNING: no HTML for %s — check taxonomy JSON manually" % bug_branch, flush=True)

    print("  [2/2] %s (expect %s PASS/WARN)" % (fix_branch, target_cls), flush=True)
    rc = run_batch(env_file, fix_branch, False, refresh, allow_partial,
                   export_html=not skip_html, html_only=html_only)
    if rc.returncode != 0:
        return rc.returncode
    batch_dir = latest_batch_dir(os.environ.get("OUTPUT_DIR", "taxonomy_reports"))
    if batch_dir and not skip_verify:
        fix_html = glob_html(batch_dir, fix_branch)
        if fix_html:
            ok, detail = verify_one(fix_html, abbrev, "BugFX")
            print(detail)
            if not ok:
                return 1
    return 0


def glob_html(batch_dir, branch_name, latest=True):
    """Find HTML under batch_dir for branch (supports SA_EPI_Bug_2.6_<timestamp> folders)."""
    if not os.path.isdir(batch_dir):
        return None
    prefix = branch_name + "_"
    matches = []
    for name in os.listdir(batch_dir):
        if name != branch_name and not name.startswith(prefix):
            continue
        folder = os.path.join(batch_dir, name)
        if not os.path.isdir(folder):
            continue
        for fn in os.listdir(folder):
            if fn.endswith(".html"):
                matches.append((name, os.path.join(folder, fn)))
    if not matches:
        return None
    matches.sort(key=lambda x: x[0], reverse=True)
    return matches[0][1] if latest else [m[1] for m in matches]


def verify_one(html_path, abbrev, branch_type):
    from verify_taxonomy_html import verify_file
    return verify_file(html_path, abbrev, branch_type)


def main():
    metric_choices = [abbrev for _, abbrev, _, _, _ in SA_METRICS] + ["all"]
    parser = argparse.ArgumentParser(description="(Legacy) Run SA metric taxonomy batch")
    parser.add_argument("--env-file", default=os.path.join(ROOT, ".env.local"))
    parser.add_argument("--metric", choices=metric_choices, default="all")
    parser.add_argument("--branch-types", default="all")
    parser.add_argument("--version", default="2.6")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--refresh-branches", action="store_true")
    parser.add_argument("--allow-partial-branches", action="store_true")
    parser.add_argument("--skip-html", action="store_true")
    parser.add_argument("--keep-intermediate", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    parser.add_argument("--pair-validate", action="store_true")
    args = parser.parse_args()

    cmd = [sys.executable, os.path.join(ROOT, "scripts", "run_sa_taxonomy.py")]
    cmd += ["--env-file", args.env_file, "--metrics", args.metric, "--version", args.version]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.refresh_branches:
        cmd.append("--refresh-branches")
    if args.allow_partial_branches:
        cmd.append("--allow-partial-branches")
    if args.skip_html:
        cmd.append("--skip-html")
    if args.keep_intermediate:
        cmd.append("--keep-intermediate")
    if args.skip_verify:
        cmd.append("--skip-verify")
    if args.pair_validate:
        cmd.append("--pair-validate")
    return subprocess.run(cmd, cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main())
