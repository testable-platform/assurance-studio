# Metric Evaluation Scripts

## Generate SA branch codebases

```powershell
py -3 scripts/generate_sa_codebase.py all --out build
## Metric-level branches (SA_EPI_Bug_2.6, ...)

```powershell
py -3 scripts/generate_sa_metric_codebase.py --metric all
py -3 scripts/create_metric_branches.py
git push -u origin SA_EPI_Bug_2.6 SA_DOV_Bug_2.6 SA_LSV_Bug_2.6 SA_TLCC_Bug_2.6 SA_TDI_Bug_2.6 SA_QRA_Bug_2.6
py -3 scripts/run_sa_taxonomy_batch.py --refresh-branches --branches SA_EPI_Bug_2.6
py -3 scripts/verify_taxonomy_html.py --dir taxonomy_reports\<batch_id>
```

## Legacy technique-level branches

py -3 scripts/deploy_one_branch.py SA_bug_2.6
```

## Run taxonomy batch (Testable platform)

1. Copy `.env.example` to `.env.local` and fill credentials.
2. Ensure platform is running (`http://localhost:3000`).
3. Connect GitHub SCM in the UI (required for all branches to appear).
4. Run:

```powershell
py -3 scripts/run_sa_taxonomy_batch.py --ensure-project --refresh-branches
```

Partial run (only branches already in catalog):

```powershell
py -3 scripts/run_sa_taxonomy_batch.py --allow-partial-branches --branches SA_bug_2.6
```

Reports are saved under `taxonomy_reports/<batch_id>/` **only after**:
1. The whitebox run reaches `completed` status (`REQUIRE_RUN_COMPLETED=true` by default)
2. The taxonomy gate reports `gate_status: completed`

Set `REQUIRE_RUN_COMPLETED=false` to save reports on failed/partial runs once the gate is ready.
