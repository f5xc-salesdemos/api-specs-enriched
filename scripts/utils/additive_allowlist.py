# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Classifier for contract-diff: is a given change additive and therefore allowed?

Encodes spec §4.3 plus the four extensions from 2026-04-22 §4. Given a deepdiff
``change_type`` and ``pointer`` string (e.g.
``"root['paths']['/x']['get']['description']"``) — and optionally the ``before``
and ``after`` values — ``is_additive_change`` returns ``True`` if the change is
on the additive allowlist (safe) and ``False`` if it represents a
contract-breaking modification.
"""

from __future__ import annotations

import re

from deepdiff import DeepDiff

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

_ERROR_RESPONSE_TYPE_RE = re.compile(
    r"\['paths'\]\[[^\]]+\]\[[^\]]+\]\['responses'\]\['[45]\d\d'\]"
    r"\['content'\]\['application/json'\]\['schema'\]\['type'\]$",
)

_OPENAPI_FORMATS = frozenset(
    {
        "uuid",
        "uri",
        "hostname",
        "ipv4",
        "ipv6",
        "email",
        "date",
        "date-time",
        "time",
        "duration",
        "byte",
        "binary",
        "password",
        "int32",
        "int64",
        "float",
        "double",
    },
)


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


def _is_dictionary_item_added_additive(
    terminal: str,
    pointer: str,
    after: object,
) -> bool:
    """Dispatch table for ``dictionary_item_added`` changes."""
    if terminal.startswith("x-"):
        return True
    if terminal in _FREE_TEXT_KEYS:
        return True
    if _is_error_response_type_add(pointer):
        return True
    if _is_positive_int_maxlength_add(terminal, after):
        return True
    return _is_known_format_add(terminal, after)


def _is_values_changed_additive(
    terminal: str,
    pointer: str,
    before: object,
    after: object,
) -> bool:
    """Dispatch table for ``values_changed`` changes."""
    if terminal in {"description", "summary", "example"}:
        return True
    if _under_x_extension(pointer):
        return True
    return _is_additive_dict_rewrite(pointer, before, after)


def is_additive_change(
    change_type: str,
    pointer: str,
    before: object = None,
    after: object = None,
) -> bool:
    """Return True iff this change is on the additive allowlist.

    Rules match spec 2026-04-21 §4.3 plus the four extensions from
    2026-04-22 §4 (error-response type, positive maxLength, recursive
    dict rewrites, known-format adds).
    """
    terminal = _terminal_key(pointer)
    parent = _parent_key(pointer)

    if change_type == "dictionary_item_added":
        return _is_dictionary_item_added_additive(terminal, pointer, after)

    if change_type == "values_changed":
        return _is_values_changed_additive(terminal, pointer, before, after)

    if change_type == "iterable_item_added":
        return parent in _ARRAY_ADDABLE_PARENTS

    return False


def _is_error_response_type_add(pointer: str) -> bool:
    """Rule 1 — `type: "string"` on 4XX/5XX response schemas (family 5)."""
    return bool(_ERROR_RESPONSE_TYPE_RE.search(pointer))


def _is_positive_int_maxlength_add(terminal: str, after: object) -> bool:
    """Rule 2 — `maxLength` with positive int (family 6)."""
    return (
        terminal == "maxLength"
        and isinstance(after, int)
        and not isinstance(after, bool)
        and after > 0
    )


def _is_known_format_add(terminal: str, after: object) -> bool:
    """Rule 4 — known OpenAPI format additions (family 8)."""
    return terminal == "format" and after in _OPENAPI_FORMATS


_MAX_DICT_REWRITE_DEPTH = 4


def _is_additive_dict_rewrite(
    pointer: str,
    before: object,
    after: object,
    _depth: int = 0,
) -> bool:
    """Rule 3 — decompose a whole-dict rewrite and apply rules recursively.

    deepdiff reports multi-key changes at a parent dict as a single
    ``values_changed``. If every inner change is individually additive by
    the rules above, the whole rewrite is additive.

    ``_depth`` caps recursion through nested dict rewrites to avoid
    blowing the Python/deepdiff stack on very deep OpenAPI subtrees.
    """
    if not (isinstance(before, dict) and isinstance(after, dict)):
        return False
    if _depth >= _MAX_DICT_REWRITE_DEPTH:
        return False

    try:
        inner = DeepDiff(
            before,
            after,
            ignore_order=True,
            view="tree",
            threshold_to_diff_deeper=0.0,
        )
    except RecursionError:
        return False
    for inner_change_type, inner_changes in inner.items():
        for inner_change in inner_changes:
            sub_pointer = f"{pointer}{inner_change.path()}"
            sub_before = getattr(inner_change, "t1", None)
            sub_after = getattr(inner_change, "t2", None)
            if not _is_additive_inner(
                inner_change_type,
                sub_pointer,
                sub_before,
                sub_after,
                _depth + 1,
            ):
                return False
    return True


def _is_additive_inner(
    change_type: str,
    pointer: str,
    before: object,
    after: object,
    depth: int,
) -> bool:
    """Depth-aware variant of :func:`is_additive_change` for Rule 3 recursion."""
    terminal = _terminal_key(pointer)
    parent = _parent_key(pointer)

    if change_type == "dictionary_item_added":
        return _is_dictionary_item_added_additive(terminal, pointer, after)

    if change_type == "values_changed":
        if terminal in {"description", "summary", "example"}:
            return True
        if _under_x_extension(pointer):
            return True
        return _is_additive_dict_rewrite(pointer, before, after, depth)

    if change_type == "iterable_item_added":
        return parent in _ARRAY_ADDABLE_PARENTS

    return False
