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
                f'stroke="#C98A2C" stroke-width="2" stroke-dasharray="5 3" opacity="0.9"/>'
            )

    node_colors = ["#5E6AD2", "#3E8A78", "#C98A2C", "#5A7DA0", "#B2586A", "#7A6899"]
    nodes_svg = []
    for i, (nid, (px, py)) in enumerate(positions.items()):
        color = node_colors[i % len(node_colors)]
        label = nid if len(nid) <= 16 else nid[:14] + "…"
        nodes_svg.append(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="14" fill="{color}" stroke="var(--surface)" stroke-width="2"/>'
            f'<text x="{px:.1f}" y="{py + 28:.1f}" text-anchor="middle" '
            f'font-family="IBM Plex Mono" font-size="10" fill="var(--ink-soft)" font-weight="600">{label}</text>'
        )

    return f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
                padding:16px;margin:16px 0;">
      <div style="font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;
                   color:var(--ink-dim);margin-bottom:12px;">Memory Traversal Pathway</div>
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
            <div style="display:flex;align-items:center;gap:18px;padding:14px 18px;
                         background:var(--surface);border:1px solid var(--border);
                         border-radius:var(--radius);margin:16px 0;">
              <div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:24px;font-weight:700;color:var(--ink);">
                  {len(res.results)}
                </span>
                <span style="font-size:12px;color:var(--ink-soft);margin-left:4px;text-transform:uppercase;">records</span>
              </div>
              <div style="width:1px;height:28px;background:var(--border);"></div>
              <div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:24px;font-weight:700;color:var(--ink);">
                  {len(res.modules_accessed)}
                </span>
                <span style="font-size:12px;color:var(--ink-soft);margin-left:4px;text-transform:uppercase;">modules</span>
              </div>
              <div style="width:1px;height:28px;background:var(--border);"></div>
              <div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:24px;font-weight:700;color:var(--amber);">
                  {res.latency_ms:.1f}<span style="font-size:13px;color:var(--ink-dim);">ms</span>
                </span>
                <span style="font-size:12px;color:var(--ink-soft);margin-left:4px;text-transform:uppercase;">latency</span>
              </div>
              <div style="margin-left:auto;font-size:12px;color:var(--ink-soft);background:var(--surface-2);padding:3px 10px;border-radius:4px;border:1px solid var(--border);max-width:36ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-family:'IBM Plex Mono',monospace;">
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
            st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-dim);margin-bottom:12px;margin-top:8px;">Retrieved Records</div>', unsafe_allow_html=True)
            for rank, item in enumerate(res.results, start=1):
                score_pct = f"{item.score:.3f}"
                bar_width = max(4, int(item.score * 100))
                st.markdown(f"""
                <div class="result-row">
                  <div class="result-meta">
                    <span class="result-rank">#{rank}</span>
                    <span class="result-id">{item.record_id}</span>
                    <span class="badge badge-violet" style="font-size:10px;">{item.module_id}</span>
                    <span class="result-score">{score_pct}</span>
                  </div>
                  <div style="height:2px;background:var(--surface-2);border-radius:2px;margin-bottom:10px;overflow:hidden;">
                    <div style="height:100%;width:{bar_width}%;background:var(--primary);border-radius:2px;"></div>
                  </div>
                  <div class="result-text">{item.text}</div>
                </div>
                """, unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error: {e}")


render()
