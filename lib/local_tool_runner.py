"""Run registry primary tools locally and emit standard tool reports."""

from __future__ import print_function

import os
import subprocess
import sys

from lib.registry import iter_branches
from lib.report_schema import from_tool_assert_result, save_report
from lib.tool_map import pip_packages_for_family, python_tool
from lib.tool_assert import _branch_context

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

FAMILY_PACKAGES = {
    "coverage": ["coverage", "pytest"],
    "crosshair": ["coverage", "pytest"],
    "pymcdc": ["coverage", "pytest"],
    "complexity": ["radon"],
    "lint": ["flake8", "pylint"],
    "security": ["bandit"],
    "sca": ["pip-audit"],
    "mutation": ["mutmut"],
    "churn": ["pydriller"],
    "duplication": [],
    "testmon": ["pytest"],
}


def _python_module_available(module):
    try:
        subprocess.run(
            [sys.executable, "-c", "import %s" % module.replace("-", "_")],
            capture_output=True,
            timeout=15,
            check=False,
        )
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False


def ensure_tool_installed(technique_code, metric_code, language="python"):
    """Install pip packages required for the metric's primary tool family."""
    if language != "python":
        return False, "only python supported"
    info = python_tool(technique_code, metric_code)
    packages = pip_packages_for_family(info["family"], info["primary"])
    if not packages:
        return True, "no pip packages required for family %s" % info["family"]

    missing = []
    for pkg in packages:
        mod = pkg.replace("-", "_")
        if pkg == "pip-audit":
            mod = "pip_audit"
        if not _python_module_available(mod):
            missing.append(pkg)

    if not missing:
        return True, "tools available"

    cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + missing
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=False)
        if proc.returncode != 0:
            return False, (proc.stderr or proc.stdout or "pip install failed").strip()
        return True, "installed: %s" % ", ".join(missing)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


def run_local_tool_report(
    branch_path,
    technique_code=None,
    metric_code=None,
    branch_type=None,
    version=None,
    language="python",
    commit_sha=None,
    run_id=None,
    install=True,
):
    """Execute local tool for one branch and return a standard report dict."""
    from lib.tool_assert import tool_assert_branch

    folder = os.path.basename(os.path.normpath(branch_path))
    from lib.metrics import parse_branch_name

    parsed = parse_branch_name(folder)
    if not parsed:
        raise ValueError("unparseable branch folder: %s" % folder)

    technique_code = (technique_code or parsed["tech"]).upper()
    metric_code = (metric_code or parsed["metric"]).upper()
    branch_type = branch_type or parsed["type"]
    version = version or parsed["version"]

    if install:
        ok, msg = ensure_tool_installed(technique_code, metric_code, language)
        if not ok:
            from lib.report_schema import make_report

            return make_report(
                technique_code=technique_code,
                metric_code=metric_code,
                branch_name=folder,
                branch_type=branch_type,
                version=version,
                tool_name="",
                source="local",
                status="ERROR",
                raw_summary=msg,
                commit_sha=commit_sha,
                run_id=run_id,
                extra={"install_error": msg},
            )

    assert_result = tool_assert_branch(
        branch_path, technique_code, metric_code, branch_type, language
    )
    return from_tool_assert_result(
        assert_result,
        source="local",
        commit_sha=commit_sha,
        run_id=run_id,
        version=version,
    )


def run_local_tool_batch(
    techniques="all",
    metrics="all",
    types=None,
    version="2.6",
    language="python",
    build_dir="build",
    output_dir="proofs",
    root=None,
    install=True,
    commit_sha_by_branch=None,
    run_id_by_branch=None,
):
    """Run local tools for selected branches; write standard reports under proofs/."""
    repo_root = root or ROOT
    commit_sha_by_branch = commit_sha_by_branch or {}
    run_id_by_branch = run_id_by_branch or {}
    reports = []

    for tech, metric, bt, bname in iter_branches(techniques, metrics, types, version):
        branch_path = os.path.join(repo_root, build_dir, bname)
        report = run_local_tool_report(
            branch_path,
            tech,
            metric,
            bt,
            version,
            language,
            commit_sha=commit_sha_by_branch.get(bname, ""),
            run_id=run_id_by_branch.get(bname, ""),
            install=install,
        )
        out_path = os.path.join(
            repo_root, output_dir, tech, bname, "local_report.json"
        )
        save_report(report, out_path)
        report["_path"] = out_path
        reports.append(report)

    return reports


def default_report_path(root, technique_code, branch_name, source="local"):
    filename = "%s_report.json" % source
    return os.path.join(root, "proofs", technique_code, branch_name, filename)
