# Metric Evaluation

SA metric branches for Structural Analysis taxonomy validation on Testable QA.

## Metrics (6 × 4 fixed branch types = 24 branches)

| Abbrev | Classification |
|--------|----------------|
| EPI | Static Analysis Metric |
| DOV | Decision Coverage |
| LSV | Condition Coverage |
| TLCC | Logic Coverage Metric |
| TDI | Maintainability Analysis |
| QRA | Test Prioritization |

**Fixed branch types** (always generated and executed together per metric):

- **Bug** — intentional defects in the target metric module (expect FAIL on target classification)
- **BugFX** — defects fixed (expect PASS/WARN on target)
- **TCC** — tool-optimized clean code with tool configs
- **CC** — general clean code (table/lookup style, distinct from TCC)

Branch naming: `SA_<METRIC>_<TYPE>_<version>` (e.g. `SA_DOV_Bug_2.6`).

## Repository layout

```
lib/
  sa_metrics.py      # metric registry, branch naming, report paths
  sa_generator.py    # branch codebase generation + optional git deploy
  sa_validate.py     # type-specific assert validators (Bug/BugFX/TCC/CC)
  sa_qa.py           # Testable QA batch runner + HTML verification
notebooks/
  01_generate_and_validate.ipynb   # generate build/ + validate all 24 branches
  02_run_qa_and_verify.ipynb       # run on QA + verify taxonomy HTML
tools/
  export_taxonomy_html.ts          # HTML export (run from ai-testable-platform frontend)
archive/                           # superseded CLI scripts (kept for reference)
```

## How to run

### Setup

```powershell
cd D:\Metric_evaluation
py -3 -m pip install -r requirements.txt
copy .env.example .env.local
# Edit .env.local with QA credentials and BRANCHES list
```

### Notebook 1 — Generate and validate

Open `notebooks/01_generate_and_validate.ipynb` and run all cells.

This writes codebases under `build/SA_<METRIC>_<TYPE>_2.6/` and runs assert validators for all four branch types. Set `CREATE_GIT=True` (and optionally `PUSH_GIT=True`) in the parameters cell to create git branches from validated `build/` output.

### Notebook 2 — Run QA and verify

Open `notebooks/02_run_qa_and_verify.ipynb` and run all cells.

This runs whitebox on Testable QA for the selected metrics, exports taxonomy HTML, and verifies that each branch's target classification behaves as expected (Bug → FAIL on target; fixed/clean branches → not FAIL).

Reports accumulate under:

```
taxonomy_reports/Structural Analysis/<branch>_<UTC timestamp>/taxonomy-gate-*.html
```

HTML export uses `tools/export_taxonomy_html.ts` from the ai-testable-platform `web-console` directory (`npx tsx`).

### Environment

Copy `.env.example` to `.env.local` (not committed). Key variables:

| Variable | Purpose |
|----------|---------|
| `AUTH_EMAIL` / `AUTH_PASSWORD` | QA login |
| `BRANCHES` | Comma-separated branch names to run |
| `OUTPUT_DIR` | Report root (default `taxonomy_reports`) |
| `REPOSITORY_MATCH` | GitHub repo slug for catalog resolution |
| `REFRESH_BRANCHES` | Sync branch SHAs before runs (set in notebook) |

Legacy CLI scripts live under `archive/` for reference only.
