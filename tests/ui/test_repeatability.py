import pytest
from ui.adapter import EngineAdapter
from ui.models import ProposalModel

def test_determinism_and_repeatability():
    adapter = EngineAdapter()
    
    # Run 1
    adapter.reset()
    props1 = adapter.propose()
    assert len(props1) > 0
    p1 = props1[0]
    cycle1 = adapter.run_adaptation_cycle(p1)
    dec1 = cycle1.decision
    rec1_before = round(cycle1.before.recall_at_k, 4)
    rec1_after = round(cycle1.after.recall_at_k, 4)

    # Run 2
    adapter.reset()
    props2 = adapter.propose()
    assert len(props2) > 0
    p2 = props2[0]
    cycle2 = adapter.run_adaptation_cycle(p2)
    dec2 = cycle2.decision
    rec2_before = round(cycle2.before.recall_at_k, 4)
    rec2_after = round(cycle2.after.recall_at_k, 4)

    # Must give identical decisions and metrics except latency
    assert dec1 == dec2, f"Decisions must be identical across resets: {dec1} vs {dec2}"
    assert rec1_before == rec2_before, f"Before recalls must be identical: {rec1_before} vs {rec2_before}"
    assert rec1_after == rec2_after, f"After recalls must be identical: {rec1_after} vs {rec2_after}"
