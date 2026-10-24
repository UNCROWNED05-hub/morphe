import copy
import json
import os
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Set
import networkx as nx
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

from engine.config import (
    CHUNK_SIZE_WORDS,
    CHUNK_OVERLAP_WORDS,
    INGEST_NEW_MODULE_SIM_THRESHOLD,
    SPLIT_MIN_MODULE_SIZE,
    SPLIT_MIN_CLUSTER_SIZE,
    SPLIT_MIN_SILHOUETTE,
    SPLIT_KMEANS_RANDOM_STATE,
    SPLIT_KMEANS_N_INIT,
    MERGE_COSINE_SIM_THRESHOLD,
    SHORTCUT_MIN_CO_ACCESS,
    MIN_ACCEPTABLE_RECALL,
    MAX_ALLOWABLE_RECALL_DROP,
    LATENCY_BENCHMARK_RUNS,
    HISTORY_PERSISTENCE_PATH,
    DATASET_PATH
)


class MemoryEngine:
    def __init__(self, data_path: str = DATASET_PATH, state_path: str = HISTORY_PERSISTENCE_PATH, model_name: str = "all-MiniLM-L6-v2"):
        self.data_path = data_path
        self.state_path = state_path
        self.encoder = SentenceTransformer(model_name)

        # Core Graph and storage state
        self.graph = nx.Graph()
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.records: Dict[str, Dict[str, Any]] = {}
        self.record_embeddings: Dict[str, np.ndarray] = {}
        
        # Telemetry: query-level co-access tracking (pure similarity hits, not graph hops)
        self.query_co_access_counts: Dict[Tuple[str, str], int] = {}
        self.benchmark_queries: List[Dict[str, Any]] = []

        # Versioning state
        self.history: List[Dict[str, Any]] = []
        self.version_counter = 1

        # Initialize or restore state
        if os.path.exists(self.state_path):
            self.load_persisted_state()
        else:
            self.load_sample_data(self.data_path)

    # -------------------------------------------------------------
    # STEP 1: INGESTION PIPELINE
    # -------------------------------------------------------------

    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP_WORDS) -> List[str]:
        """Splits raw text into word-based chunks with configurable size and overlap."""
        words = text.strip().split()
        if not words:
            return []
        if len(words) <= chunk_size:
            return [text.strip()]

        chunks = []
        step = max(1, chunk_size - overlap)
        for i in range(0, len(words), step):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
        return chunks

    def ingest_text(
        self,
        raw_text: str,
        source: str = "user_input",
        topic: str = "general",
        chunk_size: int = CHUNK_SIZE_WORDS,
        overlap: int = CHUNK_OVERLAP_WORDS,
        sim_threshold: float = INGEST_NEW_MODULE_SIM_THRESHOLD
    ) -> Dict[str, Any]:
        """
        Chunks text, embeds each chunk, and assigns it to the module with highest
        centroid cosine similarity above sim_threshold (else creates a new module).
        """
        chunks = self.chunk_text(raw_text, chunk_size, overlap)
        if not chunks:
            return {"ingested_records": 0, "records": []}

        ingested_records = []

        for chunk in chunks:
            rec_id = f"REC_{uuid.uuid4().hex[:8].upper()}"
            vec = self.encoder.encode(chunk, convert_to_numpy=True, normalize_embeddings=True)

            assigned_module_id = None
            best_sim = -1.0

            # Compare against existing module centroids
            if self.modules:
                for mod_id, mod in self.modules.items():
                    if mod["centroid"] is not None:
                        sim = float(cosine_similarity(vec.reshape(1, -1), mod["centroid"].reshape(1, -1))[0][0])
                        if sim > best_sim:
                            best_sim = sim
                            assigned_module_id = mod_id

            # If no module matches above threshold, create a new one
            if assigned_module_id is None or best_sim < sim_threshold:
                assigned_module_id = f"MOD_{topic.upper()}_{uuid.uuid4().hex[:4].upper()}"
                self.modules[assigned_module_id] = {
                    "id": assigned_module_id,
                    "name": f"Module {topic.title()}",
                    "description": f"Auto-created module for topic {topic}",
                    "record_ids": [],
                    "centroid": None,
                    "access_count": 0
                }
                self.graph.add_node(assigned_module_id, **self.modules[assigned_module_id])

            # Store record and metadata
            self.records[rec_id] = {
                "id": rec_id,
                "text": chunk,
                "source": source,
                "timestamp": time.time(),
                "topic": topic,
                "module_id": assigned_module_id
            }
            self.record_embeddings[rec_id] = vec
            self.modules[assigned_module_id]["record_ids"].append(rec_id)

            ingested_records.append({
                "record_id": rec_id,
                "module_id": assigned_module_id,
                "similarity_to_centroid": round(best_sim, 4) if best_sim >= 0 else None,
                "text_snippet": chunk[:60] + ("..." if len(chunk) > 60 else "")
            })

        self.recompute_all_centroids()
        return {
            "ingested_records": len(ingested_records),
            "records": ingested_records,
            "total_modules": len(self.modules)
        }

    def load_sample_data(self, data_path: Optional[str] = None):
        """Loads benchmark data through the pipeline and initializes V1 snapshot."""
        path = data_path or self.data_path
        if not os.path.exists(path):
            raise FileNotFoundError(f"Benchmark file not found at {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.benchmark_queries = data.get("benchmark_queries", [])
        self.graph.clear()
        self.modules.clear()
        self.records.clear()
        self.record_embeddings.clear()
        self.query_co_access_counts.clear()

        # Ingest benchmark modules
        for mod in data.get("modules", []):
            mod_id = mod["id"]
            self.modules[mod_id] = {
                "id": mod_id,
                "name": mod["name"],
                "description": mod.get("description", ""),
                "record_ids": [r["id"] for r in mod["records"]],
                "centroid": None,
                "access_count": 0
            }
            self.graph.add_node(mod_id, **self.modules[mod_id])

            for rec in mod["records"]:
                r_id = rec["id"]
                self.records[r_id] = {
                    "id": r_id,
                    "text": rec["text"],
                    "source": "benchmark_data",
                    "timestamp": time.time(),
                    "topic": rec.get("topic", "general"),
                    "module_id": mod_id
                }
                vec = self.encoder.encode(rec["text"], convert_to_numpy=True, normalize_embeddings=True)
                self.record_embeddings[r_id] = vec

        # Ingest initial edges
        for edge in data.get("initial_edges", []):
            self.graph.add_edge(edge["source"], edge["target"], weight=edge.get("weight", 0.5), co_access=0)

        self.recompute_all_centroids()

        # Save clean initial snapshot V1
        self.history.clear()
        self.version_counter = 1
        initial_metrics = self.evaluate_benchmark(top_k=4)
        self.save_snapshot("Initial Baseline", "Fresh benchmark dataset loaded", status="ACCEPTED", metrics=initial_metrics)

    def recompute_all_centroids(self):
        """Recomputes module semantic centroid vectors by averaging member record embeddings."""
        for mod_id, mod in self.modules.items():
            r_ids = mod["record_ids"]
            if not r_ids:
                mod["centroid"] = np.zeros(384, dtype=np.float32)
                continue
            vectors = np.array([self.record_embeddings[r] for r in r_ids if r in self.record_embeddings])
            centroid = np.mean(vectors, axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 0:
                centroid = centroid / norm
            mod["centroid"] = centroid
            if self.graph.has_node(mod_id):
                self.graph.nodes[mod_id]["centroid"] = centroid.tolist()

    # -------------------------------------------------------------
    # RETRIEVAL & QUERY CO-ACCESS TELEMETRY
    # -------------------------------------------------------------

    def search(self, query: str, top_k: int = 4, explore_hops: int = 1) -> Dict[str, Any]:
        """
        Retrieves top-k records using semantic centroid routing and 1-hop graph expansion.
        Tracks co-access exclusively from top query-level similarity hits (avoiding self-reinforcement).
        Tracks module utilization (access_count).
        """
        start_time = time.perf_counter()
        q_vec = self.encoder.encode(query, convert_to_numpy=True, normalize_embeddings=True).reshape(1, -1)

        # 1. Score modules by centroid cosine similarity
        module_scores = []
        for mod_id, mod in self.modules.items():
            if mod["centroid"] is None:
                continue
            sim = float(cosine_similarity(q_vec, mod["centroid"].reshape(1, -1))[0][0])
            module_scores.append((mod_id, sim))

        module_scores.sort(key=lambda x: x[1], reverse=True)
        if not module_scores:
            return {"results": [], "visited_modules": [], "latency_ms": 0.0}

        # 2. Track query-level co-access from top similarity hits (Top 2 modules)
        if len(module_scores) >= 2:
            top_mod_1 = module_scores[0][0]
            top_mod_2 = module_scores[1][0]
            sim_diff = module_scores[0][1] - module_scores[1][1]
            # If the second module is also closely relevant (sim diff < 0.15)
            if sim_diff < 0.15:
                pair = tuple(sorted([top_mod_1, top_mod_2]))
                self.query_co_access_counts[pair] = self.query_co_access_counts.get(pair, 0) + 1
                if self.graph.has_edge(pair[0], pair[1]):
                    self.graph[pair[0]][pair[1]]["co_access"] = self.query_co_access_counts[pair]

        best_mod_id = module_scores[0][0]
        self.modules[best_mod_id]["access_count"] += 1

        # 3. Graph expansion: candidates include best module + its direct graph neighbors
        candidate_modules = {best_mod_id}
        if explore_hops >= 1 and self.graph.has_node(best_mod_id):
            for neighbor in self.graph.neighbors(best_mod_id):
                candidate_modules.add(neighbor)
                self.modules[neighbor]["access_count"] += 1

        # 4. Score all individual records in candidate modules
        scored_records = []
        for m_id in candidate_modules:
            for r_id in self.modules[m_id]["record_ids"]:
                r_vec = self.record_embeddings[r_id].reshape(1, -1)
                rec_sim = float(cosine_similarity(q_vec, r_vec)[0][0])
                scored_records.append({
                    "record_id": r_id,
                    "module_id": m_id,
                    "text": self.records[r_id]["text"],
                    "similarity": round(rec_sim, 4)
                })

        scored_records.sort(key=lambda x: x["similarity"], reverse=True)
        top_records = scored_records[:top_k]
        latency_ms = (time.perf_counter() - start_time) * 1000

        return {
            "results": top_records,
            "visited_modules": list(candidate_modules),
            "primary_module": best_mod_id,
            "latency_ms": round(latency_ms, 2)
        }

    # -------------------------------------------------------------
    # STEP 2: DETECTION WITH EXPLICIT TRIGGERS
    # -------------------------------------------------------------

    def diagnose_weaknesses(self) -> List[Dict[str, Any]]:
        """
        Evaluates the current memory graph against explicit threshold rules:
        - Split: module size > N AND KMeans(k=2) gives silhouette > s AND both clusters >= min_size
        - Merge: centroid cosine similarity > t
        - Shortcut: query-level co-access >= c AND no existing direct edge
        """
        weaknesses = []

        # 1. Detect Overloaded Modules for SPLIT
        for mod_id, mod in self.modules.items():
            r_ids = mod["record_ids"]
            if len(r_ids) >= SPLIT_MIN_MODULE_SIZE:
                vectors = np.array([self.record_embeddings[r] for r in r_ids])
                kmeans = KMeans(
                    n_clusters=2,
                    random_state=SPLIT_KMEANS_RANDOM_STATE,
                    n_init=SPLIT_KMEANS_N_INIT
                ).fit(vectors)
                labels = kmeans.labels_

                count_0 = int(np.sum(labels == 0))
                count_1 = int(np.sum(labels == 1))

                if count_0 >= SPLIT_MIN_CLUSTER_SIZE and count_1 >= SPLIT_MIN_CLUSTER_SIZE:
                    sil = float(silhouette_score(vectors, labels))
                    if sil > SPLIT_MIN_SILHOUETTE:
                        weaknesses.append({
                            "signal": "OVERLOADED_MODULE_SIZE_AND_VARIANCE",
                            "measured_value": {
                                "record_count": len(r_ids),
                                "silhouette_score": round(sil, 4),
                                "cluster_sizes": [count_0, count_1]
                            },
                            "threshold": {
                                "min_size": SPLIT_MIN_MODULE_SIZE,
                                "min_silhouette": SPLIT_MIN_SILHOUETTE,
                                "min_cluster_size": SPLIT_MIN_CLUSTER_SIZE
                            },
                            "proposed_op": "SPLIT",
                            "target_modules": [mod_id],
                            "description": f"Module {mod_id} contains {len(r_ids)} records with distinct bi-modal clusters (silhouette {sil:.3f})."
                        })

        # 2. Detect Redundant Modules for MERGE
        mod_keys = list(self.modules.keys())
        for i in range(len(mod_keys)):
            for j in range(i + 1, len(mod_keys)):
                m1, m2 = mod_keys[i], mod_keys[j]
                c1, c2 = self.modules[m1]["centroid"], self.modules[m2]["centroid"]
                if c1 is not None and c2 is not None:
                    sim = float(cosine_similarity(c1.reshape(1, -1), c2.reshape(1, -1))[0][0])
                    if sim > MERGE_COSINE_SIM_THRESHOLD:
                        weaknesses.append({
                            "signal": "REDUNDANT_CENTROID_SIMILARITY",
                            "measured_value": round(sim, 4),
                            "threshold": MERGE_COSINE_SIM_THRESHOLD,
                            "proposed_op": "MERGE",
                            "target_modules": [m1, m2],
                            "description": f"Modules {m1} and {m2} have high centroid similarity ({sim:.3f} > {MERGE_COSINE_SIM_THRESHOLD})."
                        })

        # 3. Detect Missing Direct Connections for SHORTCUT
        for (m1, m2), count in self.query_co_access_counts.items():
            if m1 in self.modules and m2 in self.modules:
                if not self.graph.has_edge(m1, m2) and count >= SHORTCUT_MIN_CO_ACCESS:
                    weaknesses.append({
                        "signal": "REPEATED_QUERY_CO_ACCESS",
                        "measured_value": count,
                        "threshold": SHORTCUT_MIN_CO_ACCESS,
                        "proposed_op": "SHORTCUT",
                        "target_modules": [m1, m2],
                        "description": f"Modules {m1} and {m2} co-occurred in top query results {count} times without a direct edge."
                    })

        return weaknesses

    # -------------------------------------------------------------
    # ADAPTIVE RECONFIGURATION OPERATIONS
    # -------------------------------------------------------------

    def split_module(self, module_id: str) -> Dict[str, Any]:
        """Splits module into 2 sub-modules using KMeans."""
        if module_id not in self.modules:
            raise ValueError(f"Module {module_id} does not exist.")

        mod = self.modules[module_id]
        r_ids = mod["record_ids"]
        if len(r_ids) < SPLIT_MIN_MODULE_SIZE:
            raise ValueError(f"Module must have at least {SPLIT_MIN_MODULE_SIZE} records to split.")

        vectors = np.array([self.record_embeddings[r] for r in r_ids])
        kmeans = KMeans(
            n_clusters=2,
            random_state=SPLIT_KMEANS_RANDOM_STATE,
            n_init=SPLIT_KMEANS_N_INIT
        ).fit(vectors)
        labels = kmeans.labels_

        cluster_0 = [r_ids[i] for i in range(len(r_ids)) if labels[i] == 0]
        cluster_1 = [r_ids[i] for i in range(len(r_ids)) if labels[i] == 1]

        mod_a = f"{module_id}_A"
        mod_b = f"{module_id}_B"

        for r in cluster_0:
            self.records[r]["module_id"] = mod_a
        for r in cluster_1:
            self.records[r]["module_id"] = mod_b

        neighbors = list(self.graph.neighbors(module_id)) if self.graph.has_node(module_id) else []

        del self.modules[module_id]
        if self.graph.has_node(module_id):
            self.graph.remove_node(module_id)

        self.modules[mod_a] = {
            "id": mod_a,
            "name": f"{mod['name']} (Cluster A)",
            "description": f"Split cluster A from {module_id}",
            "record_ids": cluster_0,
            "centroid": None,
            "access_count": 0
        }
        self.modules[mod_b] = {
            "id": mod_b,
            "name": f"{mod['name']} (Cluster B)",
            "description": f"Split cluster B from {module_id}",
            "record_ids": cluster_1,
            "centroid": None,
            "access_count": 0
        }

        self.graph.add_node(mod_a, **self.modules[mod_a])
        self.graph.add_node(mod_b, **self.modules[mod_b])

        # Sub-clusters do not get linked by default to avoid keeping them artificially in the same 1-hop path
        for n in neighbors:
            if self.graph.has_node(n):
                self.graph.add_edge(mod_a, n, weight=0.5, co_access=0)
                self.graph.add_edge(mod_b, n, weight=0.5, co_access=0)

        self.recompute_all_centroids()
        return {
            "operation": "SPLIT",
            "source_module": module_id,
            "new_modules": [mod_a, mod_b],
            "cluster_counts": [len(cluster_0), len(cluster_1)]
        }

    def merge_modules(self, module_a: str, module_b: str) -> Dict[str, Any]:
        """Merges two redundant modules into one."""
        if module_a not in self.modules or module_b not in self.modules:
            raise ValueError(f"Both modules {module_a} and {module_b} must exist.")

        mod_a = self.modules[module_a]
        mod_b = self.modules[module_b]

        merged_id = f"MERGED_{module_a}_{module_b}"
        combined_records = list(set(mod_a["record_ids"] + mod_b["record_ids"]))

        for r in combined_records:
            self.records[r]["module_id"] = merged_id

        neighbors_a = set(self.graph.neighbors(module_a)) if self.graph.has_node(module_a) else set()
        neighbors_b = set(self.graph.neighbors(module_b)) if self.graph.has_node(module_b) else set()
        all_neighbors = (neighbors_a | neighbors_b) - {module_a, module_b}

        del self.modules[module_a]
        del self.modules[module_b]
        if self.graph.has_node(module_a):
            self.graph.remove_node(module_a)
        if self.graph.has_node(module_b):
            self.graph.remove_node(module_b)

        self.modules[merged_id] = {
            "id": merged_id,
            "name": f"Merged ({mod_a['name']} + {mod_b['name']})",
            "description": f"Consolidated module combining {module_a} and {module_b}",
            "record_ids": combined_records,
            "centroid": None,
            "access_count": 0
        }
        self.graph.add_node(merged_id, **self.modules[merged_id])

        for n in all_neighbors:
            if self.graph.has_node(n):
                self.graph.add_edge(merged_id, n, weight=0.8, co_access=0)

        self.recompute_all_centroids()
        return {
            "operation": "MERGE",
            "merged_id": merged_id,
            "sources": [module_a, module_b],
            "record_count": len(combined_records)
        }

    def create_shortcut(self, module_a: str, module_b: str, weight: float = 0.85) -> Dict[str, Any]:
        """Creates a direct edge between modules."""
        if module_a not in self.modules or module_b not in self.modules:
            raise ValueError("Both modules must exist.")

        self.graph.add_edge(module_a, module_b, weight=weight, is_shortcut=True, co_access=self.query_co_access_counts.get(tuple(sorted([module_a, module_b])), 1))
        return {
            "operation": "SHORTCUT",
            "module_a": module_a,
            "module_b": module_b,
            "weight": weight
        }

    # -------------------------------------------------------------
    # STEP 3: REAL VALIDATION (Recall@K, Precision@K, Multi-run Latency)
    # -------------------------------------------------------------

    def evaluate_benchmark(self, top_k: int = 4, latency_runs: int = LATENCY_BENCHMARK_RUNS) -> Dict[str, Any]:
        """
        Evaluates the current memory graph against fixed benchmark queries.
        Averages latency across multiple runs after an initial warm-up run.
        """
        # Warmup run (discarded)
        if self.benchmark_queries:
            self.search(self.benchmark_queries[0]["query"], top_k=top_k)

        all_recalls = []
        all_precisions = []
        query_details = []

        # Run accuracy evaluation
        for q in self.benchmark_queries:
            expected = set(q["expected_record_ids"])
            res = self.search(q["query"], top_k=top_k)

            retrieved = set(r["record_id"] for r in res["results"])
            hits = len(expected & retrieved)

            rec = hits / len(expected) if expected else 0.0
            prec = hits / len(retrieved) if retrieved else 0.0

            all_recalls.append(rec)
            all_precisions.append(prec)

            query_details.append({
                "id": q["id"],
                "query": q["query"],
                "expected": list(expected),
                "retrieved": list(retrieved),
                "recall": round(rec, 4),
                "precision": round(prec, 4)
            })

        # Average latency across multiple benchmark runs
        latencies = []
        for _ in range(latency_runs):
            t0 = time.perf_counter()
            for q in self.benchmark_queries:
                self.search(q["query"], top_k=top_k)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000 / max(1, len(self.benchmark_queries)))

        mean_recall = float(np.mean(all_recalls)) if all_recalls else 0.0
        mean_precision = float(np.mean(all_precisions)) if all_precisions else 0.0
        mean_latency = float(np.mean(latencies)) if latencies else 0.0

        return {
            "mean_recall": round(mean_recall, 4),
            "mean_precision": round(mean_precision, 4),
            "mean_latency_ms": round(mean_latency, 2),
            "query_count": len(self.benchmark_queries),
            "details": query_details
        }

    def execute_guarded_adaptation(
        self,
        op_type: str,
        params: Dict[str, Any],
        min_recall_threshold: float = MIN_ACCEPTABLE_RECALL,
        max_drop_epsilon: float = MAX_ALLOWABLE_RECALL_DROP
    ) -> Dict[str, Any]:
        """
        Executes a proposed adaptation with rigorous guardrail acceptance:
        - Recall >= min_recall_threshold
        - Drop vs previous accepted version <= max_drop_epsilon
        If rejected, rolls back to the exact previous snapshot.
        If accepted with 0 recall change, marks status as NEUTRAL.
        """
        # Find latest accepted version as baseline
        baseline_snapshot = None
        for s in reversed(self.history):
            if s["status"] in ("ACCEPTED", "NEUTRAL"):
                baseline_snapshot = s
                break

        if not baseline_snapshot:
            baseline_snapshot = self.history[-1]

        baseline_recall = baseline_snapshot["metrics"]["mean_recall"]
        prev_version_id = baseline_snapshot["version"]

        # 1. Apply mutation
        mutation_result = {}
        if op_type.upper() == "SPLIT":
            mutation_result = self.split_module(params["module_id"])
        elif op_type.upper() == "MERGE":
            mutation_result = self.merge_modules(params["module_a"], params["module_b"])
        elif op_type.upper() == "SHORTCUT":
            mutation_result = self.create_shortcut(params["module_a"], params["module_b"])
        else:
            raise ValueError(f"Unknown operation {op_type}")

        # 2. Benchmark post-mutation performance
        post_metrics = self.evaluate_benchmark()
        post_recall = post_metrics["mean_recall"]
        delta_recall = round(post_recall - baseline_recall, 4)

        # 3. Acceptance evaluation
        meets_absolute_min = post_recall >= min_recall_threshold
        meets_epsilon_bound = (baseline_recall - post_recall) <= max_drop_epsilon

        if meets_absolute_min and meets_epsilon_bound:
            # Determine status: IMPROVED vs NEUTRAL
            status = "ACCEPTED" if delta_recall > 0.0001 else "NEUTRAL"
            snapshot = self.save_snapshot(
                f"{status.capitalize()} {op_type.upper()}",
                f"Applied {op_type} on {params}. Delta Recall: {delta_recall:+.4f}",
                status=status,
                metrics=post_metrics,
                op_info={"op": op_type, "params": params, "mutation": mutation_result}
            )
            return {
                "decision": status,
                "operation": op_type,
                "mutation": mutation_result,
                "version": snapshot["version"],
                "before_recall": baseline_recall,
                "after_recall": post_recall,
                "delta_recall": delta_recall,
                "metrics": post_metrics
            }
        else:
            # REJECT and rollback
            reject_reason = (
                f"Recall dropped by {baseline_recall - post_recall:.4f} (exceeds epsilon {max_drop_epsilon})"
                if not meets_epsilon_bound else
                f"Recall {post_recall:.4f} fell below absolute minimum {min_recall_threshold}"
            )
            rejected_snapshot = self.save_snapshot(
                f"Rejected {op_type.upper()}",
                reject_reason,
                status="REJECTED",
                metrics=post_metrics,
                op_info={"op": op_type, "params": params, "mutation": mutation_result}
            )
            # Physical rollback to baseline snapshot
            rollback_res = self.rollback_to_version(prev_version_id)
            return {
                "decision": "REJECTED",
                "reason": reject_reason,
                "operation": op_type,
                "version": rejected_snapshot["version"],
                "before_recall": baseline_recall,
                "failed_recall": post_recall,
                "delta_recall": delta_recall,
                "restored_version": rollback_res["restored_version"],
                "current_metrics": rollback_res["metrics"]
            }

    # -------------------------------------------------------------
    # STEP 5: FLAT VECTOR BASELINE (NO GRAPH)
    # -------------------------------------------------------------

    def evaluate_flat_baseline(self, top_k: int = 4) -> Dict[str, Any]:
        """
        Evaluates a conventional flat vector search baseline over all records (no graph, no modules).
        Compares query directly against every record vector in the system.
        """
        all_recalls = []
        all_precisions = []
        latencies = []

        all_r_ids = list(self.records.keys())
        if not all_r_ids:
            return {"mean_recall": 0.0, "mean_precision": 0.0, "mean_latency_ms": 0.0}

        all_vectors = np.array([self.record_embeddings[r] for r in all_r_ids])

        for q in self.benchmark_queries:
            expected = set(q["expected_record_ids"])
            t0 = time.perf_counter()

            q_vec = self.encoder.encode(q["query"], convert_to_numpy=True, normalize_embeddings=True).reshape(1, -1)
            sims = cosine_similarity(q_vec, all_vectors)[0]

            top_indices = np.argsort(sims)[::-1][:top_k]
            retrieved = set(all_r_ids[i] for i in top_indices)

            latencies.append((time.perf_counter() - t0) * 1000)

            hits = len(expected & retrieved)
            rec = hits / len(expected) if expected else 0.0
            prec = hits / len(retrieved) if retrieved else 0.0

            all_recalls.append(rec)
            all_precisions.append(prec)

        current_graph_metrics = self.evaluate_benchmark(top_k=top_k)

        return {
            "flat_baseline": {
                "architecture": "Flat Vector Search (No Modules, No Graph)",
                "mean_recall": round(float(np.mean(all_recalls)), 4),
                "mean_precision": round(float(np.mean(all_precisions)), 4),
                "mean_latency_ms": round(float(np.mean(latencies)), 2)
            },
            "morphe_graph": {
                "architecture": f"MORPHE Graph ({self.history[-1]['version']})",
                "mean_recall": current_graph_metrics["mean_recall"],
                "mean_precision": current_graph_metrics["mean_precision"],
                "mean_latency_ms": current_graph_metrics["mean_latency_ms"]
            },
            "delta": {
                "recall_delta": round(current_graph_metrics["mean_recall"] - float(np.mean(all_recalls)), 4),
                "precision_delta": round(current_graph_metrics["mean_precision"] - float(np.mean(all_precisions)), 4),
                "latency_delta_ms": round(current_graph_metrics["mean_latency_ms"] - float(np.mean(latencies)), 2)
            }
        }

    # -------------------------------------------------------------
    # STEP 6: VERSIONING & PERSISTENCE
    # -------------------------------------------------------------

    def save_snapshot(
        self,
        label: str,
        description: str,
        status: str = "ACCEPTED",
        metrics: Optional[Dict[str, Any]] = None,
        op_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Saves snapshot and persists entire state to disk."""
        if metrics is None:
            metrics = self.evaluate_benchmark()

        snapshot = {
            "version": f"V{self.version_counter}",
            "version_label": label,
            "description": description,
            "timestamp": time.time(),
            "status": status,
            "metrics": metrics,
            "op_info": op_info or {},
            "modules": copy.deepcopy(self.modules),
            "records": copy.deepcopy(self.records),
            "graph_edges": [(u, v, d) for u, v, d in self.graph.edges(data=True)],
            "graph_nodes": [(n, d) for n, d in self.graph.nodes(data=True)]
        }
        self.history.append(snapshot)
        self.version_counter += 1
        self.persist_state_to_disk()
        return snapshot

    def rollback_to_version(self, target_version: str) -> Dict[str, Any]:
        """Restores graph and module assignments from a past snapshot."""
        candidate = None
        for s in reversed(self.history):
            if s["version"] == target_version:
                candidate = s
                break

        if not candidate:
            raise ValueError(f"Target version {target_version} not found in history.")

        self.modules = copy.deepcopy(candidate["modules"])
        self.records = copy.deepcopy(candidate["records"])

        self.graph.clear()
        for n, d in candidate["graph_nodes"]:
            self.graph.add_node(n, **d)
        for u, v, d in candidate["graph_edges"]:
            self.graph.add_edge(u, v, **d)

        self.recompute_all_centroids()

        restored_metrics = self.evaluate_benchmark()
        new_version = self.save_snapshot(
            f"Rollback to {target_version}",
            f"Restored graph topology and records from {target_version}",
            status="ACCEPTED",
            metrics=restored_metrics
        )
        return {
            "restored_version": target_version,
            "active_version": new_version["version"],
            "metrics": restored_metrics
        }

    def persist_state_to_disk(self):
        """Serializes history and current state to disk for persistent restarts."""
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            serializable_history = []
            for s in self.history:
                clean_modules = {}
                for mid, mdata in s["modules"].items():
                    clean_modules[mid] = {k: val for k, val in mdata.items() if k != "centroid"}

                entry = {
                    "version": s["version"],
                    "version_label": s["version_label"],
                    "description": s["description"],
                    "timestamp": s["timestamp"],
                    "status": s["status"],
                    "metrics": {
                        "mean_recall": s["metrics"]["mean_recall"],
                        "mean_precision": s["metrics"]["mean_precision"],
                        "mean_latency_ms": s["metrics"]["mean_latency_ms"]
                    },
                    "op_info": s.get("op_info", {}),
                    "modules": clean_modules,
                    "records": s["records"],
                    "graph_edges": [(u, v, {k: val for k, val in d.items() if not isinstance(val, np.ndarray)}) for u, v, d in s["graph_edges"]],
                    "graph_nodes": [(n, {k: val for k, val in d.items() if k != "centroid" and not isinstance(val, np.ndarray)}) for n, d in s["graph_nodes"]]
                }
                serializable_history.append(entry)

            temp_path = f"{self.state_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump({
                    "version_counter": self.version_counter,
                    "history": serializable_history
                }, f, indent=2)
            os.replace(temp_path, self.state_path)
        except Exception as e:
            print(f"Warning: Failed to persist state to disk: {e}")

    def load_persisted_state(self):
        """Loads state from disk if available."""
        with open(self.state_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.version_counter = data.get("version_counter", 1)
        raw_history = data.get("history", [])
        if not raw_history:
            self.load_sample_data(self.data_path)
            return

        latest = raw_history[-1]
        self.modules = latest["modules"]
        self.records = latest["records"]

        self.graph.clear()
        for n, d in latest["graph_nodes"]:
            self.graph.add_node(n, **d)
        for u, v, d in latest["graph_edges"]:
            self.graph.add_edge(u, v, **d)

        # Re-encode records
        for r_id, rec in self.records.items():
            vec = self.encoder.encode(rec["text"], convert_to_numpy=True, normalize_embeddings=True)
            self.record_embeddings[r_id] = vec

        self.recompute_all_centroids()

        # Load benchmark queries
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as bf:
                bdata = json.load(bf)
                self.benchmark_queries = bdata.get("benchmark_queries", [])

        self.history = raw_history

    def export_graph_json(self) -> Dict[str, Any]:
        """Returns nodes and edges formatted for frontend visualizers."""
        nodes = []
        for n in self.graph.nodes:
            mod_data = self.modules.get(n, {})
            nodes.append({
                "id": n,
                "label": mod_data.get("name", n),
                "record_count": len(mod_data.get("record_ids", [])),
                "access_count": mod_data.get("access_count", 0),
                "records": [self.records[r] for r in mod_data.get("record_ids", []) if r in self.records]
            })

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "weight": data.get("weight", 0.5),
                "is_shortcut": data.get("is_shortcut", False),
                "co_access": data.get("co_access", 0)
            })

        return {"nodes": nodes, "edges": edges}
