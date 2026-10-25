import streamlit as st
from ui.adapter import EngineAdapter
from ui.graph_payload import build_graph_payload
from ui.models import EngineContractError, ProposalModel


def render():
    st.markdown("# Adapt")
    st.markdown('<div style="font-size:14px;color:var(--ink-soft);margin-bottom:8px;">Detect structural weaknesses, propose reconfigurations, validate on frozen queries, and guard with automatic rollback.</div>', unsafe_allow_html=True)

    try:
        adapter = EngineAdapter()
        config = adapter.get_config()

        #                                                                       
        # STEP 1  -  DETECT
        #                                                                       
        st.markdown("""
        <div class="step-header">
          <div class="step-num">1</div>
          <div class="step-title">Detect</div>
          <div class="step-sub">Structural weakness telemetry</div>
        </div>
        """, unsafe_allow_html=True)

        signals = adapter.get_signals()

        overloaded_cnt = len(signals.overloaded)
        redundant_cnt = len(signals.redundant_pairs)
        coaccess_cnt = len(signals.coaccess)

        def signal_row(label, measured, threshold_label, condition, triggered):
            dot = "#F59E0B" if triggered else "#10B981"
            badge = f'<span class="badge badge-{"amber" if triggered else "green"}">' \
                    f'{"TRIGGERED" if triggered else "NORMAL"}</span>'
            return f"""
            <div class="signal-row">
              <span class="signal-indicator" style="background:{dot};box-shadow:0 0 8px {dot};"></span>
              <div style="flex:1;">
                <div style="font-size:14px;font-weight:700;color:#FFFFFF;">{label}</div>
                <div style="font-size:12px;color:var(--ink-soft);margin-top:2px;">{condition}</div>
              </div>
              <div style="text-align:right;">
                <div class="mono" style="font-size:13px;color:#CBD5E1;font-weight:600;">{measured}</div>
                <div class="mono" style="font-size:11px;color:var(--ink-dim);">{threshold_label}</div>
              </div>
              <div style="width:90px;text-align:right;">{badge}</div>
            </div>
            """

        st.markdown(f"""
        <div class="panel">
          {signal_row("Module Overload", f"{overloaded_cnt} overloaded",
                      f"min_size={signals.thresholds.get('split_min_module_size',10)}, "
                      f"min_sil={signals.thresholds.get('split_min_silhouette',0.20)}",
                      "Records > threshold & internal silhouette > threshold", overloaded_cnt > 0)}
          {signal_row("Module Redundancy", f"{redundant_cnt} redundant pairs",
                      f"cosine_thresh={signals.thresholds.get('merge_cosine_threshold',0.88)}",
                      "Centroid cosine similarity above merge threshold", redundant_cnt > 0)}
          {signal_row("Co-Access Patterns", f"{coaccess_cnt} co-accessed pairs",
                      f"min_co_access={signals.thresholds.get('shortcut_min_co_access',2)}",
                      "Query co-access count >= threshold without direct edge", coaccess_cnt > 0)}
        </div>
        """, unsafe_allow_html=True)

        #                                                                       
        # STEP 2  -  PROPOSE
        #                                                                       
        st.markdown("""
        <div class="step-header">
          <div class="step-num">2</div>
          <div class="step-title">Propose</div>
          <div class="step-sub">Candidate reconfiguration operations</div>
        </div>
        """, unsafe_allow_html=True)

        proposals = adapter.propose()

        if not proposals:
            st.markdown("""
            <div class="panel" style="text-align:center;padding:36px;">
              <div style="font-size:14px;color:var(--ink-soft);">No structural weaknesses triggered by current telemetry signals. Graph architecture is in equilibrium.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            op_colors = {"split": "#F59E0B", "merge": "#06B6D4", "shortcut": "#10B981"}
            op_badges = {"split": "amber", "merge": "cyan", "shortcut": "green"}

            prop_items_html = ""
            for i, p in enumerate(proposals):
                oc = op_colors.get(p.op.lower(), "#6366F1")
                ob = op_badges.get(p.op.lower(), "violet")
                prop_items_html += f"""
                <div style="padding:16px;border:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.02);
                             border-radius:var(--radius);margin-bottom:10px;transition:all 140ms ease-out;">
                  <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                    <span class="badge badge-{ob}">{p.op.upper()}</span>
                    <span class="mono" style="font-size:13px;color:#F8FAFC;font-weight:600;">{', '.join(p.targets)}</span>
                    <span style="margin-left:auto;font-family:'IBM Plex Mono',monospace;font-size:12px;color:#94A3B8;">
                      signal: <strong style="color:#FFFFFF;">{p.value:.3f}</strong> (thresh: {p.threshold:.3f})
                    </span>
                  </div>
                  <div style="font-size:13px;color:var(--ink-soft);">{p.reason}</div>
                </div>
                """

            st.markdown(f'<div class="panel" style="padding:16px;">{prop_items_html}</div>', unsafe_allow_html=True)

            prop_options = [
                f"{p.op.upper()}  -  {', '.join(p.targets)} (signal: {p.value:.3f})"
                for p in proposals
            ]
            sel_idx = st.selectbox("Select proposal to execute", range(len(proposals)),
                                    format_func=lambda i: prop_options[i])
            chosen_proposal = proposals[sel_idx]

            #                                                                   
            # STEP 3  -  EVALUATE & DECIDE
            #                                                                   
            st.markdown("""
            <div class="step-header">
              <div class="step-num">3</div>
              <div class="step-title">Evaluate &amp; Decide</div>
              <div class="step-sub">Run frozen 16-query benchmark before and after</div>
            </div>
            """, unsafe_allow_html=True)

            run_btn_col, _ = st.columns([1.5, 2.5])
            with run_btn_col:
                run_btn = st.button("Run adaptation cycle", type="primary", use_container_width=True)

            eval_ph = st.empty()
            if run_btn:
                eval_ph.markdown(
                    '<div class="skeleton" style="height:120px;margin:16px 0;"></div>',
                    unsafe_allow_html=True
                )
                cycle_res = adapter.run_adaptation_cycle(chosen_proposal)
                st.session_state["last_cycle_result"] = cycle_res
                eval_ph.empty()
                st.rerun()

        #                                                                       
        # STEP 4  -  DECISION LEDGER
        #                                                                       
        if "last_cycle_result" in st.session_state:
            res = st.session_state["last_cycle_result"]

            st.markdown("""
            <div class="step-header">
              <div class="step-num">4</div>
              <div class="step-title">Decision Ledger</div>
              <div class="step-sub">Rollback verification &amp; state audit</div>
            </div>
            """, unsafe_allow_html=True)

            dec = res.decision.lower()
            banner_cls = "accepted" if dec == "accepted" else ("rejected" if dec == "rejected" else "neutral")
            icon = "✓" if dec == "accepted" else ("✕" if dec == "rejected" else "•")
            dec_color = "#34D399" if dec == "accepted" else ("#FB7185" if dec == "rejected" else "#A5B4FC")

            st.markdown(f"""
            <div class="decision-banner {banner_cls}">
              <div style="display:flex;align-items:center;gap:14px;">
                <span style="font-size:24px;font-weight:800;color:{dec_color};">{icon}</span>
                <div>
                  <div style="font-size:17px;font-weight:700;color:#FFFFFF;">
                    {res.proposal.get('op','').upper()}  —  {res.decision.upper()}
                  </div>
                  <div style="font-size:13px;color:var(--ink-soft);margin-top:2px;">{res.reason}</div>
                </div>
                {('<div style="margin-left:auto;"><span class="badge badge-red" style="font-size:11px;padding:4px 10px;">ROLLED BACK</span></div>' if res.rolled_back else '<div style="margin-left:auto;"><span class="badge badge-green" style="font-size:11px;padding:4px 10px;">COMMITTED</span></div>')}
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics diff
            m1, m2, m3 = st.columns(3)
            delta_r = res.after.recall_at_k - res.before.recall_at_k
            delta_p = res.after.precision_at_k - res.before.precision_at_k
            delta_l = res.after.mean_latency_ms - res.before.mean_latency_ms

            def metric_card(label, before, after, delta, unit="", good_if_positive=True):
                is_good = (delta > 0) if good_if_positive else (delta < 0)
                dc = "#34D399" if is_good else ("#FB7185" if delta != 0 else "#94A3B8")
                arrow = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
                return f"""
                <div class="stat-card">
                  <div class="stat-label">{label}</div>
                  <div style="display:flex;align-items:baseline;gap:8px;margin-top:8px;">
                    <div class="stat-num" style="font-size:26px;">{after:.4f}{unit}</div>
                    <div style="font-size:14px;font-weight:700;color:{dc};">{arrow} {abs(delta):.4f}</div>
                  </div>
                  <div class="stat-sub">Before: {before:.4f}{unit} | Gate: {config.min_recall:.2f}</div>
                </div>
                """

            with m1:
                st.markdown(metric_card("Recall@K", res.before.recall_at_k, res.after.recall_at_k, delta_r), unsafe_allow_html=True)
            with m2:
                st.markdown(metric_card("Precision@K", res.before.precision_at_k, res.after.precision_at_k, delta_p), unsafe_allow_html=True)
            with m3:
                st.markdown(metric_card("Latency", res.before.mean_latency_ms, res.after.mean_latency_ms, delta_l, "ms", False), unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        #    Baseline comparison table                                          
        st.markdown('<div class="panel-title" style="margin-bottom:12px;">Baseline Comparison</div>', unsafe_allow_html=True)
        baseline_data = adapter.baseline_evaluate()
        if "flat_baseline" in baseline_data and "current_morphe" in baseline_data:
            fb = baseline_data["flat_baseline"]
            cm = baseline_data["current_morphe"]
            d = baseline_data.get("delta", {})

            def delta_cell(val):
                col = "var(--green)" if val >= 0 else "var(--red)"
                return f'<td class="mono strong" style="color:{col};">{val:+.4f}</td>'

            st.markdown(f"""
            <div class="panel" style="padding:0;overflow:hidden;">
              <table class="data-table">
                <thead><tr>
                  <th>Metric</th>
                  <th>Flat vector baseline</th>
                  <th>MORPHE (current)</th>
                  <th>Delta</th>
                </tr></thead>
                <tbody>
                  <tr>
                    <td class="strong">Mean Recall@K</td>
                    <td class="mono">{fb.get('mean_recall',0):.4f}</td>
                    <td class="mono strong">{cm.get('mean_recall',0):.4f}</td>
                    {delta_cell(d.get('recall_delta',0))}
                  </tr>
                  <tr>
                    <td class="strong">Mean Precision@K</td>
                    <td class="mono">{fb.get('mean_precision',0):.4f}</td>
                    <td class="mono strong">{cm.get('mean_precision',0):.4f}</td>
                    {delta_cell(d.get('precision_delta',0))}
                  </tr>
                  <tr>
                    <td class="strong">Mean Latency</td>
                    <td class="mono">{fb.get('mean_latency_ms',0):.2f} ms</td>
                    <td class="mono strong">{cm.get('mean_latency_ms',0):.2f} ms</td>
                    <td class="mono">{d.get('latency_delta_ms',0):+.2f} ms</td>
                  </tr>
                </tbody>
              </table>
            </div>
            """, unsafe_allow_html=True)

        #    Per-query evidence table                                            
        st.markdown("<hr>", unsafe_allow_html=True)
        with st.expander("16-Query Frozen Benchmark Evidence"):
            eval_res = adapter.evaluate()
            rows = ""
            for pq in eval_res.per_query:
                rc = "var(--green)" if pq.recall >= 0.75 else ("var(--amber)" if pq.recall >= 0.5 else "var(--red)")
                rows += f"""
                <tr>
                  <td style="max-width:240px;">{pq.query}</td>
                  <td class="mono" style="font-size:11px;">{', '.join(pq.expected)}</td>
                  <td class="mono" style="font-size:11px;">{', '.join(pq.retrieved)}</td>
                  <td class="mono strong" style="color:{rc};">{pq.recall:.2f}</td>
                  <td class="mono">{pq.precision:.2f}</td>
                  <td class="mono">{pq.latency_ms:.1f}ms</td>
                </tr>"""

            st.markdown(f"""
            <div class="panel" style="padding:0;overflow:hidden;">
              <table class="data-table">
                <thead><tr>
                  <th>Query</th><th>Expected</th><th>Retrieved</th>
                  <th>Recall</th><th>Precision</th><th>Latency</th>
                </tr></thead>
                <tbody>{rows}</tbody>
              </table>
            </div>
            """, unsafe_allow_html=True)

    except EngineContractError as err:
        st.error(f"Engine not connected: {err.missing_fields}")
    except Exception as e:
        st.error(f"Error: {e}")


render()
