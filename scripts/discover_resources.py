# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Discover unresolvable resources and print candidate components for manual annotation.

Loads merged specs from docs/specifications/api/. Run this before populating
config/resource_metadata.yaml to see which resources need manual entries.

Usage: PYTHONPATH=. python scripts/discover_resources.py
"""

import json
import sys
from pathlib import Path

from scripts.utils.domain_metadata import DOMAIN_PRIMARY_RESOURCES, _load_resource_metadata
from scripts.utils.resource_resolver import _get_all_path_components, resolve_resource


def main() -> None:
    """Print unresolvable resources with candidate components."""
    specs_dir = Path(__file__).parent.parent / "docs" / "specifications" / "api"
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
            print("  heuristic: empty (no operationId match)")
            print("  candidate components from domain operationIds:")
            for comp in all_components[:8]:
                print(f"    - {comp}")
            if len(all_components) > 8:
                print(f"    ... ({len(all_components) - 8} more)")
            print("  stub:")
            print(f"    {name}:")
            print("      schema_components: []  # fill in from candidates above")
            print("      api_paths: []          # fill in matching path patterns")
    print(f"\n# Total unresolvable resources: {unresolvable_count}")


if __name__ == "__main__":
    main()
    sys.exit(0)
