# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Resource resolver for mapping primary resource names to schema components and API paths.

Uses operationId regex to extract dotted component names from merged domain specs,
then ties path inclusion to schema resolution. Config overrides in resource_metadata.yaml
take precedence over heuristic results.
"""

import json
import logging
import re
import sys
from pathlib import Path
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
        if last_segment == name or comp == name:
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
        raise TypeError(
            f"schema_components must be a list, got {type(schema_components).__name__}"
        )
    if not isinstance(api_paths, list):
        raise TypeError(
            f"api_paths must be a list, got {type(api_paths).__name__}"
        )
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
            if not entries:
                pass
            else:
                for comp in entries:
                    if comp not in all_components:
                        errors.append(
                            f"resource '{resource_name}': schema_component '{comp}' "
                            f"not found in domain '{domain}' operationIds"
                        )
                if heuristic[0] and set(override_entry["schema_components"]) != set(heuristic[0]):
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
            if not entries:
                pass
            else:
                for path in entries:
                    if path not in domain_paths:
                        errors.append(
                            f"resource '{resource_name}': api_path '{path}' "
                            f"not found in domain '{domain}' paths"
                        )
                if heuristic[1] and set(override_entry["api_paths"]) != set(heuristic[1]):
                    logger.warning(
                        "resource '%s': config api_paths override replaces "
                        "heuristic result — entry may be redundant",
                        resource_name,
                    )

    return errors


def _dry_run_discovery() -> None:
    """Print unresolvable resources with candidate components."""
    specs_dir = Path(__file__).parent.parent.parent / "docs" / "specifications" / "api"
    from scripts.utils.domain_metadata import DOMAIN_PRIMARY_RESOURCES, _load_resource_metadata  # noqa: PLC0415
    resource_config = _load_resource_metadata()
    unresolvable_count = 0

    for domain, resource_names in sorted(DOMAIN_PRIMARY_RESOURCES.items()):
        spec_file = specs_dir / f"{domain}.json"
        if not spec_file.exists():
            print(f"# SKIP: {domain}.json not found (run make all first)", flush=True)
            continue
        with spec_file.open() as f:
            spec = json.load(f)
        domain_paths = spec.get("paths", {})
        all_components = sorted(_get_all_path_components(domain_paths))
        for name in resource_names:
            entry = resource_config.get(name, {})
            if "schema_components" in entry or "api_paths" in entry:
                continue
            schema_comps, _ = resolve_resource(name, domain_paths)
            if schema_comps:
                continue
            unresolvable_count += 1
            print(f"\ndomain: {domain}")
            print(f"resource: {name}")
            print(f"  heuristic: empty (no operationId match)")
            print(f"  candidate components from domain operationIds:")
            for comp in all_components[:8]:
                print(f"    - {comp}")
            if len(all_components) > 8:
                print(f"    ... ({len(all_components) - 8} more)")
            print(f"  stub:")
            print(f"    {name}:")
            print(f"      schema_components: []  # fill in from candidates above")
            print(f"      api_paths: []          # fill in matching path patterns")
    print(f"\n# Total unresolvable resources: {unresolvable_count}")


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        _dry_run_discovery()
    else:
        print("Usage: python scripts/utils/resource_resolver.py --dry-run")
        sys.exit(1)
