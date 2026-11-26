import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.data import ATTRIBUTION_ITEMS, ATTRIBUTION_CUMULATIVE, ATTRIBUTION_SEMIANNUAL
from core.ui import render_page_header, render_insight_banner


def _build_waterfall(start_label: str, end_label: str, bis_t0: float, bis_t1: float, item_vals: list):
    x_labels = [start_label] + ATTRIBUTION_ITEMS + [end_label]
    y_vals = [bis_t0] + item_vals + [bis_t1]
    measures = ["absolute"] + ["relative"] * len(ATTRIBUTION_ITEMS) + ["total"]
    texts = [f"{bis_t0:.2f}"] + [f"{v:+.2f}" for v in item_vals] + [f"{bis_t1:.2f}"]

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measures,
        x=x_labels,
        y=y_vals,
        text=texts,
        textposition="outside",
        connector={"line": {"color": "#CBD5E1", "width": 1.2, "dash": "dot"}},
        increasing={"marker": {"color": "#16A34A"}},
        decreasing={"marker": {"color": "#DC2626"}},
        totals={"marker": {"color": "#1D4ED8"}},
    ))
    y_min = min(bis_t0, bis_t1, bis_t0 + min(0, sum(item_vals))) - 3.5
    y_max = max(bis_t0, bis_t1) + 6.5
    fig.update_layout(
        height=420,
        yaxis_title="BIS 비율 (% / %p)",
        yaxis=dict(range=[max(0, y_min), y_max]),
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="white",
    )
    fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
    return fig


def _build_peer_bar(blue_vals: list, peer_vals: list):
    rev_items = ATTRIBUTION_ITEMS[::-1]
    rev_blue = blue_vals[::-1]
    rev_peer = peer_vals[::-1]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=rev_items, x=rev_peer,
        name="타 저축은행 평균",
        orientation="h",
        marker_color="#94A3B8",
    ))
    fig.add_trace(go.Bar(
        y=rev_items, x=rev_blue,
        name="푸른저축은행",
        orientation="h",
        marker_color="#1D4ED8",
    ))
    fig.add_vline(x=0, line_color="#475569", line_width=1)
    fig.update_layout(
        barmode="group",
        height=420,
        xaxis_title="기여도 (%p)",
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right"),
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9")
    return fig


def show():
    render_page_header(
        "원인 분석",
        "BIS비율 변동을 분자(자기자본 항목)와 분모(위험가중자산 항목)의 기여도로 분해합니다. 음수는 BIS를 낮춘 항목입니다."
    )

    mode = st.radio(
        "분석 구간",
        options=["누적 (2021.06 → 2026.06)", "반기별"],
        horizontal=True,
    )

    if mode.startswith("누적"):
        d = ATTRIBUTION_CUMULATIVE
        start_lbl, end_lbl = "2021.06", "2026.06"
        top_name = d["top_driver_name"]
        top_val = d["top_driver_share"]
        top_sub = d["top_driver_sub"]
        insight_txt = (
            "업계 BIS가 <b>+1.24%p</b> 오르는 동안 푸른저축은행만 <b>-5.18%p</b> 하락. "
            "이익잉여금이 +4.23%p 받쳤지만 <b>부동산담보대출 확대(-6.88%p)</b>와 기타 유가증권·유형자산(-3.12%p)의 분모 증가가 이를 압도했습니다."
        )
    else:
        period_options = [row["period"] for row in ATTRIBUTION_SEMIANNUAL]
        selected_p = st.selectbox("반기 비교 구간 선택", options=period_options, index=len(period_options) - 1)
        d = next(row for row in ATTRIBUTION_SEMIANNUAL if row["period"] == selected_p)
        start_lbl, end_lbl = selected_p.split(" → ")
        # 해당 반기 최대 기여 항목 자동 계산
        abs_idx = max(range(len(ATTRIBUTION_ITEMS)), key=lambda i: abs(d["blue_items"][i]))
        top_name = ATTRIBUTION_ITEMS[abs_idx]
        top_val = f"{d['blue_items'][abs_idx]:+.2f}%p"
        top_sub = f"업계 {d['peer_items'][abs_idx]:+.2f}%p"
        insight_txt = (
            f"<b>{selected_p}</b> 구간에서 푸른저축은행 BIS는 <b>{d['bis_t0']:.2f}% → {d['bis_t1']:.2f}% ({d['dbis_blue']:+.2f}%p)</b> 변동했으며, "
            f"가장 큰 변동 요인은 <b>{top_name} ({top_val})</b>입니다."
        )

    c_left, c_right = st.columns([1.25, 1])
    with c_left:
        st.markdown(f"#### 푸른저축은행 BIS 기여도 — {d['period']}")
        st.plotly_chart(
            _build_waterfall(start_lbl, end_lbl, d["bis_t0"], d["bis_t1"], d["blue_items"]),
            use_container_width=True,
        )

    with c_right:
        st.markdown("#### 타 저축은행 평균과 비교 (기여도, %p)")
        st.plotly_chart(
            _build_peer_bar(d["blue_items"], d["peer_items"]),
            use_container_width=True,
        )

    # 하단 요약 지표 4개
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("BIS 변동", f"{d['dbis_blue']:+.2f}%p", f"업계 {d['dbis_peer']:+.2f}%p")
    k2.metric("위험가중자산 기여 (분모)", f"{d['rwa_blue']:+.2f}%p", f"업계 {d['rwa_peer']:+.2f}%p")
    k3.metric("자기자본 기여 (분자)", f"{d['cap_blue']:+.2f}%p", f"업계 {d['cap_peer']:+.2f}%p")
    k4.metric(top_name, top_val, top_sub, delta_color="off")

    render_insight_banner(insight_txt)

    with st.expander("기여도 표 보기"):
        tbl = pd.DataFrame({
            "항목": ATTRIBUTION_ITEMS,
            "푸른저축은행 (%p)": [f"{v:+.2f}" for v in d["blue_items"]],
            "타 저축은행 평균 (%p)": [f"{v:+.2f}" for v in d["peer_items"]],
            "업계 대비 격차 (%p)": [f"{b - p:+.2f}" for b, p in zip(d["blue_items"], d["peer_items"])],
        })
        st.dataframe(tbl, use_container_width=True, hide_index=True)


show()
