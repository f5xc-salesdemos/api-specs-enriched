# tests/test_compile_catalog.py
from scripts.compile_catalog import (
    assign_danger_level,
    extract_category_name,
    generate_operation_name,
    extract_parameters,
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
import tempfile
from pathlib import Path
from scripts.compile_catalog import main


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
