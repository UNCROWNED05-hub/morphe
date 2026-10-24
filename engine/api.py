from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from engine.memory_engine import MemoryEngine

app = FastAPI(
    title="MORPHE Engine API",
    description="Adaptive Graph-Based Memory Plasticity and Versioned Evaluation Engine",
    version="1.0.0"
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton memory engine instance
engine = MemoryEngine()


# --- Pydantic Schemas for Request Validation ---

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of records to retrieve")
    explore_hops: int = Field(default=1, ge=0, le=3, description="Graph neighbor traversal hops")


class SplitRequest(BaseModel):
    module_id: str = Field(..., description="ID of overloaded module to split using KMeans")
    min_recall_threshold: float = Field(default=0.65, ge=0.0, le=1.0)


class MergeRequest(BaseModel):
    module_a: str = Field(..., description="First module to merge")
    module_b: str = Field(..., description="Second module to merge")
    min_recall_threshold: float = Field(default=0.65, ge=0.0, le=1.0)


class ShortcutRequest(BaseModel):
    module_a: str = Field(..., description="First module in co-access path")
    module_b: str = Field(..., description="Second module in co-access path")
    weight: float = Field(default=0.85, ge=0.1, le=1.0)
    min_recall_threshold: float = Field(default=0.65, ge=0.0, le=1.0)


class RollbackRequest(BaseModel):
    target_version: Optional[str] = Field(default=None, description="Version ID like 'V1', or latest if null")


# --- Endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "engine": "MORPHE v1.0",
        "active_modules": len(engine.modules),
        "total_records": len(engine.records),
        "active_version": engine.history[-1]["version"]
    }


@app.get("/api/graph")
def get_graph():
    """Returns the live graph nodes and edges for visual rendering."""
    return engine.export_graph_json()


@app.post("/api/query")
def run_query(req: QueryRequest):
    """Executes semantic search with 1-hop graph traversal and co-access telemetry."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    return engine.search(query=req.query, top_k=req.top_k, explore_hops=req.explore_hops)


@app.post("/api/adapt/split")
def adapt_split(req: SplitRequest):
    """Triggers an evaluated split on an overloaded module with automatic guardrail rollback."""
    try:
        res = engine.execute_guarded_adaptation(
            op_type="SPLIT",
            params={"module_id": req.module_id},
            min_recall_threshold=req.min_recall_threshold
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/adapt/merge")
def adapt_merge(req: MergeRequest):
    """Triggers an evaluated merge between two redundant modules with guardrail rollback."""
    try:
        res = engine.execute_guarded_adaptation(
            op_type="MERGE",
            params={"module_a": req.module_a, "module_b": req.module_b},
            min_recall_threshold=req.min_recall_threshold
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/adapt/shortcut")
def adapt_shortcut(req: ShortcutRequest):
    """Creates a Hebbian direct shortcut edge between co-accessed modules."""
    try:
        res = engine.execute_guarded_adaptation(
            op_type="SHORTCUT",
            params={"module_a": req.module_a, "module_b": req.module_b},
            min_recall_threshold=req.min_recall_threshold
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/rollback")
def rollback_version(req: RollbackRequest):
    """Restores graph topology and module states to a previous accepted version."""
    try:
        return engine.rollback_to_version(req.target_version)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/history")
def get_version_history():
    """Returns the immutable version history timeline with metrics and audit decisions."""
    summaries = []
    for s in engine.history:
        summaries.append({
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
            "node_count": len(s["graph_nodes"]),
            "edge_count": len(s["graph_edges"])
        })
    return {"history": summaries, "active_version": engine.history[-1]["version"]}


@app.get("/api/benchmark")
def get_full_benchmark():
    """Runs all 10 ground-truth evaluation queries and returns detailed score breakdown."""
    return engine.evaluate_benchmark()


@app.post("/api/reset")
def reset_to_initial():
    """Resets memory engine back to factory benchmark state."""
    global engine
    engine = MemoryEngine()
    return {"status": "reset_successful", "version": "V1"}
