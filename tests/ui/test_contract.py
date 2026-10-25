import pytest
from ui.models import (
    ConfigModel,
    RecordModel,
    QueryResult,
    ModuleDetail,
    SignalData,
    ProposalModel,
    MetricsModel,
    AdaptationCycleResult,
    VersionModel,
    EvaluationResult,
    EngineContractError
)
from ui.adapter import EngineAdapter


class MockValidEngine:
    def __init__(self):
        self.k = 4
        self.min_recall = 0.70
        self.model = "test-model"
        self.corpus_label = "synthetic"

    def get_config(self):
        return {
            "k": 4,
            "min_recall": 0.70,
            "thresholds": {"split_min_module_size": 10},
            "model": "test-model",
            "corpus_label": "synthetic",
            "seed": 42
        }

    def reset(self):
        pass

    def load_sample(self, path="sample_data.json"):
        return {"records": 60, "modules": 7, "queries": 16}

    def add_memory(self, text: str, source: str = "user"):
        return [{"id": "REC_NEW_1", "text": text, "source": source, "timestamp": 0, "topic": "gen", "module_id": "MOD_1"}]

    def list_records(self):
        return [{"id": "REC_1", "text": "sample text", "source": "corpus", "timestamp": 0, "topic": "test", "module_id": "MOD_1"}]

    def query(self, text: str, k=None):
        return {
            "query": text,
            "k": 4,
            "results": [{"record_id": "REC_1", "text": "hit", "score": 0.95, "module_id": "MOD_1"}],
            "modules_accessed": ["MOD_1"],
            "path": [],
            "latency_ms": 1.2
        }

    def get_graph(self):
        import networkx as nx
        G = nx.Graph()
        G.add_node("MOD_1", label="Module 1", record_ids=["REC_1"], topic="test")
        return G

    def get_module(self, module_id):
        return {"id": module_id, "label": "Module 1", "record_ids": ["REC_1"], "neighbors": [], "access_count": 5}

    def get_signals(self):
        return {"utilization": {"MOD_1": 5}, "coaccess": [], "overloaded": [], "redundant_pairs": [], "thresholds": {}}

    def propose(self):
        return [{"op": "split", "targets": ["MOD_1"], "signal": "OVERLOAD", "value": 15, "threshold": 10, "reason": "overcrowded"}]

    def run_adaptation_cycle(self, proposal=None):
        return {
            "proposal": {"op": "split"},
            "before": {"recall_at_k": 0.8, "precision_at_k": 0.6, "mean_latency_ms": 2.0, "mean_modules_accessed": 1.5},
            "after": {"recall_at_k": 0.85, "precision_at_k": 0.65, "mean_latency_ms": 1.9, "mean_modules_accessed": 1.4},
            "decision": "accepted",
            "reason": "Recall improved",
            "version_id": "V2",
            "rolled_back": False
        }

    def eval_queries(self):
        return [{"id": "Q1", "query": "test query", "relevant_ids": ["REC_1"]}]

    def evaluate(self):
        return {
            "metrics": {"recall_at_k": 0.85, "precision_at_k": 0.65, "mean_latency_ms": 2.0, "mean_modules_accessed": 1.5},
            "per_query": []
        }

    def baseline_evaluate(self):
        return {"flat_baseline": {"mean_recall": 0.75}}

    def list_versions(self):
        return [{
            "id": "V1",
            "parent_id": None,
            "operation": "Initial",
            "reason": "Baseline",
            "timestamp": 1000.0,
            "status": "ACCEPTED",
            "metrics": {"recall_at_k": 0.8, "precision_at_k": 0.6, "mean_latency_ms": 2.0, "mean_modules_accessed": 1.5},
            "graph": {}
        }]

    def restore(self, version_id):
        return {"restored": version_id}


def test_adapter_conformance_with_mock():
    mock = MockValidEngine()
    adapter = EngineAdapter(engine=mock)

    cfg = adapter.get_config()
    assert isinstance(cfg, ConfigModel)
    assert cfg.k == 4

    recs = adapter.list_records()
    assert len(recs) == 1
    assert isinstance(recs[0], RecordModel)

    res = adapter.query("test")
    assert isinstance(res, QueryResult)
    assert res.latency_ms == 1.2

    graph = adapter.get_graph()
    assert "MOD_1" in graph.nodes

    mod = adapter.get_module("MOD_1")
    assert isinstance(mod, ModuleDetail)

    sig = adapter.get_signals()
    assert isinstance(sig, SignalData)

    props = adapter.propose()
    assert len(props) == 1
    assert isinstance(props[0], ProposalModel)

    cycle = adapter.run_adaptation_cycle(props[0])
    assert isinstance(cycle, AdaptationCycleResult)
    assert cycle.decision == "accepted"

    vers = adapter.list_versions()
    assert len(vers) == 1
    assert isinstance(vers[0], VersionModel)


def test_adapter_with_real_engine():
    from engine.memory_engine import MemoryEngine
    real_engine = MemoryEngine()
    real_engine.load_sample_data()
    adapter = EngineAdapter(engine=real_engine)

    cfg = adapter.get_config()
    assert cfg.k == 4
    assert cfg.model == "all-MiniLM-L6-v2"

    recs = adapter.list_records()
    assert len(recs) > 0

    graph = adapter.get_graph()
    assert len(graph.nodes) > 0

    res = adapter.query("What Java concepts should I study?")
    assert len(res.results) > 0
    assert res.latency_ms > 0

