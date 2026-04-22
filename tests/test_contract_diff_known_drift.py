"""Schema + parity tests for the known_drift fixture file.

The drift file lets the contract-diff gate tolerate residual real
violations pending per-case triage (design spec 2026-04-22 §5).
"""

from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

import pytest

DRIFT = Path(__file__).parent / "fixtures" / "contract_diff_known_drift.json.gz"


@pytest.fixture(scope="module")
def drift_data():
    if not DRIFT.exists():
        pytest.skip(f"{DRIFT} not present yet — seeded in Task 8.")
    with gzip.open(DRIFT, "rt", encoding="utf-8") as f:
        return json.load(f)


def test_known_drift_file_is_valid_json(drift_data):
    assert drift_data["version"] == 1
    assert isinstance(drift_data["description"], str)
    assert isinstance(drift_data["entries"], list)


_ISSUE_RE = re.compile(r"^[\w.-]+/[\w.-]+#\d+$")


def test_known_drift_entries_have_issue_links(drift_data):
    for entry in drift_data["entries"]:
        issue = entry.get("issue", "")
        assert _ISSUE_RE.match(issue), (
            f"Entry {entry.get('fingerprint', '?')!r} has issue={issue!r}, "
            f"expected format owner/repo#N"
        )


def test_known_drift_fingerprints_unique(drift_data):
    fingerprints = [e["fingerprint"] for e in drift_data["entries"]]
    assert len(fingerprints) == len(set(fingerprints)), (
        f"Duplicate fingerprints in drift file: "
        f"{[fp for fp in fingerprints if fingerprints.count(fp) > 1]}"
    )


def test_known_drift_entries_have_required_fields(drift_data):
    required = {
        "fingerprint",
        "change_type",
        "pointer_glob",
        "before",
        "after",
        "issue",
        "category",
        "added",
    }
    for entry in drift_data["entries"]:
        missing = required - entry.keys()
        assert not missing, f"Entry missing fields: {missing}"
