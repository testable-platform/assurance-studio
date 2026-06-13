# Taxonomy vs S3 vs Build Comparison

Generated: 2026-06-12 15:23:47 UTC

## Repo context

Branches are generated under `build/<TECH>_<METRIC>_<TYPE>_<VERSION>/` with:
- a **target** module (`sa/<module_key>.py`) containing the intentional defect variant
- **stub** modules for sibling metrics

| Source | Metric | Branches |
|--------|--------|----------|
| `taxonomy_reports/Structural Analysis/` | **DOV** (Decision Coverage) | SA_DOV_{Bug,BugFX,TCC,CC}_2.6 |
| `s3_downloads/.../afb346d7.../` | **EPI** (Execution Path Integrity) | SA_EPI_{Bug,BugFX,TCC,CC}_2.6 |
| `build/` | both DOV + EPI | local generated checkouts |

> Taxonomy was collected for **DOV** (per notebook). S3 bundle is from **EPI** runs.
> Comparisons use **branch type** (Bug / BugFX / TCC / CC) as the join key.

---

## Way 1 — Taxonomy vs S3 tool reports

For each branch type, every Structural Analysis metric row in the taxonomy HTML
is compared to the pass/fail derived from the matching S3 tool JSON.

### Bug (`SA_DOV_Bug_2.6` taxonomy ↔ `SA_EPI_Bug_2.6` s3)

| Metric | Taxonomy | S3 tool | Aligned |
|--------|----------|---------|---------|
| DOV **(target)** | PASS | FAIL | **✗** |
| EPI | PASS | PASS | ✓ |
| LSV | PASS | FAIL | **✗** |
| QRA | FAIL | FAIL | ✓ |
| TDI | FAIL | PASS | **✗** |
| TLCC | PASS | PASS | ✓ |

- Target taxonomy verify: **FAIL**
- Target row aligned with S3: **no**
- Commits differ: taxonomy `e0401dc2f0a1` vs s3 `f97f58dbd863`

### BugFX (`SA_DOV_BugFX_2.6` taxonomy ↔ `SA_EPI_BugFX_2.6` s3)

| Metric | Taxonomy | S3 tool | Aligned |
|--------|----------|---------|---------|
| DOV **(target)** | PASS | FAIL | **✗** |
| EPI | PASS | PASS | ✓ |
| LSV | PASS | FAIL | **✗** |
| QRA | FAIL | FAIL | ✓ |
| TDI | FAIL | PASS | **✗** |
| TLCC | PASS | PASS | ✓ |

- Target taxonomy verify: **PASS**
- Target row aligned with S3: **no**
- Commits differ: taxonomy `1b3d8642dfc5` vs s3 `ead6b3dc4317`

### TCC (`SA_DOV_TCC_2.6` taxonomy ↔ `SA_EPI_TCC_2.6` s3)

| Metric | Taxonomy | S3 tool | Aligned |
|--------|----------|---------|---------|
| DOV **(target)** | PASS | FAIL | **✗** |
| EPI | PASS | PASS | ✓ |
| LSV | PASS | FAIL | **✗** |
| QRA | FAIL | FAIL | ✓ |
| TDI | FAIL | PASS | **✗** |
| TLCC | PASS | PASS | ✓ |

- Target taxonomy verify: **PASS**
- Target row aligned with S3: **no**
- Commits differ: taxonomy `2e7e27363ebf` vs s3 `9d5f13175bbe`

### CC (`SA_DOV_CC_2.6` taxonomy ↔ `SA_EPI_CC_2.6` s3)

| Metric | Taxonomy | S3 tool | Aligned |
|--------|----------|---------|---------|
| DOV **(target)** | PASS | FAIL | **✗** |
| EPI | PASS | PASS | ✓ |
| LSV | PASS | FAIL | **✗** |
| QRA | FAIL | FAIL | ✓ |
| TDI | FAIL | PASS | **✗** |
| TLCC | PASS | PASS | ✓ |

- Target taxonomy verify: **PASS**
- Target row aligned with S3: **no**
- Commits differ: taxonomy `6841f1e7c0d2` vs s3 `686c11adc5c4`

---

## Way 2 — Taxonomy + S3 vs local `build/` repos

### DOV (taxonomy target metric) — triple comparison

| Type | Taxonomy | S3 (coverage-py) | Build (Coverage.py) | Tax≡S3 | Tax≡Build | S3≡Build | Expected |
|------|----------|------------------|---------------------|--------|-----------|----------|----------|
| Bug | PASS | FAIL | FAIL (PASS) | ✗ | ✗ | ✓ | FAIL |
| BugFX | PASS | FAIL | PASS (PASS) | ✗ | ✓ | ✗ | FAIL |
| TCC | PASS | FAIL | PASS (PASS) | ✗ | ✓ | ✗ | FAIL |
| CC | PASS | FAIL | PASS (PASS) | ✗ | ✓ | ✗ | FAIL |

### EPI (S3 run metric) — taxonomy EPI row vs S3 vs build

| Type | Taxonomy (EPI row) | S3 (crosshair) | Build (Crosshair) | Tax≡S3 | S3≡Build | Expected |
|------|-------------------|----------------|-------------------|--------|----------|----------|
| Bug | PASS | PASS | SKIPPED (SKIPPED) | ✓ | ✗ | FAIL |
| BugFX | PASS | PASS | PASS (PASS) | ✓ | ✓ | PASS |
| TCC | PASS | PASS | PASS (PASS) | ✓ | ✓ | PASS |
| CC | PASS | PASS | PASS (PASS) | ✓ | ✓ | PASS |

### Build paths

- **Bug**: `D:\Metric_evaluation\build\SA_DOV_Bug_2.6` | `D:\Metric_evaluation\build\SA_EPI_Bug_2.6`
- **BugFX**: `D:\Metric_evaluation\build\SA_DOV_BugFX_2.6` | `D:\Metric_evaluation\build\SA_EPI_BugFX_2.6`
- **TCC**: `D:\Metric_evaluation\build\SA_DOV_TCC_2.6` | `D:\Metric_evaluation\build\SA_EPI_TCC_2.6`
- **CC**: `D:\Metric_evaluation\build\SA_DOV_CC_2.6` | `D:\Metric_evaluation\build\SA_EPI_CC_2.6`