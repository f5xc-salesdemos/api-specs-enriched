# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Resource resolver for mapping primary resource names to schema components and API paths.

Uses operationId regex to extract dotted component names from merged domain specs,
then ties path inclusion to schema resolution. Config overrides in resource_metadata.yaml
take precedence over heuristic results.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

OPERATIONID_REGEX = re.compile(r"ves\.io\.schema\.(.+?)\.(?:\w*API)\.")


def _get_all_path_components(domain_paths: dict[str, Any]) -> set[str]:
    """Extract all unique component names from operationIds across all paths."""
    components: set[str] = set()
    for path_item in domain_paths.values():
        for method_item in path_item.values():
            if not isinstance(method_item, dict):
                continue
            match = OPERATIONID_REGEX.match(method_item.get("operationId", ""))
            if match:
                components.add(match.group(1))
    return components


def _operationids_for_path(path_item: dict[str, Any]) -> set[str]:
    """Extract component names from operationIds on a single path item."""
    components: set[str] = set()
    for method_item in path_item.values():
        if not isinstance(method_item, dict):
            continue
        match = OPERATIONID_REGEX.match(method_item.get("operationId", ""))
        if match:
            components.add(match.group(1))
    return components


def resolve_resource(
    name: str,
    domain_paths: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Heuristic resolution. Returns (schema_components, api_paths)."""
    all_domain_components = _get_all_path_components(domain_paths)

    matching_components: list[str] = []
    for comp in sorted(all_domain_components):
        last_segment = comp.rsplit(".", 1)[-1]
        if name in (last_segment, comp):
            matching_components.append(comp)

    if not matching_components:
        return [], []

    matching_set = set(matching_components)
    plural = f"{name}s"

    matched_paths: list[str] = []
    for path_str, path_item in domain_paths.items():
        segments = path_str.split("/")
        if name not in segments and plural not in segments:
            continue
        path_components = _operationids_for_path(path_item)
        if path_components & matching_set:
            matched_paths.append(path_str)

    return matching_components, sorted(matched_paths)


def apply_overrides(
    heuristic: tuple[list[str], list[str]],
    config_entry: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Apply config overrides to a heuristic result."""
    schema_components = config_entry.get("schema_components", heuristic[0])
    api_paths = config_entry.get("api_paths", heuristic[1])
    if not isinstance(schema_components, list):
        raise TypeError(f"schema_components must be a list, got {type(schema_components).__name__}")
    if not isinstance(api_paths, list):
        raise TypeError(f"api_paths must be a list, got {type(api_paths).__name__}")
    return schema_components, api_paths


def validate_resource_mappings(
    heuristic_results: dict[str, tuple[list[str], list[str]]],
    config_overrides: dict[str, dict[str, Any]],
    domain_paths: dict[str, Any],
    domain: str,
) -> list[str]:
    """Validate config overrides against the domain's actual operationIds and paths."""
    errors: list[str] = []
    all_components = _get_all_path_components(domain_paths)

    for resource_name, override_entry in config_overrides.items():
        heuristic = heuristic_results.get(resource_name, ([], []))

        if "schema_components" in override_entry:
            entries = override_entry["schema_components"]
            if not isinstance(entries, list):
                errors.append(
                    f"resource '{resource_name}': schema_components must be a list, "
                    f"got {type(entries).__name__}"
                )
                continue
            if entries:
                errors.extend(
                    f"resource '{resource_name}': schema_component '{comp}' "
                    f"not found in domain '{domain}' operationIds"
                    for comp in entries
                    if comp not in all_components
                )
                if heuristic[0] and set(entries) != set(heuristic[0]):
                    logger.warning(
                        "resource '%s': config schema_components override replaces "
                        "heuristic result — entry may be redundant",
                        resource_name,
                    )

        if "api_paths" in override_entry:
            entries = override_entry["api_paths"]
            if not isinstance(entries, list):
                errors.append(
                    f"resource '{resource_name}': api_paths must be a list, "
                    f"got {type(entries).__name__}"
                )
                continue
            if entries:
                errors.extend(
                    f"resource '{resource_name}': api_path '{path}' "
                    f"not found in domain '{domain}' paths"
                    for path in entries
                    if path not in domain_paths
                )
                if heuristic[1] and set(entries) != set(heuristic[1]):
                    logger.warning(
                        "resource '%s': config api_paths override replaces "
                        "heuristic result — entry may be redundant",
                        resource_name,
                    )

    return errors
