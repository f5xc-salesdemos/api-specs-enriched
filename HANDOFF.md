<!-- markdownlint-disable MD013 MD033 MD058 MD060 -->

# HANDOFF — end of phased roadmap + followup round (2026-04-21)

> **Purpose:** clean resume state for the next session. The four-phase
> roadmap that started with PR #149 landed in full, plus a four-PR
> followup round resolving the QoL followups that accumulated during
> it. Main is clean.

## 0. Resume-here status

| Stream | State | Reference |
| --- | --- | --- |
| PR #149 — self-heal stale `release/v*` branches | Merged `e07a4d9` | Closed #142 |
| PR #156 — TDD backfill for `json_writer` + `schema_fixer` | Merged `c450951` | Closed #155 |
| PR #158 — pytest CI gate + fix 16 latent drift failures | Merged `6a18f98` | Closed #157 |
| PR #162 — exponential-backoff merge-poll script | Merged `2366495` | Closed #161 |
| PR #165 — governance guard + first HANDOFF refresh | Merged `be3e0b5` | Closed #164 |
| PR #168 — pre-commit idempotency skip | Merged `50c6d2a` | Closed #167 |
| PR #171 — biome via `biomejs/setup-biome@latest` | Merged `4be419c` | Closed #154, #169 |
| PR #174 — seed `specs/original/` in tests.yml CI | Merged `90a3026` | Closed #172 |
| PR #176 — full fixture coverage (10→55 resources, 8→20 patterns) | Merged `1c95108` | Closed #175 |

Main HEAD at session end: `1c95108`.

Full-suite pytest posture: **1901 passed + 1 xfailed** (structural namespace path-extraction limit). Up from zero tests in CI at session start.

## 1. What shipped (roadmap + followups, in merge order)

### 1.1 Phase 0 — workflow self-heal (PR #149)

Adds a pre-clean block to `.github/workflows/sync-and-enrich.yml:541-554`:
detects and closes any stale open release PR (with `--delete-branch`)
or force-deletes the stale branch before creating a fresh one. All `gh`
calls are guarded with `|| true` so cleanup cannot fail the job. Uses
`$GITHUB_RUN_ID` (not `${{ github.run_id }}`) in the shell body to
stay on the safe side of workflow-injection patterns. Exercised in
production this session — PR #150 (the previous stuck release PR) was
auto-cleaned by a subsequent scheduled run.

### 1.2 Phase 1 — TDD backfill (PR #156)

New tests:

- `tests/utils/test_json_writer.py` — 23 tests on `_is_publishing_path`,
  `_is_maxsize_only`, `_format_with_biome` gating/exception paths,
  `write_json_file` end-to-end.
- `tests/utils/test_schema_fixer.py` — 42 tests including the
  `inject_max_items` isolation-from-`x-f5xc-constraints` invariant
  (Codex P1 regression guard).
- `tests/test_enricher_integration.py::TestConstraintEnricherSchemaFixerIsolation`
  — 2 tests running the real `ConstraintEnricher` →
  `SchemaFixer.inject_max_items` sequence against
  `config/constraint_patterns.yaml`.

Coverage: 100 % lines on `json_writer.py`, 96 % on `schema_fixer.py`.

### 1.3 Phase 2 — pytest CI gate + drift cleanup (PR #158)

Adds `Makefile:test` target and `.github/workflows/tests.yml` that
runs pytest on every PR. The new gate surfaced 16 pre-existing
drifts, all fixed in the same PR:

- `test_zip_security.py` (6) — `extract_zip(..., config)` and
  `validate_zip_member_size(..., limits)` signature drift.
- `test_external_docs_enricher.py` + `test_minimum_configuration_enricher.py`
  (2) — `app_firewall` regrouped under the `virtual` domain.
- `test_uniqueness_enricher.py` (3) — snake_case drift
  (`HTTPLoadBalancer` → `http_load_balancer`, `AWSVPCSite` →
  `awsvpc_site`); "platform" scope wording switched to
  "globally unique across all F5 XC tenants".
- `test_enricher_integration.py` (5) — `waf_policy` wording; two
  pattern-matcher entries graduated to explicit resources;
  count-guards `test_all_*_count` originally marked xfail for the
  config-growth delta (later expanded in PR #176).
- `tests/test_all_endpoints_enrichment.py` — `allow_module_level=True`
  on the module-scope `pytest.skip` so the module cleanly skips in
  CI when `specs/original/` is absent (later seeded by PR #174).

### 1.4 Phase 3 — exponential-backoff merge-poll (PR #162)

Replaces the hardcoded `30×10 s = 300 s` inline poll (which timed out
on every Super-Linter run > 5 min, orphaning release PRs) with:

- `scripts/release/wait-for-merge.sh` — 60 s warm-up + exponential
  backoff up to 15 min total. Emits diagnostic JSON to stderr on
  failure. Unit-tested via `tests/shell/test_wait_for_merge.py` (6
  tests against a fake-`gh` PATH stub).

Deferred guards (stale-tag-without-branch abort, concurrent-run tag
race) never bitten in the wild — see §2.

### 1.5 Phase 4 — governance guard + first HANDOFF (PR #165)

- `scripts/verify_governance.py` — pure-stdlib CLI. Reads
  `.claude/governance.json`, runs `git diff --name-only <base>..<head>`,
  exits 1 if any changed file is in `protected_files`.
- `tests/test_verify_governance.py` — 8 tests on a throwaway repo.
- `.github/workflows/tests.yml` — new `Verify no governed files
  touched` step running only on `pull_request` events.

### 1.6 Followup — pre-commit idempotency (PR #168)

Adds a STEP-0 input-fingerprint skip to
`scripts/hooks/pre-commit-pipeline.sh`. When `git diff --cached
--name-only` returns no paths under `scripts/`, `config/`,
`specs/original/`, `requirements*.txt`, `pyproject.toml`, or
`sync-and-enrich.yml`, the hook exits 0 immediately — the previous
run's enriched output is still valid. `FORCE_PIPELINE=1` overrides.
Coverage: `tests/shell/test_pre_commit_pipeline.py` (6 tests). This
ended the `core.hooksPath=/dev/null` workaround github-ops was
applying on every commit — confirmed in PR #174's commit log
("No pipeline inputs staged — skipping enrichment + lint.").

### 1.7 Followup — biome alignment (PR #171)

Mirrors docs-control#385: swap the `npm install -g
@biomejs/biome@${BIOME_VERSION}` pin for a `biomejs/setup-biome@SHA`
step with `version: latest` (same action SHA docs-control uses).
Drops `env.BIOME_VERSION`. The runtime-resolved version is captured
into `steps.biome.outputs.version` and used as the enriched-output
cache key suffix. The pipeline's Biome and docs-control's Super-Linter
Biome now resolve to the same binary on every run.

### 1.8 Followup — seed specs/original/ (PR #174)

Adds a `Seed specs/original/` step to `tests.yml` before pytest.
Runs `python -m scripts.download` with ambient `GITHUB_TOKEN` for
rate-limit headroom (api-specs is public). The 18 previously-skipped
tests in `tests/test_all_endpoints_enrichment.py` now execute on
every PR — counted and confirmed in CI logs (main baseline 1779 →
post-#174 1797).

### 1.9 Followup — fixture coverage expansion (PR #176)

`EXPLICIT_RESOURCES_FULL_PIPELINE`, `EXPLICIT_RESOURCES_PRESERVATION`,
and `PATTERN_MATCHERS` in `tests/test_enricher_integration.py` now
match the full `config/operation_descriptions.yaml`:

- 10 → **55** explicit resources
- 8 → **20** pattern matchers

Both count-guard tests (`test_all_explicit_resources_count`,
`test_all_patterns_count`) lost their xfail decorators — they now
enforce bidirectional fixture↔config parity. Only `namespace`
remains xfail (strict=True) because the enricher's
`_extract_resource_type` legitimately skips `namespaces` as a
structural path segment. Full-suite: 1797 → **1901** (+104).

## 2. Still-open followups (intentional)

- **`docs-control#383`** — upstream biome-skew tracker. Our local
  #154 is closed (PR #171 aligned us architecturally via
  `biomejs/setup-biome@latest`). A comment has been posted on #383
  asking docs-control maintainers to close it now that #385 landed.
  Not blocking; cosmetic upstream cleanup.

- **Phase-3 deferred guards.** `sync-and-enrich.yml`'s release step
  still lacks:
  - Stale-tag-without-branch abort (pre-check
    `git ls-remote origin refs/tags/v${VERSION}` before pushing).
  - Concurrent-run tag race guard. Workflow concurrency
    `cancel-in-progress: true` mitigates but doesn't guard clock-skew
    windows.
  Neither has bitten us in the wild. Merge-poll timeout (the one that
  did bite) is closed by PR #162. A future session can pick these up
  as a narrow defensive PR.

- **Codespell-governed path shapes.** PR #176 worked around codespell
  flagging the naive `{name}-plus-s` plurals of `policy`, `proxy`, and
  `discovery` as typos (codespell wants the true English plural
  forms). Workaround: use singular path segments in the fixture
  (`/alert_policy` instead of appending an `s`) — `_extract_resource_type`
  returns non-`s`-ending parts as-is, so the singular paths still
  extract correctly. `.codespellrc` is governed — a more idiomatic
  `{name} → {name}ies` pluralization in our test paths would be an
  upstream ask against docs-control.

## 3. Ground rules that persist

- **Delegate all Git/GH ops** to `f5xc-github-ops:github-ops` via the
  `f5xc-github-ops:workflow-lifecycle` skill. The main-session Bash
  tool is blocked from `git commit`, `git push`, `gh pr create`,
  `gh pr merge` by `.claude/hooks/enforce-git-delegation.sh`.
- **Managed files listed in `.claude/governance.json`** (~40 paths)
  cannot be edited locally — open an upstream issue/PR in
  `f5xc-salesdemos/docs-control` instead.
- **No `--no-verify`, no `--admin`, no `[skip ci]`, no force-push**
  without explicit authorization.
- **Pre-commit idempotency now works**: commits that don't touch
  pipeline-input paths skip the 13-min enrichment. When editing
  `scripts/`, `config/`, `specs/original/`, `requirements*.txt`,
  `pyproject.toml`, or `sync-and-enrich.yml`, the full pipeline
  still runs — budget ~15 min wall-clock.
- **CI now runs pytest on every PR** (1901 tests + 1 xfailed) plus
  the governance-drift guard. Super-Linter's Biome is aligned with
  our pipeline's Biome via `biomejs/setup-biome@latest`.

## 4. Useful links

- Closed this session: #142, #154, #155, #157, #161, #164, #167,
  #169, #172, #175.
- Still open: docs-control#383 (upstream cosmetic).
- Roadmap file:
  `/home/vscode/.claude/plans/you-need-to-do-glimmering-beaver.md`
  (historical — the roadmap landed in full).
- Workflow artefacts: `.github/workflows/sync-and-enrich.yml:541-554`
  (pre-clean), `scripts/release/wait-for-merge.sh` (merge-poll),
  `scripts/verify_governance.py` (governance guard),
  `scripts/hooks/pre-commit-pipeline.sh` (idempotent hook).
