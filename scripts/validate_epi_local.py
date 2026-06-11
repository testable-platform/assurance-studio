#!/usr/bin/env python3
"""Local Radon check: SA_EPI_Bug should score EPI < 14, BugFX should score >= 28."""

from __future__ import print_function

import os
import subprocess
import sys
import tempfile
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _execution_path_integrity_percent(avg_ccn):
    if avg_ccn <= 10:
        bucket = 10.0
    elif avg_ccn <= 20:
        bucket = 7.0
    elif avg_ccn <= 50:
        bucket = 4.0
    else:
        bucket = 1.0
    return (bucket / 10.0) * 100.0


def _norm_higher_better(raw, threshold=28.0):
    return max(0.0, min(100.0, (raw / threshold) * 100.0))


def _outcome(norm):
    if norm > 75:
        return "pass"
    if norm >= 50:
        return "warn"
    return "fail"


def radon_avg_cc(sa_dir):
    out = subprocess.check_output(
        [sys.executable, "-m", "radon", "cc", sa_dir, "-a", "-s"],
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in reversed(out.splitlines()):
        if line.startswith("Average complexity:"):
            part = line.split("(", 1)[1].rstrip(")")
            return float(part)
    raise RuntimeError("Could not parse radon output:\n" + out)


def check_branch(branch_name):
    tmp = tempfile.mkdtemp(prefix="epi_check_")
    try:
        subprocess.check_call(
            ["git", "archive", branch_name, "sa"],
            cwd=ROOT,
            stdout=open(os.path.join(tmp, "sa.tar"), "wb"),
        )
        subprocess.check_call(["tar", "-xf", "sa.tar"], cwd=tmp)
        avg = radon_avg_cc(os.path.join(tmp, "sa"))
        epi_raw = _execution_path_integrity_percent(avg)
        norm = _norm_higher_better(epi_raw)
        outcome = _outcome(norm)
        return {"branch": branch_name, "avg_ccn": avg, "epi_raw": epi_raw, "norm": norm, "outcome": outcome}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    bug = check_branch("SA_EPI_Bug_2.6")
    fix = check_branch("SA_EPI_BugFX_2.6")
    ok = True
    print("EPI local Radon simulation (no Crosshair):")
    for row in (bug, fix):
        print("  %(branch)s: avg_ccn=%(avg_ccn).2f epi_raw=%(epi_raw).1f norm=%(norm).1f => %(outcome)s" % row)
    if bug["outcome"] != "fail":
        print("FAIL: SA_EPI_Bug_2.6 should produce EPI fail (got %s)" % bug["outcome"])
        ok = False
    else:
        print("OK: Bug branch EPI fails as expected")
    if fix["outcome"] == "fail":
        print("FAIL: SA_EPI_BugFX_2.6 should not fail EPI (got fail)")
        ok = False
    else:
        print("OK: BugFX branch EPI passes/warns as expected")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
