"""Metric Evaluation pipeline UI — end-to-end with strong triggers."""

from __future__ import print_function

import json
import os
import subprocess
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.branch_asserts import assert_build_batch  # noqa: E402
from lib.compare import compare_report_files, summarize_comparisons  # noqa: E402
from lib.credentials import audit_credentials  # noqa: E402
from lib.generator import (  # noqa: E402
    create_git_branches,
    generate_branches,
    push_branches,
    remote_branch_status,
)
from lib.metrics import github_branch_url, scan_build_dir  # noqa: E402
from lib.pipeline_selection import (  # noqa: E402
    branch_type_options,
    csv_from_list,
    metric_options,
    selection_summary,
    technique_options,
)
from lib.proofs import (  # noqa: E402
    collect_comparison_proof,
    collect_local_batch,
    collect_s3_proof,
    compare_readiness,
    list_proof_branches,
    load_proof_bundle,
    whitebox_completion,
)
from lib.registry import load_registry  # noqa: E402
from lib.sa_qa import run_taxonomy_batch, verify_login  # noqa: E402
from lib.ui_run_panel import RunPanel  # noqa: E402

LOGO = Path(__file__).parent / "assets" / "logo.png"

st.set_page_config(
    page_title="Testable Assurance Studio",
    page_icon=str(LOGO),
    layout="wide",
    initial_sidebar_state="expanded",
)


def _app_header():
    logo_col, title_col = st.columns([1, 11], vertical_alignment="center")
    with logo_col:
        st.image(str(LOGO), width=52)
    with title_col:
        st.title("Testable Assurance Studio")
        st.caption("Generate → assert → GitHub · Whitebox + S3 · Local tools · Compare")


_app_header()


def _readiness():
    audit = audit_credentials(str(ROOT / ".env.local"), root=str(ROOT))
    return audit


def _qa_session_creds():
    """Return (email, password) saved from the login form, or (None, None)."""
    email = st.session_state.get("qa_email_saved", "").strip()
    password = st.session_state.get("qa_password_saved", "")
    if email and password:
        return email, password
    return None, None


def _qa_creds_ready(audit):
    """QA ready when URLs configured and creds from session or .env.local."""
    urls_ok = audit.get("testable_urls_ok", False)
    env_creds = any(
        r["configured"] for r in audit.get("testable", [])
        if r["key"] in ("AUTH_EMAIL", "AUTH_PASSWORD")
    )
    session_creds = _qa_session_creds()[0] is not None
    return urls_ok and (env_creds or session_creds)


def _sidebar_filters():
    st.sidebar.image(str(LOGO), width=120)
    st.sidebar.header("Selection")
    registry = load_registry()
    tech_opts = technique_options(registry)
    tech_codes = [c for c, _ in tech_opts]

    use_all = st.sidebar.checkbox("All techniques (412)", value=False)
    if use_all:
        techniques, selected_techniques = "all", tech_codes
    else:
        selected_techniques = st.sidebar.multiselect(
            "Techniques", tech_codes, default=["SA"],
            format_func=lambda c: next(l for code, l in tech_opts if code == c),
        )
        techniques = csv_from_list(selected_techniques) if selected_techniques else "SA"

    use_all_metrics = st.sidebar.checkbox("All metrics", value=False)
    if use_all_metrics:
        metrics = "all"
    else:
        metric_choices = []
        for tc in (selected_techniques if not use_all else ["SA"]):
            for m in metric_options(tc, registry):
                metric_choices.append("%s:%s" % (tc, m))
        picked = st.sidebar.multiselect("Metrics", sorted(set(metric_choices)))
        if picked and len({p.split(":")[0] for p in picked}) == 1:
            metrics = csv_from_list([p.split(":")[1] for p in picked])
        else:
            metrics = "DOV" if techniques == "SA" else "all"

    type_opts = branch_type_options(registry)
    types = st.sidebar.multiselect("Branch types", type_opts, default=type_opts) or type_opts
    version = st.sidebar.text_input("Version", "2.6")

    summary = selection_summary(techniques, metrics, types, version, registry)
    st.sidebar.metric("In scope", summary["branch_count"])

    audit = _readiness()
    qa_ok = _qa_creds_ready(audit)
    c1, c2 = st.sidebar.columns(2)
    c1.metric("QA", "OK" if qa_ok else "—")
    c2.metric("S3", "OK" if audit["s3_ready"] else "—")

    return {
        "techniques": techniques,
        "metrics": metrics,
        "types": types,
        "version": version,
        "language": "python",
        "summary": summary,
        "env_file": str(ROOT / ".env.local"),
        "audit": audit,
        "qa_ready": qa_ok,
    }


def _branch_push_status(branches):
    """GitHub push readiness for in-scope branches."""
    remote = remote_branch_status(branches, str(ROOT))
    rows = []
    for name in branches:
        info = remote.get(name, {})
        rows.append({
            "branch": name,
            "on_github": "yes" if info.get("pushed") else "no",
            "remote_sha": info.get("sha") or "—",
        })
    return rows, all(info.get("pushed") for info in remote.values())


def _tab_branches(filters):
    st.header("1 — Generate branches")
    total = filters["summary"]["branch_count"]

    on_disk = scan_build_dir("build", str(ROOT))
    matched = [r for r in on_disk if r.get("metric") != "?"]
    st.metric("Branches on disk (build/)", len(matched))
    if matched:
        display_cols = ["branch_name", "technique", "metric", "branch_type", "version"]
        st.dataframe(
            [{k: r.get(k, "") for k in display_cols} for r in matched[:100]],
            use_container_width=True,
        )

    col1, col2 = st.columns(2)
    do_assert = col1.checkbox("Run assert validation", value=True)
    do_git = col2.checkbox("Create git branches + push to GitHub", value=True)
    push_only_pass = st.checkbox("Push only branches that pass asserts", value=True)
    if do_git:
        st.caption("Git branches are pushed to origin before you can run whitebox QA.")

    if st.button("Generate branches", type="primary", use_container_width=True):
        with RunPanel("Generating %d branches" % total) as panel:
            names, errors = generate_branches(
                filters["techniques"], filters["metrics"], filters["types"],
                filters["version"], filters["language"], "build", str(ROOT),
                continue_on_error=False,
                progress_callback=panel.progress,
            )
            if errors:
                st.error(errors[0]["error"])
                st.stop()
            st.session_state["last_generated"] = names
            panel.progress("generate", len(names), total, "", "generated %d" % len(names))

            assert_rows = []
            if do_assert:
                with panel.stdout_redirect():
                    assert_rows = assert_build_batch(
                        filters["techniques"], filters["metrics"], filters["types"],
                        filters["version"], filters["language"], "build", str(ROOT),
                        progress_callback=panel.progress,
                    )
                st.session_state["last_asserts"] = assert_rows
                st.dataframe(assert_rows, use_container_width=True)

            if do_git:
                panel.progress("git", 0, total, "", "creating git branches (isolated worktree)")
                to_push = names
                if push_only_pass and assert_rows:
                    passed = {r["branch_name"] for r in assert_rows if r["overall"] == "PASS"}
                    to_push = [n for n in names if n in passed]
                with panel.stdout_redirect():
                    created, git_errors = create_git_branches(
                        filters["techniques"], filters["metrics"], filters["types"],
                        filters["version"], filters["language"], str(ROOT), "build",
                        progress_callback=panel.progress,
                    )
                if git_errors:
                    st.warning("Git branch issues: %d (e.g. %s)" % (len(git_errors), git_errors[0]["error"]))
                if not created:
                    st.error("No git branches were created — push and whitebox are blocked.")
                else:
                    push_targets = [n for n in to_push if n in created]
                    if not push_targets:
                        st.error(
                            "Branches were created locally but none qualify to push "
                            "(check assert results or disable 'Push only branches that pass asserts')."
                        )
                    else:
                        panel.progress("git", 0, len(push_targets), "", "pushing to origin")
                        with panel.stdout_redirect():
                            pushed, push_errors = push_branches(push_targets, str(ROOT))
                        st.session_state["last_pushed"] = pushed
                        st.session_state["last_git_created"] = created
                        if push_errors:
                            st.error(
                                "Push failed for %d branch(es): %s"
                                % (len(push_errors), push_errors[0]["error"])
                            )
                        if pushed:
                            repo = os.environ.get("REPOSITORY_MATCH", "")
                            st.success("Pushed %d branch(es) to GitHub." % len(pushed))
                            for b in pushed[:10]:
                                st.markdown("- [%s](%s)" % (b, github_branch_url(b, repo)))
                        missing_push = [n for n in push_targets if n not in pushed]
                        if missing_push:
                            st.warning("Not pushed: %s" % ", ".join(missing_push))
        st.toast("Branch generation finished", icon="✅")

    in_scope = filters["summary"]["branches"]
    push_rows, all_pushed = _branch_push_status(in_scope)
    st.subheader("GitHub push status")
    st.dataframe(push_rows, use_container_width=True)
    if all_pushed:
        st.success("All in-scope branches are on GitHub — whitebox can run.")
    else:
        not_pushed = [r["branch"] for r in push_rows if r["on_github"] != "yes"]
        st.warning(
            "Whitebox is blocked until these branches are pushed: %s"
            % ", ".join(not_pushed)
        )

    if st.session_state.get("last_asserts"):
        st.subheader("Last assert results")
        st.dataframe(st.session_state["last_asserts"], use_container_width=True)


def _tab_whitebox(filters):
    st.header("2 — Whitebox QA + taxonomy + S3")
    if not filters.get("qa_ready"):
        st.warning("Enter QA email/password below or configure AUTH_EMAIL/AUTH_PASSWORD in .env.local")

    st.caption("Credentials are session-only and are not saved to disk.")
    with st.form("qa_login_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            qa_email = st.text_input(
                "QA email",
                value=st.session_state.get("qa_email_saved", ""),
            )
        with c2:
            qa_password = st.text_input("QA password", type="password")
        verify_clicked = st.form_submit_button("Verify login", use_container_width=True)

    if verify_clicked:
        email = qa_email.strip()
        password = qa_password
        if not email or not password:
            st.error("Enter both QA email and password.")
        else:
            st.session_state["qa_email_saved"] = email
            st.session_state["qa_password_saved"] = password
            ok, msg = verify_login(
                filters["env_file"],
                email,
                password,
            )
            if ok:
                st.session_state["qa_login_msg"] = msg
                st.session_state["qa_login_ok"] = True
                st.success(msg)
            else:
                st.session_state["qa_login_ok"] = False
                st.session_state["qa_login_msg"] = msg
                st.error(msg)
    elif st.session_state.get("qa_login_msg"):
        if st.session_state.get("qa_login_ok"):
            st.success(st.session_state["qa_login_msg"])
        else:
            st.error(st.session_state["qa_login_msg"])

    email_for_auth, password_for_auth = _qa_session_creds()

    branches = filters["summary"]["branches"]
    branches_csv = ",".join(branches)
    st.code(branches_csv, language=None)

    push_rows, all_pushed = _branch_push_status(branches)
    st.subheader("GitHub push gate")
    st.dataframe(push_rows, use_container_width=True)
    if not all_pushed:
        not_pushed = [r["branch"] for r in push_rows if r["on_github"] != "yes"]
        st.error(
            "Push all in-scope branches on the Branches tab before running whitebox. "
            "Missing on GitHub: %s" % ", ".join(not_pushed)
        )

    # Show current whitebox status for in-scope branches
    wb_status = whitebox_completion(branches, root=str(ROOT))
    if wb_status:
        st.subheader("Whitebox status")
        st.dataframe(
            [{
                "branch": b,
                "status": wb_status[b]["status"],
                "detail": wb_status[b]["detail"],
                "gate_score": wb_status[b].get("gate_score"),
            } for b in branches],
            use_container_width=True,
        )

    if st.button(
        "Run whitebox batch",
        type="primary",
        use_container_width=True,
        disabled=not all_pushed,
    ):
        if not all_pushed:
            st.error("Push all in-scope branches to GitHub before running whitebox.")
            return
        if not email_for_auth or not password_for_auth:
            st.error("Enter credentials and click Verify login before running whitebox.")
            return
        with RunPanel("Whitebox QA") as panel:
            with panel.stdout_redirect():
                rc, batch_dir = run_taxonomy_batch(
                    env_file=filters["env_file"],
                    branches_csv=branches_csv,
                    dry_run=False,
                    refresh_branches=True,
                    allow_partial_branches=True,
                    export_html=True,
                    html_only=False,
                    auth_email=email_for_auth,
                    auth_password=password_for_auth,
                    progress_callback=panel.progress,
                )
            st.session_state["last_qa_rc"] = rc
            st.session_state["last_qa_batch"] = batch_dir

            wb_after = whitebox_completion(branches, root=str(ROOT))
            proof_rows = []
            panel.progress("proofs", 0, len(branches), "", "collecting taxonomy + S3 proofs")
            for idx, bname in enumerate(branches, 1):
                info = wb_after.get(bname, {})
                row = {
                    "branch": bname,
                    "whitebox": info.get("status", "NOT_COMPLETED"),
                    "detail": info.get("detail", ""),
                }
                if info.get("status") == "COMPLETED":
                    try:
                        with panel.stdout_redirect():
                            s3_report = collect_s3_proof(
                                bname, meta=info.get("meta"), root=str(ROOT)
                            )
                        row["taxonomy_report"] = "yes"
                        row["s3_report"] = s3_report.get("status", "?")
                    except Exception as exc:
                        row["taxonomy_report"] = "error"
                        row["s3_report"] = str(exc)
                else:
                    row["taxonomy_report"] = "—"
                    row["s3_report"] = "—"
                proof_rows.append(row)
                panel.progress("proofs", idx, len(branches), bname, row["whitebox"])

            st.session_state["last_whitebox_status"] = proof_rows
            st.dataframe(proof_rows, use_container_width=True)
            completed = sum(1 for r in proof_rows if r["whitebox"] == "COMPLETED")
            if rc != 0 or completed == 0:
                st.warning(
                    "Whitebox finished with issues: %d/%d branches completed with taxonomy reports"
                    % (completed, len(branches))
                )
            else:
                st.success("Whitebox completed for all %d branches" % completed)
        st.toast("Whitebox batch finished", icon="✅")

    if st.session_state.get("last_whitebox_status"):
        st.subheader("Last whitebox run")
        st.dataframe(st.session_state["last_whitebox_status"], use_container_width=True)


def _tab_local_tools(filters):
    st.header("3 — Local tool execution")
    branches = filters["summary"]["branches"]
    wb = whitebox_completion(branches, root=str(ROOT))
    completed = [b for b in branches if wb.get(b, {}).get("status") == "COMPLETED"]
    if not completed:
        st.info("No whitebox-completed branches in scope. Run Page 2 first.")
        return

    st.caption("Install tools and run locally for %d whitebox-completed branch(es)." % len(completed))
    st.code(", ".join(completed), language=None)

    if st.button("Install tools + run locally", type="primary", use_container_width=True):
        with RunPanel("Local tool execution") as panel:
            with panel.stdout_redirect():
                results = collect_local_batch(
                    completed,
                    build_dir="build",
                    install=True,
                    root=str(ROOT),
                    progress_callback=panel.progress,
                )
            st.session_state["last_local_run"] = results
            st.dataframe(
                [{
                    "branch": r["branch_name"],
                    "status": r.get("status"),
                    "tool": r.get("tool", ""),
                    "local_status": (r.get("local_report") or {}).get("status"),
                    "error": r.get("error", ""),
                } for r in results],
                use_container_width=True,
            )
        st.toast("Local tool run finished", icon="✅")

    if st.session_state.get("last_local_run"):
        st.subheader("Last local run")
        st.dataframe(st.session_state["last_local_run"], use_container_width=True)


def _tab_comparison(filters):
    st.header("4 — Compare taxonomy / S3 / local")
    branches = filters["summary"]["branches"]
    wb = whitebox_completion(branches, root=str(ROOT))
    completed = [b for b in branches if wb.get(b, {}).get("status") == "COMPLETED"]
    if not completed:
        st.info("No whitebox-completed branches. Run Page 2 first.")
        return

    readiness = compare_readiness(completed, root=str(ROOT))
    st.subheader("Report readiness (all three required)")
    st.dataframe(
        [{
            "branch": r["branch_name"],
            "taxonomy": r["taxonomy"],
            "s3": r["s3"],
            "local": r["local"],
            "ready": r["ready"],
            "missing": ", ".join(r["missing"]) if r["missing"] else "",
        } for r in readiness],
        use_container_width=True,
    )

    all_ready = all(r["ready"] for r in readiness)
    not_ready = [r for r in readiness if not r["ready"]]
    if not_ready:
        st.warning(
            "Comparison blocked until all reports exist. Missing: "
            + "; ".join(
                "%s: %s" % (r["branch_name"], ", ".join(r["missing"]))
                for r in not_ready
            )
        )

    if st.button(
        "Run comparison",
        type="primary",
        use_container_width=True,
        disabled=not all_ready,
    ):
        with RunPanel("Comparison") as panel:
            results = []
            for idx, bname in enumerate(completed, 1):
                panel.progress("compare", idx - 1, len(completed), bname, "")
                try:
                    results.append(collect_comparison_proof(bname, root=str(ROOT)))
                except Exception as exc:
                    results.append({
                        "branch_name": bname,
                        "verdict": "ERROR",
                        "summary": str(exc),
                    })
                panel.progress("compare", idx, len(completed), bname, results[-1].get("verdict", ""))
            st.session_state["last_comparisons"] = results
            summary = summarize_comparisons(results)
            st.success(
                "MATCH=%d PARTIAL=%d MISMATCH=%d INCOMPLETE=%d"
                % (summary["match"], summary.get("partial", 0), summary["mismatch"], summary["incomplete"])
            )
        st.toast("Comparison done", icon="✅")

    proof_rows = list_proof_branches(str(ROOT))
    if proof_rows:
        st.dataframe(proof_rows, use_container_width=True)

    picks = completed
    if picks:
        branch_pick = st.selectbox("Inspect branch", picks)
        bundle = load_proof_bundle(branch_pick, root=str(ROOT))
        if bundle:
            t1, t2, t3, t4 = st.tabs(["Taxonomy", "S3", "Local", "Comparison"])
            with t1:
                st.json(bundle.get("taxonomy_report") or {"message": "taxonomy_report.json not found"})
            with t2:
                st.json(bundle.get("s3_report") or {"message": "s3_report.json not found"})
            with t3:
                st.json(bundle.get("local_report") or {"message": "local_report.json not found — run Page 3"})
            with t4:
                st.json(bundle.get("comparison") or {"message": "comparison.json not found — run comparison"})


def main():
    filters = _sidebar_filters()
    t1, t2, t3, t4 = st.tabs(["Branches", "Whitebox", "Local tools", "Compare"])
    with t1:
        _tab_branches(filters)
    with t2:
        _tab_whitebox(filters)
    with t3:
        _tab_local_tools(filters)
    with t4:
        _tab_comparison(filters)


if __name__ == "__main__":
    main()
