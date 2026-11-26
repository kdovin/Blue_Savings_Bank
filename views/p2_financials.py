import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.data import TS_FINANCIALS, LIQUIDITY_JUNE
from core.model import BASE_STATE
from core.ui import render_page_header, render_insight_banner


def _marker_symbols(confirmed_list):
    return ["circle" if c else "circle-open" for c in confirmed_list]


def show():
    render_page_header(
        "재무 지표",
        "수익성 · 유동성 · 자산건전성 · 자본적정성의 대표 지표를 같은 기간 축에서 비교합니다."
    )
    st.caption("● 채운 점 = 원 데이터셋 · 보고서 확인값 · ○ 빈 점 = 확인값 사이를 채운 가상(보간) 값")

    q = TS_FINANCIALS["quarters"]
    symbols = _marker_symbols(TS_FINANCIALS["confirmed"])

    # -----------------------------------------------------
    # 1. 상단 2x2 대표 지표 그리드
    # -----------------------------------------------------
    row1_c1, row1_c2 = st.columns(2)

    with row1_c1:
        st.markdown("#### 수익성 · ROA와 구조적이익률")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=q, y=TS_FINANCIALS["structural_profit"],
            mode="lines+markers", name="구조적이익률",
            line=dict(color="#93C5FD", width=2),
            marker=dict(symbol=symbols, size=6, color="#60A5FA"),
        ))
        fig1.add_trace(go.Scatter(
            x=q, y=TS_FINANCIALS["roa"],
            mode="lines+markers", name="ROA",
            line=dict(color="#1D4ED8", width=2.5),
            marker=dict(symbol=symbols, size=6, color="#1D4ED8"),
        ))
        fig1.update_layout(
            height=250, yaxis_title="%",
            legend=dict(orientation="h", y=1.15, x=1, xanchor="right"),
            margin=dict(l=10, r=10, t=25, b=10), plot_bgcolor="white",
        )
        fig1.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("경상적 이자이익 기반 구조적이익률(2.35%)은 양호하나 대손비용 확대로 최종 ROA(0.94%)가 하회합니다.")

    with row1_c2:
        st.markdown("#### 유동성 · 6월 기준 유동성비율 (계절성 제거)")
        fig2 = go.Figure()
        fig2.add_hline(
            y=LIQUIDITY_JUNE["reg_limit"], line_dash="dash", line_color="#EF4444",
            annotation_text="규제 기준 100%", annotation_position="bottom right",
        )
        fig2.add_trace(go.Scatter(
            x=LIQUIDITY_JUNE["years"], y=LIQUIDITY_JUNE["values"],
            mode="lines+markers+text", name="푸른저축은행",
            line=dict(color="#1D4ED8", width=2.5),
            marker=dict(size=8, color="#1D4ED8"),
            text=[f"{v:.0f}%" for v in LIQUIDITY_JUNE["values"]],
            textposition="top center",
        ))
        fig2.update_layout(
            height=250, yaxis_title="%", yaxis=dict(range=[50, 560]),
            legend=dict(orientation="h", y=1.15, x=1, xanchor="right"),
            margin=dict(l=10, r=10, t=25, b=10), plot_bgcolor="white",
        )
        fig2.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("매년 6월 결산 기준 비교 시 2024.06(482%) 정점 이후 2026.06(137.3%)로 급락하며 기간 최저치를 기록했습니다.")

    row2_c1, row2_c2 = st.columns(2)

    with row2_c1:
        st.markdown("#### 자산건전성 · 고정이하여신비율")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=q, y=TS_FINANCIALS["npl_blue"],
            mode="lines+markers", name="푸른저축은행",
            line=dict(color="#1D4ED8", width=2.5),
            marker=dict(symbol=symbols, size=6, color="#1D4ED8"),
        ))
        fig3.add_trace(go.Scatter(
            x=q, y=TS_FINANCIALS["npl_peer"],
            mode="lines+markers", name="업계 평균",
            line=dict(color="#94A3B8", width=2, dash="dash"),
            marker=dict(size=5, color="#94A3B8"),
        ))
        fig3.update_layout(
            height=250, yaxis_title="%",
            legend=dict(orientation="h", y=1.15, x=1, xanchor="right"),
            margin=dict(l=10, r=10, t=25, b=10), plot_bgcolor="white",
        )
        fig3.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("2024년 이후 부실여신 누적으로 고정이하여신비율(10.19%)이 업계 평균(8.60%)을 지속 상회하고 있습니다.")

    with row2_c2:
        st.markdown("#### 자본적정성 · BIS 자기자본비율")
        fig4 = go.Figure()
        fig4.add_hline(y=BASE_STATE["rec_bis"], line_dash="dash", line_color="#F59E0B", annotation_text="권고 11%")
        fig4.add_hline(y=BASE_STATE["reg_min_bis"], line_dash="dash", line_color="#EF4444", annotation_text="규제 8%")
        fig4.add_trace(go.Scatter(
            x=q, y=TS_FINANCIALS["bis_blue"],
            mode="lines+markers", name="푸른저축은행",
            line=dict(color="#1D4ED8", width=2.5),
            marker=dict(symbol=symbols, size=6, color="#1D4ED8"),
        ))
        fig4.add_trace(go.Scatter(
            x=q, y=TS_FINANCIALS["bis_peer"],
            mode="lines+markers", name="업계 평균",
            line=dict(color="#94A3B8", width=2, dash="dash"),
            marker=dict(size=5, color="#94A3B8"),
        ))
        fig4.update_layout(
            height=250, yaxis_title="%", yaxis=dict(range=[5, 31]),
            legend=dict(orientation="h", y=1.15, x=1, xanchor="right"),
            margin=dict(l=10, r=10, t=25, b=10), plot_bgcolor="white",
        )
        fig4.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("절대 수준(22.13%)은 업계(16.0%)보다 높지만 2021년(27.31%) 이후 추세적 하락이 이어지고 있습니다.")

    # -----------------------------------------------------
    # 2. 하단 영역별 상세 5개 탭
    # -----------------------------------------------------
    st.divider()
    st.markdown("### 영역별 상세")
    tab_prof, tab_liq, tab_asset, tab_cap, tab_link = st.tabs([
        "수익성", "유동성", "자산건전성", "자본적정성", "영역 간 연결"
    ])

    with tab_prof:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### ROA vs 구조적이익률")
            f_p1 = go.Figure()
            f_p1.add_vrect(
                x0="2023.09", x1="2026.06",
                fillcolor="#FEF3C7", opacity=0.45, line_width=0,
                annotation_text="ROA < 구조적이익률", annotation_position="top left",
            )
            f_p1.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["structural_profit"], mode="lines+markers", name="구조적이익률", line=dict(color="#60A5FA", width=2)))
            f_p1.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["roa"], mode="lines+markers", name="ROA", line=dict(color="#1D4ED8", width=2.5)))
            f_p1.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
            st.plotly_chart(f_p1, use_container_width=True)
            st.caption("2023.09 이후 경상 이익창출력(구조적이익률)과 실제 당기순이익률(ROA) 간 괴리가 고착화되었습니다.")

        with c2:
            st.markdown("##### 순이자마진(NIM)")
            f_p2 = go.Figure(go.Scatter(x=q, y=TS_FINANCIALS["nim"], mode="lines+markers", name="푸른저축은행", line=dict(color="#1D4ED8", width=2.5)))
            f_p2.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
            st.plotly_chart(f_p2, use_container_width=True)
            st.caption("예대마진 방어로 순이자마진(NIM)은 2026.06 기준 4.02%로 높은 수준을 유지하고 있습니다.")

        st.markdown("##### ROE")
        f_p3 = go.Figure(go.Scatter(x=q, y=TS_FINANCIALS["roe"], mode="lines+markers", name="푸른저축은행", line=dict(color="#1D4ED8", width=2.5)))
        f_p3.update_layout(height=250, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
        st.plotly_chart(f_p3, use_container_width=True)
        st.caption("자기자본이익률(ROE) 역시 대손충당금 전입 부담으로 과거 10%대에서 4.6% 수준으로 낮아졌습니다.")

        render_insight_banner(
            "구조적이익률은 2026.06 <b>2.35%</b>로 기간 최고지만, ROA는 2023.09부터 이를 계속 밑돌아 버는 돈이 최종 이익으로 이어지지 않습니다."
        )

    with tab_liq:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 분기별 유동성비율 추이 (계절성 포함)")
            f_l1 = go.Figure()
            f_l1.add_hline(y=100, line_dash="dash", line_color="#EF4444", annotation_text="규제 한도 100%")
            f_l1.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["liquidity_all"], mode="lines+markers", name="유동성비율(%)", line=dict(color="#005BAC", width=2.5)))
            f_l1.update_layout(height=290, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
            st.plotly_chart(f_l1, use_container_width=True)
            st.caption("만기 집중 시점에 따라 계절적 등락을 보이나 2026.06 수치는 과거 반기 대비 이례적으로 낮습니다.")

        with c2:
            st.markdown("##### 예대율 추이 (규제 한도 100% 비교)")
            f_l2 = go.Figure()
            f_l2.add_hline(y=100, line_dash="dash", line_color="#EF4444", annotation_text="규제 한도 100%")
            f_l2.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["ldr_blue"], mode="lines+markers", name="예대율(%)", line=dict(color="#D97706", width=2.5)))
            f_l2.update_layout(height=290, yaxis=dict(range=[75, 105]), margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
            st.plotly_chart(f_l2, use_container_width=True)
            st.caption("예대율이 규제 한도(100%)에 근접하게 운용되며 추가 여신 확장 및 유동성 여력이 제약되고 있습니다.")

        render_insight_banner(
            "유동성비율(6월)이 <b>137.3%</b>까지 하락하고 예대율이 규제 상한선(100%)에 근접하면서 단기 자금 완충 여력이 축소되었습니다."
        )

    with tab_asset:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 연체율 추이 (푸른저축은행 vs 업계 평균)")
            f_a1 = go.Figure()
            f_a1.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["delinquency_blue"], mode="lines+markers", name="푸른저축은행", line=dict(color="#DC2626", width=2.5)))
            f_a1.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["delinquency_peer"], mode="lines+markers", name="업계 평균", line=dict(color="#94A3B8", width=2, dash="dash")))
            f_a1.update_layout(height=290, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
            st.plotly_chart(f_a1, use_container_width=True)
            st.caption("연체율(6.89%)이 업계 평균(6.60%)을 상회하며 부실채권 상·매각 이후에도 재상승 압력이 남아 있습니다.")

        with c2:
            st.markdown("##### 대손충당금 적립률 (커버리지비율)")
            f_a2 = go.Figure()
            f_a2.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["coverage_blue"], mode="lines+markers", name="푸른저축은행", line=dict(color="#D97706", width=2.5)))
            f_a2.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["coverage_peer"], mode="lines+markers", name="업계 평균", line=dict(color="#94A3B8", width=2, dash="dash")))
            f_a2.update_layout(height=290, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
            st.plotly_chart(f_a2, use_container_width=True)
            st.caption("부실여신 증가 속도를 충당금 적립이 따라가지 못해 커버리지비율(63.7%)이 업계 평균(71.6%)을 하회합니다.")

        render_insight_banner(
            "고정이하여신비율(<b>10.19%</b>)과 연체율(<b>6.89%</b>)이 모두 업계 평균을 웃도는 가운데, 손실 흡수 버퍼인 커버리지비율(<b>63.70%</b>)은 업계 대비 7.9%p 낮습니다."
        )

    with tab_cap:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 총자본(BIS)비율 vs 기본자본(Tier1)비율")
            f_c1 = go.Figure()
            f_c1.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["bis_blue"], mode="lines+markers", name="BIS 총자본비율", line=dict(color="#003366", width=2.5)))
            f_c1.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["tier1_blue"], mode="lines+markers", name="기본자본(Tier1)비율", line=dict(color="#3B82F6", width=2, dash="dot")))
            f_c1.update_layout(height=290, margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
            st.plotly_chart(f_c1, use_container_width=True)
            st.caption("자본 구성의 대부분이 기본자본(Tier1)으로 이루어져 질적 구성은 양호하나 비율 하락 속도가 빠릅니다.")

        with c2:
            st.markdown("##### 부동산담보대출 비중 추이 (%)")
            f_c2 = go.Figure()
            f_c2.add_trace(go.Scatter(x=q, y=TS_FINANCIALS["re_share"], mode="lines+markers", name="부동산담보대출 비중(%)", line=dict(color="#DC2626", width=2.5)))
            f_c2.update_layout(height=290, yaxis=dict(range=[50, 72]), margin=dict(l=10, r=10, t=20, b=10), plot_bgcolor="white")
            st.plotly_chart(f_c2, use_container_width=True)
            st.caption("위험가중치 100%가 적용되는 부동산담보대출 비중이 56%에서 67.3%까지 확대되며 BIS 하락을 주도했습니다.")

        render_insight_banner(
            "BIS 비율은 업계 대비 <b>+6.13%p</b> 높지만, 업계와의 격차가 10.1%p(2024.12)에서 4.8%p(2026.03)로 빠르게 축소되고 있습니다."
        )

    with tab_link:
        st.markdown("##### 4개 영역 연쇄 전이 경로: 부동산 여신 편중 → 건전성 악화 → 수익성 저하 → 자본비율 하락")
        f_link = make_subplots(specs=[[{"secondary_y": True}]])
        f_link.add_trace(
            go.Bar(x=q, y=TS_FINANCIALS["npl_blue"], name="고정이하여신비율 (건전성, %)", marker_color="rgba(220, 38, 38, 0.25)"),
            secondary_y=False,
        )
        f_link.add_trace(
            go.Scatter(x=q, y=TS_FINANCIALS["roa"], name="ROA (수익성, %)", line=dict(color="#D97706", width=2.5)),
            secondary_y=False,
        )
        f_link.add_trace(
            go.Scatter(x=q, y=TS_FINANCIALS["bis_blue"], name="BIS 비율 (자본적정성, %)", line=dict(color="#003366", width=3)),
            secondary_y=True,
        )
        f_link.update_layout(
            height=330,
            legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="white",
        )
        f_link.update_yaxes(title_text="고정이하여신 · ROA (%)", secondary_y=False)
        f_link.update_yaxes(title_text="BIS 비율 (%)", range=[15, 30], secondary_y=True)
        st.plotly_chart(f_link, use_container_width=True)
        render_insight_banner(
            "<b>핵심 인과 구조:</b> 부동산담보대출 확대(RWA 증가)와 고정이하여신 상승(건전성 악화)이 대손비용을 키워 ROA(수익성)를 깎아내리고, 결국 이익잉여금 축적 둔화와 함께 BIS 비율(자본적정성)을 끌어내리고 있습니다."
        )


show()
