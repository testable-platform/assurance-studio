#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_generator.py + notebooks/01_generate_and_validate.ipynb
"""Generate metric-scoped SA branches (e.g. SA_EPI_Bug_2.6, SA_EPI_BugFX_2.6, ...)."""

from __future__ import print_function

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from lib.sa_generator import count_loc, generate_branch_files, write_branch  # noqa: E402
from sa_metrics import BRANCH_TYPES, SA_METRICS, branch_name  # noqa: E402


def generate_metric(root, abbrev, branch_type="Bug", version="2.6", language="python"):
    bname, loc = write_branch(root, abbrev, branch_type, version, language)
    print("Generated %s (target=%s, type=%s, %d counted lines)" % (bname, abbrev, branch_type, loc))
    return bname


def main():
    parser = argparse.ArgumentParser(description="Generate metric-scoped SA branches")
    parser.add_argument(
        "--metric",
        choices=[abbrev for _, abbrev, _, _, _ in SA_METRICS] + ["all"],
        default="all",
    )
    parser.add_argument(
        "--branch-type",
        choices=list(BRANCH_TYPES) + ["all"],
        default="all",
        help="Bug, BugFX, TCC, CC, or all",
    )
    parser.add_argument("--version", default="2.6")
    parser.add_argument("--language", default="python")
    parser.add_argument("--out", default="build")
    args = parser.parse_args()

    abbrevs = [a for _, a, _, _, _ in SA_METRICS] if args.metric == "all" else [args.metric]
    branch_types = list(BRANCH_TYPES) if args.branch_type == "all" else [args.branch_type]
    for abbrev in abbrevs:
        for bt in branch_types:
            bname = branch_name(abbrev, bt, args.version)
            generate_metric(
                os.path.join(args.out, bname),
                abbrev,
                branch_type=bt,
                version=args.version,
                language=args.language,
            )


if __name__ == "__main__":
    main()
