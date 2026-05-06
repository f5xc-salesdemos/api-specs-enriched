"""OneOf variant discovery via conflict probes."""

from __future__ import annotations

import copy
import json

from scripts.discovery.probes import FieldProbeResult, ProbeRequest, ProbeResponse


class OneOfProbe:
    """Discovers complete variant list by sending two conflicting variants."""

    def generate_probes(
        self,
        field_path: str,
        field_schema: dict,
        base_payload: dict,
        current_constraints: dict | None,
    ) -> list[ProbeRequest]:
        """Generate probes."""
        group_name = field_path.rsplit(".", maxsplit=1)[-1]
        ext_key = f"x-ves-oneof-field-{group_name}"
        raw = field_schema.get(ext_key, [])
        existing_variants = json.loads(raw) if isinstance(raw, str) else raw

        if len(existing_variants) < 2:
            return []

        payload = copy.deepcopy(base_payload)
        payload.setdefault("spec", {})[existing_variants[0]] = {}
        payload["spec"][existing_variants[1]] = {}

        return [
            ProbeRequest(
                field_path=field_path,
                method="POST",
                payload=payload,
                description=f"conflict: {existing_variants[0]} + {existing_variants[1]}",
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
            if r.parsed_constraint and "variants" in r.parsed_constraint:
                discovered["variants"] = r.parsed_constraint["variants"]
                confidence = 0.95

        return FieldProbeResult(
            field_path=field_path,
            field_type="oneof",
            probe_strategy="oneof_conflict",
            expected={},
            actual=discovered,
            confidence=confidence,
            gap_type=None,
            evidence=evidence,
        )
