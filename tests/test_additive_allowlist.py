# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Unit tests for the additive allowlist classifier (spec §4.3)."""

from scripts.utils.additive_allowlist import is_additive_change


def t(pointer):
    return pointer


def test_added_x_extension_is_additive():
    assert is_additive_change(
        "dictionary_item_added",
        t("root['paths']['/x']['get']['x-f5xc-cli-help']"),
    )


def test_added_description_is_additive():
    assert is_additive_change(
        "dictionary_item_added",
        t("root['components']['schemas']['Foo']['properties']['bar']['description']"),
    )


def test_rewritten_description_is_additive():
    assert is_additive_change(
        "values_changed",
        t("root['paths']['/x']['get']['description']"),
    )


def test_rewritten_summary_is_additive():
    assert is_additive_change(
        "values_changed",
        t("root['paths']['/x']['get']['summary']"),
    )


def test_rewritten_example_is_additive():
    assert is_additive_change(
        "values_changed",
        t("root['components']['schemas']['Foo']['example']"),
    )


def test_values_changed_inside_x_extension_is_additive():
    assert is_additive_change(
        "values_changed",
        t("root['paths']['/x']['get']['x-f5xc-cli-help']['hint']"),
    )


def test_appended_tag_is_additive():
    assert is_additive_change(
        "iterable_item_added",
        t("root['paths']['/x']['get']['tags'][2]"),
    )


def test_added_to_required_is_not_additive():
    assert not is_additive_change(
        "iterable_item_added",
        t("root['components']['schemas']['Foo']['required'][1]"),
    )


def test_added_to_enum_is_not_additive():
    assert not is_additive_change(
        "iterable_item_added",
        t("root['components']['schemas']['Foo']['enum'][2]"),
    )


def test_removed_key_is_not_additive():
    assert not is_additive_change(
        "dictionary_item_removed",
        t("root['paths']['/x']['get']['parameters']"),
    )


def test_appended_server_is_additive():
    """servers is one of the allowlisted array parents (spec 4.3)."""
    assert is_additive_change("iterable_item_added", t("root['servers'][1]"))


def test_appended_examples_is_additive():
    """examples is one of the allowlisted array parents (spec 4.3)."""
    assert is_additive_change(
        "iterable_item_added",
        t("root['components']['schemas']['Foo']['examples'][0]"),
    )


def test_added_summary_is_additive():
    """Free-text non-description keys are also covered by the allowlist."""
    assert is_additive_change("dictionary_item_added", t("root['paths']['/x']['get']['summary']"))


def test_nested_tag_array_is_not_additive():
    """Rule applies only when the direct parent is an allowlisted array."""
    assert not is_additive_change(
        "iterable_item_added",
        t("root['paths']['/x']['get']['tags'][2][0]"),
    )


def test_changed_type_is_not_additive():
    assert not is_additive_change(
        "type_changes",
        t("root['components']['schemas']['Foo']['properties']['bar']['type']"),
    )


def test_changed_min_length_is_not_additive():
    assert not is_additive_change(
        "values_changed",
        t("root['components']['schemas']['Foo']['properties']['bar']['minLength']"),
    )


def test_changed_ref_is_not_additive():
    assert not is_additive_change(
        "values_changed",
        t("root['components']['schemas']['Foo']['properties']['bar']['$ref']"),
    )


def test_renamed_operation_id_is_not_additive():
    assert not is_additive_change(
        "values_changed",
        t("root['paths']['/x']['get']['operationId']"),
    )


# Rule 1 — error-response type additions (family 5)


def test_error_response_type_add_is_additive():
    pointer = (
        "root['paths']['/x']['get']['responses']['401']"
        "['content']['application/json']['schema']['type']"
    )
    assert is_additive_change("dictionary_item_added", pointer, None, "string")


def test_error_response_type_add_on_2xx_is_not_additive():
    pointer = (
        "root['paths']['/x']['get']['responses']['200']"
        "['content']['application/json']['schema']['type']"
    )
    assert not is_additive_change("dictionary_item_added", pointer, None, "string")


# Rule 2 — positive-int maxLength additions (family 6)


def test_positive_int_max_length_add_is_additive():
    pointer = "root['components']['schemas']['Foo']['properties']['bar']['maxLength']"
    assert is_additive_change("dictionary_item_added", pointer, None, 128)


def test_zero_max_length_add_is_not_additive():
    """maxLength: 0 means empty-only — always broken."""
    pointer = "root['components']['schemas']['Foo']['properties']['bar']['maxLength']"
    assert not is_additive_change("dictionary_item_added", pointer, None, 0)


def test_non_int_max_length_add_is_not_additive():
    pointer = "root['components']['schemas']['Foo']['properties']['bar']['maxLength']"
    assert not is_additive_change("dictionary_item_added", pointer, None, "128")


# Rule 3 — recursive dict-node rewrites (family 7)


def test_additive_dict_rewrite_is_accepted():
    """Whole-parameter rewrite where every inner change is additive."""
    pointer = "root['paths']['/x']['get']['parameters'][0]"
    before = {
        "name": "namespace",
        "in": "path",
        "description": "The namespace.\nx-example: system",
        "required": True,
    }
    after = {
        "name": "namespace",
        "in": "path",
        "description": "The namespace.",
        "required": True,
        "x-f5xc-example": "system",
    }
    assert is_additive_change("values_changed", pointer, before, after)


def test_non_additive_dict_rewrite_is_rejected():
    """Whole-parameter rewrite where one inner change flips a required flag."""
    pointer = "root['paths']['/x']['get']['parameters'][0]"
    before = {"name": "ns", "in": "path", "required": True}
    after = {"name": "ns", "in": "path", "required": False}
    assert not is_additive_change("values_changed", pointer, before, after)


# Rule 4 — known-format additions (family 8)


def test_known_format_add_is_additive():
    pointer = "root['components']['schemas']['Foo']['properties']['uid']['format']"
    assert is_additive_change("dictionary_item_added", pointer, None, "uuid")


def test_unknown_format_add_is_not_additive():
    pointer = "root['components']['schemas']['Foo']['properties']['uid']['format']"
    assert not is_additive_change("dictionary_item_added", pointer, None, "totally-made-up")
