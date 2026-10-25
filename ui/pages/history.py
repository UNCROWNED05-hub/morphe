import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError


@st.dialog("Restore Architecture Version")
def confirm_restore_dialog(adapter, target_ver_id):
    st.markdown(f'<div style="font-size:15px;color:var(--ink);margin-bottom:16px;">Restore graph topology and module assignments to <span class="mono" style="color:var(--violet);">{target_ver_id}</span>? Current state will be overwritten.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"Restore {target_ver_id}", type="primary", use_container_width=True):
            adapter.restore(target_ver_id)
            if "last_cycle_result" in st.session_state:
                del st.session_state["last_cycle_result"]
            st.rerun()
    with c2:
        if st.button("Cancel", type="secondary", use_container_width=True):
            st.rerun()


def render():
    st.markdown("# History")
    st.markdown('<div style="font-size:14px;color:var(--ink-soft);margin-bottom:24px;">Immutable version ledger, metric progression, A/B comparison, and architecture restore.</div>', unsafe_allow_html=True)

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()
        versions = adapter.list_versions()

        if not versions:
            st.markdown("""
            <div class="panel" style="text-align:center;padding:48px;">
              <div style="font-size:14px;color:var(--ink-soft);">No versions recorded yet. Run an adaptation cycle to begin.</div>
            </div>
            """, unsafe_allow_html=True)
            return

        # ── Metric progression chart ───────────────────────────────────────────
        st.markdown('<div class="panel-title" style="margin-bottom:12px;">Retrieval metric progression</div>', unsafe_allow_html=True)
        chart_data = {
            "Version":     [v.id for v in versions],
            "Recall@K":    [v.metrics.recall_at_k for v in versions],
            "Precision@K": [v.metrics.precision_at_k for v in versions],
        }
        st.line_chart(chart_data, x="Version", y=["Recall@K", "Precision@K"], height=240)
        st.markdown(f'<div style="font-size:12px;color:var(--ink-dim);margin-top:-8px;">Min recall gate: {config.min_recall:.2f}</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── A vs B compare ────────────────────────────────────────────────────
        st.markdown('<div class="panel-title" style="margin-bottom:12px;">Compare two versions</div>', unsafe_allow_html=True)
        ver_ids = [v.id for v in versions]
        ca, cb = st.columns(2)
        with ca:
            v_a_id = st.selectbox("Version A", ver_ids, index=0)
        with cb:
            v_b_id = st.selectbox("Version B", ver_ids, index=len(ver_ids) - 1)

        v_a = next(v for v in versions if v.id == v_a_id)
        v_b = next(v for v in versions if v.id == v_b_id)

        def compare_cell(before, after, unit=""):
            delta = after - before
            col = "var(--green)" if delta >= 0 else "var(--red)"
            arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
            return f'<td class="mono">{after:.4f}{unit}</td><td class="mono" style="font-weight:700;color:{col};">{arrow} {abs(delta):.4f}</td>'

        st.markdown(f"""
        <div class="panel" style="padding:0;overflow:hidden;">
          <table class="data-table">
            <thead><tr>
              <th>Metric</th>
              <th>{v_a_id} (A)</th>
              <th>{v_b_id} (B)</th>
              <th>Delta (B - A)</th>
            </tr></thead>
            <tbody>
              <tr>
                <td class="strong">Recall@K</td>
                <td class="mono">{v_a.metrics.recall_at_k:.4f}</td>
                {compare_cell(v_a.metrics.recall_at_k, v_b.metrics.recall_at_k)}
              </tr>
              <tr>
                <td class="strong">Precision@K</td>
                <td class="mono">{v_a.metrics.precision_at_k:.4f}</td>
                {compare_cell(v_a.metrics.precision_at_k, v_b.metrics.precision_at_k)}
              </tr>
              <tr>
                <td class="strong">Latency</td>
                <td class="mono">{v_a.metrics.mean_latency_ms:.2f}ms</td>
                {compare_cell(v_a.metrics.mean_latency_ms, v_b.metrics.mean_latency_ms, "ms")}
              </tr>
            </tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Version timeline ──────────────────────────────────────────────────
        st.markdown('<div class="panel-title" style="margin-bottom:8px;">Version Architecture Ledger</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel" style="padding:8px 22px;">', unsafe_allow_html=True)

        for v in reversed(versions):
            status = v.status
            dot = "#2FA873" if status == "ACCEPTED" else ("#D9534F" if status == "REJECTED" else "#5E6AD2")
            badge_cls = "badge-green" if status == "ACCEPTED" else ("badge-red" if status == "REJECTED" else "badge-violet")

            st.markdown(f"""
            <div class="ver-item">
              <div class="ver-dot" style="background:{dot};margin-top:6px;"></div>
              <div class="ver-body">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                  <span class="ver-id">{v.id}</span>
                  <span style="font-size:13px;color:var(--ink-soft);">{v.operation}</span>
                  <span class="badge {badge_cls}" style="margin-left:auto;">{status}</span>
                </div>
                <div class="ver-op">{v.reason}</div>
                <div class="ver-metrics">
                  <div class="ver-metric-item">Recall@K <strong>{v.metrics.recall_at_k:.4f}</strong></div>
                  <div class="ver-metric-item">Precision@K <strong>{v.metrics.precision_at_k:.4f}</strong></div>
                  <div class="ver-metric-item">Latency <strong>{v.metrics.mean_latency_ms:.1f}ms</strong></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Restore {v.id}", key=f"restore_{v.id}", type="secondary"):
                confirm_restore_dialog(adapter, v.id)

        st.markdown('</div>', unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error: {e}")


render()
