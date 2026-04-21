# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Tests for scripts/release/wait-for-merge.sh.

Covers the exponential-backoff merge-poll helper that replaces the prior
hardcoded 30x10s inline loop in `.github/workflows/sync-and-enrich.yml`.
The old loop timed out whenever Super-Linter on the release PR took longer
than 5 min, leaving the release orphaned. Verifying via a pytest/subprocess
harness keeps the contract testable without shipping a new lint toolchain.

The fake `gh` binary used here is a tiny shell script that reads a state
file (or a sequence file that flips after N calls) and echoes the payload
the real `gh pr view --json state --jq '.state'` would return.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "release" / "wait-for-merge.sh"


def _write_fake_gh(tmp_path: Path, states: list[str]) -> Path:
    """Create a fake `gh` binary that returns each state in sequence.

    After the last state is emitted, the fake repeats the last value
    forever — matches reality (a PR stays in its final state).
    """
    counter = tmp_path / "fake_gh_counter"
    counter.write_text("0")

    states_file = tmp_path / "fake_gh_states"
    states_file.write_text("\n".join(states) + "\n")

    fake_gh = tmp_path / "fake_gh.sh"
    fake_gh.write_text(
        f"""#!/usr/bin/env bash
# Tiny fake gh — only implements `gh pr view ... --json state --jq '.state'`
# and `gh pr view ... --json state,mergeStateStatus,...` diagnostic form.
set -e

COUNTER_FILE={counter.as_posix()!r}
STATES_FILE={states_file.as_posix()!r}

# Diagnostic form used by fail_with_diagnostics — return a tiny JSON blob
# so stderr capture is deterministic.
if printf '%s\\n' "$@" | grep -q mergeStateStatus; then
  echo '{{"state":"UNKNOWN","mergeStateStatus":"UNKNOWN"}}'
  exit 0
fi

i=$(cat "$COUNTER_FILE")
total=$(wc -l <"$STATES_FILE" | tr -d ' ')
if [ "$i" -ge "$total" ]; then
  i=$((total - 1))
fi
sed -n "$((i + 1))p" "$STATES_FILE"
echo $((i + 1)) >"$COUNTER_FILE"
"""
    )
    fake_gh.chmod(fake_gh.stat().st_mode | stat.S_IEXEC)
    return fake_gh


def _run(
    fake_gh: Path,
    *,
    branch: str = "release/v0.0.1",
    warmup: int = 0,
    base: int = 0,
    cap: int = 0,
    max_total: int = 2,
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "WAIT_FOR_MERGE_GH": str(fake_gh),
        "WAIT_FOR_MERGE_WARMUP": str(warmup),
        "WAIT_FOR_MERGE_BASE": str(base),
        "WAIT_FOR_MERGE_CAP": str(cap),
        "WAIT_FOR_MERGE_MAX_TOTAL": str(max_total),
    }
    return subprocess.run(
        ["bash", str(_SCRIPT), branch],
        capture_output=True,
        text=True,
        env=env,
        check=False,
        timeout=30,
    )


class TestHappyPath:
    """PR reaches MERGED — exit 0, logs state."""

    def test_merged_on_first_poll(self, tmp_path: Path) -> None:
        fake = _write_fake_gh(tmp_path, ["MERGED"])
        result = _run(fake, max_total=5)
        assert result.returncode == 0, result.stderr
        assert "PR merged successfully" in result.stdout

    def test_merged_after_backoff(self, tmp_path: Path) -> None:
        fake = _write_fake_gh(tmp_path, ["OPEN", "OPEN", "OPEN", "MERGED"])
        result = _run(fake, max_total=10)
        assert result.returncode == 0, result.stderr
        assert "PR merged successfully" in result.stdout
        # At least 3 "Attempt N:" log lines (the OPEN poll attempts).
        assert result.stdout.count("Attempt ") >= 3

    def test_unknown_state_is_non_terminal(self, tmp_path: Path) -> None:
        fake = _write_fake_gh(tmp_path, ["WEIRD", "WEIRD", "MERGED"])
        result = _run(fake, max_total=10)
        assert result.returncode == 0, result.stderr
        assert "unexpected state 'WEIRD'" in result.stdout


class TestFailurePath:
    """CLOSED and timeout both exit 1 with diagnostics on stderr."""

    def test_closed_exits_nonzero(self, tmp_path: Path) -> None:
        fake = _write_fake_gh(tmp_path, ["CLOSED"])
        result = _run(fake, max_total=5)
        assert result.returncode == 1
        assert "PR was closed without merging" in result.stderr

    def test_timeout_exits_nonzero(self, tmp_path: Path) -> None:
        # Never-flipping OPEN state + base=1 + max_total=2 → ~2s wall clock
        # before the loop gives up. Diagnostic fail message on stderr.
        fake = _write_fake_gh(tmp_path, ["OPEN"])
        result = _run(fake, base=1, cap=1, max_total=2)
        assert result.returncode == 1
        assert "did not merge within" in result.stderr


class TestContract:
    """Guards on the CLI contract."""

    def test_requires_branch_argument(self, tmp_path: Path) -> None:
        fake = _write_fake_gh(tmp_path, ["MERGED"])
        result = subprocess.run(
            ["bash", str(_SCRIPT)],
            capture_output=True,
            text=True,
            env={**os.environ, "WAIT_FOR_MERGE_GH": str(fake)},
            check=False,
            timeout=5,
        )
        assert result.returncode != 0
        assert "usage" in result.stderr.lower() or "BRANCH" in result.stderr
