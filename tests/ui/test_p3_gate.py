import pytest
from ui.adapter import EngineAdapter
from ui.models import ProposalModel

def test_p3_gate_accepted_rejected_and_restore():
    adapter = EngineAdapter()
    adapter.reset()

    # Initial state: V1
    init_versions = adapter.list_versions()
    assert len(init_versions) >= 1
    assert init_versions[0].id == "V1"

    # 1. Real ACCEPTED operation: SPLIT on overloaded MOD_MIXED_CORE
    split_prop = ProposalModel(
        op="split",
        targets=["MOD_MIXED_CORE"],
        signal="OVERLOAD",
        value=14,
        threshold=10,
        reason="Overcrowded mixed topic"
    )
    cycle_1 = adapter.run_adaptation_cycle(split_prop)
    assert cycle_1.decision in ("accepted", "neutral")
    assert not cycle_1.rolled_back
    post_split_nodes = set(adapter.get_graph().nodes())
    assert "MOD_MIXED_CORE" not in post_split_nodes
    assert "MOD_MIXED_CORE_A" in post_split_nodes
    assert "MOD_MIXED_CORE_B" in post_split_nodes

    # 2. Real REJECTED operation with visible rollback:
    # Attempting to MERGE unrelated modules with min_recall_threshold=0.95 triggers guardrail rejection
    raw_rejected = adapter.engine.execute_guarded_adaptation(
        "MERGE",
        {"module_a": "MOD_VECTOR_INDEX", "module_b": "MOD_MIXED_CORE_A"},
        min_recall_threshold=0.95
    )
    assert raw_rejected["decision"] == "REJECTED"
    assert "restored_version" in raw_rejected
    # Verify rollback restored the accepted split state: MOD_MIXED_CORE_A is preserved!
    assert "MOD_MIXED_CORE_A" in adapter.get_graph().nodes()
    assert "MOD_VECTOR_INDEX" in adapter.get_graph().nodes()

    # 3. Restore to earlier version V1
    restore_res = adapter.restore("V1")
    assert restore_res["restored_version"] == "V1"
    restored_nodes = set(adapter.get_graph().nodes())
    # MOD_MIXED_CORE is back in V1!
    assert "MOD_MIXED_CORE" in restored_nodes
    assert "MOD_MIXED_CORE_A" not in restored_nodes
