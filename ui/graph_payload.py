import math
from typing import Dict, Any, List, Optional
import networkx as nx

TOPIC_COLORS = [
    "#6366F1",  # Electric Indigo
    "#06B6D4",  # Cyber Cyan
    "#10B981",  # Emerald Mint
    "#F59E0B",  # Amber Gold
    "#EC4899",  # Neon Pink
    "#8B5CF6",  # Hyper Violet
    "#38BDF8",  # Sky Blue
    "#F97316",  # Sunset Orange
]


def build_graph_payload(
    G: nx.Graph,
    modules_meta: Optional[Dict[str, Any]] = None,
    prev_pos: Optional[Dict[str, List[float]]] = None,
    changed_modules: Optional[List[str]] = None,
    width: float = 800.0,
    height: float = 500.0
) -> Dict[str, Any]:
    """
    Constructs a compact JSON payload from the real NetworkX graph.
    Positions are computed deterministically via server-side spring_layout.
    """
    if len(G.nodes) == 0:
        return {"nodes": [], "edges": [], "summary": "Empty graph with 0 modules and 0 pathways"}

    # Fixed seed for deterministic layout
    pos = nx.spring_layout(G, seed=7, pos=prev_pos if prev_pos else None, k=1.8 / math.sqrt(len(G.nodes)))

    # Topic color mapping
    topic_map: Dict[str, str] = {}
    topic_idx = 0

    nodes_payload = []
    for node_id, data in G.nodes(data=True):
        meta = (modules_meta or {}).get(node_id, {})
        record_ids = meta.get("record_ids", data.get("record_ids", []))
        rec_count = len(record_ids)
        topic = meta.get("topic", data.get("topic", "general"))

        if topic not in topic_map:
            topic_map[topic] = TOPIC_COLORS[topic_idx % len(TOPIC_COLORS)]
            topic_idx += 1

        # Scale layout coordinates to canvas bounds with padding
        norm_x, norm_y = pos[node_id]
        # pos returns roughly [-1, 1]
        cx = round((norm_x + 1.0) / 2.0 * (width - 120) + 60, 3)
        cy = round((norm_y + 1.0) / 2.0 * (height - 120) + 60, 3)

        radius = max(12, min(36, 12 + rec_count * 1.5))
        is_changed = bool(changed_modules and node_id in changed_modules)

        nodes_payload.append({
            "id": str(node_id),
            "label": str(meta.get("name", meta.get("label", node_id))),
            "record_count": rec_count,
            "topic": topic,
            "fill": topic_map[topic],
            "x": cx,
            "y": cy,
            "r": radius,
            "access_count": meta.get("access_count", data.get("access_count", 0)),
            "changed": is_changed
        })

    edges_payload = []
    for u, v, data in G.edges(data=True):
        kind = data.get("kind", "semantic")
        weight = round(float(data.get("weight", 1.0)), 3)
        co_access = data.get("co_access", 0)

        edges_payload.append({
            "source": str(u),
            "target": str(v),
            "kind": kind,
            "weight": weight,
            "co_access": co_access
        })

    summary = f"Memory graph with {len(nodes_payload)} module nodes and {len(edges_payload)} pathway edges"

    return {
        "nodes": nodes_payload,
        "edges": edges_payload,
        "summary": summary
    }
