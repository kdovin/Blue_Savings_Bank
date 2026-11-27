import streamlit as st
from core.data import COMPANY_INFO, find_logo_path


# ---------------------------------------------------------
# 1. 전역 CSS 스타일 (모든 CSS는 이 파일 한 곳에만 작성)
# ---------------------------------------------------------
def inject_global_css():
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
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
            margin-bottom: 1rem;
        }

        /* P0: 통합 현황 최상단 메인 기업 소개 히어로 섹션 */
        .company-hero-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);
            border: 1px solid #CBD5E1;
            border-left: 6px solid #005BAC;
            border-radius: 14px;
            padding: 26px 30px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
            margin-bottom: 8px;
        }
        .company-hero-badges {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }
        .hero-pill-primary {
            background-color: #005BAC;
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
        }
        .hero-pill-sub {
            background-color: #E2E8F0;
            color: #334155;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
        }
        .company-hero-title {
            font-size: 32px;
            font-weight: 800;
            color: #002B5B;
            letter-spacing: -0.6px;
            margin-bottom: 10px;
        }
        .company-hero-desc {
            font-size: 16.5px;
            font-weight: 500;
            line-height: 1.65;
            color: #1E293B;
        }
        .company-logo-fallback {
            background-color: #003366;
            color: #FFFFFF;
            border-radius: 12px;
            padding: 28px 16px;
            text-align: center;
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.3px;
        }

        /* 기업 소개와 통합 현황 사이의 확실한 구분선 */
        .hero-section-divider {
            border: none;
            border-top: 2px solid #CBD5E1;
            margin: 26px 0 28px 0;
        }

        /* 사이드바 하단 챗봇 검색 틀 */
        .sidebar-chat-box {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 12px 12px 10px 12px;
            margin-top: 8px;
        }
        .sidebar-chat-title {
            font-size: 13.5px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 4px;
        }
        .sidebar-chat-desc {
            font-size: 11.5px;
            line-height: 1.45;
            color: #64748B;
            margin-bottom: 8px;
        }
        .sidebar-chat-bubble {
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 11.5px;
            line-height: 1.45;
            color: #1E3A8A;
            margin-bottom: 8px;
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

        /* P1 KPI 카드 (미니 그래프 제거 후 깔끔한 닫힌 카드) */
        .kpi-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 15px 16px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            margin-bottom: 14px;
        }
        .kpi-card-title {
            font-size: 13px;
            font-weight: 600;
            color: #475569;
            display: flex;
            align-items: center;
            margin-bottom: 6px;
        }
        .kpi-card-val {
            font-size: 26px;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.2;
            margin-bottom: 8px;
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
# 2. P0: 통합 현황 최상단 메인 기업 소개 히어로 배너 + 구분선
# ---------------------------------------------------------
def render_hero_company_intro():
    logo_path = find_logo_path()

    st.markdown('<div class="company-hero-card">', unsafe_allow_html=True)
    col_logo, col_info = st.columns([1.0, 3.2], vertical_alignment="center")

    with col_logo:
        if logo_path:
            st.image(logo_path, use_container_width=True)
        else:
            st.markdown(
                f'<div class="company-logo-fallback">🏦 {COMPANY_INFO["name"]}</div>',
                unsafe_allow_html=True,
            )

    with col_info:
        st.markdown(f"""
        <div class="company-hero-badges">
            <span class="hero-pill-primary">{COMPANY_INFO['badge']}</span>
            <span class="hero-pill-sub">{COMPANY_INFO['ticker']}</span>
            <span class="hero-pill-sub">{COMPANY_INFO['base_date']}</span>
        </div>
        <div class="company-hero-title">{COMPANY_INFO['name']} 재무·자본 건전성 진단</div>
        <div class="company-hero-desc">{COMPANY_INFO['summary']}</div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<hr class="hero-section-divider">', unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. 사이드바 하단: 챗봇 검색 기능 틀 (추후 로직 연결용)
# ---------------------------------------------------------
def render_sidebar_chatbot_placeholder():
    with st.sidebar:
        st.divider()
        st.markdown("""
        <div class="sidebar-chat-box">
            <div class="sidebar-chat-title">💬 지표 · 용어 검색 챗봇</div>
            <div class="sidebar-chat-desc">BIS비율, RWA, 고정이하여신 등 대시보드 용어나 수치를 검색할 수 있는 영역입니다.</div>
        </div>
        """, unsafe_allow_html=True)

        if "sidebar_chat_history" not in st.session_state:
            st.session_state.sidebar_chat_history = []

        with st.form("sidebar_chat_form", clear_on_submit=True):
            user_q = st.text_input(
                "챗봇 검색어",
                placeholder="예: 고정이하여신비율 뜻이 뭐야?",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("검색", use_container_width=True)

        if submitted and user_q.strip():
            st.session_state.sidebar_chat_history.append(user_q.strip())

        if st.session_state.sidebar_chat_history:
            last_q = st.session_state.sidebar_chat_history[-1]
            st.markdown(
                f'<div class="sidebar-chat-bubble"><b>Q. {last_q}</b><br>🛠️ 챗봇 답변 엔진 연결 예정입니다. (검색어 수신 완료)</div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------
# 4. 공통 UI 헬퍼 컴포넌트
# ---------------------------------------------------------
def render_page_header(title: str, subtitle: str):
    st.markdown(f"## {title}")
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_insight_banner(text: str):
    st.markdown(f'<div class="insight-banner">💡 {text}</div>', unsafe_allow_html=True)


def render_kpi_card(card_dict: dict):
    badge_html = ""
    if card_dict.get("badge") == "위험":
        badge_html = '<span class="badge-danger">위험</span>'
    elif card_dict.get("badge") == "주의":
        badge_html = '<span class="badge-warn">주의</span>'
    elif card_dict.get("badge") == "양호":
        badge_html = '<span class="badge-good">양호</span>'

    delta_cls = "kpi-delta-pos" if card_dict["delta_type"] == "pos" else "kpi-delta-neg"
    arrow = "↑" if card_dict["delta"].startswith("+") else "↓"

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-card-title">{card_dict['title']}{badge_html}</div>
        <div class="kpi-card-val">{card_dict['value']}</div>
        <div class="{delta_cls}">{arrow} {card_dict['delta']}</div>
    </div>
    """, unsafe_allow_html=True)


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
