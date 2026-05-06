"""Probe strategies for constraint boundary testing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class ProbeRequest:
    """A single API probe to execute."""

    field_path: str
    method: str
    payload: dict
    description: str


@dataclass
class ProbeResponse:
    """Result of executing a single probe."""

    field_path: str
    status_code: int
    accepted: bool
    error_message: str | None
    parsed_constraint: dict | None
    response_body: dict | None


@dataclass
class FieldProbeResult:
    """Aggregated result for a single field after all probes run."""

    field_path: str
    field_type: str
    probe_strategy: str
    expected: dict
    actual: dict
    confidence: float
    gap_type: str | None
    evidence: list[dict] = field(default_factory=list)


@dataclass
class ResourceAuditResult:
    """Full audit result for a single resource type."""

    resource_type: str
    timestamp: str
    namespace: str
    fields: list[FieldProbeResult] = field(default_factory=list)
    server_default_fields: dict[str, Any] = field(default_factory=dict)
    response_only_fields: list[str] = field(default_factory=list)
    cleanup_status: str = "unknown"
    probes_executed: int = 0
    probes_accepted: int = 0
    probes_rejected: int = 0
    errors_unparseable: int = 0


@runtime_checkable
class ProbeStrategy(Protocol):
    """Interface all probe strategy modules implement."""

    def generate_probes(
        self,
        field_path: str,
        field_schema: dict,
        base_payload: dict,
        current_constraints: dict | None,
    ) -> list[ProbeRequest]:
        """Generate probe requests for a field."""
        ...

    def interpret_results(
        self,
        field_path: str,
        results: list[ProbeResponse],
    ) -> FieldProbeResult:
        """Interpret probe responses into a field result."""
        ...
