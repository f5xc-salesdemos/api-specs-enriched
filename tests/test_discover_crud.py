# tests/test_discover_crud.py
import pytest
from scripts.discover import generate_crud_variants, is_list_endpoint, is_item_endpoint


def test_is_list_endpoint_true():
    assert is_list_endpoint("/api/config/namespaces/{namespace}/http_loadbalancers") is True


def test_is_list_endpoint_false_for_named():
    assert is_list_endpoint("/api/config/namespaces/{namespace}/http_loadbalancers/{name}") is False


def test_is_item_endpoint_true():
    assert is_item_endpoint("/api/config/namespaces/{namespace}/http_loadbalancers/{name}") is True


def test_is_item_endpoint_false_for_list():
    assert is_item_endpoint("/api/config/namespaces/{namespace}/http_loadbalancers") is False


def test_generate_crud_variants_from_list_endpoint():
    path = "/api/config/namespaces/{namespace}/http_loadbalancers"
    variants = generate_crud_variants(path)
    methods_and_paths = [(v["method"], v["path"]) for v in variants]
    assert ("POST", path) in methods_and_paths
    assert ("GET", path + "/{name}") in methods_and_paths
    assert ("PUT", path + "/{name}") in methods_and_paths
    assert ("DELETE", path + "/{name}") in methods_and_paths


def test_generate_crud_variants_no_duplicates():
    path = "/api/config/namespaces/{namespace}/http_loadbalancers"
    variants = generate_crud_variants(path)
    seen = set()
    for v in variants:
        key = (v["method"], v["path"])
        assert key not in seen, f"Duplicate variant: {key}"
        seen.add(key)


def test_generate_crud_variants_skips_already_item_path():
    # Item paths don't generate further sub-paths
    path = "/api/config/namespaces/{namespace}/http_loadbalancers/{name}"
    variants = generate_crud_variants(path)
    # Should only get PUT/PATCH/DELETE on the item path itself, no further nesting
    paths = [v["path"] for v in variants]
    assert not any("{name}/{" in p for p in paths)


from unittest.mock import AsyncMock, MagicMock
from scripts.discover import fetch_namespaces


@pytest.mark.asyncio
async def test_fetch_namespaces_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [{"name": "default"}, {"name": "production"}, {"name": "staging"}]
    }
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    result = await fetch_namespaces(mock_client, "https://example.f5xc.com")
    assert result == ["default", "production", "staging"]


@pytest.mark.asyncio
async def test_fetch_namespaces_failure_returns_empty():
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("network error")

    result = await fetch_namespaces(mock_client, "https://example.f5xc.com")
    assert result == []
