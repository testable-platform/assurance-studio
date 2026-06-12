#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_qa.py + notebooks/02_run_qa_and_verify.ipynb
"""
Run SA metric branches on Testable QA and save taxonomy gate HTML reports.

Always runs the four fixed branch types per metric: Bug, BugFX, TCC, CC.

Reports accumulate under:
  taxonomy_reports/Structural Analysis/<branch>_<UTC timestamp>/

Usage:
  py -3 scripts/run_sa_taxonomy.py --metric all --refresh-branches
  py -3 scripts/run_sa_taxonomy.py --metrics EPI,DOV --version 2.6
  py -3 scripts/run_sa_taxonomy.py --interactive
  py -3 scripts/run_sa_taxonomy.py --dry-run --metric all
"""

from __future__ import print_function

import argparse
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from sa_metrics import (  # noqa: E402
    FIXED_BRANCH_TYPES,
    METRIC_ABBREVS,
    SA_TESTING_TYPE,
    branches_for_metrics,
    parse_metrics_arg,
)


def prompt(label, default):
    try:
        val = input("%s [%s]: " % (label, default)).strip()
    except EOFError:
        val = ""
    return val or default


def interactive_args():
    print("=== SA taxonomy execution (types: %s) ===" % ", ".join(FIXED_BRANCH_TYPES))
    version = prompt("Branch version suffix", "2.6")
    print("Metrics: %s" % ", ".join(METRIC_ABBREVS))
    metrics = prompt("Metrics (comma-separated or all)", "all")
    refresh = prompt("Refresh branches on platform before run? (y/n)", "y").lower().startswith("y")
    dry = prompt("Dry run only? (y/n)", "n").lower().startswith("y")
    return argparse.Namespace(
        env_file=os.path.join(ROOT, ".env.local"),
        metrics=metrics,
        version=version,
        dry_run=dry,
        refresh_branches=refresh,
        allow_partial_branches=False,
        skip_html=False,
        keep_intermediate=False,
        skip_verify=False,
        pair_validate=False,
    )


def load_output_dir_from_env(env_file):
    if os.path.isfile(env_file):
        with open(env_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("OUTPUT_DIR="):
                    os.environ.setdefault("OUTPUT_DIR", line.split("=", 1)[1].strip())


def latest_batch_dir(output_root):
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run SA metric branches on Testable and collect taxonomy reports",
    )
    parser.add_argument("--env-file", default=os.path.join(ROOT, ".env.local"))
    parser.add_argument(
        "--metrics",
        "--metric",
        dest="metrics",
        default="all",
        help="Comma-separated abbrevs (EPI,DOV,...) or all (default: all six metrics)",
    )
    parser.add_argument("--version", default="2.6", help="Branch version suffix (default: 2.6)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--refresh-branches", action="store_true")
    parser.add_argument("--allow-partial-branches", action="store_true")
    parser.add_argument("--skip-html", action="store_true", help="Do not export HTML after batch")
    parser.add_argument(
        "--keep-intermediate",
        action="store_true",
        help="Keep JSON/XML files (default: HTML-only in taxonomy_reports)",
    )
    parser.add_argument("--skip-verify", action="store_true", help="Do not run HTML verification")
    parser.add_argument(
        "--pair-validate",
        action="store_true",
        help="For each metric: run Bug, verify FAIL, then BugFX and verify PASS",
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="Prompt for metrics and options")
    return parser.parse_args()


def pair_validate_metrics(env_file, metrics, version, refresh, allow_partial, skip_html, skip_verify, html_only):
    from run_sa_metric_taxonomy_batch import pair_validate_metric

    for abbrev in parse_metrics_arg(metrics):
        rc = pair_validate_metric(
            env_file, abbrev, version,
            refresh, allow_partial,
            skip_html, skip_verify, html_only,
        )
        if rc != 0:
            return rc
    print("\n=== Pair validation complete ===", flush=True)
    return 0


def main():
    args = parse_args()
    if args.interactive:
        args = interactive_args()

    load_output_dir_from_env(args.env_file)
    html_only = not args.keep_intermediate

    if args.pair_validate:
        return pair_validate_metrics(
            args.env_file, args.metrics, args.version,
            args.refresh_branches, args.allow_partial_branches,
            args.skip_html, args.skip_verify, html_only,
        )

    branches = branches_for_metrics(args.metrics, args.version)
    branches_csv = ",".join(branches)

    print("=== SA taxonomy execution ===", flush=True)
    print("  metrics: %s" % args.metrics, flush=True)
    print("  version: %s" % args.version, flush=True)
    print("  types:   %s (fixed)" % ", ".join(FIXED_BRANCH_TYPES), flush=True)
    print("  count:   %d branches" % len(branches), flush=True)
    for i, name in enumerate(branches, 1):
        print("    %2d. %s" % (i, name))

    print("\n=== Starting whitebox runs ===", flush=True)
    result = run_batch(
        args.env_file, branches_csv, args.dry_run,
        args.refresh_branches, args.allow_partial_branches,
        export_html=not args.skip_html,
        html_only=html_only,
    )
    if result.returncode != 0:
        return result.returncode

    if args.dry_run:
        return 0

    batch_dir = latest_batch_dir(os.environ.get("OUTPUT_DIR", "taxonomy_reports"))
    if not batch_dir:
        print("WARNING: no batch output directory found", flush=True)
        return 0

    print("\n  batch output: %s" % batch_dir, flush=True)

    if not args.skip_verify:
        verify_rc = verify_html(batch_dir)
        if verify_rc != 0:
            print("\nWARNING: verification reported issues (see above)", flush=True)

    print("\n=== Taxonomy execution complete ===", flush=True)
    print("  reports: %s" % batch_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
