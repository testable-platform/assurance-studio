# Metric Evaluation Scripts

## Generate SA branch codebases

```powershell
py -3 scripts/generate_sa_codebase.py all --out build
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

Reports are saved under `taxonomy_reports/<batch_id>/`.
