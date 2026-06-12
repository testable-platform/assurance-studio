#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_qa.py + notebooks/02_run_qa_and_verify.ipynb
"""Download taxonomy reports from existing QA run IDs (no new whitebox runs)."""

from __future__ import print_function

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from run_sa_taxonomy_batch import (  # noqa: E402
    PlatformClient,
    ROOT,
    ensure_dir,
    export_html_reports,
    extract_gate_score,
    fetch_taxonomy,
    get_run_summary,
    load_env,
    login,
    prune_to_html_only,
    resolve_tenant_id,
    save_report,
    wait_for_taxonomy_ready,
)
from sa_metrics import SA_TESTING_TYPE, report_output_dir  # noqa: E402

# Earlier successful EPI batch on QA (taxonomy gate completed)
DEFAULT_EPI_RUNS = {
    "SA_EPI_Bug_2.6": "a747494a-a382-4982-bf19-ad9354a7d828",
    "SA_EPI_BugFX_2.6": "5e2467d3-c064-4325-b9cf-0573e766edf5",
    "SA_EPI_TCC_2.6": "82f5fe2b-04c7-4c6d-80ce-f3f51efb2d7f",
    "SA_EPI_CC_2.6": "4cf8c7a1-f871-4d0b-958e-1f1672f0e8d2",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Collect taxonomy from existing run IDs")
    parser.add_argument("--env-file", default=os.path.join(ROOT, ".env.local"))
    parser.add_argument("--preset", choices=["epi"], help="Built-in run ID map")
    parser.add_argument("--run", action="append", metavar="BRANCH=RUN_ID", help="branch=uuid")
    parser.add_argument("--keep-intermediate", action="store_true", help="Keep JSON/XML files")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env(args.env_file)
    token = login(os.environ["IDENTITY_URL"], os.environ["AUTH_EMAIL"], os.environ["AUTH_PASSWORD"])
    client = PlatformClient(
        os.environ["IDENTITY_URL"],
        os.environ["RUNTIME_URL"],
        os.environ["VIEWS_URL"],
        token,
    )
    tenant_id = resolve_tenant_id(client)

    runs = {}
    if args.preset == "epi":
        runs.update(DEFAULT_EPI_RUNS)
    for item in args.run or []:
        branch, _, run_id = item.partition("=")
        runs[branch.strip()] = run_id.strip()

    if not runs:
        print("No runs specified. Use --preset epi or --run BRANCH=RUN_ID", file=sys.stderr)
        return 1

    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = os.environ.get("OUTPUT_DIR", "taxonomy_reports")
    classification = os.environ.get("REPORT_CLASSIFICATION", SA_TESTING_TYPE)
    output_dir = os.path.join(ROOT, report_output_dir(output_root, classification))
    ensure_dir(output_dir)
    poll = int(os.environ.get("POLL_INTERVAL_SEC", "10"))
    timeout = int(os.environ.get("TAXONOMY_POLL_TIMEOUT_SEC", "120"))
    manifest = {
        "batch_id": batch_id,
        "classification": classification,
        "tenant_id": tenant_id,
        "runs": [],
    }

    for branch, run_id in sorted(runs.items()):
        print("Collecting %s (%s)..." % (branch, run_id), flush=True)
        summary = get_run_summary(client, run_id, tenant_id)
        taxonomy_json = wait_for_taxonomy_ready(client, run_id, tenant_id, poll, timeout)
        _, taxonomy_xml = fetch_taxonomy(client, run_id, tenant_id)
        report_folder = save_report(output_dir, branch, run_id, summary, taxonomy_json, taxonomy_xml)
        entry = {
            "branch": branch,
            "report_folder": report_folder,
            "run_id": run_id,
            "status": summary.get("status"),
            "gate_score": extract_gate_score(taxonomy_json),
        }
        manifest["runs"].append(entry)
        print("  saved gate_score=%s" % entry["gate_score"], flush=True)

    with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    if export_html_reports(output_dir):
        if not args.keep_intermediate:
            prune_to_html_only(output_dir)
    else:
        print("WARNING: HTML export failed — JSON kept in %s" % output_dir, flush=True)
        return 1

    print("\nReports: %s" % output_dir)
    for branch in runs:
        prefix = branch + "_"
        for name in sorted(os.listdir(output_dir)):
            if name == branch or name.startswith(prefix):
                folder = os.path.join(output_dir, name)
                if not os.path.isdir(folder):
                    continue
                for fn in os.listdir(folder):
                    if fn.endswith(".html"):
                        print("  %s" % os.path.join(folder, fn))
    return 0


if __name__ == "__main__":
    sys.exit(main())
