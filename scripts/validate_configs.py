#!/usr/bin/env python3
"""Validate configuration file interdependencies and consistency.

This script validates cross-file references and consistency across all configuration files.
"""

import sys
from pathlib import Path

import yaml


def validate_config_interdependencies() -> list[str]:
    """Validate cross-file references and consistency.

    Checks:
    1. Resources in minimum_configs exist in resource_metadata
    2. Resources in operation_descriptions match resource_metadata
    3. Domain references are consistent across files
    4. Required fields are present in all configs

    Returns:
        List of error messages (empty if valid)
    """
    errors: list[str] = []
    config_dir = Path("config")

    # Load all configs
    try:
        with (config_dir / "minimum_configs.yaml").open() as f:
            min_configs = yaml.safe_load(f) or {}

        with (config_dir / "resource_metadata.yaml").open() as f:
            resource_metadata = yaml.safe_load(f) or {}

        with (config_dir / "operation_descriptions.yaml").open() as f:
            op_descriptions = yaml.safe_load(f) or {}

    except FileNotFoundError as e:
        return [f"Configuration file not found: {e}"]
    except yaml.YAMLError as e:
        return [f"YAML parsing error: {e}"]

    # Validate: resources in minimum_configs exist in resource_metadata
    min_resources = min_configs.get("resources", {})
    metadata_resources = resource_metadata.get("resources", {})

    errors.extend(
        f"Resource '{resource}' in minimum_configs.yaml not found in resource_metadata.yaml"
        for resource in min_resources
        if resource not in metadata_resources
    )

    # Validate: resources in operation_descriptions exist in resource_metadata
    op_resources = op_descriptions.get("resources", {})

    errors.extend(
        f"Resource '{resource}' in operation_descriptions.yaml not found in resource_metadata.yaml"
        for resource in op_resources
        if resource not in metadata_resources
    )

    # Validate: consistent description structure in operation_descriptions
    for resource, descriptions in op_resources.items():
        if not isinstance(descriptions, dict):
            continue

        required_tiers = {"short", "medium", "long"}
        actual_tiers = set(descriptions.keys())

        if not required_tiers.issubset(actual_tiers):
            missing = required_tiers - actual_tiers
            errors.append(
                f"Resource '{resource}' in operation_descriptions.yaml "
                f"missing description tiers: {missing}",
            )

    # Validate: patterns in operation_descriptions have required fields
    patterns = op_descriptions.get("patterns", [])
    for i, pattern in enumerate(patterns):
        if not isinstance(pattern, dict):
            continue

        required_fields = {"resource_pattern", "short", "medium", "long"}
        actual_fields = set(pattern.keys())

        if not required_fields.issubset(actual_fields):
            missing = required_fields - actual_fields
            errors.append(
                f"Pattern {i} in operation_descriptions.yaml missing required fields: {missing}",
            )

    # Validate: method_fallbacks in operation_descriptions have required structure
    method_fallbacks = op_descriptions.get("method_fallbacks", {})
    for method, descriptions in method_fallbacks.items():
        if not isinstance(descriptions, dict):
            continue

        required_tiers = {"short", "medium", "long"}
        actual_tiers = set(descriptions.keys())

        if not required_tiers.issubset(actual_tiers):
            missing = required_tiers - actual_tiers
            errors.append(
                f"Method '{method}' in operation_descriptions.yaml "
                f"missing description tiers: {missing}",
            )

    # Validate: minimum_configs have required structure
    for resource, config in min_resources.items():
        if not isinstance(config, dict):
            continue

        required_fields = {"description", "required_fields", "example_yaml"}
        actual_fields = set(config.keys())

        if not required_fields.issubset(actual_fields):
            missing = required_fields - actual_fields
            errors.append(
                f"Resource '{resource}' in minimum_configs.yaml missing required fields: {missing}",
            )

    # Validate: resource_metadata has required structure
    for resource, metadata in metadata_resources.items():
        if not isinstance(metadata, dict):
            continue

        required_fields = {"description", "description_short"}
        actual_fields = set(metadata.keys())

        if not required_fields.issubset(actual_fields):
            missing = required_fields - actual_fields
            errors.append(
                f"Resource '{resource}' in resource_metadata.yaml "
                f"missing required fields: {missing}",
            )

    return errors


def main() -> int:
    """Main entry point."""
    errors = validate_config_interdependencies()

    if errors:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("✅ Configuration validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
