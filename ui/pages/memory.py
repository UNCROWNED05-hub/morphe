import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError, RecordModel


@st.dialog("Reset Demo State")
def confirm_reset_dialog(adapter: EngineAdapter):
    st.write("Are you sure you want to reset MORPHE to the initial baseline (V1)? All subsequent structural adaptations will be cleared.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset demo state", type="primary"):
            adapter.reset()
            st.rerun()
    with col2:
        if st.button("Cancel"):
            st.rerun()


def render():
    st.title("Memory Management")
    st.caption("Inspect stored knowledge records, module assignments, and ingest new text.")

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()

        # Action bar
        act1, act2 = st.columns([1, 1])
        with act1:
            if st.button(f"Load corpus ({config.corpus_label})", type="secondary"):
                adapter.load_sample()
                st.success("Corpus loaded.")
                st.rerun()
        with act2:
            if st.button("Reset demo state", type="secondary"):
                confirm_reset_dialog(adapter)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Ingestion form
        st.markdown("<h3 style='font-size: 17px; font-weight: 600; margin-bottom: 8px;'>Add Memory</h3>", unsafe_allow_html=True)
        with st.form("add_memory_form", clear_on_submit=True):
            mem_text = st.text_area("Memory Text", placeholder="Enter knowledge text to chunk, embed, and assign to a memory module...")
            mem_source = st.text_input("Source Identifier", value="user_input")
            submitted = st.form_submit_button("Ingest Memory", type="primary")

            if submitted:
                if mem_text.strip():
                    new_records = adapter.add_memory(text=mem_text.strip(), source=mem_source.strip())
                    st.session_state["last_added_records"] = new_records
                    st.rerun()
                else:
                    st.warning("Please provide non-empty text.")

        if "last_added_records" in st.session_state and st.session_state["last_added_records"]:
            st.markdown("<div style='padding: 12px; background: rgba(30,77,107,0.08); border: 1px solid var(--structure); border-radius: 4px; margin: 12px 0;'>", unsafe_allow_html=True)
            st.markdown("<span style='font-weight: 600; font-size: 13px; color: var(--structure);'>Ingested Records Strip:</span>", unsafe_allow_html=True)
            for rec in st.session_state["last_added_records"]:
                st.markdown(f"<div class='mono-val' style='font-size: 12px; margin-top: 4px;'><strong>{rec.id}</strong> -> Assigned Module: <code>{rec.module_id}</code> | Excerpt: {rec.text[:70]}...</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Records Ledger with Pagination & Filters
        st.markdown("<h3 style='font-size: 17px; font-weight: 600; margin-bottom: 8px;'>Stored Records Ledger</h3>", unsafe_allow_html=True)
        all_records = adapter.list_records()

        # Filter controls
        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            search_term = st.text_input("Filter records by text", placeholder="Type to filter...").strip().lower()
        with f_col2:
            modules_list = sorted(list({r.module_id for r in all_records if r.module_id}))
            selected_mod = st.selectbox("Filter by Module", ["All"] + modules_list)

        filtered_records = all_records
        if search_term:
            filtered_records = [r for r in filtered_records if search_term in r.text.lower() or search_term in r.id.lower()]
        if selected_mod != "All":
            filtered_records = [r for r in filtered_records if r.module_id == selected_mod]

        total_count = len(filtered_records)
        page_size = 25
        total_pages = max(1, (total_count + page_size - 1) // page_size)

        p_col1, p_col2 = st.columns([1, 3])
        with p_col1:
            page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        with p_col2:
            st.caption(f"Showing {min(total_count, (page_num - 1) * page_size + 1)} to {min(total_count, page_num * page_size)} of {total_count} records")

        start_idx = (page_num - 1) * page_size
        end_idx = start_idx + page_size
        page_records = filtered_records[start_idx:end_idx]

        # Render Table
        table_html = """
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px;">
            <thead>
                <tr style="border-bottom: 1px solid var(--rule); text-align: left; color: var(--ink-soft);">
                    <th style="padding: 8px 4px; width: 120px;">Record ID</th>
                    <th style="padding: 8px 4px; width: 120px;">Module</th>
                    <th style="padding: 8px 4px; width: 110px;">Topic</th>
                    <th style="padding: 8px 4px;">Text Excerpt</th>
                    <th style="padding: 8px 4px; width: 90px;">Source</th>
                </tr>
            </thead>
            <tbody>
        """
        for r in page_records:
            table_html += f"""
                <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                    <td class="mono-val" style="padding: 8px 4px; font-weight: 600;">{r.id}</td>
                    <td class="mono-val" style="padding: 8px 4px;"><span class="status-tag status-baseline">{r.module_id}</span></td>
                    <td style="padding: 8px 4px; color: var(--ink-soft);">{r.topic}</td>
                    <td style="padding: 8px 4px;">{r.text}</td>
                    <td style="padding: 8px 4px; color: var(--ink-soft);">{r.source}</td>
                </tr>
            """
        table_html += "</tbody></table>"

        if total_count > 0:
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("No records match the current filter criteria.")

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error loading records: {str(e)}")

render()
