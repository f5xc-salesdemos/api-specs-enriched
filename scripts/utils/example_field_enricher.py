# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Per-field example enricher for OpenAPI specifications.

Derives deterministic per-field create values from the single source of truth —
``x-f5xc-minimum-configuration.example_yaml`` (present for 331/333 CreateSpecType
schemas) — and stamps them as ``x-f5xc-field-examples`` (a flat field_path → value
map) on each CreateSpecType. Downstream consumers (console_field_metadata
generation, the workflow generator, the sweep) read create values from this one
place instead of hand-coding them in a downstream tool.

This closes the determinism loop: the spec is the single source; when testing
(CDP error triage) reveals a field the example_yaml does not cover, that gap is
fixed in the spec and republished — every downstream project benefits at once.

Issue: bake create-value determinism into the spec (DRY single source).
"""

import logging
from dataclasses import dataclass
from typing import Any

import yaml

logger = logging.getLogger(__name__)

X_F5XC_FIELD_EXAMPLES = "x-f5xc-field-examples"


def flatten_example(obj: Any, prefix: str = "spec") -> dict[str, Any]:
    """Flatten a parsed example ``spec`` object to leaf field_path → value.

    Lists collapse to their first element with a ``[]`` segment, so
    ``origin_servers: [{public_name: {dns_name: x}}]`` →
    ``spec.origin_servers[].public_name.dns_name: x``.
    """
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten_example(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        if obj:
            out.update(flatten_example(obj[0], f"{prefix}[]"))
    else:
        out[prefix] = obj
    return out


@dataclass
class ExampleFieldEnrichmentStats:
    """Statistics for example-field enrichment."""

    schemas_processed: int = 0
    schemas_stamped: int = 0
    fields_stamped: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to a serializable dictionary."""
        return {
            "schemas_processed": self.schemas_processed,
            "schemas_stamped": self.schemas_stamped,
            "fields_stamped": self.fields_stamped,
        }


class ExampleFieldEnricher:
    """Stamp ``x-f5xc-field-examples`` on CreateSpecType schemas from example_yaml."""

    def __init__(self) -> None:
        """Create the enricher with zeroed stats."""
        self.stats = ExampleFieldEnrichmentStats()

    def get_stats(self) -> dict[str, Any]:
        """Return enrichment stats."""
        return self.stats.to_dict()

    def reset_stats(self) -> None:
        """Reset stats (called per domain to avoid cross-domain accumulation)."""
        self.stats = ExampleFieldEnrichmentStats()

    def enrich_spec(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Stamp x-f5xc-field-examples on every CreateSpecType with an example_yaml."""
        for name, schema in spec.get("components", {}).get("schemas", {}).items():
            if "CreateSpecType" not in name or not isinstance(schema, dict):
                continue
            self.stats.schemas_processed += 1
            self._enrich_schema(schema)
        return spec

    def _enrich_schema(self, schema: dict[str, Any]) -> None:
        mc = schema.get("x-f5xc-minimum-configuration")
        if not isinstance(mc, dict):
            return
        example_yaml = mc.get("example_yaml")
        if not example_yaml:
            return
        try:
            parsed = yaml.safe_load(example_yaml)
        except yaml.YAMLError:
            return
        if not isinstance(parsed, dict):
            return
        spec_obj = parsed.get("spec")
        if not isinstance(spec_obj, dict):
            return
        examples = flatten_example(spec_obj)
        if not examples:
            return
        schema[X_F5XC_FIELD_EXAMPLES] = examples
        self.stats.schemas_stamped += 1
        self.stats.fields_stamped += len(examples)
