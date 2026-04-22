# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Contract-diff gate: ensures enrichment only makes additive changes.

Compares an input spec (from ``specs/original``) against an enriched output spec
(from ``docs/specifications/api/``) and reports violations of the additive
allowlist defined in spec §4.3.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from deepdiff import DeepDiff

from scripts.utils.additive_allowlist import is_additive_change

if TYPE_CHECKING:
    from collections.abc import Sequence

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
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
