#!/usr/bin/env python3
# ARCHIVED: superseded by lib/sa_generator.py + notebooks/01_generate_and_validate.ipynb
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KEEP = {".git", "build", "scripts", ".gitignore"}


def clean():
    for name in os.listdir(ROOT):
        if name in KEEP:
            continue
        path = os.path.join(ROOT, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def deploy(branch):
    subprocess.check_call(["git", "checkout", "-B", branch, "main"], cwd=ROOT)
    clean()
    src = os.path.join(ROOT, "build", branch)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(ROOT, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    with open(os.path.join(ROOT, ".gitignore"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("build/\n__pycache__/\n*.pyc\n*.pyo\n.env\n.env.local\ntaxonomy_reports/\n")
    paths = []
    for candidate in [".gitignore", "README.md", "main.py", "requirements.txt", "versions.txt", "sa", "tests", ".coveragerc", ".testmondata.ini", "pytest.ini", "setup.cfg"]:
        if os.path.exists(os.path.join(ROOT, candidate)):
            paths.append(candidate)
    subprocess.check_call(["git", "add"] + paths, cwd=ROOT)
    subprocess.check_call(
        ["git", "commit", "-m", "Expand Structural Analysis Python 2.6 complexity for %s" % branch],
        cwd=ROOT,
    )


if __name__ == "__main__":
    deploy(sys.argv[1])
