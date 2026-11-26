import os
import glob
import unicodedata
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="푸른저축은행 자본 건전성 및 스트레스 테스트 보고서",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    h1, h2, h3 {
        color: #003366 !important;
        letter-spacing: -0.3px;
    }
    .chapter-eyebrow {
        font-size: 13px;
        font-weight: 700;
        color: #005BAC;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .exec-summary-box {
        background-color: #F4F8FD;
        border-left: 5px solid #003366;
        border-top: 1px solid #DCE8F5;
        border-right: 1px solid #DCE8F5;
        border-bottom: 1px solid #DCE8F5;
        padding: 18px 22px;
        border-radius: 0 8px 8px 0;
        margin: 12px 0 22px 0;
        font-size: 15.5px;
        line-height: 1.65;
        color: #1E293B;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D8E6F3;
        border-left: 5px solid #005BAC;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0, 51, 102, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #334155;
    }
    .roadmap-card {
        background-color: #F8FBFF;
        border: 1px solid #CBE0F5;
        border-top: 4px solid #005BAC;
        border-radius: 8px;
        padding: 16px;
        height: 100%;
    }
    .roadmap-card-active {
        background-color: #EBF4FF;
        border: 1.5px solid #005BAC;
        border-top: 5px solid #003366;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 4px 10px rgba(0, 91, 172, 0.12);
        height: 100%;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 6px 4px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


def find_excel_path():
    xlsx_files = glob.glob("**/*.xlsx", recursive=True)
    for path in xlsx_files:
        norm_name = unicodedata.normalize("NFC", os.path.basename(path))
        if "푸른저축은행" in norm_name and not norm_name.startswith("~$"):
            return path
    for path in xlsx_files:
        if not os.path.basename(path).startswith("~$"):
            return path
    return None


@st.cache_data
def read_excel_sheet(file_source):
    return pd.read_excel(file_source, sheet_name="푸른저축은행_202606")


def find_logo():
    img_exts = (".png", ".jpg", ".jpeg", ".svg", ".webp")
    all_files = glob.glob("**/*", recursive=True)
    images = [f for f in all_files if os.path.isfile(f) and f.lower().endswith(img_exts)]
    for path in images:
        if path.startswith("assets/") or path.startswith("assets\\"):
            return path
    for path in images:
        norm_name = unicodedata.normalize("NFC", os.path.basename(path)).lower()
        if "logo" in norm_name or "로고" in norm_name:
            return path
    for path in images:
        if os.path.dirname(path) == "":
            return path
    return None


excel_path = find_excel_path()
logo_path = find_logo()

CHAPTERS = [
    "1. 현황 진단 및 서론 스트레스 테스트",
    "2. 자본 축소 기여도 분석",
    "3. 자본 회복 솔루션 시뮬레이터",
    "4. 솔루션 후 스트레스 테스트 재검증"
]

if "chapter_idx" not in st.session_state:
    st.session_state.chapter_idx = 0


def sync_from_radio():
    st.session_state.chapter_idx = CHAPTERS.index(st.session_state.chapter_radio)


def go_prev():
    if st.session_state.chapter_idx > 0:
        st.session_state.chapter_idx -= 1


def go_next():
    if st.session_state.chapter_idx < len(CHAPTERS) - 1:
        st.session_state.chapter_idx += 1


with st.sidebar:
    if logo_path:
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("## 🏦 푸른저축은행")

    st.markdown("**KOSDAQ: 007950 | 기업 건전성 분석 보고서**")
    st.divider()

    uploaded_excel = None
    if excel_path is None:
        uploaded_excel = st.file_uploader("📂 엑셀 파일 선택 (.xlsx)", type=["xlsx"])

    st.markdown("### 📑 보고서 목차 (Chapters)")
    st.radio(
        "열람할 장을 선택하세요:",
        options=CHAPTERS,
        index=st.session_state.chapter_idx,
        key="chapter_radio",
        on_change=sync_from_radio,
        label_visibility="collapsed"
    )

    cur_idx = st.session_state.chapter_idx
    st.progress((cur_idx + 1) / len(CHAPTERS))
    st.caption(f"보고서 열람 진행률: **{cur_idx + 1} / {len(CHAPTERS)} 장**")

    st.divider()

    st.markdown("### 🎛️ 기준 스트레스 시나리오")
    selected_crisis = st.radio(
        "외부 위기 충격 가정 (2026.12 ~ 2029.06)",
        options=["시나리오 1: 레고랜드 사태", "시나리오 2: 저축은행 사태"],
        index=0,
        help="과거 실제 금융위기 당시 업계 변화폭을 푸른저축은행(2026.06 기준)에 적용한 결과입니다."
    )

    st.divider()
    st.caption("기준일: 2026.06 결산 | 예측: 2026.12~2029.06")

data_source = uploaded_excel if uploaded_excel is not None else excel_path
if data_source is None:
    st.warning("⚠️ 엑셀 파일을 찾을 수 없습니다. 좌측 사이드바에서 엑셀 파일을 업로드해 주세요.")
    st.stop()

df_raw = read_excel_sheet(data_source)

periods = ["2026.06(기준)", "2026.12", "2027.06", "2027.12", "2028.06", "2028.12", "2029.06"]

base_bis = float(df_raw.iloc[42, 1])
base_cap_eok = float(df_raw.iloc[8, 1]) / 1e8
base_rwa_eok = float(df_raw.iloc[29, 1]) / 1e8
base_re_loan_eok = float(df_raw.iloc[22, 1]) / 1e8
base_tot_loan_eok = float(df_raw.iloc[24, 1]) / 1e8
base_tot_asset = float(df_raw.iloc[34, 1])
base_div_eok = float(df_raw.iloc[37, 1]) / 1e8

bis_sb = [base_bis] + [float(x) for x in df_raw.iloc[42, 2:8]]
bis_lg = [base_bis] + [float(x) for x in df_raw.iloc[42, 8:14]]

cap_sb = [base_cap_eok] + [float(x) / 1e8 for x in df_raw.iloc[8, 2:8]]
cap_lg = [base_cap_eok] + [float(x) / 1e8 for x in df_raw.iloc[8, 8:14]]

if "레고랜드" in selected_crisis:
    col_range = range(8, 14)
    active_bis_list = bis_lg
    active_cap_list = cap_lg
    crisis_short = "레고랜드 사태"
else:
    col_range = range(2, 8)
    active_bis_list = bis_sb
    active_cap_list = cap_sb
    crisis_short = "저축은행 사태"

min_bis = min(active_bis_list)
min_cap = min(active_cap_list)
bis_drop = min_bis - base_bis
cap_drop = min_cap - base_cap_eok

sol1_data = {
    "적용 전 (As-Is)": {
        "rwa": base_rwa_eok, "cap": base_cap_eok, "div": base_div_eok, "bis": base_bis,
        "desc": "현재 부동산담보대출 편중 및 기존 배당 정책 유지 상태"
    },
    "1단계: 단기 집중위험 조정": {
        "rwa": float(df_raw.iloc[46, 1]) / 1e8,
        "cap": base_cap_eok,
        "div": base_div_eok,
        "bis": float(df_raw.iloc[47, 1]),
        "desc": "고위험 부동산 편중 여신 단기 축소로 RWA 485.7억 원(-3.3%) 즉시 감축"
    },
    "2단계: 중기 위험자산 정상화": {
        "rwa": float(df_raw.iloc[48, 1]) / 1e8,
        "cap": float(df_raw.iloc[52, 1]) / 1e8,
        "div": float(df_raw.iloc[49, 1]) / 1e8,
        "bis": float(df_raw.iloc[53, 1]),
        "desc": "여신 포트폴리오 다각화 및 정상화로 RWA 누적 1,056.0억 원(-7.2%) 감축"
    },
    "3단계: 중기 자본확충 병행": {
        "rwa": float(df_raw.iloc[54, 1]) / 1e8,
        "cap": float(df_raw.iloc[58, 1]) / 1e8,
        "div": float(df_raw.iloc[55, 1]) / 1e8,
        "bis": float(df_raw.iloc[59, 1]),
        "desc": "RWA 정상화 유지 + 현금배당 50% 감축(45.1억 유보)으로 자기자본 직접 확충"
    }
}

sol2_data = {
    "적용 전 (As-Is)": {
        "rwa": base_rwa_eok, "cap": base_cap_eok, "div": base_div_eok, "bis": base_bis,
        "desc": "현재 부동산담보대출 편중 및 기존 배당 정책 유지 상태"
    },
    "회복 시나리오": {
        "rwa": float(df_raw.iloc[62, 1]) / 1e8,
        "cap": float(df_raw.iloc[66, 1]) / 1e8,
        "div": float(df_raw.iloc[63, 1]) / 1e8,
        "bis": float(df_raw.iloc[67, 1]),
        "desc": "현금배당 유보(+14.1억) 및 RWA 851.5억 원(-5.8%) 감축을 통한 기본 회복 목표"
    },
    "강화 시나리오": {
        "rwa": float(df_raw.iloc[68, 1]) / 1e8,
        "cap": float(df_raw.iloc[72, 1]) / 1e8,
        "div": float(df_raw.iloc[69, 1]) / 1e8,
        "bis": float(df_raw.iloc[73, 1]),
        "desc": "현금배당 유보(+14.1억) 및 RWA 1,921.5억 원(-13.1%) 감축으로 방어력 대폭 강화"
    },
    "최고 수준 회복 시나리오": {
        "rwa": float(df_raw.iloc[74, 1]) / 1e8,
        "cap": float(df_raw.iloc[78, 1]) / 1e8,
        "div": float(df_raw.iloc[75, 1]) / 1e8,
        "bis": float(df_raw.iloc[79, 1]),
        "desc": "현금배당 유보(+14.1억) 및 RWA 2,729.4억 원(-18.6%) 감축으로 과거 최고 BIS(27.3%) 회복"
    }
}


def get_bis_series(row_idx):
    return [float(df_raw.iloc[row_idx, 1])] + [float(df_raw.iloc[row_idx, c]) for c in col_range]


post_stress_series = {
    "적용 전 (As-Is)": active_bis_list,
    "방법 1 - 1단계 (단기 집중위험 조정)": get_bis_series(47),
    "방법 1 - 2단계 (중기 위험자산 정상화)": get_bis_series(53),
    "방법 1 - 3단계 (중기 자본확충 병행)": get_bis_series(59),
    "방법 2 - 회복 시나리오": get_bis_series(67),
    "방법 2 - 강화 시나리오": get_bis_series(73),
    "방법 2 - 최고 수준 회복 시나리오": get_bis_series(79),
}

if cur_idx == 0:
    st.markdown('<div class="chapter-eyebrow">CHAPTER 01 / 04 · EXECUTIVE DIAGNOSIS</div>', unsafe_allow_html=True)
    st.title("1. 현황 진단 및 서론 스트레스 테스트")
    st.markdown(
        f'<div class="exec-summary-box">'
        f'<b>[핵심 요약]</b> 2026년 6월 기준 푸른저축은행의 BIS 자기자본비율은 <b>{base_bis:.2f}%</b>로 양호한 외형을 보이고 있으나, '
        f'총대출의 <b>{base_re_loan_eok / base_tot_loan_eok * 100:.1f}%({base_re_loan_eok:,.0f}억 원)</b>가 부동산담보대출에 편중되어 있습니다. '
        f'과거 2대 금융위기 충격을 6개 반기(2026.12~2029.06)에 적용할 경우, <b>레고랜드 사태 시 {min(bis_lg):.2f}%(-4.41%p)</b>, '
        f'<b>저축은행 사태 시 {min(bis_sb):.2f}%(-2.91%p)</b>까지 자본 건전성이 급락하는 구조적 취약성이 확인되었습니다.'
        f'</div>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("현재 BIS 비율 (2026.06)", f"{base_bis:.2f}%", "국내 유일 상장 저축은행")
    k2.metric("부동산담보대출 편중도", f"{base_re_loan_eok / base_tot_loan_eok * 100:.1f}%", f"{base_re_loan_eok:,.0f}억 / 총대출 {base_tot_loan_eok:,.0f}억", delta_color="off")
    k3.metric("레고랜드 충격 최저 BIS", f"{min(bis_lg):.2f}%", f"{min(bis_lg) - base_bis:.2f}%p 하락 (2029.06)")
    k4.metric("저축은행 충격 최저 BIS", f"{min(bis_sb):.2f}%", f"{min(bis_sb) - base_bis:.2f}%p 하락 (2029.06)")

    st.divider()

    col_left, col_right = st.columns([1.45, 1])
    with col_left:
        st.markdown("#### 📉 위기 시나리오별 BIS 자기자본비율 하락 궤적 (2026.06 ~ 2029.06)")
        fig_stress = go.Figure()
        fig_stress.add_hline(y=base_bis, line_dash="dot", line_color="#64748B", annotation_text=f"2026.06 기준 ({base_bis:.2f}%)", annotation_position="top right")
        fig_stress.add_hline(y=20.0, line_dash="dash", line_color="#E67E22", annotation_text="건전성 심리적 방어선 (20.0%)", annotation_position="bottom left")
        fig_stress.add_trace(go.Scatter(x=periods, y=bis_sb, mode="lines+markers+text", name="시나리오 2: 저축은행 사태", line=dict(color="#0073E6", width=3), marker=dict(size=8), text=[f"{v:.2f}%" for v in bis_sb], textposition="top center"))
        fig_stress.add_trace(go.Scatter(x=periods, y=bis_lg, mode="lines+markers+text", name="시나리오 1: 레고랜드 사태", line=dict(color="#D9383A", width=3), marker=dict(size=8), text=[f"{v:.2f}%" for v in bis_lg], textposition="bottom center"))
        fig_stress.update_layout(height=420, yaxis_title="BIS 자기자본비율 (%)", yaxis=dict(range=[16.5, 23.5]), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="white")
        fig_stress.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_stress, use_container_width=True)

    with col_right:
        st.markdown("#### 🏢 위험가중자산(RWA) 편중 구조 (2026.06)")
        deposit_rwa_eok = float(df_raw.iloc[16:22, 1].sum()) * 0.2 / 1e8
        other_loan_eok = float(df_raw.iloc[23, 1]) / 1e8
        sec_eok = float(df_raw.iloc[26, 1]) / 1e8
        etc_rwa_eok = (float(df_raw.iloc[25, 1]) + float(df_raw.iloc[28, 1])) / 1e8 + deposit_rwa_eok

        rwa_df = pd.DataFrame({
            "자산 항목": ["부동산담보대출", "유가증권(지준제외)", "기타잔여대출", "기타 위험가중자산·예치금"],
            "금액(억원)": [base_re_loan_eok, sec_eok, other_loan_eok, etc_rwa_eok]
        })
        fig_rwa = px.pie(rwa_df, values="금액(억원)", names="자산 항목", hole=0.45, color_discrete_sequence=["#00468C", "#2B7DE9", "#6BA5E7", "#B8D4F5"])
        fig_rwa.update_traces(textposition="inside", textinfo="percent+label")
        fig_rwa.update_layout(height=420, showlegend=False, margin=dict(l=10, r=10, t=40, b=20))
        st.plotly_chart(fig_rwa, use_container_width=True)

    st.markdown("#### 📋 반기별 스트레스 테스트 상세 수치표 (적용 전 As-Is)")
    table_df = pd.DataFrame({
        "구분": periods,
        "레고랜드 사태 BIS (%)": [f"{v:.2f}%" for v in bis_lg],
        "레고랜드 자기자본 (억원)": [f"{v:,.1f}" for v in cap_lg],
        "저축은행 사태 BIS (%)": [f"{v:.2f}%" for v in bis_sb],
        "저축은행 자기자본 (억원)": [f"{v:,.1f}" for v in cap_sb],
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)

elif cur_idx == 1:
    base_int_inc_r = float(df_raw.iloc[30, 1])
    base_int_exp_r = float(df_raw.iloc[31, 1])
    base_prov_r = float(df_raw.iloc[32, 1])
    base_nonint_r = float(df_raw.iloc[33, 1])
    base_pretax_6_eok = (float(df_raw.iloc[39, 1]) * 6) / 1e8

    scen_int_inc_r = [float(df_raw.iloc[30, c]) for c in col_range]
    scen_int_exp_r = [float(df_raw.iloc[31, c]) for c in col_range]
    scen_prov_r = [float(df_raw.iloc[32, c]) for c in col_range]
    scen_nonint_r = [float(df_raw.iloc[33, c]) for c in col_range]
    scen_pretax_6_eok = sum(float(df_raw.iloc[39, c]) for c in col_range) / 1e8

    contrib_int_inc = (sum(base_tot_asset * r / 100 for r in scen_int_inc_r) - (base_tot_asset * base_int_inc_r / 100) * 6) / 1e8
    contrib_int_exp = -(sum(base_tot_asset * r / 100 for r in scen_int_exp_r) - (base_tot_asset * base_int_exp_r / 100) * 6) / 1e8
    contrib_prov = -(sum(base_tot_asset * r / 100 for r in scen_prov_r) - (base_tot_asset * base_prov_r / 100) * 6) / 1e8
    contrib_nonint = (sum(base_tot_asset * r / 100 for r in scen_nonint_r) - (base_tot_asset * base_nonint_r / 100) * 6) / 1e8

    cum_net_inc_eok = sum(float(df_raw.iloc[41, c]) for c in col_range) / 1e8
    cum_div_eok = -sum(float(df_raw.iloc[37, c]) for c in col_range) / 1e8
    end_cap_eok = active_cap_list[-1]

    st.markdown('<div class="chapter-eyebrow">CHAPTER 02 / 04 · ROOT CAUSE & ATTRIBUTION</div>', unsafe_allow_html=True)
    st.title(f"2. 자본 축소 기여도 분석 ({crisis_short} 기준)")

    if "레고랜드" in selected_crisis:
        summary_html = (
            f"<b>[핵심 요약]</b> 레고랜드 사태 적용 시 6개 반기 누적 세전이익은 평시 대비 <b>{scen_pretax_6_eok - base_pretax_6_eok:,.1f}억 원</b> 급감하며, "
            f"결과적으로 자기자본이 <b>{base_cap_eok:,.1f}억 → {end_cap_eok:,.1f}억 원({cap_drop:,.1f}억 원)</b>으로 축소됩니다. "
            f"변수별 분해 결과 <b>① 조달금리 상승에 따른 이자비용률 급등({contrib_int_exp:+,.1f}억 원)</b>과 "
            f"<b>② 부동산 여신 부실화에 따른 대손비용률 상승({contrib_prov:+,.1f}억 원)</b>이 자본 훼손의 주원인으로 규명되었습니다."
        )
    else:
        summary_html = (
            f"<b>[핵심 요약]</b> 저축은행 사태 적용 시 6개 반기 누적 세전이익은 평시 대비 <b>{scen_pretax_6_eok - base_pretax_6_eok:,.1f}억 원</b> 감소하며, "
            f"결과적으로 자기자본이 <b>{base_cap_eok:,.1f}억 → {end_cap_eok:,.1f}억 원({cap_drop:,.1f}억 원)</b>으로 축소됩니다. "
            f"변수별 분해 결과 <b>① 여신 부실에 따른 대손비용률 급등({contrib_prov:+,.1f}억 원)</b>과 "
            f"<b>② 유가증권·수수료 등 비이자손익률 악화({contrib_nonint:+,.1f}억 원)</b>가 자본 축소를 주도했습니다."
        )
    st.markdown(f'<div class="exec-summary-box">{summary_html}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("6반기 누적 세전이익 변동", f"{scen_pretax_6_eok - base_pretax_6_eok:+,.1f}억 원", "평시 구조 유지 대비")
    c2.metric("대손비용률 상승 기여", f"{contrib_prov:+,.1f}억 원", "여신 건전성 악화 충격")
    c3.metric("이자비용 / 비이자손익 기여", f"{contrib_int_exp:+,.1f}억 / {contrib_nonint:+,.1f}억", "조달비용 및 평가손익", delta_color="off")
    c4.metric("자기자본 최종 축소액", f"{cap_drop:+,.1f}억 원", f"순손실 {cum_net_inc_eok:,.1f}억 + 배당 {cum_div_eok:,.1f}억")

    st.divider()

    c_left, c_right = st.columns([1.25, 1])
    with c_left:
        st.markdown(f"#### 📊 변수별 6반기 누적 세전이익 변동 기여도 ({crisis_short})")
        fig_wf1 = go.Figure(go.Waterfall(
            name="세전이익 기여도", orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["평시 유지 시<br>(6반기 누적)", "이자수익률<br>변동", "이자비용률<br>변동", "대손비용률<br>변동", "비이자손익률<br>변동", f"{crisis_short}<br>누적 세전이익"],
            y=[base_pretax_6_eok, contrib_int_inc, contrib_int_exp, contrib_prov, contrib_nonint, scen_pretax_6_eok],
            text=[f"{base_pretax_6_eok:,.0f}억", f"{contrib_int_inc:+,.0f}억", f"{contrib_int_exp:+,.0f}억", f"{contrib_prov:+,.0f}억", f"{contrib_nonint:+,.0f}억", f"{scen_pretax_6_eok:,.0f}억"],
            textposition="outside",
            connector={"line": {"color": "#94A3B8", "width": 1.5, "dash": "dot"}},
            increasing={"marker": {"color": "#0066CC"}},
            decreasing={"marker": {"color": "#D9383A"}},
            totals={"marker": {"color": "#003366"}}
        ))
        fig_wf1.update_layout(height=420, yaxis_title="금액 (억 원)", yaxis=dict(range=[min(scen_pretax_6_eok, -800) - 220, base_pretax_6_eok + contrib_int_inc + 250]), margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor="white")
        fig_wf1.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_wf1, use_container_width=True)

    with c_right:
        st.markdown(f"#### 🏛️ 자기자본 축소 경로 분해 ({crisis_short})")
        fig_wf2 = go.Figure(go.Waterfall(
            name="자기자본 변동", orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["기초 자기자본<br>(2026.06)", "누적 당기순손실<br>(이익잉여금 감소)", "현금배당<br>사외유출", "기말 자기자본<br>(2029.06)"],
            y=[base_cap_eok, cum_net_inc_eok, cum_div_eok, end_cap_eok],
            text=[f"{base_cap_eok:,.0f}억", f"{cum_net_inc_eok:+,.1f}억", f"{cum_div_eok:+,.1f}억", f"{end_cap_eok:,.0f}억"],
            textposition="outside",
            connector={"line": {"color": "#94A3B8", "width": 1.5, "dash": "dot"}},
            increasing={"marker": {"color": "#0066CC"}},
            decreasing={"marker": {"color": "#E05A47"}},
            totals={"marker": {"color": "#00468C"}}
        ))
        fig_wf2.update_layout(height=420, yaxis_title="자기자본 (억 원)", yaxis=dict(range=[2200, 3550]), margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor="white")
        fig_wf2.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_wf2, use_container_width=True)

    st.markdown(f"#### 📈 반기별 핵심 손익률(%) 변동 추이 ({crisis_short})")
    rate_df = pd.DataFrame({
        "기간": periods,
        "이자수익률(%)": [base_int_inc_r] + scen_int_inc_r,
        "이자비용률(%)": [base_int_exp_r] + scen_int_exp_r,
        "대손비용률(%)": [base_prov_r] + scen_prov_r,
        "비이자손익률(%)": [base_nonint_r] + scen_nonint_r,
    })
    fig_rates = go.Figure()
    for col_name, color, dash in [("이자수익률(%)", "#005BAC", "solid"), ("이자비용률(%)", "#E67E22", "dash"), ("대손비용률(%)", "#D9383A", "solid"), ("비이자손익률(%)", "#2E86C1", "dot")]:
        fig_rates.add_trace(go.Scatter(x=rate_df["기간"], y=rate_df[col_name], mode="lines+markers", name=col_name, line=dict(color=color, width=2.5, dash=dash), marker=dict(size=7)))
    fig_rates.update_layout(height=320, yaxis_title="비율 (%)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor="white")
    fig_rates.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
    st.plotly_chart(fig_rates, use_container_width=True)

elif cur_idx == 2:
    st.markdown('<div class="chapter-eyebrow">CHAPTER 03 / 04 · STRATEGIC SOLUTIONS</div>', unsafe_allow_html=True)
    st.title("3. 자본 회복 솔루션 시뮬레이터")
    st.markdown(
        '<div class="exec-summary-box">'
        '<b>[핵심 요약]</b> 자본 축소 기여도 분석에서 도출한 <b>위험가중자산(RWA) 감축</b>과 <b>현금배당 유보</b>를 결합하여 두 가지 개선 전략을 설계했습니다. '
        '<b>방법 1(단계별 로드맵)</b>은 단기 집중위험 조정부터 중기 자본확충까지 순차 실행해 평시 BIS를 <b>24.18%(+2.05%p)</b>까지 끌어올리며, '
        '<b>방법 2(목표 강도별 시나리오)</b>는 목표 방어 수준에 따라 평시 BIS를 <b>23.60%(회복) ~ 27.31%(최고 수준 회복)</b>까지 선제적으로 강화합니다.'
        '</div>',
        unsafe_allow_html=True
    )

    sub_tab1, sub_tab2 = st.tabs([
        "🛣️ 방법 1: 단계별 로드맵 (단기 집중위험 조정 → 중기 정상화 → 중기 자본확충)",
        "🎯 방법 2: 목표 강도별 시나리오 (회복 → 강화 → 최고 수준 회복)"
    ])

    with sub_tab1:
        selected_s1 = st.select_slider("실행 단계를 이동하며 BIS 비율 및 재무구조 개선 효과를 확인하세요:", options=list(sol1_data.keys()), value="3단계: 중기 자본확충 병행")
        cur1 = sol1_data[selected_s1]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("선택 단계 평시 BIS", f"{cur1['bis']:.2f}%", f"{cur1['bis'] - base_bis:+.2f}%p (기준 대비)")
        m2.metric("위험가중자산 (RWA)", f"{cur1['rwa']:,.1f}억 원", f"{cur1['rwa'] - base_rwa_eok:+,.1f}억 원 감축", delta_color="inverse")
        m3.metric("평시 자기자본", f"{cur1['cap']:,.1f}억 원", f"{cur1['cap'] - base_cap_eok:+,.1f}억 원 확충")
        m4.metric("연간 현금배당 규모", f"{cur1['div']:,.1f}억 원", f"{cur1['div'] - base_div_eok:+,.1f}억 원 조정", delta_color="off")

        rc1, rc2, rc3 = st.columns(3)
        for col_box, st_key in zip([rc1, rc2, rc3], ["1단계: 단기 집중위험 조정", "2단계: 중기 위험자산 정상화", "3단계: 중기 자본확충 병행"]):
            info = sol1_data[st_key]
            card_cls = "roadmap-card-active" if selected_s1 == st_key else "roadmap-card"
            badge = " ✅ [현재 선택]" if selected_s1 == st_key else ""
            with col_box:
                st.markdown(f"""
                <div class="{card_cls}">
                    <h4 style="color:#003366; margin-top:0;">{st_key}{badge}</h4>
                    <p style="font-size:14px; color:#334155;">{info['desc']}</p>
                    <hr style="margin:10px 0; border-color:#CBD5E1;">
                    <ul style="font-size:14px; padding-left:18px; margin-bottom:0; color:#0F172A;">
                        <li><b>목표 BIS 비율:</b> <span style="color:#005BAC; font-weight:700;">{info['bis']:.2f}%</span> ({info['bis']-base_bis:+.2f}%p)</li>
                        <li><b>RWA 변동:</b> {info['rwa'] - base_rwa_eok:+,.1f}억 원</li>
                        <li><b>자기자본 변동:</b> {info['cap'] - base_cap_eok:+,.1f}억 원</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        s1_labels = list(sol1_data.keys())
        fig_s1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_s1.add_trace(go.Bar(x=s1_labels, y=[sol1_data[k]["rwa"] for k in s1_labels], name="위험가중자산 RWA (억 원)", marker_color=["#94A3B8", "#6BA5E7", "#2B7DE9", "#00468C"], text=[f"{sol1_data[k]['rwa']:,.0f}억" for k in s1_labels], textposition="inside"), secondary_y=False)
        fig_s1.add_trace(go.Scatter(x=s1_labels, y=[sol1_data[k]["bis"] for k in s1_labels], name="BIS 자기자본비율 (%)", mode="lines+markers+text", line=dict(color="#003366", width=3.5), marker=dict(size=11, color="#005BAC"), text=[f"{sol1_data[k]['bis']:.2f}%" for k in s1_labels], textposition="top center"), secondary_y=True)
        fig_s1.update_layout(height=380, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="white")
        fig_s1.update_yaxes(title_text="위험가중자산 (억 원)", range=[11000, 16000], showgrid=True, gridcolor="#E2E8F0", secondary_y=False)
        fig_s1.update_yaxes(title_text="BIS 비율 (%)", range=[21.0, 25.5], showgrid=False, secondary_y=True)
        st.plotly_chart(fig_s1, use_container_width=True)

    with sub_tab2:
        selected_s2 = st.select_slider("목표 시나리오 강도를 선택하여 필요 RWA 감축 규모와 BIS 개선 효과를 비교하세요:", options=list(sol2_data.keys()), value="최고 수준 회복 시나리오")
        cur2 = sol2_data[selected_s2]
        n1, n2, n3, n4 = st.columns(4)
        n1.metric("선택 시나리오 평시 BIS", f"{cur2['bis']:.2f}%", f"{cur2['bis'] - base_bis:+.2f}%p (기준 대비)")
        n2.metric("위험가중자산 (RWA)", f"{cur2['rwa']:,.1f}억 원", f"{cur2['rwa'] - base_rwa_eok:+,.1f}억 원 감축", delta_color="inverse")
        n3.metric("평시 자기자본 (배당유보)", f"{cur2['cap']:,.1f}억 원", f"{cur2['cap'] - base_cap_eok:+,.1f}억 원 확충")
        n4.metric("연간 현금배당 규모", f"{cur2['div']:,.1f}억 원", f"{cur2['div'] - base_div_eok:+,.1f}억 원 유보", delta_color="off")

        sc1, sc2, sc3 = st.columns(3)
        for col_box, sc_key in zip([sc1, sc2, sc3], ["회복 시나리오", "강화 시나리오", "최고 수준 회복 시나리오"]):
            info = sol2_data[sc_key]
            card_cls = "roadmap-card-active" if selected_s2 == sc_key else "roadmap-card"
            badge = " ✅ [현재 선택]" if selected_s2 == sc_key else ""
            with col_box:
                st.markdown(f"""
                <div class="{card_cls}">
                    <h4 style="color:#003366; margin-top:0;">{sc_key}{badge}</h4>
                    <p style="font-size:14px; color:#334155;">{info['desc']}</p>
                    <hr style="margin:10px 0; border-color:#CBD5E1;">
                    <ul style="font-size:14px; padding-left:18px; margin-bottom:0; color:#0F172A;">
                        <li><b>목표 BIS 비율:</b> <span style="color:#005BAC; font-weight:700;">{info['bis']:.2f}%</span> ({info['bis']-base_bis:+.2f}%p)</li>
                        <li><b>RWA 감축 규모:</b> {info['rwa'] - base_rwa_eok:+,.1f}억 원 ({(info['rwa'] - base_rwa_eok)/base_rwa_eok*100:.1f}%)</li>
                        <li><b>현금배당 유보액:</b> +{info['cap'] - base_cap_eok:,.1f}억 원</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        s2_labels = list(sol2_data.keys())
        fig_s2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_s2.add_trace(go.Bar(x=s2_labels, y=[sol2_data[k]["rwa"] for k in s2_labels], name="위험가중자산 RWA (억 원)", marker_color=["#94A3B8", "#6BA5E7", "#2B7DE9", "#003366"], text=[f"{sol2_data[k]['rwa']:,.0f}억" for k in s2_labels], textposition="inside"), secondary_y=False)
        fig_s2.add_trace(go.Scatter(x=s2_labels, y=[sol2_data[k]["bis"] for k in s2_labels], name="BIS 자기자본비율 (%)", mode="lines+markers+text", line=dict(color="#005BAC", width=3.5), marker=dict(size=11, color="#003366"), text=[f"{sol2_data[k]['bis']:.2f}%" for k in s2_labels], textposition="top center"), secondary_y=True)
        fig_s2.update_layout(height=380, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="white")
        fig_s2.update_yaxes(title_text="위험가중자산 (억 원)", range=[10000, 16000], showgrid=True, gridcolor="#E2E8F0", secondary_y=False)
        fig_s2.update_yaxes(title_text="BIS 비율 (%)", range=[21.0, 29.0], showgrid=False, secondary_y=True)
        st.plotly_chart(fig_s2, use_container_width=True)

elif cur_idx == 3:
    st.markdown('<div class="chapter-eyebrow">CHAPTER 04 / 04 · POST-SOLUTION VALIDATION</div>', unsafe_allow_html=True)
    st.title(f"4. 솔루션 후 스트레스 테스트 재검증 ({crisis_short})")

    if "레고랜드" in selected_crisis:
        val_summary = (
            "<b>[최종 결론]</b> 레고랜드 사태 재검증 결과, 기존 <b>17.72%</b>까지 하락하던 최저 BIS 비율이 "
            "<b>방법 1(3단계 완료) 적용 시 19.64%(+1.92%p)</b>로 개선되며, <b>방법 2(강화·최고 수준 회복) 적용 시 20.51% ~ 21.89%(+4.17%p)</b>를 기록해 "
            "극심한 금융충격 하에서도 <b>20% 건전성 방어선을 완벽히 사수</b>하는 것으로 입증되었습니다."
        )
    else:
        val_summary = (
            "<b>[최종 결론]</b> 저축은행 사태 재검증 결과, 기존 <b>19.22%</b>까지 하락하던 최저 BIS 비율이 "
            "<b>방법 1(2~3단계) 적용 시 20.71% ~ 21.04%</b>로 20% 방어선을 상회하며, "
            "<b>방법 2(강화·최고 수준 회복) 적용 시 22.23% ~ 23.73%(+4.51%p)</b>를 달성해 위기를 겪고도 현재 평시(22.13%)보다 높은 건전성을 유지합니다."
        )
    st.markdown(f'<div class="exec-summary-box">{val_summary}</div>', unsafe_allow_html=True)

    ctrl_col1, ctrl_col2 = st.columns([1.2, 1.3])
    with ctrl_col1:
        view_group = st.radio(
            "그래프 비교 그룹 선택:",
            options=[
                "방법 1 전체 비교 (단기 → 중기 → 자본확충)",
                "방법 2 전체 비교 (회복 → 강화 → 최고 수준 회복)",
                "대표 최종안 직접 비교 (방법 1-3단계 vs 방법 2-강화·최고)"
            ],
            index=2
        )
    with ctrl_col2:
        focus_solution = st.selectbox(
            "상세 KPI 검증 대상 솔루션:",
            options=[
                "방법 1 - 1단계 (단기 집중위험 조정)",
                "방법 1 - 2단계 (중기 위험자산 정상화)",
                "방법 1 - 3단계 (중기 자본확충 병행)",
                "방법 2 - 회복 시나리오",
                "방법 2 - 강화 시나리오",
                "방법 2 - 최고 수준 회복 시나리오"
            ],
            index=5
        )

    focus_series = post_stress_series[focus_solution]
    focus_min_bis = min(focus_series)
    defense_gain = focus_min_bis - min_bis
    gap_to_22 = focus_min_bis - base_bis

    v1, v2, v3 = st.columns(3)
    v1.metric(f"적용 전 최저 BIS ({crisis_short})", f"{min_bis:.2f}%", f"현재 기준({base_bis:.2f}%) 대비 {min_bis - base_bis:+.2f}%p")
    v2.metric(f"적용 후 최저 BIS ({focus_solution.split('(')[0].strip()})", f"{focus_min_bis:.2f}%", f"적용 전 최저 대비 +{defense_gain:.2f}%p 방어")
    v3.metric("20% 건전성 방어선 검증", "20% 이상 방어 성공 🎉" if focus_min_bis >= 20.0 else f"20% 기준선까지 {20.0 - focus_min_bis:.2f}%p", f"현재 평시 BIS(22.13%) 대비 {gap_to_22:+.2f}%p", delta_color="off")

    st.divider()

    chart_col1, chart_col2 = st.columns([1.45, 1])
    with chart_col1:
        st.markdown(f"#### 📈 적용 전 vs 적용 후 BIS 비율 추이 ({crisis_short})")
        fig_post = go.Figure()
        fig_post.add_hline(y=base_bis, line_dash="dot", line_color="#475569", annotation_text=f"현재 평시 BIS ({base_bis:.2f}%)", annotation_position="top right")
        fig_post.add_hline(y=20.0, line_dash="dash", line_color="#E67E22", annotation_text="건전성 방어선 (20.00%)", annotation_position="bottom left")
        fig_post.add_trace(go.Scatter(x=periods, y=active_bis_list, mode="lines+markers+text", name="적용 전 (As-Is)", line=dict(color="#D9383A", width=3, dash="dash"), marker=dict(size=8, symbol="x"), text=[f"{v:.2f}%" for v in active_bis_list], textposition="bottom center"))

        if "방법 1 전체" in view_group:
            traces_to_plot = [("방법 1 - 1단계 (단기 집중위험 조정)", "#7FB3D5", 2.2), ("방법 1 - 2단계 (중기 위험자산 정상화)", "#2E86C1", 2.8), ("방법 1 - 3단계 (중기 자본확충 병행)", "#003366", 3.5)]
        elif "방법 2 전체" in view_group:
            traces_to_plot = [("방법 2 - 회복 시나리오", "#6BA5E7", 2.2), ("방법 2 - 강화 시나리오", "#0066CC", 2.8), ("방법 2 - 최고 수준 회복 시나리오", "#002B5B", 3.5)]
        else:
            traces_to_plot = [("방법 1 - 3단계 (중기 자본확충 병행)", "#2B7DE9", 2.8), ("방법 2 - 강화 시나리오", "#005BAC", 3.0), ("방법 2 - 최고 수준 회복 시나리오", "#002B5B", 3.6)]

        for idx_t, (t_name, t_color, t_width) in enumerate(traces_to_plot):
            y_vals = post_stress_series[t_name]
            is_top = (idx_t == len(traces_to_plot) - 1)
            fig_post.add_trace(go.Scatter(x=periods, y=y_vals, mode="lines+markers+text" if is_top else "lines+markers", name=t_name, line=dict(color=t_color, width=t_width), marker=dict(size=8 if is_top else 6), text=[f"{v:.2f}%" for v in y_vals] if is_top else None, textposition="top center"))

        fig_post.update_layout(height=440, yaxis_title="BIS 자기자본비율 (%)", yaxis=dict(range=[16.8, 28.5]), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor="white")
        fig_post.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_post, use_container_width=True)

    with chart_col2:
        st.markdown(f"#### 🏆 위기 최저점(2029.06) BIS 방어력 비교")
        bar_labels = ["적용 전 (As-Is)", "방법1-1단계(단기)", "방법2-회복", "방법1-2단계(중기)", "방법1-3단계(자본확충)", "방법2-강화", "방법2-최고수준회복"]
        bar_keys = ["적용 전 (As-Is)", "방법 1 - 1단계 (단기 집중위험 조정)", "방법 2 - 회복 시나리오", "방법 1 - 2단계 (중기 위험자산 정상화)", "방법 1 - 3단계 (중기 자본확충 병행)", "방법 2 - 강화 시나리오", "방법 2 - 최고 수준 회복 시나리오"]
        bar_mins = [min(post_stress_series[k]) for k in bar_keys]
        bar_colors = ["#D9383A" if v < 20.0 else ("#2B7DE9" if v < base_bis else "#003366") for v in bar_mins]

        fig_bar_min = go.Figure(go.Bar(x=bar_mins, y=bar_labels, orientation="h", marker_color=bar_colors, text=[f"{v:.2f}% ({v - min_bis:+.2f}%p)" for v in bar_mins], textposition="outside"))
        fig_bar_min.add_vline(x=20.0, line_dash="dash", line_color="#E67E22")
        fig_bar_min.add_vline(x=base_bis, line_dash="dot", line_color="#003366")
        fig_bar_min.update_layout(height=440, xaxis_title="위기 최저 BIS 비율 (%)", xaxis=dict(range=[16.0, 26.8]), margin=dict(l=10, r=20, t=50, b=20), plot_bgcolor="white")
        fig_bar_min.update_xaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_bar_min, use_container_width=True)

    st.markdown(f"#### 📋 {crisis_short} 시나리오 적용 전·후 전체 반기별 BIS 비율(%) 상세 비교표")
    full_comp_df = pd.DataFrame({"기간": periods})
    for label, series in post_stress_series.items():
        full_comp_df[label] = [f"{v:.2f}%" for v in series]
    st.dataframe(full_comp_df, use_container_width=True, hide_index=True)

st.divider()
nav_left, nav_mid, nav_right = st.columns([1, 2, 1])

with nav_left:
    if cur_idx > 0:
        st.button(f"⬅️ 이전 장 ({cur_idx}장)", on_click=go_prev, use_container_width=True)

with nav_mid:
    st.markdown(
        f"<div style='text-align:center; color:#475569; font-weight:600; padding-top:6px;'>"
        f"푸른저축은행 건전성 분석 보고서 &nbsp;|&nbsp; {cur_idx + 1} / {len(CHAPTERS)} 장"
        f"</div>",
        unsafe_allow_html=True
    )

with nav_right:
    if cur_idx < len(CHAPTERS) - 1:
        st.button(f"다음 장 ({cur_idx + 2}장) ➡️", on_click=go_next, type="primary", use_container_width=True)
