#!/usr/bin/env python3
# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Catalog Compiler — transforms F5XC OpenAPI specs into xcsh api-catalog.json format.

Usage:
    python -m scripts.compile_catalog                         # Uses specs/discovered/openapi.json
    python -m scripts.compile_catalog --input path/to/spec.json
    python -m scripts.compile_catalog --output release/api-catalog.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("specs/discovered/openapi.json")
DEFAULT_OUTPUT = Path("release/api-catalog.json")

F5XC_AUTH = {
    "type": "api_token",
    "headerName": "Authorization",
    "headerTemplate": "APIToken {token}",
    "tokenSource": "F5XC_API_TOKEN",
    "baseUrlSource": "F5XC_API_URL",
}

F5XC_DEFAULTS = {
    "namespace": {"source": "F5XC_NAMESPACE"}
}

def merge_spec_files(dir_path: Path) -> dict[str, Any]:
    """Read all OpenAPI JSON files in a directory and merge their paths.

    Skips files without a 'paths' key (non-spec files like index.json).
    When the same path appears in multiple files, their methods are merged.
    """
    merged_paths: dict[str, Any] = {}

    for spec_file in sorted(dir_path.glob("*.json")):
        try:
            with spec_file.open() as f:
                spec = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        paths = spec.get("paths")
        if not paths or not isinstance(paths, dict):
            continue

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            if path not in merged_paths:
                merged_paths[path] = {}
            merged_paths[path].update(path_item)

    return {"openapi": "3.0.3", "paths": merged_paths}


_DANGER_MAP: dict[str, str] = {
    "GET": "low",
    "OPTIONS": "low",
    "POST": "medium",
    "PUT": "medium",
    "PATCH": "medium",
    "DELETE": "high",
}


def assign_danger_level(method: str) -> str:
    """Map HTTP method to danger level."""
    return _DANGER_MAP.get(method.upper(), "medium")


def extract_category_name(path: str) -> str:
    """Derive kebab-case category name from an API path.

    Examples:
        /api/config/namespaces/{namespace}/http_loadbalancers       -> http-loadbalancers
        /api/config/namespaces/{namespace}/http_loadbalancers/{name} -> http-loadbalancers
        /api/web/namespaces                                          -> namespaces
    """
    segments = [s for s in path.split("/") if s and not s.startswith("{")]
    prefix = {"api", "config", "web", "ml", "data"}
    filtered = [s for s in segments if s not in prefix]
    resource_segments = []
    skip_next = False
    for seg in filtered:
        if seg == "namespaces":
            skip_next = True
            continue
        if skip_next:
            skip_next = False
            continue
        resource_segments.append(seg)
    resource = resource_segments[0] if resource_segments else filtered[-1] if filtered else "unknown"
    return resource.replace("_", "-")


def generate_operation_name(method: str, path: str) -> str:
    """Generate a snake_case operation name from HTTP method and path.

    Rules:
        GET  /resources        -> list_resources
        GET  /resources/{name} -> get_resource   (singular)
        POST /resources        -> create_resource (singular)
        PUT  /resources/{name} -> replace_resource (singular)
        PATCH /resources/{name}-> update_resource (singular)
        DELETE /resources/{name}-> delete_resource (singular)
    """
    category = extract_category_name(path)
    resource_snake = category.replace("-", "_")
    singular = resource_snake.rstrip("s") if resource_snake.endswith("s") else resource_snake

    segments = path.rstrip("/").split("/")
    last_segment = segments[-1] if segments else ""
    is_item = last_segment.startswith("{") and last_segment.endswith("}")

    method = method.upper()
    if method == "GET" and not is_item:
        return f"list_{resource_snake}"
    elif method == "GET" and is_item:
        return f"get_{singular}"
    elif method == "POST":
        return f"create_{singular}"
    elif method == "PUT":
        return f"replace_{singular}"
    elif method == "PATCH":
        return f"update_{singular}"
    elif method == "DELETE":
        return f"delete_{singular}"
    else:
        return f"{method.lower()}_{singular}"


def extract_parameters(path: str, operation: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract parameters from path template and OpenAPI operation definition."""
    params: list[dict[str, Any]] = []

    for match in re.finditer(r"\{([^}]+)\}", path):
        raw_name = match.group(1)
        # Normalize dotted params: metadata.namespace -> namespace
        name = raw_name.split(".")[-1] if "." in raw_name else raw_name
        param: dict[str, Any] = {
            "name": name,
            "in": "path",
            "required": True,
            "type": "string",
        }
        if name == "namespace":
            param["default"] = "$F5XC_NAMESPACE"
        params.append(param)

    for op_param in operation.get("parameters", []):
        if op_param.get("in") == "query":
            params.append({
                "name": op_param["name"],
                "in": "query",
                "required": op_param.get("required", False),
                "type": op_param.get("schema", {}).get("type", "string"),
            })

    return params


def extract_response_schema(operation: dict[str, Any]) -> dict[str, Any] | None:
    """Extract and simplify response schema from an OpenAPI operation.

    Checks 200 then 201 response codes. Returns simplified schema with only
    type, properties (name -> {type}), and required fields. Returns None if
    no response schema is defined.
    """
    for code in ("200", "201"):
        schema = (
            operation.get("responses", {})
            .get(code, {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )
        if schema and isinstance(schema, dict):
            simplified: dict[str, Any] = {}
            if "type" in schema:
                simplified["type"] = schema["type"]
            if "properties" in schema and isinstance(schema["properties"], dict):
                simplified["properties"] = {}
                for prop_name, prop_schema in schema["properties"].items():
                    if isinstance(prop_schema, dict) and "type" in prop_schema:
                        simplified["properties"][prop_name] = {"type": prop_schema["type"]}
            if "required" in schema and isinstance(schema["required"], list):
                simplified["required"] = schema["required"]
            if simplified:
                return simplified
    return None


def group_paths_by_resource(paths: dict[str, Any]) -> dict[str, list[tuple[str, str, dict]]]:
    """Group (path, method, operation) tuples by category name."""
    groups: dict[str, list[tuple[str, str, dict]]] = {}
    for path, path_item in sorted(paths.items()):
        if not isinstance(path_item, dict):
            continue
        category = extract_category_name(path)
        if category not in groups:
            groups[category] = []
        for method, operation in path_item.items():
            if method.lower() in ("get", "post", "put", "patch", "delete", "options"):
                groups[category].append((path, method.upper(), operation or {}))
    return groups


def compile_catalog(openapi: dict[str, Any]) -> dict[str, Any]:
    """Transform an OpenAPI 3.0 spec dict into xcsh api-catalog.json format."""
    paths = openapi.get("paths", {})
    groups = group_paths_by_resource(paths)

    categories = []
    for category_name in sorted(groups.keys()):
        entries = groups[category_name]
        operations = []
        seen_op_names: set[str] = set()
        for path, method, operation in sorted(entries, key=lambda e: (e[0], e[1])):
            op_name = generate_operation_name(method, path)
            if op_name in seen_op_names:
                continue
            seen_op_names.add(op_name)
            op: dict[str, Any] = {
                "name": op_name,
                "description": operation.get("summary") or operation.get("description") or f"{method} {path}",
                "method": method,
                "path": path,
                "dangerLevel": assign_danger_level(method),
                "parameters": extract_parameters(path, operation),
            }
            body_schema = (
                operation.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            if body_schema:
                op["bodySchema"] = body_schema
            response_schema = extract_response_schema(operation)
            if response_schema:
                op["responseSchema"] = response_schema
            operations.append(op)

        if operations:
            display_name = category_name.replace("-", " ").title()
            categories.append({
                "name": category_name,
                "displayName": display_name,
                "operations": operations,
            })

    # Deduplicate operation names globally across all categories.
    # When a collision occurs, suffix the second occurrence with the category name.
    global_seen: dict[str, str] = {}  # op_name -> first_category
    for cat in categories:
        for op in cat["operations"]:
            if op["name"] in global_seen:
                # Suffix with category name to disambiguate
                op["name"] = f"{op['name']}_{cat['name'].replace('-', '_')}"
            else:
                global_seen[op["name"]] = cat["name"]

    return {
        "service": "f5xc",
        "displayName": "F5 Distributed Cloud",
        "version": "1.0.0",
        "specSource": "f5xc-salesdemos/api-specs-enriched",
        "auth": F5XC_AUTH,
        "defaults": F5XC_DEFAULTS,
        "categories": categories,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile F5XC OpenAPI spec to xcsh catalog JSON")
    parser.add_argument("--input", type=Path, default=None, help="Single OpenAPI spec input file")
    parser.add_argument("--input-dir", type=Path, default=None, help="Directory of OpenAPI spec files to merge")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output api-catalog.json path")
    args = parser.parse_args()

    if args.input_dir:
        if not args.input_dir.is_dir():
            print(f"Error: input directory not found: {args.input_dir}", file=sys.stderr)
            return 1
        openapi = merge_spec_files(args.input_dir)
    elif args.input:
        if not args.input.exists():
            print(f"Error: input file not found: {args.input}", file=sys.stderr)
            return 1
        with args.input.open() as f:
            openapi = json.load(f)
    else:
        if not DEFAULT_INPUT.exists():
            print(f"Error: default input not found: {DEFAULT_INPUT}", file=sys.stderr)
            return 1
        with DEFAULT_INPUT.open() as f:
            openapi = json.load(f)

    catalog = compile_catalog(openapi)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump(catalog, f, indent=2)
        f.write("\n")

    total_ops = sum(len(c["operations"]) for c in catalog["categories"])
    print(f"Compiled {total_ops} operations across {len(catalog['categories'])} categories -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
