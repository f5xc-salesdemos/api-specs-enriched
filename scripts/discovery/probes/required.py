"""Required field detection via field-omission probes."""

from __future__ import annotations

import copy

from scripts.discovery.probes import FieldProbeResult, ProbeRequest, ProbeResponse


class RequiredFieldProbe:
    """Detects required vs optional fields by omitting each one."""

    def generate_probes(
        self,
        field_path: str,
        field_schema: dict,
        base_payload: dict,
        current_constraints: dict | None,
    ) -> list[ProbeRequest]:
        """Generate probes."""
        payload = copy.deepcopy(base_payload)
        parts = field_path.split(".")
        node = payload
        for part in parts[:-1]:
            node = node.get(part, {})
        node.pop(parts[-1], None)

        return [
            ProbeRequest(
                field_path=field_path,
                method="POST",
                payload=payload,
                description=f"omit {field_path}",
            )
        ]

    def interpret_results(
        self,
        field_path: str,
        results: list[ProbeResponse],
    ) -> FieldProbeResult:
        """Interpret results."""
        evidence = []
        is_required = None
        confidence = 0.99

        for r in results:
            evidence.append({"accepted": r.accepted, "error": r.error_message})
            is_required = not r.accepted

        return FieldProbeResult(
            field_path=field_path,
            field_type="required_check",
            probe_strategy="field_omission",
            expected={},
            actual={"required": is_required},
            confidence=confidence,
            gap_type=None,
            evidence=evidence,
        )
