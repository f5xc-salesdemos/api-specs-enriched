"""Enum value discovery via invalid-value probe."""

from __future__ import annotations

import copy

from scripts.discovery.probes import FieldProbeResult, ProbeRequest, ProbeResponse
from scripts.discovery.probes.numeric import _set_nested


class EnumProbe:
    """Discovers valid enum values by sending an obviously invalid value."""

    def generate_probes(
        self,
        field_path: str,
        field_schema: dict,
        base_payload: dict,
        current_constraints: dict | None,
    ) -> list[ProbeRequest]:
        """Generate probes."""
        return [
            ProbeRequest(
                field_path=field_path,
                method="POST",
                payload=_set_nested(
                    copy.deepcopy(base_payload), field_path, "INVALID_ENUM_VALUE_XYZ"
                ),
                description=f"{field_path} = invalid enum sentinel",
            )
        ]

    def interpret_results(
        self,
        field_path: str,
        results: list[ProbeResponse],
    ) -> FieldProbeResult:
        """Interpret results."""
        discovered: dict = {}
        evidence = []
        confidence = 0.5

        for r in results:
            evidence.append(
                {"accepted": r.accepted, "error": r.error_message, "parsed": r.parsed_constraint}
            )
            if r.parsed_constraint and "enum_values" in r.parsed_constraint:
                discovered["enum_values"] = r.parsed_constraint["enum_values"]
                confidence = 0.95

        return FieldProbeResult(
            field_path=field_path,
            field_type="enum",
            probe_strategy="enum_invalid",
            expected={},
            actual=discovered,
            confidence=confidence,
            gap_type=None,
            evidence=evidence,
        )
