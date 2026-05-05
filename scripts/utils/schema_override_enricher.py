"""Schema Override Enricher — injects missing properties from schema_overrides.yaml."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "schema_overrides.yaml"


class SchemaOverrideEnricher:
    """Injects missing oneOf sibling fields declared in schema_overrides.yaml.

    Runs during the merge phase, before ConflictsWithEnricher, so that
    x-ves-oneof-field-* arrays are complete when conflicts-with derivation runs.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize with optional config path override."""
        self.config_path = Path(config_path) if config_path else CONFIG_PATH
        config = self._load_config()
        self.overrides: dict[str, Any] = config.get("overrides", {})
        self._compiled: list[dict] = self._compile_overrides()
        self._stats = self._empty_stats()

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            logger.warning("schema_overrides.yaml not found at %s", self.config_path)
            return {}
        with self.config_path.open() as f:
            return yaml.safe_load(f) or {}

    def _compile_overrides(self) -> list[dict]:
        compiled: list[dict | None] = []
        for entry in self.overrides.values():
            compiled.extend(
                self._compile_single(schema_entry) for schema_entry in entry.get("schemas", [])
            )
        return [c for c in compiled if c is not None]

    @staticmethod
    def _compile_single(schema_entry: dict) -> dict | None:
        try:
            return {
                "regex": re.compile(schema_entry["pattern"]),
                "oneof_group": schema_entry["oneof_group"],
                "complete_variants": schema_entry["complete_variants"],
                "inject_properties": schema_entry.get("inject_properties", {}),
            }
        except re.error as e:
            logger.warning("Invalid override pattern '%s': %s", schema_entry.get("pattern"), e)
            return None

    @staticmethod
    def _empty_stats() -> dict[str, int]:
        return {
            "schemas_processed": 0,
            "schemas_matched": 0,
            "properties_injected": 0,
            "oneof_arrays_updated": 0,
            "error_count": 0,
        }

    def enrich_spec(self, spec: dict) -> dict:
        """Enrich spec by injecting missing oneOf properties and updating variant arrays."""
        schemas = spec.get("components", {}).get("schemas")
        if not schemas:
            return spec

        for schema_name, schema in schemas.items():
            self._stats["schemas_processed"] += 1
            self._apply_overrides(schema_name, schema)

        return spec

    def _apply_overrides(self, schema_name: str, schema: dict) -> None:
        for override in self._compiled:
            if not override["regex"].search(schema_name):
                continue
            self._stats["schemas_matched"] += 1

            group = override["oneof_group"]
            ext_key = f"x-ves-oneof-field-{group}"

            existing_variants = schema.get(ext_key, [])
            if isinstance(existing_variants, str):
                existing_variants = yaml.safe_load(existing_variants)
            existing_set = set(existing_variants)

            props = schema.get("properties", {})
            for prop_name, prop_def in override["inject_properties"].items():
                if prop_name not in props:
                    props[prop_name] = dict(prop_def)
                    self._stats["properties_injected"] += 1

            if "properties" not in schema and override["inject_properties"]:
                schema["properties"] = props

            new_variants = []
            for v in override["complete_variants"]:
                if v not in existing_set:
                    new_variants.append(v)
                    existing_set.add(v)

            if new_variants:
                schema[ext_key] = sorted(existing_set)
                self._stats["oneof_arrays_updated"] += 1

    def get_stats(self) -> dict[str, int]:
        """Return current enrichment statistics."""
        return dict(self._stats)

    def reset_stats(self) -> None:
        """Reset statistics for next domain iteration."""
        self._stats = self._empty_stats()
