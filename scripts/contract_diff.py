# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Contract-diff gate: ensures enrichment only makes additive changes.

Compares an input spec (from ``specs/original``) against an enriched output spec
(from ``docs/specifications/api/``) and reports violations of the additive
allowlist defined in spec §4.3.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx
from deepdiff import DeepDiff

from scripts.utils.additive_allowlist import is_additive_change

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_CONSTRAINT_KEYS = frozenset(
    {
        "minLength",
        "maxLength",
        "pattern",
        "minimum",
        "maximum",
        "minItems",
        "maxItems",
        "enum",
        "format",
    },
)
_SHAPE_KEYS = frozenset({"type", "$ref", "required", "operationId", "oneOf", "anyOf", "allOf"})


@dataclass
class Violation:
    """One non-additive change detected between input and output specs."""

    change_type: str
    pointer: str
    before: Any
    after: Any
    rule_category: str


def _categorize(change_type: str, pointer: str) -> str:
    """Classify a non-additive change into a rule category for reporting."""
    terminal = ""
    if "'" in pointer:
        parts = pointer.rsplit("'", 2)
        if len(parts) >= 2:
            terminal = parts[-2]
    if change_type.endswith("_removed") or change_type == "iterable_item_removed":
        return "removal"
    if terminal in _CONSTRAINT_KEYS:
        return "constraint-change"
    if terminal in _SHAPE_KEYS or change_type == "type_changes":
        return "shape-change"
    return "other"


def run_contract_diff(input_spec: dict, output_spec: dict) -> list[Violation]:
    """Compare two spec dicts and return all non-additive changes as violations."""
    diff = DeepDiff(
        input_spec,
        output_spec,
        ignore_order=True,
        view="tree",
        threshold_to_diff_deeper=0.0,
    )
    violations: list[Violation] = []
    for change_type, changes in diff.items():
        for change in changes:
            pointer = change.path()
            before = getattr(change, "t1", None)
            after = getattr(change, "t2", None)
            if is_additive_change(change_type, pointer, before, after):
                continue
            violations.append(
                Violation(
                    change_type=change_type,
                    pointer=pointer,
                    before=before,
                    after=after,
                    rule_category=_categorize(change_type, pointer),
                ),
            )
    return violations


_MERGE_KEYS: tuple[str, ...] = ("paths", "definitions")
_COMPONENT_MERGE_KEYS: tuple[str, ...] = (
    "schemas",
    "responses",
    "parameters",
    "examples",
    "requestBodies",
    "headers",
    "securitySchemes",
    "links",
    "callbacks",
)


def _merge_specs(
    specs: list[tuple[str, dict]],
) -> dict[str, Any]:
    """Union the path/definitions/components.* maps across many OpenAPI specs.

    The enrichment pipeline merges ~520 per-resource upstream specs
    into ~40 per-category enriched specs, so a 1:1 file comparison is
    not meaningful. Instead, union every spec's ``paths``,
    ``definitions``, and ``components.<bucket>`` maps into a single
    aggregate dict on each side and diff those.

    Args:
        specs: list of ``(filename, parsed_json)`` tuples.

    Returns:
        A single dict with unioned top-level maps. Later entries
        overwrite earlier ones on collision; for a contract diff we
        care about presence and shape, and same-named schemas/paths
        across inputs should have identical bodies by construction.
    """
    merged: dict[str, Any] = {}
    merged_components: dict[str, Any] = {}
    for _filename, spec in specs:
        for key in _MERGE_KEYS:
            if key in spec and isinstance(spec[key], dict):
                merged.setdefault(key, {}).update(spec[key])
        components = spec.get("components") or {}
        if isinstance(components, dict):
            for bucket in _COMPONENT_MERGE_KEYS:
                if bucket in components and isinstance(components[bucket], dict):
                    merged_components.setdefault(bucket, {}).update(components[bucket])
    if merged_components:
        merged["components"] = merged_components
    return merged


def _load_specs_from_dir(spec_dir: Path) -> list[tuple[str, dict]]:
    """Load every ``*.json`` under ``spec_dir`` except ``manifest.json``.

    ``index.json`` in the enriched output is also skipped — it is a
    pipeline-emitted catalog of domains, not an OpenAPI spec.
    """
    loaded: list[tuple[str, dict]] = []
    for path in sorted(spec_dir.glob("*.json")):
        if path.name in {"manifest.json", "index.json"}:
            continue
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(doc, dict):
            loaded.append((path.name, doc))
    return loaded


def run_directory_diff(input_dir: Path, output_dir: Path) -> list[Violation]:
    """Diff the merged contract between two directories of OpenAPI specs.

    The pipeline fans in ~520 per-resource upstream specs and fans out
    into ~40 per-category enriched specs, so a naive per-file diff
    would report every input filename as ``file_removed``. Instead we
    union every spec's paths and components on each side and compare
    the two aggregates.
    """
    input_specs = _load_specs_from_dir(input_dir)
    output_specs = _load_specs_from_dir(output_dir)
    merged_input = _merge_specs(input_specs)
    merged_output = _merge_specs(output_specs)
    return run_contract_diff(merged_input, merged_output)


def render_markdown_report(violations: list[Violation]) -> str:
    """Render a human-readable markdown table of violations grouped by category."""
    if not violations:
        return "## Contract-diff gate\n\nNo violations.\n"
    lines = ["## Contract-diff gate\n", f"**{len(violations)} violation(s).**\n"]
    by_cat: dict[str, list[Violation]] = {}
    for v in violations:
        by_cat.setdefault(v.rule_category, []).append(v)
    for cat, vs in sorted(by_cat.items()):
        lines.append(f"### {cat} ({len(vs)})")
        lines.append("")
        lines.append("| Pointer | Before | After |")
        lines.append("|---|---|---|")
        lines.extend(f"| `{v.pointer}` | `{v.before!r}` | `{v.after!r}` |" for v in vs)
        lines.append("")
    return "\n".join(lines)


def live_sample(
    spec: dict,
    *,
    n: int,
    probe: Callable[[str, str], dict],
    rng_seed: int | None = None,
) -> list[dict]:
    """Probe N random paths from the enriched spec against the live API.

    ``probe(path, method)`` MUST return a dict including at least
    ``status_code`` and ``ok``. Each returned entry includes the probed
    ``path`` and ``method`` alongside the probe result.
    """
    rng = random.Random(rng_seed)
    paths = list(spec.get("paths", {}).keys())
    rng.shuffle(paths)
    sampled = paths[: min(n, len(paths))]
    results = []
    for p in sampled:
        ops = spec["paths"][p]
        method = "GET" if "get" in ops else "OPTIONS"
        results.append({"path": p, "method": method, **probe(p, method)})
    return results


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point: diff two directories and emit JSON + Markdown reports."""
    # The additive-allowlist classifier runs an inner DeepDiff per candidate
    # dict-rewrite (Rule 3). On deeply-nested OpenAPI subtrees deepdiff's own
    # recursion can exceed the 1000-frame default; bump the limit for the CLI.
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Directory with stage-1 JSON files",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Directory with enriched JSON files",
    )
    parser.add_argument("--report", type=Path, default=Path("reports/contract_diff.json"))
    parser.add_argument("--markdown", type=Path, default=Path("reports/contract_diff.md"))
    parser.add_argument(
        "--live-sample",
        type=int,
        default=0,
        help="Probe N random paths against the live F5XC API",
    )
    parser.add_argument(
        "--live-fail-on-mismatch",
        action="store_true",
        help="Non-zero exit when any live probe fails (default: informational only)",
    )
    args = parser.parse_args(argv)

    violations = run_directory_diff(args.input, args.output)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(
            [v.__dict__ for v in violations],
            indent=2,
            default=str,
            sort_keys=True,
        ),
    )
    args.markdown.write_text(render_markdown_report(violations))
    rc = 1 if violations else 0

    if args.live_sample > 0:
        api_url = os.environ.get("F5XC_API_URL")
        api_token = os.environ.get("F5XC_API_TOKEN")
        if not api_url or not api_token:
            print(
                "live-sample requested but F5XC_API_URL/TOKEN not set; skipping",
                file=sys.stderr,
            )
        else:
            client = httpx.Client(
                base_url=api_url,
                headers={"Authorization": f"Bearer {api_token}"},
                timeout=30.0,
            )
            try:
                # Pick a representative merged spec to sample; openapi.json aggregates all paths.
                merged = args.output / "openapi.json"
                if merged.exists():
                    spec = json.loads(merged.read_text())

                    def _probe(path: str, method: str) -> dict:
                        try:
                            r = client.request(method, path)
                        except httpx.HTTPError as exc:
                            return {"status_code": 0, "ok": False, "error": str(exc)}
                        return {
                            "status_code": r.status_code,
                            "ok": 200 <= r.status_code < 300,
                        }

                    live_results = live_sample(
                        spec,
                        n=args.live_sample,
                        probe=_probe,
                        rng_seed=0,
                    )
                    (args.report.parent / "contract_diff_live.json").write_text(
                        json.dumps(live_results, indent=2),
                    )
                    if args.live_fail_on_mismatch and any(not r.get("ok") for r in live_results):
                        rc = max(1, rc)
            finally:
                client.close()

    return rc


if __name__ == "__main__":
    sys.exit(main())
