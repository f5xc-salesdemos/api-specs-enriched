<!-- markdownlint-disable MD013 MD033 MD058 MD060 -->

# HANDOFF — Release Pipeline Unblock (PR #138, Issue #137)

> **Purpose:** This file is the session handoff so that Claude Code can
> resume this task after a container rebuild in an ephemeral environment.
> Read it first on any new session. Everything below reflects state as of
> the last push to `fix/137-unblock-release-auto-merge` on 2026-04-20.

## 0. Plan — Status Table

Read this first. ✅ = merged-or-pushed and verified. 🟡 = work done locally
but not yet on the branch tip. ⬜ = not started. ▶ = resume here.

| #   | Step                                                                                               | Status     | Notes                                                                                                        |
| --- | -------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------ |
| 0.1 | Diagnose why PR #127 (v2.1.62) auto-merge times out                                                | ✅ done    | Root cause: `[skip ci]` in release commit + Super-Linter is `pull_request`-only                              |
| 0.2 | Diagnose why PR #136 (governance sync) Super-Linter fails                                          | ✅ done    | Docs-control's generic lint configs conflict with this repo's tuned `pyproject.toml`; ~680 findings          |
| 0.3 | Decide strategy: fix at source vs. config skip                                                     | ✅ done    | User chose: enforce biome at generator source; reject docs-control sync; coordinate via upstream issue      |
| 0.4 | Issue #137 opened + branch `fix/137-unblock-release-auto-merge` created                            | ✅ done    | By github-ops agent                                                                                          |
| 0.5 | Commit 27fb822: json_writer.py + 4 save_spec delegations + biome env pin + `[skip ci]` removal     | ✅ pushed  | 48 files. PR #138 open.                                                                                     |
| 0.6 | PR #138 CI run 24640402025 — confirm BIOME_FORMAT passes                                           | ✅ passed  | 19 of 20 Super-Linter sub-checks green, including BIOME_FORMAT and BIOME_LINT                               |
| 0.7 | PR #138 CI run 24640402025 — CHECKOV failure surfaces                                              | ✅ known   | CKV_OPENAPI_21 — 7,348 of 9,587 array schemas in enriched JSONs lack `maxItems`                             |
| 0.8 | Decide CHECKOV mitigation                                                                          | ✅ done    | User chose: extend `SchemaFixer` to inject `maxItems: 65535` on arrays missing it                            |
| 0.9 | Edit `scripts/utils/schema_fixer.py` to inject `maxItems` + `get_stats` updates                    | 🟡 in tree | Unit-tested locally (`max_items_added: 1` on synthetic spec). Ruff + mypy clean.                            |
| 1.0 | Regenerate all enriched JSONs via `python3 -m scripts.pipeline`                                    | 🟡 mid-run | Pipeline was running at container reboot time. **Re-run on boot.**                                          |
| 1.1 | Verify checkov locally: `checkov -f <file> --framework openapi` passes                             | ⬜ ▶ next  | Run after pipeline finishes on reboot                                                                        |
| 1.2 | Verify biome + spectral still clean on regenerated tree                                            | ⬜ ▶       | `biome format docs/specifications/api/*.json` and `python3 scripts/lint.py --fail-on-error --fail-on-warning` |
| 1.3 | Delegate commit + push + CI poll to github-ops                                                     | ⬜ ▶       | Pass `Issue: #137`, `Branch: fix/137-unblock-release-auto-merge` — reuse the PR, do not create duplicates    |
| 1.4 | CI passes all 4 required checks on PR #138                                                         | ⬜         | Expect BIOME_FORMAT + BIOME_LINT + CHECKOV + the 2 sanity checks                                             |
| 1.5 | Merge PR #138 (squash)                                                                             | ⬜         | Branch auto-deletes via repo settings                                                                        |
| 1.6 | Post-merge: next scheduled `sync-and-enrich` run creates a v2.1.62 (or v2.1.63) release PR         | ⬜         | This is the end-to-end validation. Release PR should auto-merge within the 5-minute poll window              |
| 2.1 | Cleanup: close **issue #113** (downstream-dispatch failure from 2026-04-18; resolved by `f6c8c83`) | ⬜         | Comment: "Resolved by `f6c8c83` merged 2026-04-18 18:08 UTC; run 24610732291 succeeded."                     |
| 2.2 | Cleanup: close **issue #128** (auto-created workflow-failure for v2.1.62)                          | ⬜         | Comment with link to merged PR #138                                                                          |
| 2.3 | Cleanup: close **issue #129** — superseded by #135                                                 | ⬜         | Both are governance-bot duplicates                                                                           |
| 2.4 | Cleanup: close **issue #135** + **PR #136** (governance sync)                                      | ⬜         | Rationale: would force-replace tuned pyproject.toml configs; see docs-control issue                          |
| 2.5 | Open **docs-control issue**: "Request: reconsider lint config sync strategy for api-specs-enriched" | ⬜         | Propose either unmanaging ruff.toml/.mypy.ini/.python-lint for this repo, or `extend = "pyproject.toml"`    |
| 3.1 | Verify a fresh scheduled run produces a clean release PR end-to-end                                | ⬜         | Cron runs at 06:00 UTC daily; can also `workflow_dispatch` to trigger                                       |
| 3.2 | Verify downstream dispatch to `xcsh` + `vscode-f5xc-tools` succeeds post-release                   | ⬜         | Watch for issues like the old #113                                                                          |

## 1. The Goal

Make the `api-specs-enriched` end-to-end release pipeline work —
download published upstream API specs → enrich → version-bump → open
release PR → auto-merge → tag → dispatch to downstream repos
(`xcsh`, `vscode-f5xc-tools`). This was broken on `main`: the automated
release PR (PR #127, v2.1.62) timed out on "PR did not merge within
timeout" every night, and two older workflow-failure issues were open
(#113, #128).

## 2. What Has Been Done

### 2.1 Root-cause analysis (archived in earlier session)

- **PR #127 (v2.1.62 release) times out** because required CI check
  `lint / Lint Code Base` (Super-Linter) never runs on the release PR.
  The release commit message ends with `[skip ci]`, which suppresses all
  `pull_request`-triggered workflows. Auto-merge waits indefinitely.
- **Super-Linter's BIOME_FORMAT would also fail** on the committed
  enriched JSONs even if it ran, because the pipeline's `biome format`
  call was silent-best-effort (suppressed `FileNotFoundError`, `check=False`)
  and two of the four `save_spec()` variants didn't call biome at all.
- **Cache amplifies the drift** — the `docs/specifications/api/` GitHub
  Actions cache stored pre-biome-formatted JSONs. A cache hit skipped the
  pipeline entirely, so cached stale output got force-staged into release PRs.

### 2.2 Decisions made in-session (confirmed by user)

| Topic                                  | Decision                                                                                                                             |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Docs-control sync (PR #136)            | Push back upstream — close with rationale, open docs-control issue                                                                   |
| Release PR fix approach                | Remove `[skip ci]`; enforce biome at generator source; invalidate cache on biome upgrade                                             |
| Pre-existing linting errors in `tests/**` | Out of scope for this PR (confirmed; pyproject.toml-based config is preserved)                                                    |
| Biome gap mitigation                   | **Fix at source** — no workflow-level `biome format --write` band-aid; make biome formatting a hard requirement in Python generators |
| CHECKOV CKV_OPENAPI_21 mitigation      | Extend `SchemaFixer` to inject a default `maxItems` on every array schema missing one (generous `65535`)                             |

### 2.3 Code changes committed to branch `fix/137-unblock-release-auto-merge`

Commit **`27fb822 fix: enforce Biome-compliant generator output at the source`**
is already on the branch and pushed — 48 files, linked to issue #137, PR #138.

1. **`scripts/utils/json_writer.py`** — new file. Single source of truth
   for writing JSON into Super-Linter-scanned paths
   (`docs/specifications/api/**`, `docs/api-reference/**`). Runs
   `biome format --write` after `json.dump`, raises `BiomeNotFoundError`
   if biome is missing and `BiomeFormatError` on biome failure. Has a
   `_is_maxsize_only()` helper that tolerates biome's "file exceeds
   `files.maxSize`" warning the same way Super-Linter does in its
   multi-file mode (non-zero exit but only the size warning is a no-op).
   `API_SPECS_SKIP_BIOME=1` env is the escape hatch for local/test runs
   that won't commit output.

2. **Four `save_spec()` functions unified onto `write_json_file`:**
   - `scripts/pipeline.py:save_spec` — delegated
   - `scripts/merge_specs.py:save_spec` + the index write at line ~528
   - `scripts/enrich.py:save_spec` (previously no biome at all)
   - `scripts/normalize.py:save_spec` (previously no biome at all)
   - `scripts/utils/validation_exporter.py` — `docs/specifications/api/validation.json`
     writer goes through `write_json_file`

3. **`.github/workflows/sync-and-enrich.yml`** three changes:
   - Added `env.BIOME_VERSION: '2.4.12'` and pinned
     `npm install -g "@biomejs/biome@${BIOME_VERSION}"`.
   - Threaded `-biome-${{ env.BIOME_VERSION }}` into both the restore
     and save enriched-output cache keys, so a biome upgrade busts the
     cache and forces a clean re-run.
   - **Removed `[skip ci]`** from the release commit message on
     line ~545. The push trigger's existing `paths:` filter
     (`scripts/**`, `config/**`, `requirements.txt`, this workflow file,
     `docs/**/*.html`) already excludes every path the release commit
     touches — no recursion risk.

4. **`docs/specifications/api/*.json`** — 38 enriched JSONs reformatted
   once with `biome format --write` (plus `virtual.json`, `openapi.json`,
   `sites.json` picked up by the pre-commit auto-stage of
   `docs/specifications/api/*.json`). Content unchanged; spectral lint
   still passes 39/39.

### 2.4 Code changes NOT yet committed (in the working tree)

- **`scripts/utils/schema_fixer.py`** — adds a new fix: injects
  `maxItems: 65535` into every array schema that lacks one. New config
  knobs `fix_missing_max_items` (default `True`) and `default_max_items`
  (default `65535`) live under `schema_fixes:` in `config/enrichment.yaml`.
  Upstream-set `maxItems` values are preserved. New stats:
  `max_items_added`, `fix_missing_max_items`, `default_max_items`.

  Why: Super-Linter's CHECKOV sub-linter fails CKV_OPENAPI_21 on the 41
  enriched JSONs in PR #138 because 7,348 of 9,587 array schemas lack
  `maxItems`. Local `checkov --config-file .checkov.yaml -d .` reports
  0 failures because directory-mode skips OpenAPI framework detection,
  but Super-Linter invokes `checkov -f <file>` per file, which triggers
  the OpenAPI framework and surfaces the finding.

- **`docs/specifications/api/*.json`** — in the process of being
  regenerated by `python3 -m scripts.pipeline` (running in a prior
  session's background task). May not be complete on disk. Re-run the
  pipeline on boot to produce a clean set.

### 2.5 PR #138 status

- URL: <https://github.com/f5xc-salesdemos/api-specs-enriched/pull/138>
- Branch: `fix/137-unblock-release-auto-merge`
- Base: `main`
- Head commit at last push: `27fb822`
- CI result of that commit:
  | Check                     | Result          | Meaning                                                                           |
  | ------------------------- | --------------- | --------------------------------------------------------------------------------- |
  | `check / Check linked issues` | ✅ SUCCESS      | —                                                                                 |
  | `Validate PR`                 | ✅ SUCCESS      | —                                                                                 |
  | `Dependabot Auto-Merge`       | SKIPPED         | Not a dependabot PR                                                               |
  | `auto-merge`                  | SKIPPED         | Auto-merge hasn't been enabled yet                                                |
  | `lint / Lint Code Base`       | ❌ FAILURE      | **19 of 20 Super-Linter sub-checks passed** including BIOME_FORMAT and BIOME_LINT |

  The only failing sub-check is CHECKOV — exactly what the uncommitted
  `SchemaFixer` change is designed to fix.

### 2.6 Deferred cleanup (contingent on PR #138 merge)

Not yet done — do these **after** PR #138 merges:

1. Close **issue #113** — "Notify Downstream Repositories … Dispatch to
   vscode-f5xc-tools". Resolved by commit `f6c8c83` merged 2026-04-18
   18:08 UTC; subsequent scheduled run `24610732291` succeeded.
2. Close **issue #128** — auto-created "Commit and tag release" workflow
   failure for v2.1.62. PR #138 addresses it directly; close with a link
   to the merge commit.
3. Close **issue #129** — older duplicate of issue #135 (both
   auto-generated by the managed-files governance sync bot). Mark
   superseded.
4. Close **issue #135** + **PR #136** — governance sync would force
   replacement of the repo's tuned `pyproject.toml` lint config with
   generic docs-control configs, surfacing ~680 pre-existing style
   findings that are intentional repo patterns. Decision: reject with
   rationale; coordinate via the docs-control issue below.
5. **Open an issue in `f5xc-salesdemos/docs-control`** titled
   "Request: reconsider lint config sync strategy for api-specs-enriched".
   Body:
   - The canonical standalone `ruff.toml`, `.mypy.ini`, `.python-lint`
     conflict with this repo's `pyproject.toml` per-file-ignores
     (tuned for `tests/**`, `scripts/discover.py`, `scripts/enrich.py`,
     `scripts/analyze_constraints.py`).
   - Proposal: (a) unmanage these three files for `api-specs-enriched`,
     OR (b) change the canonical versions to `extend = "pyproject.toml"`.
   - Cross-reference closed PR #136.

## 3. Where To Pick Up On Reboot

**The `main` CLAUDE.md policy delegates all Git + gh operations to
`f5xc-github-ops:github-ops` (invoked via the `workflow-lifecycle`
skill). Keep doing that — do not run `git commit` / `git push` /
`gh pr create` directly from the main session.**

### 3.1 First-session bootstrap

```bash
# 1. Clean checkout of the branch (not main)
cd /workspace/api-specs-enriched
git fetch origin fix/137-unblock-release-auto-merge:refs/remotes/origin/fix/137-unblock-release-auto-merge
git checkout fix/137-unblock-release-auto-merge
git pull --ff-only origin fix/137-unblock-release-auto-merge

# 2. Re-download upstream specs (specs/original/ is gitignored).
#    The pre-commit hook's enrichment pipeline requires this to exist.
python3 -m scripts.download
# Expect ~520 files in specs/original/

# 3. Install any missing Python deps. Most pain point is openapi_spec_validator.
pip install --quiet openapi-spec-validator types-PyYAML

# 4. Sanity check: biome is available at the pinned version.
biome --version   # should report 2.4.12 (see BIOME_VERSION in
                  # .github/workflows/sync-and-enrich.yml env block)
#   If missing: npm install -g "@biomejs/biome@2.4.12"
```

### 3.2 Resume the in-flight work

```bash
# 5. If scripts/utils/schema_fixer.py still has the in-tree maxItems
#    change (inspect with `git diff scripts/utils/schema_fixer.py`),
#    skip to step 6. Otherwise re-apply it — see section 4.1 below.

# 6. Regenerate enriched JSONs with the new SchemaFixer behaviour.
python3 -m scripts.pipeline
# Takes ~13 min. Expect it to exit 0 with 521 files processed,
# 0 failures. Stats line should show max_items_added > 7000.

# 7. Verify checkov is now clean on a representative file.
checkov --config-file .checkov.yaml -f docs/specifications/api/authentication.json --framework openapi --compact 2>&1 | tail -5
# Expect "Passed checks: 5, Failed checks: 0" (was "Passed: 4, Failed: 1").

# 8. Verify biome + spectral still clean on the regenerated tree.
biome format docs/specifications/api/*.json 2>&1 | tail -3
# Expect "No fixes applied" plus 3 warnings for the oversize files.
python3 scripts/lint.py --input-dir docs/specifications/api --fail-on-error --fail-on-warning 2>&1 | tail -3
# Expect "All 39 specifications passed linting!"

# 9. Delegate commit + push + CI poll to github-ops.
#    Use the workflow-lifecycle skill; pass Issue: #137 and
#    Branch: fix/137-unblock-release-auto-merge so github-ops reuses
#    the existing issue/branch/PR rather than creating duplicates.
#    See section 3.3 below for the exact prompt shape.
```

### 3.3 github-ops prompt template for the follow-up commit

```
fix: inject default maxItems into array schemas to satisfy Checkov CKV_OPENAPI_21

Issue: #137
Branch: fix/137-unblock-release-auto-merge

Files:
- scripts/utils/schema_fixer.py (new fix_missing_max_items path + get_stats updates)
- docs/specifications/api/*.json (regenerated by the pipeline with
  `maxItems: 65535` injected on every array schema that lacked one;
  upstream-set values preserved)

Why: PR #138 landed the biome-at-source fix and BIOME_FORMAT passes on
the CI run. CHECKOV still fails CKV_OPENAPI_21 because 7,348 of 9,587
array schemas in the enriched specs do not declare maxItems. Extending
SchemaFixer to inject a generous default (65535) at generation time
satisfies Checkov without hand-editing the upstream schemas and keeps
future pipeline runs compliant. Locally verified: checkov passes on
representative files; biome + spectral still clean.

After PR #138 merges, perform the 6-step cleanup (see HANDOFF.md §2.6).
```

## 4. Exact Patch Content (in case the working tree was lost)

### 4.1 `scripts/utils/schema_fixer.py` diff (apply if missing)

The change is a superset of the current committed file on `main`. Key
additions:

- Class docstring updated to mention CKV_OPENAPI_21.
- Class constant `DEFAULT_ARRAY_MAX_ITEMS: ClassVar[int] = 65535`.
- `__init__` initialises `_fix_missing_max_items = True`,
  `_default_max_items = self.DEFAULT_ARRAY_MAX_ITEMS`,
  `_max_items_added = 0`.
- `_load_config` reads two new keys under `schema_fixes:` —
  `fix_missing_max_items` (bool, default `True`) and
  `default_max_items` (int, default `65535`).
- `fix_spec` resets `_max_items_added`.
- `_fix_recursive` calls a new check `_needs_max_items(obj)` and applies
  `_apply_max_items(obj)` when true, alongside the existing type-fix.
- `_needs_max_items` returns `True` when `obj.get("type") == "array"`
  and `"maxItems"` is absent and the schema is not a `$ref` /
  `allOf` / `oneOf` / `anyOf` composition.
- `_apply_max_items` returns a new dict with `"maxItems":
  self._default_max_items` merged in (non-destructive).
- `get_stats` now returns `max_items_added`, `fix_missing_max_items`,
  `default_max_items` alongside the existing fields.

Reference patch (on top of commit `27fb822`):

```python
# In class SchemaFixer, near the class docstring:
class SchemaFixer:
    """Fixes malformed schema definitions in OpenAPI specs.

    Fixes:
    - Add missing 'type' field where 'format' exists alone ...
    - Add a default 'maxItems' to every array schema that lacks one,
      so the output satisfies Checkov CKV_OPENAPI_21 ...
    """

    DEFAULT_ARRAY_MAX_ITEMS: ClassVar[int] = 65535

# __init__ defaults:
    self._fix_missing_max_items = True
    self._default_max_items = self.DEFAULT_ARRAY_MAX_ITEMS
    ...
    self._max_items_added = 0

# _load_config additions:
    self._fix_missing_max_items = schema_config.get("fix_missing_max_items", True)
    self._default_max_items = schema_config.get("default_max_items", self.DEFAULT_ARRAY_MAX_ITEMS)

# fix_spec additions:
    self._max_items_added = 0

# _fix_recursive additions (inside `if isinstance(obj, dict):` before the recurse):
    if self._fix_missing_max_items and self._needs_max_items(obj):
        obj = self._apply_max_items(obj)

# New methods:
    def _needs_max_items(self, obj: dict[str, Any]) -> bool:
        if obj.get("type") != "array":
            return False
        if "maxItems" in obj:
            return False
        return not any(key in obj for key in ("$ref", "allOf", "oneOf", "anyOf"))

    def _apply_max_items(self, obj: dict[str, Any]) -> dict[str, Any]:
        obj = {**obj, "maxItems": self._default_max_items}
        self._max_items_added += 1
        return obj

# get_stats additions:
    "max_items_added": self._max_items_added,
    "fix_missing_max_items": self._fix_missing_max_items,
    "default_max_items": self._default_max_items,
```

Unit-test the change before regenerating:

```bash
python3 -c "
from scripts.utils.schema_fixer import SchemaFixer
fx = SchemaFixer()
out = fx.fix_spec({'items': {'type': 'array', 'items': {'type': 'string'}}})
assert out['items']['maxItems'] == 65535
print('stats:', fx.get_stats())
"
```

## 5. Key Files At A Glance

| Path                                                                     | Role                                                                                                    |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `scripts/utils/json_writer.py`                                           | Biome-enforced JSON writer. The only sanctioned way to write JSON under `docs/specifications/api/**`. |
| `scripts/utils/schema_fixer.py`                                          | Will carry the `maxItems` injection (Section 4.1).                                                      |
| `scripts/pipeline.py`                                                    | `python -m scripts.pipeline` entry point for the full enrichment run.                                   |
| `scripts/hooks/pre-commit-pipeline.sh`                                   | Pre-commit hook — runs the full pipeline + spectral lint on every commit. Needs `specs/original/`.      |
| `.github/workflows/sync-and-enrich.yml`                                  | The scheduled release workflow. Env `BIOME_VERSION` now pinned; `[skip ci]` removed from release commit. |
| `.checkov.yaml`                                                          | **Managed by docs-control.** Only `CKV_GHA_7`, `CKV2_GHA_1`, and a `CKV_SECRET_4` path skip are listed. |
| `biome.json`                                                             | **Managed by docs-control.** `files.maxSize: 5242880` (5 MiB) is too tight for virtual.json / openapi.json / sites.json; biome skips them with a warning that json_writer now tolerates. |
| `.claude/governance.json`                                                | Lists every managed file — edit-blocked by `.claude/hooks/protect-managed-files.sh`.                    |
| `CONTRIBUTING.md`                                                        | Delegation rules. **All git/gh ops go through `f5xc-github-ops:github-ops`.**                          |
| `/etc/claude-code/CLAUDE.md`, `/home/vscode/.claude/CLAUDE.md`, `.claude/CLAUDE.md` | Three-layer policy. Container default + user global + repo-specific. Read on every boot.     |

## 6. Gotchas Collected This Session

1. **`[skip ci]`** is a sneaky block — it stops `pull_request` events
   from firing but not `pull_request_target`. If a required check is
   `pull_request`-only (Super-Linter is), the release PR hangs forever
   with the check in "expected" state.
2. **GitHub Actions cache** is not keyed on tool versions by default —
   a biome / checkov / spectral upgrade will not bust it. Include the
   tool version as a suffix when tool output shape matters
   (the `BIOME_VERSION` env is the template to follow).
3. **Super-Linter BIOME_FORMAT** receives each file individually; a file
   over biome's `files.maxSize` yields non-zero exit in single-file mode
   but is merely a warning in multi-file mode. `json_writer._is_maxsize_only`
   encodes this distinction. Don't "fix" it by removing the check.
4. **Managed files** (governance-enforced): editing is blocked by
   `.claude/hooks/protect-managed-files.sh`. Do not try to work around
   the hook — open a docs-control PR instead. The hook's block is
   correct and intentional.
5. **`docs/specifications/api/` is gitignored.** The release workflow
   force-adds with `git add -f`. The pre-commit hook similarly uses
   `git add --ignore-errors docs/specifications/api/*.json`. Don't be
   surprised when `git status` shows these as modified / deleted
   against an empty worktree after pipeline runs.
6. **`specs/original/` is an ephemeral download.** On every new
   container it starts missing. `scripts/download.py` re-fetches from
   `f5xc-salesdemos/api-specs` releases using `GITHUB_TOKEN`. The
   pre-commit pipeline will fail with `Input directory not found:
   specs/original` if you skip this.
7. **`.github_release`** is bumped by `scripts/download.py` every time
   it fetches a newer upstream release. On the fix-branch PR it MUST
   stay at whatever `main` has (today: `v2026.04.16-7`). The scheduled
   release workflow is the one that advances it.
8. **`ruff check` + `TCH`/`RUF`** — the repo's `pyproject.toml` has
   both enabled. Use `TYPE_CHECKING` for import-only-in-annotations
   modules (see `json_writer.py`). Avoid `×` (U+00D7) in Python
   docstrings — use plain ASCII or a noqa.
9. **`check=False` + `contextlib.suppress`** was the prior antipattern
   that let the biome gap silently rot. Never do this for an
   at-source-integrity step.

## 7. Useful Links

- Branch: <https://github.com/f5xc-salesdemos/api-specs-enriched/tree/fix/137-unblock-release-auto-merge>
- PR #138: <https://github.com/f5xc-salesdemos/api-specs-enriched/pull/138>
- Issue #137 (primary): <https://github.com/f5xc-salesdemos/api-specs-enriched/issues/137>
- Latest failing CI run: <https://github.com/f5xc-salesdemos/api-specs-enriched/actions/runs/24640402025>
- Upstream specs repo: <https://github.com/f5xc-salesdemos/api-specs>
- Docs-control (managed files source): <https://github.com/f5xc-salesdemos/docs-control>
