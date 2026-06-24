# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Console UI Enricher for OpenAPI specifications.

Applies console UI metadata from config/console_ui.yaml to OpenAPI specs:
- x-f5xc-console (schema-level): Navigation, routing, and form structure
- x-f5xc-console-field (property-level): Widget type, selector, visibility
- x-f5xc-console-navigation (spec-level): Global navigation tree

This enrichment enables downstream consumers (xcsh, vscode-xcsh,
console catalog) to derive console navigation and form metadata directly
from the enriched API specs — the single source of truth.

Usage:
    enricher = ConsoleUIEnricher()
    spec = enricher.enrich_spec(spec)
    stats = enricher.get_stats()
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .extension_constants import (
    X_F5XC_CONSOLE,
    X_F5XC_CONSOLE_FIELD,
    X_F5XC_CONSOLE_NAVIGATION,
)


@dataclass
class ConsoleUIEnrichmentStats:
    """Statistics from console UI enrichment."""

    specs_processed: int = 0
    resources_enriched: int = 0
    fields_enriched: int = 0
    sections_mapped: int = 0
    skipped_no_config: int = 0
    navigation_applied: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "specs_processed": self.specs_processed,
            "resources_enriched": self.resources_enriched,
            "fields_enriched": self.fields_enriched,
            "sections_mapped": self.sections_mapped,
            "skipped_no_config": self.skipped_no_config,
            "navigation_applied": self.navigation_applied,
        }


class ConsoleUIEnricher:
    """Enrich OpenAPI specifications with console UI metadata.

    Loads console UI configuration from config/console_ui.yaml and applies
    it to the enriched specs at schema-level (per resource) and property-level
    (per field).

    The enrichment maps API resources to their console UI locations:
    - Which workspace the resource belongs to
    - Sidebar navigation path and breadcrumbs
    - URL route pattern for the list/create views
    - Form sections with their API field groupings
    - Per-field widget metadata (type, defaults, selectors)

    Attributes:
        config_path: Path to console_ui.yaml
        field_config_path: Path to console_field_metadata.yaml
        config: Loaded console UI configuration
        field_config: Loaded field metadata configuration
        stats: Enrichment statistics
    """

    def __init__(
        self,
        config_path: Path | None = None,
        field_config_path: Path | None = None,
    ) -> None:
        """Initialize enricher with console UI configuration.

        Args:
            config_path: Path to console_ui.yaml.
                        Defaults to config/console_ui.yaml.
            field_config_path: Path to console_field_metadata.yaml.
                              Defaults to config/console_field_metadata.yaml.
        """
        config_dir = Path(__file__).parent.parent.parent / "config"

        if config_path is None:
            config_path = config_dir / "console_ui.yaml"
        if field_config_path is None:
            field_config_path = config_dir / "console_field_metadata.yaml"

        self.config_path = config_path
        self.field_config_path = field_config_path
        self.config: dict[str, Any] = {}
        self.field_config: dict[str, Any] = {}
        self.stats = ConsoleUIEnrichmentStats()

        self._load_config()

    def _load_config(self) -> None:
        """Load console UI configuration from YAML files."""
        if self.config_path.exists():
            try:
                with self.config_path.open() as f:
                    self.config = yaml.safe_load(f) or {}
            except yaml.YAMLError:
                pass

        if self.field_config_path.exists():
            try:
                with self.field_config_path.open() as f:
                    self.field_config = yaml.safe_load(f) or {}
            except yaml.YAMLError:
                pass

    def _extract_resource_kind(self, spec: dict[str, Any]) -> str | None:
        """Extract resource kind from spec metadata.

        Looks for the resource kind in the x-ves-proto-package or info title,
        then normalizes to the config key format (e.g., 'http_loadbalancer').

        Args:
            spec: OpenAPI specification dictionary

        Returns:
            Resource kind string or None if not determinable
        """
        proto_pkg = spec.get("info", {}).get("x-ves-proto-package", "")
        if proto_pkg:
            parts = proto_pkg.split(".")
            if parts:
                kind = parts[-1]
                if kind in self.config.get("resources", {}):
                    return kind

        title = spec.get("info", {}).get("title", "")
        if title:
            normalized = title.lower().replace(" ", "_").replace("-", "_")
            for key in self.config.get("resources", {}):
                if key in normalized:
                    return key

        for path in spec.get("paths", {}):
            for key in self.config.get("resources", {}):
                if key in path.replace("-", "_"):
                    return key

        return None

    def enrich_spec(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Apply console UI enrichments to an OpenAPI spec.

        Adds:
        - x-f5xc-console on the CreateSpecType schema (schema-level)
        - x-f5xc-console-field on individual properties (property-level)
        - x-f5xc-console-navigation on the spec info (spec-level)

        Args:
            spec: OpenAPI specification dictionary

        Returns:
            Enriched specification (modified in-place)
        """
        self.stats.specs_processed += 1

        resource_kind = self._extract_resource_kind(spec)
        if resource_kind is None or resource_kind not in self.config.get("resources", {}):
            self.stats.skipped_no_config += 1
            return spec

        ui_config = self.config["resources"][resource_kind]

        self._enrich_schema_level(spec, resource_kind, ui_config)
        self._enrich_property_level(spec, resource_kind)
        self._enrich_navigation(spec)

        self.stats.resources_enriched += 1
        return spec

    def _enrich_schema_level(
        self,
        spec: dict[str, Any],
        kind: str,
        ui_config: dict[str, Any],
    ) -> None:
        """Add x-f5xc-console to the resource's CreateSpecType schema.

        Args:
            spec: OpenAPI specification
            kind: Resource kind (e.g., 'http_loadbalancer')
            ui_config: Console UI configuration for this resource
        """
        schemas = spec.get("components", {}).get("schemas", {})

        target_schemas = [
            f"views{kind}CreateSpecType",
            f"{kind}CreateSpecType",
        ]

        for candidate in target_schemas:
            if candidate not in schemas:
                continue
            if X_F5XC_CONSOLE in schemas[candidate]:
                break

            workspace_id = ui_config.get("workspace", "")
            workspace_config = self.config.get("workspaces", {}).get(workspace_id, {})

            console_metadata: dict[str, Any] = {
                "workspace": workspace_id,
                "workspace_label": workspace_config.get("label", ""),
                "route_prefix": workspace_config.get("route_prefix", ""),
                "menu_path": ui_config.get("menu_path", []),
                "route_pattern": ui_config.get("route_pattern", ""),
                "breadcrumbs": ui_config.get("breadcrumbs", []),
            }

            if "add_action" in ui_config:
                console_metadata["add_action"] = ui_config["add_action"]
            if "save_action" in ui_config:
                console_metadata["save_action"] = ui_config["save_action"]
            if "form_tabs" in ui_config:
                console_metadata["form_tabs"] = ui_config["form_tabs"]
            if "namespace_scoped" in ui_config:
                console_metadata["namespace_scoped"] = ui_config["namespace_scoped"]

            if "form_sections" in ui_config:
                console_metadata["form_sections"] = ui_config["form_sections"]
                self.stats.sections_mapped += len(ui_config["form_sections"])

            if "metadata" in ui_config:
                console_metadata["metadata"] = ui_config["metadata"]

            schemas[candidate][X_F5XC_CONSOLE] = console_metadata
            break

    def _enrich_property_level(
        self,
        spec: dict[str, Any],
        kind: str,
    ) -> None:
        """Add x-f5xc-console-field to individual API properties.

        Args:
            spec: OpenAPI specification
            kind: Resource kind
        """
        field_overrides = self.field_config.get("resources", {}).get(kind, {})
        if not field_overrides:
            return

        schemas = spec.get("components", {}).get("schemas", {})

        for schema_obj in schemas.values():
            if "properties" not in schema_obj:
                continue

            for prop_name, prop_obj in schema_obj["properties"].items():
                full_path = f"spec.{prop_name}"

                if full_path in field_overrides and X_F5XC_CONSOLE_FIELD not in prop_obj:
                    prop_obj[X_F5XC_CONSOLE_FIELD] = field_overrides[full_path]
                    self.stats.fields_enriched += 1

    def _enrich_navigation(self, spec: dict[str, Any]) -> None:
        """Add x-f5xc-console-navigation to spec info.

        Only applied if the config contains a navigation tree.

        Args:
            spec: OpenAPI specification
        """
        workspaces = self.config.get("workspaces")
        if not workspaces:
            return

        if X_F5XC_CONSOLE_NAVIGATION not in spec.get("info", {}):
            spec.setdefault("info", {})[X_F5XC_CONSOLE_NAVIGATION] = {
                "workspaces": workspaces,
            }
            self.stats.navigation_applied += 1

    def get_stats(self) -> dict[str, Any]:
        """Return enrichment statistics.

        Returns:
            Dictionary of enrichment metrics
        """
        return self.stats.to_dict()
