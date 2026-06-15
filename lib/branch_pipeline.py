"""Sequential per-branch generate -> validate -> fix -> GitHub API push."""

from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile

from lib.branch_asserts import assert_branch_full
from lib.github_api import push_branch_to_github
from lib.github_auth import check_app_repo_access
from lib.python_generator import generate_branch_files, write_branch
from lib.registry import iter_branches
from lib.tool_map import pip_packages_for_family, python_tool


def _failure_detail(assert_row):
    if not assert_row:
        return "validation failed"
    parts = []
    for key in ("structure", "tool_support", "metric_behavior"):
        if assert_row.get(key) not in ("PASS",):
            parts.append("%s=%s" % (key, assert_row.get(key)))
    for msg in assert_row.get("messages") or []:
        parts.append(msg)
    return "; ".join(parts) if parts else "overall=%s" % assert_row.get("overall")


def _result_row(bname, tech, metric, bt, attempts, assert_row, pushed, failure=""):
    row = {
        "branch_name": bname,
        "technique_code": tech,
        "metric_code": metric,
        "branch_type": bt,
        "attempts": attempts,
        "pushed": pushed,
        "failure_reason": failure,
    }
    if assert_row:
        row.update({
            "structure": assert_row.get("structure"),
            "tool_support": assert_row.get("tool_support"),
            "metric_behavior": assert_row.get("metric_behavior"),
            "overall": assert_row.get("overall"),
            "messages": "; ".join(assert_row.get("messages") or []),
        })
    else:
        row.update({
            "structure": "—",
            "tool_support": "—",
            "metric_behavior": "—",
            "overall": "FAIL",
            "messages": failure,
        })
    return row


def _install_packages(packages):
    if not packages:
        return False, "no packages to install"
    cmd = [sys.executable, "-m", "pip", "install", "-q"] + list(packages)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=False)
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "pip install failed").strip()
            return False, detail[:500]
        return True, "installed: %s" % ",".join(packages)
    except Exception as exc:
        return False, str(exc)


def _fix_branch(tech, metric, bt, version, language, branch_path, auto_install):
    """Regenerate one branch in *branch_path* and optionally install tools."""
    write_branch(branch_path, tech, metric, bt, version, language)
    notes = ["regenerated"]
    if not auto_install:
        return "; ".join(notes)

    info = python_tool(tech, metric)
    family = info["family"]
    if family == "unknown":
        return "; ".join(notes)

    pkgs = pip_packages_for_family(family, info["primary"])
    ok, msg = _install_packages(pkgs)
    notes.append(msg if ok else "install failed: %s" % msg)
    return "; ".join(notes)


def process_branches_sequentially(
    techniques,
    metrics,
    types,
    version,
    language,
    repo_root,
    github_config=None,
    max_fix_attempts=2,
    auto_install=True,
    progress_callback=None,
):
    """Process each branch: ephemeral validate, then push via GitHub API."""
    repo_root = os.path.abspath(repo_root)
    if not github_config or not github_config.get("token") or not github_config.get("repo_slug"):
        return {
            "rows": [],
            "completed": [],
            "stopped_at": None,
            "stop_reason": "GitHub not configured",
            "success": False,
            "needs_install": False,
            "total": 0,
        }

    token = github_config["token"]
    repo_slug = github_config["repo_slug"]
    base_branch = (github_config.get("default_branch") or "main").strip() or "main"
    push_login = github_config.get("login", "")

    ok, needs_install, access_msg = check_app_repo_access(token, repo_slug)
    if not ok:
        return {
            "rows": [],
            "completed": [],
            "stopped_at": None,
            "stop_reason": access_msg,
            "success": False,
            "needs_install": needs_install,
            "total": 0,
        }

    planned = list(iter_branches(techniques, metrics, types, version))
    total = len(planned)
    rows = []
    completed = []
    stopped_at = None
    stop_reason = None

    for idx, (tech, metric, bt, bname) in enumerate(planned, start=1):
        tmp_root = tempfile.mkdtemp(prefix="branch_")
        tmp = os.path.join(tmp_root, bname)

        def _progress(step, msg):
            if progress_callback:
                progress_callback(step, idx - 1, total, bname, msg)

        try:
            _progress("generate", "generating in memory")
            try:
                write_branch(tmp, tech, metric, bt, version, language)
            except Exception as exc:
                row = _result_row(bname, tech, metric, bt, 0, None, False, "generate failed: %s" % exc)
                rows.append(row)
                stopped_at = bname
                stop_reason = row["failure_reason"]
                break

            attempts = 0
            assert_row = assert_branch_full(tmp, tech, metric, bt, version, language)
            _progress("assert", assert_row.get("overall", "?"))

            while assert_row.get("overall") == "FAIL" and attempts < max_fix_attempts:
                attempts += 1
                _progress("fix", "fix attempt %d/%d" % (attempts, max_fix_attempts))
                _fix_branch(tech, metric, bt, version, language, tmp, auto_install)
                assert_row = assert_branch_full(tmp, tech, metric, bt, version, language)
                _progress("assert", assert_row.get("overall", "?"))

            overall = assert_row.get("overall")
            if overall == "FAIL":
                reason = _failure_detail(assert_row)
                row = _result_row(bname, tech, metric, bt, attempts + 1, assert_row, False, reason)
                rows.append(row)
                stopped_at = bname
                stop_reason = reason
                break

            if overall not in ("PASS", "PARTIAL"):
                reason = _failure_detail(assert_row) or "unexpected overall=%s" % overall
                row = _result_row(bname, tech, metric, bt, attempts + 1, assert_row, False, reason)
                rows.append(row)
                stopped_at = bname
                stop_reason = reason
                break

            _progress("push", "pushing to GitHub")
            files = generate_branch_files(tech, metric, bt, version, language)
            commit_sha, push_err, _method = push_branch_to_github(
                token,
                repo_slug,
                bname,
                files=files,
                source_dir=tmp,
                base=base_branch,
                message="Add %s codebase" % bname,
                login=push_login,
            )
            if push_err:
                row = _result_row(bname, tech, metric, bt, attempts + 1, assert_row, False, push_err)
                rows.append(row)
                stopped_at = bname
                stop_reason = push_err
                break

            row = _result_row(bname, tech, metric, bt, attempts + 1, assert_row, True, "")
            if overall == "PARTIAL":
                row["failure_reason"] = "metric-behavior deferred to Local tools"
            if commit_sha:
                row["commit_sha"] = commit_sha[:12]
            rows.append(row)
            completed.append(bname)
            _progress("done", "%s + pushed" % overall)
        finally:
            shutil.rmtree(tmp_root, ignore_errors=True)

    return {
        "rows": rows,
        "completed": completed,
        "stopped_at": stopped_at,
        "stop_reason": stop_reason,
        "success": stopped_at is None and len(completed) == total,
        "needs_install": False,
        "total": total,
    }
