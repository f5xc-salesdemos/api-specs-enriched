"""Centralized constants for x-f5xc-* OpenAPI extension namespace.

This module provides:
1. Unified namespace prefix for all enrichment extensions
2. Field name constants to avoid string duplication
3. Migration mapping from old field names to new
4. Validation utilities for extension compliance

All enrichment code should import field names from this module
rather than using hardcoded strings.

Issue: #292
"""

from __future__ import annotations

# =============================================================================
# NAMESPACE PREFIX
# =============================================================================

X_F5XC_PREFIX = "x-f5xc-"

# =============================================================================
# SPEC-LEVEL EXTENSIONS (info section)
# =============================================================================

X_F5XC_CLI_DOMAIN = "x-f5xc-cli-domain"
X_F5XC_UPSTREAM_TIMESTAMP = "x-f5xc-upstream-timestamp"
X_F5XC_UPSTREAM_ETAG = "x-f5xc-upstream-etag"
X_F5XC_ENRICHED_VERSION = "x-f5xc-enriched-version"

# =============================================================================
# SCHEMA-LEVEL EXTENSIONS (component schemas)
# =============================================================================

X_F5XC_CLI_ALIASES = "x-f5xc-cli-aliases"
X_F5XC_MINIMUM_CONFIGURATION = "x-f5xc-minimum-configuration"
X_F5XC_NAMESPACE_SCOPE = "x-f5xc-namespace-scope"
X_F5XC_DISPLAYORDER = "x-f5xc-displayorder"
X_F5XC_TERRAFORM_RESOURCE = "x-f5xc-terraform-resource"
X_F5XC_DISPLAY_NAME = "x-f5xc-display-name"

# =============================================================================
# PROPERTY-LEVEL EXTENSIONS (schema properties)
# =============================================================================

X_F5XC_DESCRIPTION = "x-f5xc-description"
X_F5XC_VALIDATION = "x-f5xc-validation"
X_F5XC_EXAMPLES = "x-f5xc-examples"
X_F5XC_EXAMPLE = "x-f5xc-example"
X_F5XC_COMPLETION = "x-f5xc-completion"
X_F5XC_DEFAULTS = "x-f5xc-defaults"
X_F5XC_REQUIRED_FOR_OPERATIONS = "x-f5xc-required-for-operations"
X_F5XC_REQUIRED_FOR = "x-f5xc-required-for"
X_F5XC_CONDITIONS = "x-f5xc-conditions"
X_F5XC_DEPRECATED = "x-f5xc-deprecated"

# =============================================================================
# OPERATION-LEVEL EXTENSIONS (path operations)
# =============================================================================

X_F5XC_REQUIRED_FIELDS = "x-f5xc-required-fields"
X_F5XC_DANGER_LEVEL = "x-f5xc-danger-level"
X_F5XC_CONFIRMATION_REQUIRED = "x-f5xc-confirmation-required"
X_F5XC_SIDE_EFFECTS = "x-f5xc-side-effects"

# =============================================================================
# INDEX-LEVEL EXTENSIONS (index.json metadata)
# =============================================================================

# Single category field for CLI, UI, docs, and Terraform grouping (DRY)
X_F5XC_CATEGORY = "x-f5xc-category"
X_F5XC_PRIMARY_RESOURCES = "x-f5xc-primary-resources"
X_F5XC_PRIMARY_RESOURCES_SIMPLE = "x-f5xc-primary-resources-simple"
X_F5XC_CRITICAL_RESOURCES = "x-f5xc-critical-resources"
X_F5XC_DESCRIPTION_SHORT = "x-f5xc-description-short"
X_F5XC_DESCRIPTION_MEDIUM = "x-f5xc-description-medium"
X_F5XC_COMPLEXITY = "x-f5xc-complexity"
X_F5XC_REQUIRES_TIER = "x-f5xc-requires-tier"
X_F5XC_IS_PREVIEW = "x-f5xc-is-preview"
X_F5XC_ALIASES = "x-f5xc-aliases"
X_F5XC_USE_CASES = "x-f5xc-use-cases"
X_F5XC_ICON = "x-f5xc-icon"
X_F5XC_LOGO_SVG = "x-f5xc-logo-svg"
X_F5XC_RELATED_DOMAINS = "x-f5xc-related-domains"
X_F5XC_DOC_SECTION = "x-f5xc-doc-section"

# =============================================================================
# F5 NATIVE EXTENSIONS TO PRESERVE (DO NOT MODIFY)
# =============================================================================

PRESERVED_NATIVE_EXTENSIONS = frozenset(
    [
        "x-ves-proto-package",
        "x-ves-proto-file",
        "x-ves-proto-message",
        "x-ves-proto-service",
        "x-ves-proto-rpc",
        "x-displayname",
        "x-ves-oneof",
        "x-ves-default",
        "x-ves-required",
    ],
)

# =============================================================================
# MIGRATION MAPPING (old field -> new field)
# =============================================================================

FIELD_MIGRATION: dict[str, str] = {
    # Spec-level
    "x-ves-cli-domain": X_F5XC_CLI_DOMAIN,
    "x-upstream-timestamp": X_F5XC_UPSTREAM_TIMESTAMP,
    "x-upstream-etag": X_F5XC_UPSTREAM_ETAG,
    "x-enriched-version": X_F5XC_ENRICHED_VERSION,
    # Schema-level
    "x-ves-cli-aliases": X_F5XC_CLI_ALIASES,
    "x-ves-minimum-configuration": X_F5XC_MINIMUM_CONFIGURATION,
    "x-ves-namespace-scope": X_F5XC_NAMESPACE_SCOPE,
    "x-ves-displayorder": X_F5XC_DISPLAYORDER,
    # Property-level
    "x-ves-description": X_F5XC_DESCRIPTION,
    "x-ves-validation": X_F5XC_VALIDATION,
    "x-ves-examples": X_F5XC_EXAMPLES,
    "x-ves-example": X_F5XC_EXAMPLE,
    "x-ves-completion": X_F5XC_COMPLETION,
    "x-ves-defaults": X_F5XC_DEFAULTS,
    "x-ves-required-for-operations": X_F5XC_REQUIRED_FOR_OPERATIONS,
    "x-ves-required-for": X_F5XC_REQUIRED_FOR,
    "x-ves-conditions": X_F5XC_CONDITIONS,
    "x-ves-deprecated": X_F5XC_DEPRECATED,
    # Operation-level
    "x-ves-required-fields": X_F5XC_REQUIRED_FIELDS,
    "x-ves-danger-level": X_F5XC_DANGER_LEVEL,
    "x-ves-confirmation-required": X_F5XC_CONFIRMATION_REQUIRED,
    "x-ves-side-effects": X_F5XC_SIDE_EFFECTS,
    # Index-level (non-prefixed to prefixed)
    # Single category field replaces both domain_category and ui_category (DRY)
    "domain_category": X_F5XC_CATEGORY,
    "ui_category": X_F5XC_CATEGORY,
    "category": X_F5XC_CATEGORY,
    "primary_resources": X_F5XC_PRIMARY_RESOURCES,
    "primary_resources_simple": X_F5XC_PRIMARY_RESOURCES_SIMPLE,
    "x-ves-critical-resources": X_F5XC_CRITICAL_RESOURCES,
    "description_short": X_F5XC_DESCRIPTION_SHORT,
    "description_medium": X_F5XC_DESCRIPTION_MEDIUM,
    "complexity": X_F5XC_COMPLEXITY,
    "requires_tier": X_F5XC_REQUIRES_TIER,
    "is_preview": X_F5XC_IS_PREVIEW,
    "aliases": X_F5XC_ALIASES,
    "use_cases": X_F5XC_USE_CASES,
    "icon": X_F5XC_ICON,
    "logo_svg": X_F5XC_LOGO_SVG,
    "related_domains": X_F5XC_RELATED_DOMAINS,
}

# Reverse mapping for validation
FIELD_MIGRATION_REVERSE: dict[str, str] = {v: k for k, v in FIELD_MIGRATION.items()}

# All valid x-f5xc-* extension names
VALID_X_F5XC_EXTENSIONS = frozenset(FIELD_MIGRATION.values()) | {
    X_F5XC_TERRAFORM_RESOURCE,
    X_F5XC_DISPLAY_NAME,
    X_F5XC_DOC_SECTION,
    X_F5XC_PRIMARY_RESOURCES_SIMPLE,
    X_F5XC_CRITICAL_RESOURCES,
}


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================


def is_valid_extension(field_name: str) -> bool:
    """Check if a field name is a valid x-f5xc-* extension.

    Args:
        field_name: The field name to validate

    Returns:
        True if the field is a valid x-f5xc-* extension
    """
    return field_name in VALID_X_F5XC_EXTENSIONS


def is_preserved_native(field_name: str) -> bool:
    """Check if a field is an F5 native extension that must be preserved.

    Args:
        field_name: The field name to check

    Returns:
        True if the field is a preserved F5 native extension
    """
    return field_name in PRESERVED_NATIVE_EXTENSIONS


def is_old_extension(field_name: str) -> bool:
    """Check if a field name is an old extension that needs migration.

    Args:
        field_name: The field name to check

    Returns:
        True if the field should be migrated to x-f5xc-* namespace
    """
    return field_name in FIELD_MIGRATION


def migrate_field_name(old_name: str) -> str:
    """Get the new x-f5xc-* field name for an old field.

    Args:
        old_name: The old field name

    Returns:
        The new x-f5xc-* field name, or the original if no migration needed
    """
    return FIELD_MIGRATION.get(old_name, old_name)


def validate_no_invalid_extensions(obj: dict, path: str = "") -> list[str]:
    """Validate that an object contains no invalid custom extensions.

    Checks that all custom fields (x-* or non-standard) are either:
    - Valid x-f5xc-* extensions
    - Preserved F5 native extensions
    - Standard OpenAPI fields

    Args:
        obj: Dictionary to validate
        path: Current path for error reporting

    Returns:
        List of validation errors (empty if valid)
    """
    errors: list[str] = []

    # Standard OpenAPI fields that are allowed
    standard_fields = {
        "openapi",
        "info",
        "servers",
        "paths",
        "components",
        "security",
        "tags",
        "externalDocs",
        "title",
        "description",
        "version",
        "termsOfService",
        "contact",
        "license",
        "name",
        "url",
        "email",
        "schemas",
        "responses",
        "parameters",
        "examples",
        "requestBodies",
        "headers",
        "securitySchemes",
        "links",
        "callbacks",
        "type",
        "properties",
        "items",
        "required",
        "enum",
        "default",
        "format",
        "minimum",
        "maximum",
        "minLength",
        "maxLength",
        "pattern",
        "additionalProperties",
        "allOf",
        "anyOf",
        "oneOf",
        "not",
        "$ref",
        "nullable",
        "readOnly",
        "writeOnly",
        "deprecated",
        "example",
        "summary",
        "operationId",
        "requestBody",
        "in",
        "schema",
        "content",
        "variables",
    }

    for key, value in obj.items():
        current_path = f"{path}.{key}" if path else key

        # Check if this is a custom field
        if key.startswith("x-"):
            # Must be either x-f5xc-* or preserved native
            if not (is_valid_extension(key) or is_preserved_native(key)):
                # Check if it's an old field that should have been migrated
                if is_old_extension(key):
                    new_name = migrate_field_name(key)
                    errors.append(
                        f"{current_path}: Old extension '{key}' should be migrated to '{new_name}'",
                    )
                else:
                    errors.append(
                        f"{current_path}: Invalid extension '{key}' (not in x-f5xc-* namespace)",
                    )
        elif key not in standard_fields and not key.startswith("$") and is_old_extension(key):
            # Non-standard field without x- prefix in index.json context
            new_name = migrate_field_name(key)
            errors.append(
                f"{current_path}: Non-standard field '{key}' should be migrated to '{new_name}'",
            )

        # Recursively check nested objects
        if isinstance(value, dict):
            errors.extend(validate_no_invalid_extensions(value, current_path))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    errors.extend(validate_no_invalid_extensions(item, f"{current_path}[{i}]"))

    return errors
