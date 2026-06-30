# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Unit tests for the dependency-graph projection.

The coarse resource_dependency_graph.json is a PROJECTION of the per-field
x-f5xc-references (single source of truth) — not hand-maintained. Edges that
come from a choice-gated reference are flagged conditional.
"""

from scripts.build_dependency_graph import Edge, project_graph


def test_topological_order_dependencies_before_dependents():
    edges = [
        Edge(src="http-load-balancer", target="origin-pool", conditional=False, required=True),
        Edge(src="origin-pool", target="health-check", conditional=False, required=True),
    ]
    g = project_graph(edges, ["http-load-balancer", "origin-pool", "health-check"])
    order = g["sorted"]
    assert order.index("health-check") < order.index("origin-pool")
    assert order.index("origin-pool") < order.index("http-load-balancer")


def test_conditional_flag_preserved():
    edges = [Edge(src="fleet", target="dc-cluster-group", conditional=True, required=False)]
    g = project_graph(edges, ["fleet", "dc-cluster-group"])
    edge = g["edges"]["fleet"][0]
    assert edge["target"] == "dc-cluster-group"
    assert edge["conditional"] is True
    assert edge["required"] is False


def test_leaves_and_prerequisites():
    edges = [Edge(src="http-load-balancer", target="origin-pool", conditional=False, required=True)]
    g = project_graph(edges, ["http-load-balancer", "origin-pool", "ip-prefix-set"])
    assert "origin-pool" in g["leaves"]
    assert "ip-prefix-set" in g["leaves"]
    assert "http-load-balancer" not in g["leaves"]
    assert g["prerequisites"] == ["origin-pool"]


def test_cycle_does_not_hang_and_includes_all():
    edges = [
        Edge(src="a", target="b", conditional=False, required=True),
        Edge(src="b", target="a", conditional=False, required=True),
    ]
    g = project_graph(edges, ["a", "b"])
    assert set(g["sorted"]) == {"a", "b"}
