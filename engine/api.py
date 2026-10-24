from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine.memory_engine import MemoryEngine
from engine.config import (
    CHUNK_SIZE_WORDS,
    CHUNK_OVERLAP_WORDS,
    INGEST_NEW_MODULE_SIM_THRESHOLD,
    MIN_ACCEPTABLE_RECALL,
    MAX_ALLOWABLE_RECALL_DROP
)

app = FastAPI(
    title="MORPHE Engine API",
    description="Adaptive Graph-Based Memory Plasticity and Evaluation API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = MemoryEngine()


# --- Pydantic Schemas ---

class IngestRequest(BaseModel):
    raw_text: str = Field(..., description="Raw text to chunk, embed, and assign")
    source: str = Field(default="user_input", description="Source identifier")
    topic: str = Field(default="general", description="Topic tag")
    chunk_size: int = Field(default=CHUNK_SIZE_WORDS, ge=5, le=500)
    overlap: int = Field(default=CHUNK_OVERLAP_WORDS, ge=0, le=100)
    sim_threshold: float = Field(default=INGEST_NEW_MODULE_SIM_THRESHOLD, ge=0.0, le=1.0)


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(default=4, ge=1, le=20)
    explore_hops: int = Field(default=1, ge=0, le=3)


class SplitRequest(BaseModel):
    module_id: str = Field(..., description="Target module ID")
    min_recall_threshold: float = Field(default=MIN_ACCEPTABLE_RECALL, ge=0.0, le=1.0)
    max_drop_epsilon: float = Field(default=MAX_ALLOWABLE_RECALL_DROP, ge=0.0, le=1.0)


class MergeRequest(BaseModel):
    module_a: str = Field(..., description="First module to merge")
    module_b: str = Field(..., description="Second module to merge")
    min_recall_threshold: float = Field(default=MIN_ACCEPTABLE_RECALL, ge=0.0, le=1.0)
    max_drop_epsilon: float = Field(default=MAX_ALLOWABLE_RECALL_DROP, ge=0.0, le=1.0)


class ShortcutRequest(BaseModel):
    module_a: str = Field(..., description="First module in pathway")
    module_b: str = Field(..., description="Second module in pathway")
    weight: float = Field(default=0.85, ge=0.1, le=1.0)
    min_recall_threshold: float = Field(default=MIN_ACCEPTABLE_RECALL, ge=0.0, le=1.0)
    max_drop_epsilon: float = Field(default=MAX_ALLOWABLE_RECALL_DROP, ge=0.0, le=1.0)


class RollbackRequest(BaseModel):
    version_id: str = Field(..., description="Target version ID (e.g. 'V1')")


# --- Endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "engine": "MORPHE v2.0",
        "active_modules": len(engine.modules),
        "total_records": len(engine.records),
        "active_version": engine.history[-1]["version"] if engine.history else "V0"
    }


# STEP 1: Ingestion
@app.post("/api/ingest")
def ingest_text(req: IngestRequest):
    """Chunks raw text, embeds chunks, and dynamically assigns to modules or spawns new ones."""
    if not req.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text cannot be empty")
    return engine.ingest_text(
        raw_text=req.raw_text,
        source=req.source,
        topic=req.topic,
        chunk_size=req.chunk_size,
        overlap=req.overlap,
        sim_threshold=req.sim_threshold
    )


@app.post("/api/load-sample")
def load_sample():
    """Reloads the clean benchmark dataset through the pipeline."""
    engine.load_sample_data()
    return {
        "status": "sample_loaded",
        "modules_loaded": len(engine.modules),
        "records_loaded": len(engine.records),
        "active_version": engine.history[-1]["version"]
    }


# STEP 2: Explicit Diagnostics
@app.get("/api/diagnose")
def diagnose():
    """Returns detected structural weaknesses with measured values, thresholds, and proposed ops."""
    return {"weaknesses": engine.diagnose_weaknesses()}


@app.get("/api/graph")
def get_graph():
    """Returns live graph nodes (including access_count utilization) and edges."""
    return engine.export_graph_json()


@app.post("/api/query")
def run_query(req: QueryRequest):
    """Executes search with 1-hop traversal and query-level co-access tracking."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    return engine.search(query=req.query, top_k=req.top_k, explore_hops=req.explore_hops)


# STEP 3 & 4: Reconfiguration & Guardrail
@app.post("/api/adapt/split")
def adapt_split(req: SplitRequest):
    try:
        return engine.execute_guarded_adaptation(
            op_type="SPLIT",
            params={"module_id": req.module_id},
            min_recall_threshold=req.min_recall_threshold,
            max_drop_epsilon=req.max_drop_epsilon
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/adapt/merge")
def adapt_merge(req: MergeRequest):
    try:
        return engine.execute_guarded_adaptation(
            op_type="MERGE",
            params={"module_a": req.module_a, "module_b": req.module_b},
            min_recall_threshold=req.min_recall_threshold,
            max_drop_epsilon=req.max_drop_epsilon
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/adapt/shortcut")
def adapt_shortcut(req: ShortcutRequest):
    try:
        return engine.execute_guarded_adaptation(
            op_type="SHORTCUT",
            params={"module_a": req.module_a, "module_b": req.module_b},
            min_recall_threshold=req.min_recall_threshold,
            max_drop_epsilon=req.max_drop_epsilon
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# STEP 5: Baseline vs Graph
@app.get("/api/baseline")
def get_baseline_comparison(top_k: int = 4):
    """Compares current MORPHE graph against flat vector search over all records."""
    return engine.evaluate_flat_baseline(top_k=top_k)


# STEP 6: Versioning & Rollback
@app.get("/api/versions")
def get_versions():
    """Lists all versions with metrics, operations, and status (ACCEPTED/NEUTRAL/REJECTED)."""
    summaries = []
    for s in engine.history:
        summaries.append({
            "version": s["version"],
            "version_label": s["version_label"],
            "description": s["description"],
            "timestamp": s["timestamp"],
            "status": s["status"],
            "metrics": s["metrics"],
            "op_info": s.get("op_info", {}),
            "node_count": len(s["graph_nodes"]),
            "edge_count": len(s["graph_edges"])
        })
    return {"versions": summaries, "active_version": engine.history[-1]["version"]}


@app.get("/api/versions/{version_id}")
def get_version_detail(version_id: str):
    """Returns full snapshot detail for a specific version."""
    for s in engine.history:
        if s["version"] == version_id:
            return s
    raise HTTPException(status_code=404, detail=f"Version {version_id} not found")


@app.post("/api/rollback")
def rollback(req: RollbackRequest):
    try:
        return engine.rollback_to_version(req.version_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/benchmark")
def get_benchmark():
    return engine.evaluate_benchmark()


@app.post("/api/reset")
def reset_to_initial():
    engine.load_sample_data()
    return {"status": "reset_successful", "active_version": "V1"}
