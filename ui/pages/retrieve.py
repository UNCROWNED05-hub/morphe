import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError


def render_traversal_svg(graph, touched_modules, path):
    if not touched_modules:
        return ""
    nodes = list(touched_modules)
    n = len(nodes)
    width, height = 680, 190

    import math
    positions = {}
    if n == 1:
        positions[nodes[0]] = (width / 2, height / 2)
    else:
        cx, cy, r = width / 2, height / 2, min(width, height) * 0.38
        for i, nid in enumerate(nodes):
            angle = (2 * math.pi * i / n) - math.pi / 2
            positions[nid] = (cx + r * math.cos(angle), cy + r * math.sin(angle))

    edges_svg = []
    for edge in path:
        if len(edge) == 2 and edge[0] in positions and edge[1] in positions:
            x1, y1 = positions[edge[0]]
            x2, y2 = positions[edge[1]]
            edges_svg.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="#F59E0B" stroke-width="2.8" stroke-dasharray="6 3" opacity="0.9" filter="drop-shadow(0 0 4px rgba(245,158,11,0.6))"/>'
            )

    node_colors = ["#6366F1", "#06B6D4", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"]
    nodes_svg = []
    for i, (nid, (px, py)) in enumerate(positions.items()):
        color = node_colors[i % len(node_colors)]
        label = nid if len(nid) <= 16 else nid[:14] + "…"
        nodes_svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="22" fill="{color}" opacity="0.2" filter="drop-shadow(0 0 8px {color})"/>'
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="15" fill="{color}" opacity="0.95" stroke="#FFFFFF" stroke-width="1.5"/>'
            f'<text x="{px:.1f}" y="{py + 32:.1f}" text-anchor="middle" '
            f'font-family="IBM Plex Mono" font-size="11" fill="#E2E8F0" font-weight="600">{label}</text>'
        )

    return f"""
    <div style="background:linear-gradient(180deg, rgba(16,23,38,0.85) 0%, rgba(13,19,32,0.95) 100%);
                border:1px solid var(--border);border-radius:var(--radius-lg);
                padding:18px;margin:18px 0;box-shadow:0 4px 20px rgba(0,0,0,0.3);">
      <div style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;
                   color:var(--ink-soft);margin-bottom:12px;display:flex;align-items:center;gap:8px;">
        <span style="width:6px;height:6px;border-radius:50%;background:#F59E0B;box-shadow:0 0 6px #F59E0B;"></span>
        Memory Traversal Pathway Telemetry
      </div>
      <svg width="100%" height="{height}" viewBox="0 0 {width} {height}" style="overflow:visible;">
        {''.join(edges_svg)}
        {''.join(nodes_svg)}
      </svg>
    </div>
    """


def render():
    st.markdown("# Retrieve")
    st.markdown('<div style="font-size:14px;color:var(--ink-soft);margin-bottom:20px;">Semantic search across memory modules with traversal inspection.</div>', unsafe_allow_html=True)

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()

        # ── Frozen query chips ────────────────────────────────────────────────
        eval_queries = adapter.eval_queries()
        if eval_queries:
            st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-dim);margin-bottom:8px;">Benchmark queries</div>', unsafe_allow_html=True)
            chip_cols = st.columns(min(4, len(eval_queries)))
            for idx, q_item in enumerate(eval_queries[:4]):
                q_text = q_item.get("query", "")
                with chip_cols[idx]:
                    label = q_text[:28] + ("…" if len(q_text) > 28 else "")
                    if st.button(label, key=f"chip_{idx}", use_container_width=True, type="secondary"):
                        st.session_state["active_query_text"] = q_text
                        st.rerun()

        # ── Search form ───────────────────────────────────────────────────────
        default_query = st.session_state.get("active_query_text", "What Java concepts should I study?")
        with st.form("search_form"):
            q_col, k_col, btn_col = st.columns([5, 1, 1])
            with q_col:
                query_input = st.text_input("Query", value=default_query, label_visibility="collapsed",
                                             placeholder="Enter a semantic query…")
            with k_col:
                k_val = st.number_input("K", min_value=1, max_value=20, value=config.k)
            with btn_col:
                search_clicked = st.form_submit_button("Search", type="primary", use_container_width=True)

        placeholder = st.empty()

        if search_clicked or "last_query_result" in st.session_state:
            if search_clicked:
                placeholder.markdown(
                    '<div class="skeleton" style="height:80px;margin:16px 0;"></div>',
                    unsafe_allow_html=True
                )
                res = adapter.query(text=query_input, k=k_val)
                st.session_state["last_query_result"] = res
                placeholder.empty()
            else:
                res = st.session_state["last_query_result"]

            # ── Summary banner ─────────────────────────────────────────────────
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:20px;padding:16px 22px;
                         background:linear-gradient(180deg, rgba(16,23,38,0.9) 0%, rgba(13,19,32,0.95) 100%);
                         border:1px solid var(--border);border-radius:var(--radius-lg);margin:16px 0;
                         box-shadow:0 4px 16px rgba(0,0,0,0.3);">
              <div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:26px;font-weight:700;color:#FFFFFF;">
                  {len(res.results)}
                </span>
                <span style="font-size:12px;color:var(--ink-soft);margin-left:6px;text-transform:uppercase;font-weight:600;">records</span>
              </div>
              <div style="width:1px;height:32px;background:var(--border);"></div>
              <div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:26px;font-weight:700;color:#38BDF8;">
                  {len(res.modules_accessed)}
                </span>
                <span style="font-size:12px;color:var(--ink-soft);margin-left:6px;text-transform:uppercase;font-weight:600;">modules hit</span>
              </div>
              <div style="width:1px;height:32px;background:var(--border);"></div>
              <div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:26px;font-weight:700;color:#FBBF24;">
                  {res.latency_ms:.1f}<span style="font-size:14px;color:var(--ink-dim);">ms</span>
                </span>
                <span style="font-size:12px;color:var(--ink-soft);margin-left:6px;text-transform:uppercase;font-weight:600;">latency</span>
              </div>
              <div style="margin-left:auto;font-size:13px;color:#A5B4FC;background:rgba(99,102,241,0.1);padding:4px 12px;border-radius:6px;border:1px solid rgba(99,102,241,0.25);max-width:40ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-family:'IBM Plex Mono',monospace;">
                "{res.query}"
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Traversal SVG ──────────────────────────────────────────────────
            graph = adapter.get_graph()
            svg = render_traversal_svg(graph, res.modules_accessed, res.path)
            if svg:
                st.markdown(svg, unsafe_allow_html=True)

            # ── Results ────────────────────────────────────────────────────────
            st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:12px;margin-top:10px;">Retrieved Knowledge Chunks</div>', unsafe_allow_html=True)
            for rank, item in enumerate(res.results, start=1):
                score_pct = f"{item.score:.3f}"
                bar_width = max(6, int(item.score * 100))
                st.markdown(f"""
                <div class="result-row">
                  <div class="result-meta">
                    <span class="result-rank">#{rank}</span>
                    <span class="result-id">{item.record_id}</span>
                    <span class="badge badge-violet" style="font-size:10px;">{item.module_id}</span>
                    <span class="result-score">similarity {score_pct}</span>
                  </div>
                  <div style="height:3px;background:rgba(255,255,255,0.06);border-radius:3px;margin-bottom:12px;overflow:hidden;">
                    <div style="height:100%;width:{bar_width}%;background:linear-gradient(90deg, #6366F1, #06B6D4);border-radius:3px;box-shadow:0 0 8px rgba(6,182,212,0.5);"></div>
                  </div>
                  <div class="result-text">{item.text}</div>
                </div>
                """, unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error: {e}")


render()
