"""Extract run metadata from taxonomy reports and manifest."""

from __future__ import print_function

import json
import re
from pathlib import Path

from lib.metrics import branch_name_from_report_folder, classification_dir_for_branch

_HTML_FIELDS = (
    ("branch", r"Branch name</th><td>([^<]+)"),
    ("commit_sha", r"Commit ID</th><td>([^<]+)"),
    ("run_id", r"Run ID</th><td>([^<]+)"),
    ("repo", r"Repo name</th><td>([^<]+)"),
)


def parse_taxonomy_html(html_path):
    """Return dict with branch, commit_sha, run_id, repo, html_path."""
    path = Path(html_path)
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = {"html_path": str(path)}
    for key, pattern in _HTML_FIELDS:
        m = re.search(pattern, text)
        if m:
            meta[key] = m.group(1).strip()
    folder = path.parent.name
    if "branch" not in meta:
        meta["branch"] = branch_name_from_report_folder(folder)
    if "run_id" not in meta:
        m = re.search(r"taxonomy-gate-([0-9a-f-]+)\.html", path.name, re.I)
        if m:
            meta["run_id"] = m.group(1)
    return meta


def _html_files(classification_dir):
    root = Path(classification_dir)
    if not root.is_dir():
        return []
    files = []
    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        for html in folder.glob("taxonomy-gate*.html"):
            files.append(html)
    return files


def latest_taxonomy_by_branch(classification_dir):
    """Map branch -> latest metadata dict from taxonomy HTML folders."""
    by_branch = {}
    for html_path in _html_files(classification_dir):
        meta = parse_taxonomy_html(html_path)
        branch = meta.get("branch")
        if not branch:
            continue
        folder = html_path.parent.name
        ts = folder.rsplit("_", 1)[-1] if "_" in folder else ""
        prev = by_branch.get(branch)
        if prev is None or ts >= prev.get("_folder_ts", ""):
            meta["_folder_ts"] = ts
            meta["report_folder"] = folder
            by_branch[branch] = meta
    return by_branch


def load_manifest_runs(classification_dir):
    manifest_path = Path(classification_dir) / "manifest.json"
    if not manifest_path.is_file():
        return []
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return data.get("runs", [])


def _meta_with_usable_html(meta):
    """True when meta dict points at an existing taxonomy HTML file."""
    html_path = meta.get("html_path", "")
    return bool(html_path and Path(html_path).is_file())


def resolve_branch_taxonomy_meta(
    branch_name,
    taxonomy_root="taxonomy_reports",
    root=None,
    registry=None,
):
    """Return (meta, source_class_dir) for a branch, with cross-folder fallback.

    Looks in the canonical technique classification dir first, then scans every
    subdir under taxonomy_root for legacy misfiled reports.
    """
    from lib.registry import load_registry

    reg = registry or load_registry()
    repo_root = Path(root) if root else Path(__file__).resolve().parents[1]
    tax_root = repo_root / taxonomy_root
    canonical_dir = classification_dir_for_branch(
        branch_name, taxonomy_root, root=str(repo_root), registry=reg,
    )

    def _meta_from_dir(class_dir):
        if not class_dir or not class_dir.is_dir():
            return {}
        return latest_taxonomy_by_branch(class_dir).get(branch_name, {})

    best_meta = _meta_from_dir(canonical_dir)
    best_dir = canonical_dir

    if tax_root.is_dir():
        for alt_dir in sorted(tax_root.iterdir()):
            if not alt_dir.is_dir():
                continue
            if alt_dir == canonical_dir:
                continue
            alt_meta = _meta_from_dir(alt_dir)
            if not _meta_with_usable_html(alt_meta):
                continue
            if not _meta_with_usable_html(best_meta):
                best_meta, best_dir = alt_meta, alt_dir
            elif alt_meta.get("_folder_ts", "") >= best_meta.get("_folder_ts", ""):
                best_meta, best_dir = alt_meta, alt_dir

    return best_meta, best_dir


def load_run_summary_from_meta(meta):
    """Load run_summary.json adjacent to taxonomy HTML if present."""
    html_path = meta.get("html_path", "")
    if not html_path:
        return {}
    summary_path = Path(html_path).parent / "run_summary.json"
    if not summary_path.is_file():
        return {}
    try:
        return json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_taxonomy_gate_json(meta):
    """Load taxonomy-gate.json from the report folder when available."""
    html_path = meta.get("html_path", "")
    if not html_path:
        return {}
    gate_path = Path(html_path).parent / "taxonomy-gate.json"
    if not gate_path.is_file():
        return {}
    try:
        return json.loads(gate_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def failing_sections(taxonomy_json, score_threshold=0.0):
    """Return classifications/techniques with zero or missing normalized scores."""
    rows = []
    if not taxonomy_json:
        return rows
    for tt in taxonomy_json.get("weighted_breakdown") or []:
        testing_type = tt.get("testing_type", "")
        for technique in tt.get("techniques") or []:
            tech_name = technique.get("technique", "")
            for cls in technique.get("classifications") or []:
                score = cls.get("normalized_score")
                if score is None or float(score) <= score_threshold:
                    rows.append({
                        "testing_type": testing_type,
                        "technique": tech_name,
                        "classification": cls.get("classification", ""),
                        "normalized_score": score,
                    })
    return rows


def branch_taxonomy_scope(branch_name, registry=None):
    """Registry taxonomy labels that apply to one generated branch."""
    from lib.metrics import infer_from_branch_name
    from lib.registry import metric_entry

    tech, metric, _, _ = infer_from_branch_name(branch_name, registry)
    if not tech or not metric:
        return set()
    try:
        _, entry = metric_entry(tech, metric, registry)
    except KeyError:
        return set()
    labels = {
        entry.get("taxonomy_classification"),
        entry.get("l4_classification"),
        entry.get("l5_metric"),
    }
    return {label.strip() for label in labels if label and str(label).strip()}


def failing_sections_for_branch(
    taxonomy_json,
    branch_name,
    registry=None,
    score_threshold=0.0,
):
    """Like failing_sections, but only for classifications in this branch's metric scope."""
    scope = branch_taxonomy_scope(branch_name, registry)
    if not scope:
        return failing_sections(taxonomy_json, score_threshold=score_threshold)
    rows = []
    if not taxonomy_json:
        return rows
    for tt in taxonomy_json.get("weighted_breakdown") or []:
        testing_type = tt.get("testing_type", "")
        for technique in tt.get("techniques") or []:
            tech_name = technique.get("technique", "")
            for cls in technique.get("classifications") or []:
                name = cls.get("classification", "")
                if name not in scope:
                    continue
                score = cls.get("normalized_score")
                if score is None or float(score) <= score_threshold:
                    rows.append({
                        "testing_type": testing_type,
                        "technique": tech_name,
                        "classification": name,
                        "normalized_score": score,
                    })
    return rows
