# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Integration tests for resource resolution against real domain specs (Issue #252).

These tests load actual merged specs from docs/specifications/api/. Run
`make all` first to generate the spec files.
"""

import json
import logging
from pathlib import Path

import pytest

from scripts.utils.domain_metadata import DOMAIN_PRIMARY_RESOURCES, get_primary_resources_metadata
from scripts.utils.resource_resolver import (
    resolve_resource,
    validate_resource_mappings,
)

SPECS_DIR = Path(__file__).parent.parent / "docs" / "specifications" / "api"


def load_spec(domain: str) -> dict | None:
    """Load merged spec for a domain. Returns None if not found."""
    spec_file = SPECS_DIR / f"{domain}.json"
    if not spec_file.exists():
        return None
    return json.loads(spec_file.read_text())


@pytest.fixture(scope="module")
def all_domain_specs() -> dict:
    """Load all available domain specs. Skip domains with no spec file."""
    specs = {}
    for domain in DOMAIN_PRIMARY_RESOURCES:
        spec = load_spec(domain)
        if spec is not None:
            specs[domain] = spec
    if not specs:
        pytest.skip("No domain specs found — run `make all` first")
    return specs


class TestAllResourcesResolve:
    """Every primary resource must have schema_components and api_paths."""

    def test_all_resources_have_mapping_fields(self, all_domain_specs):
        """After resolution, no resource is missing schema_components or api_paths."""
        problems: list[str] = []
        for domain, spec in all_domain_specs.items():
            resources = get_primary_resources_metadata(domain, spec=spec)
            for r in resources:
                if "schema_components" not in r:
                    problems.append(f"{domain}/{r['name']}: missing schema_components")
                if "api_paths" not in r:
                    problems.append(f"{domain}/{r['name']}: missing api_paths")

        assert not problems, "Resources missing mapping fields:\n" + "\n".join(problems)

    def test_resolved_resources_are_lists(self, all_domain_specs):
        """schema_components and api_paths must always be lists (never None)."""
        for domain, spec in all_domain_specs.items():
            resources = get_primary_resources_metadata(domain, spec=spec)
            for r in resources:
                assert isinstance(r.get("schema_components"), list), (
                    f"{domain}/{r['name']}: schema_components is not a list"
                )
                assert isinstance(r.get("api_paths"), list), (
                    f"{domain}/{r['name']}: api_paths is not a list"
                )


class TestAutoResolvePartition:
    """Dynamically verify the heuristic/manual partition is consistent."""

    def test_manual_resources_have_config_overrides(self, all_domain_specs):
        """Every resource where heuristic returns empty must have a config entry."""
        from scripts.utils.domain_metadata import _load_resource_metadata

        resource_config = _load_resource_metadata()
        needs_config: list[str] = []
        has_config: list[str] = []
        auto_resolves: list[str] = []

        for domain, spec in all_domain_specs.items():
            domain_paths = spec.get("paths", {})
            for name in DOMAIN_PRIMARY_RESOURCES.get(domain, []):
                schema_comps, _ = resolve_resource(name, domain_paths)
                if schema_comps:
                    auto_resolves.append(f"{domain}/{name}")
                else:
                    entry = resource_config.get(name, {})
                    if "schema_components" in entry or "api_paths" in entry:
                        has_config.append(f"{domain}/{name}")
                    else:
                        needs_config.append(f"{domain}/{name}")

        logging.getLogger(__name__).info(
            "Resolution partition: %d auto-resolve, %d manual config, %d need config",
            len(auto_resolves),
            len(has_config),
            len(needs_config),
        )

        assert not needs_config, (
            "Resources need manual config entry in resource_metadata.yaml:\n"
            + "\n".join(needs_config)
        )

    def test_manual_resources_need_config_not_heuristic(self, all_domain_specs):
        """Resources with config overrides should NOT auto-resolve via heuristic."""
        from scripts.utils.domain_metadata import _load_resource_metadata

        resource_config = _load_resource_metadata()
        redundant: list[str] = []

        for domain, spec in all_domain_specs.items():
            domain_paths = spec.get("paths", {})
            for name in DOMAIN_PRIMARY_RESOURCES.get(domain, []):
                entry = resource_config.get(name, {})
                has_override = "schema_components" in entry or "api_paths" in entry
                if not has_override:
                    continue

                schema_comps, _ = resolve_resource(name, domain_paths)
                if schema_comps:
                    redundant.append(f"{domain}/{name} (heuristic now finds: {schema_comps})")

        if redundant:
            logging.getLogger(__name__).warning(
                "Config overrides may be redundant (heuristic now resolves these):\n%s",
                "\n".join(redundant),
            )


class TestAllOverridesValidAgainstSpec:
    """All config overrides must reference valid components and paths."""

    def test_overrides_valid_against_current_spec(self, all_domain_specs):
        """validate_resource_mappings must pass for every domain."""
        from scripts.utils.domain_metadata import _load_resource_metadata

        resource_config = _load_resource_metadata()
        all_errors: list[str] = []

        for domain, spec in all_domain_specs.items():
            domain_paths = spec.get("paths", {})
            resource_names = DOMAIN_PRIMARY_RESOURCES.get(domain, [])

            heuristic_results = {
                name: resolve_resource(name, domain_paths) for name in resource_names
            }
            config_overrides = {
                name: resource_config[name]
                for name in resource_names
                if name in resource_config
                and (
                    "schema_components" in resource_config[name]
                    or "api_paths" in resource_config[name]
                )
                and not heuristic_results[name][0]
            }

            errors = validate_resource_mappings(
                heuristic_results, config_overrides, domain_paths, domain
            )
            all_errors.extend(f"[{domain}] {err}" for err in errors)

        assert not all_errors, (
            "Config overrides reference invalid components or paths:\n" + "\n".join(all_errors)
        )
