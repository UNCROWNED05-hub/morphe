import sys
import os
import copy
import numpy as np

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.memory_engine import MemoryEngine
from engine.config import MIN_ACCEPTABLE_RECALL, MAX_ALLOWABLE_RECALL_DROP


def test_morphe_rigorous_validation():
    print("\n================================================================================")
    print("                     MORPHE RIGOROUS VERIFICATION SUITE                         ")
    print("================================================================================")

    # Clean initial state
    engine = MemoryEngine()
    engine.load_sample_data()

    results_table = []

    # ---------------------------------------------------------
    # 1. Baseline Evaluation
    # ---------------------------------------------------------
    v1_metrics = engine.evaluate_benchmark(top_k=4)
    print(f"\n[1] Initial State (V1):")
    print(f"    Nodes: {len(engine.graph.nodes)}, Edges: {len(engine.graph.edges)}")
    print(f"    Baseline Recall@4: {v1_metrics['mean_recall']:.4f}, Precision@4: {v1_metrics['mean_precision']:.4f}, Latency: {v1_metrics['mean_latency_ms']:.2f}ms")
    assert len(engine.graph.nodes) == 7
    assert len(engine.records) == 46

    # Flat baseline comparison
    flat_comp = engine.evaluate_flat_baseline(top_k=4)
    print(f"    Flat Vector Baseline Recall@4: {flat_comp['flat_baseline']['mean_recall']:.4f}")
    print(f"    Graph vs Flat Recall Delta:    {flat_comp['delta']['recall_delta']:+.4f}")

    # ---------------------------------------------------------
    # 2. Diagnosing Weaknesses (Explicit Triggers)
    # ---------------------------------------------------------
    weaknesses = engine.diagnose_weaknesses()
    print(f"\n[2] Explicit Weakness Diagnostics: Found {len(weaknesses)} issue(s)")
    for w in weaknesses:
        print(f"    - [{w['proposed_op']}] Signal: {w['signal']} -> Targets: {w['target_modules']}")
        print(f"      Measured: {w['measured_value']} | Threshold: {w['threshold']}")
    
    assert any(w["proposed_op"] == "SPLIT" for w in weaknesses)
    assert any(w["proposed_op"] == "MERGE" for w in weaknesses)

    # ---------------------------------------------------------
    # 3. Test SPLIT on Overloaded Mixed Module
    # ---------------------------------------------------------
    before_recall = engine.history[-1]["metrics"]["mean_recall"]
    before_lat = engine.history[-1]["metrics"]["mean_latency_ms"]

    split_res = engine.execute_guarded_adaptation("SPLIT", {"module_id": "MOD_MIXED_CORE"})
    after_recall = split_res["after_recall"]
    after_lat = split_res["metrics"]["mean_latency_ms"]
    
    print(f"\n[3] Executed SPLIT on 'MOD_MIXED_CORE':")
    print(f"    Status: {split_res['decision']}")
    print(f"    Recall: {before_recall:.4f} -> {after_recall:.4f} (Delta: {split_res['delta_recall']:+.4f})")
    print(f"    Latency: {before_lat:.2f}ms -> {after_lat:.2f}ms")
    assert split_res["decision"] in ("ACCEPTED", "NEUTRAL")
    assert "MOD_MIXED_CORE" not in engine.modules
    assert "MOD_MIXED_CORE_A" in engine.modules
    assert "MOD_MIXED_CORE_B" in engine.modules

    results_table.append({
        "op": "SPLIT",
        "signal": "OVERLOADED_SIZE_AND_VARIANCE",
        "before_recall": before_recall,
        "after_recall": after_recall,
        "latency": after_lat,
        "outcome": split_res["decision"]
    })

    # ---------------------------------------------------------
    # 4. Test MERGE on Redundant Vector Modules
    # ---------------------------------------------------------
    before_recall = engine.history[-1]["metrics"]["mean_recall"]
    before_lat = engine.history[-1]["metrics"]["mean_latency_ms"]

    merge_res = engine.execute_guarded_adaptation("MERGE", {
        "module_a": "MOD_VECTOR_INDEX",
        "module_b": "MOD_EMBEDDING_RETRIEVAL"
    })
    after_recall = merge_res["after_recall"]
    after_lat = merge_res["metrics"]["mean_latency_ms"]

    print(f"\n[4] Executed MERGE on 'MOD_VECTOR_INDEX' + 'MOD_EMBEDDING_RETRIEVAL':")
    print(f"    Status: {merge_res['decision']}")
    print(f"    Recall: {before_recall:.4f} -> {after_recall:.4f} (Delta: {merge_res['delta_recall']:+.4f})")
    print(f"    Latency: {before_lat:.2f}ms -> {after_lat:.2f}ms")
    assert merge_res["decision"] in ("ACCEPTED", "NEUTRAL")

    results_table.append({
        "op": "MERGE",
        "signal": "REDUNDANT_CENTROID_SIMILARITY",
        "before_recall": before_recall,
        "after_recall": after_recall,
        "latency": after_lat,
        "outcome": merge_res["decision"]
    })

    # ---------------------------------------------------------
    # 5. Test SHORTCUT on Frequently Co-accessed Modules
    # ---------------------------------------------------------
    # Run cross-module queries (Q12, Q13) to register co-access telemetry
    engine.search("How do Pandas DataFrames integrate with PyTorch DataLoaders in end-to-end training workflows?")
    engine.search("How does NumPy array preprocessing feed into neural network tensor transformations?")
    engine.search("Combine dataframe feature processing and PyTorch neural network training")

    before_recall = engine.history[-1]["metrics"]["mean_recall"]
    before_lat = engine.history[-1]["metrics"]["mean_latency_ms"]

    shortcut_res = engine.execute_guarded_adaptation("SHORTCUT", {
        "module_a": "MOD_PYTHON_DATA",
        "module_b": "MOD_ML_MODELS"
    })
    after_recall = shortcut_res["after_recall"]
    after_lat = shortcut_res["metrics"]["mean_latency_ms"]

    print(f"\n[5] Executed SHORTCUT between 'MOD_PYTHON_DATA' and 'MOD_ML_MODELS':")
    print(f"    Status: {shortcut_res['decision']}")
    print(f"    Recall: {before_recall:.4f} -> {after_recall:.4f} (Delta: {shortcut_res['delta_recall']:+.4f})")
    print(f"    Latency: {before_lat:.2f}ms -> {after_lat:.2f}ms")
    assert shortcut_res["decision"] in ("ACCEPTED", "NEUTRAL")
    assert engine.graph.has_edge("MOD_PYTHON_DATA", "MOD_ML_MODELS")

    results_table.append({
        "op": "SHORTCUT",
        "signal": "REPEATED_QUERY_CO_ACCESS",
        "before_recall": before_recall,
        "after_recall": after_recall,
        "latency": after_lat,
        "outcome": shortcut_res["decision"]
    })

    # ---------------------------------------------------------
    # 6. STEP 4: Genuine Rejection Demo under DEFAULT Thresholds
    # ---------------------------------------------------------
    # Capture deep snapshot of state before the bad operation
    pre_op_nodes = copy.deepcopy(sorted(list(engine.graph.nodes(data=True))))
    pre_op_edges = copy.deepcopy(sorted(list(engine.graph.edges(data=True))))
    pre_op_modules = copy.deepcopy(engine.modules)
    pre_op_records = copy.deepcopy(engine.records)
    pre_op_version = engine.history[-1]["version"]
    before_recall = engine.history[-1]["metrics"]["mean_recall"]

    print(f"\n[6] STEP 4 Genuine Rejection Demo (Under DEFAULT thresholds: min={MIN_ACCEPTABLE_RECALL}, drop_eps={MAX_ALLOWABLE_RECALL_DROP}):")
    print(f"    Attempting destructive MERGE between unrelated modules: 'MOD_MIXED_CORE_B' (Java OOP) and 'MOD_PYTHON_DATA' (Python Data)...")
    
    # Destructive merge of two completely distinct domains (Java OOP + Python)
    bad_merge_res = engine.execute_guarded_adaptation("MERGE", {
        "module_a": "MOD_MIXED_CORE_B",
        "module_b": "MOD_PYTHON_DATA"
    })

    print(f"    Result: {bad_merge_res['decision']}")
    print(f"    Reason: {bad_merge_res['reason']}")
    print(f"    Recall before: {bad_merge_res['before_recall']:.4f} -> Failed recall: {bad_merge_res['failed_recall']:.4f} (Delta: {bad_merge_res['delta_recall']:+.4f})")
    print(f"    Restored Version: {bad_merge_res['restored_version']}")
    
    assert bad_merge_res["decision"] == "REJECTED"
    assert bad_merge_res["failed_recall"] < bad_merge_res["before_recall"]

    # Assert deep-equality of state restoration after rollback
    post_rollback_nodes = sorted(list(engine.graph.nodes(data=True)))
    post_rollback_edges = sorted(list(engine.graph.edges(data=True)))

    assert [n[0] for n in post_rollback_nodes] == [n[0] for n in pre_op_nodes], "Node keys must match exactly after rollback!"
    assert [(e[0], e[1]) for e in post_rollback_edges] == [(e[0], e[1]) for e in pre_op_edges], "Edge pairs must match exactly after rollback!"
    assert engine.modules.keys() == pre_op_modules.keys(), "Module assignment keys must match exactly after rollback!"
    for mid, mdata in engine.modules.items():
        assert mdata["record_ids"] == pre_op_modules[mid]["record_ids"], f"Module {mid} records must match exactly!"
    assert engine.records == pre_op_records, "Record metadata must be deep equal after rollback!"
    print("    [PASS] Deep equality assertion confirmed: Graph structure, module assignments, and records are identical to pre-op snapshot!")

    results_table.append({
        "op": "MERGE (Unrelated)",
        "signal": "ARTIFICIAL_DESTRUCTIVE_MERGE",
        "before_recall": bad_merge_res["before_recall"],
        "after_recall": bad_merge_res["failed_recall"],
        "latency": engine.history[-1]["metrics"]["mean_latency_ms"],
        "outcome": "REJECTED (Rolled back)"
    })

    # ---------------------------------------------------------
    # 7. STEP 1 Ingestion Test
    # ---------------------------------------------------------
    print("\n[7] Testing Ingestion Pipeline (POST /api/ingest):")
    sample_text = "Rust memory safety is guaranteed by its ownership and borrowing system without a garbage collector. Lifetimes prevent dangling pointer dereferences."
    ingest_res = engine.ingest_text(raw_text=sample_text, topic="rust_safety")
    print(f"    Ingested {ingest_res['ingested_records']} record(s). Created module: {ingest_res['records'][0]['module_id']}")
    assert ingest_res["ingested_records"] >= 1
    assert any(rec["module_id"].startswith("MOD_RUST_SAFETY") for rec in ingest_res["records"])

    # ---------------------------------------------------------
    # 8. Results Summary Table
    # ---------------------------------------------------------
    print("\n" + "=" * 90)
    print(f"{'OPERATION':<20} | {'TRIGGER SIGNAL':<30} | {'BEFORE':<8} | {'AFTER':<8} | {'LATENCY':<8} | {'OUTCOME'}")
    print("-" * 90)
    for r in results_table:
        print(f"{r['op']:<20} | {r['signal']:<30} | {r['before_recall']:<8.4f} | {r['after_recall']:<8.4f} | {r['latency']:>5.2f}ms | {r['outcome']}")
    print("=" * 90)


if __name__ == "__main__":
    test_morphe_rigorous_validation()
