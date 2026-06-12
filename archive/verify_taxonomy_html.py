#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_qa.py + notebooks/02_run_qa_and_verify.ipynb
"""Cross-verify taxonomy HTML for metric-scoped SA branches.

Bug:     target classification should FAIL; others should not FAIL.
BugFX/TCC/CC: target classification should PASS or WARN (not FAIL).
"""

from __future__ import print_function

import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from sa_metrics import (  # noqa: E402
    ABBREV_TO_CLASSIFICATION,
    SA_METRICS,
    branch_name_from_report_folder,
    infer_metric_from_report_folder,
)

CLASSIFICATION_TO_ABBREV = {cls: abbrev for _, abbrev, cls, _, _ in SA_METRICS}

ROW_RE = re.compile(
    r'<div class="cls-name">([^<]+)</div>.*?'
    r'<td class="result-em"><span class="rp rp-(\w+)">',
    re.DOTALL,
)


def parse_sa_results(html):
    sa_start = html.find("<h2>Structural Analysis</h2>")
    if sa_start < 0:
        return {}
    section = html[sa_start:]
    cyclo_start = section.find("<h3>Cyclomatic Complexity</h3>")
    if cyclo_start < 0:
        return {}
    section = section[cyclo_start:]
    next_h2 = section.find("<h2>", 1)
    if next_h2 > 0:
        section = section[:next_h2]
    return {name.strip(): result.strip().lower() for name, result in ROW_RE.findall(section)}


def infer_from_folder(path):
    folder = os.path.basename(os.path.dirname(path))
    abbrev, branch_type = infer_metric_from_report_folder(folder)
    if abbrev and branch_type:
        return abbrev, branch_type
    base = branch_name_from_report_folder(folder)
    parts = base.split("_")
    if len(parts) >= 3 and parts[0] == "SA":
        return parts[1], parts[2]
    return None, None


def verify_file(html_path, target_abbrev, branch_type):
    with open(html_path, encoding="utf-8") as fh:
        html = fh.read()
    results = parse_sa_results(html)
    if not results:
        return False, "Structural Analysis / Cyclomatic Complexity section not found"

    target_cls = ABBREV_TO_CLASSIFICATION[target_abbrev]
    expect_target_fail = branch_type == "Bug"
    lines = []
    ok = True

    for cls, abbrev in sorted(CLASSIFICATION_TO_ABBREV.items(), key=lambda x: x[1]):
        result = results.get(cls, "missing")
        is_target = abbrev == target_abbrev
        if is_target:
            if expect_target_fail:
                if result != "fail":
                    ok = False
                    lines.append("  TARGET %s (%s): %s (expected FAIL)" % (abbrev, cls, result.upper()))
                else:
                    lines.append("  TARGET %s (%s): FAIL (ok)" % (abbrev, cls))
            else:
                if result == "fail":
                    ok = False
                    lines.append("  TARGET %s (%s): FAIL (expected PASS/WARN after fix)" % (abbrev, cls))
                else:
                    lines.append("  TARGET %s (%s): %s (ok)" % (abbrev, cls, result.upper()))
        else:
            if result == "fail" and branch_type == "Bug":
                lines.append("  note   %s (%s): FAIL (non-target; check tool defaults)" % (abbrev, cls))
            else:
                lines.append("  other  %s (%s): %s" % (abbrev, cls, result.upper()))

    return ok, "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Verify taxonomy HTML metric differentiation")
    parser.add_argument("html", nargs="*", help="taxonomy-gate-*.html files")
    parser.add_argument("--dir", help="Scan branch subfolders under batch directory")
    args = parser.parse_args()

    paths = list(args.html)
    if args.dir:
        for name in sorted(os.listdir(args.dir)):
            folder = os.path.join(args.dir, name)
            if not os.path.isdir(folder):
                continue
            for fn in os.listdir(folder):
                if fn.endswith(".html"):
                    paths.append(os.path.join(folder, fn))

    if not paths:
        print("No HTML files found.", file=sys.stderr)
        return 1

    failed = 0
    for path in paths:
        abbrev, branch_type = infer_from_folder(path)
        if not abbrev or not branch_type:
            print("%s: cannot infer metric/type from folder name" % path)
            failed += 1
            continue
        ok, detail = verify_file(path, abbrev, branch_type)
        print("\n%s (target=%s, type=%s) %s" % (path, abbrev, branch_type, "PASS" if ok else "FAIL"))
        print(detail)
        if not ok:
            failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
