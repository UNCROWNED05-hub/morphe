import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError

# Nav icon SVG
LOGO_SVG = """<svg width="26" height="26" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="18" cy="32" r="8" fill="#5E6AD2"/>
  <path d="M26 32 H35 L46 20 M35 32 L46 44" stroke="#5E6AD2" stroke-width="3" stroke-linecap="round" opacity="0.5"/>
  <circle cx="48" cy="20" r="7" fill="#3E8A78"/>
  <circle cx="48" cy="44" r="7" fill="#C98A2C"/>
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
    <div style="padding:18px 16px 14px 16px; margin-bottom:6px; border-bottom:1px solid var(--border);">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
        {LOGO_SVG}
        <div>
          <span style="font-size:17px;font-weight:700;letter-spacing:-0.02em;color:var(--ink);">MORPHE</span>
          <div style="font-size:10px;color:var(--ink-dim);letter-spacing:0.06em;text-transform:uppercase;font-weight:600;">Adaptive Memory</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:4px 12px;margin-bottom:4px;font-size:10px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--ink-dim);">Workspace</div>', unsafe_allow_html=True)

    st.page_link(pages["Overview"], label="Overview")
    st.page_link(pages["Memory"],   label="Memory")
    st.page_link(pages["Retrieve"], label="Retrieve")
    st.page_link(pages["Graph"],    label="Graph")
    st.page_link(pages["Adapt"],    label="Adapt")
    st.page_link(pages["History"],  label="History")

    st.markdown("<hr style='margin:10px 8px !important;'>", unsafe_allow_html=True)

    try:
        _a = EngineAdapter()
        _c = _a.get_config()
        _versions = _a.list_versions()
        _ver = _versions[-1].id if _versions else "V1"
        _status = _versions[-1].status if _versions else "BASELINE"
        _dot_color = "#2FA873" if _status in ("ACCEPTED","BASELINE","NEUTRAL") else "#D9534F"
        st.markdown(f"""
        <div style="margin:4px 8px;padding:10px 12px;background:var(--surface-2);border:1px solid var(--border);border-radius:6px;font-size:12px;line-height:1.5;">
          <div style="display:flex;align-items:center;gap:7px;margin-bottom:6px;">
            <span style="width:7px;height:7px;border-radius:50%;background:{_dot_color};flex-shrink:0;display:inline-block;"></span>
            <span style="font-weight:600;color:var(--ink);font-size:12px;">Engine Online</span>
            <span style="margin-left:auto;font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--ink-soft);background:var(--surface);border:1px solid var(--border);padding:1px 5px;border-radius:3px;">{_ver}</span>
          </div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--ink-soft);">model: <span style="color:var(--ink);">{_c.model}</span></div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--ink-soft);">corpus: <span style="color:var(--ink);">{_c.corpus_label}</span></div>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <div style="margin:4px 8px;padding:10px 12px;background:var(--surface-2);border:1px solid var(--border);border-radius:6px;font-size:12px;">
          <div style="display:flex;align-items:center;gap:7px;">
            <span style="width:7px;height:7px;border-radius:50%;background:#D9534F;flex-shrink:0;display:inline-block;"></span>
            <span style="font-weight:600;color:#D9534F;">Engine Offline</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.page_link(pages["Privacy"], label="Privacy")
    st.page_link(pages["Terms"],   label="Terms")

current_page.run()
