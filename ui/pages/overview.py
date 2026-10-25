import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError

def render():
    st.title("Overview")
    st.markdown("""
<h2 style="font-size: 22px; font-weight: 700; color: var(--ink); margin-top: 0; margin-bottom: 8px;">
MORPHE reorganizes an AI agent's memory, then checks whether it helped.
</h2>
<p style="font-size: 15px; color: var(--ink-soft); max-width: 68ch; line-height: 1.5; margin-bottom: 24px;">
It splits overloaded modules, merges redundant ones, and adds shortcuts between modules retrieved together. Each change is scored on the same labelled queries and rolled back if retrieval gets worse.
</p>
""", unsafe_allow_html=True)

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()
        graph = adapter.get_graph()
        records = adapter.list_records()
        versions = adapter.list_versions()

        current_ver = versions[-1].id if versions else "V1"
        last_decision = versions[-1].status if versions else "BASELINE"

        st.markdown("<h3 style='font-size: 17px; font-weight: 600; margin-bottom: 12px;'>Live Architecture State</h3>", unsafe_allow_html=True)

        # Metric ledger table
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Records", len(records))
            st.caption("Active chunks in storage")
        with col2:
            st.metric("Modules", len(graph.nodes))
            st.caption("Graph module nodes")
        with col3:
            st.metric("Connections", len(graph.edges))
            st.caption("Graph pathway edges")
        with col4:
            st.metric("Active Version", current_ver)
            st.caption(f"Status: {last_decision}")

        st.markdown("<hr>", unsafe_allow_html=True)

        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Evaluation K", config.k)
        with col6:
            st.metric("Min Recall Gate", f"{config.min_recall:.2f}")
        with col7:
            st.metric("Embedding Model", config.model)
        with col8:
            st.metric("Corpus Label", config.corpus_label)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Primary actions
        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            if len(records) == 0:
                if st.button("Load sample corpus", type="primary"):
                    adapter.load_sample()
                    st.rerun()
            else:
                if st.button("Run adaptation cycle", type="primary"):
                    proposals = adapter.propose()
                    if proposals:
                        adapter.run_adaptation_cycle(proposals[0])
                        st.rerun()
                    else:
                        st.info("No structural weakness currently detected.")

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Engine connection failed: {str(e)}")

render()
