import streamlit as st
from ui.adapter import EngineAdapter
from ui.models import EngineContractError, VersionModel


@st.dialog("Restore Architecture Version")
def confirm_restore_dialog(adapter: EngineAdapter, target_ver_id: str):
    st.write(f"Restore the memory graph and record assignments to version **{target_ver_id}**?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"Restore {target_ver_id}", type="primary"):
            adapter.restore(target_ver_id)
            st.rerun()
    with c2:
        if st.button("Cancel"):
            st.rerun()


def render():
    st.title("Architecture Version History")
    st.caption("Inspect immutable graph snapshots, compare metrics across versions, and restore previous architectures.")

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()
        versions = adapter.list_versions()

        if not versions:
            st.info("No architecture versions recorded yet.")
            return

        # Step chart: Recall and Precision across versions with gate line
        st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-bottom: 8px;'>Retrieval Metrics Progression</h3>", unsafe_allow_html=True)
        chart_data = {
            "Version": [v.id for v in versions],
            "Recall@K": [v.metrics.recall_at_k for v in versions],
            "Precision@K": [v.metrics.precision_at_k for v in versions]
        }
        st.line_chart(chart_data, x="Version", y=["Recall@K", "Precision@K"])
        st.caption(f"Horizontal acceptance gate line: Min Acceptable Recall = {config.min_recall:.2f}")

        st.markdown("<hr>", unsafe_allow_html=True)

        # Side-by-side A vs B Compare
        st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-bottom: 8px;'>Compare Two Versions</h3>", unsafe_allow_html=True)
        ver_ids = [v.id for v in versions]
        c_a, c_b = st.columns(2)
        with c_a:
            v_a_id = st.selectbox("Version A (Baseline)", ver_ids, index=0)
        with c_b:
            v_b_id = st.selectbox("Version B (Comparison)", ver_ids, index=len(ver_ids)-1)

        v_a = next(v for v in versions if v.id == v_a_id)
        v_b = next(v for v in versions if v.id == v_b_id)

        d_recall = v_b.metrics.recall_at_k - v_a.metrics.recall_at_k
        d_prec = v_b.metrics.precision_at_k - v_a.metrics.precision_at_k
        d_lat = v_b.metrics.mean_latency_ms - v_a.metrics.mean_latency_ms

        st.markdown(f"""
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 16px;">
            <thead>
                <tr style="border-bottom: 1px solid var(--rule); text-align: left; color: var(--ink-soft);">
                    <th style="padding: 6px 4px;">Metric</th>
                    <th style="padding: 6px 4px;">{v_a_id}</th>
                    <th style="padding: 6px 4px;">{v_b_id}</th>
                    <th style="padding: 6px 4px;">Delta</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                    <td style="padding: 6px 4px; font-weight: 600;">Recall@K</td>
                    <td class="mono-val" style="padding: 6px 4px;">{v_a.metrics.recall_at_k:.4f}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{v_b.metrics.recall_at_k:.4f}</td>
                    <td class="mono-val" style="padding: 6px 4px; font-weight: 600; color: {'var(--accepted)' if d_recall>=0 else 'var(--rejected)'};">{d_recall:+.4f}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                    <td style="padding: 6px 4px; font-weight: 600;">Precision@K</td>
                    <td class="mono-val" style="padding: 6px 4px;">{v_a.metrics.precision_at_k:.4f}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{v_b.metrics.precision_at_k:.4f}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{d_prec:+.4f}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                    <td style="padding: 6px 4px; font-weight: 600;">Mean Latency</td>
                    <td class="mono-val" style="padding: 6px 4px;">{v_a.metrics.mean_latency_ms:.2f} ms</td>
                    <td class="mono-val" style="padding: 6px 4px;">{v_b.metrics.mean_latency_ms:.2f} ms</td>
                    <td class="mono-val" style="padding: 6px 4px;">{d_lat:+.2f} ms</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Version Timeline (Newest first)
        st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-bottom: 8px;'>Version History Timeline</h3>", unsafe_allow_html=True)
        reversed_versions = list(reversed(versions))

        for v in reversed_versions:
            status_tag = "status-accepted" if v.status == "ACCEPTED" else ("status-baseline" if v.status == "NEUTRAL" else "status-rejected")
            st.markdown(f"""
            <div style="padding: 14px; background: #FFFFFF; border: 1px solid var(--rule); border-radius: 4px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="mono-val" style="font-weight: 700; font-size: 15px; color: var(--ink);">{v.id}</span>
                        <span style="font-size: 14px; font-weight: 600;">{v.operation}</span>
                    </div>
                    <span class="status-tag {status_tag}">{v.status}</span>
                </div>
                <div style="font-size: 13px; color: var(--ink-soft); margin-top: 6px;">{v.reason}</div>
                <div style="display: flex; gap: 20px; font-size: 12px; margin-top: 10px; color: var(--ink-soft);">
                    <div>Recall@K: <strong class="mono-val" style="color: var(--ink);">{v.metrics.recall_at_k:.4f}</strong></div>
                    <div>Precision@K: <strong class="mono-val" style="color: var(--ink);">{v.metrics.precision_at_k:.4f}</strong></div>
                    <div>Latency: <strong class="mono-val" style="color: var(--ink);">{v.metrics.mean_latency_ms:.2f} ms</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Restore {v.id}", key=f"btn_restore_{v.id}", type="secondary"):
                confirm_restore_dialog(adapter, v.id)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")

render()
