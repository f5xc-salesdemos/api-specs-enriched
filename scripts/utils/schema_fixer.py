#!/usr/bin/env python3
# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Schema fixer for OpenAPI specifications.

Fixes malformed schema definitions that violate OpenAPI 3.0.3 specification,
such as schemas with 'format' but missing 'type' field.
"""

from pathlib import Path
from typing import Any, ClassVar

import yaml


class SchemaFixer:
    """Fixes malformed schema definitions in OpenAPI specs.

    Two independent fixes are provided:

    ``fix_spec()`` adds missing 'type' fields where 'format' exists
    alone (addresses 14,000+ malformed error response schemas). It
    runs early in the enrichment pipeline, before constraint and
    description enrichers read the schema.

    ``inject_max_items()`` stamps a configurable default ``maxItems``
    onto every array schema that lacks one so the output satisfies
    Checkov's CKV_OPENAPI_21 check under Super-Linter. It must run
    after ``ConstraintEnricher`` so the synthetic bound does not leak
    into ``x-f5xc-constraints`` and shadow the pattern-inferred
    bounds that downstream tooling relies on.
    """

    # Default upper bound injected into array schemas that do not
    # declare `maxItems` explicitly. 65535 is a generous-but-bounded
    # ceiling: large enough for any real F5 XC config payload, small
    # enough that Checkov CKV_OPENAPI_21 is satisfied. Upstream-set
    # values are never overwritten.
    DEFAULT_ARRAY_MAX_ITEMS: ClassVar[int] = 65535

    # Mapping of format values to their corresponding type
    FORMAT_TYPE_MAPPING: ClassVar[dict[str, str]] = {
        # String formats
        "string": "string",
        "binary": "string",
        "byte": "string",
        "date": "string",
        "date-time": "string",
        "password": "string",
        "uuid": "string",
        "email": "string",
        "uri": "string",
        "hostname": "string",
        "ipv4": "string",
        "ipv6": "string",
        # Integer formats
        "int32": "integer",
        "int64": "integer",
        # Number formats
        "float": "number",
        "double": "number",
    }

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize with configuration from file.

        Args:
            config_path: Path to enrichment.yaml config.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "enrichment.yaml"

        # Default configuration
        self._fix_format_without_type = True
        self._fix_missing_max_items = True
        self._default_max_items = self.DEFAULT_ARRAY_MAX_ITEMS
        self._format_type_mapping = self.FORMAT_TYPE_MAPPING.copy()

        self._load_config(config_path)

        # Statistics tracking
        self._fixes_applied = 0
        self._max_items_added = 0

    def _load_config(self, config_path: Path) -> None:
        """Load configuration from YAML config."""
        if not config_path.exists():
            return

        with config_path.open() as f:
            config = yaml.safe_load(f) or {}

        schema_config = config.get("schema_fixes", {})
        self._fix_format_without_type = schema_config.get("fix_format_without_type", True)
        self._fix_missing_max_items = schema_config.get("fix_missing_max_items", True)
        self._default_max_items = schema_config.get(
            "default_max_items",
            self.DEFAULT_ARRAY_MAX_ITEMS,
        )

        # Override format-type mappings if provided
        custom_mappings = schema_config.get("format_type_mapping", {})
        if custom_mappings:
            self._format_type_mapping.update(custom_mappings)

    def fix_spec(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Apply early-stage schema fixes (format-without-type).

        Intentionally does NOT inject ``maxItems``; that is a late-stage
        Checkov-compliance pass — see ``inject_max_items()``.

        Args:
            spec: OpenAPI specification dictionary.

        Returns:
            Specification with fixed schemas.
        """
        self._fixes_applied = 0
        return self._fix_recursive(spec)

    def inject_max_items(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Inject a default ``maxItems`` into every array schema that lacks one.

        Must run **after** ``ConstraintEnricher`` so the synthetic bound
        does not leak into ``x-f5xc-constraints``.

        Args:
            spec: OpenAPI specification dictionary.

        Returns:
            Specification with ``maxItems`` stamped on every unbounded
            array schema.
        """
        self._max_items_added = 0
        if not self._fix_missing_max_items:
            return spec
        return self._inject_max_items_recursive(spec)

    def _fix_recursive(self, obj: Any) -> Any:
        """Recursively traverse and apply the format-without-type fix."""
        if isinstance(obj, dict):
            if self._fix_format_without_type and self._needs_type_fix(obj):
                obj = self._apply_type_fix(obj)
            return {key: self._fix_recursive(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [self._fix_recursive(item) for item in obj]
        return obj

    def _inject_max_items_recursive(self, obj: Any) -> Any:
        """Recursively traverse and stamp maxItems on unbounded arrays."""
        if isinstance(obj, dict):
            if self._needs_max_items(obj):
                obj = self._apply_max_items(obj)
            return {key: self._inject_max_items_recursive(value) for key, value in obj.items()}
        if isinstance(obj, list):
            return [self._inject_max_items_recursive(item) for item in obj]
        return obj

    def _needs_max_items(self, obj: dict[str, Any]) -> bool:
        """Check if object is an array schema missing a maxItems bound.

        Checkov's CKV_OPENAPI_21 requires every array to declare
        maxItems to guard against unbounded payloads. Only adds
        when the field is absent — upstream-set values are respected.
        """
        if obj.get("type") != "array":
            return False
        if "maxItems" in obj:
            return False
        # $ref objects and composition keywords are handled elsewhere
        # — never augment them.
        return not any(key in obj for key in ("$ref", "allOf", "oneOf", "anyOf"))

    def _apply_max_items(self, obj: dict[str, Any]) -> dict[str, Any]:
        """Inject the configured default maxItems into an array schema."""
        obj = {**obj, "maxItems": self._default_max_items}
        self._max_items_added += 1
        return obj

    def _needs_type_fix(self, obj: dict[str, Any]) -> bool:
        """Check if object has 'format' but no 'type' field.

        This is a common issue in error response schemas where they only
        specify format: "string" without the required type field.
        """
        # Must have 'format' field
        if "format" not in obj:
            return False

        # Must NOT have 'type' field
        if "type" in obj:
            return False

        # Must NOT be a reference (has $ref)
        if "$ref" in obj:
            return False

        # Must NOT have allOf/oneOf/anyOf (composition)
        return not any(key in obj for key in ("allOf", "oneOf", "anyOf"))

    def _apply_type_fix(self, obj: dict[str, Any]) -> dict[str, Any]:
        """Add missing 'type' field based on 'format' value."""
        format_value = obj.get("format", "")

        # Look up the appropriate type for this format
        type_value = self._format_type_mapping.get(format_value.lower(), "string")

        # Create new dict with 'type' added before other fields
        result = {"type": type_value}
        result.update(obj)

        self._fixes_applied += 1
        return result

    def get_stats(self) -> dict[str, Any]:
        """Return statistics about fixes applied."""
        return {
            "fixes_applied": self._fixes_applied,
            "fix_format_without_type": self._fix_format_without_type,
            "max_items_added": self._max_items_added,
            "fix_missing_max_items": self._fix_missing_max_items,
            "default_max_items": self._default_max_items,
        }
