"""String length and pattern probe strategy."""

from __future__ import annotations

import copy

from scripts.discovery.probes import FieldProbeResult, ProbeRequest, ProbeResponse
from scripts.discovery.probes.numeric import _set_nested


class StringProbe:
    """Discovers minLength, maxLength, and pattern constraints."""

    def generate_probes(
        self,
        field_path: str,
        field_schema: dict,
        base_payload: dict,
        current_constraints: dict | None,
    ) -> list[ProbeRequest]:
        """Generate probes."""
        probes = []
        probes.append(
            ProbeRequest(
                field_path=field_path,
                method="POST",
                payload=_set_nested(copy.deepcopy(base_payload), field_path, ""),
                description=f"{field_path} = empty string",
            )
        )
        probes.append(
            ProbeRequest(
                field_path=field_path,
                method="POST",
                payload=_set_nested(copy.deepcopy(base_payload), field_path, "a" * 10_000),
                description=f"{field_path} = 10000-char string",
            )
        )
        final_segment = field_path.rsplit(".", maxsplit=1)[-1]
        if final_segment in ("name", "namespace"):
            probes.append(
                ProbeRequest(
                    field_path=field_path,
                    method="POST",
                    payload=_set_nested(copy.deepcopy(base_payload), field_path, "1-invalid-name"),
                    description=f"{field_path} = digit-first (DNS-1035 test)",
                )
            )
        return probes

    def interpret_results(
        self,
        field_path: str,
        results: list[ProbeResponse],
    ) -> FieldProbeResult:
        """Interpret results."""
        discovered: dict = {}
        evidence = []
        confidence = 0.7

        for r in results:
            evidence.append(
                {"accepted": r.accepted, "error": r.error_message, "parsed": r.parsed_constraint}
            )
            if r.parsed_constraint:
                discovered.update(r.parsed_constraint)
                confidence = 0.95

        return FieldProbeResult(
            field_path=field_path,
            field_type="string",
            probe_strategy="string_length",
            expected={},
            actual=discovered,
            confidence=confidence,
            gap_type=None,
            evidence=evidence,
        )
