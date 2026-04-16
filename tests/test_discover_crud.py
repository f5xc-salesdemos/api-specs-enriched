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


import json
import tempfile
from pathlib import Path
from scripts.discover import run_discovery, get_default_config
import scripts.discover as discover_module


@pytest.mark.asyncio
async def test_run_discovery_expands_crud_endpoints(monkeypatch):
    """run_discovery with dry_run=True returns a session without errors after CRUD expansion."""
    config = get_default_config()
    config["api_url"] = "https://test.example.com"
    config["auth_token"] = "test-token"

    monkeypatch.setattr(
        discover_module,
        "extract_endpoints_from_specs",
        lambda specs_dir: [{"method": "GET", "path": "/api/config/namespaces/{namespace}/http_loadbalancers"}],
    )

    session = await run_discovery(config, dry_run=True)

    assert session is not None
    assert len(session.errors) == 0


@pytest.mark.asyncio
async def test_run_discovery_auto_discovers_namespaces(monkeypatch):
    """run_discovery (non-dry-run, empty endpoints) calls fetch_namespaces and populates session.namespaces."""
    config = get_default_config()
    config["api_url"] = "https://test.example.com"
    config["auth_token"] = "test-token"

    monkeypatch.setattr(
        discover_module,
        "extract_endpoints_from_specs",
        lambda specs_dir: [],
    )

    async def fake_fetch_namespaces(client, api_url):
        return ["auto-ns-1", "auto-ns-2"]

    monkeypatch.setattr(discover_module, "fetch_namespaces", fake_fetch_namespaces)

    # dry_run=False so the httpx block (and fetch_namespaces) is reached;
    # empty endpoint list means the discovery loop never actually makes HTTP calls.
    session = await run_discovery(config, dry_run=False)

    assert "auto-ns-1" in session.namespaces
    assert "auto-ns-2" in session.namespaces


@pytest.mark.asyncio
async def test_run_discovery_dry_run_returns_session_without_error(monkeypatch):
    """run_discovery with dry_run=True returns a non-None session with no errors."""
    config = get_default_config()
    config["api_url"] = "https://test.example.com"
    config["auth_token"] = "test-token"

    monkeypatch.setattr(
        discover_module,
        "extract_endpoints_from_specs",
        lambda specs_dir: [{"method": "GET", "path": "/api/config/namespaces/{namespace}/virtual_sites"}],
    )

    session = await run_discovery(config, dry_run=True)

    assert session is not None
    assert len(session.errors) == 0
