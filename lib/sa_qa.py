"""Run SA branches on Testable QA and verify taxonomy HTML reports."""

from __future__ import print_function

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from lib.sa_metrics import (  # noqa: E402
    ABBREV_TO_CLASSIFICATION,
    SA_METRICS,
    SA_TESTING_TYPE,
    branch_name_from_report_folder,
    infer_metric_from_report_folder,
    report_folder_name,
    report_output_dir,
)

CLASSIFICATION_TO_ABBREV = {cls: abbrev for _, abbrev, cls, _, _ in SA_METRICS}
ROW_RE = re.compile(
    r'<div class="cls-name">([^<]+)</div>.*?'
    r'<td class="result-em"><span class="rp rp-(\w+)">',
    re.DOTALL,
)

TERMINAL_STATUSES = frozenset(["completed", "failed", "partial", "cancelled"])
IN_FLIGHT_STATUSES = frozenset(["pending", "queued", "running", "executing", "in_progress"])
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def load_env(path):
    if not os.path.isfile(path):
        print("WARNING: env file not found: %s" % path, file=sys.stderr, flush=True)
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            k, v = key.strip(), val.strip()
            if k and (k not in os.environ or not str(os.environ.get(k, "")).strip()):
                os.environ[k] = v


class PlatformClient(object):
    def __init__(self, identity_url, runtime_url, views_url, session_token):
        self.identity_url = identity_url.rstrip("/")
        self.runtime_url = runtime_url.rstrip("/")
        self.views_url = views_url.rstrip("/")
        self.session_token = session_token

    def _request(self, method, url, body=None, accept=None):
        req = urllib.request.Request(url, method=method)
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", BROWSER_USER_AGENT)
        if accept:
            req.add_header("Accept", accept)
        if self.session_token:
            req.add_header("Cookie", "session_token=%s" % self.session_token)
        if body is not None:
            req.data = json.dumps(body).encode("utf-8")
        try:
            resp = urllib.request.urlopen(req, timeout=300)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError("HTTP %s %s %s" % (method, url, detail)) from e
        content_type = resp.headers.get("Content-Type", "")
        raw = resp.read()
        if "application/json" in content_type or (raw[:1] in (b"{", b"[")):
            return json.loads(raw.decode("utf-8"))
        return raw

    def get_json(self, url, timeout=300, retries=3, retry_delay=15):
        last_exc = None
        for attempt in range(1, retries + 1):
            try:
                req = urllib.request.Request(url, method="GET")
                req.add_header("Content-Type", "application/json")
                req.add_header("User-Agent", BROWSER_USER_AGENT)
                if self.session_token:
                    req.add_header("Cookie", "session_token=%s" % self.session_token)
                resp = urllib.request.urlopen(req, timeout=timeout)
                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read()
                if "application/json" in content_type or (raw[:1] in (b"{", b"[")):
                    return json.loads(raw.decode("utf-8"))
                return raw
            except Exception as exc:
                last_exc = exc
                msg = str(exc).lower()
                if attempt < retries and ("timed out" in msg or "timeout" in msg):
                    print(
                        "  API read timeout (attempt %d/%d), retrying in %ds..."
                        % (attempt, retries, retry_delay),
                        flush=True,
                    )
                    time.sleep(retry_delay)
                    continue
                if isinstance(exc, urllib.error.HTTPError):
                    detail = exc.read().decode("utf-8", errors="replace")
                    raise RuntimeError("HTTP GET %s %s" % (url, detail)) from exc
                raise
        raise last_exc

    def post_json(self, url, body):
        return self._request("POST", url, body=body)


def resolve_tenant_id(client):
    """Resolve tenant from the authenticated session (QA/live friendly)."""
    data = client.get_json("%s/v1/me/tenant" % client.identity_url)
    tenant_id = data.get("tenant_id")
    if not tenant_id:
        raise RuntimeError("Session tenant missing from /v1/me/tenant: %s" % data)
    return str(tenant_id)


def login(identity_url, email, password):
    url = "%s/api/v1/auth/login" % identity_url.rstrip("/")
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", BROWSER_USER_AGENT)
    req.add_header("Origin", os.environ.get("FRONTEND_URL", "https://qa-frontend.testable.cc"))
    req.add_header("Referer", "%s/auth/login" % os.environ.get(
        "FRONTEND_URL", "https://qa-frontend.testable.cc").rstrip("/"))
    req.data = json.dumps({"identifier": email, "password": password}).encode("utf-8")
    try:
        resp = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        raise RuntimeError("Login failed: %s" % e.read().decode("utf-8", errors="replace")) from e
    cookie = resp.headers.get("Set-Cookie", "")
    token = None
    for part in cookie.split(";"):
        part = part.strip()
        if part.startswith("session_token="):
            token = part.split("=", 1)[1]
            break
    if not token:
        raise RuntimeError("Login succeeded but session_token cookie missing")
    return token


def dev_verify(identity_url, email):
    url = "%s/v1/auth/dev-verify" % identity_url.rstrip("/")
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    req.data = json.dumps({"email": email}).encode("utf-8")
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError:
        pass


def github_tip_sha(branch_name, repository_match):
    repo = repository_match.strip().strip("/")
    if repo.endswith(".git"):
        repo = repo[:-4]
    parts = repo.split("/")
    if len(parts) < 2:
        return None
    owner, name = parts[-2], parts[-1]
    api_url = "https://api.github.com/repos/%s/%s/git/ref/heads/%s" % (
        owner, name, urllib.parse.quote(branch_name))
    req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("object", {}).get("sha")
    except Exception:
        return None


def resolve_commit_sha(branch_name, branch_row, repository_match, prefer_github=False):
    if prefer_github:
        sha = github_tip_sha(branch_name, repository_match)
        if sha:
            print("  commit from GitHub tip: %s" % sha[:12], flush=True)
            return sha
    for key in ("head_commit_sha", "headCommitSha", "commit_sha", "tip_sha"):
        val = branch_row.get(key)
        if val:
            return val
    sha = github_tip_sha(branch_name, repository_match)
    if sha:
        print("  resolved commit via GitHub API: %s" % sha[:12], flush=True)
        return sha
    # Fallback: local git ls-remote (works when repo is cloned and remote configured)
    try:
        proc = subprocess.Popen(
            ["git", "ls-remote", "origin", "refs/heads/%s" % branch_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
        )
        out, _ = proc.communicate(timeout=30)
        line = out.decode("utf-8", errors="replace").strip().splitlines()
        if line:
            sha = line[0].split()[0]
            print("  resolved commit via git ls-remote: %s" % sha[:12])
            return sha
    except Exception as exc:
        print("  git ls-remote failed: %s" % exc)
    return None


def normalize_repo_label(clone_url):
    if not clone_url:
        return ""
    raw = clone_url.strip().rstrip("/")
    if raw.endswith(".git"):
        raw = raw[:-4]
    parts = raw.replace(":", "/").split("/")
    parts = [p for p in parts if p and p not in ("https", "http", "git@github.com")]
    if len(parts) >= 2:
        return "%s/%s" % (parts[-2], parts[-1])
    return raw


def ensure_project(client, name, clone_url, default_branch):
    projects = client.get_json("%s/v1/projects" % client.runtime_url)
    if projects.get("projects"):
        return None
    body = {
        "name": name,
        "clone_url": clone_url,
        "branch_name": default_branch,
        "scm_provider": "github",
    }
    print("  creating project '%s'..." % name)
    return client.post_json("%s/v1/projects" % client.runtime_url, body)


def refresh_branches(client, repository_id):
    url = "%s/v1/repositories/%s/branches/refresh" % (client.runtime_url, repository_id)
    return client.post_json(url, {})


def wait_for_branches(client, repository_id, required_names, poll_interval=10, timeout_sec=300):
    started = time.time()
    branch_map = {}
    while time.time() - started < timeout_sec:
        try:
            branches_resp = client.get_json(
                "%s/v1/repositories/%s/branches" % (client.runtime_url, repository_id))
        except Exception as exc:
            print("  branch poll error: %s (retrying...)" % exc, flush=True)
            time.sleep(poll_interval)
            continue
        branch_list = branches_resp.get("branches") or branches_resp.get("items") or []
        branch_map = {b.get("name"): b for b in branch_list if b.get("name")}
        missing = [n for n in required_names if n not in branch_map]
        if not missing:
            return branch_map
        print("  waiting for branches (missing: %s)..." % missing, flush=True)
        time.sleep(poll_interval)
    return branch_map


def resolve_catalog(client, project_id, repository_match):
    projects = client.get_json("%s/v1/projects" % client.runtime_url)
    project_list = projects.get("projects") or []
    if not project_list:
        raise RuntimeError("No projects found for this user")
    project = None
    if project_id:
        for p in project_list:
            if p.get("id") == project_id:
                project = p
                break
        if not project:
            print(
                "  WARNING: PROJECT_ID %s not found — auto-selecting from catalog"
                % project_id,
                flush=True,
            )
    if not project:
        needle = repository_match.lower()
        for p in project_list:
            name = (p.get("name") or "").lower()
            slug = (p.get("slug") or "").lower()
            if needle.split("/")[-1] in name or needle.split("/")[-1] in slug:
                project = p
                break
    if not project:
        project = project_list[0]
    pid = project["id"]
    repos = client.get_json("%s/v1/projects/%s/repositories" % (client.runtime_url, pid))
    repo_list = repos.get("repositories") or repos.get("items") or []
    repository = None
    needle = repository_match.lower()
    for r in repo_list:
        label = normalize_repo_label(r.get("clone_url") or r.get("url") or "")
        name = (r.get("name") or "").lower()
        if needle in label.lower() or needle in name or label.lower() == needle:
            repository = r
            break
    if not repository:
        available = [normalize_repo_label(r.get("clone_url")) for r in repo_list]
        raise RuntimeError("Repository '%s' not found. Available: %s" % (repository_match, available))
    rid = repository["id"]
    branches_resp = client.get_json("%s/v1/repositories/%s/branches" % (client.runtime_url, rid))
    branch_list = branches_resp.get("branches") or branches_resp.get("items") or []
    branch_map = {}
    for b in branch_list:
        name = b.get("name")
        if name:
            branch_map[name] = b
    return {
        "project_id": pid,
        "project_name": project.get("name"),
        "repository_id": rid,
        "repository_label": normalize_repo_label(repository.get("clone_url")),
        "branches": branch_map,
    }


def is_admission_delayed(exc):
    msg = str(exc).lower()
    return (
        "rate_limited" in msg
        or "quota_exceeded" in msg
        or "admission delayed" in msg
    )


def create_run(client, project_id, repository_id, branch_id, commit_sha):
    body = {
        "project_id": project_id,
        "repository_id": repository_id,
        "branch_id": branch_id,
        "commit_sha": commit_sha,
        "trigger_type": "manual",
    }
    return client.post_json("%s/v1/runs" % client.runtime_url, body)


def create_run_with_retry(client, project_id, repository_id, branch_id, commit_sha,
                          max_retries, retry_delay_sec):
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            return create_run(client, project_id, repository_id, branch_id, commit_sha)
        except Exception as exc:
            last_exc = exc
            if not is_admission_delayed(exc) or attempt >= max_retries:
                raise
            wait = retry_delay_sec * attempt
            print(
                "  quota/rate limit (attempt %d/%d) — waiting %ds before retry..."
                % (attempt, max_retries, wait),
                flush=True,
            )
            time.sleep(wait)
    raise last_exc


def get_run_summary(client, run_id, tenant_id):
    params = urllib.parse.urlencode({"tenant_id": tenant_id})
    return client.get_json("%s/v1/runs/%s/summary?%s" % (client.views_url, run_id, params))


def wait_for_whitebox_run(client, run_id, tenant_id, poll_interval, timeout_sec, require_completed):
    """Poll until whitebox execution finishes. Reports require a completed run by default."""
    started = time.time()
    while True:
        if time.time() - started > timeout_sec:
            raise RuntimeError("Timeout waiting for whitebox run %s" % run_id)
        summary = get_run_summary(client, run_id, tenant_id)
        status = (summary.get("status") or "").lower()
        total = summary.get("total_tasks") or 0
        done = summary.get("completed_tasks") or 0
        failed = summary.get("failed_tasks") or 0
        print(
            "    whitebox status=%s tasks=%s/%s failed=%s"
            % (status, done, total, failed),
            flush=True,
        )
        if status in IN_FLIGHT_STATUSES:
            time.sleep(poll_interval)
            continue
        if status not in TERMINAL_STATUSES:
            time.sleep(poll_interval)
            continue
        if require_completed and status != "completed":
            raise RuntimeError(
                "Whitebox run ended with status '%s' — taxonomy report not generated "
                "(set REQUIRE_RUN_COMPLETED=false to save after whitebox finishes, even if status is failed/partial)"
                % status
            )
        if status in ("failed", "partial") and total > 0:
            print(
                "    whitebox finished (status=%s, tasks=%s/%s, tool_failures=%s) — proceeding to taxonomy"
                % (status, done, total, failed),
                flush=True,
            )
        return summary


def fetch_taxonomy_gate(client, run_id, tenant_id):
    params = urllib.parse.urlencode({"tenant_id": tenant_id})
    return client.get_json(
        "%s/v1/runs/%s/taxonomy-gate?%s" % (client.views_url, run_id, params))


def wait_for_taxonomy_ready(client, run_id, tenant_id, poll_interval, timeout_sec):
    """Poll taxonomy gate until gate_status is completed (matches UI export readiness)."""
    started = time.time()
    while True:
        if time.time() - started > timeout_sec:
            raise RuntimeError("Timeout waiting for taxonomy gate on run %s" % run_id)
        taxonomy = fetch_taxonomy_gate(client, run_id, tenant_id)
        gate_status = (taxonomy.get("gate_status") or "").lower()
        has_types = bool(taxonomy.get("testing_types"))
        print("    taxonomy gate_status=%s types=%s" % (gate_status, has_types), flush=True)
        if gate_status == "completed" and has_types:
            return taxonomy
        time.sleep(poll_interval)


def fetch_taxonomy(client, run_id, tenant_id):
    params = urllib.parse.urlencode({"tenant_id": tenant_id})
    json_url = "%s/v1/runs/%s/taxonomy-gate?%s" % (client.views_url, run_id, params)
    xml_url = "%s/v1/runs/%s/taxonomy-gate.xml?%s" % (client.views_url, run_id, params)
    taxonomy_json = fetch_taxonomy_gate(client, run_id, tenant_id)
    taxonomy_xml = client._request("GET", xml_url, accept="application/xml")
    return taxonomy_json, taxonomy_xml


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def export_html_reports(batch_dir):
    """Build UI-format HTML from saved taxonomy-gate.json files."""
    html_script = os.path.join(ROOT, "tools", "export_taxonomy_html.ts")
    web_console = os.environ.get(
        "WEB_CONSOLE_DIR",
        os.path.join(os.path.dirname(ROOT), "ai-testable-platform", "frontend", "web-console"),
    )
    if not os.path.isfile(html_script):
        print("  WARNING: HTML export script not found: %s" % html_script, flush=True)
        return False
    if not os.path.isdir(web_console):
        print("  WARNING: web-console not found: %s" % web_console, flush=True)
        return False
    print("\n=== Export HTML reports ===", flush=True)
    npx = shutil.which("npx")
    if not npx and sys.platform == "win32":
        npx = shutil.which("npx.cmd")
    if not npx:
        print("  WARNING: npx not found on PATH", flush=True)
        return False
    result = subprocess.run(
        [npx, "--yes", "tsx", "--tsconfig", "tsconfig.json", html_script, os.path.abspath(batch_dir)],
        cwd=web_console,
        shell=False,
    )
    return result.returncode == 0


def _iter_run_dirs(batch_dir):
    from lib.qa_reports import iter_run_dirs
    for run_dir in iter_run_dirs(batch_dir):
        yield run_dir


def prune_to_html_only(batch_dir):
    """Keep manifest.json and taxonomy-gate.html; remove JSON/XML and other intermediates."""
    removed = 0
    for run_dir in _iter_run_dirs(batch_dir):
        for fn in os.listdir(run_dir):
            if fn.endswith(".html"):
                continue
            path = os.path.join(run_dir, fn)
            if os.path.isfile(path):
                os.remove(path)
                removed += 1
    if removed:
        print("  removed %d non-HTML artifact(s)" % removed, flush=True)


def save_report(output_dir, branch_name, run_id, summary, taxonomy_json, collected_at=None):
    """Write export inputs under <output>/<branch>/<branch>_<ts>/ (HTML produced later)."""
    folder_name = report_folder_name(branch_name, collected_at)
    branch_dir = os.path.join(output_dir, branch_name, folder_name)
    ensure_dir(branch_dir)
    with open(os.path.join(branch_dir, "run_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    with open(os.path.join(branch_dir, "taxonomy-gate.json"), "w", encoding="utf-8") as fh:
        json.dump(taxonomy_json, fh, indent=2)
    return os.path.join(branch_name, folder_name)


def extract_gate_score(taxonomy_json):
    for key in ("pipeline_gate_score", "gate_score", "overall_score", "headline_score"):
        if key in taxonomy_json and taxonomy_json[key] is not None:
            return taxonomy_json[key]
    return taxonomy_json.get("score")


def parse_args():
    parser = argparse.ArgumentParser(description="Run SA branches and collect taxonomy reports")
    parser.add_argument("--env-file", default=os.path.join(ROOT, ".env.local"))
    parser.add_argument("--branches", default=None, help="Comma-separated branch names")
    parser.add_argument("--dry-run", action="store_true", help="Resolve catalog only, do not run")
    parser.add_argument("--skip-login", action="store_true", help="Use SESSION_TOKEN env var")
    parser.add_argument("--ensure-project", action="store_true", help="Create project if none exists")
    parser.add_argument("--refresh-branches", action="store_true", help="Refresh branch catalog before runs")
    parser.add_argument(
        "--allow-partial-branches",
        action="store_true",
        help="Run only branches present in catalog (skip missing)",
    )
    parser.add_argument(
        "--export-html",
        action="store_true",
        default=os.environ.get("EXPORT_HTML", "true").lower() == "true",
        help="Generate taxonomy-gate HTML after batch (default: true)",
    )
    parser.add_argument(
        "--no-export-html",
        action="store_false",
        dest="export_html",
        help="Skip HTML export",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        default=os.environ.get("HTML_ONLY", "true").lower() == "true",
        help="Keep only taxonomy-gate.html per run (default: true / HTML_ONLY env)",
    )
    parser.add_argument(
        "--keep-artifacts",
        action="store_true",
        help="Retain taxonomy-gate.json and other intermediates after HTML export",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if getattr(args, "keep_artifacts", False):
        args.html_only = False
    rc, _ = main_with_args(args)
    return rc


def parse_sa_results(html):
    sa_start = html.find("<h2>Structural Analysis</h2>")
    if sa_start < 0:
        return {}
    section = html[sa_start:]
    cyclo_start = section.find("<h3>Cyclomatic Complexity</h3>")
    if cyclo_start < 0:
        return {}
    section = section[cyclo_start:]
    next_h2 = section.find("<h2>", 1)
    if next_h2 > 0:
        section = section[:next_h2]
    return {name.strip(): result.strip().lower() for name, result in ROW_RE.findall(section)}


def infer_from_folder(path):
    folder = os.path.basename(os.path.dirname(path))
    abbrev, branch_type = infer_metric_from_report_folder(folder)
    if abbrev and branch_type:
        return abbrev, branch_type
    base = branch_name_from_report_folder(folder)
    parts = base.split("_")
    if len(parts) >= 3 and parts[0] == "SA":
        return parts[1], parts[2]
    return None, None


def verify_taxonomy_file(html_path, target_abbrev, branch_type):
    with open(html_path, encoding="utf-8") as fh:
        html = fh.read()
    results = parse_sa_results(html)
    if not results:
        return False, "Structural Analysis / Cyclomatic Complexity section not found"
    target_cls = ABBREV_TO_CLASSIFICATION[target_abbrev]
    expect_target_fail = branch_type == "Bug"
    lines = []
    ok = True
    for cls, abbrev in sorted(CLASSIFICATION_TO_ABBREV.items(), key=lambda x: x[1]):
        result = results.get(cls, "missing")
        is_target = abbrev == target_abbrev
        if is_target:
            if expect_target_fail:
                if result != "fail":
                    ok = False
                    lines.append("  TARGET %s (%s): %s (expected FAIL)" % (abbrev, cls, result.upper()))
                else:
                    lines.append("  TARGET %s (%s): FAIL (ok)" % (abbrev, cls))
            else:
                if result == "fail":
                    ok = False
                    lines.append("  TARGET %s (%s): FAIL (expected PASS/WARN)" % (abbrev, cls))
                else:
                    lines.append("  TARGET %s (%s): %s (ok)" % (abbrev, cls, result.upper()))
        else:
            lines.append("  other  %s (%s): %s" % (abbrev, cls, result.upper()))
    return ok, "\n".join(lines)


def iter_taxonomy_html_paths(batch_dir):
    """Yield taxonomy-gate.html files under nested branch/run folders."""
    for run_dir in sorted(_iter_run_dirs(batch_dir)):
        for fn in os.listdir(run_dir):
            if fn.endswith(".html"):
                yield os.path.join(run_dir, fn)


def verify_taxonomy_dir(batch_dir):
    """Verify all HTML reports under a batch directory. Returns failure count."""
    failed = 0
    for path in iter_taxonomy_html_paths(batch_dir):
        abbrev, branch_type = infer_from_folder(path)
        if not abbrev or not branch_type:
            print("%s: cannot infer metric/type" % path)
            failed += 1
            continue
        ok, detail = verify_taxonomy_file(path, abbrev, branch_type)
        print("\n%s (target=%s, type=%s) %s" % (path, abbrev, branch_type, "PASS" if ok else "FAIL"))
        print(detail)
        if not ok:
            failed += 1
    return failed


def run_taxonomy_batch(env_file=None, branches_csv=None, dry_run=False, refresh_branches=False,
                       allow_partial_branches=False, export_html=True, html_only=True):
    """Notebook-friendly wrapper. Returns (exit_code, batch_output_dir)."""
    env_file = env_file or os.path.join(ROOT, ".env.local")
    load_env(env_file)
    branches = (branches_csv or os.environ.get("BRANCHES", "")).split(",")
    branches = [b.strip() for b in branches if b.strip()]
    args = argparse.Namespace(
        env_file=env_file,
        branches=",".join(branches),
        dry_run=dry_run,
        skip_login=False,
        ensure_project=False,
        refresh_branches=refresh_branches,
        allow_partial_branches=allow_partial_branches,
        export_html=export_html,
        html_only=html_only,
    )
    return main_with_args(args)


def main_with_args(args):
    """Core batch logic extracted for programmatic use."""
    load_env(args.env_file)
    identity_url = os.environ.get("IDENTITY_URL", "http://localhost:8000")
    runtime_url = os.environ.get("RUNTIME_URL", "http://localhost:8002")
    views_url = os.environ.get("VIEWS_URL", "http://localhost:8003")
    email = os.environ.get("AUTH_EMAIL")
    password = os.environ.get("AUTH_PASSWORD")
    tenant_id = os.environ.get("TENANT_ID")
    project_id = os.environ.get("PROJECT_ID") or None
    repository_match = os.environ.get("REPOSITORY_MATCH", "Mohammed-shihaf/Metric_eveluation")
    branches = (args.branches or os.environ.get(
        "BRANCHES", "SA_bug_2.6,SA_bugFX_2.6,SA_TCC_2.6,SA_CC_2.6")).split(",")
    branches = [b.strip() for b in branches if b.strip()]
    output_root = os.environ.get("OUTPUT_DIR", "taxonomy_reports")
    poll_interval = int(os.environ.get("POLL_INTERVAL_SEC", "30"))
    poll_timeout = int(os.environ.get("POLL_TIMEOUT_SEC", "3600"))
    continue_on_failure = os.environ.get("CONTINUE_ON_FAILURE", "true").lower() == "true"
    require_run_completed = os.environ.get("REQUIRE_RUN_COMPLETED", "true").lower() == "true"
    taxonomy_poll_timeout = int(os.environ.get("TAXONOMY_POLL_TIMEOUT_SEC", str(poll_timeout)))
    branch_delay_sec = int(os.environ.get("BRANCH_DELAY_SEC", "0"))
    run_create_max_retries = int(os.environ.get("RUN_CREATE_MAX_RETRIES", "15"))
    run_create_retry_sec = int(os.environ.get("RUN_CREATE_RETRY_SEC", "120"))
    prefer_github_commit = os.environ.get("PREFER_GITHUB_COMMIT", "true").lower() == "true"

    print("=== Authenticate ===", flush=True)
    if args.skip_login:
        token = os.environ.get("SESSION_TOKEN")
        if not token:
            print("ERROR: SESSION_TOKEN required with --skip-login", file=sys.stderr)
            return 1, None
    else:
        if not email or not password:
            print("ERROR: AUTH_EMAIL and AUTH_PASSWORD required", file=sys.stderr)
            return 1, None
        if "localhost" in identity_url or "127.0.0.1" in identity_url:
            dev_verify(identity_url, email)
        token = login(identity_url, email, password)
        print("  logged in as %s" % email, flush=True)

    client = PlatformClient(identity_url, runtime_url, views_url, token)
    env_tenant_id = tenant_id
    try:
        tenant_id = resolve_tenant_id(client)
        print("  tenant_id=%s (from session)" % tenant_id, flush=True)
        if env_tenant_id and env_tenant_id != tenant_id:
            print("  WARNING: TENANT_ID in .env.local differs from session", flush=True)
    except Exception as exc:
        if not tenant_id:
            print("ERROR: could not resolve tenant: %s" % exc, file=sys.stderr)
            return 1, None
        print("  WARNING: using TENANT_ID from env: %s" % exc, flush=True)

    if args.ensure_project:
        clone_url = os.environ.get("CLONE_URL", "https://github.com/%s.git" % repository_match)
        ensure_project(client, os.environ.get("PROJECT_NAME", "Metric Evaluation SA"), clone_url, branches[0])

    print("\n=== Resolve catalog ===")
    catalog = resolve_catalog(client, project_id, repository_match)
    if args.refresh_branches:
        print("  refreshing branch catalog...")
        try:
            refresh_branches(client, catalog["repository_id"])
        except Exception as exc:
            print("  refresh trigger: %s" % exc)
        catalog["branches"] = wait_for_branches(client, catalog["repository_id"], branches)
    print("  project: %s (%s)" % (catalog.get("project_name"), catalog["project_id"]))
    print("  repository: %s (%s)" % (catalog.get("repository_label"), catalog["repository_id"]))

    missing = [b for b in branches if b not in catalog["branches"]]
    if missing:
        if args.allow_partial_branches:
            print("  WARNING: skipping missing branches: %s" % missing)
            branches = [b for b in branches if b in catalog["branches"]]
        else:
            print("ERROR: branches missing from catalog: %s" % missing, file=sys.stderr)
            return 1, None
    if not branches:
        print("ERROR: no branches available", file=sys.stderr)
        return 1, None
    if args.dry_run:
        print("\nDry run complete.")
        classification = os.environ.get("REPORT_CLASSIFICATION", SA_TESTING_TYPE)
        output_dir = os.path.join(ROOT, report_output_dir(
            os.environ.get("OUTPUT_DIR", "taxonomy_reports"), classification))
        return 0, output_dir

    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    classification = os.environ.get("REPORT_CLASSIFICATION", SA_TESTING_TYPE)
    output_dir = os.path.join(ROOT, report_output_dir(output_root, classification))
    ensure_dir(output_dir)
    manifest = {
        "batch_id": batch_id,
        "classification": classification,
        "tenant_id": tenant_id,
        "repository": catalog.get("repository_label"),
        "project_id": catalog["project_id"],
        "repository_id": catalog["repository_id"],
        "runs": [],
    }

    print("\n=== Sequential branch runs ===")
    for idx, branch_name in enumerate(branches, start=1):
        print("\n[%d/%d] %s" % (idx, len(branches), branch_name))
        branch = catalog["branches"][branch_name]
        branch_id = branch.get("id") or branch.get("branch_id")
        if idx > 1 and branch_delay_sec > 0:
            time.sleep(branch_delay_sec)
        commit_sha = resolve_commit_sha(
            branch_name, branch, catalog.get("repository_label"), prefer_github_commit)
        if not branch_id or not commit_sha:
            if not continue_on_failure:
                return 1, output_dir
            continue
        try:
            run_resp = create_run_with_retry(
                client, catalog["project_id"], catalog["repository_id"], branch_id, commit_sha,
                run_create_max_retries, run_create_retry_sec)
            run_id = run_resp["run_id"]
            summary = wait_for_whitebox_run(
                client, run_id, tenant_id, poll_interval, poll_timeout, require_run_completed)
            taxonomy_json = wait_for_taxonomy_ready(
                client, run_id, tenant_id, poll_interval, taxonomy_poll_timeout)
            report_folder = save_report(output_dir, branch_name, run_id, summary, taxonomy_json)
            run_entry = {
                "branch": branch_name,
                "report_folder": report_folder,
                "run_id": run_id,
                "commit_sha": commit_sha,
                "status": summary.get("status"),
                "gate_score": extract_gate_score(taxonomy_json),
            }
            manifest["runs"].append(run_entry)
            print("  saved to %s" % os.path.join(output_dir, report_folder.replace("\\", "/")))

            if os.environ.get("SYNC_S3_AFTER_TAXONOMY", "true").lower() == "true":
                try:
                    from lib.s3_sync import sync_run, update_manifest
                    html_path = os.path.join(output_dir, report_folder, "taxonomy-gate.html")
                    sync_result = sync_run(
                        branch=branch_name,
                        commit_sha=commit_sha,
                        run_id=run_id,
                        taxonomy_html_path=html_path if os.path.isfile(html_path) else "",
                    )
                    run_entry["s3_sync"] = {
                        "status": sync_result.get("status"),
                        "local_path": sync_result.get("local_path"),
                        "coverage_status": sync_result.get("coverage_status"),
                        "coverage": sync_result.get("coverage"),
                    }
                    print("  S3 sync: %s" % sync_result.get("status"), flush=True)
                    if sync_result.get("coverage"):
                        cov = sync_result["coverage"]
                        print(
                            "    coverage-py statements=%s covered=%s"
                            % (cov.get("num_statements"), cov.get("covered_lines")),
                            flush=True,
                        )
                except Exception as sync_exc:
                    print("  WARNING: S3 sync failed: %s" % sync_exc, flush=True)
                    run_entry["s3_sync"] = {"status": "ERROR", "error": str(sync_exc)}
        except Exception as exc:
            print("  FAILED: %s" % exc)
            manifest["runs"].append({"branch": branch_name, "error": str(exc)})
            if not continue_on_failure:
                break

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    successful = [r for r in manifest["runs"] if r.get("run_id")]
    if args.export_html and successful:
        exported = export_html_reports(output_dir)
        from lib.qa_reports import normalize_taxonomy_html

        for run_dir in _iter_run_dirs(output_dir):
            normalize_taxonomy_html(run_dir)
        if args.html_only:
            prune_to_html_only(output_dir)
        elif not exported:
            print("  WARNING: HTML export failed", flush=True)

        if os.environ.get("SYNC_S3_AFTER_TAXONOMY", "true").lower() == "true":
            try:
                from lib.s3_sync import backfill_missing
                print("\n=== S3 backfill after HTML export ===", flush=True)
                backfill_missing(output_dir)
            except Exception as exc:
                print("  WARNING: S3 backfill failed: %s" % exc, flush=True)

    print("\n=== Done ===")
    print("Reports: %s" % output_dir)
    if not successful:
        return 1, output_dir
    failed = [r for r in manifest["runs"] if r.get("error")]
    return (1 if failed else 0), output_dir


if __name__ == "__main__":
    sys.exit(main())
