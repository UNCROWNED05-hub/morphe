import streamlit as st

THEME_CSS = """
:root {
  /* Core dark palette */
  --bg: #0A0A0F;
  --surface: #111118;
  --surface-2: #1A1A24;
  --border: #2A2A38;
  --border-bright: #3A3A50;

  /* Text */
  --ink: #E8E8F0;
  --ink-soft: #8888A8;
  --ink-dim: #555568;

  /* Accent colors */
  --violet: #7C6AF7;
  --violet-dim: rgba(124, 106, 247, 0.15);
  --violet-glow: rgba(124, 106, 247, 0.3);
  --amber: #F5A623;
  --amber-dim: rgba(245, 166, 35, 0.15);
  --green: #3DD68C;
  --green-dim: rgba(61, 214, 140, 0.12);
  --red: #F56565;
  --red-dim: rgba(245, 101, 101, 0.12);
  --blue: #63B3ED;
  --blue-dim: rgba(99, 179, 237, 0.12);

  /* Topic fills */
  --topic-1: #7C6AF7;
  --topic-2: #3DD68C;
  --topic-3: #F5A623;
  --topic-4: #63B3ED;
  --topic-5: #F56565;
  --topic-6: #D6BCFA;

  --radius-sm: 4px;
  --radius: 8px;
  --radius-lg: 12px;

  --ease-out: cubic-bezier(.22, 1, .36, 1);
}

@font-face {
  font-family: 'Atkinson Hyperlegible';
  src: url('/app/static/fonts/atkinson-hyperlegible-latin-400-normal.woff2') format('woff2');
  font-weight: 400; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'Atkinson Hyperlegible';
  src: url('/app/static/fonts/atkinson-hyperlegible-latin-700-normal.woff2') format('woff2');
  font-weight: 700; font-style: normal; font-display: swap;
}
@font-face {
  font-family: 'IBM Plex Mono';
  src: url('/app/static/fonts/ibm-plex-mono-latin-400-normal.woff2') format('woff2');
  font-weight: 400; font-style: normal; font-display: swap;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background-color: var(--bg) !important;
  color: var(--ink) !important;
  font-family: 'Atkinson Hyperlegible', sans-serif !important;
}

#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"], .stDeployButton {
  display: none !important;
}

[data-testid="stApp"] [data-stale="true"] {
  opacity: 1 !important;
  filter: none !important;
  transition: none !important;
}

.main .block-container {
  max-width: 1280px !important;
  padding-top: 1.5rem !important;
  padding-bottom: 4rem !important;
  padding-left: 2.5rem !important;
  padding-right: 2.5rem !important;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
  width: 240px !important;
  min-width: 240px !important;
  max-width: 240px !important;
  background-color: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
  display: none !important;
}
[data-testid="stSidebar"] .stPageLink a {
  color: var(--ink-soft) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 8px 12px !important;
  border-radius: var(--radius-sm) !important;
  transition: color 120ms, background 120ms !important;
  display: block !important;
}
[data-testid="stSidebar"] .stPageLink a:hover {
  color: var(--ink) !important;
  background: var(--surface-2) !important;
}
[data-testid="stSidebar"] .stPageLink a[aria-current="page"] {
  color: var(--violet) !important;
  background: var(--violet-dim) !important;
}

/* ---- Inputs ---- */
input, textarea, [data-baseweb="input"] input {
  background-color: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  color: var(--ink) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Atkinson Hyperlegible', sans-serif !important;
}
input:focus, textarea:focus {
  border-color: var(--violet) !important;
  box-shadow: 0 0 0 3px var(--violet-glow) !important;
}

/* ---- Buttons ---- */
button, .stButton > button {
  font-family: 'Atkinson Hyperlegible', sans-serif !important;
  border-radius: var(--radius-sm) !important;
  transition: all 140ms var(--ease-out) !important;
  font-weight: 600 !important;
  height: 38px !important;
}
.stButton > button[kind="primary"] {
  background: var(--violet) !important;
  color: #fff !important;
  border: none !important;
}
.stButton > button[kind="primary"]:hover {
  background: #8f7ef9 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px var(--violet-glow) !important;
}
.stButton > button[kind="secondary"] {
  background: transparent !important;
  color: var(--ink-soft) !important;
  border: 1px solid var(--border-bright) !important;
}
.stButton > button[kind="secondary"]:hover {
  color: var(--ink) !important;
  border-color: var(--violet) !important;
  background: var(--violet-dim) !important;
}

/* ---- Select boxes ---- */
[data-baseweb="select"] > div {
  background-color: var(--surface-2) !important;
  border-color: var(--border) !important;
  border-radius: var(--radius-sm) !important;
}

/* ---- Metric widgets ---- */
[data-testid="stMetricValue"] {
  font-size: 28px !important;
  font-weight: 700 !important;
  color: var(--ink) !important;
  font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricLabel"] {
  font-size: 12px !important;
  color: var(--ink-soft) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}
[data-testid="stMetricDelta"] {
  font-size: 13px !important;
  font-family: 'IBM Plex Mono', monospace !important;
}

/* ---- Line chart ---- */
[data-testid="stVegaLiteChart"] {
  background: var(--surface) !important;
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
}

/* ---- Expander ---- */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}
[data-testid="stExpander"] summary {
  color: var(--ink-soft) !important;
  font-size: 14px !important;
}

/* ---- Form ---- */
[data-testid="stForm"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 16px !important;
}

/* ---- HR ---- */
hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 1.5rem 0 !important;
}

/* ---- Mono utility ---- */
.mono {
  font-family: 'IBM Plex Mono', monospace !important;
  font-variant-numeric: tabular-nums !important;
}

/* ---- Stat cards ---- */
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 24px;
}
.stat-card:hover {
  border-color: var(--border-bright);
}
.stat-card .stat-num {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 32px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1;
  margin-bottom: 6px;
  font-variant-numeric: tabular-nums;
}
.stat-card .stat-label {
  font-size: 12px;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.stat-card .stat-sub {
  font-size: 12px;
  color: var(--ink-dim);
  margin-top: 4px;
  font-family: 'IBM Plex Mono', monospace;
}

/* ---- Badge / status pills ---- */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.badge-green {
  background: var(--green-dim);
  color: var(--green);
  border: 1px solid rgba(61,214,140,0.25);
}
.badge-red {
  background: var(--red-dim);
  color: var(--red);
  border: 1px solid rgba(245,101,101,0.25);
}
.badge-violet {
  background: var(--violet-dim);
  color: var(--violet);
  border: 1px solid rgba(124,106,247,0.3);
}
.badge-amber {
  background: var(--amber-dim);
  color: var(--amber);
  border: 1px solid rgba(245,166,35,0.3);
}
.badge-blue {
  background: var(--blue-dim);
  color: var(--blue);
  border: 1px solid rgba(99,179,237,0.25);
}

/* ---- Panel / card ---- */
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}
.panel-title {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-soft);
  margin-bottom: 14px;
}

/* ---- Table ---- */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.data-table th {
  padding: 10px 12px;
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-dim);
  border-bottom: 1px solid var(--border);
}
.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  color: var(--ink-soft);
  vertical-align: middle;
}
.data-table tr:last-child td {
  border-bottom: none;
}
.data-table tr:hover td {
  background: var(--surface-2);
  color: var(--ink);
}
.data-table td.strong {
  color: var(--ink);
  font-weight: 600;
}

/* ---- Result row ---- */
.result-row {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 18px;
  margin-bottom: 8px;
  transition: border-color 120ms;
}
.result-row:hover {
  border-color: var(--border-bright);
}
.result-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.result-rank {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  color: var(--violet);
  background: var(--violet-dim);
  border: 1px solid rgba(124,106,247,0.3);
  border-radius: 4px;
  padding: 2px 7px;
}
.result-id {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: var(--ink-soft);
}
.result-score {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: var(--amber);
  margin-left: auto;
}
.result-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--ink);
}

/* ---- Adapt step headers ---- */
.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  margin-top: 28px;
}
.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--violet-dim);
  border: 1px solid rgba(124,106,247,0.4);
  font-size: 13px;
  font-weight: 700;
  color: var(--violet);
  flex-shrink: 0;
}
.step-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--ink);
}
.step-sub {
  font-size: 13px;
  color: var(--ink-soft);
  margin-left: auto;
}

/* ---- Decision banner ---- */
.decision-banner {
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 20px;
}
.decision-banner.accepted {
  background: var(--green-dim);
  border: 1px solid rgba(61,214,140,0.25);
}
.decision-banner.rejected {
  background: var(--red-dim);
  border: 1px solid rgba(245,101,101,0.25);
}
.decision-banner.neutral {
  background: var(--violet-dim);
  border: 1px solid rgba(124,106,247,0.25);
}

/* ---- Version timeline item ---- */
.ver-item {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}
.ver-item:last-child { border-bottom: none; }
.ver-dot {
  flex-shrink: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 5px;
}
.ver-body { flex: 1; }
.ver-id {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
}
.ver-op {
  font-size: 13px;
  color: var(--ink-soft);
  margin-top: 2px;
}
.ver-metrics {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}
.ver-metric-item {
  font-size: 12px;
  color: var(--ink-dim);
}
.ver-metric-item strong {
  color: var(--ink-soft);
  font-family: 'IBM Plex Mono', monospace;
}

/* ---- Overview hero ---- */
.hero-block {
  background: linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px 36px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
}
.hero-block::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 300px; height: 300px;
  background: radial-gradient(circle at 100% 0%, var(--violet-glow) 0%, transparent 70%);
  pointer-events: none;
}
.hero-tagline {
  font-size: 30px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.25;
  max-width: 56ch;
  margin-bottom: 12px;
}
.hero-sub {
  font-size: 15px;
  color: var(--ink-soft);
  max-width: 62ch;
  line-height: 1.6;
}

/* ---- Signal row ---- */
.signal-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.signal-row:last-child { border-bottom: none; }
.signal-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ---- Skeleton ---- */
.skeleton {
  background: linear-gradient(90deg, var(--surface) 25%, var(--surface-2) 50%, var(--surface) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: var(--radius-sm);
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ---- Info / alert boxes ---- */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  border-left-width: 3px !important;
  background: var(--surface) !important;
}

/* Page title styling */
h1[data-testid="stHeading"], [data-testid="stMarkdownContainer"] h1 {
  font-size: 26px !important;
  font-weight: 700 !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em !important;
  margin-bottom: 4px !important;
}

/* Reduced-motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
"""

def inject_theme():
    minified = "\n".join(
        line.strip() for line in THEME_CSS.splitlines()
        if line.strip() and not line.strip().startswith("/*")
    )
    st.markdown(f"<style>{minified}</style>", unsafe_allow_html=True)
