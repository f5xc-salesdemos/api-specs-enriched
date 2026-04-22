# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Unit tests for ``live_sample`` in ``scripts.contract_diff``."""

from unittest.mock import MagicMock

from scripts.contract_diff import live_sample


def test_live_sample_probes_random_paths_and_returns_results():
    spec = {"paths": {f"/p{i}": {"get": {"operationId": f"op{i}"}} for i in range(20)}}
    probe = MagicMock(return_value={"status_code": 200, "ok": True})
    results = live_sample(spec, n=5, probe=probe, rng_seed=0)
    assert len(results) == 5
    # Each called with a distinct path.
    called_paths = {c.args[0] for c in probe.call_args_list}
    assert len(called_paths) == 5


def test_live_sample_flags_mismatch_when_probe_reports_fail():
    spec = {"paths": {"/a": {"get": {"operationId": "a"}}, "/b": {"get": {"operationId": "b"}}}}
    probe = MagicMock(return_value={"status_code": 500, "ok": False})
    results = live_sample(spec, n=2, probe=probe, rng_seed=1)
    assert all(not r["ok"] for r in results)


def test_live_sample_respects_n_cap_against_path_count():
    spec = {"paths": {"/only": {"get": {"operationId": "o"}}}}
    probe = MagicMock(return_value={"status_code": 200, "ok": True})
    results = live_sample(spec, n=10, probe=probe, rng_seed=0)
    assert len(results) == 1  # n clamped to path count


def test_live_sample_prefers_get_over_options():
    spec = {"paths": {"/x": {"get": {"operationId": "gx"}, "options": {}}}}
    probe = MagicMock(return_value={"status_code": 200, "ok": True})
    results = live_sample(spec, n=1, probe=probe, rng_seed=0)
    assert results[0]["method"] == "GET"


def test_live_sample_falls_back_to_options_when_no_get():
    spec = {"paths": {"/x": {"options": {"operationId": "ox"}}}}
    probe = MagicMock(return_value={"status_code": 200, "ok": True})
    results = live_sample(spec, n=1, probe=probe, rng_seed=0)
    assert results[0]["method"] == "OPTIONS"
