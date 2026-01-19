# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Unit tests for ConflictsWithEnricher."""

import pytest

from scripts.utils.conflicts_with_enricher import (
    ConflictsWithEnricher,
    ConflictsWithEnrichmentStats,
)
from scripts.utils.extension_constants import X_F5XC_CONFLICTS_WITH


@pytest.fixture
def enricher():
    """Create enricher instance."""
    return ConflictsWithEnricher()


@pytest.fixture
def spec_with_two_variant_oneof():
    """Create a spec with a two-variant OneOf group."""
    return {
        "components": {
            "schemas": {
                "healthcheckHttpHealthCheck": {
                    "type": "object",
                    "x-ves-oneof-field-host_header_choice": [
                        "host_header",
                        "use_origin_server_name",
                    ],
                    "properties": {
                        "host_header": {"type": "string"},
                        "use_origin_server_name": {"type": "object"},
                        "path": {"type": "string"},
                    },
                },
            },
        },
    }


@pytest.fixture
def spec_with_three_variant_oneof():
    """Create a spec with a three-variant OneOf group."""
    return {
        "components": {
            "schemas": {
                "appFirewallDetectionSetting": {
                    "type": "object",
                    "x-ves-oneof-field-signatures_staging_settings": [
                        "disable_staging",
                        "stage_new_and_updated_signatures",
                        "stage_new_signatures",
                    ],
                    "properties": {
                        "disable_staging": {"type": "object"},
                        "stage_new_and_updated_signatures": {"type": "object"},
                        "stage_new_signatures": {"type": "object"},
                        "other_field": {"type": "string"},
                    },
                },
            },
        },
    }


@pytest.fixture
def spec_with_multiple_oneof_groups():
    """Create a spec with multiple OneOf groups."""
    return {
        "components": {
            "schemas": {
                "complexSchema": {
                    "type": "object",
                    "x-ves-oneof-field-mode_choice": ["blocking", "monitoring"],
                    "x-ves-oneof-field-detection_choice": [
                        "default_detection",
                        "custom_detection",
                    ],
                    "properties": {
                        "blocking": {"type": "object"},
                        "monitoring": {"type": "object"},
                        "default_detection": {"type": "object"},
                        "custom_detection": {"type": "object"},
                    },
                },
            },
        },
    }


@pytest.fixture
def spec_with_single_variant():
    """Create a spec with a single-variant OneOf group (should be skipped)."""
    return {
        "components": {
            "schemas": {
                "singleVariantSchema": {
                    "type": "object",
                    "x-ves-oneof-field-only_choice": ["only_option"],
                    "properties": {
                        "only_option": {"type": "object"},
                    },
                },
            },
        },
    }


@pytest.fixture
def spec_with_existing_conflicts():
    """Create a spec with existing x-f5xc-conflicts-with values."""
    return {
        "components": {
            "schemas": {
                "existingConflictsSchema": {
                    "type": "object",
                    "x-ves-oneof-field-choice": ["option_a", "option_b", "option_c"],
                    "properties": {
                        "option_a": {
                            "type": "object",
                            X_F5XC_CONFLICTS_WITH: ["option_b"],  # Partial existing
                        },
                        "option_b": {"type": "object"},
                        "option_c": {"type": "object"},
                    },
                },
            },
        },
    }


@pytest.fixture
def spec_without_schemas():
    """Create a spec without schemas."""
    return {
        "info": {"title": "Empty Spec"},
        "paths": {},
    }


@pytest.fixture
def spec_without_properties():
    """Create a spec with OneOf but no properties."""
    return {
        "components": {
            "schemas": {
                "noPropertiesSchema": {
                    "type": "object",
                    "x-ves-oneof-field-choice": ["a", "b"],
                },
            },
        },
    }


@pytest.fixture
def spec_with_json_string_oneof():
    """Create a spec with OneOf extension value as JSON string (as in enriched specs)."""
    return {
        "components": {
            "schemas": {
                "healthcheckHttpHealthCheck": {
                    "type": "object",
                    "x-ves-oneof-field-host_header_choice": '["host_header","use_origin_server_name"]',
                    "properties": {
                        "host_header": {"type": "string"},
                        "use_origin_server_name": {"type": "object"},
                        "path": {"type": "string"},
                    },
                },
            },
        },
    }


class TestConflictsWithEnricherBasics:
    """Test basic enricher functionality."""

    def test_initialization(self):
        """Test enricher initializes correctly."""
        enricher = ConflictsWithEnricher()
        assert enricher is not None
        assert enricher.stats is not None

    def test_empty_spec(self, enricher):
        """Test handling of empty spec."""
        spec = {}
        result = enricher.enrich_spec(spec)
        assert result == spec
        stats = enricher.get_stats()
        assert stats["schemas_processed"] == 0

    def test_spec_without_schemas(self, enricher, spec_without_schemas):
        """Test handling of spec without schemas."""
        result = enricher.enrich_spec(spec_without_schemas)
        assert result == spec_without_schemas
        stats = enricher.get_stats()
        assert stats["schemas_processed"] == 0


class TestTwoVariantOneOf:
    """Test two-variant OneOf group enrichment."""

    def test_enriches_both_variants(self, enricher, spec_with_two_variant_oneof):
        """Test that both variants get x-f5xc-conflicts-with."""
        result = enricher.enrich_spec(spec_with_two_variant_oneof)

        schema = result["components"]["schemas"]["healthcheckHttpHealthCheck"]
        props = schema["properties"]

        # Check host_header has conflicts-with pointing to use_origin_server_name
        assert X_F5XC_CONFLICTS_WITH in props["host_header"]
        assert props["host_header"][X_F5XC_CONFLICTS_WITH] == ["use_origin_server_name"]

        # Check use_origin_server_name has conflicts-with pointing to host_header
        assert X_F5XC_CONFLICTS_WITH in props["use_origin_server_name"]
        assert props["use_origin_server_name"][X_F5XC_CONFLICTS_WITH] == ["host_header"]

        # Check that non-OneOf properties are unchanged
        assert X_F5XC_CONFLICTS_WITH not in props["path"]

    def test_statistics_updated(self, enricher, spec_with_two_variant_oneof):
        """Test that statistics are correctly updated."""
        enricher.enrich_spec(spec_with_two_variant_oneof)
        stats = enricher.get_stats()

        assert stats["schemas_processed"] == 1
        assert stats["schemas_with_oneof"] == 1
        assert stats["oneof_groups_found"] == 1
        assert stats["properties_enriched"] == 2
        assert stats["conflicts_added"] == 2  # Each variant points to 1 other


class TestThreeVariantOneOf:
    """Test three-variant OneOf group enrichment."""

    def test_enriches_all_three_variants(self, enricher, spec_with_three_variant_oneof):
        """Test that all three variants list the other two."""
        result = enricher.enrich_spec(spec_with_three_variant_oneof)

        schema = result["components"]["schemas"]["appFirewallDetectionSetting"]
        props = schema["properties"]

        # Each variant should list the other two (sorted)
        assert props["disable_staging"][X_F5XC_CONFLICTS_WITH] == [
            "stage_new_and_updated_signatures",
            "stage_new_signatures",
        ]
        assert props["stage_new_and_updated_signatures"][X_F5XC_CONFLICTS_WITH] == [
            "disable_staging",
            "stage_new_signatures",
        ]
        assert props["stage_new_signatures"][X_F5XC_CONFLICTS_WITH] == [
            "disable_staging",
            "stage_new_and_updated_signatures",
        ]

        # Non-OneOf field should not have conflicts-with
        assert X_F5XC_CONFLICTS_WITH not in props["other_field"]

    def test_statistics_for_three_variants(self, enricher, spec_with_three_variant_oneof):
        """Test statistics for three-variant group."""
        enricher.enrich_spec(spec_with_three_variant_oneof)
        stats = enricher.get_stats()

        assert stats["properties_enriched"] == 3
        # Each of 3 variants lists 2 others = 6 total conflicts
        assert stats["conflicts_added"] == 6


class TestMultipleOneOfGroups:
    """Test multiple OneOf groups in same schema."""

    def test_enriches_all_groups_independently(
        self,
        enricher,
        spec_with_multiple_oneof_groups,
    ):
        """Test that multiple OneOf groups are handled independently."""
        result = enricher.enrich_spec(spec_with_multiple_oneof_groups)

        schema = result["components"]["schemas"]["complexSchema"]
        props = schema["properties"]

        # Mode choice group
        assert props["blocking"][X_F5XC_CONFLICTS_WITH] == ["monitoring"]
        assert props["monitoring"][X_F5XC_CONFLICTS_WITH] == ["blocking"]

        # Detection choice group
        assert props["default_detection"][X_F5XC_CONFLICTS_WITH] == ["custom_detection"]
        assert props["custom_detection"][X_F5XC_CONFLICTS_WITH] == ["default_detection"]

    def test_statistics_for_multiple_groups(
        self,
        enricher,
        spec_with_multiple_oneof_groups,
    ):
        """Test statistics for multiple OneOf groups."""
        enricher.enrich_spec(spec_with_multiple_oneof_groups)
        stats = enricher.get_stats()

        assert stats["oneof_groups_found"] == 2
        assert stats["properties_enriched"] == 4


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_single_variant_skipped(self, enricher, spec_with_single_variant):
        """Test that single-variant groups are skipped."""
        result = enricher.enrich_spec(spec_with_single_variant)

        schema = result["components"]["schemas"]["singleVariantSchema"]
        props = schema["properties"]

        # Single variant should not have conflicts-with (nothing to conflict with)
        assert X_F5XC_CONFLICTS_WITH not in props["only_option"]

        stats = enricher.get_stats()
        assert stats["oneof_groups_found"] == 0

    def test_preserves_existing_conflicts(self, enricher, spec_with_existing_conflicts):
        """Test that existing x-f5xc-conflicts-with values are preserved and merged."""
        result = enricher.enrich_spec(spec_with_existing_conflicts)

        schema = result["components"]["schemas"]["existingConflictsSchema"]
        props = schema["properties"]

        # option_a had existing ["option_b"], should now have ["option_b", "option_c"]
        assert X_F5XC_CONFLICTS_WITH in props["option_a"]
        conflicts = props["option_a"][X_F5XC_CONFLICTS_WITH]
        assert "option_b" in conflicts
        assert "option_c" in conflicts

        stats = enricher.get_stats()
        assert stats["existing_preserved"] == 1

    def test_missing_properties_handled(self, enricher, spec_without_properties):
        """Test handling of schema with OneOf but no properties."""
        enricher.enrich_spec(spec_without_properties)

        stats = enricher.get_stats()
        assert stats["schemas_processed"] == 1
        # Schema has OneOf groups but no properties to enrich
        assert stats["schemas_with_oneof"] == 1
        assert stats["oneof_groups_found"] == 1
        assert stats["properties_enriched"] == 0  # No properties to enrich

    def test_reset_stats(self, enricher, spec_with_two_variant_oneof):
        """Test that reset_stats clears all counters."""
        enricher.enrich_spec(spec_with_two_variant_oneof)
        assert enricher.get_stats()["schemas_processed"] > 0

        enricher.reset_stats()
        stats = enricher.get_stats()

        assert stats["schemas_processed"] == 0
        assert stats["schemas_with_oneof"] == 0
        assert stats["conflicts_added"] == 0

    def test_handles_json_string_oneof_values(
        self,
        enricher,
        spec_with_json_string_oneof,
    ):
        """Test handling of JSON-encoded string values for OneOf extensions."""
        enriched_spec = enricher.enrich_spec(spec_with_json_string_oneof)

        schema = enriched_spec["components"]["schemas"]["healthcheckHttpHealthCheck"]
        props = schema["properties"]

        # Should correctly parse JSON string and add conflicts-with
        assert X_F5XC_CONFLICTS_WITH in props["host_header"]
        assert props["host_header"][X_F5XC_CONFLICTS_WITH] == ["use_origin_server_name"]

        assert X_F5XC_CONFLICTS_WITH in props["use_origin_server_name"]
        assert props["use_origin_server_name"][X_F5XC_CONFLICTS_WITH] == ["host_header"]

        # Non-OneOf field should not have conflicts-with
        assert X_F5XC_CONFLICTS_WITH not in props["path"]

        stats = enricher.get_stats()
        assert stats["schemas_with_oneof"] == 1
        assert stats["properties_enriched"] == 2


class TestStatisticsDataclass:
    """Test ConflictsWithEnrichmentStats dataclass."""

    def test_stats_to_dict(self):
        """Test statistics conversion to dictionary."""
        stats = ConflictsWithEnrichmentStats(
            schemas_processed=10,
            schemas_with_oneof=5,
            oneof_groups_found=8,
            conflicts_added=20,
            properties_enriched=16,
            existing_preserved=2,
        )

        result = stats.to_dict()

        assert result["schemas_processed"] == 10
        assert result["schemas_with_oneof"] == 5
        assert result["oneof_groups_found"] == 8
        assert result["conflicts_added"] == 20
        assert result["properties_enriched"] == 16
        assert result["existing_preserved"] == 2
        assert result["error_count"] == 0

    def test_stats_with_errors(self):
        """Test statistics with errors."""
        stats = ConflictsWithEnrichmentStats(
            errors=[{"schema": "TestSchema", "error": "Test error"}],
        )

        result = stats.to_dict()

        assert result["error_count"] == 1
        assert len(result["errors"]) == 1


class TestIntegrationScenarios:
    """Test integration-like scenarios with realistic spec structures."""

    def test_healthcheck_example_from_issue(self, enricher):
        """Test the healthcheck example from Issue #494."""
        spec = {
            "components": {
                "schemas": {
                    "healthcheckHttpHealthCheck": {
                        "type": "object",
                        "x-ves-oneof-field-host_header_choice": [
                            "host_header",
                            "use_origin_server_name",
                        ],
                        "properties": {
                            "host_header": {
                                "type": "string",
                                "description": "Host header to use",
                            },
                            "use_origin_server_name": {
                                "type": "object",
                                "description": "Use origin server name",
                            },
                            "path": {
                                "type": "string",
                                "description": "Health check path",
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds",
                            },
                        },
                    },
                },
            },
        }

        result = enricher.enrich_spec(spec)

        props = result["components"]["schemas"]["healthcheckHttpHealthCheck"]["properties"]

        # Verify the exact output format from the issue
        assert props["host_header"][X_F5XC_CONFLICTS_WITH] == ["use_origin_server_name"]
        assert props["use_origin_server_name"][X_F5XC_CONFLICTS_WITH] == ["host_header"]

        # Verify non-OneOf fields are unchanged
        assert X_F5XC_CONFLICTS_WITH not in props["path"]
        assert X_F5XC_CONFLICTS_WITH not in props["timeout"]

    def test_app_firewall_multiple_groups(self, enricher):
        """Test realistic app_firewall schema with multiple OneOf groups."""
        spec = {
            "components": {
                "schemas": {
                    "appFirewallCreateSpecType": {
                        "type": "object",
                        "x-ves-oneof-field-enforcement_mode_choice": [
                            "blocking",
                            "monitoring",
                        ],
                        "x-ves-oneof-field-detection_setting_choice": [
                            "ai_risk_based_blocking",
                            "default_detection_settings",
                            "detection_settings",
                        ],
                        "properties": {
                            "blocking": {"type": "object"},
                            "monitoring": {"type": "object"},
                            "ai_risk_based_blocking": {"type": "object"},
                            "default_detection_settings": {"type": "object"},
                            "detection_settings": {"type": "object"},
                            "name": {"type": "string"},
                        },
                    },
                },
            },
        }

        result = enricher.enrich_spec(spec)

        props = result["components"]["schemas"]["appFirewallCreateSpecType"]["properties"]

        # Enforcement mode group
        assert props["blocking"][X_F5XC_CONFLICTS_WITH] == ["monitoring"]
        assert props["monitoring"][X_F5XC_CONFLICTS_WITH] == ["blocking"]

        # Detection setting group (3 variants)
        assert set(props["ai_risk_based_blocking"][X_F5XC_CONFLICTS_WITH]) == {
            "default_detection_settings",
            "detection_settings",
        }
        assert set(props["default_detection_settings"][X_F5XC_CONFLICTS_WITH]) == {
            "ai_risk_based_blocking",
            "detection_settings",
        }
        assert set(props["detection_settings"][X_F5XC_CONFLICTS_WITH]) == {
            "ai_risk_based_blocking",
            "default_detection_settings",
        }

        # Name should not be affected
        assert X_F5XC_CONFLICTS_WITH not in props["name"]


class TestAcceptance:
    """Acceptance tests verifying end-to-end behavior with real-world patterns.

    These tests verify the enricher works correctly with schema patterns
    found in the actual F5 XC API specifications after pipeline processing.
    """

    def test_accepts_json_string_values_from_pipeline(self, enricher):
        """Acceptance: Enricher handles JSON-encoded values from pipeline output.

        The F5 XC pipeline stores x-ves-oneof-field-* values as JSON strings
        (e.g., '["host_header","use_origin_server_name"]'). The enricher must
        parse these correctly.
        """
        # Real-world pattern from virtual.json after pipeline processing
        spec = {
            "components": {
                "schemas": {
                    "healthcheckHttpHealthCheck": {
                        "type": "object",
                        "description": "HTTP Health Check configuration",
                        "x-displayname": "HTTP Health Check.",
                        "x-ves-oneof-field-host_header_choice": '["host_header","use_origin_server_name"]',
                        "x-ves-proto-message": "ves.io.schema.healthcheck.HttpHealthCheck",
                        "properties": {
                            "host_header": {
                                "type": "string",
                                "x-displayname": "Host Header Value.",
                            },
                            "use_origin_server_name": {
                                "type": "object",
                                "x-f5xc-server-default": True,
                            },
                            "path": {
                                "type": "string",
                                "x-ves-required": "true",
                            },
                        },
                    },
                },
            },
        }

        result = enricher.enrich_spec(spec)
        props = result["components"]["schemas"]["healthcheckHttpHealthCheck"]["properties"]

        # Acceptance criteria: Both variants have bidirectional conflicts
        assert props["host_header"][X_F5XC_CONFLICTS_WITH] == ["use_origin_server_name"]
        assert props["use_origin_server_name"][X_F5XC_CONFLICTS_WITH] == ["host_header"]

        # Acceptance criteria: Existing extensions preserved
        assert props["host_header"]["x-displayname"] == "Host Header Value."
        assert props["use_origin_server_name"]["x-f5xc-server-default"] is True
        assert props["path"]["x-ves-required"] == "true"

    def test_accepts_multiple_oneof_groups_in_single_schema(self, enricher):
        """Acceptance: Enricher handles schemas with 5+ OneOf groups.

        Real app_firewall schemas have many OneOf groups. Each group must
        be processed independently without cross-contamination.
        """
        spec = {
            "components": {
                "schemas": {
                    "appFirewallCreateSpecType": {
                        "type": "object",
                        # 6 OneOf groups (realistic count for app_firewall)
                        "x-ves-oneof-field-enforcement_mode_choice": '["blocking","monitoring"]',
                        "x-ves-oneof-field-detection_setting_choice": '["ai_risk_based_blocking","default_detection_settings","detection_settings"]',
                        "x-ves-oneof-field-blocking_page_choice": '["blocking_page","use_default_blocking_page"]',
                        "x-ves-oneof-field-bot_protection_choice": '["bot_protection_setting","default_bot_setting"]',
                        "x-ves-oneof-field-anonymization_setting": '["custom_anonymization","default_anonymization","disable_anonymization"]',
                        "x-ves-oneof-field-allowed_response_codes_choice": '["allow_all_response_codes","allowed_response_codes"]',
                        "properties": {
                            # Enforcement mode group
                            "blocking": {"type": "object"},
                            "monitoring": {"type": "object"},
                            # Detection setting group
                            "ai_risk_based_blocking": {"type": "object"},
                            "default_detection_settings": {"type": "object"},
                            "detection_settings": {"type": "object"},
                            # Blocking page group
                            "blocking_page": {"type": "object"},
                            "use_default_blocking_page": {"type": "object"},
                            # Bot protection group
                            "bot_protection_setting": {"type": "object"},
                            "default_bot_setting": {"type": "object"},
                            # Anonymization group
                            "custom_anonymization": {"type": "object"},
                            "default_anonymization": {"type": "object"},
                            "disable_anonymization": {"type": "object"},
                            # Response codes group
                            "allow_all_response_codes": {"type": "object"},
                            "allowed_response_codes": {"type": "object"},
                            # Non-OneOf field
                            "name": {"type": "string"},
                        },
                    },
                },
            },
        }

        result = enricher.enrich_spec(spec)
        props = result["components"]["schemas"]["appFirewallCreateSpecType"]["properties"]
        stats = enricher.get_stats()

        # Acceptance criteria: 6 OneOf groups found
        assert stats["oneof_groups_found"] == 6

        # Acceptance criteria: No cross-group contamination
        # blocking should only conflict with monitoring (same group)
        assert props["blocking"][X_F5XC_CONFLICTS_WITH] == ["monitoring"]
        assert "ai_risk_based_blocking" not in props["blocking"][X_F5XC_CONFLICTS_WITH]

        # detection_settings should only conflict with other detection options
        assert set(props["detection_settings"][X_F5XC_CONFLICTS_WITH]) == {
            "ai_risk_based_blocking",
            "default_detection_settings",
        }
        assert "blocking" not in props["detection_settings"][X_F5XC_CONFLICTS_WITH]

        # 3-variant group should have 2 conflicts each
        assert len(props["custom_anonymization"][X_F5XC_CONFLICTS_WITH]) == 2
        assert len(props["default_anonymization"][X_F5XC_CONFLICTS_WITH]) == 2
        assert len(props["disable_anonymization"][X_F5XC_CONFLICTS_WITH]) == 2

        # Non-OneOf field should be untouched
        assert X_F5XC_CONFLICTS_WITH not in props["name"]

    def test_accepts_large_spec_with_many_schemas(self, enricher):
        """Acceptance: Enricher handles specs with 100+ schemas efficiently.

        Real domain specs (like virtual.json) have 700+ schemas. The enricher
        must process these without errors and track accurate statistics.
        """
        # Generate a spec with 150 schemas, some with OneOf groups
        schemas = {}
        oneof_count = 0
        for i in range(150):
            if i % 3 == 0:  # Every 3rd schema has a OneOf group
                schemas[f"Schema{i}"] = {
                    "type": "object",
                    "x-ves-oneof-field-choice": f'["option_a_{i}","option_b_{i}"]',
                    "properties": {
                        f"option_a_{i}": {"type": "object"},
                        f"option_b_{i}": {"type": "object"},
                        "other_field": {"type": "string"},
                    },
                }
                oneof_count += 1
            else:
                schemas[f"Schema{i}"] = {
                    "type": "object",
                    "properties": {
                        "field1": {"type": "string"},
                        "field2": {"type": "integer"},
                    },
                }

        spec = {"components": {"schemas": schemas}}

        enricher.enrich_spec(spec)
        stats = enricher.get_stats()

        # Acceptance criteria: All schemas processed
        assert stats["schemas_processed"] == 150

        # Acceptance criteria: Correct number of OneOf schemas identified
        assert stats["schemas_with_oneof"] == oneof_count

        # Acceptance criteria: All OneOf groups found (50 schemas x 1 group each)
        assert stats["oneof_groups_found"] == oneof_count

        # Acceptance criteria: Correct number of properties enriched (50 schemas x 2 variants)
        assert stats["properties_enriched"] == oneof_count * 2

        # Acceptance criteria: No errors
        assert stats["error_count"] == 0

    def test_accepts_spec_and_produces_terraform_compatible_output(self, enricher):
        """Acceptance: Output format is compatible with Terraform provider consumption.

        The x-f5xc-conflicts-with extension must be an array of strings that
        Terraform providers can use for ConflictsWith validation rules.
        """
        spec = {
            "components": {
                "schemas": {
                    "originPoolCreateSpecType": {
                        "type": "object",
                        "x-ves-oneof-field-origin_server_type": '["public_ip","public_name","k8s_service","consul_service","private_ip","custom_endpoint"]',
                        "properties": {
                            "public_ip": {"type": "object"},
                            "public_name": {"type": "object"},
                            "k8s_service": {"type": "object"},
                            "consul_service": {"type": "object"},
                            "private_ip": {"type": "object"},
                            "custom_endpoint": {"type": "object"},
                        },
                    },
                },
            },
        }

        result = enricher.enrich_spec(spec)
        props = result["components"]["schemas"]["originPoolCreateSpecType"]["properties"]

        # Acceptance criteria for Terraform compatibility:
        for prop_name in [
            "public_ip",
            "public_name",
            "k8s_service",
            "consul_service",
            "private_ip",
            "custom_endpoint",
        ]:
            conflicts = props[prop_name].get(X_F5XC_CONFLICTS_WITH)

            # 1. Must be a list
            assert isinstance(conflicts, list), f"{prop_name} conflicts-with is not a list"

            # 2. Must contain strings only (Terraform resource attribute names)
            for item in conflicts:
                assert isinstance(item, str), f"{prop_name} contains non-string: {item}"

            # 3. Must not include self
            assert prop_name not in conflicts, f"{prop_name} conflicts with itself"

            # 4. Must list all OTHER variants (5 others in a 6-variant group)
            assert len(conflicts) == 5, f"{prop_name} should have 5 conflicts, got {len(conflicts)}"

            # 5. Must be sorted for deterministic output
            assert conflicts == sorted(conflicts), f"{prop_name} conflicts not sorted"
