#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_generator.py + notebooks/01_generate_and_validate.ipynb
"""Create all metric-scoped SA git branches (Bug, BugFX, TCC, CC × 6 metrics)."""

from __future__ import print_function

import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from sa_metrics import FIXED_BRANCH_TYPES, branch_name, parse_metrics_arg  # noqa: E402

KEEP = {".git", "build", "scripts", ".gitignore", ".env.local"}


def run(cmd, cwd=ROOT):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def clean_worktree():
    for name in os.listdir(ROOT):
        if name in KEEP:
            continue
        path = os.path.join(ROOT, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def deploy_branch(branch):
    clean_worktree()
    src = os.path.join(ROOT, "build", branch)
    if not os.path.isdir(src):
        raise RuntimeError("Missing build output: %s (run generate_sa_metric_codebase.py first)" % src)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(ROOT, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    add_paths = ["sa", "tests", "README.md", "main.py", "requirements.txt", "versions.txt"]
    for optional in (".coveragerc", ".testmondata.ini", "pytest.ini", "setup.cfg"):
        if os.path.exists(os.path.join(ROOT, optional)):
            add_paths.append(optional)
    run(["git", "add", "-A"] + add_paths)
    run(["git", "commit", "-m", "Add metric-scoped SA %s codebase" % branch])


def create_git_branches(metrics="all", version="2.6", language="python"):
    """Create git branches for metrics × fixed types (Bug, BugFX, TCC, CC)."""
    branches = []
    for abbrev in parse_metrics_arg(metrics):
        for bt in FIXED_BRANCH_TYPES:
            branches.append(branch_name(abbrev, bt, version))
    for branch in branches:
        run(["git", "checkout", "-B", branch, "main"])
        deploy_branch(branch)
    run(["git", "checkout", "main"])
    print("Created %d branches (%s, version %s, language %s)" % (
        len(branches), metrics, version, language))
    return branches


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Create git branches from build/ output")
    parser.add_argument("--metrics", default="all")
    parser.add_argument("--version", default="2.6")
    parser.add_argument("--language", default="python")
    args = parser.parse_args()
    create_git_branches(args.metrics, args.version, args.language)


if __name__ == "__main__":
    main()
