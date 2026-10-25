import streamlit as st

THEME_CSS = """
:root {
  /* Rich obsidian & nebula foundation */
  --bg: #080C15;
  --surface: #0F1626;
  --surface-2: #162035;
  --surface-3: #1E2B47;
  --border: rgba(255, 255, 255, 0.08);
  --border-bright: rgba(255, 255, 255, 0.16);
  --border-focus: rgba(99, 102, 241, 0.5);

  /* High-legibility typography */
  --ink: #F8FAFC;
  --ink-soft: #94A3B8;
  --ink-dim: #64748B;
  --ink-muted: #475569;

  /* Multi-spectrum chromatic accents */
  --primary: #6366F1;
  --primary-hover: #4F46E5;
  --primary-dim: rgba(99, 102, 241, 0.14);
  --primary-glow: rgba(99, 102, 241, 0.35);

  --violet: #8B5CF6;
  --violet-dim: rgba(139, 92, 246, 0.14);
  --violet-glow: rgba(139, 92, 246, 0.35);

  --cyan: #06B6D4;
  --cyan-dim: rgba(6, 182, 212, 0.14);

  --amber: #F59E0B;
  --amber-dim: rgba(245, 158, 11, 0.14);
  --green: #10B981;
  --green-dim: rgba(16, 185, 129, 0.14);
  --red: #F43F5E;
  --red-dim: rgba(244, 63, 94, 0.14);
  --blue: #38BDF8;
  --blue-dim: rgba(56, 189, 248, 0.14);
  --pink: #EC4899;
  --pink-dim: rgba(236, 72, 153, 0.14);

  /* Topic fills for modules */
  --topic-1: #6366F1;
  --topic-2: #06B6D4;
  --topic-3: #10B981;
  --topic-4: #F59E0B;
  --topic-5: #EC4899;
  --topic-6: #8B5CF6;

  --radius-sm: 6px;
  --radius: 10px;
  --radius-lg: 16px;

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
  background-image:
    radial-gradient(at 15% 15%, rgba(99, 102, 241, 0.08) 0px, transparent 45%),
    radial-gradient(at 85% 10%, rgba(6, 182, 212, 0.06) 0px, transparent 40%),
    radial-gradient(at 50% 90%, rgba(139, 92, 246, 0.05) 0px, transparent 50%) !important;
  background-attachment: fixed !important;
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
  width: 250px !important;
  min-width: 250px !important;
  max-width: 250px !important;
  background: linear-gradient(180deg, #0C111D 0%, #080C14 100%) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.25) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
  display: none !important;
}
[data-testid="stSidebar"] .stPageLink a {
  color: var(--ink-soft) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 9px 14px !important;
  border-radius: var(--radius) !important;
  margin: 2px 8px !important;
  transition: all 140ms var(--ease-out) !important;
  display: flex !important;
  align-items: center !important;
}
[data-testid="stSidebar"] .stPageLink a:hover {
  color: #FFFFFF !important;
  background: var(--surface-2) !important;
  transform: translateX(2px) !important;
}
[data-testid="stSidebar"] .stPageLink a[aria-current="page"] {
  color: #FFFFFF !important;
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.22) 0%, rgba(99, 102, 241, 0.06) 100%) !important;
  border-left: 3px solid var(--primary) !important;
  font-weight: 600 !important;
  box-shadow: inset 0 0 12px rgba(99, 102, 241, 0.15) !important;
}

/* ---- Inputs ---- */
input, textarea, [data-baseweb="input"] input {
  background-color: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--ink) !important;
  border-radius: var(--radius-sm) !important;
  font-family: 'Atkinson Hyperlegible', sans-serif !important;
  transition: all 140ms var(--ease-out) !important;
}
input:focus, textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
  background-color: var(--surface-2) !important;
}

/* ---- Buttons ---- */
button, .stButton > button {
  font-family: 'Atkinson Hyperlegible', sans-serif !important;
  border-radius: var(--radius-sm) !important;
  transition: all 140ms var(--ease-out) !important;
  font-weight: 600 !important;
  height: 40px !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
  color: #FFFFFF !important;
  border: none !important;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.35) !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
  box-shadow: 0 4px 18px rgba(99, 102, 241, 0.5) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
  background: var(--surface-2) !important;
  color: var(--ink) !important;
  border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover {
  color: #FFFFFF !important;
  border-color: var(--border-bright) !important;
  background: var(--surface-3) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
  transform: translateY(-1px) !important;
}

/* ---- Select boxes ---- */
[data-baseweb="select"] > div {
  background-color: var(--surface) !important;
  border-color: var(--border) !important;
  border-radius: var(--radius-sm) !important;
}

/* ---- Metric widgets ---- */
[data-testid="stMetricValue"] {
  font-size: 28px !important;
  font-weight: 700 !important;
  color: #FFFFFF !important;
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
  box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.25) !important;
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
  border-radius: var(--radius-lg) !important;
  padding: 20px !important;
  box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.25) !important;
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
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 22, 38, 0.95) 100%);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
  position: relative;
  overflow: hidden;
  transition: all 180ms var(--ease-out);
  box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.35);
}
.stat-card:hover {
  border-color: var(--border-bright);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.45);
}
.stat-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, #6366F1 0%, #06B6D4 100%);
  opacity: 0.8;
}
.stat-card:nth-child(2)::after {
  background: linear-gradient(90deg, #06B6D4 0%, #10B981 100%);
}
.stat-card:nth-child(3)::after {
  background: linear-gradient(90deg, #10B981 0%, #F59E0B 100%);
}
.stat-card:nth-child(4)::after {
  background: linear-gradient(90deg, #F59E0B 0%, #EC4899 100%);
}
.stat-card .stat-num {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 34px;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.1;
  margin-bottom: 6px;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}
.stat-card .stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.08em;
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
  padding: 3px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-family: 'IBM Plex Mono', monospace;
}
.badge-green {
  background: rgba(16, 185, 129, 0.14);
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.35);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
}
.badge-red {
  background: rgba(244, 63, 94, 0.14);
  color: #FB7185;
  border: 1px solid rgba(244, 63, 94, 0.35);
  box-shadow: 0 0 10px rgba(244, 63, 94, 0.15);
}
.badge-violet {
  background: rgba(139, 92, 246, 0.14);
  color: #C084FC;
  border: 1px solid rgba(139, 92, 246, 0.35);
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.15);
}
.badge-amber {
  background: rgba(245, 158, 11, 0.14);
  color: #FBBF24;
  border: 1px solid rgba(245, 158, 11, 0.35);
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.15);
}
.badge-blue {
  background: rgba(56, 189, 248, 0.14);
  color: #38BDF8;
  border: 1px solid rgba(56, 189, 248, 0.35);
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.15);
}
.badge-cyan {
  background: rgba(6, 182, 212, 0.14);
  color: #22D3EE;
  border: 1px solid rgba(6, 182, 212, 0.35);
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.15);
}

/* ---- Panel / card ---- */
.panel {
  background: linear-gradient(180deg, rgba(16, 23, 38, 0.85) 0%, rgba(13, 19, 32, 0.9) 100%);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px;
  box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.3);
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
  padding: 11px 14px;
  text-align: left;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-dim);
  border-bottom: 1px solid var(--border);
}
.data-table td {
  padding: 11px 14px;
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
  background: linear-gradient(180deg, rgba(18, 25, 42, 0.8) 0%, rgba(14, 20, 34, 0.85) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 10px;
  transition: all 140ms var(--ease-out);
}
.result-row:hover {
  border-color: rgba(99, 102, 241, 0.4);
  background: linear-gradient(180deg, rgba(22, 31, 52, 0.9) 0%, rgba(16, 23, 39, 0.95) 100%);
  transform: translateX(2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
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
  color: #C084FC;
  background: var(--violet-dim);
  border: 1px solid rgba(139, 92, 246, 0.35);
  border-radius: 4px;
  padding: 2px 8px;
}
.result-id {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: var(--ink-soft);
}
.result-score {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  color: #FBBF24;
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
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%);
  border: 1px solid rgba(99, 102, 241, 0.45);
  font-size: 13px;
  font-weight: 700;
  color: #A5B4FC;
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.2);
  flex-shrink: 0;
}
.step-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: -0.01em;
}
.step-sub {
  font-size: 13px;
  color: var(--ink-soft);
  margin-left: auto;
}

/* ---- Decision banner ---- */
.decision-banner {
  border-radius: var(--radius-lg);
  padding: 18px 24px;
  margin-bottom: 22px;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
}
.decision-banner.accepted {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.06) 100%);
  border: 1px solid rgba(16, 185, 129, 0.35);
}
.decision-banner.rejected {
  background: linear-gradient(135deg, rgba(244, 63, 94, 0.12) 0%, rgba(225, 29, 72, 0.06) 100%);
  border: 1px solid rgba(244, 63, 94, 0.35);
}
.decision-banner.neutral {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.06) 100%);
  border: 1px solid rgba(99, 102, 241, 0.35);
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
  background: linear-gradient(135deg, rgba(18, 25, 42, 0.9) 0%, rgba(13, 19, 32, 0.95) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: var(--radius-lg);
  padding: 32px 36px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.4);
}
.hero-block::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 380px; height: 380px;
  background: radial-gradient(circle at 90% 10%, rgba(99, 102, 241, 0.18) 0%, rgba(6, 182, 212, 0.08) 45%, transparent 70%);
  pointer-events: none;
}
.hero-tagline {
  font-size: 32px;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.25;
  max-width: 56ch;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}
.hero-sub {
  font-size: 15px;
  color: var(--ink-soft);
  max-width: 64ch;
  line-height: 1.65;
}

/* ---- Signal row ---- */
.signal-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 0;
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
  box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.25) !important;
}

/* Page title styling */
h1[data-testid="stHeading"], [data-testid="stMarkdownContainer"] h1 {
  font-size: 28px !important;
  font-weight: 700 !important;
  color: #FFFFFF !important;
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

