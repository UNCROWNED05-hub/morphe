import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError

# Nav icon SVG
LOGO_SVG = """<svg width="30" height="30" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="18" cy="32" r="8.5" fill="#6366F1"/>
  <path d="M26.5 32 H35 L46 19 M35 32 L46 45" stroke="#818CF8" stroke-width="3.5" stroke-linecap="round" opacity="0.85"/>
  <circle cx="47" cy="19" r="7.5" fill="#06B6D4"/>
  <circle cx="47" cy="45" r="7.5" fill="#10B981"/>
  <circle cx="18" cy="32" r="12" stroke="#6366F1" stroke-width="1.5" stroke-opacity="0.4"/>
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
    <div style="padding:22px 16px 18px 16px; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.06);">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
        {LOGO_SVG}
        <div>
          <span style="font-size:20px;font-weight:800;letter-spacing:-0.03em;
                       background:linear-gradient(135deg, #FFFFFF 0%, #C7D2FE 100%);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;">MORPHE</span>
          <div style="font-size:10px;color:#94A3B8;letter-spacing:0.08em;text-transform:uppercase;font-weight:600;">Adaptive Memory OS</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:4px 12px;margin-bottom:6px;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#64748B;">Workspace</div>', unsafe_allow_html=True)

    st.page_link(pages["Overview"], label="Overview")
    st.page_link(pages["Memory"],   label="Memory")
    st.page_link(pages["Retrieve"], label="Retrieve")
    st.page_link(pages["Graph"],    label="Graph")
    st.page_link(pages["Adapt"],    label="Adapt")
    st.page_link(pages["History"],  label="History")

    st.markdown("<hr style='margin:12px 8px !important;'>", unsafe_allow_html=True)

    try:
        _a = EngineAdapter()
        _c = _a.get_config()
        _versions = _a.list_versions()
        _ver = _versions[-1].id if _versions else "V1"
        _status = _versions[-1].status if _versions else "BASELINE"
        _dot_color = "#10B981" if _status in ("ACCEPTED","BASELINE","NEUTRAL") else "#F43F5E"
        st.markdown(f"""
        <div style="margin:4px 8px;padding:12px 14px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:10px;font-size:12px;line-height:1.6;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="width:8px;height:8px;border-radius:50%;background:{_dot_color};flex-shrink:0;display:inline-block;box-shadow:0 0 8px {_dot_color};"></span>
            <span style="font-weight:700;color:#F8FAFC;font-size:12px;">Engine Online</span>
            <span style="margin-left:auto;font-family:'IBM Plex Mono',monospace;font-size:10px;color:#94A3B8;background:rgba(255,255,255,0.06);padding:1px 6px;border-radius:4px;">{_ver}</span>
          </div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#94A3B8;">model: <span style="color:#CBD5E1;">{_c.model}</span></div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#94A3B8;">corpus: <span style="color:#CBD5E1;">{_c.corpus_label}</span></div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <div style="margin:4px 8px;padding:12px 14px;background:rgba(244,63,94,0.06);border:1px solid rgba(244,63,94,0.2);border-radius:10px;font-size:12px;">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="width:8px;height:8px;border-radius:50%;background:#F43F5E;flex-shrink:0;display:inline-block;box-shadow:0 0 8px #F43F5E;"></span>
            <span style="font-weight:700;color:#FB7185;">Engine Offline</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.page_link(pages["Privacy"], label="Privacy")
    st.page_link(pages["Terms"],   label="Terms")

current_page.run()
