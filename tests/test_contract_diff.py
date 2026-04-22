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
