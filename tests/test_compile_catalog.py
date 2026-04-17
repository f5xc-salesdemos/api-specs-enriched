# tests/test_compile_catalog.py
from scripts.compile_catalog import (
    assign_danger_level,
    extract_category_name,
    generate_operation_name,
    extract_parameters,
    extract_response_schema,
    compile_catalog,
    group_paths_by_resource,
)


def test_assign_danger_level_get():
    assert assign_danger_level("GET") == "low"

def test_assign_danger_level_options():
    assert assign_danger_level("OPTIONS") == "low"

def test_assign_danger_level_post():
    assert assign_danger_level("POST") == "medium"

def test_assign_danger_level_put():
    assert assign_danger_level("PUT") == "medium"

def test_assign_danger_level_patch():
    assert assign_danger_level("PATCH") == "medium"

def test_assign_danger_level_delete():
    assert assign_danger_level("DELETE") == "high"

def test_extract_category_name_namespace_path():
    path = "/api/config/namespaces/{namespace}/http_loadbalancers"
    assert extract_category_name(path) == "http-loadbalancers"

def test_extract_category_name_web_path():
    path = "/api/web/namespaces"
    assert extract_category_name(path) == "namespaces"

def test_extract_category_name_item_path():
    path = "/api/config/namespaces/{namespace}/http_loadbalancers/{name}"
    assert extract_category_name(path) == "http-loadbalancers"

def test_generate_operation_name_list():
    assert generate_operation_name("GET", "/api/config/namespaces/{namespace}/http_loadbalancers") == "list_http_loadbalancers"

def test_generate_operation_name_get_item():
    assert generate_operation_name("GET", "/api/config/namespaces/{namespace}/http_loadbalancers/{name}") == "get_http_loadbalancer"

def test_generate_operation_name_post():
    assert generate_operation_name("POST", "/api/config/namespaces/{namespace}/http_loadbalancers") == "create_http_loadbalancer"

def test_generate_operation_name_put():
    assert generate_operation_name("PUT", "/api/config/namespaces/{namespace}/http_loadbalancers/{name}") == "replace_http_loadbalancer"

def test_generate_operation_name_patch():
    assert generate_operation_name("PATCH", "/api/config/namespaces/{namespace}/http_loadbalancers/{name}") == "update_http_loadbalancer"

def test_generate_operation_name_delete():
    assert generate_operation_name("DELETE", "/api/config/namespaces/{namespace}/http_loadbalancers/{name}") == "delete_http_loadbalancer"

def test_extract_parameters_path_params():
    path = "/api/config/namespaces/{namespace}/http_loadbalancers/{name}"
    params = extract_parameters(path, {})
    assert any(p["name"] == "namespace" and p["in"] == "path" and p["required"] is True for p in params)
    assert any(p["name"] == "name" and p["in"] == "path" and p["required"] is True for p in params)

def test_extract_parameters_namespace_gets_default():
    path = "/api/config/namespaces/{namespace}/http_loadbalancers"
    params = extract_parameters(path, {})
    ns_param = next(p for p in params if p["name"] == "namespace")
    assert ns_param["default"] == "$F5XC_NAMESPACE"

def test_group_paths_by_resource():
    paths = {
        "/api/config/namespaces/{namespace}/http_loadbalancers": {"get": {}},
        "/api/config/namespaces/{namespace}/http_loadbalancers/{name}": {"delete": {}},
        "/api/config/namespaces/{namespace}/origin_pools": {"get": {}},
    }
    groups = group_paths_by_resource(paths)
    assert "http-loadbalancers" in groups
    assert "origin-pools" in groups
    assert len(groups["http-loadbalancers"]) == 2

def test_compile_catalog_structure():
    openapi = {
        "openapi": "3.0.3",
        "paths": {
            "/api/config/namespaces/{namespace}/http_loadbalancers": {
                "get": {"operationId": "list_lbs", "responses": {}}
            },
            "/api/config/namespaces/{namespace}/http_loadbalancers/{name}": {
                "delete": {"operationId": "delete_lb", "responses": {}}
            },
        }
    }
    catalog = compile_catalog(openapi)
    assert catalog["service"] == "f5xc"
    assert catalog["auth"]["type"] == "api_token"
    assert catalog["auth"]["headerTemplate"] == "APIToken {token}"
    assert len(catalog["categories"]) >= 1
    cat = next(c for c in catalog["categories"] if c["name"] == "http-loadbalancers")
    op_names = [op["name"] for op in cat["operations"]]
    assert "list_http_loadbalancers" in op_names
    assert "delete_http_loadbalancer" in op_names

def test_compile_catalog_operation_fields():
    openapi = {
        "openapi": "3.0.3",
        "paths": {
            "/api/config/namespaces/{namespace}/http_loadbalancers/{name}": {
                "delete": {"operationId": "delete_lb", "responses": {}}
            },
        }
    }
    catalog = compile_catalog(openapi)
    cat = catalog["categories"][0]
    op = cat["operations"][0]
    assert op["method"] == "DELETE"
    assert op["dangerLevel"] == "high"
    assert op["path"] == "/api/config/namespaces/{namespace}/http_loadbalancers/{name}"
    assert any(p["name"] == "namespace" for p in op["parameters"])
    assert any(p["name"] == "name" for p in op["parameters"])

def test_compile_catalog_deterministic():
    openapi = {
        "openapi": "3.0.3",
        "paths": {
            "/api/config/namespaces/{namespace}/http_loadbalancers": {"get": {"responses": {}}},
            "/api/config/namespaces/{namespace}/origin_pools": {"get": {"responses": {}}},
        }
    }
    result1 = compile_catalog(openapi)
    result2 = compile_catalog(openapi)
    assert result1 == result2


import json
import sys
import tempfile
from pathlib import Path
from scripts.compile_catalog import main
from scripts.compile_catalog import merge_spec_files


def test_main_cli_writes_output_file():
    """main() reads input OpenAPI spec and writes valid api-catalog.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "input.json"
        output_path = Path(tmpdir) / "output" / "api-catalog.json"
        spec = {
            "openapi": "3.0.3",
            "paths": {
                "/api/config/namespaces/{namespace}/widgets": {
                    "get": {"operationId": "list_widgets", "responses": {"200": {}}}
                }
            },
        }
        input_path.write_text(json.dumps(spec))

        import sys
        original_argv = sys.argv
        sys.argv = ["compile_catalog", "--input", str(input_path), "--output", str(output_path)]
        try:
            exit_code = main()
        finally:
            sys.argv = original_argv

        assert exit_code == 0
        assert output_path.exists()
        catalog = json.loads(output_path.read_text())
        assert catalog["service"] == "f5xc"
        assert len(catalog["categories"]) >= 1


def test_compile_catalog_against_real_spec():
    """compile_catalog() processes the real specs/discovered/openapi.json without error."""
    import pytest
    spec_path = Path("specs/discovered/openapi.json")
    if not spec_path.exists():
        pytest.skip("Real spec not available")
    with spec_path.open() as f:
        openapi = json.load(f)
    catalog = compile_catalog(openapi)
    assert catalog["service"] == "f5xc"
    assert catalog["auth"]["type"] == "api_token"
    assert len(catalog["categories"]) > 0
    for cat in catalog["categories"]:
        assert "name" in cat
        assert "displayName" in cat
        for op in cat["operations"]:
            assert "name" in op
            assert "method" in op
            assert "path" in op
            assert "dangerLevel" in op
            assert "parameters" in op


def test_compile_catalog_handles_extension_fields():
    """compile_catalog() ignores OpenAPI extension fields (x-*) without crashing."""
    openapi = {
        "openapi": "3.0.3",
        "paths": {
            "/api/config/namespaces/{namespace}/widgets": {
                "get": {
                    "operationId": "list_widgets",
                    "responses": {"200": {}},
                    "x-response-time-ms": 159.81,
                },
                "x-displayname": "Widget Management",
                "x-ves-proto-service": "ves.io.schema.widget.API",
            }
        },
    }
    catalog = compile_catalog(openapi)
    assert len(catalog["categories"]) >= 1
    cat = catalog["categories"][0]
    assert len(cat["operations"]) >= 1
    assert cat["operations"][0]["name"] == "list_widgets"


def test_merge_spec_files_combines_paths_from_multiple_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        spec1 = {"openapi": "3.0.3", "paths": {"/api/widgets": {"get": {"responses": {}}}}}
        spec2 = {"openapi": "3.0.3", "paths": {"/api/gadgets": {"post": {"responses": {}}}}}
        Path(tmpdir, "widgets.json").write_text(json.dumps(spec1))
        Path(tmpdir, "gadgets.json").write_text(json.dumps(spec2))
        merged = merge_spec_files(Path(tmpdir))
        assert "/api/widgets" in merged["paths"]
        assert "/api/gadgets" in merged["paths"]
        assert len(merged["paths"]) == 2


def test_merge_spec_files_skips_non_spec_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        spec = {"openapi": "3.0.3", "paths": {"/api/items": {"get": {"responses": {}}}}}
        non_spec = {"metadata": {"version": "1.0"}}
        Path(tmpdir, "items.json").write_text(json.dumps(spec))
        Path(tmpdir, "index.json").write_text(json.dumps(non_spec))
        Path(tmpdir, "config.json").write_text(json.dumps(non_spec))
        merged = merge_spec_files(Path(tmpdir))
        assert "/api/items" in merged["paths"]
        assert len(merged["paths"]) == 1


def test_merge_spec_files_handles_duplicate_paths():
    with tempfile.TemporaryDirectory() as tmpdir:
        spec1 = {"openapi": "3.0.3", "paths": {"/api/items": {"get": {"operationId": "list"}}}}
        spec2 = {"openapi": "3.0.3", "paths": {"/api/items": {"post": {"operationId": "create"}}}}
        Path(tmpdir, "spec1.json").write_text(json.dumps(spec1))
        Path(tmpdir, "spec2.json").write_text(json.dumps(spec2))
        merged = merge_spec_files(Path(tmpdir))
        assert "get" in merged["paths"]["/api/items"]
        assert "post" in merged["paths"]["/api/items"]


def test_compile_catalog_from_enriched_specs():
    import pytest
    enriched_dir = Path("docs/specifications/api")
    if not enriched_dir.exists():
        pytest.skip("Enriched specs not available")
    merged = merge_spec_files(enriched_dir)
    catalog = compile_catalog(merged)
    assert catalog["service"] == "f5xc"
    total_ops = sum(len(c["operations"]) for c in catalog["categories"])
    assert total_ops > 100, f"Expected >100 operations, got {total_ops}"
    assert len(catalog["categories"]) > 10


def test_compile_catalog_deduplicates_operation_names_globally():
    # /api/.../sites  -> category "sites",       op "create_site"
    # /api/.../foos   -> category "foos",         op "create_foo"  (singular strips 's')
    # Two different categories that happen to produce identical op names after singularisation
    # We use "widgets" vs "widget_things" — both produce "create_widget" when singularised.
    # Actually the cleaner way: use paths that map to different categories but the same final
    # op name.  "namespaces/{ns}/things" -> category "things", op "create_thing"
    # and "namespaces/{ns}/other_things" -> category "other-things", op "create_other_thing"
    # — those differ.  Instead, use explicitly colliding resource roots:
    # paths under different prefixes that both collapse to the same category resource name.
    # Easiest: put the same resource name under two different top-level API paths so they land
    # in different categories but produce the same op name.
    openapi = {
        "openapi": "3.0.3",
        "paths": {
            # category: "sites", op: "create_site"
            "/api/config/namespaces/{namespace}/sites": {"post": {"responses": {}}},
            # category: "sites" (same) but a different prefix segment outside namespace scope
            # To force two DIFFERENT categories with identical op names, use a path segment
            # that is not filtered by the prefix rules and lands in a different category.
            # The simplest approach: one path has extra sub-resource that changes category
            # but the resource stem is the same word.
            # "/api/ml/namespaces/{namespace}/sites" -> category "sites", op "create_site"
            # Both land in category "sites" so the per-category dedup catches them.
            # Use a path where the resource segment differs only by a trailing 's' quirk:
            # "managed_sites" singularizes to "managed_site"; category "managed-sites"
            # vs plain "sites" -> "create_site". These differ.
            # REAL collision scenario: two paths where extract_category_name gives different
            # strings but generate_operation_name gives the same string.
            # "http_loadbalancers" -> category "http-loadbalancers", op "create_http_loadbalancer"
            # "http_loadbalancer"  -> category "http-loadbalancer",  op "create_http_loadbalancer"
            "/api/config/namespaces/{namespace}/http_loadbalancers": {"post": {"responses": {}}},
            "/api/config/namespaces/{namespace}/http_loadbalancer": {"post": {"responses": {}}},
        }
    }
    catalog = compile_catalog(openapi)
    all_op_names = [op["name"] for cat in catalog["categories"] for op in cat["operations"]]
    assert len(all_op_names) == len(set(all_op_names)), f"Duplicate names found: {all_op_names}"


def test_extract_parameters_normalizes_dotted_params():
    path = "/api/config/namespaces/{metadata.namespace}/http_loadbalancers"
    params = extract_parameters(path, {})
    ns_param = next(p for p in params if p["name"] == "namespace")
    assert ns_param["default"] == "$F5XC_NAMESPACE"
    assert ns_param["in"] == "path"


def test_main_cli_with_input_dir_flag():
    with tempfile.TemporaryDirectory() as tmpdir:
        specs_dir = Path(tmpdir) / "specs"
        specs_dir.mkdir()
        output_path = Path(tmpdir) / "catalog.json"
        spec = {"openapi": "3.0.3", "paths": {
            "/api/config/namespaces/{namespace}/widgets": {"get": {"responses": {}}},
            "/api/config/namespaces/{namespace}/gadgets": {"delete": {"responses": {}}},
        }}
        (specs_dir / "test.json").write_text(json.dumps(spec))
        original_argv = sys.argv
        sys.argv = ["compile_catalog", "--input-dir", str(specs_dir), "--output", str(output_path)]
        try:
            exit_code = main()
        finally:
            sys.argv = original_argv
        assert exit_code == 0
        assert output_path.exists()
        catalog = json.loads(output_path.read_text())
        assert catalog["service"] == "f5xc"
        total_ops = sum(len(c["operations"]) for c in catalog["categories"])
        assert total_ops >= 2


def test_extract_response_schema_from_200():
    operation = {
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "items": {"type": "array", "items": {"type": "string"}},
                                "errors": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["items"],
                        }
                    }
                }
            }
        }
    }
    schema = extract_response_schema(operation)
    assert schema is not None
    assert schema["type"] == "object"
    assert "items" in schema["properties"]
    assert schema["properties"]["items"]["type"] == "array"
    assert schema["required"] == ["items"]


def test_extract_response_schema_from_201_for_post():
    operation = {
        "responses": {
            "201": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "metadata": {"type": "object"},
                            },
                        }
                    }
                }
            }
        }
    }
    schema = extract_response_schema(operation)
    assert schema is not None
    assert schema["type"] == "object"


def test_extract_response_schema_simplifies_nested_refs():
    """$ref and description fields are stripped; only type/properties/required kept."""
    operation = {
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "description": "A list response",
                            "properties": {
                                "items": {
                                    "type": "array",
                                    "description": "The items",
                                    "items": {"$ref": "#/components/schemas/Item"},
                                },
                                "count": {"type": "integer", "description": "Total count"},
                            },
                            "required": ["items"],
                            "additionalProperties": True,
                        }
                    }
                }
            }
        }
    }
    schema = extract_response_schema(operation)
    assert schema is not None
    assert "description" not in schema
    assert "additionalProperties" not in schema
    assert schema["properties"]["items"]["type"] == "array"
    assert schema["properties"]["count"]["type"] == "integer"


def test_extract_response_schema_returns_none_when_missing():
    operation = {"responses": {"404": {"description": "Not found"}}}
    schema = extract_response_schema(operation)
    assert schema is None
