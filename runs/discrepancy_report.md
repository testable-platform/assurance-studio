# DOV Discrepancy Report

Generated: 2026-06-12 16:05:44 UTC

## Summary

- Branches compared: **4**
- MATCH: **0** | DISCREPANCY: **4**
- Taxonomy target verify PASS: **3** / **4**

## Comparison A + B — Taxonomy | S3 (coverage-py) | Build (tool_assert)

| Branch | Expected | Taxonomy | S3 (coverage-py) | Build (tool_assert) | Status |
|--------|----------|----------|------------------|---------------------|--------|
| SA_DOV_BugFX_2.6 | PASS/WARN | PASS | FAIL | PASS (PASS) | **DISCREPANCY** |
| SA_DOV_Bug_2.6 | FAIL | PASS | FAIL | FAIL (PASS) | **DISCREPANCY** |
| SA_DOV_CC_2.6 | PASS/WARN | PASS | FAIL | PASS (PASS) | **DISCREPANCY** |
| SA_DOV_TCC_2.6 | PASS/WARN | PASS | FAIL | PASS (PASS) | **DISCREPANCY** |

## Discrepancy notes

### SA_DOV_BugFX_2.6
- Expected: **PASS/WARN**
- Taxonomy: **PASS** (verify ok: True)
- Taxonomy value: `100/100`
- S3: **FAIL** (coverage file status: EMPTY)
- S3 coverage %: 0.0
- Build: **PASS** (`8.0% cov tests=124`)
- Taxonomy HTML: `D:\Metric_evaluation\taxonomy_reports\Structural Analysis\SA_DOV_BugFX_2.6\SA_DOV_BugFX_2.6_20260612T132310Z\taxonomy-gate.html`
- S3 coverage.json: `D:\Metric_evaluation\s3_downloads\5009fa1f-3a98-413b-8bed-1c28b4dede46\6accd063-50a6-4655-b831-36cd440b6e7b\SA_DOV_BugFX_2.6\1b3d8642dfc583eebfa84790371852355fd28f64\74f2568a-c90c-4173-9e74-1ab402672cd9\coverage-py\0\coverage.json`
- Build path: `d:\Metric_evaluation\build\SA_DOV_BugFX_2.6`

### SA_DOV_Bug_2.6
- Expected: **FAIL**
- Taxonomy: **PASS** (verify ok: False)
- Taxonomy value: `100/100`
- S3: **FAIL** (coverage file status: EMPTY)
- S3 coverage %: 0.0
- Build: **FAIL** (`4.0% cov tests=1`)
- Taxonomy HTML: `D:\Metric_evaluation\taxonomy_reports\Structural Analysis\SA_DOV_Bug_2.6\SA_DOV_Bug_2.6_20260612T133912Z\taxonomy-gate.html`
- S3 coverage.json: `D:\Metric_evaluation\s3_downloads\5009fa1f-3a98-413b-8bed-1c28b4dede46\ad598af5-26e0-41c2-b914-4c8a20ffc778\SA_DOV_Bug_2.6\e0401dc2f0a1c79830c26b457551f94202f405cd\70cf47e4-b1ef-4fba-9f89-adaf2c9cf1ab\coverage-py\0\coverage.json`
- Build path: `d:\Metric_evaluation\build\SA_DOV_Bug_2.6`

### SA_DOV_CC_2.6
- Expected: **PASS/WARN**
- Taxonomy: **PASS** (verify ok: True)
- Taxonomy value: `100/100`
- S3: **FAIL** (coverage file status: EMPTY)
- S3 coverage %: 0.0
- Build: **PASS** (`11.0% cov tests=124`)
- Taxonomy HTML: `D:\Metric_evaluation\taxonomy_reports\Structural Analysis\SA_DOV_CC_2.6\SA_DOV_CC_2.6_20260612T132803Z\taxonomy-gate.html`
- S3 coverage.json: `D:\Metric_evaluation\s3_downloads\5009fa1f-3a98-413b-8bed-1c28b4dede46\d9c77c6c-da51-4935-9858-b222278102ef\SA_DOV_CC_2.6\6841f1e7c0d20e175bcae40d4baa4905f4f6102c\5aedff64-de79-44c7-b05c-215d099cdd21\coverage-py\0\coverage.json`
- Build path: `d:\Metric_evaluation\build\SA_DOV_CC_2.6`

### SA_DOV_TCC_2.6
- Expected: **PASS/WARN**
- Taxonomy: **PASS** (verify ok: True)
- Taxonomy value: `100/100`
- S3: **FAIL** (coverage file status: EMPTY)
- S3 coverage %: 0.0
- Build: **PASS** (`7.0% cov tests=124`)
- Taxonomy HTML: `D:\Metric_evaluation\taxonomy_reports\Structural Analysis\SA_DOV_TCC_2.6\SA_DOV_TCC_2.6_20260612T132552Z\taxonomy-gate.html`
- S3 coverage.json: `D:\Metric_evaluation\s3_downloads\5009fa1f-3a98-413b-8bed-1c28b4dede46\1a165e4e-465c-4131-acc6-49d3ec084567\SA_DOV_TCC_2.6\2e7e27363ebfe83057095b8954a9b2d06ab6f3fd\d91b5dad-0da0-4c69-a97a-b3a82b403617\coverage-py\0\coverage.json`
- Build path: `d:\Metric_evaluation\build\SA_DOV_TCC_2.6`


## Manual verification

For each branch, complete the checklist below after automated comparison.

### SA_DOV_BugFX_2.6

- [ ] Checkout commit `1b3d8642dfc583eebfa84790371852355fd28f64`
- [ ] Confirm seeded marker in `sa/decision_coverage.py` (Bug: `escalated-` + decision_case functions)
- [ ] Run local coverage on `sa/decision_coverage.py`; compare to S3 `coverage.json`
- [ ] Open taxonomy HTML; confirm Decision Coverage row matches local run
- [ ] Confirm `tool_assert_branch(build/SA_DOV_BugFX_2.6)` matches manual coverage
- [ ] **Manual result:** confirmed / not confirmed — notes:

### SA_DOV_Bug_2.6

- [ ] Checkout commit `e0401dc2f0a1c79830c26b457551f94202f405cd`
- [ ] Confirm seeded marker in `sa/decision_coverage.py` (Bug: `escalated-` + decision_case functions)
- [ ] Run local coverage on `sa/decision_coverage.py`; compare to S3 `coverage.json`
- [ ] Open taxonomy HTML; confirm Decision Coverage row matches local run
- [ ] Confirm `tool_assert_branch(build/SA_DOV_Bug_2.6)` matches manual coverage
- [ ] **Manual result:** confirmed / not confirmed — notes:

### SA_DOV_CC_2.6

- [ ] Checkout commit `6841f1e7c0d20e175bcae40d4baa4905f4f6102c`
- [ ] Confirm seeded marker in `sa/decision_coverage.py` (Bug: `escalated-` + decision_case functions)
- [ ] Run local coverage on `sa/decision_coverage.py`; compare to S3 `coverage.json`
- [ ] Open taxonomy HTML; confirm Decision Coverage row matches local run
- [ ] Confirm `tool_assert_branch(build/SA_DOV_CC_2.6)` matches manual coverage
- [ ] **Manual result:** confirmed / not confirmed — notes:

### SA_DOV_TCC_2.6

- [ ] Checkout commit `2e7e27363ebfe83057095b8954a9b2d06ab6f3fd`
- [ ] Confirm seeded marker in `sa/decision_coverage.py` (Bug: `escalated-` + decision_case functions)
- [ ] Run local coverage on `sa/decision_coverage.py`; compare to S3 `coverage.json`
- [ ] Open taxonomy HTML; confirm Decision Coverage row matches local run
- [ ] Confirm `tool_assert_branch(build/SA_DOV_TCC_2.6)` matches manual coverage
- [ ] **Manual result:** confirmed / not confirmed — notes:
