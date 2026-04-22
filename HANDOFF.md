<!-- markdownlint-disable MD013 MD033 MD058 MD060 -->

# HANDOFF — mid-reconciliation checkpoint (2026-04-22)

> **Purpose:** clean resume state for the next session. The contract-diff
> reconciliation work (Tasks 1-9) is half complete — Commits 1 and 2 landed,
> Tasks 7-9 remain. This document describes exactly where to pick up.

## 0. Resume-here status

| Stream | State | Reference |
| --- | --- | --- |
| PR #155 — Part A issue-sync automation (api-specs) | Merged | Closed #152 |
| PR #184 — Part B contract-diff gate + extension catalog | Merged | Closed #183 |
| Issue #190 — reconciliation work in progress | **OPEN** | feature/190-contract-diff-reconciliation |

### Current branch state

- **Repo:** `/workspace/api-specs-enriched`
- **Branch:** `feature/190-contract-diff-reconciliation` (pushed to origin)
- **HEAD:** `3ef6a0b` — `feat(contract-diff): add four allowlist rules for legitimate enrichment`
- **Base:** `cd88f97` (main, includes PR #184 squash merge)
- **Plan completion:** 6 of 9 tasks done; Commits 1 and 2 landed; Tasks 7/8/9 pending

### Reference documents

- **Design spec:** `/workspace/docs/superpowers/specs/2026-04-22-contract-diff-reconciliation-design.md`
- **Implementation plan:** `/workspace/docs/superpowers/plans/2026-04-22-contract-diff-reconciliation-plan.md`
- **Prior phase spec+plan** (already shipped): `2026-04-21-api-specs-pipeline-hardening-*.md`

## 1. What's done (on this branch)

### 1.1 Commit 1 — `592ce3c`

**`fix(enricher): stop emitting title rewrites and sentinel constraints`**

Four enricher changes eliminate ~23,000 zero-info emissions:

1. **Title preservation** — `"title"` removed from all five sites that control `target_fields`:
   - `scripts/utils/acronyms.py:99` (default list)
   - `scripts/utils/branding.py:270,370,589` (three defaults)
   - `scripts/utils/grammar.py:231` (default list)
   - `config/enrichment.yaml:184-189` (config-driven list — this was the dominant site)
   - `scripts/pipeline.py:248` (in-code fallback)
2. **`minLength: 0` suppression** — removed from `validation_enricher.py::_use_default_config()` + `config/validation_rules.yaml`.
3. **`maxItems: 65535` suppression** — `DEFAULT_ARRAY_MAX_ITEMS` in `schema_fixer.py` changed from `65535` to `None`; `inject_max_items()` gained an early-return guard.
4. **int32 default-range suppression** — paired `minimum: 0 / maximum: 2147483647` removed from the integer type-default in `validation_enricher.py` + `config/validation_rules.yaml`. Legitimate ranges (port 1-65535, VLAN 1-4094) unchanged.

New tests:

- `tests/test_title_preservation.py` — 3 tests (one per enricher).
- `tests/test_sentinel_suppression.py` — 5 tests (`minLength`, `maxItems` ×2, `int32 pair`, port-preservation).

Existing tests updated to match inverted behavior:

- `tests/test_validation_enricher.py` — `test_string_type_gets_defaults`, `test_integer_type_gets_no_default_range`, `test_email_field_comprehensive_enrichment`, `test_enrich_simple_spec`.
- `tests/utils/test_schema_fixer.py` — 6 tests retrofitted to set explicit `default_max_items: 1024` instead of relying on the former 65535 sentinel.
- `tests/test_enricher_integration.py` — 2 tests updated with a `bounded_fixer` fixture.

### 1.2 Commit 2 — `3ef6a0b`

**`feat(contract-diff): add four allowlist rules for legitimate enrichment`**

`is_additive_change(change_type, pointer, before=None, after=None)` — backward-compatible signature extension — plus four new rules:

1. **Rule 1** — `_is_error_response_type_add`: allow `type: "string"` additions on 4XX/5XX response schemas.
2. **Rule 2** — `_is_positive_int_maxlength_add`: allow `maxLength` additions where `after` is int > 0.
3. **Rule 3** — `_is_additive_dict_rewrite`: recursively decompose `values_changed` on a dict; accept iff every inner change is individually additive. Depth-capped at 4 with a `RecursionError` fail-safe.
4. **Rule 4** — `_is_known_format_add`: allow `format` keys with values in the standard OpenAPI set.

Secondary fixes surfaced during real-data testing:

- **DeepDiff `threshold_to_diff_deeper=0.0`** on both outer and inner diff calls. Without it, DeepDiff's similarity heuristic collapses multi-key dict diffs into a single `values_changed` at root, which broke Rule 3.
- **Recursion-limit bump** in `contract_diff.main()` via `sys.setrecursionlimit(max(..., 20000))` for deep OpenAPI schemas.

New tests:

- `tests/test_additive_allowlist.py` — 9 new tests (positive + negative for each rule).

### 1.3 Violation trajectory against real data

| Stage | Real-data violations |
| --- | --- |
| PR #184 baseline (informational gate) | 50,231 |
| After Commit 1 (enricher tightening) | 27,034 |
| After Commit 2 (allowlist rules) | ~3,754 |

Remaining ~3,754 violations are genuine contract-drift (majority: `maxLength`-tightened values, real schema removals). These are the target of Task 8's drift-file seeding.

## 2. What's pending

### 2.1 Task 7 — fingerprint + `known_drift` support

**Files to create/modify:**

- Add `_fingerprint_violation(change_type, pointer, before, after) -> str` and `_normalize_pointer(pointer) -> str` helpers in `scripts/contract_diff.py`.
- Add `load_known_drift(path) -> set[str]` helper.
- Extend `run_contract_diff(input, output, known_drift=None)` and `run_directory_diff(input_dir, output_dir, known_drift=None)`.
- Add `--known-drift PATH` CLI flag in `main()`, default `tests/fixtures/contract_diff_known_drift.json`.
- New tests in `tests/test_contract_diff.py` (4 new) + new `tests/test_contract_diff_known_drift.py` (4 schema tests).

Details: plan §7 (Task 7).

### 2.2 Task 8 — seed drift file + file tracking issues + Commit 3

**Files to create/modify:**

- Create `scripts/contract_diff_seed_drift.py` (one-shot seed script).
- Run it, produce `tests/fixtures/contract_diff_known_drift.json` with ~3,754 entries grouped into five categories (`maxLength-tightened`, `removal`, `ref-retarget`, `operationId-rename`, `misc`).
- File four tracking issues in `f5xc-salesdemos/api-specs-enriched` via `f5xc-github-ops:github-ops`:
  1. `fix(enricher): reconcile maxLength-tightened overrides with upstream`
  2. `fix(enricher): investigate removals against upstream-preserved fields`
  3. `fix(contract): $ref retargets detected — upstream schema renames`
  4. `fix(contract): operationId renames and misc contract drift`
- Search-replace `TBD-*` placeholders in the drift file with real `owner/repo#N` issue URLs.
- End-to-end verification: local `python -m scripts.contract_diff` reports 0 violations.
- Commit 3 — drift machinery.

Details: plan §8 (Task 8).

### 2.3 Task 9 — flip gate to enforcing (Commit 4)

**Files to modify:**

- `.github/workflows/tests.yml`:
  - Remove `continue-on-error: true` from `Run contract-diff gate` step.
  - Remove the informational banner text from the PR-comment step's script.
  - Change the comment-step condition from `steps.contract_diff.outcome == 'failure'` to `failure()`.
  - Keep `continue-on-error: true` on the comment step (GitHub's 64KB cap can still fire).

Details: plan §9 (Task 9).

## 3. Quick resume commands

```bash
cd /workspace/api-specs-enriched
git fetch origin
git status                                     # confirm clean tree
git log --oneline main..HEAD                   # shows 592ce3c, 3ef6a0b
pytest -o addopts= tests/                      # baseline green run
python -m scripts.contract_diff \
    --input specs/original \
    --output docs/specifications/api \
    --report reports/contract_diff.json \
    --markdown reports/contract_diff.md
jq 'length' reports/contract_diff.json         # expect ~3754
```

Then pick up with Task 7 per the implementation plan.

## 4. Known environmental quirks (from this session)

- **Pre-commit pipeline hook** (`scripts/hooks/pre-commit-pipeline.sh`) re-runs the full enrichment pipeline whenever anything under `scripts/`, `config/`, or `specs/original/` is staged. It takes ~13-24 minutes per commit. Set `API_SPECS_SKIP_BIOME=1` if Biome is not installed locally — the pipeline will still run, just skipping the cosmetic JSON formatter. Tasks 7-8 touch `scripts/contract_diff.py` so expect the slow pre-commit; Task 9 is workflow-only (`.github/workflows/`) so it short-circuits in ~9 seconds.
- **`config/enrichment.yaml` and `config/validation_rules.yaml`** are the *actual* sources of enricher defaults; the Python `_use_default_config()` paths are only fallbacks. If fixing a sentinel emission, always check both.
- **DeepDiff with real-data dicts** requires `threshold_to_diff_deeper=0.0` to decompose multi-key rewrites; without it, large dict diffs collapse into a single `values_changed`.
- **Python recursion limit** must be bumped (~20000) before running `DeepDiff` on full OpenAPI schemas.
- **F5XC credentials** for live verification are VPN-locked lab tokens; already set in the environment when needed.

## 5. Session summary (context for resume)

The contract-diff gate landed in PR #184 as informational (`continue-on-error: true`) because a first real-data run surfaced 50,231 violations. The user directed this follow-up work to drive the gate from informational back to enforcing with zero false positives.

Strategy (three levers):

1. **Enricher tightening** — stop emitting zero-information noise (title rewrites, JSON-Schema-default sentinels). Landed in Commit 1.
2. **Allowlist extension** — four narrow rules covering legitimate enrichment (error-response typing, positive `maxLength` adds, recursive dict rewrites, known-format adds). Landed in Commit 2.
3. **Known-drift tracker** — fingerprint-keyed JSON file that suppresses per-violation residuals pending per-case triage. Tasks 7-8 land this. Task 9 flips the gate.

After the three levers land the real-data gate reports 0 violations and the `continue-on-error: true` is removed.

Four tracking issues (per the plan) will own the residual ~3,754 fingerprints — each is a real gap between enricher behavior and spec §4.3, to be resolved continuously over time.
