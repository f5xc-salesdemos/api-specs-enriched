# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Tests for MinimalDefaultsExporter.

Verifies that the exporter walks each covered resource's SpecType schema
(resolving allOf/$ref, building spec.-prefixed dot-paths) and emits the flat
{serverDefaultFields, fieldDefaults, minimumConfigFields, fieldConflicts}
artifact consumed by @f5-sales-demo/pi-resource-management.
"""

import pytest

from scripts.utils.minimal_defaults_exporter import MinimalDefaultsExporter


@pytest.fixture
def exporter(tmp_path):
    """Exporter with a one-resource config matching origin_pool SpecTypes."""
    config_file = tmp_path / "discovered_defaults.yaml"
    config_file.write_text(
        """\
settings: {}
resources:
  origin_pool:
    schema_pattern: "origin_pool.*SpecType"
"""
    )
    return MinimalDefaultsExporter(config_path=config_file)


@pytest.fixture
def schemas():
    """A minimal enriched component-schema set for origin_pool."""
    return {
        "viewsorigin_poolGlobalSpecType": {
            "properties": {
                "endpoint_selection": {
                    "type": "string",
                    "default": "DISTRIBUTED",
                    "x-f5xc-server-default": True,
                },
                "round_robin": {
                    "allOf": [{"$ref": "#/components/schemas/ioschemaEmpty"}],
                    "default": {},
                    "x-f5xc-server-default": True,
                    "x-f5xc-conflicts-with": ["least_active", "random"],
                },
                "origin_servers": {
                    "type": "array",
                    "x-f5xc-required-for": {"minimum_config": True, "create": True},
                },
                "advanced_options": {
                    "allOf": [{"$ref": "#/components/schemas/originPoolAdvancedOptions"}],
                },
            },
        },
        "ioschemaEmpty": {"type": "object", "properties": {}},
        "originPoolAdvancedOptions": {
            "properties": {
                "connection_timeout": {
                    "type": "integer",
                    "default": 0,
                    "x-f5xc-server-default": True,
                },
            },
        },
    }


class TestBuild:
    def test_collects_server_default_fields_with_spec_prefix(self, exporter, schemas):
        result = exporter.build(schemas)
        op = result["resources"]["origin_pool"]
        assert sorted(op["serverDefaultFields"]) == [
            "spec.advanced_options.connection_timeout",
            "spec.endpoint_selection",
            "spec.round_robin",
        ]

    def test_records_known_default_values(self, exporter, schemas):
        op = exporter.build(schemas)["resources"]["origin_pool"]
        assert op["fieldDefaults"] == {
            "spec.endpoint_selection": "DISTRIBUTED",
            "spec.round_robin": {},
            "spec.advanced_options.connection_timeout": 0,
        }

    def test_collects_minimum_config_fields(self, exporter, schemas):
        op = exporter.build(schemas)["resources"]["origin_pool"]
        assert op["minimumConfigFields"] == ["spec.origin_servers"]

    def test_collects_field_conflicts(self, exporter, schemas):
        op = exporter.build(schemas)["resources"]["origin_pool"]
        assert op["fieldConflicts"] == {"spec.round_robin": ["least_active", "random"]}

    def test_includes_version(self, exporter, schemas):
        result = exporter.build(schemas, version="2.1.145")
        assert result["version"] == "2.1.145"
        assert "resources" in result

    def test_resource_with_no_markers_is_omitted(self, exporter):
        # SpecType present but no markers anywhere -> no resource entry.
        schemas = {"viewsorigin_poolGlobalSpecType": {"properties": {"name": {"type": "string"}}}}
        result = exporter.build(schemas)
        assert "origin_pool" not in result["resources"]

    def test_unmatched_resource_absent(self, exporter):
        # No schema matches the origin_pool pattern.
        result = exporter.build({"somethingElse": {"properties": {}}})
        assert result["resources"] == {}
