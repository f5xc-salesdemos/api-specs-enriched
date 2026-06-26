#!/usr/bin/env python3
# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Verify a PR does not modify files governed by docs-control.

`.claude/governance.json`'s ``protected_files`` list holds ~40 config
and workflow paths that the docs-control governance template owns.
A Claude Code session is blocked from editing them by the
`protect-managed-files.sh` PreToolUse hook, but that hook only fires
inside Claude Code — a developer editing the same file in any other
editor (or amending a commit on the CLI) bypasses it silently. The
next upstream governance-sync PR would then either clobber their
work or land a drift that nobody notices until the next release run
fails some obscure sub-linter.

This script closes the gap on the CI side:

    python3 -m scripts.verify_governance [--base REF] [--head REF]

Resolves changed paths against the range ``REF_BASE..REF_HEAD`` (default
``origin/main..HEAD``) and exits non-zero if any of them appears in
``.claude/governance.json``'s ``protected_files`` set.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_GOVERNANCE_JSON = Path(".claude/governance.json")

# Branches created by the docs-control sync-managed-files workflow carry
# the very files this check would otherwise reject. Exempt them by prefix;
# the sync is the authorized upstream channel, so blocking it would self-
# block every consumer every time docs-control updates a managed file.
SYNC_BRANCH_PREFIXES = ("governance/sync-managed-files",)


def _is_governance_sync_branch() -> bool:
    """Return True when running on a PR from the managed-files sync bot."""
    head_ref = os.environ.get("GITHUB_HEAD_REF", "")
    return any(head_ref.startswith(prefix) for prefix in SYNC_BRANCH_PREFIXES)


class GovernanceViolationError(RuntimeError):
    """Raised when a diff touches a governed file."""


def _load_protected(governance_path: Path) -> set[str]:
    with governance_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    protected = data.get("protected_files", [])
    if not isinstance(protected, list):
        msg = f"{governance_path}: 'protected_files' must be a list, got {type(protected).__name__}"
        raise GovernanceViolationError(msg)
    return {str(entry) for entry in protected}


def _changed_paths(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..{head}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def verify(
    base: str,
    head: str,
    governance_path: Path = DEFAULT_GOVERNANCE_JSON,
) -> list[str]:
    """Return the list of violating paths (empty if clean).

    Raises:
        GovernanceViolationError: governance.json is missing or malformed.
        subprocess.CalledProcessError: `git diff` failed (bad ref, etc.).
    """
    if not governance_path.exists():
        msg = f"Governance manifest not found: {governance_path}"
        raise GovernanceViolationError(msg)

    protected = _load_protected(governance_path)
    changed = _changed_paths(base, head)
    return sorted(path for path in changed if path in protected)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(
        description="Fail if a diff touches files governed by docs-control.",
    )
    parser.add_argument(
        "--base",
        default="origin/main",
        help="Base ref for the diff (default: origin/main)",
    )
    parser.add_argument(
        "--head",
        default="HEAD",
        help="Head ref for the diff (default: HEAD)",
    )
    parser.add_argument(
        "--governance-json",
        type=Path,
        default=DEFAULT_GOVERNANCE_JSON,
        help="Path to governance.json (default: .claude/governance.json)",
    )
    args = parser.parse_args(argv)

    if _is_governance_sync_branch():
        head_ref = os.environ.get("GITHUB_HEAD_REF", "")
        print(f"ok: skipping governance check on sync branch {head_ref}")
        return 0

    try:
        violations = verify(args.base, args.head, args.governance_json)
    except GovernanceViolationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not violations:
        print(f"ok: no governed files modified between {args.base} and {args.head}")
        return 0

    print(
        f"error: {len(violations)} governed file(s) modified between {args.base} and {args.head}:",
        file=sys.stderr,
    )
    for path in violations:
        print(f"  - {path}", file=sys.stderr)
    print(
        "These files are owned by f5-sales-demo/docs-control. "
        "Open an upstream issue/PR there instead of editing locally.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
