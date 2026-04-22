# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Tests for the structural contract-diff driver."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.contract_diff import Violation, run_contract_diff

FIXTURES = Path(__file__).parent / "fixtures" / "contract_diff"


def _load(pair: str) -> tuple[dict, dict]:
    return (
        json.loads((FIXTURES / pair / "input.json").read_text()),
        json.loads((FIXTURES / pair / "output.json").read_text()),
    )


def test_pass_additive_extension_and_description() -> None:
    i, o = _load("pass_add_ext")
    violations = run_contract_diff(i, o)
    assert violations == []


def test_fail_when_constraint_tightened() -> None:
    i, o = _load("fail_tighten")
    violations = run_contract_diff(i, o)
    assert len(violations) >= 1
    assert any("minLength" in v.pointer for v in violations)


def test_fail_when_property_removed() -> None:
    i, o = _load("fail_remove")
    violations = run_contract_diff(i, o)
    assert any("parameters" in v.pointer for v in violations)


def test_violation_structure_has_rule_category() -> None:
    i, o = _load("fail_tighten")
    violations = run_contract_diff(i, o)
    assert isinstance(violations[0], Violation)
    assert violations[0].rule_category in {"removal", "shape-change", "constraint-change", "other"}


def test_run_directory_diff_merges_fan_in_fan_out(tmp_path: Path) -> None:
    """The enrichment pipeline merges ~520 input files into ~40 output
    files grouped by category, so ``run_directory_diff`` must compare
    the aggregate contract on both sides rather than doing a 1:1 file
    match (which would flag every input filename as ``file_removed``).
    """
    from scripts.contract_diff import run_directory_diff

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    # Two upstream specs that land on the same category.
    (input_dir / "docs-cloud.0001.ai_assistant.ves-swagger.json").write_text(
        json.dumps(
            {
                "openapi": "3.0.0",
                "paths": {"/ai/assistant": {"get": {"operationId": "getAssistant"}}},
                "components": {"schemas": {"Assistant": {"type": "object"}}},
            },
        ),
    )
    (input_dir / "docs-cloud.0002.ai_services.ves-swagger.json").write_text(
        json.dumps(
            {
                "openapi": "3.0.0",
                "paths": {"/ai/inference": {"post": {"operationId": "infer"}}},
                "components": {"schemas": {"InferenceRequest": {"type": "object"}}},
            },
        ),
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    # Single merged enriched output — adds a description to getAssistant,
    # adds x-f5xc-cli-help; does NOT remove anything.
    (output_dir / "ai_services.json").write_text(
        json.dumps(
            {
                "openapi": "3.0.0",
                "paths": {
                    "/ai/assistant": {
                        "get": {
                            "operationId": "getAssistant",
                            "description": "Retrieves assistant info.",
                            "x-f5xc-cli-help": "xcsh ai assistant get",
                        },
                    },
                    "/ai/inference": {"post": {"operationId": "infer"}},
                },
                "components": {
                    "schemas": {
                        "Assistant": {"type": "object"},
                        "InferenceRequest": {"type": "object"},
                    },
                },
            },
        ),
    )
    violations = run_directory_diff(input_dir, output_dir)
    assert violations == []


def test_run_directory_diff_flags_merged_removal(tmp_path: Path) -> None:
    """If the merged output drops a path that exists in any input, flag it."""
    from scripts.contract_diff import run_directory_diff

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "a.ves-swagger.json").write_text(
        json.dumps(
            {
                "paths": {"/a": {"get": {"operationId": "a"}}},
                "components": {"schemas": {}},
            },
        ),
    )
    (input_dir / "b.ves-swagger.json").write_text(
        json.dumps(
            {
                "paths": {"/b": {"get": {"operationId": "b"}}},
                "components": {"schemas": {}},
            },
        ),
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    # Enriched output only keeps /a — /b is dropped.
    (output_dir / "all.json").write_text(
        json.dumps(
            {"paths": {"/a": {"get": {"operationId": "a"}}}, "components": {"schemas": {}}},
        ),
    )
    violations = run_directory_diff(input_dir, output_dir)
    assert any("/b" in v.pointer for v in violations)
    assert all(v.rule_category == "removal" for v in violations)


def test_run_directory_diff_skips_manifest_and_index(tmp_path: Path) -> None:
    """manifest.json (input) and index.json (output) are pipeline metadata,
    not OpenAPI specs; they must not participate in the diff."""
    from scripts.contract_diff import run_directory_diff

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "manifest.json").write_text(json.dumps({"files": ["a.json"]}))
    (input_dir / "a.json").write_text(json.dumps({"paths": {}, "components": {"schemas": {}}}))
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "index.json").write_text(json.dumps({"domains": []}))
    (output_dir / "a.json").write_text(json.dumps({"paths": {}, "components": {"schemas": {}}}))
    violations = run_directory_diff(input_dir, output_dir)
    assert violations == []
