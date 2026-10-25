import os
import sys
import json
import time
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def export_all():
    from ui.adapter import EngineAdapter
    from ui.models import ProposalModel

    adapter = EngineAdapter()
    adapter.reset()

    # 1. Config & Baseline
    config = adapter.get_config()
    baseline = adapter.baseline_evaluate()
    v1_eval = adapter.evaluate()

    # 2. Run adaptations
    # Cycle 1: Split
    split_prop = ProposalModel(
        op="split",
        targets=["MOD_MIXED_CORE"],
        signal="OVERLOAD",
        value=14,
        threshold=10,
        reason="Overloaded module with distinct bi-modal topic clusters"
    )
    cycle_split = adapter.run_adaptation_cycle(split_prop)

    # Cycle 2: Merge
    merge_prop = ProposalModel(
        op="merge",
        targets=["MOD_VECTOR_INDEX", "MOD_EMBEDDING_RETRIEVAL"],
        signal="REDUNDANCY",
        value=0.912,
        threshold=0.88,
        reason="High centroid semantic similarity"
    )
    cycle_merge = adapter.run_adaptation_cycle(merge_prop)

    # Cycle 3: Shortcut
    shortcut_prop = ProposalModel(
        op="shortcut",
        targets=["MOD_PYTHON_DATA", "MOD_ML_MODELS"],
        signal="CO_ACCESS",
        value=3,
        threshold=2,
        reason="Frequent co-access in multi-domain retrieval queries"
    )
    cycle_shortcut = adapter.run_adaptation_cycle(shortcut_prop)

    # Adapted evaluation
    adapted_eval = adapter.evaluate()

    # 3. Read versions
    versions = adapter.list_versions()
    version_summaries = []
    for v in versions:
        version_summaries.append({
            "id": v.id,
            "operation": v.operation,
            "reason": v.reason,
            "status": v.status,
            "timestamp": v.timestamp,
            "metrics": {
                "recall_at_k": round(v.metrics.recall_at_k, 4),
                "precision_at_k": round(v.metrics.precision_at_k, 4),
                "mean_latency_ms": round(v.metrics.mean_latency_ms, 2)
            }
        })

    # 4. Read Lighthouse scores if generated
    lh_scores = {}
    lh_file = ROOT / "docs" / "lh-desktop.json"
    if lh_file.exists():
        try:
            with open(lh_file, "r", encoding="utf-8") as f:
                lh_data = json.load(f)
                cats = lh_data.get("categories", {})
                lh_scores = {
                    "performance": round(cats.get("performance", {}).get("score", 0.0) * 100),
                    "accessibility": round(cats.get("accessibility", {}).get("score", 0.0) * 100),
                    "best_practices": round(cats.get("best-practices", {}).get("score", 0.0) * 100),
                    "seo": round(cats.get("seo", {}).get("score", 0.0) * 100)
                }
        except Exception:
            pass

    # 5. Assemble results payload
    results = {
        "timestamp": time.time(),
        "date": "2026-10-25",
        "machine_info": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor()
        },
        "config": {
            "k": config.k,
            "min_recall": config.min_recall,
            "thresholds": config.thresholds,
            "model": config.model,
            "corpus_label": config.corpus_label,
            "seed": config.seed
        },
        "baseline": baseline,
        "v1_metrics": {
            "recall_at_k": round(v1_eval.metrics.recall_at_k, 4),
            "precision_at_k": round(v1_eval.metrics.precision_at_k, 4),
            "mean_latency_ms": round(v1_eval.metrics.mean_latency_ms, 2)
        },
        "adapted_metrics": {
            "recall_at_k": round(adapted_eval.metrics.recall_at_k, 4),
            "precision_at_k": round(adapted_eval.metrics.precision_at_k, 4),
            "mean_latency_ms": round(adapted_eval.metrics.mean_latency_ms, 2)
        },
        "version_timeline": version_summaries,
        "lighthouse": lh_scores
    }

    out_path = ROOT / "docs" / "results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Results exported successfully to {out_path}")


if __name__ == "__main__":
    export_all()
