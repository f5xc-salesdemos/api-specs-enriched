# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Conflicts-with enricher for OpenAPI specifications.

This enricher auto-derives mutual exclusivity relationships from existing
x-ves-oneof-field-* extensions and adds x-f5xc-conflicts-with to each
property, enabling downstream tools (Terraform, CLI, MCP) to validate
conflicts at schema level rather than runtime.

Issue: #494 - Add x-f5xc-conflicts-with extension for OneOf groups
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from .extension_constants import X_F5XC_CONFLICTS_WITH, X_VES_ONEOF_FIELD_PREFIX

logger = logging.getLogger(__name__)


@dataclass
class ConflictsWithEnrichmentStats:
    """Statistics for conflicts-with enrichment."""

    schemas_processed: int = 0
    schemas_with_oneof: int = 0
    oneof_groups_found: int = 0
    conflicts_added: int = 0
    properties_enriched: int = 0
    existing_preserved: int = 0
    ref_skipped: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "schemas_processed": self.schemas_processed,
            "schemas_with_oneof": self.schemas_with_oneof,
            "oneof_groups_found": self.oneof_groups_found,
            "conflicts_added": self.conflicts_added,
            "properties_enriched": self.properties_enriched,
            "existing_preserved": self.existing_preserved,
            "ref_skipped": self.ref_skipped,
            "error_count": len(self.errors),
            "errors": self.errors,
        }


class ConflictsWithEnricher:
    """Enrich OpenAPI specs with x-f5xc-conflicts-with extensions.

    Auto-derives mutual exclusivity relationships from x-ves-oneof-field-*
    extensions in schemas. For each OneOf group, adds x-f5xc-conflicts-with
    to each variant property listing all other variants in the same group.

    Example input schema:
        {
            "type": "object",
            "x-ves-oneof-field-host_header_choice": ["host_header", "use_origin_server_name"],
            "properties": {
                "host_header": {"type": "string"},
                "use_origin_server_name": {"type": "object"}
            }
        }

    Example output:
        {
            "type": "object",
            "x-ves-oneof-field-host_header_choice": ["host_header", "use_origin_server_name"],
            "properties": {
                "host_header": {
                    "type": "string",
                    "x-f5xc-conflicts-with": ["use_origin_server_name"]
                },
                "use_origin_server_name": {
                    "type": "object",
                    "x-f5xc-conflicts-with": ["host_header"]
                }
            }
        }
    """

    def __init__(self) -> None:
        """Initialize the enricher."""
        self.stats = ConflictsWithEnrichmentStats()

    def enrich_spec(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Enrich OpenAPI specification with conflicts-with extensions.

        Args:
            spec: OpenAPI specification dictionary

        Returns:
            Enriched specification
        """
        schemas = spec.get("components", {}).get("schemas", {})

        if not schemas:
            logger.debug("No schemas found in spec, skipping conflicts-with enrichment")
            return spec

        logger.info("Enriching %d schemas with conflicts-with extensions", len(schemas))

        for schema_name, schema in schemas.items():
            self.stats.schemas_processed += 1
            self._enrich_schema(schema_name, schema)

        logger.info("Conflicts-with enrichment complete: %s", self.stats.to_dict())
        return spec

    def _enrich_schema(self, schema_name: str, schema: dict[str, Any]) -> None:
        """Enrich individual schema with conflicts-with extensions.

        Args:
            schema_name: Name of the schema
            schema: Schema definition
        """
        if not isinstance(schema, dict):
            return

        # Find all x-ves-oneof-field-* extensions in the schema
        oneof_groups = self._extract_oneof_groups(schema)

        if not oneof_groups:
            return

        self.stats.schemas_with_oneof += 1
        self.stats.oneof_groups_found += len(oneof_groups)

        properties = schema.get("properties", {})
        if not properties:
            logger.debug(
                "Schema %s has OneOf groups but no properties, skipping",
                schema_name,
            )
            return

        try:
            # For each OneOf group, add conflicts-with to each variant property
            for group_name, variants in oneof_groups.items():
                self._apply_conflicts_to_group(
                    schema_name,
                    properties,
                    group_name,
                    variants,
                )
        except Exception as e:
            logger.exception("Error enriching schema %s with conflicts-with", schema_name)
            self.stats.errors.append(
                {
                    "schema": schema_name,
                    "error": str(e),
                },
            )

    def _extract_oneof_groups(
        self,
        schema: dict[str, Any],
    ) -> dict[str, list[str]]:
        """Extract OneOf groups from schema.

        Finds all x-ves-oneof-field-* extensions and returns a mapping
        of group names to variant field names.

        Handles both list values and JSON-encoded string values (e.g.,
        '["host_header","use_origin_server_name"]').

        Args:
            schema: Schema definition

        Returns:
            Dictionary mapping group names to lists of variant field names
        """
        oneof_groups: dict[str, list[str]] = {}

        for key, value in schema.items():
            if key.startswith(X_VES_ONEOF_FIELD_PREFIX):
                # Extract group name from extension key
                # e.g., "x-ves-oneof-field-host_header_choice" -> "host_header_choice"
                group_name = key[len(X_VES_ONEOF_FIELD_PREFIX) :]

                # Handle JSON-encoded string values
                variants = value
                if isinstance(value, str):
                    try:
                        variants = json.loads(value)
                    except json.JSONDecodeError:
                        logger.debug(
                            "Could not parse OneOf group %s value as JSON: %s",
                            group_name,
                            value,
                        )
                        continue

                if isinstance(variants, list) and len(variants) >= 2:
                    # Only process groups with 2+ variants (single variant is not a conflict)
                    oneof_groups[group_name] = variants
                elif isinstance(variants, list) and len(variants) == 1:
                    logger.debug(
                        "Skipping single-variant OneOf group %s: %s",
                        group_name,
                        variants,
                    )

        return oneof_groups

    def _apply_conflicts_to_group(
        self,
        schema_name: str,
        properties: dict[str, Any],
        group_name: str,
        variants: list[str],
    ) -> None:
        """Apply conflicts-with extensions to properties in a OneOf group.

        For each variant in the group, adds x-f5xc-conflicts-with listing
        all other variants in the same group.

        Args:
            schema_name: Name of the schema (for logging)
            properties: Properties dictionary from schema
            group_name: Name of the OneOf group
            variants: List of variant field names
        """
        for variant in variants:
            if variant not in properties:
                logger.debug(
                    "Schema %s: variant %s not found in properties for group %s",
                    schema_name,
                    variant,
                    group_name,
                )
                continue

            prop_schema = properties[variant]
            if not isinstance(prop_schema, dict):
                continue

            # Skip properties that have $ref to avoid Spectral no-$ref-siblings
            # violation. In OpenAPI 3.0, $ref must not appear alongside other
            # properties. The conflicts-with metadata is informational and can
            # safely be omitted for $ref properties.
            if "$ref" in prop_schema:
                logger.debug(
                    "Schema %s: skipping variant %s (has $ref) for group %s",
                    schema_name,
                    variant,
                    group_name,
                )
                self.stats.ref_skipped += 1
                continue

            # Calculate other variants (all variants except this one)
            other_variants = [v for v in variants if v != variant]

            if not other_variants:
                continue

            # Check if x-f5xc-conflicts-with already exists
            if X_F5XC_CONFLICTS_WITH in prop_schema:
                # Preserve existing value, merge if needed
                existing = prop_schema[X_F5XC_CONFLICTS_WITH]
                if isinstance(existing, list):
                    # Merge with existing, avoiding duplicates
                    merged = list(set(existing) | set(other_variants))
                    if merged != existing:
                        prop_schema[X_F5XC_CONFLICTS_WITH] = sorted(merged)
                        self.stats.conflicts_added += len(merged) - len(existing)
                    self.stats.existing_preserved += 1
                    continue

            # Add new x-f5xc-conflicts-with extension
            prop_schema[X_F5XC_CONFLICTS_WITH] = sorted(other_variants)
            self.stats.properties_enriched += 1
            self.stats.conflicts_added += len(other_variants)

    def get_stats(self) -> dict[str, Any]:
        """Get enrichment statistics.

        Returns:
            Statistics dictionary
        """
        return self.stats.to_dict()

    def reset_stats(self) -> None:
        """Reset statistics for a new enrichment run."""
        self.stats = ConflictsWithEnrichmentStats()
