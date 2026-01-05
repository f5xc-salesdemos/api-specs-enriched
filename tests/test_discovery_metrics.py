"""Unit tests for discovery metrics modules.

Tests rate limit discoverer and error catalog builder functionality.
"""

import pytest

from scripts.discovery.error_catalog_builder import (
    BuilderStats,
    EndpointErrors,
    ErrorCatalog,
    ErrorCatalogBuilder,
    ErrorCatalogConfig,
    ErrorEntry,
)
from scripts.discovery.rate_limit_discoverer import (
    DiscovererStats,
    ProbeResult,
    RateLimitDiscoverer,
    RateLimitDiscoveryConfig,
    RateLimitInfo,
    parse_rate_limit_headers,
)


class TestRateLimitDiscoveryConfig:
    """Test RateLimitDiscoveryConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = RateLimitDiscoveryConfig()
        assert config.enabled is False  # Opt-in only
        assert config.max_probe_rate == 20
        assert config.probe_delay_seconds == 0.1
        assert config.cooldown_seconds == 60.0
        assert config.safe_mode is True

    def test_custom_values(self):
        """Test custom configuration values."""
        config = RateLimitDiscoveryConfig(
            enabled=True,
            max_probe_rate=50,
            probe_delay_seconds=0.05,
            cooldown_seconds=30.0,
            safe_mode=False,
        )
        assert config.enabled is True
        assert config.max_probe_rate == 50
        assert config.probe_delay_seconds == 0.05
        assert config.safe_mode is False


class TestRateLimitInfo:
    """Test RateLimitInfo dataclass."""

    def test_default_values(self):
        """Test default info values."""
        info = RateLimitInfo()
        assert info.endpoint == ""
        assert info.method == "GET"
        assert info.requests_per_minute is None
        assert info.confidence == "unknown"

    def test_to_dict(self):
        """Test to_dict method."""
        info = RateLimitInfo(
            endpoint="/api/test",
            method="POST",
            requests_per_minute=100,
            burst_limit=10,
            retry_after_header=True,
            retry_after_value=60.0,
            discovered_at="2024-01-01T00:00:00Z",
            confidence="high",
        )
        result = info.to_dict()

        assert result["endpoint"] == "/api/test"
        assert result["method"] == "POST"
        assert result["requests_per_minute"] == 100
        assert result["burst_limit"] == 10
        assert result["retry_after_header"] is True
        assert result["confidence"] == "high"

    def test_to_dict_optional_fields(self):
        """Test to_dict omits None values."""
        info = RateLimitInfo(
            endpoint="/api/test",
            method="GET",
            discovered_at="2024-01-01T00:00:00Z",
            confidence="low",
        )
        result = info.to_dict()

        assert "requests_per_minute" not in result
        assert "burst_limit" not in result
        assert "retry_after_header" not in result

    def test_to_extension(self):
        """Test to_extension method for OpenAPI output."""
        info = RateLimitInfo(
            endpoint="/api/test",
            method="GET",
            requests_per_minute=100,
            requests_per_second=1.67,
            burst_limit=10,
            retry_after_header=True,
            discovered_at="2024-01-01T00:00:00Z",
        )
        result = info.to_extension()

        assert result["requests_per_minute"] == 100
        assert result["burst_limit"] == 10
        assert result["retry_after_header"] is True
        assert result["discovered_at"] == "2024-01-01T00:00:00Z"
        # Should not include internal fields
        assert "endpoint" not in result
        assert "method" not in result
        assert "confidence" not in result


class TestDiscovererStats:
    """Test DiscovererStats dataclass."""

    def test_default_values(self):
        """Test default stats values."""
        stats = DiscovererStats()
        assert stats.endpoints_probed == 0
        assert stats.requests_made == 0
        assert stats.rate_limits_hit == 0
        assert stats.limits_discovered == 0
        assert stats.skipped_disabled == 0

    def test_to_dict(self):
        """Test to_dict method."""
        stats = DiscovererStats(
            endpoints_probed=5,
            requests_made=100,
            rate_limits_hit=3,
            limits_discovered=2,
            skipped_disabled=1,
        )
        result = stats.to_dict()

        assert result["endpoints_probed"] == 5
        assert result["requests_made"] == 100
        assert result["rate_limits_hit"] == 3


class TestProbeResult:
    """Test ProbeResult dataclass."""

    def test_basic_result(self):
        """Test basic probe result."""
        result = ProbeResult(
            status_code=200,
            response_time_ms=50.0,
        )
        assert result.status_code == 200
        assert result.response_time_ms == 50.0
        assert result.retry_after is None

    def test_rate_limit_result(self):
        """Test probe result with rate limit info."""
        result = ProbeResult(
            status_code=429,
            response_time_ms=10.0,
            retry_after=60.0,
            rate_limit_remaining=0,
            rate_limit_limit=100,
        )
        assert result.status_code == 429
        assert result.retry_after == 60.0
        assert result.rate_limit_remaining == 0
        assert result.rate_limit_limit == 100


class TestRateLimitDiscovererInitialization:
    """Test RateLimitDiscoverer initialization."""

    def test_default_config(self):
        """Test initialization with default config."""
        discoverer = RateLimitDiscoverer()
        assert discoverer.config.enabled is False
        assert discoverer.config.max_probe_rate == 20
        assert discoverer.is_enabled() is False

    def test_dict_config(self):
        """Test initialization with dict config."""
        config = {
            "enabled": True,
            "max_probe_rate": 30,
            "safe_mode": False,
        }
        discoverer = RateLimitDiscoverer(config=config)
        assert discoverer.config.enabled is True
        assert discoverer.config.max_probe_rate == 30
        assert discoverer.is_enabled() is True

    def test_config_object(self):
        """Test initialization with RateLimitDiscoveryConfig object."""
        config = RateLimitDiscoveryConfig(enabled=True)
        discoverer = RateLimitDiscoverer(config=config)
        assert discoverer.is_enabled() is True


class TestRateLimitDiscoverLimits:
    """Test rate limit discovery functionality."""

    @pytest.mark.asyncio
    async def test_discover_limits_disabled(self):
        """Test that disabled discoverer returns unknown confidence."""
        discoverer = RateLimitDiscoverer(config={"enabled": False})

        async def mock_request():
            return ProbeResult(status_code=200, response_time_ms=50.0)

        result = await discoverer.discover_limits("/api/test", mock_request)

        assert result.confidence == "unknown"
        stats = discoverer.get_stats()
        assert stats["skipped_disabled"] == 1
        assert stats["endpoints_probed"] == 0

    @pytest.mark.asyncio
    async def test_discover_limits_no_rate_limit(self):
        """Test discovery when no rate limit is hit."""
        discoverer = RateLimitDiscoverer(
            config={
                "enabled": True,
                "max_probe_rate": 5,
                "probe_delay_seconds": 0.01,
            },
        )

        async def mock_request():
            return ProbeResult(status_code=200, response_time_ms=50.0)

        result = await discoverer.discover_limits("/api/test", mock_request)

        # Confidence is low because we didn't hit the limit
        assert result.confidence == "low"
        assert result.endpoint == "/api/test"
        stats = discoverer.get_stats()
        assert stats["requests_made"] == 5

    @pytest.mark.asyncio
    async def test_discover_limits_hits_rate_limit(self):
        """Test discovery when rate limit is hit."""
        discoverer = RateLimitDiscoverer(
            config={
                "enabled": True,
                "max_probe_rate": 10,
                "probe_delay_seconds": 0.01,
                "safe_mode": True,
            },
        )

        call_count = 0

        async def mock_request():
            nonlocal call_count
            call_count += 1
            if call_count > 3:
                return ProbeResult(status_code=429, response_time_ms=10.0, retry_after=60.0)
            return ProbeResult(status_code=200, response_time_ms=50.0)

        result = await discoverer.discover_limits("/api/test", mock_request)

        # Should stop at first 429 in safe mode
        assert call_count == 4
        assert result.retry_after_header is True
        stats = discoverer.get_stats()
        assert stats["rate_limits_hit"] == 1

    @pytest.mark.asyncio
    async def test_discover_limits_with_headers(self):
        """Test discovery with rate limit headers."""
        discoverer = RateLimitDiscoverer(
            config={
                "enabled": True,
                "max_probe_rate": 3,
                "probe_delay_seconds": 0.01,
            },
        )

        async def mock_request():
            return ProbeResult(
                status_code=200,
                response_time_ms=50.0,
                rate_limit_limit=100,
                rate_limit_remaining=95,
            )

        result = await discoverer.discover_limits("/api/test", mock_request)

        assert result.requests_per_minute == 100
        assert result.rate_limit_header == "X-RateLimit-Limit"


class TestRateLimitDiscoverFromHeaders:
    """Test header-only rate limit discovery."""

    @pytest.mark.asyncio
    async def test_discover_from_headers(self):
        """Test discovering rate limits from headers."""
        discoverer = RateLimitDiscoverer()

        async def mock_request():
            return ProbeResult(
                status_code=200,
                response_time_ms=50.0,
                headers={
                    "X-RateLimit-Limit": "1000",
                    "X-RateLimit-Remaining": "950",
                },
            )

        result = await discoverer.discover_from_headers("/api/test", mock_request)

        assert result.requests_per_minute == 1000
        assert result.rate_limit_header == "X-RateLimit-Limit"
        assert result.confidence == "high"

    @pytest.mark.asyncio
    async def test_discover_from_headers_429(self):
        """Test discovering from 429 response headers."""
        discoverer = RateLimitDiscoverer()

        async def mock_request():
            return ProbeResult(
                status_code=429,
                response_time_ms=10.0,
                headers={
                    "Retry-After": "60",
                },
            )

        result = await discoverer.discover_from_headers("/api/test", mock_request)

        assert result.retry_after_header is True
        assert result.retry_after_value == 60.0
        stats = discoverer.get_stats()
        assert stats["rate_limits_hit"] == 1


class TestParseRateLimitHeaders:
    """Test parse_rate_limit_headers convenience function."""

    def test_parse_standard_headers(self):
        """Test parsing standard rate limit headers."""
        headers = {
            "X-RateLimit-Limit": "1000",
            "X-RateLimit-Remaining": "950",
            "X-RateLimit-Reset": "1609459200",
        }
        result = parse_rate_limit_headers(headers)

        assert result["limit"] == 1000
        assert result["remaining"] == 950
        assert result["reset"] == 1609459200

    def test_parse_retry_after(self):
        """Test parsing Retry-After header."""
        headers = {"Retry-After": "60"}
        result = parse_rate_limit_headers(headers)

        assert result["retry_after"] == 60.0

    def test_parse_case_insensitive(self):
        """Test that header parsing is case-insensitive."""
        headers = {
            "x-ratelimit-limit": "500",
            "RETRY-AFTER": "30",
        }
        result = parse_rate_limit_headers(headers)

        assert result["limit"] == 500
        assert result["retry_after"] == 30.0

    def test_parse_invalid_values(self):
        """Test parsing with invalid values."""
        headers = {
            "X-RateLimit-Limit": "not-a-number",
            "Retry-After": "invalid",
        }
        result = parse_rate_limit_headers(headers)

        # Invalid values should not be included or kept as strings
        assert "limit" not in result
        assert result.get("retry_after") == "invalid"


# Error Catalog Builder Tests


class TestErrorCatalogConfig:
    """Test ErrorCatalogConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ErrorCatalogConfig()
        assert config.enabled is True
        assert config.max_errors_per_endpoint == 10
        assert config.max_message_length == 200
        assert config.track_frequency is True
        assert config.categorize_errors is True


class TestErrorEntry:
    """Test ErrorEntry dataclass."""

    def test_to_dict(self):
        """Test to_dict method."""
        entry = ErrorEntry(
            status_code=401,
            error_type="authentication",
            message="Invalid token",
            message_pattern="Invalid token",
            endpoint="/api/test",
            method="GET",
            frequency=5,
            resolution="Check API token validity",
        )
        result = entry.to_dict()

        assert result["status_code"] == 401
        assert result["error_type"] == "authentication"
        assert result["message_pattern"] == "Invalid token"
        assert result["frequency"] == 5
        assert result["resolution"] == "Check API token validity"

    def test_to_dict_without_resolution(self):
        """Test to_dict omits empty resolution."""
        entry = ErrorEntry(
            status_code=400,
            error_type="validation",
            message="Invalid request",
            message_pattern="Invalid request",
            endpoint="/api/test",
            method="POST",
        )
        result = entry.to_dict()

        assert "resolution" not in result

    def test_to_extension(self):
        """Test to_extension method."""
        entry = ErrorEntry(
            status_code=404,
            error_type="not_found",
            message="Resource not found",
            message_pattern="Resource not found",
            endpoint="/api/test",
            method="GET",
            frequency=3,
            resolution="Check resource exists",
        )
        result = entry.to_extension()

        assert result["status_code"] == 404
        assert result["error_type"] == "not_found"
        assert result["resolution"] == "Check resource exists"


class TestEndpointErrors:
    """Test EndpointErrors dataclass."""

    def test_to_dict(self):
        """Test to_dict method."""
        entry = ErrorEntry(
            status_code=401,
            error_type="authentication",
            message="Auth error",
            message_pattern="Auth error",
            endpoint="/api/test",
            method="GET",
        )
        endpoint_errors = EndpointErrors(
            endpoint="/api/test",
            method="GET",
            errors=[entry],
            total_errors=5,
        )
        result = endpoint_errors.to_dict()

        assert result["endpoint"] == "/api/test"
        assert result["method"] == "GET"
        assert result["total_errors"] == 5
        assert len(result["errors"]) == 1


class TestErrorCatalog:
    """Test ErrorCatalog dataclass."""

    def test_to_dict(self):
        """Test to_dict method."""
        catalog = ErrorCatalog(
            total_errors=10,
            unique_patterns=5,
            discovered_at="2024-01-01T00:00:00Z",
        )
        result = catalog.to_dict()

        assert result["total_errors"] == 10
        assert result["unique_patterns"] == 5
        assert result["discovered_at"] == "2024-01-01T00:00:00Z"

    def test_to_extension(self):
        """Test to_extension method."""
        entry = ErrorEntry(
            status_code=401,
            error_type="authentication",
            message="Auth error",
            message_pattern="Auth error",
            endpoint="/api/test",
            method="GET",
            resolution="Check token",
        )
        catalog = ErrorCatalog()
        catalog.errors_by_status[401] = [entry]
        result = catalog.to_extension()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["status_code"] == 401


class TestBuilderStats:
    """Test BuilderStats dataclass."""

    def test_default_values(self):
        """Test default stats values."""
        stats = BuilderStats()
        assert stats.errors_recorded == 0
        assert stats.errors_deduplicated == 0
        assert stats.patterns_extracted == 0
        assert stats.resolutions_generated == 0

    def test_to_dict(self):
        """Test to_dict method."""
        stats = BuilderStats(
            errors_recorded=50,
            errors_deduplicated=10,
            patterns_extracted=40,
            resolutions_generated=35,
        )
        result = stats.to_dict()

        assert result["errors_recorded"] == 50
        assert result["errors_deduplicated"] == 10


class TestErrorCatalogBuilder:
    """Test ErrorCatalogBuilder class."""

    def test_default_initialization(self):
        """Test initialization with default config."""
        builder = ErrorCatalogBuilder()
        assert builder.config.enabled is True
        assert builder.config.max_errors_per_endpoint == 10

    def test_dict_config(self):
        """Test initialization with dict config."""
        config = {
            "enabled": True,
            "max_errors_per_endpoint": 5,
            "max_message_length": 100,
        }
        builder = ErrorCatalogBuilder(config=config)
        assert builder.config.max_errors_per_endpoint == 5
        assert builder.config.max_message_length == 100

    def test_config_object(self):
        """Test initialization with ErrorCatalogConfig object."""
        config = ErrorCatalogConfig(enabled=False)
        builder = ErrorCatalogBuilder(config=config)
        assert builder.config.enabled is False


class TestErrorRecording:
    """Test error recording functionality."""

    def test_record_error_basic(self):
        """Test basic error recording."""
        builder = ErrorCatalogBuilder()
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized access"},
        )

        assert entry is not None
        assert entry.status_code == 401
        assert entry.endpoint == "/api/test"
        assert entry.method == "GET"

    def test_record_error_disabled(self):
        """Test error recording when disabled."""
        builder = ErrorCatalogBuilder(config={"enabled": False})
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized"},
        )

        assert entry is None

    def test_record_error_max_limit(self):
        """Test that max errors per endpoint is respected."""
        builder = ErrorCatalogBuilder(config={"max_errors_per_endpoint": 2})

        # Record different error patterns
        for i in range(5):
            builder.record_error(
                endpoint="/api/test",
                method="GET",
                status_code=400 + i,
                response_body={"message": f"Error {i}"},
            )

        errors = builder.get_errors_for_endpoint("/api/test", "GET")
        assert len(errors) == 2

    def test_record_error_deduplication(self):
        """Test that duplicate errors are deduplicated."""
        builder = ErrorCatalogBuilder()

        # Record same error twice
        builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized"},
        )
        builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized"},
        )

        errors = builder.get_errors_for_endpoint("/api/test", "GET")
        assert len(errors) == 1
        assert errors[0].frequency == 2

    def test_record_error_string_body(self):
        """Test recording error with string body."""
        builder = ErrorCatalogBuilder()
        entry = builder.record_error(
            endpoint="/api/test",
            method="POST",
            status_code=500,
            response_body="Internal server error",
        )

        assert entry is not None
        assert "Internal server error" in entry.message

    def test_record_error_none_body(self):
        """Test recording error with None body."""
        builder = ErrorCatalogBuilder()
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=503,
            response_body=None,
        )

        assert entry is not None
        assert entry.message == ""


class TestErrorClassification:
    """Test error type classification."""

    @pytest.fixture
    def builder(self):
        """Create a fresh builder for each test."""
        return ErrorCatalogBuilder()

    def test_classify_authentication(self, builder):
        """Test authentication error classification."""
        # Use "Unauthorized" message that matches authentication patterns
        # Note: "Invalid token" would match "invalid" (validation) before "token" (auth)
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized access - token expired"},
        )

        assert entry.error_type == "authentication"

    def test_classify_authorization(self, builder):
        """Test authorization error classification."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=403,
            response_body={"message": "Access denied"},
        )

        assert entry.error_type == "authorization"

    def test_classify_not_found(self, builder):
        """Test not found error classification."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=404,
            response_body={"message": "Resource not found"},
        )

        assert entry.error_type == "not_found"

    def test_classify_validation(self, builder):
        """Test validation error classification."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="POST",
            status_code=400,
            response_body={"message": "Invalid request format"},
        )

        assert entry.error_type == "validation"

    def test_classify_conflict(self, builder):
        """Test conflict error classification."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="POST",
            status_code=409,
            response_body={"message": "Resource already exists"},
        )

        assert entry.error_type == "conflict"

    def test_classify_rate_limit(self, builder):
        """Test rate limit error classification."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=429,
            response_body={"message": "Too many requests"},
        )

        assert entry.error_type == "rate_limit"

    def test_classify_server_error(self, builder):
        """Test server error classification."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=500,
            response_body={"message": "Internal error occurred"},
        )

        assert entry.error_type == "server_error"


class TestPatternExtraction:
    """Test pattern extraction from error messages."""

    @pytest.fixture
    def builder(self):
        """Create a fresh builder for each test."""
        return ErrorCatalogBuilder()

    def test_extract_uuid_pattern(self, builder):
        """Test UUID replacement in patterns."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=404,
            response_body={"message": "Resource 550e8400-e29b-41d4-a716-446655440000 not found"},
        )

        assert "{id}" in entry.message_pattern
        assert "550e8400" not in entry.message_pattern

    def test_extract_quoted_string_pattern(self, builder):
        """Test quoted string replacement."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="POST",
            status_code=400,
            response_body={"message": 'Field "username" is required'},
        )

        assert '"{value}"' in entry.message_pattern

    def test_extract_number_pattern(self, builder):
        """Test number replacement."""
        entry = builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=400,
            response_body={"message": "Maximum of 100 items exceeded"},
        )

        assert "{number}" in entry.message_pattern


class TestBuildCatalog:
    """Test catalog building functionality."""

    def test_build_empty_catalog(self):
        """Test building empty catalog."""
        builder = ErrorCatalogBuilder()
        catalog = builder.build_catalog()

        assert catalog.total_errors == 0
        assert catalog.unique_patterns == 0
        assert catalog.discovered_at != ""

    def test_build_catalog_with_errors(self):
        """Test building catalog with recorded errors."""
        builder = ErrorCatalogBuilder()

        builder.record_error(
            endpoint="/api/users",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized"},
        )
        builder.record_error(
            endpoint="/api/users",
            method="POST",
            status_code=400,
            response_body={"message": "Invalid request"},
        )

        catalog = builder.build_catalog()

        assert catalog.total_errors == 2
        assert catalog.unique_patterns == 2
        assert 401 in catalog.errors_by_status
        assert 400 in catalog.errors_by_status

    def test_get_errors_by_status(self):
        """Test getting errors by status code."""
        builder = ErrorCatalogBuilder()

        builder.record_error(
            endpoint="/api/users",
            method="GET",
            status_code=401,
            response_body={"message": "Auth error 1"},
        )
        builder.record_error(
            endpoint="/api/items",
            method="GET",
            status_code=401,
            response_body={"message": "Auth error 2"},
        )

        errors = builder.get_errors_by_status(401)
        assert len(errors) == 2

    def test_clear(self):
        """Test clearing recorded errors."""
        builder = ErrorCatalogBuilder()

        builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=500,
            response_body={"message": "Error"},
        )

        assert builder.get_stats()["errors_recorded"] > 0

        builder.clear()

        assert builder.get_stats()["errors_recorded"] == 0
        catalog = builder.build_catalog()
        assert catalog.total_errors == 0


class TestBuilderStatsTracking:
    """Test builder statistics tracking."""

    def test_stats_after_recording(self):
        """Test that stats are updated correctly."""
        builder = ErrorCatalogBuilder()

        builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized"},
        )

        stats = builder.get_stats()
        assert stats["errors_recorded"] == 1
        assert stats["patterns_extracted"] == 1
        assert stats["resolutions_generated"] == 1

    def test_stats_deduplication(self):
        """Test deduplication is tracked in stats."""
        builder = ErrorCatalogBuilder()

        # Same error twice
        builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized"},
        )
        builder.record_error(
            endpoint="/api/test",
            method="GET",
            status_code=401,
            response_body={"message": "Unauthorized"},
        )

        stats = builder.get_stats()
        assert stats["errors_recorded"] == 2
        assert stats["errors_deduplicated"] == 1
