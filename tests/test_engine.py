import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.memory_engine import MemoryEngine

def test_full_morphe_lifecycle():
    print("==================================================")
    print("   MORPHE FULL ADAPTATION LIFECYCLE TEST          ")
    print("==================================================")

    # 1. Initialize Engine
    engine = MemoryEngine()
    print(f"[Phase 1] Initialized V1: {len(engine.graph.nodes)} nodes, {len(engine.graph.edges)} edges.")
    v1_metrics = engine.history[-1]["metrics"]
    print(f"          Baseline Mean Recall@4: {v1_metrics['mean_recall']:.4f}")
    assert len(engine.graph.nodes) == 5

    # 2. Test Split on Overloaded Module
    print("\n[Phase 2] Triggering KMeans SPLIT on 'MOD_OVERLOADED_CORE'...")
    split_res = engine.execute_guarded_adaptation("SPLIT", {"module_id": "MOD_OVERLOADED_CORE"})
    print(f"          Decision: {split_res['decision']} -> Version: {split_res['version']}")
    print(f"          New Nodes: {split_res['mutation']['new_modules']}")
    print(f"          Recall Delta: {split_res['before_recall']:.4f} -> {split_res['after_recall']:.4f}")
    assert split_res["decision"] == "ACCEPTED"
    assert "MOD_OVERLOADED_CORE" not in engine.modules
    assert "MOD_OVERLOADED_CORE_A" in engine.modules
    assert "MOD_OVERLOADED_CORE_B" in engine.modules

    # 3. Test Merge on Redundant Vector Modules
    print("\n[Phase 3] Triggering MERGE on redundant 'MOD_VECTOR_SEARCH_A' and 'MOD_VECTOR_SEARCH_B'...")
    merge_res = engine.execute_guarded_adaptation("MERGE", {
        "module_a": "MOD_VECTOR_SEARCH_A",
        "module_b": "MOD_VECTOR_SEARCH_B"
    })
    print(f"          Decision: {merge_res['decision']} -> Version: {merge_res['version']}")
    print(f"          Unified Node: {merge_res['mutation']['merged_id']}")
    print(f"          Combined Records: {merge_res['mutation']['record_count']}")
    assert merge_res["decision"] == "ACCEPTED"

    # 4. Test Shortcut Creation
    print("\n[Phase 4] Creating Hebbian SHORTCUT between 'MOD_PYTHON_DATA' and 'MOD_ML_PIPELINES'...")
    shortcut_res = engine.execute_guarded_adaptation("SHORTCUT", {
        "module_a": "MOD_PYTHON_DATA",
        "module_b": "MOD_ML_PIPELINES"
    })
    print(f"          Decision: {shortcut_res['decision']} -> Version: {shortcut_res['version']}")
    assert engine.graph.has_edge("MOD_PYTHON_DATA", "MOD_ML_PIPELINES")

    # 5. Test Safety Guardrail & Rollback (Intentional bad threshold to force rejection)
    print("\n[Phase 5] Simulating Unsafe Mutation with strict guardrail threshold (0.999)...")
    # Trying to split with an impossibly high recall requirement to prove rollback works
    bad_res = engine.execute_guarded_adaptation(
        "SPLIT",
        {"module_id": "MOD_OVERLOADED_CORE_A"},
        min_recall_threshold=0.999
    )
    print(f"          Decision: {bad_res['decision']}")
    print(f"          Reason: {bad_res.get('reason')}")
    print(f"          Restored Version: {bad_res.get('restored_version')}")
    assert bad_res["decision"] == "REJECTED"
    # Ensure graph was rolled back and node still exists
    assert "MOD_OVERLOADED_CORE_A" in engine.modules

    # 6. Verify Semantic Retrieval with 1-hop traversal
    print("\n[Phase 6] Testing Semantic Search across adapted graph...")
    query = "How do NumPy and PyTorch integrate in training pipelines?"
    search_res = engine.search(query, top_k=3)
    print(f"          Query: '{query}'")
    print(f"          Visited Modules: {search_res['visited_modules']}")
    print(f"          Search Latency: {search_res['latency_ms']} ms")
    print("          Top Retrieved Result:")
    print(f"          - [{search_res['results'][0]['record_id']}] {search_res['results'][0]['text']} (Score: {search_res['results'][0]['similarity']})")
    assert len(search_res["results"]) > 0

    print("\n==================================================")
    print("   ALL TESTS PASSED! MORPHE ENGINE READY!         ")
    print("==================================================")

if __name__ == "__main__":
    test_full_morphe_lifecycle()
