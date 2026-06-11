#!/usr/bin/env python3
"""Collect taxonomy reports from existing run IDs (no new whitebox runs)."""

from __future__ import print_function

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from scripts.run_sa_taxonomy_batch import (  # noqa: E402
    PlatformClient,
    ensure_dir,
    extract_gate_score,
    fetch_taxonomy,
    get_run_summary,
    load_env,
    login,
    save_report,
    wait_for_taxonomy_ready,
)

# From batch 20260611T103648Z
DEFAULT_RUNS = {
    "SA_bug_2.6": "98f42ce3-5367-4eaa-9355-68a91233e6e8",
    "SA_bugFX_2.6": "b17c6185-fa8b-4fb0-bf6a-899eb57cac91",
    "SA_TCC_2.6": "94682dc3-0eec-4fb7-8a1f-2908b8b37c3e",
    "SA_CC_2.6": "a3ce10c7-15fe-4892-9d88-81c4bbb101c6",
}


def main():
    load_env(os.path.join(ROOT, ".env.local"))
    tenant_id = os.environ["TENANT_ID"]
    output_dir = os.path.join(ROOT, os.environ.get("OUTPUT_DIR", "taxonomy_reports"), "20260611T103648Z-collected")
    ensure_dir(output_dir)

    token = login(
        os.environ["IDENTITY_URL"],
        os.environ["AUTH_EMAIL"],
        os.environ["AUTH_PASSWORD"],
    )
    client = PlatformClient(
        os.environ["IDENTITY_URL"],
        os.environ["RUNTIME_URL"],
        os.environ["VIEWS_URL"],
        token,
    )

    manifest = {"runs": []}
    poll_interval = int(os.environ.get("POLL_INTERVAL_SEC", "10"))
    taxonomy_timeout = int(os.environ.get("TAXONOMY_POLL_TIMEOUT_SEC", "120"))

    for branch, run_id in DEFAULT_RUNS.items():
        print("Collecting %s (%s)..." % (branch, run_id), flush=True)
        summary = get_run_summary(client, run_id, tenant_id)
        taxonomy_json = wait_for_taxonomy_ready(
            client, run_id, tenant_id, poll_interval, taxonomy_timeout)
        _, taxonomy_xml = fetch_taxonomy(client, run_id, tenant_id)
        save_report(output_dir, branch, run_id, summary, taxonomy_json, taxonomy_xml)
        manifest["runs"].append({
            "branch": branch,
            "run_id": run_id,
            "status": summary.get("status"),
            "gate_score": extract_gate_score(taxonomy_json),
        })
        print("  saved gate_score=%s" % manifest["runs"][-1]["gate_score"], flush=True)

    with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    html_script = os.path.join(ROOT, "scripts", "export_taxonomy_html.ts")
    web_console = os.environ.get(
        "WEB_CONSOLE_DIR",
        os.path.join(os.path.dirname(ROOT), "ai-testable-platform", "frontend", "web-console"),
    )
    if os.path.isfile(html_script) and os.path.isdir(web_console):
        import subprocess
        print("Generating HTML reports (UI download format)...", flush=True)
        subprocess.run(
            [
                "npx", "--yes", "tsx", "--tsconfig", "tsconfig.json",
                html_script, output_dir,
            ],
            cwd=web_console,
            check=False,
        )
    print("Done:", output_dir)


if __name__ == "__main__":
    main()
