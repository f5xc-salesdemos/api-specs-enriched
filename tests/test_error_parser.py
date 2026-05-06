"""Unit tests for constraint error message parser."""

from __future__ import annotations

from scripts.discovery.error_parser import parse_constraint_from_error


class TestNumericRangePatterns:
    def test_parses_gte_lte_format(self):
        error = "value must be >= 1 and <= 600"
        result = parse_constraint_from_error(error)
        assert result == {"minimum": 1, "maximum": 600}

    def test_parses_between_format(self):
        error = "value must be between 1 and 600"
        result = parse_constraint_from_error(error)
        assert result == {"minimum": 1, "maximum": 600}

    def test_parses_gte_only(self):
        error = "value must be >= 10"
        result = parse_constraint_from_error(error)
        assert result == {"minimum": 10}

    def test_parses_lte_only(self):
        error = "value must be <= 50"
        result = parse_constraint_from_error(error)
        assert result == {"maximum": 50}


class TestStringPatterns:
    def test_parses_dns1035_pattern(self):
        error = "does not satisfy DNS-1035 label requirements"
        result = parse_constraint_from_error(error)
        assert result == {"pattern": "^[a-z]([-a-z0-9]*[a-z0-9])?$", "format": "dns-1035"}

    def test_parses_max_length(self):
        error = "length must be <= 63"
        result = parse_constraint_from_error(error)
        assert result == {"maxLength": 63}

    def test_parses_min_length(self):
        error = "length must be >= 1"
        result = parse_constraint_from_error(error)
        assert result == {"minLength": 1}


class TestOneOfPatterns:
    def test_parses_exactly_one_of(self):
        error = "exactly one of [http_health_check tcp_health_check udp_icmp_health_check] must be specified"
        result = parse_constraint_from_error(error)
        assert result == {
            "variants": ["http_health_check", "tcp_health_check", "udp_icmp_health_check"]
        }

    def test_parses_one_of_with_commas(self):
        error = "one of [a, b, c] must be specified"
        result = parse_constraint_from_error(error)
        assert result == {"variants": ["a", "b", "c"]}


class TestEnumPatterns:
    def test_parses_valid_values_list(self):
        error = "invalid value 'BAD', valid values are [VAL_A, VAL_B, VAL_C]"
        result = parse_constraint_from_error(error)
        assert result == {"enum_values": ["VAL_A", "VAL_B", "VAL_C"]}


class TestUnknownError:
    def test_returns_none_for_unknown_format(self):
        error = "some completely unrecognized error format xyz"
        result = parse_constraint_from_error(error)
        assert result is None

    def test_returns_none_for_empty_string(self):
        result = parse_constraint_from_error("")
        assert result is None
