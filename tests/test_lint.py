# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Tests for scripts/lint.py and Spectral runner adapter."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from scripts import lint
from scripts.utils.lint_reporter import LintIssue, LintResult, LintStats


class TestCheckSpectralInstalled:
    """Tests for environment and dependency verification."""

    def test_installed_when_node_and_runner_present(self) -> None:
        with patch("shutil.which", return_value="/usr/bin/node"), patch.object(
            Path, "exists", return_value=True
        ):
            assert lint.check_spectral_installed() is True

    def test_not_installed_when_node_missing(self) -> None:
        with patch("shutil.which", return_value=None):
            assert lint.check_spectral_installed() is False

    def test_not_installed_when_runner_missing(self) -> None:
        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "scripts.lint.get_runner_path", return_value=Path("/nonexistent/runner.mjs")
        ):
            assert lint.check_spectral_installed() is False


class TestRunSpectral:
    """Tests for run_spectral function."""

    def test_missing_node_returns_error(self, tmp_path: Path) -> None:
        spec = tmp_path / "spec.json"
        spec.write_text("{}")
        with patch("shutil.which", return_value=None):
            success, issues, err = lint.run_spectral(spec)
            assert success is False
            assert issues == []
            assert err is not None
            assert "Node.js not found" in err

    def test_missing_runner_returns_error(self, tmp_path: Path) -> None:
        spec = tmp_path / "spec.json"
        spec.write_text("{}")
        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "scripts.lint.get_runner_path", return_value=tmp_path / "nonexistent.mjs"
        ):
            success, issues, err = lint.run_spectral(spec)
            assert success is False
            assert "Spectral runner not found" in str(err)

    def test_missing_ruleset_returns_error(self, tmp_path: Path) -> None:
        spec = tmp_path / "spec.json"
        spec.write_text("{}")
        runner = tmp_path / "runner.mjs"
        runner.write_text("// runner")
        ruleset = tmp_path / "nonexistent_ruleset.mjs"
        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "scripts.lint.get_runner_path", return_value=runner
        ):
            success, issues, err = lint.run_spectral(spec, ruleset_path=ruleset)
            assert success is False
            assert "Spectral ruleset not found" in str(err)

    def test_valid_json_output_parsed(self, tmp_path: Path) -> None:
        spec = tmp_path / "spec.json"
        spec.write_text("{}")
        runner = tmp_path / "runner.mjs"
        runner.write_text("// runner")
        ruleset = tmp_path / "ruleset.mjs"
        ruleset.write_text("export default {}")

        mock_findings = [
            {
                "code": "oas3-api-servers",
                "message": "OpenAPI `servers` must be present",
                "path": [],
                "severity": 1,
                "range": {"start": {"line": 1, "character": 0}, "end": {"line": 1, "character": 1}},
            }
        ]
        mock_proc = MagicMock(returncode=0, stdout=json.dumps(mock_findings), stderr="")

        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "scripts.lint.get_runner_path", return_value=runner
        ), patch("subprocess.run", return_value=mock_proc):
            success, issues, err = lint.run_spectral(spec, ruleset_path=ruleset)
            assert success is True
            assert len(issues) == 1
            assert issues[0]["code"] == "oas3-api-servers"
            assert err is None

    def test_malformed_json_returns_error(self, tmp_path: Path) -> None:
        spec = tmp_path / "spec.json"
        spec.write_text("{}")
        runner = tmp_path / "runner.mjs"
        runner.write_text("// runner")
        ruleset = tmp_path / "ruleset.mjs"
        ruleset.write_text("export default {}")

        mock_proc = MagicMock(returncode=0, stdout="not valid json", stderr="")

        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "scripts.lint.get_runner_path", return_value=runner
        ), patch("subprocess.run", return_value=mock_proc):
            success, issues, err = lint.run_spectral(spec, ruleset_path=ruleset)
            assert success is False
            assert issues == []
            assert "Failed to parse Spectral JSON" in str(err)

    def test_non_list_json_returns_error(self, tmp_path: Path) -> None:
        spec = tmp_path / "spec.json"
        spec.write_text("{}")
        runner = tmp_path / "runner.mjs"
        runner.write_text("// runner")
        ruleset = tmp_path / "ruleset.mjs"
        ruleset.write_text("export default {}")

        mock_proc = MagicMock(returncode=0, stdout=json.dumps({"error": "something"}), stderr="")

        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "scripts.lint.get_runner_path", return_value=runner
        ), patch("subprocess.run", return_value=mock_proc):
            success, issues, err = lint.run_spectral(spec, ruleset_path=ruleset)
            assert success is False
            assert "non-list JSON" in str(err)

    def test_nonzero_exit_code_returns_error(self, tmp_path: Path) -> None:
        spec = tmp_path / "spec.json"
        spec.write_text("{}")
        runner = tmp_path / "runner.mjs"
        runner.write_text("// runner")
        ruleset = tmp_path / "ruleset.mjs"
        ruleset.write_text("export default {}")

        mock_proc = MagicMock(returncode=2, stdout="", stderr="Fatal JS error occurred")

        with patch("shutil.which", return_value="/usr/bin/node"), patch(
            "scripts.lint.get_runner_path", return_value=runner
        ), patch("subprocess.run", return_value=mock_proc):
            success, issues, err = lint.run_spectral(spec, ruleset_path=ruleset)
            assert success is False
            assert "Fatal JS error occurred" in str(err)


class TestParseSpectralIssues:
    """Tests for parse_spectral_issues."""

    def test_parses_fields_correctly(self) -> None:
        raw = [
            {
                "code": "operation-operationId-unique",
                "message": "Duplicate operationId",
                "path": ["paths", "/test", "get"],
                "severity": 0,
                "range": {"start": {"line": 10, "character": 4}, "end": {"line": 10, "character": 20}},
            }
        ]
        parsed = lint.parse_spectral_issues(raw)
        assert len(parsed) == 1
        issue = parsed[0]
        assert isinstance(issue, LintIssue)
        assert issue.code == "operation-operationId-unique"
        assert issue.severity == 0
        assert issue.severity_name == "error"
        assert issue.range_start == {"line": 10, "character": 4}


class TestLintSpecFile:
    """Tests for lint_spec_file."""

    def test_clean_file_passes(self, tmp_path: Path) -> None:
        spec = tmp_path / "clean.json"
        spec.write_text("{}")
        config = {"linting": {"fail_on_error": True, "fail_on_warning": True}}

        with patch("scripts.lint.run_spectral", return_value=(True, [], None)):
            result = lint.lint_spec_file(spec, None, config)
            assert result.success is True
            assert result.errors == 0
            assert result.warnings == 0

    def test_error_fails_when_fail_on_error(self, tmp_path: Path) -> None:
        spec = tmp_path / "bad.json"
        spec.write_text("{}")
        config = {"linting": {"fail_on_error": True, "fail_on_warning": False}}
        mock_issue = [{"code": "err", "message": "msg", "path": [], "severity": 0}]

        with patch("scripts.lint.run_spectral", return_value=(True, mock_issue, None)):
            result = lint.lint_spec_file(spec, None, config)
            assert result.success is False
            assert result.errors == 1

    def test_warning_fails_when_fail_on_warning(self, tmp_path: Path) -> None:
        spec = tmp_path / "warn.json"
        spec.write_text("{}")
        config = {"linting": {"fail_on_error": False, "fail_on_warning": True}}
        mock_issue = [{"code": "warn", "message": "msg", "path": [], "severity": 1}]

        with patch("scripts.lint.run_spectral", return_value=(True, mock_issue, None)):
            result = lint.lint_spec_file(spec, None, config)
            assert result.success is False
            assert result.warnings == 1


class TestMainBehavior:
    """Tests for main() exit codes and fail-closed operational errors."""

    def test_exit_code_2_on_missing_node(self) -> None:
        with patch("scripts.lint.check_spectral_installed", return_value=False), patch(
            "sys.argv", ["lint.py"]
        ):
            assert lint.main() == 2

    def test_exit_code_2_on_missing_input_dir(self, tmp_path: Path) -> None:
        nonexistent = tmp_path / "missing_dir"
        with patch("scripts.lint.check_spectral_installed", return_value=True), patch(
            "sys.argv", ["lint.py", "--input-dir", str(nonexistent)]
        ):
            assert lint.main() == 2

    def test_exit_code_2_on_missing_ruleset(self, tmp_path: Path) -> None:
        input_dir = tmp_path / "specs"
        input_dir.mkdir()
        missing_ruleset = tmp_path / "missing_ruleset.mjs"
        with patch("scripts.lint.check_spectral_installed", return_value=True), patch(
            "sys.argv",
            ["lint.py", "--input-dir", str(input_dir), "--ruleset", str(missing_ruleset)],
        ):
            assert lint.main() == 2

    def test_exit_code_1_on_lint_errors(self, tmp_path: Path) -> None:
        input_dir = tmp_path / "specs"
        input_dir.mkdir()
        ruleset = tmp_path / "ruleset.mjs"
        ruleset.write_text("export default {}")

        mock_stats = LintStats(
            files_processed=1,
            files_passed=0,
            files_failed=1,
            total_errors=1,
            total_warnings=0,
            results=[
                LintResult(
                    filename="bad.json",
                    success=False,
                    errors=1,
                    issues=[LintIssue(code="err", message="msg", path=[], severity=0)],
                )
            ],
        )

        with patch("scripts.lint.check_spectral_installed", return_value=True), patch(
            "scripts.lint.lint_all_specs", return_value=mock_stats
        ), patch("scripts.lint.LintReporter.generate_all"), patch(
            "sys.argv",
            [
                "lint.py",
                "--input-dir",
                str(input_dir),
                "--ruleset",
                str(ruleset),
                "--fail-on-error",
            ],
        ):
            assert lint.main() == 1

    def test_exit_code_0_on_success(self, tmp_path: Path) -> None:
        input_dir = tmp_path / "specs"
        input_dir.mkdir()
        ruleset = tmp_path / "ruleset.mjs"
        ruleset.write_text("export default {}")

        mock_stats = LintStats(
            files_processed=1,
            files_passed=1,
            files_failed=0,
            total_errors=0,
            total_warnings=0,
            results=[LintResult(filename="good.json", success=True)],
        )

        with patch("scripts.lint.check_spectral_installed", return_value=True), patch(
            "scripts.lint.lint_all_specs", return_value=mock_stats
        ), patch("scripts.lint.LintReporter.generate_all"), patch(
            "sys.argv",
            ["lint.py", "--input-dir", str(input_dir), "--ruleset", str(ruleset)],
        ):
            assert lint.main() == 0
