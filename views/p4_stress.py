import streamlit as st
import plotly.graph_objects as go
from core.model import (
    BASE_STATE,
    STRESS_PERIODS,
    STRATEGY_PRESETS,
    get_excel_stress_series,
    simulate_strategy,
    get_all_strategy_comparison,
)
from core.ui import render_page_header, render_insight_banner


def show():
    render_page_header(
        "위기상황분석",
        "2026.06 재무 상태에 과거 위기의 업계 변화폭을 적용해 3년간 BIS 경로를 봅니다. 전략을 끄면 과거 평상시 출발 경로와, 켜면 전략 적용 경로와 비교합니다."
    )

    # 세션 상태 초기화 (토글 시 시나리오 유지 및 P5 시뮬레이터 연동)
    if "stress_scenario" not in st.session_state:
        st.session_state.stress_scenario = "레고랜드 사태"
    if "stress_apply_strategy" not in st.session_state:
        st.session_state.stress_apply_strategy = False
    if "stress_strategy_name" not in st.session_state:
        st.session_state.stress_strategy_name = "중기 위험자산 정상화"

    strategy_options = list(STRATEGY_PRESETS.keys())
    if "custom_sim_params" in st.session_state:
        strategy_options = ["시뮬레이터 설정 전략"] + strategy_options

    # 상단 컨트롤 바
    ctrl1, ctrl2, ctrl3 = st.columns([1.1, 0.8, 1.3])
    with ctrl1:
        st.session_state.stress_scenario = st.radio(
            "시나리오",
            options=["레고랜드 사태", "저축은행 사태"],
            index=0 if st.session_state.stress_scenario == "레고랜드 사태" else 1,
            horizontal=True,
        )
    with ctrl2:
        st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
        st.session_state.stress_apply_strategy = st.toggle(
            "전략 적용",
            value=st.session_state.stress_apply_strategy,
        )
    with ctrl3:
        default_idx = (
            strategy_options.index(st.session_state.stress_strategy_name)
            if st.session_state.stress_strategy_name in strategy_options
            else 0
        )
        st.session_state.stress_strategy_name = st.selectbox(
            "비교할 전략",
            options=strategy_options,
            index=default_idx,
        )

    scenarios = get_excel_stress_series()
    sc_name = st.session_state.stress_scenario
    sc = scenarios[sc_name]
    st.caption(sc["subtitle"])

    # 선택된 전략 시뮬레이션 계산
    sel_strat = st.session_state.stress_strategy_name
    if sel_strat == "시뮬레이터 설정 전략" and "custom_sim_params" in st.session_state:
        p = st.session_state.custom_sim_params
    else:
        p = STRATEGY_PRESETS.get(sel_strat, STRATEGY_PRESETS["현상 유지"])

    sim_res = simulate_strategy(
        p["cut_4"], p["cut_5"], p["cut_6"], p["dividend"], p["years"], p.get("internal_bonus", 0.0)
    )

    base_path = sc["baseline_bis"]
    base_min = min(base_path)
    strat_path = sim_res["stress_paths"][sc_name]
    strat_min = min(strat_path)

    apply_on = st.session_state.stress_apply_strategy
    active_min = strat_min if apply_on else base_min
    start_bis = strat_path[0] if apply_on else base_path[0]
    drop_from_start = active_min - start_bis
    buffer_over_8 = active_min - BASE_STATE["reg_min_bis"]

    # 핵심 지표 4개
    k1, k2, k3, k4 = st.columns(4)
    if apply_on:
        k1.metric("기간 중 최저 BIS (전략 적용)", f"{active_min:.2f}%", f"{active_min - base_min:+.2f}%p vs 현상 유지")
    else:
        k1.metric("기간 중 최저 BIS", f"{active_min:.2f}%", "2029.06 도달", delta_color="off")
    k2.metric("출발 대비 하락폭", f"{drop_from_start:+.2f}%p", f"출발 BIS {start_bis:.2f}%", delta_color="off")
    k3.metric("규제 최저선(8%) 여유", f"+{buffer_over_8:.2f}%p", "최소 규제 기준 8.0%")
    k4.metric("3년 누적 순이익", f"{sc['cum_net_income_eok']:,}억원", "현상 유지 기준", delta_color="off")

    # 메인 차트 2개
    x_labels = [f"{p_lbl}<br><span style='font-size:10px;color:#94A3B8;'>{h_lbl}</span>"
                for p_lbl, h_lbl in zip(STRESS_PERIODS, sc["reproduced_half"])]

    c_left, c_right = st.columns([1.25, 1])
    with c_left:
        st.markdown(f"#### {sc_name} 시 BIS 경로")
        fig_path = go.Figure()
        fig_path.add_trace(go.Scatter(
            x=x_labels, y=base_path,
            mode="lines+markers", name="현상 유지",
            line=dict(color="#64748B", width=2.5),
            marker=dict(size=7, color="#64748B"),
        ))

        if apply_on:
            fig_path.add_trace(go.Scatter(
                x=x_labels, y=strat_path,
                mode="lines+markers+text", name=f"전략 적용 ({sel_strat})",
                line=dict(color="#1D4ED8", width=3.5),
                marker=dict(size=8, color="#1D4ED8"),
                text=[f"{v:.2f}%" for v in strat_path],
                textposition="top center",
            ))
        else:
            fig_path.add_trace(go.Scatter(
                x=x_labels, y=sc["normal_2009"],
                mode="lines+markers", name="2009.12 출발 (과거 평상시)",
                line=dict(color="#92400E", width=2, dash="dot"),
                marker=dict(size=6),
            ))
            fig_path.add_trace(go.Scatter(
                x=x_labels, y=sc["normal_2021"],
                mode="lines+markers", name="2021.12 출발 (과거 평상시)",
                line=dict(color="#1D4ED8", width=2, dash="dot"),
                marker=dict(size=6),
            ))

        fig_path.update_layout(
            height=390,
            yaxis_title="BIS 비율 (%)",
            yaxis=dict(range=[5, 32]),
            legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="white",
        )
        fig_path.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        st.plotly_chart(fig_path, use_container_width=True)

    with c_right:
        st.markdown("#### 전략별 최저 BIS 비교 (두 시나리오)")
        comp_df = get_all_strategy_comparison()
        rev_df = comp_df.iloc[::-1]

        fig_dumb = go.Figure()
        for _, row in rev_df.iterrows():
            fig_dumb.add_trace(go.Scatter(
                x=[row["레고랜드 사태"], row["저축은행 사태"]],
                y=[row["전략"], row["전략"]],
                mode="lines",
                line=dict(color="#CBD5E1", width=3),
                showlegend=False,
                hoverinfo="skip",
            ))

        fig_dumb.add_trace(go.Scatter(
            x=rev_df["레고랜드 사태"],
            y=rev_df["전략"],
            mode="markers",
            name="레고랜드 사태",
            marker=dict(color="#DC2626", size=11),
        ))
        fig_dumb.add_trace(go.Scatter(
            x=rev_df["저축은행 사태"],
            y=rev_df["전략"],
            mode="markers",
            name="저축은행 사태",
            marker=dict(color="#EAB308", size=11),
        ))
        fig_dumb.update_layout(
            height=390,
            xaxis_title="기간 중 최저 BIS (%)",
            xaxis=dict(range=[16.5, 25.0]),
            legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="white",
        )
        fig_dumb.update_xaxes(showgrid=True, gridcolor="#F1F5F9")
        st.plotly_chart(fig_dumb, use_container_width=True)

    if apply_on:
        render_insight_banner(
            f"<b>[{sel_strat}]</b> 적용 시 {sc_name} 기간 중 최저 BIS는 <b>{strat_min:.2f}%</b>로, 현상 유지({base_min:.2f}%) 대비 <b>{strat_min - base_min:+.2f}%p</b> 개선됩니다."
        )
    else:
        render_insight_banner(
            f"현상 유지 시 {sc_name}에서 BIS는 3년간 <b>{base_min - base_path[0]:+.2f}%p</b> 하락해 <b>{base_min:.2f}%</b>까지 내려갑니다. 상단의 <b>전략 적용</b>을 켜면 같은 충격에서 전략 효과를 비교합니다."
        )

    with st.expander("시나리오별 충격 변수 경로 보기 (업계 변화폭 적용 후 비율, 반기 %)"):
        st.dataframe(sc["shock_vars"], use_container_width=True, hide_index=True)


show()
