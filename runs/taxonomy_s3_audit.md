# Taxonomy vs S3 Tool Reports Audit

Generated: 2026-06-12 14:58:23 UTC

## Summary

| Metric | Count |
|--------|-------|
| Branches with taxonomy report | 4 |
| Branches with S3 tool bundle | 4 |
| Matched branch pairs | 0 |
| Taxonomy-only (no S3 bundle) | 4 |
| S3-only (no taxonomy report) | 4 |
| Taxonomy target verify PASS | 3 |
| Taxonomy target verify FAIL | 1 |
| S3 primary tool verify PASS | 3 |
| S3 primary tool verify FAIL | 1 |

> **Note:** Taxonomy and S3 bundles must share the same branch name to be cross-checked.
> Unpaired branches are still audited independently.

## Per-branch results

### `SA_DOV_BugFX_2.6` (TAXONOMY_ONLY)
- **Taxonomy:** PASS — target `DOV` = **PASS**
  - HTML: `D:\Metric_evaluation\taxonomy_reports\Structural Analysis\SA_DOV_BugFX_2.6\SA_DOV_BugFX_2.6_20260612T132310Z\taxonomy-gate.html`
  - Commit: `1b3d8642dfc583eebfa84790371852355fd28f64` | Run: `74f2568a-c90c-4173-9e74-1ab402672cd9`
- **S3 tools:** not found

### `SA_DOV_Bug_2.6` (TAXONOMY_ONLY)
- **Taxonomy:** FAIL — target `DOV` = **PASS**
  - HTML: `D:\Metric_evaluation\taxonomy_reports\Structural Analysis\SA_DOV_Bug_2.6\SA_DOV_Bug_2.6_20260612T133912Z\taxonomy-gate.html`
  - Commit: `e0401dc2f0a1c79830c26b457551f94202f405cd` | Run: `70cf47e4-b1ef-4fba-9f89-adaf2c9cf1ab`
- **S3 tools:** not found

### `SA_DOV_CC_2.6` (TAXONOMY_ONLY)
- **Taxonomy:** PASS — target `DOV` = **PASS**
  - HTML: `D:\Metric_evaluation\taxonomy_reports\Structural Analysis\SA_DOV_CC_2.6\SA_DOV_CC_2.6_20260612T132803Z\taxonomy-gate.html`
  - Commit: `6841f1e7c0d20e175bcae40d4baa4905f4f6102c` | Run: `5aedff64-de79-44c7-b05c-215d099cdd21`
- **S3 tools:** not found

### `SA_DOV_TCC_2.6` (TAXONOMY_ONLY)
- **Taxonomy:** PASS — target `DOV` = **PASS**
  - HTML: `D:\Metric_evaluation\taxonomy_reports\Structural Analysis\SA_DOV_TCC_2.6\SA_DOV_TCC_2.6_20260612T132552Z\taxonomy-gate.html`
  - Commit: `2e7e27363ebfe83057095b8954a9b2d06ab6f3fd` | Run: `d91b5dad-0da0-4c69-a97a-b3a82b403617`
- **S3 tools:** not found

### `SA_EPI_BugFX_2.6` (S3_ONLY)
- **Taxonomy:** not found
- **S3 primary tool:** PASS — outcome **PASS** (Crosshair)
  - Path: `D:\Metric_evaluation\s3_downloads\afb346d7-6a48-4f19-bdc6-56b77367ded4\53aee55f-0465-4613-b600-88964d11cbcb\SA_EPI_BugFX_2.6\ead6b3dc431777ea991fa749740db347099da0ae\5e2467d3-c064-4325-b9cf-0573e766edf5`
  - Commit: `ead6b3dc431777ea991fa749740db347099da0ae` | Tools: 28
  - Detail: `{"execution_path_integrity_pct": 100.0, "functions_with_counterexample": 0.0, "boundary_issue_ratio": 0.0}`

### `SA_EPI_Bug_2.6` (S3_ONLY)
- **Taxonomy:** not found
- **S3 primary tool:** FAIL — outcome **PASS** (Crosshair)
  - Path: `D:\Metric_evaluation\s3_downloads\afb346d7-6a48-4f19-bdc6-56b77367ded4\92e14eb6-41c7-4d32-98af-6a67e89f9441\SA_EPI_Bug_2.6\f97f58dbd863d9b7faea3083cb60d548024ec8b3\a747494a-a382-4982-bf19-ad9354a7d828`
  - Commit: `f97f58dbd863d9b7faea3083cb60d548024ec8b3` | Tools: 28
  - Detail: `{"execution_path_integrity_pct": 100.0, "functions_with_counterexample": 0.0, "boundary_issue_ratio": 0.0}`

### `SA_EPI_CC_2.6` (S3_ONLY)
- **Taxonomy:** not found
- **S3 primary tool:** PASS — outcome **PASS** (Crosshair)
  - Path: `D:\Metric_evaluation\s3_downloads\afb346d7-6a48-4f19-bdc6-56b77367ded4\1126d1b3-9bdd-4aba-b680-a38c599c7940\SA_EPI_CC_2.6\686c11adc5c4c1fcb874a90182b91e2b3d27bef5\4cf8c7a1-f871-4d0b-958e-1f1672f0e8d2`
  - Commit: `686c11adc5c4c1fcb874a90182b91e2b3d27bef5` | Tools: 28
  - Detail: `{"execution_path_integrity_pct": 100.0, "functions_with_counterexample": 0.0, "boundary_issue_ratio": 0.0}`

### `SA_EPI_TCC_2.6` (S3_ONLY)
- **Taxonomy:** not found
- **S3 primary tool:** PASS — outcome **PASS** (Crosshair)
  - Path: `D:\Metric_evaluation\s3_downloads\afb346d7-6a48-4f19-bdc6-56b77367ded4\e6dc257f-10e4-4dd6-8099-f90d33fcce6e\SA_EPI_TCC_2.6\9d5f13175bbefe76a7e50c0c57d35ed1639f9db0\82f5fe2b-04c7-4c6d-80ce-f3f51efb2d7f`
  - Commit: `9d5f13175bbefe76a7e50c0c57d35ed1639f9db0` | Tools: 28
  - Detail: `{"execution_path_integrity_pct": 100.0, "functions_with_counterexample": 0.0, "boundary_issue_ratio": 0.0}`
