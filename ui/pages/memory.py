import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError


@st.dialog("Reset Demo State")
def confirm_reset_dialog(adapter: EngineAdapter):
    st.markdown('<div style="font-size:15px;color:var(--ink);margin-bottom:16px;">Reset MORPHE to the initial V1 baseline? All structural adaptations and version history after V1 will be cleared.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Reset", type="primary", use_container_width=True):
            adapter.reset()
            st.rerun()
    with c2:
        if st.button("Cancel", type="secondary", use_container_width=True):
            st.rerun()


def render():
    st.markdown("# Memory")
    st.markdown('<div style="font-size:14px;color:var(--ink-soft);margin-bottom:24px;">Ingest text, inspect stored records, and manage the knowledge corpus.</div>', unsafe_allow_html=True)

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()

        # ── Action bar ──────────────────────────────────────────────────────────
        act1, act2, spacer = st.columns([1.4, 1.4, 3])
        with act1:
            if st.button(f"Load corpus ({config.corpus_label})", type="primary", use_container_width=True):
                adapter.load_sample()
                st.success("Corpus loaded.")
                st.rerun()
        with act2:
            if st.button("Reset demo state", type="secondary", use_container_width=True):
                confirm_reset_dialog(adapter)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Ingestion form ───────────────────────────────────────────────────────
        st.markdown('<div class="panel-title">Add Memory</div>', unsafe_allow_html=True)
        with st.form("add_memory_form", clear_on_submit=True):
            mem_text = st.text_area(
                "Memory text",
                placeholder="Enter knowledge text to chunk, embed, and assign to a memory module...",
                height=100
            )
            col_src, col_btn = st.columns([3, 1])
            with col_src:
                mem_source = st.text_input("Source identifier", value="user_input")
            with col_btn:
                st.write("")
                submitted = st.form_submit_button("Ingest", type="primary", use_container_width=True)

            if submitted:
                if mem_text.strip():
                    new_records = adapter.add_memory(text=mem_text.strip(), source=mem_source.strip())
                    st.session_state["last_added_records"] = new_records
                    st.rerun()
                else:
                    st.warning("Please provide non-empty text.")

        # ── Ingestion result strip ───────────────────────────────────────────────
        if st.session_state.get("last_added_records"):
            recs = st.session_state["last_added_records"]
            items_html = "".join(
                f'<div style="display:flex;align-items:baseline;gap:10px;padding:6px 0;border-bottom:1px solid var(--border);">'
                f'<span class="mono" style="font-size:12px;color:var(--violet);font-weight:700;">{r.id}</span>'
                f'<span style="font-size:12px;color:var(--ink-dim);">→</span>'
                f'<span class="badge badge-violet">{r.module_id}</span>'
                f'<span style="font-size:12px;color:var(--ink-soft);flex:1;">{r.text[:80]}…</span>'
                f'</div>'
                for r in recs
            )
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid rgba(124,106,247,0.3);border-radius:var(--radius);
                         padding:14px 18px;margin:12px 0;">
              <div style="font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;
                           color:var(--violet);margin-bottom:8px;">Ingested {len(recs)} record(s)</div>
              {items_html}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Records table ────────────────────────────────────────────────────────
        all_records = adapter.list_records()

        f1, f2 = st.columns([3, 2])
        with f1:
            search_term = st.text_input("Search records", placeholder="Filter by text or ID…").strip().lower()
        with f2:
            mods = sorted({r.module_id for r in all_records if r.module_id})
            selected_mod = st.selectbox("Module", ["All"] + mods)

        filtered = all_records
        if search_term:
            filtered = [r for r in filtered if search_term in r.text.lower() or search_term in r.id.lower()]
        if selected_mod != "All":
            filtered = [r for r in filtered if r.module_id == selected_mod]

        total = len(filtered)
        page_size = 25
        total_pages = max(1, (total + page_size - 1) // page_size)

        pg_col, info_col = st.columns([1, 4])
        with pg_col:
            page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        with info_col:
            st.markdown(f'<div style="font-size:12px;color:var(--ink-dim);padding-top:32px;">{total} records</div>', unsafe_allow_html=True)

        start = (page_num - 1) * page_size
        page_records = filtered[start:start + page_size]

        if total == 0:
            st.info("No records match. Load the corpus first or clear filters.")
        else:
            # Topic → color map (deterministic by hash)
            topic_colors = ["#7C6AF7", "#3DD68C", "#F5A623", "#63B3ED", "#F56565", "#D6BCFA"]
            topic_map = {}
            rows_html = ""
            for r in page_records:
                if r.topic not in topic_map:
                    topic_map[r.topic] = topic_colors[len(topic_map) % len(topic_colors)]
                tc = topic_map[r.topic]
                rows_html += f"""
                <tr>
                  <td class="strong mono" style="color:var(--violet);font-size:12px;">{r.id}</td>
                  <td><span class="badge badge-violet" style="font-size:10px;">{r.module_id}</span></td>
                  <td><span style="font-size:12px;font-weight:700;color:{tc};">{r.topic}</span></td>
                  <td style="color:var(--ink);max-width:480px;">{r.text[:100]}{"…" if len(r.text)>100 else ""}</td>
                  <td class="mono" style="font-size:11px;">{r.source}</td>
                </tr>"""

            st.markdown(f"""
            <div class="panel" style="padding:0;overflow:hidden;">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>ID</th><th>Module</th><th>Topic</th><th>Text</th><th>Source</th>
                  </tr>
                </thead>
                <tbody>{rows_html}</tbody>
              </table>
            </div>
            """, unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error: {e}")


render()
