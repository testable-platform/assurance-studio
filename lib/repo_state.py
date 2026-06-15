"""Track active GitHub repo and clear stale pipeline artifacts on repo change."""

from __future__ import print_function

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER_NAME = ".pipeline_repo.json"
ARTIFACT_DIRS = ("proofs", "taxonomy_reports", "s3_downloads", "build")


def marker_path(root=None):
    return Path(root or ROOT) / MARKER_NAME


def read_stored_repo(root=None):
    path = marker_path(root)
    if not path.is_file():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return ""
    return (data.get("repo_slug") or "").strip()


def write_stored_repo(repo_slug, root=None):
    repo_slug = (repo_slug or "").strip()
    if not repo_slug:
        return
    path = marker_path(root)
    path.write_text(
        json.dumps({"repo_slug": repo_slug}, indent=2) + "\n",
        encoding="utf-8",
    )


def clear_pipeline_artifacts(root=None):
    """Remove local reports/downloads from prior repo runs."""
    repo_root = Path(root or ROOT)
    removed = []
    for name in ARTIFACT_DIRS:
        target = repo_root / name
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
            removed.append(name)
    return removed


def ensure_repo_aligned(repo_slug, root=None, clear_on_change=True):
    """If repo_slug changed, optionally clear artifacts and update marker.

    Returns dict with keys: changed (bool), old_repo, new_repo, cleared (list).
    """
    repo_root = Path(root or ROOT)
    new_repo = (repo_slug or "").strip()
    old_repo = read_stored_repo(repo_root)

    if not new_repo:
        return {"changed": False, "old_repo": old_repo, "new_repo": "", "cleared": []}

    if old_repo == new_repo:
        return {"changed": False, "old_repo": old_repo, "new_repo": new_repo, "cleared": []}

    cleared = clear_pipeline_artifacts(repo_root) if clear_on_change else []
    write_stored_repo(new_repo, repo_root)
    return {
        "changed": True,
        "old_repo": old_repo,
        "new_repo": new_repo,
        "cleared": cleared,
    }
