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
