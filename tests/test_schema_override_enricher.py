"""Tests for SchemaOverrideEnricher."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from scripts.utils.schema_override_enricher import SchemaOverrideEnricher


@pytest.fixture
def config_path():
    return Path(__file__).parent.parent / "config" / "schema_overrides.yaml"


@pytest.fixture
def enricher(config_path):
    return SchemaOverrideEnricher(config_path=config_path)


@pytest.fixture
def healthcheck_spec():
    """Minimal spec with 3-variant healthcheck schemas (mimics upstream gap)."""
    base_props = {
        "http_health_check": {"$ref": "#/components/schemas/healthcheckHttpHealthCheck"},
        "tcp_health_check": {"$ref": "#/components/schemas/healthcheckTcpHealthCheck"},
        "udp_icmp_health_check": {"$ref": "#/components/schemas/ioschemaEmpty"},
        "timeout": {"type": "integer"},
        "interval": {"type": "integer"},
        "healthy_threshold": {"type": "integer"},
        "unhealthy_threshold": {"type": "integer"},
        "jitter_percent": {"type": "integer"},
    }
    base_ext = {
        "x-ves-oneof-field-health_check": [
            "http_health_check",
            "tcp_health_check",
            "udp_icmp_health_check",
        ],
    }

    def make_schema(_name):
        return {
            "type": "object",
            "properties": dict(base_props),
            **{k: list(v) for k, v in base_ext.items()},
        }

    return {
        "components": {
            "schemas": {
                "healthcheckCreateSpecType": make_schema("Create"),
                "healthcheckGetSpecType": make_schema("Get"),
                "healthcheckReplaceSpecType": make_schema("Replace"),
                "healthcheckHttpHealthCheck": {"type": "object", "properties": {}},
                "healthcheckTcpHealthCheck": {"type": "object", "properties": {}},
                "ioschemaEmpty": {"type": "object"},
            },
        },
    }


class TestSchemaOverrideEnricher:
    """Core enricher behavior."""

    def test_injects_missing_properties(self, enricher, healthcheck_spec):
        result = enricher.enrich_spec(healthcheck_spec)
        schema = result["components"]["schemas"]["healthcheckCreateSpecType"]
        for variant in [
            "dns_health_check",
            "dns_proxy_icmp_health_check",
            "dns_proxy_tcp_health_check",
            "dns_proxy_udp_health_check",
        ]:
            assert variant in schema["properties"], f"Missing injected property: {variant}"
            assert schema["properties"][variant] == {"$ref": "#/components/schemas/ioschemaEmpty"}

    def test_updates_oneof_extension_array(self, enricher, healthcheck_spec):
        result = enricher.enrich_spec(healthcheck_spec)
        for schema_name in [
            "healthcheckCreateSpecType",
            "healthcheckGetSpecType",
            "healthcheckReplaceSpecType",
        ]:
            schema = result["components"]["schemas"][schema_name]
            variants = schema["x-ves-oneof-field-health_check"]
            assert len(variants) == 7
            assert "dns_health_check" in variants
            assert "dns_proxy_udp_health_check" in variants

    def test_preserves_existing_properties(self, enricher, healthcheck_spec):
        result = enricher.enrich_spec(healthcheck_spec)
        schema = result["components"]["schemas"]["healthcheckCreateSpecType"]
        assert "http_health_check" in schema["properties"]
        assert "timeout" in schema["properties"]
        assert schema["properties"]["http_health_check"] == {
            "$ref": "#/components/schemas/healthcheckHttpHealthCheck"
        }

    def test_preserves_existing_variants_in_extension(self, enricher, healthcheck_spec):
        result = enricher.enrich_spec(healthcheck_spec)
        schema = result["components"]["schemas"]["healthcheckCreateSpecType"]
        variants = schema["x-ves-oneof-field-health_check"]
        for existing in ["http_health_check", "tcp_health_check", "udp_icmp_health_check"]:
            assert existing in variants

    def test_does_not_duplicate_existing_variants(self, enricher, healthcheck_spec):
        result = enricher.enrich_spec(healthcheck_spec)
        schema = result["components"]["schemas"]["healthcheckCreateSpecType"]
        variants = schema["x-ves-oneof-field-health_check"]
        assert len(variants) == len(set(variants))

    def test_skips_non_matching_schemas(self, enricher, healthcheck_spec):
        result = enricher.enrich_spec(healthcheck_spec)
        empty = result["components"]["schemas"]["ioschemaEmpty"]
        assert "x-ves-oneof-field-health_check" not in empty

    def test_stats_tracking(self, enricher, healthcheck_spec):
        enricher.enrich_spec(healthcheck_spec)
        stats = enricher.get_stats()
        assert stats["schemas_processed"] > 0
        assert stats["properties_injected"] == 12  # 4 variants x 3 schema types
        assert stats["oneof_arrays_updated"] == 3

    def test_reset_stats(self, enricher, healthcheck_spec):
        enricher.enrich_spec(healthcheck_spec)
        enricher.reset_stats()
        stats = enricher.get_stats()
        assert stats["schemas_processed"] == 0
        assert stats["properties_injected"] == 0


class TestEdgeCases:
    """Edge cases and error handling."""

    def test_empty_spec(self, enricher):
        result = enricher.enrich_spec({})
        assert result == {}

    def test_spec_without_schemas(self, enricher):
        result = enricher.enrich_spec({"components": {}})
        assert result == {"components": {}}

    def test_no_matching_schemas(self, enricher):
        spec = {
            "components": {
                "schemas": {
                    "unrelatedSchema": {
                        "type": "object",
                        "properties": {"foo": {"type": "string"}},
                    },
                },
            },
        }
        result = enricher.enrich_spec(spec)
        schema = result["components"]["schemas"]["unrelatedSchema"]
        assert "x-ves-oneof-field-health_check" not in schema

    def test_already_complete_spec(self, enricher, healthcheck_spec):
        """If all 7 variants already present, enricher should be a no-op."""
        schema = healthcheck_spec["components"]["schemas"]["healthcheckCreateSpecType"]
        schema["properties"]["dns_health_check"] = {"$ref": "#/components/schemas/ioschemaEmpty"}
        schema["x-ves-oneof-field-health_check"].append("dns_health_check")

        result = enricher.enrich_spec(healthcheck_spec)
        create_schema = result["components"]["schemas"]["healthcheckCreateSpecType"]
        assert len(create_schema["x-ves-oneof-field-health_check"]) == 7

    def test_preserves_json_string_encoding(self, enricher):
        """When x-ves-oneof-field is a JSON string, output must also be a JSON string."""
        import json

        spec = {
            "components": {
                "schemas": {
                    "healthcheckCreateSpecType": {
                        "type": "object",
                        "properties": {
                            "http_health_check": {
                                "$ref": "#/components/schemas/healthcheckHttpHealthCheck"
                            },
                        },
                        "x-ves-oneof-field-health_check": json.dumps(
                            [
                                "http_health_check",
                                "tcp_health_check",
                                "udp_icmp_health_check",
                            ]
                        ),
                    },
                },
            },
        }
        result = enricher.enrich_spec(spec)
        schema = result["components"]["schemas"]["healthcheckCreateSpecType"]
        ext_value = schema["x-ves-oneof-field-health_check"]
        assert isinstance(ext_value, str), f"Expected JSON string, got {type(ext_value)}"
        parsed = json.loads(ext_value)
        assert len(parsed) == 7
        assert "dns_health_check" in parsed


class TestConfigLoading:
    """Config file loading and validation."""

    def test_loads_real_config(self, config_path):
        enricher = SchemaOverrideEnricher(config_path=config_path)
        assert enricher.overrides is not None
        assert "healthcheck" in enricher.overrides

    def test_config_structure(self, config_path):
        with config_path.open() as f:
            config = yaml.safe_load(f)
        assert "overrides" in config
        hc = config["overrides"]["healthcheck"]
        assert "schemas" in hc
        for schema_entry in hc["schemas"]:
            assert "pattern" in schema_entry
            assert "oneof_group" in schema_entry
            assert "complete_variants" in schema_entry
            assert "inject_properties" in schema_entry
            re.compile(schema_entry["pattern"])
