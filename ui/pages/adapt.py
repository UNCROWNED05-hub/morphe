import streamlit as st
from ui.adapter import EngineAdapter
from ui.graph_payload import build_graph_payload
from ui.models import EngineContractError, ProposalModel


def render():
    st.title("Adaptation Pipeline")
    st.caption("Inspect structural weaknesses, propose heuristic reconfigurations, validate against frozen queries, and guard with automatic rollback.")

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()

        # Step 1: Detect Signals
        st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-top: 16px; margin-bottom: 8px;'>1. Detect: Structural Weakness Telemetry</h3>", unsafe_allow_html=True)
        signals = adapter.get_signals()

        sig_table = """
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 16px;">
            <thead>
                <tr style="border-bottom: 1px solid var(--rule); text-align: left; color: var(--ink-soft);">
                    <th style="padding: 6px 4px;">Signal</th>
                    <th style="padding: 6px 4px;">Measured Value</th>
                    <th style="padding: 6px 4px;">Threshold</th>
                    <th style="padding: 6px 4px;">Trigger Condition</th>
                    <th style="padding: 6px 4px;">Status</th>
                </tr>
            </thead>
            <tbody>
        """
        # Overloaded signal
        overloaded_cnt = len(signals.overloaded)
        sig_table += f"""
            <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                <td style="padding: 6px 4px; font-weight: 600;">Module Overload</td>
                <td class="mono-val" style="padding: 6px 4px;">{overloaded_cnt} modules overloaded</td>
                <td class="mono-val" style="padding: 6px 4px;">min_size={signals.thresholds.get('split_min_module_size', 10)}, min_sil={signals.thresholds.get('split_min_silhouette', 0.20)}</td>
                <td style="padding: 6px 4px;">Records &gt; 10 &amp; silhouette &gt; 0.20</td>
                <td style="padding: 6px 4px;"><span class="status-tag {'status-change' if overloaded_cnt > 0 else 'status-accepted'}">{'TRIGGERED' if overloaded_cnt > 0 else 'NORMAL'}</span></td>
            </tr>
        """
        # Redundancy signal
        redundant_cnt = len(signals.redundant_pairs)
        sig_table += f"""
            <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                <td style="padding: 6px 4px; font-weight: 600;">Module Redundancy</td>
                <td class="mono-val" style="padding: 6px 4px;">{redundant_cnt} redundant pairs</td>
                <td class="mono-val" style="padding: 6px 4px;">cosine_threshold={signals.thresholds.get('merge_cosine_threshold', 0.88)}</td>
                <td style="padding: 6px 4px;">Centroid Cosine Sim &gt; 0.88</td>
                <td style="padding: 6px 4px;"><span class="status-tag {'status-change' if redundant_cnt > 0 else 'status-accepted'}">{'TRIGGERED' if redundant_cnt > 0 else 'NORMAL'}</span></td>
            </tr>
        """
        # Co-access signal
        coaccess_cnt = len(signals.coaccess)
        sig_table += f"""
            <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                <td style="padding: 6px 4px; font-weight: 600;">Repeated Co-Access</td>
                <td class="mono-val" style="padding: 6px 4px;">{coaccess_cnt} co-accessed pairs</td>
                <td class="mono-val" style="padding: 6px 4px;">min_co_access={signals.thresholds.get('shortcut_min_co_access', 2)}</td>
                <td style="padding: 6px 4px;">Query co-access hits &gt;= 2 &amp; no direct edge</td>
                <td style="padding: 6px 4px;"><span class="status-tag {'status-change' if coaccess_cnt > 0 else 'status-baseline'}">{'LOGGED' if coaccess_cnt > 0 else 'IDLE'}</span></td>
            </tr>
        """
        sig_table += "</tbody></table>"
        st.markdown(sig_table, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Step 2: Propose Operations
        st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-bottom: 8px;'>2. Propose: Candidate Reconfiguration Operations</h3>", unsafe_allow_html=True)
        proposals = adapter.propose()

        if proposals:
            prop_options = [f"{p.op.upper()} on {', '.join(p.targets)} (Measured: {p.value:.3f} vs Thresh: {p.threshold:.3f})" for p in proposals]
            sel_idx = st.selectbox("Select Candidate Proposal", range(len(proposals)), format_func=lambda i: prop_options[i])
            chosen_proposal = proposals[sel_idx]

            st.markdown(f"""
            <div style="padding: 10px 14px; background: #FFFFFF; border: 1px solid var(--rule); border-radius: 4px; font-size: 13px; margin: 8px 0;">
                <div><strong>Heuristic Reason:</strong> {chosen_proposal.reason}</div>
            </div>
            """, unsafe_allow_html=True)

            # Step 3: Evaluate & Decide
            st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-top: 16px; margin-bottom: 8px;'>3. Evaluate &amp; Decide</h3>", unsafe_allow_html=True)
            col_eval1, col_eval2 = st.columns([1, 2])
            with col_eval1:
                run_btn = st.button("Run adaptation cycle", type="primary", use_container_width=True)

            eval_placeholder = st.empty()

            if run_btn:
                eval_placeholder.markdown("""
                <div class="skeleton" style="height: 90px; width: 100%; margin: 12px 0;"></div>
                """, unsafe_allow_html=True)

                cycle_res = adapter.run_adaptation_cycle(chosen_proposal)
                st.session_state["last_cycle_result"] = cycle_res
                eval_placeholder.empty()

        else:
            st.info("No candidate reconfiguration operations currently triggered by telemetry rules.")

        # Show Last Cycle Result
        if "last_cycle_result" in st.session_state:
            res = st.session_state["last_cycle_result"]
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-bottom: 8px;'>4. Decision Ledger &amp; Rollback Verification</h3>", unsafe_allow_html=True)

            tag_class = "status-accepted" if res.decision == "accepted" else ("status-baseline" if res.decision == "neutral" else "status-rejected")
            st.markdown(f"""
            <div style="padding: 12px; background: #FFFFFF; border: 1px solid var(--rule); border-radius: 4px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; font-size: 14px;">Operation: {res.proposal.get('op', '').upper()}</span>
                    <span class="status-tag {tag_class}">{res.decision.upper()}</span>
                </div>
                <div style="font-size: 13px; color: var(--ink-soft); margin-top: 6px;">{res.reason}</div>
                {f'<div class="status-tag status-rejected" style="margin-top: 8px;">Rolled back to previous version: Graph restored.</div>' if res.rolled_back else ''}
            </div>
            """, unsafe_allow_html=True)

            # Metrics ledger before vs after with threshold tick
            m_col1, m_col2, m_col3 = st.columns(3)
            delta_recall = res.after.recall_at_k - res.before.recall_at_k
            word = "up" if delta_recall > 0 else ("down" if delta_recall < 0 else "neutral")
            with m_col1:
                st.metric("Recall@K", f"{res.after.recall_at_k:.4f}", f"{word} {abs(delta_recall):.4f}")
                st.caption(f"Before: {res.before.recall_at_k:.4f} | Gate Tick: {config.min_recall:.2f}")
            with m_col2:
                delta_prec = res.after.precision_at_k - res.before.precision_at_k
                st.metric("Precision@K", f"{res.after.precision_at_k:.4f}", f"{'+' if delta_prec>=0 else ''}{delta_prec:.4f}")
                st.caption(f"Before: {res.before.precision_at_k:.4f}")
            with m_col3:
                st.metric("Latency", f"{res.after.mean_latency_ms:.2f} ms")
                st.caption(f"Before: {res.before.mean_latency_ms:.2f} ms")

        st.markdown("<hr>", unsafe_allow_html=True)

        # Baseline Comparison Table
        st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-bottom: 8px;'>Baseline Comparison (Fixed vs Adaptive)</h3>", unsafe_allow_html=True)
        baseline_data = adapter.baseline_evaluate()
        if "flat_baseline" in baseline_data and "current_morphe" in baseline_data:
            fb = baseline_data["flat_baseline"]
            cm = baseline_data["current_morphe"]
            d = baseline_data.get("delta", {})

            st.markdown(f"""
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="border-bottom: 1px solid var(--rule); text-align: left; color: var(--ink-soft);">
                        <th style="padding: 6px 4px;">Metric</th>
                        <th style="padding: 6px 4px;">Flat Vector Baseline</th>
                        <th style="padding: 6px 4px;">MORPHE Graph Memory</th>
                        <th style="padding: 6px 4px;">Delta</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                        <td style="padding: 6px 4px; font-weight: 600;">Mean Recall@K</td>
                        <td class="mono-val" style="padding: 6px 4px;">{fb.get('mean_recall', 0):.4f}</td>
                        <td class="mono-val" style="padding: 6px 4px; font-weight: 600;">{cm.get('mean_recall', 0):.4f}</td>
                        <td class="mono-val" style="padding: 6px 4px; color: {'var(--accepted)' if d.get('recall_delta', 0)>=0 else 'var(--rejected)'};">{d.get('recall_delta', 0):+.4f}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                        <td style="padding: 6px 4px; font-weight: 600;">Mean Precision@K</td>
                        <td class="mono-val" style="padding: 6px 4px;">{fb.get('mean_precision', 0):.4f}</td>
                        <td class="mono-val" style="padding: 6px 4px; font-weight: 600;">{cm.get('mean_precision', 0):.4f}</td>
                        <td class="mono-val" style="padding: 6px 4px;">{d.get('precision_delta', 0):+.4f}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(211,217,210,0.5);">
                        <td style="padding: 6px 4px; font-weight: 600;">Mean Query Latency</td>
                        <td class="mono-val" style="padding: 6px 4px;">{fb.get('mean_latency_ms', 0):.2f} ms</td>
                        <td class="mono-val" style="padding: 6px 4px; font-weight: 600;">{cm.get('mean_latency_ms', 0):.2f} ms</td>
                        <td class="mono-val" style="padding: 6px 4px;">{d.get('latency_delta_ms', 0):+.2f} ms</td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Per-Query Evidence Table
        st.markdown("<h3 style='font-size: 16px; font-weight: 600; margin-bottom: 8px;'>Per-Query Evidence (Frozen Benchmark)</h3>", unsafe_allow_html=True)
        eval_res = adapter.evaluate()
        with st.expander("Expand 16-Query Ground Truth Evaluation Evidence Table"):
            st.markdown("""
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <thead>
                    <tr style="border-bottom: 1px solid var(--rule); text-align: left; color: var(--ink-soft);">
                        <th style="padding: 6px 4px;">Query</th>
                        <th style="padding: 6px 4px;">Expected Records</th>
                        <th style="padding: 6px 4px;">Retrieved Records</th>
                        <th style="padding: 6px 4px;">Recall</th>
                        <th style="padding: 6px 4px;">Precision</th>
                        <th style="padding: 6px 4px;">Latency</th>
                    </tr>
                </thead>
                <tbody>
            """, unsafe_allow_html=True)
            for pq in eval_res.per_query:
                st.markdown(f"""
                <tr style="border-bottom: 1px solid rgba(211,217,210,0.4);">
                    <td style="padding: 6px 4px;">{pq.query}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{', '.join(pq.expected)}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{', '.join(pq.retrieved)}</td>
                    <td class="mono-val" style="padding: 6px 4px; font-weight: 600;">{pq.recall:.2f}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{pq.precision:.2f}</td>
                    <td class="mono-val" style="padding: 6px 4px;">{pq.latency_ms:.2f} ms</td>
                </tr>
                """, unsafe_allow_html=True)
            st.markdown("</tbody></table>", unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error in adaptation pipeline: {str(e)}")

render()
