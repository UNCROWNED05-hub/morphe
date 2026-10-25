import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError


def render():
    try:
        adapter = EngineAdapter()
        config = adapter.get_config()
        graph = adapter.get_graph()
        records = adapter.list_records()
        versions = adapter.list_versions()

        current_ver = versions[-1].id if versions else "V1"
        last_status = versions[-1].status if versions else "BASELINE"
        status_color = "#3DD68C" if last_status in ("ACCEPTED", "BASELINE", "NEUTRAL") else "#F56565"

    except Exception:
        adapter = None
        config = None
        graph = None
        records = []
        versions = []
        current_ver = " - "
        last_status = "OFFLINE"
        status_color = "#F56565"

    # ── Hero block ──────────────────────────────────────────────────────────────
    # ── Hero block ──────────────────────────────────────────────────────────────
    status_badge = f'<span class="badge badge-{"green" if last_status in ("ACCEPTED","BASELINE","NEUTRAL") else "red"}">{last_status}</span>'
    st.markdown(f"""
    <div class="hero-block">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
        <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;
               font-weight:600;color:var(--ink-soft);letter-spacing:0.04em;text-transform:uppercase;
               background:var(--surface-2);padding:2px 8px;border-radius:4px;border:1px solid var(--border);">
          Active Version: {current_ver}
        </span>
        {status_badge}
      </div>
      <div class="hero-tagline">Self-organizing neural memory topology for autonomous agents.</div>
      <div class="hero-sub">
        MORPHE detects structural bottlenecks across knowledge modules, proposes and applies
        targeted graph reconfigurations (split, merge, shortcut), evaluates against frozen benchmark queries, and executes zero-regression rollbacks.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 4-up stat grid ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    stat_cols = [c1, c2, c3, c4]
    stats = [
        (len(records), "Records", "knowledge chunks stored", "#5E6AD2"),
        (len(graph.nodes) if graph else 0, "Modules", "graph cluster nodes", "#3E8A78"),
        (len(graph.edges) if graph else 0, "Pathways", "retrieval edge pathways", "#4A88B5"),
        (len(versions), "Versions", "adaptation cycles logged", "#C98A2C"),
    ]
    for col, (num, label, sub, color) in zip(stat_cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
              <div class="stat-num">{num}</div>
              <div class="stat-label" style="display:flex;align-items:center;gap:6px;">
                <span style="width:6px;height:6px;border-radius:50%;background:{color};display:inline-block;"></span>
                {label}
              </div>
              <div class="stat-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Config + action row ─────────────────────────────────────────────────────
    left, right = st.columns([3, 2])

    with left:
        if config:
            st.markdown(f"""
            <div class="panel">
              <div class="panel-title">Engine Configuration</div>
              <table class="data-table">
                <tr>
                  <td>Embedding Model</td>
                  <td class="strong mono">{config.model}</td>
                </tr>
                <tr>
                  <td>Retrieval K</td>
                  <td class="strong mono">{config.k}</td>
                </tr>
                <tr>
                  <td>Min Recall Gate</td>
                  <td class="strong mono">{config.min_recall:.2f}</td>
                </tr>
                <tr>
                  <td>Target Corpus</td>
                  <td class="strong mono">{config.corpus_label}</td>
                </tr>
              </table>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Engine Controls</div>', unsafe_allow_html=True)
        if adapter:
            if len(records) == 0:
                if st.button("Load sample corpus", type="primary", use_container_width=True):
                    adapter.load_sample()
                    st.rerun()
                st.markdown('<div style="font-size:12px;color:var(--ink-dim);margin-top:8px;">No records yet. Load the benchmark corpus to begin.</div>', unsafe_allow_html=True)
            else:
                if st.button("Run Adaptation Cycle", type="primary", use_container_width=True):
                    proposals = adapter.propose()
                    if proposals:
                        adapter.run_adaptation_cycle(proposals[0])
                        st.rerun()
                    else:
                        st.info("No structural weakness currently triggered.")
                if st.button("Explore Adapt View →", type="secondary", use_container_width=True):
                    st.switch_page("ui/pages/adapt.py")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Version mini-timeline ──────────────────────────────────────────────────
    if versions:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="panel-title" style="margin-bottom:12px;">Architecture Evolution History</div>', unsafe_allow_html=True)
        for v in reversed(versions[-4:]):
            dot = "#2FA873" if v.status == "ACCEPTED" else ("#D9534F" if v.status == "REJECTED" else "#5E6AD2")
            status_badge_class = 'green' if v.status=='ACCEPTED' else ('red' if v.status=='REJECTED' else 'violet')
            st.markdown(f"""
            <div class="ver-item">
              <div class="ver-dot" style="background:{dot};margin-top:6px;"></div>
              <div class="ver-body">
                <div style="display:flex;align-items:center;gap:10px;">
                  <span class="ver-id">{v.id}</span>
                  <span style="font-size:13px;color:var(--ink-soft);">{v.operation}</span>
                  <span class="badge badge-{status_badge_class}" style="margin-left:auto;">{v.status}</span>
                </div>
                <div class="ver-metrics">
                  <div class="ver-metric-item">Recall@K <strong>{v.metrics.recall_at_k:.4f}</strong></div>
                  <div class="ver-metric-item">Precision@K <strong>{v.metrics.precision_at_k:.4f}</strong></div>
                  <div class="ver-metric-item">Latency <strong>{v.metrics.mean_latency_ms:.1f}ms</strong></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


render()
