import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError

# Nav icon SVG
LOGO_SVG = """<svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="20" cy="32" r="8" fill="#7C6AF7"/>
  <path d="M28 32 H36 L46 20 M36 32 L46 44" stroke="#7C6AF7" stroke-width="3.5" stroke-linecap="round" opacity="0.6"/>
  <circle cx="48" cy="18" r="7" fill="#F5A623"/>
  <circle cx="48" cy="46" r="7" fill="#3DD68C"/>
</svg>"""

st.set_page_config(
    page_title="MORPHE",
    page_icon="static/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.theme import inject_theme
inject_theme()

pages = {
    "Overview":  st.Page("ui/pages/overview.py",   title="Overview"),
    "Memory":    st.Page("ui/pages/memory.py",     title="Memory"),
    "Retrieve":  st.Page("ui/pages/retrieve.py",   title="Retrieve"),
    "Graph":     st.Page("ui/pages/graph_view.py", title="Graph"),
    "Adapt":     st.Page("ui/pages/adapt.py",      title="Adapt"),
    "History":   st.Page("ui/pages/history.py",    title="History"),
    "Privacy":   st.Page("ui/pages/privacy.py",    title="Privacy"),
    "Terms":     st.Page("ui/pages/terms.py",      title="Terms"),
}

current_page = st.navigation(list(pages.values()), position="hidden")

with st.sidebar:
    st.markdown(f"""
    <div style="padding:20px 16px 16px 16px; margin-bottom:8px;">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
        {LOGO_SVG}
        <span style="font-size:18px;font-weight:700;letter-spacing:-0.03em;color:#E8E8F0;">MORPHE</span>
      </div>
      <div style="font-size:11px;color:#555568;letter-spacing:0.04em;text-transform:uppercase;margin-left:2px;">Adaptive Memory System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0 8px;margin-bottom:4px;font-size:11px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:#555568;">Navigation</div>', unsafe_allow_html=True)

    st.page_link(pages["Overview"], label="Overview")
    st.page_link(pages["Memory"],   label="Memory")
    st.page_link(pages["Retrieve"], label="Retrieve")
    st.page_link(pages["Graph"],    label="Graph")
    st.page_link(pages["Adapt"],    label="Adapt")
    st.page_link(pages["History"],  label="History")

    st.markdown("<hr>", unsafe_allow_html=True)

    try:
        _a = EngineAdapter()
        _c = _a.get_config()
        _versions = _a.list_versions()
        _ver = _versions[-1].id if _versions else "V1"
        _status = _versions[-1].status if _versions else "BASELINE"
        _dot_color = "#3DD68C" if _status in ("ACCEPTED","BASELINE","NEUTRAL") else "#F56565"
        st.markdown(f"""
        <div style="padding:0 8px;font-size:12px;line-height:1.6;">
          <div style="display:flex;align-items:center;gap:7px;margin-bottom:6px;">
            <span style="width:8px;height:8px;border-radius:50%;background:{_dot_color};flex-shrink:0;display:inline-block;box-shadow:0 0 6px {_dot_color}88;"></span>
            <span style="font-weight:700;color:#E8E8F0;font-size:12px;">Engine Online</span>
          </div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#555568;">model: {_c.model}</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#555568;">corpus: {_c.corpus_label}</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#555568;">version: {_ver}</div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <div style="padding:0 8px;font-size:12px;">
          <div style="display:flex;align-items:center;gap:7px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#F56565;flex-shrink:0;display:inline-block;"></span>
            <span style="font-weight:700;color:#F56565;">Engine Offline</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.page_link(pages["Privacy"], label="Privacy")
    st.page_link(pages["Terms"],   label="Terms")

current_page.run()
