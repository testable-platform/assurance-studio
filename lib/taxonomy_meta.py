"""Extract run metadata from taxonomy reports and manifest."""

from __future__ import print_function

import json
import os
import re
from pathlib import Path

from lib.metrics import branch_name_from_report_folder, infer_from_branch_name

DOV_BRANCHES = frozenset([
    "SA_DOV_Bug_2.6",
    "SA_DOV_BugFX_2.6",
    "SA_DOV_TCC_2.6",
    "SA_DOV_CC_2.6",
])

_HTML_FIELDS = (
    ("branch", r"Branch name</th><td>([^<]+)"),
    ("commit_sha", r"Commit ID</th><td>([^<]+)"),
    ("run_id", r"Run ID</th><td>([^<]+)"),
    ("repo", r"Repo name</th><td>([^<]+)"),
)


def parse_taxonomy_html(html_path):
    """Return dict with branch, commit_sha, run_id, repo, html_path."""
    path = Path(html_path)
    text = path.read_text(encoding="utf-8")
    out = {"html_path": str(path.resolve())}
    for key, pattern in _HTML_FIELDS:
        m = re.search(pattern, text)
        out[key] = m.group(1).strip() if m else ""
    tech, metric, branch_type, version = infer_from_branch_name(out.get("branch", ""))
    out["technique"] = tech
    out["metric"] = metric
    out["branch_type"] = branch_type
    out["version"] = version
    return out


def parse_run_summary(run_dir):
    """Read run_summary.json if present (before html_only prune)."""
    path = Path(run_dir) / "run_summary.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}


def iter_taxonomy_run_dirs(classification_dir, branches=None):
    """
    Yield metadata dicts for taxonomy runs under Structural Analysis.
    Prefers run_meta.json, then taxonomy-gate.html, then run_summary + folder name.
    """
    classification_dir = Path(classification_dir)
    branches = branches or DOV_BRANCHES
    seen = set()

    for html in sorted(classification_dir.rglob("taxonomy-gate.html")):
        meta = parse_taxonomy_html(html)
        branch = meta.get("branch", "")
        if branch not in branches:
            continue
        run_dir = html.parent
        key = (branch, meta.get("commit_sha"), meta.get("run_id"))
        if key in seen:
            continue
        seen.add(key)
        meta["report_folder"] = str(run_dir.relative_to(classification_dir)).replace("\\", "/")
        meta["run_dir"] = str(run_dir)
        yield meta

    manifest_path = classification_dir / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            manifest = {}
        for row in manifest.get("runs", []):
            branch = row.get("branch", "")
            if branch not in branches:
                continue
            commit = row.get("commit_sha", "")
            run_id = row.get("run_id", "")
            key = (branch, commit, run_id)
            if key in seen:
                continue
            folder = row.get("report_folder", "")
            run_dir = classification_dir / folder.replace("/", os.sep)
            html = run_dir / "taxonomy-gate.html"
            if html.is_file():
                meta = parse_taxonomy_html(html)
            else:
                meta = {
                    "branch": branch,
                    "commit_sha": commit,
                    "run_id": run_id,
                    "html_path": "",
                }
            meta["report_folder"] = folder
            meta["run_dir"] = str(run_dir)
            meta["manifest_row"] = row
            seen.add(key)
            yield meta


def latest_taxonomy_by_branch(classification_dir, branches=None):
    """Return branch -> latest metadata (by report folder timestamp)."""
    by_branch = {}
    for meta in iter_taxonomy_run_dirs(classification_dir, branches):
        branch = meta["branch"]
        prev = by_branch.get(branch)
        if not prev or meta.get("report_folder", "") > prev.get("report_folder", ""):
            by_branch[branch] = meta
    return by_branch
