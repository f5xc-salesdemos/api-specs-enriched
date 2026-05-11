"""Constrained Fields Enricher — stamps x-f5xc-constraints from minimum_configs.yaml.

Reads the ``constrained_fields`` section for each resource in minimum_configs.yaml
and applies structured constraint metadata to matching schema properties.  Merges
additively with any pre-existing ``x-f5xc-constraints`` set by the ConstraintEnricher.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

from .extension_constants import X_F5XC_CONSTRAINTS

logger = logging.getLogger(__name__)

_CAMELCASE_TO_SNAKE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")

# Schema suffixes that indicate top-level resource schemas worth enriching.
_RESOURCE_SUFFIXES = (
    "CreateSpecType",
    "UpdateSpecType",
    "GetSpecType",
    "ReplaceSpecType",
    "DeleteSpecType",
    "GlobalSpecType",
    "SpecType",
)


class ConstrainedFieldsEnricher:
    """Enrich OpenAPI specs with constraint metadata from minimum_configs.yaml."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize enricher, loading constrained_fields from minimum_configs.yaml."""
        self.config_path = (
            config_path or Path(__file__).parent.parent.parent / "config" / "minimum_configs.yaml"
        )
        self._resources: dict[str, Any] = {}
        self.stats: dict[str, int] = {
            "schemas_processed": 0,
            "constraints_applied": 0,
            "constraints_merged": 0,
            "fields_not_found": 0,
            "resources_matched": 0,
        }
        self._load_config()

    # ------------------------------------------------------------------
    # Config loading
    # ------------------------------------------------------------------

    def _load_config(self) -> None:
        try:
            with self.config_path.open() as f:
                cfg = yaml.safe_load(f) or {}
            self._resources = {
                name: data
                for name, data in cfg.get("resources", {}).items()
                if data.get("constrained_fields")
            }
            logger.info(
                "ConstrainedFieldsEnricher: loaded %d resources with constrained_fields",
                len(self._resources),
            )
        except FileNotFoundError:
            logger.warning("Config not found: %s", self.config_path)
        except yaml.YAMLError:
            logger.exception("Error parsing %s", self.config_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enrich_spec(self, spec: dict[str, Any]) -> dict[str, Any]:
        """Enrich *spec* in-place and return it."""
        if not self._resources:
            return spec

        schemas = spec.get("components", {}).get("schemas", {})
        logger.info("ConstrainedFieldsEnricher: scanning %d schemas", len(schemas))

        for schema_name, schema in schemas.items():
            self.stats["schemas_processed"] += 1
            resource_type = self._detect_resource_type(schema_name)
            if resource_type is None:
                continue
            resource_cfg = self._resources.get(resource_type)
            if resource_cfg is None:
                continue
            if not self._is_resource_schema(schema_name):
                continue

            self.stats["resources_matched"] += 1
            for field_def in resource_cfg.get("constrained_fields", []):
                self._apply_field_constraint(field_def, schema, schemas)

        logger.info("ConstrainedFieldsEnricher: done — %s", self.stats)
        return spec

    def get_stats(self) -> dict[str, int]:
        """Return enrichment statistics."""
        return dict(self.stats)

    def reset_stats(self) -> None:
        """Reset stats counters (call between domains in pipeline)."""
        for key in self.stats:
            self.stats[key] = 0

    # ------------------------------------------------------------------
    # Field resolution
    # ------------------------------------------------------------------

    def _apply_field_constraint(
        self,
        field_def: dict[str, Any],
        schema: dict[str, Any],
        all_schemas: dict[str, Any],
    ) -> None:
        """Resolve a dot-path and stamp ``x-f5xc-constraints`` on the terminal property.

        Walks ``spec.use_tls.tls_config.custom_security.min_version`` style paths
        through $ref chains and applies constraint metadata.
        """
        raw_path: str = field_def.get("field", "")
        parts = self._normalize_path(raw_path)
        if not parts:
            return

        prop = self._walk_path(parts, schema, all_schemas)
        if prop is None:
            self.stats["fields_not_found"] += 1
            logger.debug("Field path not found: %s", raw_path)
            return

        constraint = self._build_constraint(field_def)
        self._merge_constraint(prop, constraint)

    @staticmethod
    def _normalize_path(raw: str) -> list[str]:
        """Turn ``spec.foo[].bar`` into ``['foo', 'bar']`` (strip ``spec.`` prefix and ``[]``)."""
        path = raw.removeprefix("spec.")
        # Remove array brackets — we just walk into items automatically.
        path = re.sub(r"\[\]", "", path)
        return [p for p in path.split(".") if p]

    def _walk_path(
        self,
        parts: list[str],
        schema: dict[str, Any],
        all_schemas: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Walk *parts* through nested properties / $ref chains.

        Returns the property dict for the terminal field, or ``None``.
        """
        current = schema
        for i, part in enumerate(parts):
            # Resolve $ref if present
            current = self._resolve_ref(current, all_schemas)

            # Try properties directly
            props = current.get("properties", {})
            if part in props:
                if i == len(parts) - 1:
                    return props[part]
                current = props[part]
                continue

            # For arrays, dive into items
            items = current.get("items", {})
            if items:
                items = self._resolve_ref(items, all_schemas)
                items_props = items.get("properties", {})
                if part in items_props:
                    if i == len(parts) - 1:
                        return items_props[part]
                    current = items_props[part]
                    continue

            # Try allOf / oneOf variants
            for combo_key in ("allOf", "oneOf", "anyOf"):
                for variant in current.get(combo_key, []):
                    resolved = self._resolve_ref(variant, all_schemas)
                    vprops = resolved.get("properties", {})
                    if part in vprops:
                        if i == len(parts) - 1:
                            return vprops[part]
                        current = vprops[part]
                        break
                else:
                    continue
                break
            else:
                # Part not found at this level
                return None

        return None

    @staticmethod
    def _resolve_ref(node: dict[str, Any], all_schemas: dict[str, Any]) -> dict[str, Any]:
        """Dereference a single ``$ref`` if it points into ``#/components/schemas/``."""
        ref = node.get("$ref", "")
        if ref.startswith("#/components/schemas/"):
            ref_name = ref.rsplit("/", 1)[-1]
            return all_schemas.get(ref_name, node)
        return node

    # ------------------------------------------------------------------
    # Constraint building & merging
    # ------------------------------------------------------------------

    @staticmethod
    def _build_constraint(field_def: dict[str, Any]) -> dict[str, Any]:
        """Build the constraint dict from a config entry."""
        ctype = field_def.get("type", "")
        constraint: dict[str, Any] = {"source": "minimum_configs"}

        if ctype == "enum":
            constraint["constraintType"] = "enum"
            values = field_def.get("values")
            if values:
                constraint["enumValues"] = list(values)
        elif ctype == "integer":
            constraint["constraintType"] = "range"
            rng = field_def.get("range")
            if rng and len(rng) == 2:
                constraint["minimum"] = rng[0]
                constraint["maximum"] = rng[1]
        elif ctype == "array":
            constraint["constraintType"] = "array"
            if field_def.get("min_items") is not None:
                constraint["minItems"] = field_def["min_items"]
            if field_def.get("item_format"):
                constraint["itemFormat"] = field_def["item_format"]

        if "default" in field_def:
            constraint["default"] = field_def["default"]
        if field_def.get("description"):
            constraint["description"] = field_def["description"]

        return constraint

    def _merge_constraint(self, prop: dict[str, Any], new: dict[str, Any]) -> None:
        """Merge *new* constraint into the property's existing x-f5xc-constraints."""
        existing = prop.get(X_F5XC_CONSTRAINTS)
        if existing and isinstance(existing, dict):
            # Additive merge: don't overwrite constraintType or existing keys
            for key, value in new.items():
                if key not in existing:
                    existing[key] = value
            self.stats["constraints_merged"] += 1
        else:
            prop[X_F5XC_CONSTRAINTS] = new
            self.stats["constraints_applied"] += 1

    # ------------------------------------------------------------------
    # Resource type detection (mirrors MinimumConfigurationEnricher logic)
    # ------------------------------------------------------------------

    def _detect_resource_type(self, schema_name: str) -> str | None:
        """Map schema name → resource key in minimum_configs.yaml."""
        if schema_name in self._resources:
            return schema_name

        working = schema_name
        for prefix in ("views", "api", "schema"):
            if working.startswith(prefix):
                rest = working[len(prefix) :]
                if rest and rest[0] != "_":
                    working = rest
                break

        for suffix in _RESOURCE_SUFFIXES:
            if working.endswith(suffix):
                base = working[: -len(suffix)]
                snake = _CAMELCASE_TO_SNAKE.sub("_", base).lower()
                if snake in self._resources:
                    return snake

        snake_full = _CAMELCASE_TO_SNAKE.sub("_", working).lower()
        if snake_full in self._resources:
            return snake_full

        for resource in self._resources:
            if resource in working.lower():
                return resource

        return None

    @staticmethod
    def _is_resource_schema(name: str) -> bool:
        return any(name.endswith(s) for s in _RESOURCE_SUFFIXES)
