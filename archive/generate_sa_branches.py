#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_generator.py + notebooks/01_generate_and_validate.ipynb
"""
Generate SA metric branch codebases (and optionally create git branches).

Branch types are fixed: Bug, BugFX, TCC, CC (always all four per metric).

Usage:
  py -3 scripts/generate_sa_branches.py --version 2.6 --language python --metrics all
  py -3 scripts/generate_sa_branches.py --metrics EPI,DOV --git
  py -3 scripts/generate_sa_branches.py --interactive
"""

from __future__ import print_function

import argparse
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from create_metric_branches import create_git_branches  # noqa: E402
from generate_sa_metric_codebase import generate_metric  # noqa: E402
from validate_sa_branch import BranchValidationError, validate_build  # noqa: E402
from sa_metrics import (  # noqa: E402
    FIXED_BRANCH_TYPES,
    METRIC_ABBREVS,
    SUPPORTED_LANGUAGES,
    branch_name,
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
    print("=== SA branch generation (types: %s) ===" % ", ".join(FIXED_BRANCH_TYPES))
    version = prompt("Python/runtime version (branch suffix)", "2.6")
    language = prompt("Language", "python").lower()
    if language not in SUPPORTED_LANGUAGES:
        print("WARNING: language %r not in %s — continuing anyway" % (language, SUPPORTED_LANGUAGES))
    print("Metrics: %s" % ", ".join(METRIC_ABBREVS))
    metrics = prompt("Metrics (comma-separated or all)", "all")
    git = prompt("Create git branches after build? (y/n)", "n").lower().startswith("y")
    push = False
    if git:
        push = prompt("Push to origin? (y/n)", "n").lower().startswith("y")
    return argparse.Namespace(
        version=version,
        language=language,
        metrics=metrics,
        out="build",
        git=git,
        push=push,
    )


def generate_build(metrics, version, language, out_dir):
    abbrevs = parse_metrics_arg(metrics)
    names = []
    for abbrev in abbrevs:
        for bt in FIXED_BRANCH_TYPES:
            bname = branch_name(abbrev, bt, version)
            root = os.path.join(ROOT, out_dir, bname)
            generate_metric(root, abbrev, branch_type=bt, version=version, language=language)
            names.append(bname)
    return names


def push_branches(branch_names):
    for name in branch_names:
        subprocess.check_call(["git", "push", "-u", "origin", name, "--force"], cwd=ROOT)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate SA metric branches (Bug, BugFX, TCC, CC per metric)",
    )
    parser.add_argument(
        "--version",
        default="2.6",
        help="Runtime version suffix in branch name, e.g. SA_EPI_Bug_2.6 (default: 2.6)",
    )
    parser.add_argument(
        "--language",
        default="python",
        choices=list(SUPPORTED_LANGUAGES),
        help="Source language (default: python)",
    )
    parser.add_argument(
        "--metrics",
        default="all",
        help="Comma-separated metric abbrevs (EPI,DOV,...) or all (default: all six)",
    )
    parser.add_argument("--out", default="build", help="Output directory (default: build)")
    parser.add_argument(
        "--git",
        action="store_true",
        help="Create git branches from build/ and commit on each branch",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="After --git, force-push branches to origin (use with care)",
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="Prompt for version, language, metrics")
    parser.add_argument("--skip-validate", action="store_true", help="Skip post-generation assert validation")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.interactive:
        args = interactive_args()

    names = branches_for_metrics(args.metrics, args.version)
    print("=== Generate SA branches ===")
    print("  language: %s" % args.language)
    print("  version:  %s" % args.version)
    print("  metrics:  %s" % args.metrics)
    print("  types:    %s (fixed)" % ", ".join(FIXED_BRANCH_TYPES))
    print("  count:    %d branches" % len(names))
    for i, n in enumerate(names, 1):
        print("    %2d. %s" % (i, n))

    generate_build(args.metrics, args.version, args.language, args.out)
    print("\nBuild output: %s" % os.path.join(ROOT, args.out))

    if not args.skip_validate:
        print("\n=== Assert validation (Bug / BugFX / TCC / CC) ===")
        try:
            results = validate_build(
                args.metrics, args.version, args.language, args.out, ROOT)
        except BranchValidationError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        for name, bt in results:
            print("  OK  %s  [%s]" % (name, bt))
        print("  All %d branches passed type-specific asserts." % len(results))

    if args.git:
        print("\n=== Create git branches ===")
        create_git_branches(args.metrics, args.version, args.language)
        if args.push:
            print("\n=== Push to origin ===")
            push_branches(names)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
