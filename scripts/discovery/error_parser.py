"""Parse F5 XC API validation error messages to extract constraint values."""

from __future__ import annotations

import re


def _to_num(s: str) -> int | float:
    """Convert string to int if whole number, else float."""
    f = float(s)
    return int(f) if f == int(f) else f


_PATTERNS: list[tuple[re.Pattern, callable]] = [
    (
        re.compile(r"must be >= (-?[\d.]+) and <= (-?[\d.]+)", re.IGNORECASE),
        lambda m: {"minimum": _to_num(m.group(1)), "maximum": _to_num(m.group(2))},
    ),
    (
        re.compile(r"must be between (-?[\d.]+) and (-?[\d.]+)", re.IGNORECASE),
        lambda m: {"minimum": _to_num(m.group(1)), "maximum": _to_num(m.group(2))},
    ),
    (
        re.compile(r"DNS-1035 label", re.IGNORECASE),
        lambda _m: {"pattern": "^[a-z]([-a-z0-9]*[a-z0-9])?$", "format": "dns-1035"},
    ),
    (
        re.compile(r"length must be <= (\d+)", re.IGNORECASE),
        lambda m: {"maxLength": int(m.group(1))},
    ),
    (
        re.compile(r"length must be >= (\d+)", re.IGNORECASE),
        lambda m: {"minLength": int(m.group(1))},
    ),
    (
        re.compile(r"must be >= (-?[\d.]+)(?!\s+and)", re.IGNORECASE),
        lambda m: {"minimum": _to_num(m.group(1))},
    ),
    (
        re.compile(r"must be <= (-?[\d.]+)", re.IGNORECASE),
        lambda m: {"maximum": _to_num(m.group(1))},
    ),
    (
        re.compile(r"one of \[([^\]]+)\]", re.IGNORECASE),
        lambda m: {
            "variants": [v.strip().rstrip(",") for v in m.group(1).split() if v.strip().rstrip(",")]
        },
    ),
    (
        re.compile(r"valid values are \[([^\]]+)\]", re.IGNORECASE),
        lambda m: {"enum_values": [v.strip() for v in m.group(1).split(",") if v.strip()]},
    ),
]


def parse_constraint_from_error(error_message: str) -> dict | None:
    """Extract a constraint from an F5 XC API validation error message."""
    if not error_message:
        return None

    for pattern, extractor in _PATTERNS:
        match = pattern.search(error_message)
        if match:
            return extractor(match)

    return None
