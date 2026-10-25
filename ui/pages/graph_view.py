import streamlit as st
from ui.adapter import EngineAdapter
from ui.graph_payload import build_graph_payload
from ui.components import morphe_graph_component
from ui.models import EngineContractError


def render():
    st.title("Memory Graph")
    st.caption("Inspect live NetworkX memory topology, module centroids, and retrieval pathways.")

    try:
        adapter = EngineAdapter()
        versions = adapter.list_versions()
        ver_ids = [v.id for v in versions] if versions else ["V1"]

        # Controls row
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            selected_ver = st.selectbox("Architecture Version", ver_ids, index=len(ver_ids)-1)
        with c2:
            st.write("")
            st.write("")
            view_mode = st.radio("Display Mode", ["Graph Canvas", "Table View"], horizontal=True)

        graph = adapter.get_graph()
        modules_meta = adapter.engine.modules

        # Get changed modules for active version
        active_version_obj = next((v for v in versions if v.id == selected_ver), None) if versions else None
        changed_mods = []
        if active_version_obj and hasattr(adapter.engine, "history"):
            for h in adapter.engine.history:
                if h["version"] == selected_ver:
                    op_info = h.get("op_info", {})
                    if op_info.get("type") == "SPLIT":
                        changed_mods = op_info.get("new_modules", [])
                    elif op_info.get("type") == "MERGE":
                        changed_mods = [op_info.get("merged_module", "")]
                    elif op_info.get("type") == "SHORTCUT":
                        changed_mods = [op_info.get("module_a", ""), op_info.get("module_b", "")]

        payload = build_graph_payload(
            graph,
            modules_meta=modules_meta,
            changed_modules=changed_mods
        )

        if view_mode == "Table View":
            st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-top: 16px;'>Modules (Nodes)</h3>", unsafe_allow_html=True)
            nodes_table = """
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="border-bottom: 1px solid var(--rule); text-align: left; color: var(--ink-soft);">
                        <th style="padding: 6px 4px;">Module ID</th>
                        <th style="padding: 6px 4px;">Label</th>
                        <th style="padding: 6px 4px;">Topic</th>
                        <th style="padding: 6px 4px;">Record Count</th>
                        <th style="padding: 6px 4px;">Access Count</th>
                    </tr>
                </thead>
                <tbody>
            """
            for n in payload["nodes"]:
                nodes_table += f"""
                <tr style="border-bottom: 1px solid rgba(211,217,210,0.4);">
                    <td class="mono-val" style="padding: 6px 4px; font-weight: 600;">{n['id']}</td>
                    <td style="padding: 6px 4px;">{n['label']}</td>
                    <td style="padding: 6px 4px;">{n['topic']}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{n['record_count']}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{n['access_count']}</td>
                </tr>
                """
            nodes_table += "</tbody></table>"
            st.markdown(nodes_table, unsafe_allow_html=True)

            st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-top: 24px;'>Pathways (Edges)</h3>", unsafe_allow_html=True)
            edges_table = """
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="border-bottom: 1px solid var(--rule); text-align: left; color: var(--ink-soft);">
                        <th style="padding: 6px 4px;">Source</th>
                        <th style="padding: 6px 4px;">Target</th>
                        <th style="padding: 6px 4px;">Kind</th>
                        <th style="padding: 6px 4px;">Weight</th>
                        <th style="padding: 6px 4px;">Co-Access Count</th>
                    </tr>
                </thead>
                <tbody>
            """
            for e in payload["edges"]:
                edges_table += f"""
                <tr style="border-bottom: 1px solid rgba(211,217,210,0.4);">
                    <td class="mono-val" style="padding: 6px 4px; font-weight: 600;">{e['source']}</td>
                    <td class="mono-val" style="padding: 6px 4px; font-weight: 600;">{e['target']}</td>
                    <td style="padding: 6px 4px;">{e['kind']}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{e['weight']:.3f}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{e['co_access']}</td>
                </tr>
                """
            edges_table += "</tbody></table>"
            st.markdown(edges_table, unsafe_allow_html=True)

        else:
            # Legend
            st.markdown("""
            <div style="display: flex; gap: 16px; font-size: 12px; color: var(--ink-soft); margin-bottom: 8px;">
                <span style="display: inline-flex; align-items: center; gap: 4px;">
                    <span style="width: 12px; height: 12px; border-radius: 2px; background: #1E4D6B;"></span> Semantic Module
                </span>
                <span style="display: inline-flex; align-items: center; gap: 4px;">
                    <span style="width: 12px; height: 12px; border-radius: 2px; border: 2px solid #F0B429;"></span> Reconfigured / Changed
                </span>
                <span style="display: inline-flex; align-items: center; gap: 4px;">
                    <span style="width: 16px; height: 2px; background: #1E4D6B;"></span> Semantic Pathway
                </span>
                <span style="display: inline-flex; align-items: center; gap: 4px;">
                    <span style="width: 16px; height: 2px; border-top: 2px dashed #F0B429;"></span> Shortcut Connection
                </span>
            </div>
            """, unsafe_allow_html=True)

            # Mount graph custom component
            comp_res = morphe_graph_component(
                data=payload,
                key=f"morphe_graph_{selected_ver}",
                on_selected_node_change=lambda: None,
                on_selected_edge_change=lambda: None,
                on_closed_drawer_change=lambda: None
            )

            # Selection detection with explicit fallback controls
            selected_node = comp_res.selected_node if comp_res and hasattr(comp_res, "selected_node") else None
            selected_edge = comp_res.selected_edge if comp_res and hasattr(comp_res, "selected_edge") else None

            st.write("")
            c_sel1, c_sel2 = st.columns([1, 1])
            with c_sel1:
                node_opts = ["(None selected)"] + [f"{n['id']} | {n['label']} ({n['record_count']} records)" for n in payload["nodes"]]
                user_node_choice = st.selectbox("Inspect Module Details", node_opts, index=0)
                if user_node_choice != "(None selected)":
                    selected_node = user_node_choice.split(" | ")[0]
            with c_sel2:
                edge_opts = ["(None selected)"] + [f"{e['source']} <-> {e['target']} [{e['kind']}]" for e in payload["edges"]]
                user_edge_choice = st.selectbox("Inspect Pathway Details", edge_opts, index=0)
                if user_edge_choice != "(None selected)":
                    src, rest = user_edge_choice.split(" <-> ")
                    tgt = rest.split(" [")[0]
                    selected_edge = next((e for e in payload["edges"] if (e["source"] == src and e["target"] == tgt) or (e["source"] == tgt and e["target"] == src)), None)

            # Inspector Drawer
            if selected_node:
                mod = adapter.get_module(selected_node)
                st.markdown(f"""
                <div style="background: #F8FAF7; border: 1px solid var(--rule); border-radius: 4px; padding: 16px; margin-top: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--rule); pb: 8px;">
                        <span style="font-size: 16px; font-weight: 700; color: var(--ink);">Module Inspector: {mod.label}</span>
                        <span class="mono-val status-tag status-baseline">ID: {mod.id}</span>
                    </div>
                    <div style="display: flex; gap: 24px; margin: 12px 0; font-size: 13px;">
                        <div><strong>Records:</strong> <span class="mono-val">{len(mod.record_ids)}</span></div>
                        <div><strong>Access Utilization:</strong> <span class="mono-val">{mod.access_count} queries</span></div>
                        <div><strong>Direct Graph Neighbors:</strong> <span class="mono-val">{', '.join(mod.neighbors) if mod.neighbors else 'None'}</span></div>
                    </div>
                    <div style="font-size: 13px; font-weight: 600; margin-top: 12px; margin-bottom: 6px;">Contained Records Excerpts:</div>
                </div>
                """, unsafe_allow_html=True)
                for r_id in mod.record_ids:
                    rec = adapter.engine.records.get(r_id, {})
                    st.markdown(f"""
                    <div style="padding: 8px 12px; background: #FFFFFF; border: 1px solid var(--rule); border-radius: 2px; margin-bottom: 6px; font-size: 13px;">
                        <span class="mono-val" style="font-weight: 600; color: var(--structure);">{r_id}:</span> {rec.get('text', '')}
                    </div>
                    """, unsafe_allow_html=True)

            elif selected_edge:
                st.markdown(f"""
                <div style="background: #F8FAF7; border: 1px solid var(--rule); border-radius: 4px; padding: 16px; margin-top: 16px;">
                    <span style="font-size: 16px; font-weight: 700; color: var(--ink);">Pathway Inspector</span>
                    <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 13px;">
                        <div><strong>Pathway:</strong> <span class="mono-val">{selected_edge.get('source')} &harr; {selected_edge.get('target')}</span></div>
                        <div><strong>Kind:</strong> <span class="status-tag status-change">{selected_edge.get('kind')}</span></div>
                        <div><strong>Weight:</strong> <span class="mono-val">{selected_edge.get('weight')}</span></div>
                        <div><strong>Co-Access Count:</strong> <span class="mono-val">{selected_edge.get('co_access')}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error loading graph: {str(e)}")

render()
