import streamlit as st

THEME_CSS = """
:root {
  --paper: #F2F4F0;
  --ink: #0F1B24;
  --ink-soft: #46555F;
  --rule: #D3D9D2;
  --structure: #1E4D6B;
  --change: #F0B429;
  --accepted: #2D6A4F;
  --rejected: #B23A2E;
  
  --topic-1: #2F6F8F;
  --topic-2: #5B8C5A;
  --topic-3: #8A6F4E;
  --topic-4: #3E8E86;
  --topic-5: #A8556B;
  --topic-6: #6B7C93;

  --ease-out: cubic-bezier(.22, 1, .36, 1);
  --ease-io: cubic-bezier(.65, 0, .35, 1);
}

@font-face {
  font-family: 'Atkinson Hyperlegible';
  src: url('/app/static/fonts/atkinson-hyperlegible-latin-400-normal.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Atkinson Hyperlegible';
  src: url('/app/static/fonts/atkinson-hyperlegible-latin-700-normal.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'IBM Plex Mono';
  src: url('/app/static/fonts/ibm-plex-mono-latin-400-normal.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

/* Base resets & typography */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background-color: var(--paper) !important;
  color: var(--ink) !important;
  font-family: 'Atkinson Hyperlegible', sans-serif !important;
  line-height: 1.5 !important;
}

/* Hide Streamlit default chrome & deploy button */
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"], .stDeployButton {
  display: none !important;
  visibility: hidden !important;
}

/* Suppress stale element fade & flicker */
[data-testid="stApp"] [data-stale="true"] {
  opacity: 1 !important;
  filter: none !important;
  transition: none !important;
}

/* Main container constraints */
.main .block-container {
  max-width: 1240px !important;
  padding-top: 2rem !important;
  padding-bottom: 3rem !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}

/* Control borders & radius: 2px controls, 4px panels, NEVER pills */
button, input, select, textarea, [data-baseweb="input"], [data-baseweb="select"] {
  border-radius: 2px !important;
  font-family: 'Atkinson Hyperlegible', sans-serif !important;
}

/* Primary buttons: ink fill, paper text, 40px height */
button[kind="primary"], .stButton > button[kind="primary"] {
  background-color: var(--ink) !important;
  color: var(--paper) !important;
  border: 1px solid var(--ink) !important;
  height: 40px !important;
  border-radius: 2px !important;
  font-weight: 600 !important;
  transition: transform 120ms var(--ease-out), opacity 120ms var(--ease-out) !important;
}
button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
  opacity: 0.9 !important;
  transform: translateY(-1px) !important;
}
button[kind="primary"]:active, .stButton > button[kind="primary"]:active {
  transform: translateY(0px) !important;
  opacity: 0.8 !important;
}

/* Secondary buttons: 1px ink outline */
button[kind="secondary"], .stButton > button[kind="secondary"] {
  background-color: transparent !important;
  color: var(--ink) !important;
  border: 1px solid var(--ink) !important;
  height: 40px !important;
  border-radius: 2px !important;
  transition: transform 120ms var(--ease-out), opacity 120ms var(--ease-out) !important;
}
button[kind="secondary"]:hover, .stButton > button[kind="secondary"]:hover {
  background-color: var(--rule) !important;
  opacity: 0.9 !important;
}

/* Inputs */
input, textarea {
  border: 1px solid var(--rule) !important;
  background-color: #FFFFFF !important;
  color: var(--ink) !important;
}
input:focus, textarea:focus {
  border-color: var(--structure) !important;
  box-shadow: 0 0 0 1px var(--structure) !important;
}

/* Tabular mono numbers */
.mono-val, td, .metric-num {
  font-family: 'IBM Plex Mono', monospace !important;
  font-variant-numeric: tabular-nums !important;
}

/* Hairline dividers */
hr {
  border: none !important;
  border-top: 1px solid var(--rule) !important;
  margin: 1.5rem 0 !important;
}

/* Custom rail styling */
[data-testid="stSidebar"] {
  width: 232px !important;
  min-width: 232px !important;
  max-width: 232px !important;
  background-color: #EAECE6 !important;
  border-right: 1px solid var(--rule) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
  display: none !important;
}

/* Skeleton loader */
.skeleton {
  background-color: #E2E6DF;
  border-radius: 2px;
  animation: skeleton-pulse 1.4s ease-in-out infinite;
}
@keyframes skeleton-pulse {
  0% { opacity: 0.5; }
  50% { opacity: 0.9; }
  100% { opacity: 0.5; }
}

/* Status marks */
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 6px;
  border-radius: 2px;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.2;
}
.status-accepted {
  background-color: rgba(45, 106, 79, 0.12);
  color: var(--accepted);
  border: 1px solid rgba(45, 106, 79, 0.25);
}
.status-rejected {
  background-color: rgba(178, 58, 46, 0.12);
  color: var(--rejected);
  border: 1px solid rgba(178, 58, 46, 0.25);
}
.status-baseline {
  background-color: rgba(30, 77, 107, 0.12);
  color: var(--structure);
  border: 1px solid rgba(30, 77, 107, 0.25);
}
.status-change {
  background-color: rgba(240, 180, 41, 0.18);
  color: #8C6205;
  border: 1px solid rgba(240, 180, 41, 0.35);
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
"""

def inject_theme():
    # Minify CSS by stripping comments and blank lines
    minified = "\n".join(
        line.strip() for line in THEME_CSS.splitlines()
        if line.strip() and not line.strip().startswith("/*")
    )
    st.markdown(f"<style>{minified}</style>", unsafe_allow_html=True)
