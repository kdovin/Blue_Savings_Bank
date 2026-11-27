import streamlit as st
import pandas as pd
from core.data import P1_KPI_CARDS, ALERT_SIGNALS, HISTORICAL_SHOCK_TABLE, ISSUE_TIMELINE
from core.model import get_excel_stress_series, BASE_STATE
from core.ui import (
    render_hero_company_intro,
    render_page_header,
    render_kpi_card,
    render_alert_panel,
    render_timeline_panel,
)


def show():
    # 0. 최상단 메인 기업 소개 + 구분선
    render_hero_company_intro()

    # 1. 스크롤 후 시작되는 통합 현황 헤더
    render_page_header(
        "통합 현황",
        "2026.06 기준 핵심 지표와 경보 신호, 위기 시 자본 완충력을 한눈에 확인합니다."
    )

    # 2. 상단 KPI 카드 6개 가로 1줄 배치 (미니 그래프 제거)
    kpi_cols = st.columns(len(P1_KPI_CARDS))
    for col, card in zip(kpi_cols, P1_KPI_CARDS):
        with col:
            render_kpi_card(card)

    # 3. 하단 3단 패널 (경보 신호 | 위기 시 자본 완충력 | 주요 이슈 타임라인)
    col_alert, col_buffer, col_timeline = st.columns([1.15, 1.0, 1.15])

    with col_alert:
        render_alert_panel(ALERT_SIGNALS)

    with col_buffer:
        scenarios = get_excel_stress_series()
        lg_min = min(scenarios["레고랜드 사태"]["baseline_bis"])
        sb_min = min(scenarios["저축은행 사태"]["baseline_bis"])
        lg_drop = lg_min - BASE_STATE["bis"]
        sb_drop = sb_min - BASE_STATE["bis"]

        st.markdown("#### 위기 시 자본 완충력")
        st.caption("2026.06 출발 · 과거 위기 업계 변화폭 적용 · 3년")

        b1, b2 = st.columns(2)
        b1.metric("레고랜드 사태 최저 BIS", f"{lg_min:.2f}%", f"{lg_drop:+.2f}%p")
        b2.metric("저축은행 사태 최저 BIS", f"{sb_min:.2f}%", f"{sb_drop:+.2f}%p")

        st.markdown("**같은 충격, 기준 시점별 하락폭 (%p)**")
        st.dataframe(
            pd.DataFrame(HISTORICAL_SHOCK_TABLE),
            use_container_width=True,
            hide_index=True,
        )

    with col_timeline:
        render_timeline_panel(ISSUE_TIMELINE)


show()
