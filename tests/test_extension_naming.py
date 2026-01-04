"""Tests for extension naming constants and validation utilities.

Issue: #292
"""

from __future__ import annotations

import pytest

from scripts.utils.extension_constants import (
    FIELD_MIGRATION,
    FIELD_MIGRATION_REVERSE,
    PRESERVED_NATIVE_EXTENSIONS,
    VALID_X_F5XC_EXTENSIONS,
    X_F5XC_CATEGORY,
    X_F5XC_CLI_ALIASES,
    X_F5XC_CLI_DOMAIN,
    X_F5XC_DANGER_LEVEL,
    X_F5XC_DESCRIPTION,
    X_F5XC_DESCRIPTION_MEDIUM,
    X_F5XC_DESCRIPTION_SHORT,
    X_F5XC_DISPLAY_NAME,
    X_F5XC_DISPLAYORDER,
    X_F5XC_DOC_SECTION,
    X_F5XC_ENRICHED_VERSION,
    X_F5XC_MINIMUM_CONFIGURATION,
    X_F5XC_NAMESPACE_SCOPE,
    X_F5XC_PREFIX,
    X_F5XC_PRIMARY_RESOURCES,
    X_F5XC_REQUIRED_FIELDS,
    X_F5XC_SIDE_EFFECTS,
    X_F5XC_TERRAFORM_RESOURCE,
    X_F5XC_UPSTREAM_ETAG,
    X_F5XC_UPSTREAM_TIMESTAMP,
    is_old_extension,
    is_preserved_native,
    is_valid_extension,
    migrate_field_name,
    validate_no_invalid_extensions,
)


class TestNamespacePrefix:
    """Tests for the namespace prefix constant."""

    def test_prefix_value(self) -> None:
        """Verify the prefix is exactly 'x-f5xc-'."""
        assert X_F5XC_PREFIX == "x-f5xc-"

    def test_prefix_starts_with_x(self) -> None:
        """Prefix must start with 'x-' for OpenAPI compliance."""
        assert X_F5XC_PREFIX.startswith("x-")

    def test_prefix_lowercase(self) -> None:
        """Prefix must be lowercase."""
        assert X_F5XC_PREFIX.lower() == X_F5XC_PREFIX


class TestExtensionConstants:
    """Tests for individual extension constant values."""

    @pytest.mark.parametrize(
        "constant",
        [
            X_F5XC_CLI_DOMAIN,
            X_F5XC_CLI_ALIASES,
            X_F5XC_MINIMUM_CONFIGURATION,
            X_F5XC_NAMESPACE_SCOPE,
            X_F5XC_DISPLAYORDER,
            X_F5XC_DESCRIPTION,
            X_F5XC_DANGER_LEVEL,
            X_F5XC_REQUIRED_FIELDS,
            X_F5XC_SIDE_EFFECTS,
            X_F5XC_CATEGORY,  # Single category field (DRY)
            X_F5XC_PRIMARY_RESOURCES,
            X_F5XC_DESCRIPTION_SHORT,
            X_F5XC_DESCRIPTION_MEDIUM,
            X_F5XC_UPSTREAM_TIMESTAMP,
            X_F5XC_UPSTREAM_ETAG,
            X_F5XC_ENRICHED_VERSION,
            X_F5XC_TERRAFORM_RESOURCE,
            X_F5XC_DISPLAY_NAME,
            X_F5XC_DOC_SECTION,
        ],
    )
    def test_constant_has_prefix(self, constant: str) -> None:
        """All extension constants must use x-f5xc- prefix."""
        assert constant.startswith(X_F5XC_PREFIX), f"Constant '{constant}' missing x-f5xc- prefix"

    @pytest.mark.parametrize(
        "constant",
        [
            X_F5XC_CLI_DOMAIN,
            X_F5XC_CLI_ALIASES,
            X_F5XC_MINIMUM_CONFIGURATION,
            X_F5XC_NAMESPACE_SCOPE,
            X_F5XC_DISPLAYORDER,
            X_F5XC_DESCRIPTION,
            X_F5XC_DANGER_LEVEL,
            X_F5XC_REQUIRED_FIELDS,
            X_F5XC_SIDE_EFFECTS,
            X_F5XC_CATEGORY,  # Single category field (DRY)
            X_F5XC_PRIMARY_RESOURCES,
            X_F5XC_DESCRIPTION_SHORT,
            X_F5XC_DESCRIPTION_MEDIUM,
        ],
    )
    def test_constant_is_lowercase(self, constant: str) -> None:
        """Extension names must be lowercase with hyphens."""
        assert constant == constant.lower(), f"Constant '{constant}' must be lowercase"

    @pytest.mark.parametrize(
        "constant",
        [
            X_F5XC_CLI_DOMAIN,
            X_F5XC_CLI_ALIASES,
            X_F5XC_MINIMUM_CONFIGURATION,
            X_F5XC_NAMESPACE_SCOPE,
            X_F5XC_DISPLAYORDER,
            X_F5XC_DESCRIPTION,
            X_F5XC_DANGER_LEVEL,
            X_F5XC_REQUIRED_FIELDS,
            X_F5XC_SIDE_EFFECTS,
            X_F5XC_CATEGORY,  # Single category field (DRY)
            X_F5XC_PRIMARY_RESOURCES,
            X_F5XC_DESCRIPTION_SHORT,
            X_F5XC_DESCRIPTION_MEDIUM,
        ],
    )
    def test_constant_no_underscores(self, constant: str) -> None:
        """Extension names should use hyphens, not underscores (after prefix)."""
        after_prefix = constant[len(X_F5XC_PREFIX) :]
        assert "_" not in after_prefix, f"Constant '{constant}' should use hyphens, not underscores"


class TestFieldMigration:
    """Tests for field migration mapping."""

    def test_migration_mapping_not_empty(self) -> None:
        """Migration mapping should have entries."""
        assert len(FIELD_MIGRATION) > 0

    def test_all_migrations_to_x_f5xc(self) -> None:
        """All migration targets must use x-f5xc- prefix."""
        for old, new in FIELD_MIGRATION.items():
            assert new.startswith(X_F5XC_PREFIX), (
                f"Migration '{old}' -> '{new}' target missing prefix"
            )

    def test_reverse_mapping_consistency(self) -> None:
        """Reverse mapping should map to at least one valid old field.

        Note: Multiple old fields can map to the same new field (DRY principle).
        For example: domain_category, ui_category, category -> x-f5xc-category
        """
        # Reverse mapping has fewer entries due to DRY consolidation
        assert len(FIELD_MIGRATION_REVERSE) <= len(FIELD_MIGRATION)
        for new_field in FIELD_MIGRATION_REVERSE:
            # The reverse should point to one of the old fields that maps to it
            old_field = FIELD_MIGRATION_REVERSE[new_field]
            assert FIELD_MIGRATION[old_field] == new_field

    @pytest.mark.parametrize(
        ("old_field", "expected_new"),
        [
            ("x-ves-cli-domain", "x-f5xc-cli-domain"),
            ("x-ves-minimum-configuration", "x-f5xc-minimum-configuration"),
            ("x-ves-danger-level", "x-f5xc-danger-level"),
            # All category fields map to single x-f5xc-category (DRY)
            ("domain_category", "x-f5xc-category"),
            ("ui_category", "x-f5xc-category"),
            ("category", "x-f5xc-category"),
            ("primary_resources", "x-f5xc-primary-resources"),
            ("description_short", "x-f5xc-description-short"),
            ("description_medium", "x-f5xc-description-medium"),
            ("x-upstream-timestamp", "x-f5xc-upstream-timestamp"),
            ("x-enriched-version", "x-f5xc-enriched-version"),
        ],
    )
    def test_specific_migrations(self, old_field: str, expected_new: str) -> None:
        """Test specific field migrations are correct."""
        assert FIELD_MIGRATION[old_field] == expected_new

    def test_no_self_migrations(self) -> None:
        """No field should migrate to itself."""
        for old, new in FIELD_MIGRATION.items():
            assert old != new, f"Field '{old}' migrates to itself"


class TestPreservedNativeExtensions:
    """Tests for preserved F5 native extensions."""

    def test_preserved_extensions_not_empty(self) -> None:
        """Should have preserved extensions."""
        assert len(PRESERVED_NATIVE_EXTENSIONS) > 0

    @pytest.mark.parametrize(
        "extension",
        [
            "x-ves-proto-package",
            "x-ves-proto-file",
            "x-ves-proto-message",
            "x-displayname",
        ],
    )
    def test_known_preserved_extensions(self, extension: str) -> None:
        """Known F5 native extensions should be in preserved set."""
        assert extension in PRESERVED_NATIVE_EXTENSIONS

    def test_preserved_not_in_migration(self) -> None:
        """Preserved extensions should not be in migration mapping."""
        for ext in PRESERVED_NATIVE_EXTENSIONS:
            assert ext not in FIELD_MIGRATION, f"Preserved extension '{ext}' should not be migrated"


class TestValidExtensions:
    """Tests for valid extension set."""

    def test_valid_extensions_not_empty(self) -> None:
        """Valid extensions set should not be empty."""
        assert len(VALID_X_F5XC_EXTENSIONS) > 0

    def test_all_valid_have_prefix(self) -> None:
        """All valid extensions must have x-f5xc- prefix."""
        for ext in VALID_X_F5XC_EXTENSIONS:
            assert ext.startswith(X_F5XC_PREFIX), f"Valid extension '{ext}' missing prefix"

    def test_migration_targets_are_valid(self) -> None:
        """All migration targets should be valid extensions."""
        for new in FIELD_MIGRATION.values():
            assert new in VALID_X_F5XC_EXTENSIONS, f"Migration target '{new}' not in valid set"

    def test_new_fields_are_valid(self) -> None:
        """New fields should be in valid extensions set."""
        new_fields = [X_F5XC_TERRAFORM_RESOURCE, X_F5XC_DISPLAY_NAME, X_F5XC_DOC_SECTION]
        for field in new_fields:
            assert field in VALID_X_F5XC_EXTENSIONS, f"New field '{field}' not in valid set"


class TestValidationFunctions:
    """Tests for validation utility functions."""

    def test_is_valid_extension_true(self) -> None:
        """Valid extensions should return True."""
        assert is_valid_extension(X_F5XC_CLI_DOMAIN)
        assert is_valid_extension(X_F5XC_DANGER_LEVEL)
        assert is_valid_extension(X_F5XC_TERRAFORM_RESOURCE)

    def test_is_valid_extension_false(self) -> None:
        """Invalid extensions should return False."""
        assert not is_valid_extension("x-ves-cli-domain")  # old name
        assert not is_valid_extension("domain_category")  # non-prefixed
        assert not is_valid_extension("x-random-extension")  # unknown

    def test_is_preserved_native_true(self) -> None:
        """Preserved native extensions should return True."""
        assert is_preserved_native("x-ves-proto-package")
        assert is_preserved_native("x-displayname")

    def test_is_preserved_native_false(self) -> None:
        """Non-native extensions should return False."""
        assert not is_preserved_native(X_F5XC_CLI_DOMAIN)
        assert not is_preserved_native("x-ves-cli-domain")

    def test_is_old_extension_true(self) -> None:
        """Old extensions should return True."""
        assert is_old_extension("x-ves-cli-domain")
        assert is_old_extension("domain_category")
        assert is_old_extension("x-upstream-timestamp")

    def test_is_old_extension_false(self) -> None:
        """New extensions should return False."""
        assert not is_old_extension(X_F5XC_CLI_DOMAIN)
        assert not is_old_extension("x-random-field")

    def test_migrate_field_name_old(self) -> None:
        """Old field names should be migrated."""
        assert migrate_field_name("x-ves-cli-domain") == X_F5XC_CLI_DOMAIN
        # Both old category fields map to the single X_F5XC_CATEGORY (DRY)
        assert migrate_field_name("domain_category") == X_F5XC_CATEGORY
        assert migrate_field_name("ui_category") == X_F5XC_CATEGORY
        assert migrate_field_name("category") == X_F5XC_CATEGORY

    def test_migrate_field_name_unknown(self) -> None:
        """Unknown fields should return unchanged."""
        assert migrate_field_name("unknown-field") == "unknown-field"
        assert migrate_field_name(X_F5XC_CLI_DOMAIN) == X_F5XC_CLI_DOMAIN


class TestValidateNoInvalidExtensions:
    """Tests for the spec validation function."""

    def test_valid_spec_no_errors(self) -> None:
        """Valid spec should have no errors."""
        valid_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                X_F5XC_CLI_DOMAIN: "test",
                X_F5XC_ENRICHED_VERSION: "2.0.0",
            },
            "x-ves-proto-package": "native.field",  # preserved
        }
        errors = validate_no_invalid_extensions(valid_spec)
        assert len(errors) == 0

    def test_old_x_ves_field_error(self) -> None:
        """Old x-ves-* fields should produce errors."""
        spec = {
            "info": {
                "x-ves-cli-domain": "test",  # old field
            },
        }
        errors = validate_no_invalid_extensions(spec)
        assert len(errors) == 1
        assert "x-ves-cli-domain" in errors[0]
        assert "x-f5xc-cli-domain" in errors[0]

    def test_non_prefixed_field_error(self) -> None:
        """Non-prefixed fields should produce errors."""
        spec = {
            "domain_category": "test",  # should be x-f5xc-category (DRY)
        }
        errors = validate_no_invalid_extensions(spec)
        assert len(errors) == 1
        assert "domain_category" in errors[0]
        assert "x-f5xc-category" in errors[0]  # Consolidated category field

    def test_preserved_native_no_error(self) -> None:
        """Preserved native fields should not produce errors."""
        spec = {
            "x-ves-proto-package": "ves.io.schema.test",
            "x-displayname": "Test API",
        }
        errors = validate_no_invalid_extensions(spec)
        assert len(errors) == 0

    def test_nested_errors(self) -> None:
        """Nested invalid fields should be caught."""
        spec = {
            "components": {
                "schemas": {
                    "TestSchema": {
                        "type": "object",
                        "x-ves-minimum-configuration": {},  # old field
                    },
                },
            },
        }
        errors = validate_no_invalid_extensions(spec)
        assert len(errors) == 1
        assert "components.schemas.TestSchema" in errors[0]

    def test_array_nested_errors(self) -> None:
        """Errors in arrays should include index."""
        spec = {
            "tags": [
                {"name": "valid"},
                {"name": "invalid", "x-ves-cli-domain": "test"},
            ],
        }
        errors = validate_no_invalid_extensions(spec)
        assert len(errors) == 1
        assert "[1]" in errors[0]

    def test_unknown_x_extension_error(self) -> None:
        """Unknown x-* extensions should produce errors."""
        spec = {
            "x-random-vendor-field": "value",  # not in our namespace
        }
        errors = validate_no_invalid_extensions(spec)
        assert len(errors) == 1
        assert "x-random-vendor-field" in errors[0]


class TestMigrationCompleteness:
    """Tests to ensure migration mapping is complete."""

    def test_all_x_ves_cli_fields_migrated(self) -> None:
        """All known x-ves-cli-* fields should have migration."""
        expected_x_ves_cli = ["x-ves-cli-domain", "x-ves-cli-aliases"]
        for field in expected_x_ves_cli:
            assert field in FIELD_MIGRATION, f"Missing migration for '{field}'"

    def test_all_index_fields_migrated(self) -> None:
        """All known index.json non-prefixed fields should have migration."""
        expected_index = [
            "domain_category",
            "ui_category",
            "primary_resources",
            "description_short",
            "description_medium",
            "complexity",
            "requires_tier",
            "is_preview",
            "aliases",
            "use_cases",
            "icon",
            "logo_svg",
            "related_domains",
        ]
        for field in expected_index:
            assert field in FIELD_MIGRATION, f"Missing migration for index field '{field}'"

    def test_intentional_dry_consolidation(self) -> None:
        """DRY consolidation: multiple old fields can map to same new field.

        Specifically, domain_category, ui_category, and category all map to
        x-f5xc-category to avoid redundant fields in the spec.
        """
        # All three category fields should map to the same target
        assert FIELD_MIGRATION["domain_category"] == X_F5XC_CATEGORY
        assert FIELD_MIGRATION["ui_category"] == X_F5XC_CATEGORY
        assert FIELD_MIGRATION["category"] == X_F5XC_CATEGORY

        # Verify we have fewer unique targets than source fields (due to consolidation)
        targets = list(FIELD_MIGRATION.values())
        unique_targets = set(targets)
        assert len(unique_targets) < len(targets), (
            "Expected DRY consolidation (fewer targets than sources)"
        )
