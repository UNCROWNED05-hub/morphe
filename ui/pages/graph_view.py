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
            st.markdown("<h3 style='font-size: 16px; font-weight: 700; margin-top: 16px; color: #FFFFFF;'>Modules (Nodes)</h3>", unsafe_allow_html=True)
            nodes_table = """
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Module ID</th>
                        <th>Label</th>
                        <th>Topic</th>
                        <th>Record Count</th>
                        <th>Access Count</th>
                    </tr>
                </thead>
                <tbody>
            """
            for n in payload["nodes"]:
                nodes_table += f"""
                <tr>
                    <td class="mono strong">{n['id']}</td>
                    <td>{n['label']}</td>
                    <td><span class="badge" style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.35); color: #A5B4FC;">{n['topic']}</span></td>
                    <td class="mono">{n['record_count']}</td>
                    <td class="mono">{n['access_count']}</td>
                </tr>
                """
            nodes_table += "</tbody></table>"
            st.markdown(nodes_table, unsafe_allow_html=True)

            st.markdown("<h3 style='font-size: 16px; font-weight: 700; margin-top: 24px; color: #FFFFFF;'>Pathways (Edges)</h3>", unsafe_allow_html=True)
            edges_table = """
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Target</th>
                        <th>Kind</th>
                        <th>Weight</th>
                        <th>Co-Access Count</th>
                    </tr>
                </thead>
                <tbody>
            """
            for e in payload["edges"]:
                kind_badge = "badge-amber" if e['kind'] == 'shortcut' else "badge-blue"
                edges_table += f"""
                <tr>
                    <td class="mono strong">{e['source']}</td>
                    <td class="mono strong">{e['target']}</td>
                    <td><span class="badge {kind_badge}">{e['kind']}</span></td>
                    <td class="mono">{e['weight']:.3f}</td>
                    <td class="mono">{e['co_access']}</td>
                </tr>
                """
            edges_table += "</tbody></table>"
            st.markdown(edges_table, unsafe_allow_html=True)

        else:
            # Legend
            st.markdown("""
            <div style="display: flex; gap: 20px; font-size: 12px; color: var(--ink-soft); margin-bottom: 14px; padding: 10px 16px; background: linear-gradient(180deg, rgba(16, 23, 38, 0.8) 0%, rgba(13, 19, 32, 0.9) 100%); border: 1px solid var(--border); border-radius: var(--radius-sm); backdrop-filter: blur(8px);">
                <span style="display: inline-flex; align-items: center; gap: 6px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; background: #6366F1; box-shadow: 0 0 6px rgba(99, 102, 241, 0.6);"></span> Module Node
                </span>
                <span style="display: inline-flex; align-items: center; gap: 6px;">
                    <span style="width: 10px; height: 10px; border-radius: 50%; border: 2px dashed #F59E0B; box-shadow: 0 0 6px rgba(245, 158, 11, 0.6);"></span> Reconfigured
                </span>
                <span style="display: inline-flex; align-items: center; gap: 6px;">
                    <span style="width: 16px; height: 2px; background: #38BDF8;"></span> Semantic Pathway
                </span>
                <span style="display: inline-flex; align-items: center; gap: 6px;">
                    <span style="width: 16px; height: 2px; border-top: 2px dashed #F59E0B;"></span> Learned Shortcut
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
                <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px; margin-top: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px;">
                        <span style="font-size: 16px; font-weight: 700; color: var(--ink);">Module Inspector: {mod.label}</span>
                        <span class="mono badge badge-blue">ID: {mod.id}</span>
                    </div>
                    <div style="display: flex; gap: 24px; margin: 14px 0; font-size: 13px; color: var(--ink-soft);">
                        <div><strong style="color: var(--ink);">Records:</strong> <span class="mono" style="color: var(--ink);">{len(mod.record_ids)}</span></div>
                        <div><strong style="color: var(--ink);">Access Utilization:</strong> <span class="mono" style="color: var(--ink);">{mod.access_count} queries</span></div>
                        <div><strong style="color: var(--ink);">Direct Neighbors:</strong> <span class="mono" style="color: var(--ink);">{', '.join(mod.neighbors) if mod.neighbors else 'None'}</span></div>
                    </div>
                    <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-soft); margin-top: 14px; margin-bottom: 8px;">Contained Records:</div>
                </div>
                """, unsafe_allow_html=True)
                for r_id in mod.record_ids:
                    rec = adapter.engine.records.get(r_id, {})
                    st.markdown(f"""
                    <div style="padding: 10px 14px; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-sm); margin-bottom: 6px; font-size: 13px; color: var(--ink);">
                        <span class="mono" style="font-weight: 600; color: var(--primary);">{r_id}:</span> {rec.get('text', '')}
                    </div>
                    """, unsafe_allow_html=True)

            elif selected_edge:
                st.markdown(f"""
                <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px; margin-top: 16px;">
                    <span style="font-size: 16px; font-weight: 700; color: var(--ink);">Pathway Inspector</span>
                    <div style="display: flex; gap: 24px; margin-top: 12px; font-size: 13px; color: var(--ink-soft);">
                        <div><strong style="color: var(--ink);">Pathway:</strong> <span class="mono" style="color: var(--ink);">{selected_edge.get('source')} &harr; {selected_edge.get('target')}</span></div>
                        <div><strong style="color: var(--ink);">Kind:</strong> <span class="badge badge-amber">{selected_edge.get('kind')}</span></div>
                        <div><strong style="color: var(--ink);">Weight:</strong> <span class="mono" style="color: var(--ink);">{selected_edge.get('weight')}</span></div>
                        <div><strong style="color: var(--ink);">Co-Access Count:</strong> <span class="mono" style="color: var(--ink);">{selected_edge.get('co_access')}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error loading graph: {str(e)}")

render()
