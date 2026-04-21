# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Tests for scripts/verify_governance.py.

The verifier blocks PRs that touch files owned by docs-control's
governance template. Unit tests drive a throwaway git repo so the
assertion covers the full `git diff --name-only` path without needing
a network-dependent setup.
"""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

import pytest

from scripts.verify_governance import (
    GovernanceViolationError,
    main,
    verify,
)

if TYPE_CHECKING:
    from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A minimal git repo with one commit on main and a branch with two changes.

    Also writes a governance.json stub so tests can point --governance-json at it.
    """
    _run(["git", "init", "-q", "-b", "main"], tmp_path)
    _run(["git", "config", "user.email", "t@t.t"], tmp_path)
    _run(["git", "config", "user.name", "t"], tmp_path)
    (tmp_path / "README.md").write_text("root\n")
    (tmp_path / "biome.json").write_text("{}\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "build.py").write_text("print('hi')\n")
    _run(["git", "add", "."], tmp_path)
    _run(["git", "commit", "-q", "-m", "init"], tmp_path)
    _run(["git", "checkout", "-q", "-b", "feature"], tmp_path)

    governance = tmp_path / "governance.json"
    governance.write_text(
        json.dumps({"protected_files": ["biome.json", "README.md"]}) + "\n",
    )
    return tmp_path


class TestVerify:
    """Direct calls to verify(); no argparse layer."""

    def test_clean_diff_returns_empty(self, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (repo / "scripts" / "build.py").write_text("print('ok')\n")
        _run(["git", "add", "."], repo)
        _run(["git", "commit", "-q", "-m", "touch untracked area"], repo)

        monkeypatch.chdir(repo)
        violations = verify("main", "feature", governance_path=repo / "governance.json")
        assert violations == []

    def test_touching_protected_is_flagged(
        self,
        repo: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (repo / "biome.json").write_text('{"formatter": false}\n')
        _run(["git", "add", "."], repo)
        _run(["git", "commit", "-q", "-m", "edit biome"], repo)

        monkeypatch.chdir(repo)
        violations = verify("main", "feature", governance_path=repo / "governance.json")
        assert violations == ["biome.json"]

    def test_multiple_violations_are_sorted(
        self,
        repo: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        (repo / "biome.json").write_text('{"new": true}\n')
        (repo / "README.md").write_text("changed\n")
        _run(["git", "add", "."], repo)
        _run(["git", "commit", "-q", "-m", "edit two protected files"], repo)

        monkeypatch.chdir(repo)
        violations = verify("main", "feature", governance_path=repo / "governance.json")
        assert violations == ["README.md", "biome.json"]

    def test_missing_governance_raises(self, repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(repo)
        with pytest.raises(GovernanceViolationError, match="not found"):
            verify("main", "feature", governance_path=repo / "does-not-exist.json")

    def test_malformed_governance_raises(
        self,
        repo: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        bad = repo / "bad.json"
        bad.write_text('{"protected_files": "not-a-list"}\n')
        monkeypatch.chdir(repo)
        with pytest.raises(GovernanceViolationError, match="must be a list"):
            verify("main", "feature", governance_path=bad)


class TestMain:
    """CLI entrypoint — exit-code contract."""

    def test_exit_zero_when_clean(
        self,
        repo: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        (repo / "scripts" / "build.py").write_text("print('v2')\n")
        _run(["git", "add", "."], repo)
        _run(["git", "commit", "-q", "-m", "non-governed change"], repo)

        monkeypatch.chdir(repo)
        rc = main(
            [
                "--base",
                "main",
                "--head",
                "feature",
                "--governance-json",
                str(repo / "governance.json"),
            ],
        )
        assert rc == 0
        captured = capsys.readouterr()
        assert "ok:" in captured.out

    def test_exit_one_when_violation(
        self,
        repo: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        (repo / "biome.json").write_text('{"x": 1}\n')
        _run(["git", "add", "."], repo)
        _run(["git", "commit", "-q", "-m", "edit"], repo)

        monkeypatch.chdir(repo)
        rc = main(
            [
                "--base",
                "main",
                "--head",
                "feature",
                "--governance-json",
                str(repo / "governance.json"),
            ],
        )
        assert rc == 1
        captured = capsys.readouterr()
        assert "biome.json" in captured.err
        assert "docs-control" in captured.err

    def test_exit_two_on_missing_manifest(
        self,
        repo: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.chdir(repo)
        rc = main(
            [
                "--base",
                "main",
                "--head",
                "feature",
                "--governance-json",
                str(repo / "absent.json"),
            ],
        )
        assert rc == 2
        captured = capsys.readouterr()
        assert "error:" in captured.err
