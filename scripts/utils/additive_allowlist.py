# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Classifier for contract-diff: is a given change additive and therefore allowed?

Encodes spec §4.3. Given a deepdiff ``change_type`` and ``pointer`` string
(e.g. ``"root['paths']['/x']['get']['description']"``), ``is_additive_change``
returns ``True`` if the change is on the additive allowlist (safe) and
``False`` if it represents a contract-breaking modification.
"""

from __future__ import annotations

import re

_FREE_TEXT_KEYS = frozenset(
    {
        "description",
        "summary",
        "example",
        "examples",
        "externalDocs",
        "tags",
    },
)
_ARRAY_ADDABLE_PARENTS = frozenset({"tags", "servers", "examples"})

_SEGMENT_RE = re.compile(r"\['([^']+)'\]|\[(\d+)\]")
_X_EXTENSION_RE = re.compile(r"\['x-[^']+'\]")


def _terminal_key(pointer: str) -> str:
    """Return the last bracketed segment from a deepdiff pointer string.

    Example: ``root['a']['b']['c']`` -> ``"c"``; ``root['tags'][2]`` -> ``"2"``.
    """
    segments = _SEGMENT_RE.findall(pointer)
    if not segments:
        return ""
    last = segments[-1]
    return last[0] or last[1]


def _parent_key(pointer: str) -> str:
    """Return the second-to-last bracketed segment, or ``""`` if absent."""
    segments = _SEGMENT_RE.findall(pointer)
    if len(segments) < 2:
        return ""
    prev = segments[-2]
    return prev[0] or prev[1]


def _under_x_extension(pointer: str) -> bool:
    """Return ``True`` if any path segment is a vendor extension key (``x-*``)."""
    return bool(_X_EXTENSION_RE.search(pointer))


def is_additive_change(change_type: str, pointer: str) -> bool:
    """Return ``True`` iff this change is on the additive allowlist (spec §4.3)."""
    terminal = _terminal_key(pointer)
    parent = _parent_key(pointer)

    if change_type == "dictionary_item_added":
        if terminal.startswith("x-"):
            return True
        return terminal in _FREE_TEXT_KEYS

    if change_type == "values_changed":
        if terminal in {"description", "summary", "example"}:
            return True
        return _under_x_extension(pointer)

    if change_type == "iterable_item_added":
        return parent in _ARRAY_ADDABLE_PARENTS

    return False
