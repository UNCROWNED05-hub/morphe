from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ConfigModel:
    k: int
    min_recall: float
    thresholds: Dict[str, Any]
    model: str
    corpus_label: str
    seed: int


@dataclass
class RecordModel:
    id: str
    text: str
    source: str
    timestamp: Any
    topic: str
    module_id: str


@dataclass
class QueryResultItem:
    record_id: str
    text: str
    score: float
    module_id: str


@dataclass
class QueryResult:
    query: str
    k: int
    results: List[QueryResultItem]
    modules_accessed: List[str]
    path: List[List[str]]
    latency_ms: float


@dataclass
class ModuleDetail:
    id: str
    label: str
    record_ids: List[str]
    neighbors: List[str]
    access_count: int


@dataclass
class SignalData:
    utilization: Dict[str, int]
    coaccess: List[Dict[str, Any]]
    overloaded: List[str]
    redundant_pairs: List[List[str]]
    thresholds: Dict[str, Any]


@dataclass
class ProposalModel:
    op: str
    targets: List[str]
    signal: str
    value: float
    threshold: float
    reason: str


@dataclass
class MetricsModel:
    recall_at_k: float
    precision_at_k: float
    mean_latency_ms: float
    mean_modules_accessed: float


@dataclass
class AdaptationCycleResult:
    proposal: Dict[str, Any]
    before: MetricsModel
    after: MetricsModel
    decision: str
    reason: str
    version_id: str
    rolled_back: bool


@dataclass
class VersionModel:
    id: str
    parent_id: Optional[str]
    operation: str
    reason: str
    timestamp: float
    status: str
    metrics: MetricsModel
    graph: Dict[str, Any]


@dataclass
class PerQueryEval:
    query: str
    expected: List[str]
    retrieved: List[str]
    recall: float
    precision: float
    latency_ms: float


@dataclass
class EvaluationResult:
    metrics: MetricsModel
    per_query: List[PerQueryEval]


class EngineContractError(Exception):
    """Raised when the engine does not conform to the expected interface."""
    def __init__(self, missing_fields: List[str], view_name: str = ""):
        self.missing_fields = missing_fields
        self.view_name = view_name
        msg = f"EngineContractError: Missing functions or fields: {', '.join(missing_fields)}"
        if view_name:
            msg += f" (required by view '{view_name}')"
        super().__init__(msg)
