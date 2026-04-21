# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Integration tests for enricher pipeline interactions.

Tests the critical interaction between OperationDescriptionEnricher (Step 14)
and OperationMetadataEnricher (Step 15) to ensure DRY-compliant, noun-first
descriptions flow through the pipeline correctly.

Issue: #408 - OperationMetadataEnricher overwrites DRY-compliant purpose descriptions
"""

from pathlib import Path
from typing import ClassVar

import pytest

from scripts.utils.constraint_enricher import ConstraintEnricher
from scripts.utils.operation_description_enricher import OperationDescriptionEnricher
from scripts.utils.operation_metadata_enricher import OperationMetadataEnricher
from scripts.utils.schema_fixer import SchemaFixer


def _get_resource_id(item):
    """Extract resource ID from tuple or pytest.param.

    Helper function for parametrize ids generation when mixing
    regular tuples with pytest.param objects.
    """
    if hasattr(item, "values"):
        # pytest.param object
        return item.values[0]
    return item[0]


@pytest.fixture
def description_enricher():
    """Create OperationDescriptionEnricher with default config."""
    return OperationDescriptionEnricher()


@pytest.fixture
def metadata_enricher():
    """Create OperationMetadataEnricher with default config."""
    return OperationMetadataEnricher()


@pytest.fixture
def sample_spec_with_http_loadbalancer():
    """Sample spec with http_loadbalancer operations (explicit config resource)."""
    return {
        "paths": {
            "/api/config/namespaces/{namespace}/http_loadbalancers": {
                "post": {
                    "operationId": "createHttpLoadBalancer",
                    "summary": "Create HTTP Load Balancer",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["metadata"],
                                    "properties": {
                                        "metadata": {"type": "object"},
                                    },
                                },
                            },
                        },
                    },
                },
                "get": {
                    "operationId": "listHttpLoadBalancers",
                    "summary": "List HTTP Load Balancers",
                },
            },
        },
    }


@pytest.fixture
def sample_spec_with_unknown_resource():
    """Sample spec with unknown resource (should use method fallback)."""
    return {
        "paths": {
            "/api/config/namespaces/{namespace}/custom_widgets": {
                "post": {
                    "operationId": "createCustomWidget",
                    "summary": "Create Custom Widget",
                },
            },
        },
    }


class TestPurposeFieldPreservation:
    """Test that purpose field from OperationDescriptionEnricher survives OperationMetadataEnricher."""

    def test_noun_first_purpose_preserved_for_explicit_resource(
        self,
        description_enricher,
        metadata_enricher,
        sample_spec_with_http_loadbalancer,
    ):
        """Test that noun-first purpose from explicit config is preserved."""
        spec = sample_spec_with_http_loadbalancer

        # Step 14: OperationDescriptionEnricher sets noun-first purpose
        spec = description_enricher.enrich_spec(spec)
        post_op = spec["paths"]["/api/config/namespaces/{namespace}/http_loadbalancers"]["post"]

        # If description enricher is enabled, check purpose was set
        if description_enricher.enabled:
            purpose_after_desc = post_op["x-f5xc-operation-metadata"]["purpose"]

            # Should be noun-first from config/operation_descriptions.yaml
            assert purpose_after_desc.startswith("HTTP")  # Noun-first
            assert not purpose_after_desc.lower().startswith("create")  # Not verb-first
            assert len(purpose_after_desc) <= 60  # Short tier

            # Step 15: OperationMetadataEnricher should PRESERVE the purpose
            spec = metadata_enricher.enrich_spec(spec)
            post_op = spec["paths"]["/api/config/namespaces/{namespace}/http_loadbalancers"]["post"]
            purpose_after_meta = post_op["x-f5xc-operation-metadata"]["purpose"]

            # Purpose should be IDENTICAL (preserved, not overwritten)
            assert purpose_after_meta == purpose_after_desc
            assert purpose_after_meta.startswith("HTTP")  # Still noun-first
            assert not purpose_after_meta.lower().startswith("create")  # Not verb-first

    def test_purpose_preserved_when_pre_existing(self, metadata_enricher):
        """Test that pre-existing purpose field is preserved, not overwritten."""
        spec = {
            "paths": {
                "/api/config/namespaces/{namespace}/http_loadbalancers": {
                    "post": {
                        "operationId": "createHttpLoadBalancer",
                        "x-f5xc-operation-metadata": {
                            "purpose": "HTTP/HTTPS load balancer with origin pools",
                        },
                    },
                },
            },
        }

        result = metadata_enricher.enrich_spec(spec)
        post_op = result["paths"]["/api/config/namespaces/{namespace}/http_loadbalancers"]["post"]
        metadata = post_op["x-f5xc-operation-metadata"]

        # Purpose should be preserved, not overwritten with "Create new http-loadbalancer"
        assert metadata["purpose"] == "HTTP/HTTPS load balancer with origin pools"
        assert not metadata["purpose"].startswith("Create")

    def test_verb_first_fallback_for_unknown_resource(
        self,
        description_enricher,
        metadata_enricher,
        sample_spec_with_unknown_resource,
    ):
        """Test that unknown resources use verb-first fallback."""
        spec = sample_spec_with_unknown_resource

        # Step 14: OperationDescriptionEnricher may not match this resource
        spec = description_enricher.enrich_spec(spec)

        # Step 15: OperationMetadataEnricher provides fallback
        spec = metadata_enricher.enrich_spec(spec)
        post_op = spec["paths"]["/api/config/namespaces/{namespace}/custom_widgets"]["post"]
        purpose = post_op["x-f5xc-operation-metadata"]["purpose"]

        # Should have SOME purpose (either from pattern or method fallback)
        assert purpose is not None
        assert len(purpose) > 0

    def test_fallback_generates_verb_first_when_no_existing_purpose(self, metadata_enricher):
        """Test that fallback generates verb-first description when no purpose exists."""
        spec = {
            "paths": {
                "/api/config/namespaces/{namespace}/unknown_things": {
                    "post": {
                        "operationId": "createUnknownThing",
                    },
                },
            },
        }

        result = metadata_enricher.enrich_spec(spec)
        post_op = result["paths"]["/api/config/namespaces/{namespace}/unknown_things"]["post"]
        purpose = post_op["x-f5xc-operation-metadata"]["purpose"]

        # Should generate verb-first fallback
        assert purpose == "Create new unknown-thing"


class TestDRYComplianceAcrossEnrichers:
    """Test DRY compliance is maintained through the enricher pipeline."""

    @pytest.mark.parametrize(
        ("resource_type", "expected_prefix"),
        [
            ("http_loadbalancer", "HTTP"),
            ("origin_pool", "Backend"),
        ],
    )
    def test_explicit_resources_have_noun_first_descriptions(
        self,
        description_enricher,
        metadata_enricher,
        resource_type,
        expected_prefix,
    ):
        """Test explicit resources maintain noun-first descriptions through pipeline."""
        # Skip if description enricher is disabled
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        spec = {
            "paths": {
                f"/api/config/namespaces/{{namespace}}/{resource_type}s": {
                    "post": {
                        "operationId": f"create{resource_type.title().replace('_', '')}",
                        "summary": f"Create {resource_type}",
                    },
                },
            },
        }

        # Run both enrichers in sequence
        spec = description_enricher.enrich_spec(spec)
        spec = metadata_enricher.enrich_spec(spec)

        post_op = spec["paths"][f"/api/config/namespaces/{{namespace}}/{resource_type}s"]["post"]
        purpose = post_op["x-f5xc-operation-metadata"]["purpose"]

        # Should be noun-first, not verb-first
        assert purpose.startswith(expected_prefix), (
            f"Expected {resource_type} to start with '{expected_prefix}', got: {purpose}"
        )
        assert not purpose.lower().startswith("create"), (
            f"Purpose should be noun-first, not verb-first: {purpose}"
        )


class TestAllExplicitResources:
    """Comprehensive test coverage for ALL 10 explicit resources from operation_descriptions.yaml.

    This test class programmatically verifies that every resource configured in
    config/operation_descriptions.yaml receives the correct noun-first description
    through the enrichment pipeline.
    """

    # Complete inventory of all 10 explicit resources from config/operation_descriptions.yaml
    # Test data format: resource_type, expected_short_description, api_path_pattern
    # NOTE: EXPLICIT_RESOURCES_FULL_PIPELINE includes xfail for namespace due to path extraction limitation
    # EXPLICIT_RESOURCES_PRESERVATION tests don't need xfail since they don't use path extraction
    EXPLICIT_RESOURCES_FULL_PIPELINE: ClassVar[list] = [
        (
            "http_loadbalancer",
            "HTTP/HTTPS load balancer with origin pools and routing rules",
            "/api/config/namespaces/{namespace}/http_loadbalancers",
        ),
        (
            "origin_pool",
            "Backend server pool for load balancing and failover",
            "/api/config/namespaces/{namespace}/origin_pools",
        ),
        (
            "app_firewall",
            "Web application firewall for threat protection",
            "/api/config/namespaces/{namespace}/app_firewalls",
        ),
        (
            "virtual_host",
            "DNS name mapping to routes and load balancers",
            "/api/config/namespaces/{namespace}/virtual_hosts",
        ),
        (
            "healthcheck",
            "Endpoint health monitoring configuration",
            "/api/config/namespaces/{namespace}/healthchecks",
        ),
        (
            "tcp_loadbalancer",
            "Layer 4 TCP load balancer for non-HTTP traffic",
            "/api/config/namespaces/{namespace}/tcp_loadbalancers",
        ),
        (
            "certificate",
            "TLS/SSL certificate for secure connections",
            "/api/config/namespaces/{namespace}/certificates",
        ),
        # NOTE: "namespace" resource has a path extraction limitation.
        # All common API paths for namespace (/api/system/namespaces, /api/web/namespaces)
        # contain only skip-list segments (api, system, web, namespaces, config).
        # This is tracked as a separate issue from Issue #408.
        # The test for namespace is marked as xfail because full pipeline test uses path extraction.
        pytest.param(
            "namespace",
            "Logical resource grouping and multi-tenancy boundary",
            "/api/system/namespaces",
            marks=pytest.mark.xfail(
                reason="Path extraction limitation: 'namespace' cannot be extracted from standard API paths",
                strict=True,
            ),
        ),
        (
            "route",
            "HTTP routing rule for path-based traffic distribution",
            "/api/config/namespaces/{namespace}/routes",
        ),
        (
            "waf_policy",
            "Security policy for application protection",
            "/api/config/namespaces/{namespace}/waf_policys",
        ),
    ]

    # Preservation tests don't use path extraction, so no xfail needed for namespace
    EXPLICIT_RESOURCES_PRESERVATION: ClassVar[list] = [
        (
            "http_loadbalancer",
            "HTTP/HTTPS load balancer with origin pools and routing rules",
            "/api/config/namespaces/{namespace}/http_loadbalancers",
        ),
        (
            "origin_pool",
            "Backend server pool for load balancing and failover",
            "/api/config/namespaces/{namespace}/origin_pools",
        ),
        (
            "app_firewall",
            "Web application firewall for threat protection",
            "/api/config/namespaces/{namespace}/app_firewalls",
        ),
        (
            "virtual_host",
            "DNS name mapping to routes and load balancers",
            "/api/config/namespaces/{namespace}/virtual_hosts",
        ),
        (
            "healthcheck",
            "Endpoint health monitoring configuration",
            "/api/config/namespaces/{namespace}/healthchecks",
        ),
        (
            "tcp_loadbalancer",
            "Layer 4 TCP load balancer for non-HTTP traffic",
            "/api/config/namespaces/{namespace}/tcp_loadbalancers",
        ),
        (
            "certificate",
            "TLS/SSL certificate for secure connections",
            "/api/config/namespaces/{namespace}/certificates",
        ),
        (
            "namespace",
            "Logical resource grouping and multi-tenancy boundary",
            "/api/system/namespaces",
        ),
        (
            "route",
            "HTTP routing rule for path-based traffic distribution",
            "/api/config/namespaces/{namespace}/routes",
        ),
        (
            "waf_policy",
            "Security policy for application protection",
            "/api/config/namespaces/{namespace}/waf_policys",
        ),
    ]

    @pytest.mark.parametrize(
        ("resource_type", "expected_description", "api_path"),
        EXPLICIT_RESOURCES_FULL_PIPELINE,
        ids=[_get_resource_id(r) for r in EXPLICIT_RESOURCES_FULL_PIPELINE],
    )
    def test_explicit_resource_description_preserved(
        self,
        description_enricher,
        metadata_enricher,
        resource_type,
        expected_description,
        api_path,
    ):
        """Test that each explicit resource gets its configured description preserved.

        This test verifies:
        1. OperationDescriptionEnricher sets the correct noun-first description
        2. OperationMetadataEnricher preserves it (doesn't overwrite with verb-first)
        3. The final purpose matches exactly what's configured in operation_descriptions.yaml
        """
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        spec = {
            "paths": {
                api_path: {
                    "post": {
                        "operationId": f"create{resource_type.title().replace('_', '')}",
                        "summary": f"Create {resource_type}",
                    },
                },
            },
        }

        # Step 14: OperationDescriptionEnricher
        spec = description_enricher.enrich_spec(spec)

        # Verify description was applied
        post_op = spec["paths"][api_path]["post"]
        assert "x-f5xc-operation-metadata" in post_op, (
            f"x-f5xc-operation-metadata not found for {resource_type}"
        )
        purpose_after_step14 = post_op["x-f5xc-operation-metadata"].get("purpose")
        assert purpose_after_step14 is not None, (
            f"Purpose not set for {resource_type} after OperationDescriptionEnricher"
        )

        # Step 15: OperationMetadataEnricher
        spec = metadata_enricher.enrich_spec(spec)

        # Verify purpose was PRESERVED (not overwritten)
        post_op = spec["paths"][api_path]["post"]
        purpose_after_step15 = post_op["x-f5xc-operation-metadata"]["purpose"]

        # The purpose should match the configured description EXACTLY
        assert purpose_after_step15 == expected_description, (
            f"Resource {resource_type}: Expected '{expected_description}', "
            f"got '{purpose_after_step15}'"
        )

        # Verify it's noun-first (not verb-first)
        assert not purpose_after_step15.lower().startswith("create"), (
            f"Resource {resource_type}: Purpose should be noun-first, "
            f"not verb-first: {purpose_after_step15}"
        )
        assert not purpose_after_step15.lower().startswith("list"), (
            f"Resource {resource_type}: Purpose should be noun-first, "
            f"not verb-first: {purpose_after_step15}"
        )
        assert not purpose_after_step15.lower().startswith("delete"), (
            f"Resource {resource_type}: Purpose should be noun-first, "
            f"not verb-first: {purpose_after_step15}"
        )

    @pytest.mark.parametrize(
        ("resource_type", "expected_description", "api_path"),
        EXPLICIT_RESOURCES_PRESERVATION,
        ids=[f"{r[0]}_metadata_only" for r in EXPLICIT_RESOURCES_PRESERVATION],
    )
    def test_pre_existing_purpose_preserved_by_metadata_enricher(
        self,
        metadata_enricher,
        resource_type,
        expected_description,
        api_path,
    ):
        """Test that OperationMetadataEnricher preserves pre-existing purpose.

        This simulates the scenario where OperationDescriptionEnricher has already
        set the purpose, and we verify OperationMetadataEnricher doesn't overwrite it.
        """
        spec = {
            "paths": {
                api_path: {
                    "post": {
                        "operationId": f"create{resource_type.title().replace('_', '')}",
                        "x-f5xc-operation-metadata": {
                            "purpose": expected_description,
                        },
                    },
                },
            },
        }

        # Run metadata enricher (should preserve purpose)
        result = metadata_enricher.enrich_spec(spec)
        post_op = result["paths"][api_path]["post"]
        actual_purpose = post_op["x-f5xc-operation-metadata"]["purpose"]

        # Purpose should be IDENTICAL (preserved, not overwritten)
        assert actual_purpose == expected_description, (
            f"Resource {resource_type}: Purpose was overwritten! "
            f"Expected '{expected_description}', got '{actual_purpose}'"
        )

    def test_all_explicit_resources_count(self, description_enricher):
        """Verify test coverage matches config file resource count.

        This test ensures we're testing ALL resources from operation_descriptions.yaml,
        not just a subset. If new resources are added to config, this test will fail
        until the EXPLICIT_RESOURCES list is updated.
        """
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        # Get configured resources from enricher (use the resources attribute)
        configured_resources = list(description_enricher.resources.keys())

        # Get tested resources (use PRESERVATION list which has plain tuples)
        tested_resources = [r[0] for r in self.EXPLICIT_RESOURCES_PRESERVATION]

        # Verify counts match
        assert len(tested_resources) == len(configured_resources), (
            f"Test coverage mismatch! Config has {len(configured_resources)} resources, "
            f"but tests cover {len(tested_resources)}. "
            f"Missing: {set(configured_resources) - set(tested_resources)}"
        )

        # Verify all configured resources are tested
        missing_tests = set(configured_resources) - set(tested_resources)
        assert not missing_tests, f"Resources in config but not in tests: {missing_tests}"

        # Verify no extra tests for non-existent resources
        extra_tests = set(tested_resources) - set(configured_resources)
        assert not extra_tests, f"Resources in tests but not in config: {extra_tests}"


class TestAllPatternMatchers:
    """Comprehensive test coverage for ALL 8 pattern matchers from operation_descriptions.yaml.

    Pattern matchers provide auto-generated descriptions for resources that don't have
    explicit configurations. These tests verify the regex patterns match correctly.
    """

    # Complete inventory of all 8 patterns from config/operation_descriptions.yaml
    # Test data format: pattern_name, resource_example, expected_short_description
    PATTERN_MATCHERS: ClassVar[list] = [
        # Pattern 1: .*loadbalancer.*
        (
            "loadbalancer_pattern",
            "custom_loadbalancer",
            "Load balancing configuration for traffic distribution",
        ),
        (
            "loadbalancer_pattern_udp",
            "udp_loadbalancer",
            "Load balancing configuration for traffic distribution",
        ),
        # Pattern 2: .*pool.*
        (
            "pool_pattern",
            "connection_pool",
            "Backend server pool configuration",
        ),
        (
            "pool_pattern_server",
            "server_pool",
            "Backend server pool configuration",
        ),
        # Pattern 3: .*policy.* (generic)
        (
            "policy_pattern",
            "rate_limit_policy",
            "Configuration policy for resource behavior",
        ),
        (
            "policy_pattern_access",
            "access_policy",
            "Configuration policy for resource behavior",
        ),
        # Pattern 4: .*firewall.*|.*waf.*
        (
            "firewall_pattern",
            "network_firewall",
            "Security policy for threat protection",
        ),
        (
            "waf_pattern",
            "custom_waf",
            "Security policy for threat protection",
        ),
        # Pattern 5: .*route.*|.*routing.*
        (
            "route_pattern",
            "service_route",
            "Traffic routing configuration",
        ),
        (
            "routing_pattern",
            "dynamic_routing",
            "Traffic routing configuration",
        ),
        # Pattern 6: .*health.*|.*monitor.*
        (
            "health_pattern",
            "custom_health",
            "Health monitoring configuration",
        ),
        (
            "monitor_pattern",
            "endpoint_monitor",
            "Health monitoring configuration",
        ),
        # Pattern 7: .*certificate.*|.*cert.*|.*tls.*|.*ssl.*
        (
            "certificate_pattern",
            "custom_certificate",
            "TLS/SSL certificate management",
        ),
        (
            "cert_pattern",
            "client_cert",
            "TLS/SSL certificate management",
        ),
        (
            "tls_pattern",
            "tls_config",
            "TLS/SSL certificate management",
        ),
        (
            "ssl_pattern",
            "ssl_profile",
            "TLS/SSL certificate management",
        ),
        # Pattern 8: .*namespace.*|.*tenant.*
        (
            "namespace_pattern",
            "custom_namespace",
            "Resource isolation and multi-tenancy boundary",
        ),
        (
            "tenant_pattern",
            "multi_tenant",
            "Resource isolation and multi-tenancy boundary",
        ),
    ]

    @pytest.mark.parametrize(
        ("pattern_name", "resource_type", "expected_description"),
        PATTERN_MATCHERS,
        ids=[p[0] for p in PATTERN_MATCHERS],
    )
    def test_pattern_matcher_applies_correct_description(
        self,
        description_enricher,
        metadata_enricher,
        pattern_name,
        resource_type,
        expected_description,
    ):
        """Test that pattern matchers generate correct descriptions for matching resources."""
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        # Create API path that will extract to the test resource type
        api_path = f"/api/config/namespaces/{{namespace}}/{resource_type}s"

        spec = {
            "paths": {
                api_path: {
                    "post": {
                        "operationId": f"create{resource_type.title().replace('_', '')}",
                        "summary": f"Create {resource_type}",
                    },
                },
            },
        }

        # Run description enricher
        spec = description_enricher.enrich_spec(spec)

        # Run metadata enricher (should preserve purpose)
        spec = metadata_enricher.enrich_spec(spec)

        post_op = spec["paths"][api_path]["post"]
        purpose = post_op["x-f5xc-operation-metadata"]["purpose"]

        # Verify pattern matched and description was applied
        assert purpose == expected_description, (
            f"Pattern {pattern_name}: Expected '{expected_description}', got '{purpose}'"
        )

    def test_all_patterns_count(self, description_enricher):
        """Verify test coverage includes all pattern variations.

        This test ensures we have comprehensive pattern coverage.
        """
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        # Get configured patterns (use the patterns attribute)
        configured_patterns = description_enricher.patterns

        # Verify we have tests for all 8 patterns
        assert len(configured_patterns) == 8, (
            f"Expected 8 patterns in config, found {len(configured_patterns)}"
        )


class TestAllMethodFallbacks:
    """Comprehensive test coverage for ALL 5 HTTP method fallbacks.

    When no explicit resource or pattern matches, the method fallback provides
    verb-first descriptions based on the HTTP method.
    """

    # Complete inventory of all 5 method fallbacks from config
    # Test data format: method, expected_short_description
    METHOD_FALLBACKS: ClassVar[list] = [
        ("post", "Create new"),
        ("get", "List all"),
        ("put", "Replace existing"),
        ("patch", "Update"),
        ("delete", "Delete"),
    ]

    @pytest.mark.parametrize(
        ("method", "expected_pattern"),
        METHOD_FALLBACKS,
        ids=[f"method_{m[0].upper()}" for m in METHOD_FALLBACKS],
    )
    def test_method_fallback_generates_verb_first_description(
        self,
        metadata_enricher,
        method,
        expected_pattern,
    ):
        """Test fallback generates correct verb-first pattern for HTTP methods."""
        # Use a resource that won't match any pattern
        api_path = "/api/config/namespaces/{namespace}/xyzzy_things"

        spec = {
            "paths": {
                api_path: {
                    method: {
                        "operationId": f"{method}XyzzyThing",
                    },
                },
            },
        }

        result = metadata_enricher.enrich_spec(spec)
        op = result["paths"][api_path][method]
        purpose = op["x-f5xc-operation-metadata"]["purpose"]

        # Verify fallback pattern was used
        assert expected_pattern in purpose, (
            f"Method {method.upper()}: Expected '{expected_pattern}' in purpose, got '{purpose}'"
        )

    def test_method_fallback_only_when_no_pattern_match(
        self,
        description_enricher,
        metadata_enricher,
    ):
        """Test that method fallback is only used when no pattern matches."""
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        # This resource should NOT match any pattern
        api_path = "/api/config/namespaces/{namespace}/unknown_gadgets"

        spec = {
            "paths": {
                api_path: {
                    "post": {
                        "operationId": "createUnknownGadget",
                    },
                },
            },
        }

        # Run both enrichers
        spec = description_enricher.enrich_spec(spec)
        spec = metadata_enricher.enrich_spec(spec)

        post_op = spec["paths"][api_path]["post"]
        purpose = post_op["x-f5xc-operation-metadata"]["purpose"]

        # When OperationDescriptionEnricher runs with no pattern match, it uses method_fallbacks
        # which returns "Resource creation operation" (noun-first from config)
        # This is then preserved by OperationMetadataEnricher
        assert purpose == "Resource creation operation", (
            f"Expected method fallback from config for unknown resource, got: {purpose}"
        )


class TestEndToEndPipelineCoverage:
    """End-to-end tests verifying the complete enrichment pipeline.

    These tests simulate real-world scenarios with multiple resources
    and verify the entire pipeline works correctly.
    """

    def test_mixed_spec_with_explicit_pattern_and_fallback_resources(
        self,
        description_enricher,
        metadata_enricher,
    ):
        """Test spec containing explicit, pattern-matched, and fallback resources."""
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        spec = {
            "paths": {
                # Explicit resource (http_loadbalancer)
                "/api/config/namespaces/{namespace}/http_loadbalancers": {
                    "post": {"operationId": "createHttpLoadBalancer"},
                },
                # Pattern-matched resource (custom_pool matches .*pool.*)
                "/api/config/namespaces/{namespace}/custom_pools": {
                    "post": {"operationId": "createCustomPool"},
                },
                # Fallback resource (no pattern match)
                "/api/config/namespaces/{namespace}/unknown_widgets": {
                    "post": {"operationId": "createUnknownWidget"},
                },
            },
        }

        # Run full pipeline
        spec = description_enricher.enrich_spec(spec)
        spec = metadata_enricher.enrich_spec(spec)

        # Verify explicit resource has noun-first description
        http_lb_purpose = spec["paths"]["/api/config/namespaces/{namespace}/http_loadbalancers"][
            "post"
        ]["x-f5xc-operation-metadata"]["purpose"]
        assert http_lb_purpose == "HTTP/HTTPS load balancer with origin pools and routing rules"
        assert not http_lb_purpose.lower().startswith("create")

        # Verify pattern-matched resource has pattern description
        pool_purpose = spec["paths"]["/api/config/namespaces/{namespace}/custom_pools"]["post"][
            "x-f5xc-operation-metadata"
        ]["purpose"]
        assert pool_purpose == "Backend server pool configuration"
        assert not pool_purpose.lower().startswith("create")

        # Verify fallback resource has method-fallback description from config
        # When OperationDescriptionEnricher runs first, it applies "Resource creation operation"
        # from method_fallbacks in config, which is then preserved by OperationMetadataEnricher
        widget_purpose = spec["paths"]["/api/config/namespaces/{namespace}/unknown_widgets"][
            "post"
        ]["x-f5xc-operation-metadata"]["purpose"]
        assert widget_purpose == "Resource creation operation", (
            f"Expected method fallback from config, got: {widget_purpose}"
        )

    def test_all_http_methods_on_single_resource(
        self,
        description_enricher,
        metadata_enricher,
    ):
        """Test all HTTP methods on a single resource path."""
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        spec = {
            "paths": {
                "/api/config/namespaces/{namespace}/http_loadbalancers": {
                    "get": {"operationId": "listHttpLoadBalancers"},
                    "post": {"operationId": "createHttpLoadBalancer"},
                },
                "/api/config/namespaces/{namespace}/http_loadbalancers/{name}": {
                    "get": {"operationId": "getHttpLoadBalancer"},
                    "put": {"operationId": "replaceHttpLoadBalancer"},
                    "delete": {"operationId": "deleteHttpLoadBalancer"},
                },
            },
        }

        # Run full pipeline
        spec = description_enricher.enrich_spec(spec)
        spec = metadata_enricher.enrich_spec(spec)

        # All operations should have noun-first description (same resource)
        expected_description = "HTTP/HTTPS load balancer with origin pools and routing rules"

        for path in spec["paths"]:
            for method in spec["paths"][path]:
                if method in ["get", "post", "put", "delete"]:
                    purpose = spec["paths"][path][method]["x-f5xc-operation-metadata"]["purpose"]
                    assert purpose == expected_description, (
                        f"Path {path} method {method}: Expected '{expected_description}', "
                        f"got '{purpose}'"
                    )

    def test_statistics_track_all_match_types(
        self,
        description_enricher,
        metadata_enricher,
    ):
        """Test that statistics correctly track explicit, pattern, and fallback matches."""
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        spec = {
            "paths": {
                "/api/config/namespaces/{namespace}/http_loadbalancers": {
                    "post": {"operationId": "createHttpLoadBalancer"},
                },
                "/api/config/namespaces/{namespace}/custom_pools": {
                    "post": {"operationId": "createCustomPool"},
                },
                "/api/config/namespaces/{namespace}/unknown_widgets": {
                    "post": {"operationId": "createUnknownWidget"},
                },
            },
        }

        description_enricher.reset_stats()
        spec = description_enricher.enrich_spec(spec)
        stats = description_enricher.get_stats()

        # Verify statistics
        assert stats["operations_processed"] == 3
        assert stats["exact_matches"] >= 1  # http_loadbalancer
        assert stats["pattern_matches"] >= 1  # custom_pool
        # method_fallbacks tracked separately


class TestComprehensiveMetadataPreservation:
    """Test that comprehensive metadata includes all fields after both enrichers."""

    def test_all_metadata_fields_present(
        self,
        description_enricher,
        metadata_enricher,
        sample_spec_with_http_loadbalancer,
    ):
        """Test comprehensive metadata has all expected fields."""
        spec = sample_spec_with_http_loadbalancer

        # Run both enrichers
        spec = description_enricher.enrich_spec(spec)
        spec = metadata_enricher.enrich_spec(spec)

        post_op = spec["paths"]["/api/config/namespaces/{namespace}/http_loadbalancers"]["post"]
        metadata = post_op["x-f5xc-operation-metadata"]

        # Verify all comprehensive metadata fields
        assert "purpose" in metadata
        assert "required_fields" in metadata
        assert "optional_fields" in metadata
        assert "field_docs" in metadata
        assert "conditions" in metadata
        assert "side_effects" in metadata
        assert "danger_level" in metadata
        assert "confirmation_required" in metadata
        assert "common_errors" in metadata
        assert "performance_impact" in metadata

    def test_metadata_structure_after_pipeline(self, metadata_enricher):
        """Test metadata structure is correct after enrichment."""
        spec = {
            "paths": {
                "/api/config/namespaces/{namespace}/test_resources": {
                    "post": {
                        "operationId": "createTestResource",
                        "x-f5xc-operation-metadata": {
                            "purpose": "Test resource for validation",
                        },
                    },
                    "delete": {
                        "operationId": "deleteTestResource",
                    },
                },
            },
        }

        result = metadata_enricher.enrich_spec(spec)

        # POST should preserve purpose
        post_meta = result["paths"]["/api/config/namespaces/{namespace}/test_resources"]["post"][
            "x-f5xc-operation-metadata"
        ]
        assert post_meta["purpose"] == "Test resource for validation"
        assert post_meta["danger_level"] == "medium"  # POST default

        # DELETE should have fallback purpose
        del_meta = result["paths"]["/api/config/namespaces/{namespace}/test_resources"]["delete"][
            "x-f5xc-operation-metadata"
        ]
        assert del_meta["purpose"] == "Delete test-resource"
        assert del_meta["danger_level"] == "high"  # DELETE default


class TestEnricherPipelineStatistics:
    """Test statistics are correctly tracked through the pipeline."""

    def test_description_enricher_stats_tracked(
        self,
        description_enricher,
        sample_spec_with_http_loadbalancer,
    ):
        """Test OperationDescriptionEnricher tracks statistics."""
        if not description_enricher.enabled:
            pytest.skip("OperationDescriptionEnricher is disabled")

        description_enricher.reset_stats()
        description_enricher.enrich_spec(sample_spec_with_http_loadbalancer)
        stats = description_enricher.get_stats()

        assert stats["operations_processed"] >= 1
        assert stats["descriptions_applied"] >= 1
        assert stats["exact_matches"] >= 1  # http_loadbalancer is explicit config

    def test_metadata_enricher_stats_tracked(
        self,
        metadata_enricher,
        sample_spec_with_http_loadbalancer,
    ):
        """Test OperationMetadataEnricher tracks statistics."""
        metadata_enricher.stats = type(metadata_enricher.stats)()  # Reset stats
        metadata_enricher.enrich_spec(sample_spec_with_http_loadbalancer)
        stats = metadata_enricher.get_stats()

        assert stats["operations_enriched"] >= 1


class TestHTTPMethodFallbacks:
    """Test HTTP method fallbacks for verb-first descriptions."""

    @pytest.mark.parametrize(
        ("method", "expected_pattern"),
        [
            ("get", "List all"),
            ("post", "Create new"),
            ("put", "Replace existing"),
            ("patch", "Update"),
            ("delete", "Delete"),
        ],
    )
    def test_method_fallback_patterns(self, metadata_enricher, method, expected_pattern):
        """Test fallback generates correct verb-first pattern for HTTP methods."""
        spec = {
            "paths": {
                "/api/config/namespaces/{namespace}/test_items": {
                    method: {
                        "operationId": f"{method}TestItem",
                    },
                },
            },
        }

        result = metadata_enricher.enrich_spec(spec)
        op = result["paths"]["/api/config/namespaces/{namespace}/test_items"][method]
        purpose = op["x-f5xc-operation-metadata"]["purpose"]

        assert expected_pattern in purpose


class TestEdgeCases:
    """Test edge cases in enricher pipeline."""

    def test_empty_spec(self, description_enricher, metadata_enricher):
        """Test handling of empty spec."""
        spec = {}

        result = description_enricher.enrich_spec(spec)
        result = metadata_enricher.enrich_spec(result)

        assert result == {}

    def test_spec_without_paths(self, description_enricher, metadata_enricher):
        """Test handling of spec without paths."""
        spec = {"info": {"title": "Test API"}}

        result = description_enricher.enrich_spec(spec)
        result = metadata_enricher.enrich_spec(result)

        assert result == {"info": {"title": "Test API"}}

    def test_preserves_other_metadata_fields(self, metadata_enricher):
        """Test that other metadata fields are preserved when purpose exists."""
        spec = {
            "paths": {
                "/api/config/namespaces/{namespace}/test_resources": {
                    "post": {
                        "operationId": "createTestResource",
                        "x-f5xc-operation-metadata": {
                            "purpose": "Pre-existing purpose",
                            "custom_field": "custom_value",
                        },
                    },
                },
            },
        }

        result = metadata_enricher.enrich_spec(spec)
        metadata = result["paths"]["/api/config/namespaces/{namespace}/test_resources"]["post"][
            "x-f5xc-operation-metadata"
        ]

        # Purpose should be preserved
        assert metadata["purpose"] == "Pre-existing purpose"
        # Comprehensive metadata should be added (overwrites entire object but preserves purpose)
        assert "danger_level" in metadata
        assert "required_fields" in metadata


class TestConstraintEnricherSchemaFixerIsolation:
    """End-to-end regression: inject_max_items must run AFTER ConstraintEnricher.

    Codex P1 (HANDOFF.md §1.1) was the symmetric failure: running
    ``SchemaFixer.inject_max_items`` BEFORE ``ConstraintEnricher``
    caused the synthetic 65535 schema-level ``maxItems`` to leak into
    ``x-f5xc-constraints.maxItems``, shadowing the pattern-inferred
    bounds (100 for ``tags``, 50 for ``origins``, etc.). The
    production ordering is locked in ``scripts/enrich.py::save_spec``
    and ``scripts/pipeline.py::save_spec`` — this test exercises the
    full sequence against real ``config/constraint_patterns.yaml``
    and asserts the isolation invariant.
    """

    @pytest.fixture
    def constraint_enricher(self) -> ConstraintEnricher:
        config_path = Path(__file__).parent.parent / "config" / "constraint_patterns.yaml"
        return ConstraintEnricher(config_path=config_path)

    def test_tags_preserves_pattern_inferred_max_items(
        self,
        constraint_enricher: ConstraintEnricher,
    ) -> None:
        """A ``tags`` array gets x-f5xc-constraints.maxItems=100 (pattern-inferred)
        and schema.maxItems=65535 (Checkov compliance), with no crossover.
        """
        spec = {
            "components": {
                "schemas": {
                    "Resource": {
                        "type": "object",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "unknown_list": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }

        spec = constraint_enricher.enrich_spec(spec)
        spec = SchemaFixer().inject_max_items(spec)

        tags = spec["components"]["schemas"]["Resource"]["properties"]["tags"]
        unknown = spec["components"]["schemas"]["Resource"]["properties"]["unknown_list"]

        # tags received a pattern-inferred constraint (100) and the
        # Checkov-compliance schema bound (65535). They must be
        # independent values — no leakage in either direction.
        assert tags["maxItems"] == 65535
        assert tags["x-f5xc-constraints"]["maxItems"] == 100

        # unknown_list matches no constraint pattern, so no
        # x-f5xc-constraints is added, but the schema bound is still
        # stamped so Checkov CKV_OPENAPI_21 passes.
        assert unknown["maxItems"] == 65535
        assert "x-f5xc-constraints" not in unknown or (
            "maxItems" not in unknown.get("x-f5xc-constraints", {})
        )

    def test_ordering_is_not_commutative(
        self,
        constraint_enricher: ConstraintEnricher,
    ) -> None:
        """Reverse ordering is the bug: running inject_max_items first
        poisons x-f5xc-constraints with 65535. This documents the
        failure mode so future refactors cannot regress silently.
        """
        spec = {
            "components": {
                "schemas": {
                    "Resource": {
                        "type": "object",
                        "properties": {
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
        }

        # WRONG order
        spec = SchemaFixer().inject_max_items(spec)
        spec = constraint_enricher.enrich_spec(spec)

        tags = spec["components"]["schemas"]["Resource"]["properties"]["tags"]
        # EXISTING priority wins over INFERRED in ConstraintReconciler, so
        # the 65535 now shadows the pattern-inferred 100. Assert the
        # poisoned state to document the failure mode.
        assert tags["maxItems"] == 65535
        assert tags["x-f5xc-constraints"]["maxItems"] == 65535


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
