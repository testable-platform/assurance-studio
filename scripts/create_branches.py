#!/usr/bin/env python3
"""Create SA_* git branches with isolated codebases."""

from __future__ import print_function

import os
import shutil
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRANCHES = ["SA_bug_2.6", "SA_bugFX_2.6", "SA_TCC_2.6", "SA_CC_2.6"]
KEEP = {".git", "build", "scripts", ".gitignore"}


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
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(ROOT, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    run(["git", "add", ".gitignore", "README.md", "main.py", "requirements.txt", "versions.txt", "sa", "tests", ".coveragerc", ".testmondata.ini", "pytest.ini", "setup.cfg"])
    run(["git", "commit", "-m", "Add Structural Analysis Python 2.6 codebase for %s" % branch])


def main():
    for branch in BRANCHES:
        run(["git", "checkout", "-B", branch, "main"])
        deploy_branch(branch)
    run(["git", "checkout", "main"])
    print("Created branches:", ", ".join(BRANCHES))


if __name__ == "__main__":
    main()
