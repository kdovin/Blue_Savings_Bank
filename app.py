import streamlit as st
from core.ui import inject_global_css, render_sidebar_chatbot_placeholder

st.set_page_config(
    page_title="푸른저축은행 자본 건전성 대시보드",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_css()

pages = [
    st.Page("views/p1_overview.py", title="통합 현황", icon="📊", default=True, url_path="overview"),
    st.Page("views/p2_financials.py", title="재무 지표", icon="📈", url_path="financials"),
    st.Page("views/p3_attribution.py", title="원인 분석", icon="🔍", url_path="attribution"),
    st.Page("views/p4_stress.py", title="위기상황분석", icon="⚡", url_path="stress"),
    st.Page("views/p5_simulator.py", title="전략 시뮬레이터", icon="🎛️", url_path="simulator"),
]

pg = st.navigation(pages)
render_sidebar_chatbot_placeholder()
pg.run()
