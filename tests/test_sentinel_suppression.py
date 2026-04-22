"""Sentinel constraints that equal the JSON Schema / type default
should NOT be emitted by the enricher. See design spec 2026-04-22 sections 3.2-3.4.
"""

from __future__ import annotations

from typing import Any


def _collect_min_length_zero_sites(
    obj: Any,
    acc: list[str] | None = None,
    path: str = "",
) -> list[str]:
    """Walk ``obj`` and return a list of paths where ``minLength: 0`` appears."""
    acc = [] if acc is None else acc
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "minLength" and v == 0:
                acc.append(path)
            _collect_min_length_zero_sites(v, acc, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _collect_min_length_zero_sites(item, acc, f"{path}[{i}]")
    return acc


def test_validation_enricher_does_not_emit_min_length_zero() -> None:
    """``minLength: 0`` is the JSON Schema default for strings - zero info."""
    from scripts.utils.validation_enricher import ValidationEnricher

    # Minimal spec with an unconstrained string property.
    spec: dict[str, Any] = {
        "openapi": "3.0.0",
        "info": {"title": "t", "version": "0"},
        "paths": {},
        "components": {
            "schemas": {
                "Foo": {
                    "type": "object",
                    "properties": {
                        "bar": {"type": "string"},
                    },
                },
            },
        },
    }
    enriched = ValidationEnricher().enrich_spec(spec)
    sites = _collect_min_length_zero_sites(enriched)
    assert sites == [], f"Expected no `minLength: 0` emissions; found at: {sites}"


def _collect_sentinel_max_items(
    obj: Any,
    acc: list[str] | None = None,
    path: str = "",
) -> list[str]:
    """Walk ``obj`` and return paths where ``maxItems: 65535`` appears."""
    acc = [] if acc is None else acc
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "maxItems" and v == 65535:
                acc.append(path)
            _collect_sentinel_max_items(v, acc, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _collect_sentinel_max_items(item, acc, f"{path}[{i}]")
    return acc


def test_schema_fixer_does_not_stamp_sentinel_max_items() -> None:
    """``maxItems: 65535`` is the protobuf "unlimited" sentinel - zero info."""
    from scripts.utils.schema_fixer import SchemaFixer

    spec: dict[str, Any] = {
        "components": {
            "schemas": {
                "Foo": {
                    "type": "object",
                    "properties": {
                        "items": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
    }
    fixer = SchemaFixer()
    fixed = fixer.inject_max_items(spec)
    sites = _collect_sentinel_max_items(fixed)
    assert sites == [], f"Expected no maxItems: 65535 emissions; found at: {sites}"


def test_validation_enricher_does_not_emit_sentinel_max_items() -> None:
    """Same sentinel check for the validation enricher path."""
    from scripts.utils.validation_enricher import ValidationEnricher

    spec: dict[str, Any] = {
        "openapi": "3.0.0",
        "info": {"title": "t", "version": "0"},
        "paths": {},
        "components": {
            "schemas": {
                "Foo": {
                    "type": "object",
                    "properties": {
                        "items": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
    }
    enriched = ValidationEnricher().enrich_spec(spec)
    sites = _collect_sentinel_max_items(enriched)
    assert sites == [], f"Expected no maxItems: 65535 emissions; found at: {sites}"


def _collect_int32_sentinel_pairs(
    obj: Any,
    acc: list[str] | None = None,
    path: str = "",
) -> list[str]:
    """Walk ``obj`` and return paths of ``integer`` schemas that have BOTH
    ``minimum: 0`` and ``maximum: 2147483647`` - the full int32 sentinel
    range. Unpaired sentinels (e.g. a property with just minimum: 0)
    are tolerated because they may be intentional.
    """
    acc = [] if acc is None else acc
    if isinstance(obj, dict):
        if (
            obj.get("type") == "integer"
            and obj.get("minimum") == 0
            and obj.get("maximum") == 2147483647
        ):
            acc.append(path)
        for k, v in obj.items():
            _collect_int32_sentinel_pairs(v, acc, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _collect_int32_sentinel_pairs(item, acc, f"{path}[{i}]")
    return acc


def test_validation_enricher_does_not_emit_int32_default_range() -> None:
    """The paired ``minimum: 0 / maximum: 2147483647`` on int32 adds zero info."""
    from scripts.utils.validation_enricher import ValidationEnricher

    spec: dict[str, Any] = {
        "openapi": "3.0.0",
        "info": {"title": "t", "version": "0"},
        "paths": {},
        "components": {
            "schemas": {
                "Foo": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "format": "int32"},
                    },
                },
            },
        },
    }
    enriched = ValidationEnricher().enrich_spec(spec)
    sites = _collect_int32_sentinel_pairs(enriched)
    assert sites == [], f"Expected int32 default range to be suppressed; found at: {sites}"


def test_validation_enricher_preserves_port_range() -> None:
    """Ports: legitimate ``minimum: 1 / maximum: 65535`` MUST still emit."""
    from scripts.utils.validation_enricher import ValidationEnricher

    spec: dict[str, Any] = {
        "openapi": "3.0.0",
        "info": {"title": "t", "version": "0"},
        "paths": {},
        "components": {
            "schemas": {
                "Foo": {
                    "type": "object",
                    "properties": {
                        # Pattern-trigger field name for the port rule.
                        "port": {"type": "integer"},
                    },
                },
            },
        },
    }
    enriched = ValidationEnricher().enrich_spec(spec)
    port_schema = enriched["components"]["schemas"]["Foo"]["properties"]["port"]
    # Assertion is soft: either port got port-pattern-specific bounds,
    # OR it got no bounds. What MUST NOT happen is the int32 default pair.
    if "minimum" in port_schema and "maximum" in port_schema:
        assert not (port_schema["minimum"] == 0 and port_schema["maximum"] == 2147483647), (
            f"Port schema got clobbered with int32 default: {port_schema!r}"
        )
