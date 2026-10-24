import copy
import json
import os
import time
from typing import Dict, List, Any, Optional, Tuple
import networkx as nx
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity


class MemoryEngine:
    def __init__(self, data_path: str = "data/benchmark_data.json", model_name: str = "all-MiniLM-L6-v2"):
        self.data_path = data_path
        self.model_name = model_name
        self.encoder = SentenceTransformer(model_name)
        
        # Core Graph state
        self.graph = nx.Graph()
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.records: Dict[str, Dict[str, Any]] = {}
        self.record_embeddings: Dict[str, np.ndarray] = {}
        self.co_access_counts: Dict[Tuple[str, str], int] = {}
        self.benchmark_queries: List[Dict[str, Any]] = []

        # Version history stack for safe recovery and rollback
        self.history: List[Dict[str, Any]] = []
        self.version_counter = 1

        # Load initial data
        self.load_benchmark_data()
        self.recompute_all_centroids()
        self.save_snapshot("Initial V1 Baseline", "Initial state loaded from benchmark", status="ACCEPTED")

    def load_benchmark_data(self):
        """Loads modules, records, and ground truth benchmark queries."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Benchmark file not found at {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.benchmark_queries = data.get("benchmark_queries", [])
        
        # Ingest modules and records
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
                    "topic": rec.get("topic", "general"),
                    "module_id": mod_id
                }
                # Precompute embedding vector
                vec = self.encoder.encode(rec["text"], convert_to_numpy=True, normalize_embeddings=True)
                self.record_embeddings[r_id] = vec

        # Add initial edges
        for edge in data.get("initial_edges", []):
            self.graph.add_edge(edge["source"], edge["target"], weight=edge.get("weight", 0.5), co_access=0)

    def recompute_all_centroids(self):
        """Recomputes module semantic centroid vectors by averaging record embeddings."""
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
            self.graph.nodes[mod_id]["centroid"] = centroid.tolist()

    def search(self, query: str, top_k: int = 5, explore_hops: int = 1) -> Dict[str, Any]:
        """
        Retrieves top-k records using semantic similarity and 1-hop graph traversal.
        Tracks co-access across modules for Hebbian shortcut detection.
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

        best_mod_id, best_score = module_scores[0]
        self.modules[best_mod_id]["access_count"] += 1

        # 2. Graph expansion: include neighbors of the best module
        candidate_modules = {best_mod_id}
        if explore_hops >= 1 and self.graph.has_node(best_mod_id):
            for neighbor in self.graph.neighbors(best_mod_id):
                candidate_modules.add(neighbor)
                self.modules[neighbor]["access_count"] += 1

        # Track co-access between all visited candidate modules
        candidate_list = sorted(list(candidate_modules))
        for i in range(len(candidate_list)):
            for j in range(i + 1, len(candidate_list)):
                pair = (candidate_list[i], candidate_list[j])
                self.co_access_counts[pair] = self.co_access_counts.get(pair, 0) + 1
                if self.graph.has_edge(pair[0], pair[1]):
                    self.graph[pair[0]][pair[1]]["co_access"] = self.co_access_counts[pair]

        # 3. Score all individual records residing in candidate modules
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
    # ADAPTIVE MUTATION OPERATIONS
    # -------------------------------------------------------------

    def split_module(self, module_id: str) -> Dict[str, Any]:
        """
        Splits an overloaded module into 2 sub-modules using KMeans clustering on record vectors.
        """
        if module_id not in self.modules:
            raise ValueError(f"Module {module_id} does not exist.")

        mod = self.modules[module_id]
        r_ids = mod["record_ids"]
        if len(r_ids) < 4:
            raise ValueError("Module must contain at least 4 records to perform a split.")

        vectors = np.array([self.record_embeddings[r] for r in r_ids])
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10).fit(vectors)
        labels = kmeans.labels_

        cluster_0_records = [r_ids[i] for i in range(len(r_ids)) if labels[i] == 0]
        cluster_1_records = [r_ids[i] for i in range(len(r_ids)) if labels[i] == 1]

        mod_id_a = f"{module_id}_A"
        mod_id_b = f"{module_id}_B"

        # Transfer records and assign new modules
        for r in cluster_0_records:
            self.records[r]["module_id"] = mod_id_a
        for r in cluster_1_records:
            self.records[r]["module_id"] = mod_id_b

        # Save existing edges to transfer to sub-modules
        neighbors = list(self.graph.neighbors(module_id)) if self.graph.has_node(module_id) else []

        # Remove parent module
        del self.modules[module_id]
        if self.graph.has_node(module_id):
            self.graph.remove_node(module_id)

        # Add new sub-modules
        self.modules[mod_id_a] = {
            "id": mod_id_a,
            "name": f"{mod['name']} (Sub-Cluster A)",
            "description": f"Specialized cluster formed via KMeans split of {module_id}",
            "record_ids": cluster_0_records,
            "centroid": None,
            "access_count": 0
        }
        self.modules[mod_id_b] = {
            "id": mod_id_b,
            "name": f"{mod['name']} (Sub-Cluster B)",
            "description": f"Specialized cluster formed via KMeans split of {module_id}",
            "record_ids": cluster_1_records,
            "centroid": None,
            "access_count": 0
        }

        self.graph.add_node(mod_id_a, **self.modules[mod_id_a])
        self.graph.add_node(mod_id_b, **self.modules[mod_id_b])

        # Add internal edge between newly split twin clusters
        self.graph.add_edge(mod_id_a, mod_id_b, weight=0.75, co_access=0)

        # Re-attach inherited neighbors
        for n in neighbors:
            if self.graph.has_node(n):
                self.graph.add_edge(mod_id_a, n, weight=0.5, co_access=0)
                self.graph.add_edge(mod_id_b, n, weight=0.5, co_access=0)

        self.recompute_all_centroids()
        return {
            "operation": "SPLIT",
            "source_module": module_id,
            "new_modules": [mod_id_a, mod_id_b],
            "cluster_counts": [len(cluster_0_records), len(cluster_1_records)]
        }

    def merge_modules(self, module_a: str, module_b: str) -> Dict[str, Any]:
        """
        Merges two redundant modules into a single unified module.
        """
        if module_a not in self.modules or module_b not in self.modules:
            raise ValueError("Both modules must exist to merge.")

        mod_a = self.modules[module_a]
        mod_b = self.modules[module_b]

        merged_id = f"MERGED_{module_a}_{module_b}"
        combined_records = list(set(mod_a["record_ids"] + mod_b["record_ids"]))

        for r in combined_records:
            self.records[r]["module_id"] = merged_id

        # Aggregate neighbors
        neighbors_a = set(self.graph.neighbors(module_a)) if self.graph.has_node(module_a) else set()
        neighbors_b = set(self.graph.neighbors(module_b)) if self.graph.has_node(module_b) else set()
        all_neighbors = (neighbors_a | neighbors_b) - {module_a, module_b}

        # Remove old nodes
        del self.modules[module_a]
        del self.modules[module_b]
        if self.graph.has_node(module_a):
            self.graph.remove_node(module_a)
        if self.graph.has_node(module_b):
            self.graph.remove_node(module_b)

        # Create new merged node
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

    def create_shortcut(self, module_a: str, module_b: str, weight: float = 0.9) -> Dict[str, Any]:
        """
        Creates a direct retrieval shortcut edge between frequently co-accessed modules.
        """
        if module_a not in self.modules or module_b not in self.modules:
            raise ValueError("Both modules must exist to create a shortcut edge.")

        self.graph.add_edge(module_a, module_b, weight=weight, is_shortcut=True, co_access=self.co_access_counts.get((module_a, module_b), 1))
        return {
            "operation": "SHORTCUT",
            "module_a": module_a,
            "module_b": module_b,
            "weight": weight
        }

    # -------------------------------------------------------------
    # BENCHMARK EVALUATION & AUDIT GUARDRAIL
    # -------------------------------------------------------------

    def evaluate_benchmark(self, top_k: int = 4) -> Dict[str, Any]:
        """
        Evaluates the current memory graph against the 10 fixed ground-truth benchmark queries.
        Computes Mean Recall@K, Mean Precision@K, and Average Latency.
        """
        recalls = []
        precisions = []
        latencies = []

        query_details = []
        for q in self.benchmark_queries:
            expected_ids = set(q["expected_record_ids"])
            res = self.search(q["query"], top_k=top_k)

            retrieved_ids = set(r["record_id"] for r in res["results"])
            hits = len(expected_ids & retrieved_ids)

            recall = hits / len(expected_ids) if expected_ids else 0.0
            precision = hits / len(retrieved_ids) if retrieved_ids else 0.0

            recalls.append(recall)
            precisions.append(precision)
            latencies.append(res["latency_ms"])

            query_details.append({
                "query_id": q["id"],
                "query": q["query"],
                "expected": list(expected_ids),
                "retrieved": list(retrieved_ids),
                "recall": round(recall, 3),
                "latency_ms": res["latency_ms"]
            })

        mean_recall = float(np.mean(recalls)) if recalls else 0.0
        mean_precision = float(np.mean(precisions)) if precisions else 0.0
        mean_latency = float(np.mean(latencies)) if latencies else 0.0

        return {
            "mean_recall": round(mean_recall, 4),
            "mean_precision": round(mean_precision, 4),
            "mean_latency_ms": round(mean_latency, 2),
            "query_count": len(self.benchmark_queries),
            "details": query_details
        }

    def save_snapshot(self, version_label: str, description: str, status: str = "ACCEPTED", metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Saves an immutable snapshot of graph topology and module states."""
        if metrics is None:
            metrics = self.evaluate_benchmark()

        snapshot = {
            "version": f"V{self.version_counter}",
            "version_label": version_label,
            "description": description,
            "timestamp": time.time(),
            "status": status,
            "metrics": metrics,
            "modules": copy.deepcopy(self.modules),
            "records": copy.deepcopy(self.records),
            "graph_edges": [(u, v, d) for u, v, d in self.graph.edges(data=True)],
            "graph_nodes": [(n, d) for n, d in self.graph.nodes(data=True)]
        }
        self.history.append(snapshot)
        self.version_counter += 1
        return snapshot

    def rollback_to_version(self, target_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Restores graph topology and module assignments from a past snapshot.
        If target_version is not specified, rolls back to the last ACCEPTED version.
        """
        candidate_snapshot = None
        if target_version:
            for s in reversed(self.history):
                if s["version"] == target_version:
                    candidate_snapshot = s
                    break
        else:
            for s in reversed(self.history[:-1]):
                if s["status"] == "ACCEPTED":
                    candidate_snapshot = s
                    break

        if not candidate_snapshot:
            raise ValueError("No eligible previous accepted snapshot found for rollback.")

        # Reconstruct graph and modules from deep snapshot
        self.modules = copy.deepcopy(candidate_snapshot["modules"])
        self.records = copy.deepcopy(candidate_snapshot["records"])
        
        self.graph.clear()
        for n, d in candidate_snapshot["graph_nodes"]:
            self.graph.add_node(n, **d)
        for u, v, d in candidate_snapshot["graph_edges"]:
            self.graph.add_edge(u, v, **d)

        self.recompute_all_centroids()

        # Log rollback event in history
        new_version = self.save_snapshot(
            f"Rollback to {candidate_snapshot['version']}",
            f"Restored graph and assignments from {candidate_snapshot['version']}",
            status="ACCEPTED"
        )
        return {
            "restored_version": candidate_snapshot["version"],
            "new_active_version": new_version["version"],
            "metrics": new_version["metrics"]
        }

    def execute_guarded_adaptation(self, op_type: str, params: Dict[str, Any], min_recall_threshold: float = 0.65) -> Dict[str, Any]:
        """
        Executes a proposed adaptation inside an evaluated sandbox.
        If Recall drops below min_recall_threshold, it rejects and rolls back immediately!
        """
        prev_snapshot = self.history[-1]
        baseline_recall = prev_snapshot["metrics"]["mean_recall"]

        # 1. Execute mutation
        mutation_result = {}
        if op_type.upper() == "SPLIT":
            mutation_result = self.split_module(params["module_id"])
        elif op_type.upper() == "MERGE":
            mutation_result = self.merge_modules(params["module_a"], params["module_b"])
        elif op_type.upper() == "SHORTCUT":
            mutation_result = self.create_shortcut(params["module_a"], params["module_b"])
        else:
            raise ValueError(f"Unknown adaptation operation: {op_type}")

        # 2. Evaluate performance of mutated graph
        post_metrics = self.evaluate_benchmark()
        post_recall = post_metrics["mean_recall"]

        # 3. Decision guardrail: check if performance degraded beyond threshold
        is_accepted = post_recall >= min_recall_threshold and (post_recall >= baseline_recall - 0.05)

        if is_accepted:
            snapshot = self.save_snapshot(
                f"Accepted {op_type.upper()}",
                f"Successfully applied {op_type} on {params}",
                status="ACCEPTED",
                metrics=post_metrics
            )
            return {
                "decision": "ACCEPTED",
                "operation": op_type,
                "mutation": mutation_result,
                "version": snapshot["version"],
                "before_recall": baseline_recall,
                "after_recall": post_recall,
                "delta": round(post_recall - baseline_recall, 4),
                "metrics": post_metrics
            }
        else:
            # Reject mutation and record rejected snapshot
            rejected_snapshot = self.save_snapshot(
                f"Rejected {op_type.upper()}",
                f"Degraded recall to {post_recall} (Threshold {min_recall_threshold}). Rolled back.",
                status="REJECTED",
                metrics=post_metrics
            )
            # Perform instant physical rollback
            rollback_res = self.rollback_to_version(prev_snapshot["version"])
            return {
                "decision": "REJECTED",
                "reason": f"Recall dropped from {baseline_recall} to {post_recall} below safe threshold {min_recall_threshold}.",
                "operation": op_type,
                "version": rejected_snapshot["version"],
                "before_recall": baseline_recall,
                "failed_recall": post_recall,
                "restored_version": rollback_res["restored_version"],
                "current_metrics": rollback_res["metrics"]
            }

    def export_graph_json(self) -> Dict[str, Any]:
        """Returns nodes and edges formatted for frontend D3/Canvas visualizers."""
        nodes = []
        for n, data in self.graph.nodes(data=True):
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
