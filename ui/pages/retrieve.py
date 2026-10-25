import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError, QueryResult


def render_small_graph(graph, touched_modules, path):
    """Draws an SVG subgraph of the touched modules and traversed path."""
    if not touched_modules:
        return ""

    width = 600
    height = 200
    nodes = list(touched_modules)
    num_nodes = len(nodes)
    
    # Simple horizontal layout
    positions = {}
    margin_x = 80
    spacing = (width - 2 * margin_x) / max(1, num_nodes - 1) if num_nodes > 1 else 0
    for idx, node_id in enumerate(nodes):
        cx = margin_x + idx * spacing if num_nodes > 1 else width / 2
        cy = height / 2
        positions[node_id] = (cx, cy)

    svg_lines = []
    # Draw path edges
    for edge in path:
        if len(edge) == 2 and edge[0] in positions and edge[1] in positions:
            p1 = positions[edge[0]]
            p2 = positions[edge[1]]
            svg_lines.append(
                f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" '
                f'stroke="#F0B429" stroke-width="3" stroke-dasharray="4 2"/>'
            )

    # Draw nodes
    svg_nodes = []
    for node_id, (cx, cy) in positions.items():
        # Outer amber ring for touched module
        svg_nodes.append(
            f'<circle cx="{cx}" cy="{cy}" r="22" fill="none" stroke="#F0B429" stroke-width="2.5" class="touched-pulse"/>'
        )
        # Inner node circle
        svg_nodes.append(
            f'<circle cx="{cx}" cy="{cy}" r="16" fill="#1E4D6B"/>'
        )
        # Label
        svg_nodes.append(
            f'<text x="{cx}" y="{cy + 34}" text-anchor="middle" font-family="IBM Plex Mono" font-size="11" fill="#0F1B24" font-weight="600">{node_id}</text>'
        )

    return f"""
    <div style="background: #FFFFFF; border: 1px solid var(--rule); border-radius: 4px; padding: 12px; margin-top: 12px;">
        <div style="font-size: 12px; font-weight: 600; color: var(--ink-soft); margin-bottom: 4px;">Traversal Pathway Across Modules:</div>
        <svg width="100%" height="{height}" viewBox="0 0 {width} {height}" style="overflow: visible;">
            {''.join(svg_lines)}
            {''.join(svg_nodes)}
        </svg>
    </div>
    """


def render():
    st.title("Semantic Retrieval")
    st.caption("Execute semantic queries across memory modules with 1-hop traversal inspection.")

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()

        # Frozen evaluation queries as chips
        st.markdown("<div style='font-size: 13px; font-weight: 600; color: var(--ink); margin-bottom: 6px;'>Frozen Evaluation Queries (1-Click):</div>", unsafe_allow_html=True)
        eval_queries = adapter.eval_queries()
        
        chip_cols = st.columns(min(4, len(eval_queries)))
        for idx, q_item in enumerate(eval_queries[:4]):
            with chip_cols[idx]:
                q_text = q_item.get("query", "")
                if st.button(f"{q_text[:30]}...", key=f"chip_{idx}", use_container_width=True):
                    st.session_state["active_query_text"] = q_text
                    st.rerun()

        default_query = st.session_state.get("active_query_text", "What Java concepts should I study?")

        # Search Form
        with st.form("search_form"):
            col_q, col_k, col_btn = st.columns([4, 1, 1])
            with col_q:
                query_input = st.text_input("Query", value=default_query, placeholder="Enter search query...")
            with col_k:
                k_val = st.number_input("Top K", min_value=1, max_value=20, value=config.k)
            with col_btn:
                st.write("")
                st.write("")
                search_clicked = st.form_submit_button("Search", type="primary", use_container_width=True)

        # Loading placeholder for neutral skeleton
        placeholder = st.empty()

        if search_clicked or "last_query_result" in st.session_state:
            active_q = query_input if search_clicked else st.session_state["last_query_result"].query

            if search_clicked:
                # Show neutral skeleton block before engine call
                placeholder.markdown("""
                <div class="skeleton" style="height: 120px; width: 100%; margin: 16px 0;"></div>
                """, unsafe_allow_html=True)

                res = adapter.query(text=active_q, k=k_val)
                st.session_state["last_query_result"] = res
                placeholder.empty()
            else:
                res = st.session_state["last_query_result"]

            # Summary line
            num_records = len(res.results)
            num_modules = len(res.modules_accessed)
            st.markdown(f"""
            <div style="padding: 10px 14px; background: rgba(30,77,107,0.06); border: 1px solid var(--rule); border-radius: 4px; margin: 16px 0; font-size: 14px;">
                Retrieved <strong class="mono-val">{num_records}</strong> records from <strong class="mono-val">{num_modules}</strong> modules in <strong class="mono-val">{res.latency_ms:.2f} ms</strong>.
            </div>
            """, unsafe_allow_html=True)

            # Traversal graph
            graph = adapter.get_graph()
            svg_graph = render_small_graph(graph, res.modules_accessed, res.path)
            st.markdown(svg_graph, unsafe_allow_html=True)

            # Results List
            st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-top: 20px; margin-bottom: 8px;'>Retrieved Knowledge Chunks</h3>", unsafe_allow_html=True)
            for rank, item in enumerate(res.results, start=1):
                st.markdown(f"""
                <div style="padding: 12px; background: #FFFFFF; border: 1px solid var(--rule); border-radius: 4px; margin-bottom: 8px; animation: enter-row 240ms ease-out;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 600; font-size: 13px;">#{rank} <span class="mono-val">{item.record_id}</span></span>
                        <div>
                            <span class="status-tag status-baseline" style="margin-right: 8px;">Module: {item.module_id}</span>
                            <span class="mono-val" style="font-size: 12px; color: var(--ink-soft);">Score: {item.score:.4f}</span>
                        </div>
                    </div>
                    <div style="font-size: 14px; color: var(--ink);">{item.text}</div>
                </div>
                """, unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error during retrieval: {str(e)}")

render()
