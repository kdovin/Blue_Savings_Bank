import streamlit as st
from core.model import (
    BASE_STATE,
    STRATEGY_PRESETS,
    simulate_strategy,
    reverse_calculate_bis,
)
from core.ui import render_page_header


def _apply_preset(preset_name: str):
    p = STRATEGY_PRESETS[preset_name]
    st.session_state.sim_preset = preset_name
    st.session_state.sim_cut_4 = float(p["cut_4"])
    st.session_state.sim_cut_5 = float(p["cut_5"])
    st.session_state.sim_cut_6 = float(p["cut_6"])
    st.session_state.sim_dividend = float(p["dividend"])
    st.session_state.sim_years = int(p["years"])
    st.session_state.sim_bonus = float(p.get("internal_bonus", 0.0))


def show():
    render_page_header(
        "전략 시뮬레이터",
        "위험가중자산 감축과 배당 정책을 조정해 목표 BIS를 계산합니다. 여기서 고른 전략은 위기상황분석의 '전략 적용'에 그대로 연결됩니다."
    )

    if "sim_preset" not in st.session_state:
        _apply_preset("중기 위험자산 정상화")

    col_left, col_right = st.columns([1.05, 1.15])

    # -----------------------------------------------------
    # 01 · 전략 조건 (프리셋 + RWA 감축 + 배당·내부유보)
    # -----------------------------------------------------
    with col_left:
        st.markdown("#### 01 · 전략 조건")
        st.caption("프리셋")

        preset_names = list(STRATEGY_PRESETS.keys())
        r1_cols = st.columns(4)
        for idx, name in enumerate(preset_names[:4]):
            btn_type = "primary" if st.session_state.sim_preset == name else "secondary"
            if r1_cols[idx].button(name, key=f"pre_{name}", type=btn_type, use_container_width=True):
                _apply_preset(name)
                st.rerun()

        r2_cols = st.columns(3)
        for idx, name in enumerate(preset_names[4:]):
            btn_type = "primary" if st.session_state.sim_preset == name else "secondary"
            if r2_cols[idx].button(name, key=f"pre_{name}", type=btn_type, use_container_width=True):
                _apply_preset(name)
                st.rerun()

        cur_preset_info = STRATEGY_PRESETS.get(st.session_state.sim_preset)
        if cur_preset_info:
            st.caption(cur_preset_info["desc"])

        st.markdown("**위험가중자산 감축 (억원)**")
        cut_4 = st.slider("④ 부동산담보대출", min_value=0.0, max_value=3000.0, step=10.0, key="sim_cut_4")
        cut_5 = st.slider("⑤ 기타 잔여대출", min_value=0.0, max_value=1500.0, step=10.0, key="sim_cut_5")
        cut_6 = st.slider("⑥ 기타 유가증권·유형자산", min_value=0.0, max_value=1500.0, step=10.0, key="sim_cut_6")

        st.markdown("**배당 · 내부유보**")
        dividend = st.slider("연간 현금배당 (억원)", min_value=0.0, max_value=120.0, step=0.1, key="sim_dividend")
        years = st.slider("평상시 누적 기간 (년)", min_value=1, max_value=5, step=1, key="sim_years")
        st.caption(f"기준 배당 {BASE_STATE['dividend']}억 대비 줄인 배당은 2025 결산분부터 자기자본에 바로 유보됩니다.")

    # 실시간 시뮬레이션 결과 계산 & 세션 동기화
    res = simulate_strategy(cut_4, cut_5, cut_6, dividend, years, st.session_state.get("sim_bonus", 0.0))
    st.session_state.custom_sim_params = {
        "cut_4": cut_4,
        "cut_5": cut_5,
        "cut_6": cut_6,
        "dividend": dividend,
        "years": years,
        "internal_bonus": st.session_state.get("sim_bonus", 0.0),
    }

    # -----------------------------------------------------
    # 02 · 결과 + 위기 시나리오 연동
    # -----------------------------------------------------
    with col_right:
        st.markdown(f"#### 02 · 결과 — {st.session_state.sim_preset}")

        m1, m2 = st.columns(2)
        m1.metric("목표 BIS (평상시)", f"{res['target_bis']:.2f}%", f"{res['bis_diff']:+.2f}%p vs 현재")
        m2.metric("위험가중자산", f"{res['new_rwa']:,}억원", f"{-res['rwa_cut']:,}억원", delta_color="inverse")

        m3, m4 = st.columns(2)
        m3.metric("자기자본", f"{res['new_cap']:,}억원", f"+{res['cap_gain']:,}억원 내부유보")
        m4.metric("부동산담보대출 RWA 감축률", f"{res['re_cut_pct']:.1f}%", f"잔액 {int(BASE_STATE['bal_4']):,}억원 기준", delta_color="off")

        st.markdown("**같은 전략을 위기 시나리오에 적용하면 (기간 중 최저 BIS)**")
        s1, s2 = st.columns(2)
        lg_min = res["stress_mins"]["레고랜드 사태"]
        sb_min = res["stress_mins"]["저축은행 사태"]
        s1.metric("레고랜드 사태", f"{lg_min:.2f}%", f"{res['stress_min_diffs']['레고랜드 사태']:+.2f}%p vs 현상 유지")
        s2.metric("저축은행 사태", f"{sb_min:.2f}%", f"{res['stress_min_diffs']['저축은행 사태']:+.2f}%p vs 현상 유지")

        if st.button("⚡ 위기상황분석에서 경로로 비교하기 →", use_container_width=True):
            st.session_state.stress_apply_strategy = True
            st.session_state.stress_strategy_name = "시뮬레이터 설정 전략"
            st.switch_page("views/p4_stress.py")

    # -----------------------------------------------------
    # 하단: 목표 BIS 역산 계산기
    # -----------------------------------------------------
    st.divider()
    st.markdown("#### 목표 BIS 역산")
    st.caption("목표 BIS와 배당을 정하면 필요한 위험가중자산 감축액을 계산하고, 부동산담보대출 : 기타 유가증권·유형자산 잔액 비율로 배분합니다 (솔루션 1 방식).")

    rev_c1, rev_c2, rev_c3 = st.columns([1, 1, 1.6])
    with rev_c1:
        rev_bis = st.number_input("목표 BIS (%)", min_value=20.0, max_value=35.0, value=25.58, step=0.1)
    with rev_c2:
        rev_div = st.number_input("연간 배당 (억원)", min_value=0.0, max_value=120.0, value=76.17, step=0.1)
    with rev_c3:
        rev_out = reverse_calculate_bis(rev_bis, rev_div, years=1)
        st.markdown(
            f"**필요 RWA 감축 {rev_out['needed_cut']:,}억원 → ④ 부동산담보대출 {rev_out['cut_4']:,}억원 + ⑥ 기타 유가증권·유형자산 {rev_out['cut_6']:,}억원**  \n"
            f"(조정 자기자본 {rev_out['adj_cap']:,}억원 ÷ 목표 RWA {rev_out['target_rwa']:,}억원)"
        )
        if st.button("이 조건을 시뮬레이터에 적용"):
            st.session_state.sim_preset = "역산 맞춤 조건"
            st.session_state.sim_cut_4 = float(rev_out["cut_4"])
            st.session_state.sim_cut_5 = 0.0
            st.session_state.sim_cut_6 = float(rev_out["cut_6"])
            st.session_state.sim_dividend = float(rev_div)
            st.session_state.sim_years = 1
            st.session_state.sim_bonus = 0.0
            st.rerun()


show()
