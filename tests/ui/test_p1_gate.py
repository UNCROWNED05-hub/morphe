import pytest
from ui.adapter import EngineAdapter

def test_p1_gate_load_and_query():
    adapter = EngineAdapter()
    adapter.load_sample()
    
    # Run the exact BRIEF example query
    query_str = "What Java concepts should I study?"
    result = adapter.query(text=query_str, k=4)
    
    assert result.query == query_str
    assert len(result.results) > 0
    assert result.latency_ms > 0
    assert len(result.modules_accessed) > 0
    
    # Check that scores and records exist and are non-empty
    for item in result.results:
        assert item.record_id
        assert item.text
        assert item.score > 0
        assert item.module_id

    # Verify records ledger has records
    records = adapter.list_records()
    assert len(records) >= 60
