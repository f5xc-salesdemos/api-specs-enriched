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
    diff = DeepDiff(input_spec, output_spec, ignore_order=True, view="tree")
    violations: list[Violation] = []
    for change_type, changes in diff.items():
        for change in changes:
            pointer = change.path()
            if is_additive_change(change_type, pointer):
                continue
            violations.append(
                Violation(
                    change_type=change_type,
                    pointer=pointer,
                    before=getattr(change, "t1", None),
                    after=getattr(change, "t2", None),
                    rule_category=_categorize(change_type, pointer),
                ),
            )
    return violations


def run_directory_diff(input_dir: Path, output_dir: Path) -> list[Violation]:
    """Run contract_diff per-file across two directories."""
    violations: list[Violation] = []
    for inp in sorted(input_dir.glob("*.json")):
        out = output_dir / inp.name
        if not out.exists():
            violations.append(
                Violation(
                    change_type="file_removed",
                    pointer=inp.name,
                    before=True,
                    after=False,
                    rule_category="removal",
                ),
            )
            continue
        violations.extend(
            run_contract_diff(
                json.loads(inp.read_text()),
                json.loads(out.read_text()),
            ),
        )
    return violations


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
