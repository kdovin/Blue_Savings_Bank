import streamlit as st
import plotly.graph_objects as go
from core.data import COMPANY_INFO, find_logo_path


# ---------------------------------------------------------
# 1. 전역 CSS 스타일 (모든 CSS는 이 파일 한 곳에만 작성)
# ---------------------------------------------------------
def inject_global_css():
    st.markdown("""
    <style>
        /* 페이지 여백 최적화 (P1 1920x1080 한 화면 수납 지원) */
        .block-container {
            padding-top: 1.35rem !important;
            padding-bottom: 1.5rem !important;
            padding-left: 2.2rem !important;
            padding-right: 2.2rem !important;
            max-width: 100% !important;
        }
        h1, h2, h3 {
            color: #0F172A !important;
            letter-spacing: -0.4px;
            margin-bottom: 0.25rem !important;
        }
        .page-subtitle {
            color: #64748B;
            font-size: 14px;
            margin-bottom: 0.85rem;
        }

        /* 사이드바 P0 기업 소개 박스 */
        .sidebar-brand-box {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-left: 4px solid #005BAC;
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 10px;
        }
        .sidebar-brand-title {
            font-size: 17px;
            font-weight: 800;
            color: #003366;
            margin-bottom: 2px;
        }
        .sidebar-brand-sub {
            font-size: 11.5px;
            font-weight: 600;
            color: #005BAC;
            margin-bottom: 6px;
        }
        .sidebar-brand-desc {
            font-size: 12px;
            line-height: 1.5;
            color: #475569;
        }

        /* 상태 배지 (위험 / 주의 / 양호) */
        .badge-danger {
            background-color: #FEE2E2;
            color: #DC2626;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 5px;
            margin-left: 6px;
        }
        .badge-warn {
            background-color: #FEF3C7;
            color: #D97706;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 5px;
            margin-left: 6px;
        }
        .badge-good {
            background-color: #DCFCE7;
            color: #16A34A;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 5px;
            margin-left: 6px;
        }

        /* P1 KPI 카드 */
        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 12px 14px 4px 14px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }
        .kpi-card-title {
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            display: flex;
            align-items: center;
            margin-bottom: 4px;
        }
        .kpi-card-val {
            font-size: 26px;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.15;
            margin-bottom: 6px;
        }
        .kpi-delta-pos {
            display: inline-block;
            background-color: #DCFCE7;
            color: #15803D;
            font-size: 11.5px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 999px;
        }
        .kpi-delta-neg {
            display: inline-block;
            background-color: #FEE2E2;
            color: #DC2626;
            font-size: 11.5px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 999px;
        }

        /* P1 하단 3패널 컨테이너 */
        .panel-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
            height: 100%;
        }
        .panel-title {
            font-size: 16px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 2px;
        }
        .panel-sub {
            font-size: 12px;
            color: #64748B;
            margin-bottom: 12px;
        }

        /* 경보 신호 행 */
        .alert-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 7px 10px;
            border-radius: 7px;
            margin-bottom: 6px;
            font-size: 12.5px;
            line-height: 1.4;
        }
        .alert-danger {
            background-color: #FEF2F2;
            border-left: 3.5px solid #EF4444;
        }
        .alert-warn {
            background-color: #FFFBEB;
            border-left: 3.5px solid #F59E0B;
        }
        .alert-good {
            background-color: #F0FDF4;
            border-left: 3.5px solid #22C55E;
        }

        /* 이슈 타임라인 행 */
        .timeline-row {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            padding: 6px 0;
            border-bottom: 1px solid #F1F5F9;
            font-size: 12.5px;
            line-height: 1.4;
        }
        .timeline-date {
            color: #005BAC;
            font-weight: 700;
            min-width: 52px;
        }
        .timeline-tag {
            background-color: #EFF6FF;
            color: #1D4ED8;
            font-size: 11px;
            font-weight: 600;
            padding: 1px 6px;
            border-radius: 4px;
            min-width: 48px;
            text-align: center;
        }

        /* 인사이트 콜아웃 박스 */
        .insight-banner {
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-left: 4px solid #005BAC;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13.5px;
            color: #1E3A8A;
            margin-top: 10px;
            line-height: 1.55;
        }

        /* 일반 메트릭 카드 */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 14px 16px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. P0: 사이드바 제목 및 기업 소개 렌더링
# ---------------------------------------------------------
def render_sidebar_p0():
    logo_path = find_logo_path()
    with st.sidebar:
        if logo_path:
            st.image(logo_path, use_container_width=True)
        st.markdown(f"""
        <div class="sidebar-brand-box">
            <div class="sidebar-brand-title">🏦 {COMPANY_INFO['name']}</div>
            <div class="sidebar-brand-sub">{COMPANY_INFO['ticker']} · {COMPANY_INFO['badge']}</div>
            <div class="sidebar-brand-desc">{COMPANY_INFO['summary']}</div>
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. 공통 UI 헬퍼 컴포넌트
# ---------------------------------------------------------
def render_page_header(title: str, subtitle: str):
    st.markdown(f"## {title}")
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_insight_banner(text: str):
    st.markdown(f'<div class="insight-banner">💡 {text}</div>', unsafe_allow_html=True)


def render_kpi_spark_card(card_dict: dict):
    badge_html = ""
    if card_dict.get("badge") == "위험":
        badge_html = '<span class="badge-danger">위험</span>'
    elif card_dict.get("badge") == "주의":
        badge_html = '<span class="badge-warn">주의</span>'
    elif card_dict.get("badge") == "양호":
        badge_html = '<span class="badge-good">양호</span>'

    delta_cls = "kpi-delta-pos" if card_dict["delta_type"] == "pos" else "kpi-delta-neg"
    arrow = "↑" if card_dict["delta"].startswith("+") else "↓"
    line_color = "#16A34A" if card_dict["delta_type"] == "pos" else "#DC2626"
    fill_color = "rgba(22, 163, 74, 0.08)" if card_dict["delta_type"] == "pos" else "rgba(220, 38, 38, 0.08)"

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-card-title">{card_dict['title']}{badge_html}</div>
        <div class="kpi-card-val">{card_dict['value']}</div>
        <div class="{delta_cls}">{arrow} {card_dict['delta']}</div>
    </div>
    """, unsafe_allow_html=True)

    y_vals = card_dict["spark"]
    fig = go.Figure(go.Scatter(
        x=list(range(len(y_vals))),
        y=y_vals,
        mode="lines",
        line=dict(color=line_color, width=2),
        fill="tozeroy",
        fillcolor=fill_color,
        hoverinfo="skip",
    ))
    fig.update_layout(
        height=46,
        margin=dict(l=0, r=0, t=2, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, range=[min(y_vals) * 0.9, max(y_vals) * 1.05]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_alert_panel(alerts: list):
    rows_html = []
    for item in alerts:
        lvl = item["level"]
        if lvl == "위험":
            row_cls, dot, badge = "alert-danger", "🔴", '<span class="badge-danger">위험</span>'
        elif lvl == "주의":
            row_cls, dot, badge = "alert-warn", "🟡", '<span class="badge-warn">주의</span>'
        else:
            row_cls, dot, badge = "alert-good", "🟢", '<span class="badge-good">양호</span>'

        rows_html.append(f"""
        <div class="alert-row {row_cls}">
            <div>{dot} <b>{item['metric']}</b> <span style="color:#334155;">{item['detail']}</span></div>
            <div>{badge}</div>
        </div>
        """)

    st.markdown(f"""
    <div class="panel-card">
        <div class="panel-title">경보 신호</div>
        <div class="panel-sub">2026.06 기준 · 업계 평균은 최근 공표치(2026.03)</div>
        {''.join(rows_html)}
    </div>
    """, unsafe_allow_html=True)


def render_timeline_panel(issues: list):
    rows_html = []
    for item in issues:
        rows_html.append(f"""
        <div class="timeline-row">
            <div class="timeline-date">{item['date']}</div>
            <div class="timeline-tag">{item['tag']}</div>
            <div style="color:#1E293B;">{item['text']}</div>
        </div>
        """)

    st.markdown(f"""
    <div class="panel-card">
        <div class="panel-title">주요 이슈 타임라인</div>
        <div class="panel-sub">최신 주요 사건 · 재무 및 건전성 공시 이력</div>
        {''.join(rows_html)}
        <div style="font-size:11px; color:#94A3B8; margin-top:8px;">
            출처: 분석 데이터셋 · 한국신용평가 · 언론 보도 (일부는 DART 공시로 최종 확인)
        </div>
    </div>
    """, unsafe_allow_html=True)
