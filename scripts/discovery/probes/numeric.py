"""Numeric boundary probe strategy."""

from __future__ import annotations

import copy

from scripts.discovery.probes import FieldProbeResult, ProbeRequest, ProbeResponse


class NumericBoundaryProbe:
    """Discovers min/max constraints by sending boundary-violating values."""

    def generate_probes(
        self,
        field_path: str,
        field_schema: dict,
        base_payload: dict,
        current_constraints: dict | None,
    ) -> list[ProbeRequest]:
        """Generate probes at boundary values."""
        test_values: list[tuple[int, str]] = [
            (-1, "below zero (-1)"),
            (0, "zero (0)"),
            (999_999, "extreme high (999999)"),
        ]

        if current_constraints:
            if "minimum" in current_constraints:
                mn = current_constraints["minimum"]
                test_values.append((mn - 1, f"config min-1 ({mn - 1})"))
            if "maximum" in current_constraints:
                mx = current_constraints["maximum"]
                test_values.append((mx + 1, f"config max+1 ({mx + 1})"))

        probes: list[ProbeRequest] = []
        for value, description in test_values:
            payload = _set_nested(copy.deepcopy(base_payload), field_path, value)
            probes.append(
                ProbeRequest(
                    field_path=field_path,
                    method="POST",
                    payload=payload,
                    description=f"{field_path} = {description}",
                )
            )

        return probes

    def interpret_results(
        self,
        field_path: str,
        results: list[ProbeResponse],
    ) -> FieldProbeResult:
        """Derive actual min/max from accepted/rejected probes."""
        discovered: dict = {}
        evidence: list[dict] = []
        confidence = 0.7

        for r in results:
            evidence.append(
                {
                    "status_code": r.status_code,
                    "accepted": r.accepted,
                    "error": r.error_message,
                    "parsed": r.parsed_constraint,
                }
            )
            if r.parsed_constraint:
                discovered.update(r.parsed_constraint)
                confidence = 0.95

        return FieldProbeResult(
            field_path=field_path,
            field_type="number",
            probe_strategy="numeric_boundary",
            expected={},
            actual=discovered,
            confidence=confidence,
            gap_type=None,
            evidence=evidence,
        )


def _set_nested(payload: dict, field_path: str, value: object) -> dict:
    """Set a value at a dot-notation path within a nested dict."""
    parts = field_path.split(".")
    node = payload
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value
    return payload
