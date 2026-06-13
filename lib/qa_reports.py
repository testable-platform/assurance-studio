"""Save taxonomy HTML to main branch under registry-driven paths."""

from __future__ import print_function

import os
import shutil
import subprocess

from lib.metrics import (
    REPORT_TS_SUFFIX_RE,
    branch_name_from_report_folder,
    infer_from_branch_name,
    report_file_path,
    report_group_label,
    report_html_filename,
    report_timestamp,
)


def save_html_on_main(repo_root, branch_name, html_content, collected_at=None):
    """taxonomy_reports/<L2>/<BRANCH>/<BRANCH>_<ts>/taxonomy-gate.html"""
    tech, metric, _, _ = infer_from_branch_name(branch_name)
    if not tech:
        raise ValueError("cannot parse branch name: %s" % branch_name)
    group = report_group_label(tech)
    ts = collected_at or report_timestamp()
    out_path = report_file_path(group, branch_name, ts)
    full = os.path.join(repo_root, out_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(html_content)
    return full, out_path


def iter_run_dirs(batch_dir):
    """Yield run directories containing taxonomy-gate.json (flat or nested layout)."""
    for name in os.listdir(batch_dir):
        path = os.path.join(batch_dir, name)
        if not os.path.isdir(path):
            continue
        if os.path.isfile(os.path.join(path, "taxonomy-gate.json")):
            yield path
            continue
        for sub in os.listdir(path):
            sub_path = os.path.join(path, sub)
            if os.path.isdir(sub_path):
                yield sub_path


def normalize_taxonomy_html(run_dir):
    """Rename taxonomy-gate-<run_id>.html -> taxonomy-gate.html in one run folder."""
    canonical = report_html_filename()
    htmls = [f for f in os.listdir(run_dir) if f.endswith(".html")]
    if not htmls:
        return False
    target = os.path.join(run_dir, canonical)
    if canonical in htmls:
        for f in htmls:
            if f != canonical:
                os.remove(os.path.join(run_dir, f))
        return True
    src = sorted(htmls)[0]
    if src != canonical:
        shutil.move(os.path.join(run_dir, src), target)
    for f in htmls[1:]:
        path = os.path.join(run_dir, f)
        if os.path.isfile(path):
            os.remove(path)
    return True


def reorganize_taxonomy_reports(classification_dir, html_only=True):
    """
    Move flat SA_DOV_Bug_2.6_<ts>/ folders under SA_DOV_Bug_2.6/SA_DOV_Bug_2.6_<ts>/,
    normalize HTML name, optionally drop JSON/XML intermediates.
    """
    classification_dir = os.path.abspath(classification_dir)
    if not os.path.isdir(classification_dir):
        raise FileNotFoundError(classification_dir)

    moved = 0
    for name in list(os.listdir(classification_dir)):
        flat = os.path.join(classification_dir, name)
        if not os.path.isdir(flat) or name in (".git",):
            continue
        if not REPORT_TS_SUFFIX_RE.search(name):
            continue
        branch = branch_name_from_report_folder(name)
        nested_parent = os.path.join(classification_dir, branch)
        nested = os.path.join(nested_parent, name)
        if os.path.normpath(flat) == os.path.normpath(nested):
            continue
        if os.path.exists(nested):
            continue
        os.makedirs(nested_parent, exist_ok=True)
        shutil.move(flat, nested)
        moved += 1
        print("  moved %s -> %s/%s" % (name, branch, name))

    normalized = 0
    for run_dir in iter_run_dirs(classification_dir):
        if normalize_taxonomy_html(run_dir):
            normalized += 1

    removed = 0
    if html_only:
        for run_dir in iter_run_dirs(classification_dir):
            for fn in os.listdir(run_dir):
                if fn.endswith(".html"):
                    continue
                path = os.path.join(run_dir, fn)
                if os.path.isfile(path):
                    os.remove(path)
                    removed += 1

    return {"moved": moved, "normalized": normalized, "pruned": removed}


def git_commit_report(repo_root, rel_path, branch_name):
    subprocess.check_call(["git", "checkout", "main"], cwd=repo_root)
    subprocess.check_call(["git", "add", rel_path], cwd=repo_root)
    msg = "Add taxonomy report for %s" % branch_name
    subprocess.check_call(["git", "commit", "-m", msg], cwd=repo_root)
    rev = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], cwd=repo_root).decode().strip()
    return rev
