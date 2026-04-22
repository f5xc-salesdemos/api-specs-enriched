"""Regression guard: enrichers must not rewrite upstream `title` values.

Title is a metadata field that downstream codegens and doc tools
compare byte-for-byte against upstream; silently rewriting it breaks
those tools. See design spec 2026-04-22 section 3.1.
"""

from __future__ import annotations

from scripts.utils.acronyms import AcronymNormalizer
from scripts.utils.branding import BrandingTransformer
from scripts.utils.grammar import GrammarImprover


def _spec_with_titles() -> dict:
    return {
        "info": {"title": "some api", "description": "Some API."},
        "components": {
            "schemas": {
                "InitializerType": {
                    "type": "object",
                    "title": "InitializerType",
                    "properties": {
                        "message": {"type": "string", "title": "message"},
                        "annotations": {"type": "array", "title": "annotations"},
                    },
                },
            },
        },
    }


def _collect_titles(obj, acc=None):
    acc = {} if acc is None else acc
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "title" and isinstance(v, str):
                acc.setdefault(v, 0)
                acc[v] += 1
            _collect_titles(v, acc)
    elif isinstance(obj, list):
        for item in obj:
            _collect_titles(item, acc)
    return acc


def test_acronym_normalizer_preserves_titles():
    spec = _spec_with_titles()
    before = _collect_titles(spec)
    result = AcronymNormalizer().normalize_spec(spec)
    after = _collect_titles(result)
    assert after == before, (
        f"Acronym normalizer must not rewrite title values. Before: {before}, After: {after}"
    )


def test_branding_transformer_preserves_titles():
    spec = _spec_with_titles()
    before = _collect_titles(spec)
    result = BrandingTransformer().transform_spec(spec)
    after = _collect_titles(result)
    assert after == before


def test_grammar_improver_preserves_titles():
    spec = _spec_with_titles()
    before = _collect_titles(spec)
    result = GrammarImprover().improve_spec(spec)
    after = _collect_titles(result)
    assert after == before
