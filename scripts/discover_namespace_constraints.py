"""Discover namespace constraints by probing the live F5 XC API.

Outputs a YAML report showing which namespace types each resource
accepts or rejects. Run manually, review output, update namespace_profile.yaml.

Requires: F5XC_API_URL and F5XC_API_TOKEN environment variables.

Usage:
    python scripts/discover_namespace_constraints.py [--output discovery_report.yaml]
    python scripts/discover_namespace_constraints.py --diff config/namespace_profile.yaml
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests
import yaml

NAMESPACE_TYPES_TO_TEST = ["system", "shared", "default"]


def get_api_client() -> tuple[str, dict[str, str]]:
    """Return (base_url, headers) for the F5 XC API."""
    url = os.environ.get("F5XC_API_URL", "")
    token = os.environ.get("F5XC_API_TOKEN", "")
    if not url or not token:
        print("Error: F5XC_API_URL and F5XC_API_TOKEN must be set", file=sys.stderr)
        sys.exit(1)
    headers = {"Authorization": f"APIToken {token}", "Content-Type": "application/json"}
    return url.rstrip("/"), headers


def list_resource_types_from_specs(specs_dir: Path) -> list[dict[str, str]]:
    """Extract resource types and their API paths from enriched specs."""
    resources = []
    index_path = specs_dir / "index.json"
    if not index_path.exists():
        print(f"Error: {index_path} not found", file=sys.stderr)
        sys.exit(1)

    with index_path.open() as f:
        index = json.load(f)

    specs = index.get("specifications", [])
    if isinstance(specs, dict):
        specs = specs.values()
    for domain_info in specs:
        for resource in domain_info.get("x-f5xc-primary-resources", []):
            name = resource.get("name", "")
            api_paths = resource.get("api_paths", [])
            if isinstance(api_paths, dict):
                list_path = api_paths.get("list", "")
            elif isinstance(api_paths, list) and api_paths:
                list_path = api_paths[0]
            else:
                list_path = ""
            if name and list_path:
                resources.append({"name": name, "list_path": list_path})
    return resources


def probe_namespace(
    base_url: str,
    headers: dict[str, str],
    list_path: str,
    namespace: str,
) -> dict[str, Any]:
    """Try a GET request against a resource in a specific namespace."""
    url = f"{base_url}{list_path}".replace("{namespace}", namespace)
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        return {
            "status": resp.status_code,
            "allowed": resp.status_code in (200, 404),
            "error": resp.json().get("message", "") if resp.status_code >= 400 else "",
        }
    except Exception as e:
        return {"status": 0, "allowed": False, "error": str(e)}


def discover_all(specs_dir: Path) -> dict[str, Any]:
    """Probe all resources across all namespace types."""
    base_url, headers = get_api_client()
    resources = list_resource_types_from_specs(specs_dir)
    results: dict[str, Any] = {}

    print(f"Discovering namespace constraints for {len(resources)} resources...")
    for i, resource in enumerate(resources):
        name = resource["name"]
        print(f"  [{i + 1}/{len(resources)}] {name}", end=" ")
        results[name] = {"allowed": [], "denied": []}
        for ns_type in NAMESPACE_TYPES_TO_TEST:
            probe = probe_namespace(base_url, headers, resource["list_path"], ns_type)
            if probe["allowed"]:
                results[name]["allowed"].append(ns_type)
                print(f"+{ns_type}", end=" ")
            else:
                results[name]["denied"].append(ns_type)
                print(f"-{ns_type}", end=" ")
        # Infer custom namespace: if any non-system namespace is allowed, custom is likely allowed
        non_system_allowed = [ns for ns in results[name]["allowed"] if ns != "system"]
        if non_system_allowed:
            results[name]["allowed"].append("custom")
        print()

    return results


def diff_with_config(discovery: dict[str, Any], config_path: Path) -> list[str]:
    """Compare discovery results against current config and report differences."""
    with config_path.open() as f:
        config = yaml.safe_load(f)

    default_allowed = config["default_profile"]["constraint"]["allowed"]
    diffs = []

    for name, result in discovery.items():
        resource_config = config.get("resources", {}).get(name, {})
        config_allowed = resource_config.get("constraint", {}).get("allowed", default_allowed)
        discovered_allowed = sorted(result["allowed"])
        if sorted(config_allowed) != discovered_allowed:
            diffs.append(
                f"DRIFT: {name} — config={sorted(config_allowed)}, discovered={discovered_allowed}"
            )

    return diffs


def main() -> None:
    """Run namespace constraint discovery and generate a report."""
    parser = argparse.ArgumentParser(description="Discover F5 XC namespace constraints")
    parser.add_argument(
        "--specs-dir", default="docs/specifications/api", help="Enriched specs directory"
    )
    parser.add_argument("--output", default="discovery_report.yaml", help="Output report path")
    parser.add_argument("--diff", metavar="CONFIG", help="Diff discovery against config file")
    args = parser.parse_args()

    specs_dir = Path(args.specs_dir)
    results = discover_all(specs_dir)

    with Path(args.output).open("w") as f:
        yaml.dump(results, f, default_flow_style=False, sort_keys=True)
    print(f"\nReport written to {args.output}")

    if args.diff:
        diffs = diff_with_config(results, Path(args.diff))
        if diffs:
            print(f"\n{len(diffs)} drift(s) found:")
            for d in diffs:
                print(f"  {d}")
        else:
            print("\nNo drift found — config matches discovery.")


if __name__ == "__main__":
    main()
