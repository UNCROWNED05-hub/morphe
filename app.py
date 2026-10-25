import streamlit as st
from ui.theme import inject_theme
from ui.adapter import EngineAdapter
from ui.models import EngineContractError

# 1. Must be the very first Streamlit command
st.set_page_config(
    page_title="MORPHE",
    page_icon="static/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject design system tokens and resets
inject_theme()

# 3. Define navigation pages (do NOT pass icon= to st.Page)
pages = {
    "Overview": st.Page("ui/pages/overview.py", title="Overview"),
    "Memory": st.Page("ui/pages/memory.py", title="Memory"),
    "Retrieve": st.Page("ui/pages/retrieve.py", title="Retrieve"),
    "Graph": st.Page("ui/pages/graph_view.py", title="Graph"),
    "Adapt": st.Page("ui/pages/adapt.py", title="Adapt"),
    "History": st.Page("ui/pages/history.py", title="History"),
    "Privacy": st.Page("ui/pages/privacy.py", title="Privacy"),
    "Terms": st.Page("ui/pages/terms.py", title="Terms")
}

# 4. Hidden default navigation so custom persistent rail drives routing
current_page = st.navigation(list(pages.values()), position="hidden")

# 5. Build persistent left rail (232px)
with st.sidebar:
    st.markdown("""
    <div style="padding: 12px 4px 18px 4px; border-bottom: 1px solid var(--rule); margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <svg width="24" height="24" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="20" cy="32" r="7" fill="#1E4D6B"/>
                <path d="M27 32 H36 L46 20 M36 32 L46 44" stroke="#1E4D6B" stroke-width="4" stroke-linecap="round"/>
                <circle cx="48" cy="18" r="6" fill="#F0B429"/>
                <circle cx="48" cy="46" r="6" fill="#2D6A4F"/>
            </svg>
            <span style="font-size: 17px; font-weight: 700; letter-spacing: -0.02em; color: var(--ink);">MORPHE</span>
        </div>
        <div style="font-size: 11px; color: var(--ink-soft); margin-top: 4px;">Adaptive Memory System</div>
    </div>
    """, unsafe_allow_html=True)

    # Five main nav links as words
    st.page_link(pages["Overview"], label="Overview")
    st.page_link(pages["Memory"], label="Memory")
    st.page_link(pages["Retrieve"], label="Retrieve")
    st.page_link(pages["Graph"], label="Graph")
    st.page_link(pages["Adapt"], label="Adapt")
    st.page_link(pages["History"], label="History")

    # Engine status line in rail
    st.markdown("<hr style='margin: 16px 0;'>", unsafe_allow_html=True)
    try:
        adapter = EngineAdapter()
        config = adapter.get_config()
        st.markdown(f"""
        <div style="font-size: 12px; color: var(--ink-soft); line-height: 1.4;">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                <span style="display: inline-block; width: 7px; height: 7px; border-radius: 2px; background-color: var(--accepted);"></span>
                <span style="font-weight: 600; color: var(--ink);">Engine Online</span>
            </div>
            <div class="mono-val" style="font-size: 11px;">Model: {config.model}</div>
            <div class="mono-val" style="font-size: 11px;">Corpus: {config.corpus_label}</div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
        <div style="font-size: 12px; color: var(--rejected); line-height: 1.4;">
            <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                <span style="display: inline-block; width: 7px; height: 7px; border-radius: 2px; background-color: var(--rejected);"></span>
                <span style="font-weight: 600;">Engine Offline</span>
            </div>
            <div style="font-size: 11px;">Connecting...</div>
        </div>
        """, unsafe_allow_html=True)

    # Footer links for Privacy and Terms
    st.markdown("""
    <div style="position: fixed; bottom: 16px; width: 200px; font-size: 12px; border-top: 1px solid var(--rule); padding-top: 12px;">
    </div>
    """, unsafe_allow_html=True)
    st.page_link(pages["Privacy"], label="Privacy")
    st.page_link(pages["Terms"], label="Terms")

# 6. Execute selected route
current_page.run()
