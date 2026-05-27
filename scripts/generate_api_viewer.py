#!/usr/bin/env python3
# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Generate API catalog page and starlight-openapi plugin configuration.

Reads docs/specifications/api/index.json and generates:
    - docs/api-reference/index.mdx        (catalog landing page)
    - docs/openapi-specs-config.json       (starlight-openapi plugin config)

Usage:
    python -m scripts.generate_api_viewer
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

SPEC_DIR = Path("docs/specifications/api")
MDX_DIR = Path("docs/api-reference")
INDEX_JSON = SPEC_DIR / "index.json"
OPENAPI_CONFIG_PATH = Path("docs/openapi-specs-config.json")


def generate_openapi_specs_config(specs: list[dict]) -> str:
    """Generate the starlight-openapi plugin configuration JSON."""
    config = []
    for spec in specs:
        domain = spec["domain"]
        title = spec["title"]
        if spec.get("path_count", 0) == 0:
            continue
        config.append(
            {
                "base": f"api-reference/{domain}",
                "schema": f"public/specifications/api/{domain}.json",
                "sidebar": {
                    "label": title,
                    "collapsed": True,
                },
            },
        )
    return json.dumps(config, indent=2) + "\n"


def generate_catalog_mdx(
    specs: list[dict],
) -> str:
    """Generate the API Reference catalog landing page."""
    categories: dict[str, list[dict]] = defaultdict(list)
    for spec in specs:
        cat = spec.get("x-f5xc-category", "Other")
        categories[cat].append(spec)

    category_order = [
        "Security",
        "Networking",
        "Infrastructure",
        "Platform",
        "Operations",
        "AI",
        "Other",
    ]

    cards_sections = []
    for cat in category_order:
        if cat not in categories:
            continue
        domain_list = sorted(categories[cat], key=lambda s: s["title"])

        cards = []
        for spec in domain_list:
            domain = spec["domain"]
            title = spec["title"]
            icon = spec.get("x-f5xc-icon", "")
            short_desc = spec.get("x-f5xc-description-short", "")
            complexity = spec.get("x-f5xc-complexity", "")
            path_count = spec.get("path_count", 0)
            schema_count = spec.get("schema_count", 0)

            badge = ""
            if spec.get("x-f5xc-is-preview"):
                badge = " (Preview)"

            description_line = short_desc or title
            stats_line = f"{path_count} paths, {schema_count} schemas"
            if complexity:
                stats_line += f", {complexity}"

            cards.append(
                f'  <LinkCard title="{icon} {title}{badge}" '
                f'description="{description_line} — {stats_line}" '
                f'href="./{domain}/" />',
            )

        cards_block = "\n".join(cards)
        cards_sections.append(f"### {cat}\n\n<CardGrid>\n{cards_block}\n</CardGrid>")

    all_sections = "\n\n".join(cards_sections)

    return f"""---
title: API Reference
description: API documentation for F5 Distributed Cloud services
tableOfContents: false
sidebar:
    order: 0
---

import {{ CardGrid, LinkCard }} from '@astrojs/starlight/components';

Explore the F5 Distributed Cloud API documentation. Each domain includes
endpoint details, request and response schemas, and code examples.

{all_sections}
"""


def main() -> int:
    """Generate catalog page and plugin configuration."""
    if not INDEX_JSON.exists():
        print(f"Error: {INDEX_JSON} not found. Run 'make pipeline' first.")
        return 1

    with INDEX_JSON.open() as f:
        index = json.load(f)

    specs = index.get("specifications", [])
    if not specs:
        print("Error: No specifications found in index.json")
        return 1

    MDX_DIR.mkdir(parents=True, exist_ok=True)

    # Remove stale domain MDX wrappers from previous iframe-based approach
    valid_domains = {spec["domain"] for spec in specs}
    for stale in MDX_DIR.glob("*.mdx"):
        if stale.stem != "index" and stale.stem not in valid_domains:
            stale.unlink()

    # Generate catalog landing page
    catalog_path = MDX_DIR / "index.mdx"
    catalog_path.write_text(generate_catalog_mdx(specs))

    # Generate starlight-openapi plugin configuration
    config_content = generate_openapi_specs_config(specs)
    OPENAPI_CONFIG_PATH.write_text(config_content)

    print(f"Generated catalog page at {catalog_path}")
    print(f"Generated OpenAPI specs config at {OPENAPI_CONFIG_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
