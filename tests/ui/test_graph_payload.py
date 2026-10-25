import pytest
from ui.adapter import EngineAdapter
from ui.graph_payload import build_graph_payload

def test_payload_equals_engine_graph():
    adapter = EngineAdapter()
    adapter.load_sample()

    engine_graph = adapter.get_graph()
    modules_meta = adapter.engine.modules

    payload = build_graph_payload(engine_graph, modules_meta=modules_meta)

    # 1. Node count and IDs equality
    engine_node_ids = set(engine_graph.nodes())
    payload_node_ids = {n["id"] for n in payload["nodes"]}
    assert payload_node_ids == engine_node_ids, "Payload nodes must exactly equal engine graph nodes"

    # 2. Edge count and pairs equality
    engine_edge_pairs = {tuple(sorted([u, v])) for u, v in engine_graph.edges()}
    payload_edge_pairs = {tuple(sorted([e["source"], e["target"]])) for e in payload["edges"]}
    assert payload_edge_pairs == engine_edge_pairs, "Payload edges must exactly equal engine graph edges"

    # 3. Selecting a node shows its real records
    for node in payload["nodes"]:
        node_id = node["id"]
        mod_detail = adapter.get_module(node_id)
        assert mod_detail.id == node_id
        assert len(mod_detail.record_ids) == node["record_count"]
        # Verify records exist in storage
        for r_id in mod_detail.record_ids:
            assert r_id in adapter.engine.records
