# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Unit tests for ExampleFieldEnricher.

Derives per-field example values from x-f5xc-minimum-configuration.example_yaml
(the single source of truth — present for 331/333 CreateSpecType schemas) and
stamps them as x-f5xc-field-examples on the schema, so downstream tools (field
metadata, workflow generator, sweep) read deterministic create values from one
place instead of hand-coding them.
"""

from scripts.utils.example_field_enricher import ExampleFieldEnricher, flatten_example


def test_flatten_nested_and_list_leaves():
    spec = {
        "origin_servers": [{"public_name": {"dns_name": "backend1.example.com"}}],
        "port": 8080,
    }
    flat = flatten_example(spec)
    assert flat["spec.origin_servers[].public_name.dns_name"] == "backend1.example.com"
    assert flat["spec.port"] == 8080


def test_enrich_stamps_field_examples_from_example_yaml():
    spec = {
        "components": {
            "schemas": {
                "viewsorigin_poolCreateSpecType": {
                    "type": "object",
                    "x-f5xc-minimum-configuration": {
                        "example_yaml": (
                            "metadata:\n  name: backend-pool\nspec:\n  origin_servers:\n"
                            "    - public_name:\n        dns_name: backend1.example.com\n  port: 8080\n"
                        ),
                    },
                    "properties": {"port": {"type": "integer"}},
                },
            },
        },
    }
    out = ExampleFieldEnricher().enrich_spec(spec)
    sch = out["components"]["schemas"]["viewsorigin_poolCreateSpecType"]
    examples = sch["x-f5xc-field-examples"]
    assert examples["spec.port"] == 8080
    assert examples["spec.origin_servers[].public_name.dns_name"] == "backend1.example.com"


def test_no_example_yaml_is_noop():
    spec = {"components": {"schemas": {"fooCreateSpecType": {"properties": {}}}}}
    out = ExampleFieldEnricher().enrich_spec(spec)
    assert "x-f5xc-field-examples" not in out["components"]["schemas"]["fooCreateSpecType"]


def test_idempotent():
    spec = {
        "components": {
            "schemas": {
                "barCreateSpecType": {
                    "x-f5xc-minimum-configuration": {"example_yaml": "spec:\n  port: 80\n"},
                    "properties": {},
                },
            },
        },
    }
    e = ExampleFieldEnricher()
    once = e.enrich_spec(spec)
    e.reset_stats()
    twice = e.enrich_spec(once)
    assert twice["components"]["schemas"]["barCreateSpecType"]["x-f5xc-field-examples"] == {
        "spec.port": 80
    }
