import streamlit as st

THEME_CSS = """
:root {
  /* Clean, matte, executive dark palette (Linear/Stripe style) */
  --bg: #0D0E10;
  --surface: #151619;
  --surface-2: #1C1E22;
  --surface-3: #25282F;
  --border: #262930;
  --border-bright: #383D47;
  --border-focus: #5E6AD2;

  /* Typography */
  --ink: #ECEFF2;
  --ink-soft: #8F96A3;
  --ink-dim: #5F6673;

  /* Refined, muted functional accents (Zero neon) */
  --primary: #5E6AD2;
  --primary-hover: #4F5BD5;
  --primary-dim: rgba(94, 106, 210, 0.12);

  --violet: #7A6899;
  --violet-dim: rgba(122, 104, 153, 0.12);

  --amber: #C98A2C;
  --amber-dim: rgba(201, 138, 44, 0.12);
  --green: #2FA873;
  --green-dim: rgba(47, 168, 115, 0.12);
  --red: #D9534F;
  --red-dim: rgba(217, 83, 79, 0.12);
  --blue: #4A88B5;
  --blue-dim: rgba(74, 136, 181, 0.12);
  --sage: #3E8A78;
  --sage-dim: rgba(62, 138, 120, 0.12);

  /* Topic fills for modules */
  --topic-1: #5E6AD2;
  --topic-2: #3E8A78;
  --topic-3: #C98A2C;
  --topic-4: #5A7DA0;
  --topic-5: #B2586A;
  --topic-6: #7A6899;

  --radius-sm: 5px;
  --radius: 8px;
  --radius-lg: 12px;

  --ease-out: cubic-bezier(.2, 0.8, .2, 1);
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
  width: 245px !important;
  min-width: 245px !important;
  max-width: 245px !important;
  background-color: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
  display: none !important;
}
[data-testid="stSidebar"] .stPageLink a {
  color: var(--ink-soft) !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  padding: 8px 12px !important;
  border-radius: var(--radius-sm) !important;
  margin: 2px 8px !important;
  transition: color 100ms, background 100ms !important;
  display: flex !important;
  align-items: center !important;
}
[data-testid="stSidebar"] .stPageLink a:hover {
  color: var(--ink) !important;
  background: var(--surface-2) !important;
}
[data-testid="stSidebar"] .stPageLink a[aria-current="page"] {
  color: var(--ink) !important;
  background: var(--surface-2) !important;
  border-left: 3px solid var(--primary) !important;
  font-weight: 600 !important;
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
  border-color: var(--border-focus) !important;
  box-shadow: 0 0 0 1px var(--border-focus) !important;
  background-color: var(--surface-2) !important;
}

/* ---- Buttons ---- */
button, .stButton > button {
  font-family: 'Atkinson Hyperlegible', sans-serif !important;
  border-radius: var(--radius-sm) !important;
  transition: all 120ms var(--ease-out) !important;
  font-weight: 600 !important;
  height: 38px !important;
}
.stButton > button[kind="primary"] {
  background: var(--primary) !important;
  color: #FFFFFF !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--primary-hover) !important;
}
.stButton > button[kind="secondary"] {
  background: var(--surface-2) !important;
  color: var(--ink-soft) !important;
  border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
  color: var(--ink) !important;
  border-color: var(--border-bright) !important;
  background: var(--surface-3) !important;
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
  font-size: 11.5px !important;
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
  padding: 18px !important;
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
  padding: 20px 22px;
  position: relative;
  overflow: hidden;
  transition: border-color 120ms ease;
}
.stat-card:hover {
  border-color: var(--border-bright);
}
.stat-card .stat-num {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 30px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.15;
  margin-bottom: 6px;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}
.stat-card .stat-label {
  font-size: 11.5px;
  font-weight: 600;
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
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-family: 'IBM Plex Mono', monospace;
}
.badge-green {
  background: var(--green-dim);
  color: #38C182;
  border: 1px solid rgba(47, 168, 115, 0.25);
}
.badge-red {
  background: var(--red-dim);
  color: #E26864;
  border: 1px solid rgba(217, 83, 79, 0.25);
}
.badge-violet {
  background: var(--violet-dim);
  color: #9E8EC0;
  border: 1px solid rgba(122, 104, 153, 0.25);
}
.badge-amber {
  background: var(--amber-dim);
  color: #DC9B3C;
  border: 1px solid rgba(201, 138, 44, 0.25);
}
.badge-blue {
  background: var(--blue-dim);
  color: #62A0CD;
  border: 1px solid rgba(74, 136, 181, 0.25);
}
.badge-cyan {
  background: var(--sage-dim);
  color: #55A894;
  border: 1px solid rgba(62, 138, 120, 0.25);
}

/* ---- Panel / card ---- */
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}
.panel-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-soft);
  margin-bottom: 12px;
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
  letter-spacing: 0.05em;
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
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  margin-bottom: 8px;
  transition: border-color 120ms ease;
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
  color: #9E8EC0;
  background: var(--violet-dim);
  border: 1px solid rgba(122, 104, 153, 0.25);
  border-radius: 3px;
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
  font-weight: 600;
  color: #DC9B3C;
  margin-left: auto;
}
.result-text {
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--ink);
}

/* ---- Adapt step headers ---- */
.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  margin-top: 24px;
}
.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 4px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  font-size: 12px;
  font-weight: 700;
  color: var(--ink);
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
  border: 1px solid rgba(47, 168, 115, 0.3);
}
.decision-banner.rejected {
  background: var(--red-dim);
  border: 1px solid rgba(217, 83, 79, 0.3);
}
.decision-banner.neutral {
  background: var(--primary-dim);
  border: 1px solid rgba(94, 106, 210, 0.3);
}

/* ---- Version timeline item ---- */
.ver-item {
  display: flex;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}
.ver-item:last-child { border-bottom: none; }
.ver-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
}
.ver-body { flex: 1; }
.ver-id {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 13.5px;
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
  margin-top: 6px;
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
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px 32px;
  margin-bottom: 24px;
  position: relative;
}
.hero-tagline {
  font-size: 26px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.3;
  max-width: 58ch;
  margin-bottom: 10px;
}
.hero-sub {
  font-size: 14.5px;
  color: var(--ink-soft);
  max-width: 64ch;
  line-height: 1.6;
}

/* ---- Signal row ---- */
.signal-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 0;
  border-bottom: 1px solid var(--border);
}
.signal-row:last-child { border-bottom: none; }
.signal-indicator {
  width: 7px;
  height: 7px;
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
  border-radius: var(--radius-sm) !important;
  border-left-width: 3px !important;
  background: var(--surface) !important;
}

/* Page title styling */
h1[data-testid="stHeading"], [data-testid="stMarkdownContainer"] h1 {
  font-size: 24px !important;
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

