from typing import List, Dict, Any, Optional
import networkx as nx
import streamlit as st

from ui.models import (
    ConfigModel,
    RecordModel,
    QueryResultItem,
    QueryResult,
    ModuleDetail,
    SignalData,
    ProposalModel,
    MetricsModel,
    AdaptationCycleResult,
    VersionModel,
    PerQueryEval,
    EvaluationResult,
    EngineContractError
)


@st.cache_resource
def get_cached_engine_instance():
    """Initializes and caches the underlying engine once across reruns."""
    try:
        from engine.memory_engine import MemoryEngine
        engine = MemoryEngine()
        engine.load_sample_data()
        return engine
    except Exception as e:
        raise EngineContractError([f"Engine initialization failed: {str(e)}"])


class EngineAdapter:
    """Only importer and normalizer for the MemoryEngine."""

    def __init__(self, engine=None):
        if engine is not None:
            self.engine = engine
        elif "morphe_engine" in st.session_state:
            self.engine = st.session_state["morphe_engine"]
        else:
            self.engine = get_cached_engine_instance()
            st.session_state["morphe_engine"] = self.engine

    def get_config(self) -> ConfigModel:
        if hasattr(self.engine, "get_config"):
            cfg = self.engine.get_config()
            return ConfigModel(
                k=cfg.get("k", 4),
                min_recall=cfg.get("min_recall", 0.70),
                thresholds=cfg.get("thresholds", {}),
                model=cfg.get("model", "all-MiniLM-L6-v2"),
                corpus_label=cfg.get("corpus_label", "synthetic"),
                seed=cfg.get("seed", 42)
            )
        # Adapt from Person 2's config / engine attributes
        try:
            from engine.config import (
                MIN_ACCEPTABLE_RECALL,
                SPLIT_MIN_MODULE_SIZE,
                SPLIT_MIN_SILHOUETTE,
                MERGE_COSINE_SIM_THRESHOLD,
                SHORTCUT_MIN_CO_ACCESS,
                SPLIT_KMEANS_RANDOM_STATE
            )
            return ConfigModel(
                k=4,
                min_recall=MIN_ACCEPTABLE_RECALL,
                thresholds={
                    "split_min_module_size": SPLIT_MIN_MODULE_SIZE,
                    "split_min_silhouette": SPLIT_MIN_SILHOUETTE,
                    "merge_cosine_threshold": MERGE_COSINE_SIM_THRESHOLD,
                    "shortcut_min_co_access": SHORTCUT_MIN_CO_ACCESS
                },
                model="all-MiniLM-L6-v2",
                corpus_label="synthetic",
                seed=SPLIT_KMEANS_RANDOM_STATE
            )
        except Exception as e:
            raise EngineContractError([f"get_config failed: {e}"], view_name="Overview")

    def reset(self) -> None:
        if hasattr(self.engine, "reset"):
            self.engine.reset()
        elif hasattr(self.engine, "load_sample_data"):
            self.engine.load_sample_data()
        else:
            raise EngineContractError(["reset or load_sample_data"], view_name="Memory")

    def load_sample(self, path: str = "sample_data.json") -> Dict[str, Any]:
        if hasattr(self.engine, "load_sample"):
            return self.engine.load_sample(path)
        elif hasattr(self.engine, "load_sample_data"):
            self.engine.load_sample_data()
            return {
                "records": len(self.engine.records),
                "modules": len(self.engine.modules),
                "queries": len(self.engine.benchmark_queries)
            }
        else:
            raise EngineContractError(["load_sample or load_sample_data"], view_name="Memory")

    def add_memory(self, text: str, source: str = "user") -> List[RecordModel]:
        if hasattr(self.engine, "add_memory"):
            res = self.engine.add_memory(text, source)
        elif hasattr(self.engine, "ingest_text"):
            res = self.engine.ingest_text(raw_text=text, source=source)
            records = res.get("assigned_records", [])
            return [
                RecordModel(
                    id=r["id"],
                    text=r["text"],
                    source=source,
                    timestamp=r.get("timestamp", 0),
                    topic=r.get("topic", "general"),
                    module_id=r.get("module_id", "")
                )
                for r in records
            ]
        else:
            raise EngineContractError(["add_memory or ingest_text"], view_name="Memory")
        return [
            RecordModel(
                id=r["id"],
                text=r["text"],
                source=r.get("source", source),
                timestamp=r.get("timestamp", 0),
                topic=r.get("topic", "general"),
                module_id=r.get("module_id", "")
            )
            for r in res
        ]

    def list_records(self) -> List[RecordModel]:
        if hasattr(self.engine, "list_records"):
            records_data = self.engine.list_records()
        elif hasattr(self.engine, "records"):
            records_data = list(self.engine.records.values())
        else:
            raise EngineContractError(["list_records or records"], view_name="Memory")

        return [
            RecordModel(
                id=r["id"],
                text=r["text"],
                source=r.get("source", "corpus"),
                timestamp=r.get("timestamp", 0),
                topic=r.get("topic", "general"),
                module_id=r.get("module_id", "")
            )
            for r in records_data
        ]

    def query(self, text: str, k: Optional[int] = None) -> QueryResult:
        k_val = k if k is not None else 4
        if hasattr(self.engine, "query"):
            res = self.engine.query(text, k_val)
        elif hasattr(self.engine, "search"):
            res = self.engine.search(query=text, top_k=k_val)
        else:
            raise EngineContractError(["query or search"], view_name="Retrieve")

        items = [
            QueryResultItem(
                record_id=hit.get("record_id", hit.get("id", "")),
                text=hit.get("text", ""),
                score=float(hit.get("score", hit.get("similarity", 0.0))),
                module_id=hit.get("module_id", "")
            )
            for hit in res.get("results", [])
        ]
        visited = res.get("modules_accessed", res.get("visited_modules", []))
        primary = res.get("primary_module", visited[0] if visited else "")
        computed_path = res.get("path", [])
        if not computed_path and primary and len(visited) > 1:
            computed_path = [[primary, v] for v in visited if v != primary]

        return QueryResult(
            query=res.get("query", text),
            k=res.get("top_k", k_val),
            results=items,
            modules_accessed=visited,
            path=computed_path,
            latency_ms=float(res.get("latency_ms", 0.0))
        )

    def get_graph(self) -> nx.Graph:
        if hasattr(self.engine, "get_graph"):
            return self.engine.get_graph()
        elif hasattr(self.engine, "graph"):
            return self.engine.graph
        else:
            raise EngineContractError(["get_graph or graph"], view_name="Graph")

    def get_module(self, module_id: str) -> ModuleDetail:
        if hasattr(self.engine, "get_module"):
            m = self.engine.get_module(module_id)
            return ModuleDetail(
                id=m["id"],
                label=m.get("label", m.get("name", module_id)),
                record_ids=m.get("record_ids", []),
                neighbors=m.get("neighbors", []),
                access_count=m.get("access_count", 0)
            )
        elif hasattr(self.engine, "modules"):
            m = self.engine.modules.get(module_id, {})
            neighbors = list(self.engine.graph.neighbors(module_id)) if module_id in self.engine.graph else []
            return ModuleDetail(
                id=module_id,
                label=m.get("name", m.get("label", module_id)),
                record_ids=m.get("record_ids", []),
                neighbors=neighbors,
                access_count=m.get("access_count", 0)
            )
        else:
            raise EngineContractError(["get_module or modules"], view_name="Graph")

    def get_signals(self) -> SignalData:
        if hasattr(self.engine, "get_signals"):
            sig = self.engine.get_signals()
            return SignalData(
                utilization=sig.get("utilization", {}),
                coaccess=sig.get("coaccess", []),
                overloaded=sig.get("overloaded", []),
                redundant_pairs=sig.get("redundant_pairs", []),
                thresholds=sig.get("thresholds", {})
            )
        # Adapt from Person 2's engine telemetry
        try:
            weaknesses = self.engine.diagnose_weaknesses() if hasattr(self.engine, "diagnose_weaknesses") else []
            overloaded = [w["target_module_id"] for w in weaknesses if w.get("operation") == "SPLIT"]
            redundant_pairs = [[w["target_module_a"], w["target_module_b"]] for w in weaknesses if w.get("operation") == "MERGE"]
            utilization = {mid: m.get("access_count", 0) for mid, m in self.engine.modules.items()}
            coaccess = [
                {"a": k[0], "b": k[1], "count": count}
                for k, count in getattr(self.engine, "query_co_access_counts", {}).items()
            ]
            cfg = self.get_config()
            return SignalData(
                utilization=utilization,
                coaccess=coaccess,
                overloaded=overloaded,
                redundant_pairs=redundant_pairs,
                thresholds=cfg.thresholds
            )
        except Exception as e:
            raise EngineContractError([f"get_signals failed: {e}"], view_name="Adapt")

    def propose(self) -> List[ProposalModel]:
        if hasattr(self.engine, "propose"):
            props = self.engine.propose()
            return [
                ProposalModel(
                    op=p["op"],
                    targets=p["targets"],
                    signal=p["signal"],
                    value=p["value"],
                    threshold=p["threshold"],
                    reason=p["reason"]
                )
                for p in props
            ]
        # Adapt from Person 2's diagnose_weaknesses
        try:
            weaknesses = self.engine.diagnose_weaknesses()
            proposals = []
            for w in weaknesses:
                op = w["operation"].lower()
                targets = []
                if "target_module_id" in w:
                    targets = [w["target_module_id"]]
                elif "target_module_a" in w and "target_module_b" in w:
                    targets = [w["target_module_a"], w["target_module_b"]]
                proposals.append(
                    ProposalModel(
                        op=op,
                        targets=targets,
                        signal=w.get("weakness_type", ""),
                        value=float(w.get("measured_value", 0.0)),
                        threshold=float(w.get("threshold_value", 0.0)),
                        reason=w.get("explanation", "")
                    )
                )
            return proposals
        except Exception as e:
            raise EngineContractError([f"propose failed: {e}"], view_name="Adapt")

    def run_adaptation_cycle(self, proposal: Optional[ProposalModel] = None) -> AdaptationCycleResult:
        if hasattr(self.engine, "run_adaptation_cycle"):
            prop_dict = {
                "op": proposal.op,
                "targets": proposal.targets,
                "signal": proposal.signal,
                "value": proposal.value,
                "threshold": proposal.threshold,
                "reason": proposal.reason
            } if proposal else None
            res = self.engine.run_adaptation_cycle(prop_dict)
            return AdaptationCycleResult(
                proposal=res.get("proposal", {}),
                before=MetricsModel(**res["before"]),
                after=MetricsModel(**res["after"]),
                decision=res.get("decision", "rejected"),
                reason=res.get("reason", ""),
                version_id=res.get("version_id", ""),
                rolled_back=res.get("rolled_back", False)
            )
        # Adapt from Person 2's execute_guarded_adaptation
        try:
            if not proposal:
                proposals = self.propose()
                if not proposals:
                    raise Exception("No adaptation proposal available to execute")
                proposal = proposals[0]

            op_type = proposal.op.upper()
            params = {}
            if op_type == "SPLIT":
                params["module_id"] = proposal.targets[0]
            elif op_type in ("MERGE", "SHORTCUT"):
                params["module_a"] = proposal.targets[0]
                params["module_b"] = proposal.targets[1]

            cfg = self.get_config()
            raw_res = self.engine.execute_guarded_adaptation(
                op_type=op_type,
                params=params,
                min_recall_threshold=cfg.min_recall
            )
            decision = raw_res.get("decision", raw_res.get("status", "accepted")).lower()
            version_id = raw_res.get("version", "")
            reason = raw_res.get("reason", f"Decision: {decision.upper()}")
            rolled_back = (decision == "rejected")

            before_recall = raw_res.get("before_recall", 0.0)
            after_recall = raw_res.get("after_recall", raw_res.get("failed_recall", 0.0))
            metrics_dict = raw_res.get("metrics", raw_res.get("current_metrics", {}))

            before_m = MetricsModel(
                recall_at_k=float(before_recall),
                precision_at_k=float(metrics_dict.get("mean_precision", 0.5)),
                mean_latency_ms=float(metrics_dict.get("mean_latency_ms", 10.0)),
                mean_modules_accessed=float(metrics_dict.get("mean_modules_accessed", 2.0))
            )
            after_m = MetricsModel(
                recall_at_k=float(after_recall),
                precision_at_k=float(metrics_dict.get("mean_precision", 0.5)),
                mean_latency_ms=float(metrics_dict.get("mean_latency_ms", 10.0)),
                mean_modules_accessed=float(metrics_dict.get("mean_modules_accessed", 2.0))
            )

            return AdaptationCycleResult(
                proposal={
                    "op": proposal.op,
                    "targets": proposal.targets,
                    "signal": proposal.signal,
                    "value": proposal.value,
                    "threshold": proposal.threshold,
                    "reason": proposal.reason
                },
                before=before_m,
                after=after_m,
                decision=decision,
                reason=reason,
                version_id=version_id,
                rolled_back=rolled_back
            )
        except Exception as e:
            raise EngineContractError([f"run_adaptation_cycle failed: {e}"], view_name="Adapt")

    def eval_queries(self) -> List[Dict[str, Any]]:
        if hasattr(self.engine, "eval_queries"):
            return self.engine.eval_queries()
        elif hasattr(self.engine, "benchmark_queries"):
            return self.engine.benchmark_queries
        else:
            raise EngineContractError(["eval_queries or benchmark_queries"], view_name="Retrieve")

    def evaluate(self) -> EvaluationResult:
        if hasattr(self.engine, "evaluate"):
            res = self.engine.evaluate()
            return EvaluationResult(
                metrics=MetricsModel(**res["metrics"]),
                per_query=[PerQueryEval(**pq) for pq in res.get("per_query", [])]
            )
        # Adapt from Person 2's evaluate_benchmark
        try:
            raw = self.engine.evaluate_benchmark(top_k=4)
            per_query_list = []
            for pq in raw.get("query_evaluations", []):
                per_query_list.append(
                    PerQueryEval(
                        query=pq["query"],
                        expected=pq["expected_record_ids"],
                        retrieved=pq["retrieved_record_ids"],
                        recall=float(pq["recall_at_k"]),
                        precision=float(pq["precision_at_k"]),
                        latency_ms=float(pq["latency_ms"])
                    )
                )
            return EvaluationResult(
                metrics=MetricsModel(
                    recall_at_k=float(raw["mean_recall"]),
                    precision_at_k=float(raw["mean_precision"]),
                    mean_latency_ms=float(raw["mean_latency_ms"]),
                    mean_modules_accessed=float(raw.get("mean_modules_accessed", 2.0))
                ),
                per_query=per_query_list
            )
        except Exception as e:
            raise EngineContractError([f"evaluate failed: {e}"], view_name="Adapt")

    def baseline_evaluate(self) -> Dict[str, Any]:
        if hasattr(self.engine, "baseline_evaluate"):
            return self.engine.baseline_evaluate()
        elif hasattr(self.engine, "evaluate_flat_baseline"):
            return self.engine.evaluate_flat_baseline(top_k=4)
        else:
            raise EngineContractError(["baseline_evaluate or evaluate_flat_baseline"], view_name="Adapt")

    def list_versions(self) -> List[VersionModel]:
        if hasattr(self.engine, "list_versions"):
            v_list = self.engine.list_versions()
            return [
                VersionModel(
                    id=v["id"],
                    parent_id=v.get("parent_id"),
                    operation=v["operation"],
                    reason=v["reason"],
                    timestamp=float(v["timestamp"]),
                    status=v["status"],
                    metrics=MetricsModel(**v["metrics"]),
                    graph=v.get("graph", {})
                )
                for v in v_list
            ]
        elif hasattr(self.engine, "history"):
            models = []
            for h in self.engine.history:
                m = h["metrics"]
                models.append(
                    VersionModel(
                        id=h["version"],
                        parent_id=None,
                        operation=h.get("version_label", h.get("description", "Snapshot")),
                        reason=h.get("description", ""),
                        timestamp=float(h.get("timestamp", 0.0)),
                        status=h.get("status", "ACCEPTED"),
                        metrics=MetricsModel(
                            recall_at_k=float(m.get("mean_recall", 0.0)),
                            precision_at_k=float(m.get("mean_precision", 0.0)),
                            mean_latency_ms=float(m.get("mean_latency_ms", 0.0)),
                            mean_modules_accessed=float(m.get("mean_modules_accessed", 2.0))
                        ),
                        graph={"nodes": h.get("graph_nodes", []), "edges": h.get("graph_edges", [])}
                    )
                )
            return models
        else:
            raise EngineContractError(["list_versions or history"], view_name="History")

    def restore(self, version_id: str) -> Dict[str, Any]:
        if hasattr(self.engine, "restore"):
            return self.engine.restore(version_id)
        elif hasattr(self.engine, "rollback_to_version"):
            return self.engine.rollback_to_version(version_id)
        else:
            raise EngineContractError(["restore or rollback_to_version"], view_name="History")
