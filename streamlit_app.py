
import os
import glob
import unicodedata
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------
# 1. 페이지 기본 설정 & 푸른저축은행 블루 테마 CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="푸른저축은행 자본 건전성 및 스트레스 테스트 분석",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    h1, h2, h3 {
        color: #003366 !important;
    }
    div[data-testid="stMetric"] {
        background-color: #F0F6FC;
        border-left: 5px solid #005BAC;
        padding: 15px 18px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 51, 102, 0.06);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #1E3A5F;
    }
    button[data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #005BAC !important;
        border-bottom-color: #005BAC !important;
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
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. 데이터 및 로고 자동 로드 함수
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# 3. 사이드바 구성 (로고 + 시나리오 컨트롤러)
# ---------------------------------------------------------
with st.sidebar:
    if logo_path:
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("## 🏦 푸른저축은행")
    
    st.markdown("**KOSDAQ: 007950 | 기업 건전성 분석 리포트**")
    st.divider()

    uploaded_excel = None
    if excel_path is None:
        uploaded_excel = st.file_uploader("📂 엑셀 파일 직접 선택 (.xlsx)", type=["xlsx"])

    st.markdown("### 🎛️ 스트레스 시나리오 선택")
    selected_crisis = st.radio(
        "외부 위기 충격 시나리오 (2026.12 ~ 2029.06)",
        options=["시나리오 1: 레고랜드 사태", "시나리오 2: 저축은행 사태"],
        index=0,
        help="과거 실제 금융위기 당시 업계 변화폭을 푸른저축은행(2026.06 기준)에 적용한 결과입니다."
    )

    st.divider()
    st.markdown("### 📌 분석 프로세스")
    st.markdown(
        "1. **현황 진단:** 위기 시 BIS 하락폭 확인\n"
        "2. **원인 규명:** 손익·배당 기여도 분해\n"
        "3. **솔루션 설계:** 방법 1(단계) · 방법 2(강도)\n"
        "4. **효과 재검증:** 적용 전·후 방어력 비교"
    )

data_source = uploaded_excel if uploaded_excel is not None else excel_path
if data_source is None:
    st.warning("⚠️ 현재 작업 폴더에서 엑셀 파일을 찾지 못했습니다. 좌측 사이드바의 **[Browse files]** 버튼을 눌러 엑셀 파일을 직접 선택해 주세요.")
    st.stop()

df_raw = read_excel_sheet(data_source)


# ---------------------------------------------------------
# 4. 엑셀 데이터 파싱 (기준값, 스트레스 테스트, 기여도, 솔루션 1·2 전/후)
# ---------------------------------------------------------
periods = ["2026.06(기준)", "2026.12", "2027.06", "2027.12", "2028.06", "2028.12", "2029.06"]

base_bis = float(df_raw.iloc[42, 1])
base_cap_eok = float(df_raw.iloc[8, 1]) / 1e8
base_rwa_eok = float(df_raw.iloc[29, 1]) / 1e8
base_re_loan_eok = float(df_raw.iloc[22, 1]) / 1e8
base_tot_loan_eok = float(df_raw.iloc[24, 1]) / 1e8
base_tot_asset = float(df_raw.iloc[34, 1])
base_div_eok = float(df_raw.iloc[37, 1]) / 1e8

# BIS & 자기자본 시계열 (As-Is)
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

# 솔루션 1 & 솔루션 2 기준시점(2026.06) 데이터 구조화
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

# 솔루션 적용 후 스트레스 테스트 시계열 (현재 선택된 위기 시나리오 기준)
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


# ---------------------------------------------------------
# 5. 메인 헤더 & 상단 핵심 KPI 4개
# ---------------------------------------------------------
st.title("🏦 푸른저축은행 자본 적정성 및 스트레스 테스트 분석")
st.markdown("외부 금융충격 시나리오에 따른 **BIS 자기자본비율 하락 리스크 진단** 및 **포트폴리오·자본 구조 개선 효과**를 검증합니다.")

k1, k2, k3, k4 = st.columns(4)
k1.metric(
    label="현재 BIS 비율 (2026.06)",
    value=f"{base_bis:.2f}%",
    delta="국내 유일 상장 저축은행"
)
k2.metric(
    label=f"{crisis_short} 최저 BIS",
    value=f"{min_bis:.2f}%",
    delta=f"{bis_drop:.2f}%p 하락 (2029.06)",
    delta_color="normal"
)
k3.metric(
    label="현재 자기자본 → 최저 자기자본",
    value=f"{min_cap:,.0f}억 원",
    delta=f"{cap_drop:,.0f}억 원 축소 (기준 {base_cap_eok:,.0f}억)"
)
k4.metric(
    label="위험가중자산 (RWA)",
    value=f"{base_rwa_eok:,.0f}억 원",
    delta=f"부동산담보 비중 {base_re_loan_eok / base_rwa_eok * 100:.1f}%",
    delta_color="off"
)

st.divider()


# ---------------------------------------------------------
# 6. 4단계 분석 탭 (전체 구현 완료)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ 현황 진단 & 스트레스 테스트",
    "2️⃣ 자본 축소 기여도 분석",
    "3️⃣ 자본 회복 솔루션 시뮬레이터",
    "4️⃣ 솔루션 적용 후 재검증"
])

# =========================================================
# [탭 1] 현황 진단 & 스트레스 테스트
# =========================================================
with tab1:
    st.subheader("📌 [서론] 현재 자본 구조 진단 및 외부 충격 스트레스 테스트")
    st.markdown(
        f"2026년 6월 기준 푸른저축은행의 BIS 자기자본비율은 **{base_bis:.2f}%**로 양호해 보이나, "
        f"총대출의 **{base_re_loan_eok / base_tot_loan_eok * 100:.1f}%({base_re_loan_eok:,.0f}억 원)**가 부동산담보대출에 편중되어 있습니다. "
        f"과거 위기 충격을 적용할 경우 **레고랜드 사태 시 {min(bis_lg):.2f}%**, **저축은행 사태 시 {min(bis_sb):.2f}%**까지 BIS 비율이 하락합니다."
    )

    col_left, col_right = st.columns([1.45, 1])

    with col_left:
        st.markdown("#### 📉 위기 시나리오별 BIS 자기자본비율 추이 (2026.06 ~ 2029.06)")
        fig_stress = go.Figure()

        fig_stress.add_hline(
            y=base_bis, line_dash="dot", line_color="#64748B",
            annotation_text=f"2026.06 기준 ({base_bis:.2f}%)", annotation_position="top right"
        )
        fig_stress.add_trace(go.Scatter(
            x=periods, y=bis_sb, mode="lines+markers+text",
            name="시나리오 2: 저축은행 사태",
            line=dict(color="#0073E6", width=3),
            marker=dict(size=8),
            text=[f"{v:.2f}%" for v in bis_sb],
            textposition="top center"
        ))
        fig_stress.add_trace(go.Scatter(
            x=periods, y=bis_lg, mode="lines+markers+text",
            name="시나리오 1: 레고랜드 사태",
            line=dict(color="#D9383A", width=3),
            marker=dict(size=8),
            text=[f"{v:.2f}%" for v in bis_lg],
            textposition="bottom center"
        ))

        fig_stress.update_layout(
            height=410,
            yaxis_title="BIS 자기자본비율 (%)",
            yaxis=dict(range=[16.5, 23.5]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="white"
        )
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

        fig_rwa = px.pie(
            rwa_df, values="금액(억원)", names="자산 항목", hole=0.45,
            color_discrete_sequence=["#00468C", "#2B7DE9", "#6BA5E7", "#B8D4F5"]
        )
        fig_rwa.update_traces(textposition="inside", textinfo="percent+label")
        fig_rwa.update_layout(
            height=410,
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=20)
        )
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


# =========================================================
# [탭 2] 자본 축소 기여도 분석
# =========================================================
with tab2:
    st.subheader(f"🔍 [원인 규명] {crisis_short} 시 자본은 왜 축소되는가? (변수별 기여도 분석)")

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

    if "레고랜드" in selected_crisis:
        st.markdown(
            f"**레고랜드 사태** 적용 시 6개 반기 누적 세전이익은 평시 구조 유지 대비 **{scen_pretax_6_eok - base_pretax_6_eok:,.1f}억 원** 감소합니다. "
            f"기여도 분석 결과 **① 조달금리 상승에 따른 이자비용률 급등({contrib_int_exp:+,.1f}억 원)**과 "
            f"**② 부동산 PF 부실화에 따른 대손비용률 상승({contrib_prov:+,.1f}억 원)**이 자본 축소의 핵심 원인으로 나타났습니다."
        )
    else:
        st.markdown(
            f"**저축은행 사태** 적용 시 6개 반기 누적 세전이익은 평시 구조 유지 대비 **{scen_pretax_6_eok - base_pretax_6_eok:,.1f}억 원** 감소합니다. "
            f"기여도 분석 결과 **① 여신 부실화에 따른 대손비용률 급등({contrib_prov:+,.1f}억 원)**과 "
            f"**② 유가증권·수수료 등 비이자손익률 악화({contrib_nonint:+,.1f}억 원)**가 자본 축소를 주도했습니다."
        )

    c_left, c_right = st.columns([1.25, 1])

    with c_left:
        st.markdown(f"#### 📊 변수별 6반기 누적 세전이익 변동 기여도 ({crisis_short})")
        fig_wf1 = go.Figure(go.Waterfall(
            name="세전이익 기여도",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["평시 유지 시<br>(6반기 누적)", "이자수익률<br>변동", "이자비용률<br>변동", "대손비용률<br>변동", "비이자손익률<br>변동", f"{crisis_short}<br>누적 세전이익"],
            y=[base_pretax_6_eok, contrib_int_inc, contrib_int_exp, contrib_prov, contrib_nonint, scen_pretax_6_eok],
            text=[
                f"{base_pretax_6_eok:,.0f}억",
                f"{contrib_int_inc:+,.0f}억",
                f"{contrib_int_exp:+,.0f}억",
                f"{contrib_prov:+,.0f}억",
                f"{contrib_nonint:+,.0f}억",
                f"{scen_pretax_6_eok:,.0f}억"
            ],
            textposition="outside",
            connector={"line": {"color": "#94A3B8", "width": 1.5, "dash": "dot"}},
            increasing={"marker": {"color": "#0066CC"}},
            decreasing={"marker": {"color": "#D9383A"}},
            totals={"marker": {"color": "#003366"}}
        ))
        fig_wf1.update_layout(
            height=420,
            yaxis_title="금액 (억 원)",
            yaxis=dict(range=[min(scen_pretax_6_eok, -800) - 220, base_pretax_6_eok + contrib_int_inc + 250]),
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor="white"
        )
        fig_wf1.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_wf1, use_container_width=True)

    with c_right:
        st.markdown(f"#### 🏛️ 자기자본 축소 경로 분해 ({crisis_short})")
        fig_wf2 = go.Figure(go.Waterfall(
            name="자기자본 변동",
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["기초 자기자본<br>(2026.06)", "누적 당기순손실<br>(이익잉여금 감소)", "현금배당<br>사외유출", "기말 자기자본<br>(2029.06)"],
            y=[base_cap_eok, cum_net_inc_eok, cum_div_eok, end_cap_eok],
            text=[
                f"{base_cap_eok:,.0f}억",
                f"{cum_net_inc_eok:+,.1f}억",
                f"{cum_div_eok:+,.1f}억",
                f"{end_cap_eok:,.0f}억"
            ],
            textposition="outside",
            connector={"line": {"color": "#94A3B8", "width": 1.5, "dash": "dot"}},
            increasing={"marker": {"color": "#0066CC"}},
            decreasing={"marker": {"color": "#E05A47"}},
            totals={"marker": {"color": "#00468C"}}
        ))
        fig_wf2.update_layout(
            height=420,
            yaxis_title="자기자본 (억 원)",
            yaxis=dict(range=[2200, 3550]),
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor="white"
        )
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
    rate_styles = [
        ("이자수익률(%)", "#005BAC", "solid"),
        ("이자비용률(%)", "#E67E22", "dash"),
        ("대손비용률(%)", "#D9383A", "solid"),
        ("비이자손익률(%)", "#2E86C1", "dot"),
    ]
    for col_name, color, dash in rate_styles:
        fig_rates.add_trace(go.Scatter(
            x=rate_df["기간"], y=rate_df[col_name],
            mode="lines+markers", name=col_name,
            line=dict(color=color, width=2.5, dash=dash),
            marker=dict(size=7)
        ))
    fig_rates.update_layout(
        height=330,
        yaxis_title="비율 (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="white"
    )
    fig_rates.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
    st.plotly_chart(fig_rates, use_container_width=True)

    st.info(
        "💡 **기여도 분석을 통해 도출한 자본 회복 핵심 레버(Lever) 3가지**\n"
        "1. **위험가중자산(RWA) 감축:** 부동산담보대출 편중을 완화하여 위기 시에도 BIS 분모 부담을 경감\n"
        "2. **현금배당 유보 및 조정:** 사외 배당 유출을 통제하여 이익잉여금 기반의 자체 자본 완충력 보강\n"
        "3. **단계적·강도별 자본 적정성 회복:** 위 두 변수를 조합해 **방법 1(단기·중기 로드맵)**과 **방법 2(강도별 시나리오)**를 설계"
    )


# =========================================================
# [탭 3] 자본 회복 솔루션 시뮬레이터
# =========================================================
with tab3:
    st.subheader("🛠️ [해결방안] 포트폴리오 조정 및 자본 확충 전략 시뮬레이터")
    st.markdown(
        "기여도 분석에서 도출된 **위험가중자산(RWA) 감축**과 **현금배당 유보(자기자본 보강)** 변수를 수정하여 "
        "시계열 단계별 로드맵(**방법 1**)과 목표 회복 강도별 시나리오(**방법 2**)를 설계했습니다."
    )

    sub_tab1, sub_tab2 = st.tabs([
        "🛣️ 방법 1: 단계별 로드맵 (단기 집중위험 조정 → 중기 정상화 → 중기 자본확충)",
        "🎯 방법 2: 목표 강도별 시나리오 (회복 → 강화 → 최고 수준 회복)"
    ])

    with sub_tab1:
        st.markdown("#### 📌 실행 단계 선택 시뮬레이터")
        selected_s1 = st.select_slider(
            "실행 단계를 이동하며 BIS 비율 및 재무구조 개선 효과를 확인하세요:",
            options=list(sol1_data.keys()),
            value="3단계: 중기 자본확충 병행"
        )

        cur1 = sol1_data[selected_s1]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "선택 단계 BIS 비율",
            f"{cur1['bis']:.2f}%",
            f"{cur1['bis'] - base_bis:+.2f}%p (기준 대비)"
        )
        m2.metric(
            "위험가중자산 (RWA)",
            f"{cur1['rwa']:,.1f}억 원",
            f"{cur1['rwa'] - base_rwa_eok:+,.1f}억 원 감축",
            delta_color="inverse"
        )
        m3.metric(
            "평시 자기자본",
            f"{cur1['cap']:,.1f}억 원",
            f"{cur1['cap'] - base_cap_eok:+,.1f}억 원 확충"
        )
        m4.metric(
            "연간 현금배당 규모",
            f"{cur1['div']:,.1f}억 원",
            f"{cur1['div'] - base_div_eok:+,.1f}억 원 조정",
            delta_color="off"
        )

        st.markdown("#### 🪜 방법 1의 3단계 추진 로드맵")
        rc1, rc2, rc3 = st.columns(3)
        stage_keys = [
            "1단계: 단기 집중위험 조정",
            "2단계: 중기 위험자산 정상화",
            "3단계: 중기 자본확충 병행"
        ]
        for col_box, st_key in zip([rc1, rc2, rc3], stage_keys):
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

        st.markdown("#### 📊 단계별 위험가중자산(RWA) 감축 및 BIS 비율 계단식 상승")
        s1_labels = list(sol1_data.keys())
        s1_rwas = [sol1_data[k]["rwa"] for k in s1_labels]
        s1_biss = [sol1_data[k]["bis"] for k in s1_labels]

        fig_s1 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_s1.add_trace(
            go.Bar(
                x=s1_labels, y=s1_rwas, name="위험가중자산 RWA (억 원)",
                marker_color=["#94A3B8", "#6BA5E7", "#2B7DE9", "#00468C"],
                text=[f"{v:,.0f}억" for v in s1_rwas],
                textposition="inside"
            ),
            secondary_y=False
        )
        fig_s1.add_trace(
            go.Scatter(
                x=s1_labels, y=s1_biss, name="BIS 자기자본비율 (%)",
                mode="lines+markers+text",
                line=dict(color="#003366", width=3.5),
                marker=dict(size=11, color="#005BAC"),
                text=[f"{v:.2f}%" for v in s1_biss],
                textposition="top center"
            ),
            secondary_y=True
        )
        fig_s1.update_layout(
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="white"
        )
        fig_s1.update_yaxes(title_text="위험가중자산 (억 원)", range=[11000, 16000], showgrid=True, gridcolor="#E2E8F0", secondary_y=False)
        fig_s1.update_yaxes(title_text="BIS 비율 (%)", range=[21.0, 25.5], showgrid=False, secondary_y=True)
        st.plotly_chart(fig_s1, use_container_width=True)

    with sub_tab2:
        st.markdown("#### 📌 목표 회복 강도 선택 시뮬레이터")
        selected_s2 = st.select_slider(
            "목표 시나리오 강도를 선택하여 필요 RWA 감축 규모와 BIS 개선 효과를 비교하세요:",
            options=list(sol2_data.keys()),
            value="최고 수준 회복 시나리오"
        )

        cur2 = sol2_data[selected_s2]
        n1, n2, n3, n4 = st.columns(4)
        n1.metric(
            "선택 시나리오 BIS 비율",
            f"{cur2['bis']:.2f}%",
            f"{cur2['bis'] - base_bis:+.2f}%p (기준 대비)"
        )
        n2.metric(
            "위험가중자산 (RWA)",
            f"{cur2['rwa']:,.1f}억 원",
            f"{cur2['rwa'] - base_rwa_eok:+,.1f}억 원 감축",
            delta_color="inverse"
        )
        n3.metric(
            "평시 자기자본 (배당유보 반영)",
            f"{cur2['cap']:,.1f}억 원",
            f"{cur2['cap'] - base_cap_eok:+,.1f}억 원 확충"
        )
        n4.metric(
            "연간 현금배당 규모",
            f"{cur2['div']:,.1f}억 원",
            f"{cur2['div'] - base_div_eok:+,.1f}억 원 유보",
            delta_color="off"
        )

        st.markdown("#### 🎯 방법 2의 3단계 목표 강도 비교 카드")
        sc1, sc2, sc3 = st.columns(3)
        scen_keys = ["회복 시나리오", "강화 시나리오", "최고 수준 회복 시나리오"]
        for col_box, sc_key in zip([sc1, sc2, sc3], scen_keys):
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

        st.markdown("#### 📊 강도별 위험가중자산(RWA) 감축 및 BIS 비율 상승 비교")
        s2_labels = list(sol2_data.keys())
        s2_rwas = [sol2_data[k]["rwa"] for k in s2_labels]
        s2_biss = [sol2_data[k]["bis"] for k in s2_labels]

        fig_s2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig_s2.add_trace(
            go.Bar(
                x=s2_labels, y=s2_rwas, name="위험가중자산 RWA (억 원)",
                marker_color=["#94A3B8", "#6BA5E7", "#2B7DE9", "#003366"],
                text=[f"{v:,.0f}억" for v in s2_rwas],
                textposition="inside"
            ),
            secondary_y=False
        )
        fig_s2.add_trace(
            go.Scatter(
                x=s2_labels, y=s2_biss, name="BIS 자기자본비율 (%)",
                mode="lines+markers+text",
                line=dict(color="#005BAC", width=3.5),
                marker=dict(size=11, color="#003366"),
                text=[f"{v:.2f}%" for v in s2_biss],
                textposition="top center"
            ),
            secondary_y=True
        )
        fig_s2.update_layout(
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="white"
        )
        fig_s2.update_yaxes(title_text="위험가중자산 (억 원)", range=[10000, 16000], showgrid=True, gridcolor="#E2E8F0", secondary_y=False)
        fig_s2.update_yaxes(title_text="BIS 비율 (%)", range=[21.0, 29.0], showgrid=False, secondary_y=True)
        st.plotly_chart(fig_s2, use_container_width=True)

    st.divider()
    st.markdown("#### 📋 방법 1 vs 방법 2 전체 솔루션 변수 조정 요약표 (2026.06 기준)")
    comp_rows = [
        ("기존 상태 (As-Is)", "기준선", base_rwa_eok, base_cap_eok, base_div_eok, base_bis),
        ("방법 1 - 1단계", "단기 집중위험 조정", sol1_data["1단계: 단기 집중위험 조정"]["rwa"], sol1_data["1단계: 단기 집중위험 조정"]["cap"], sol1_data["1단계: 단기 집중위험 조정"]["div"], sol1_data["1단계: 단기 집중위험 조정"]["bis"]),
        ("방법 1 - 2단계", "중기 위험자산 정상화", sol1_data["2단계: 중기 위험자산 정상화"]["rwa"], sol1_data["2단계: 중기 위험자산 정상화"]["cap"], sol1_data["2단계: 중기 위험자산 정상화"]["div"], sol1_data["2단계: 중기 위험자산 정상화"]["bis"]),
        ("방법 1 - 3단계", "중기 자본확충 병행", sol1_data["3단계: 중기 자본확충 병행"]["rwa"], sol1_data["3단계: 중기 자본확충 병행"]["cap"], sol1_data["3단계: 중기 자본확충 병행"]["div"], sol1_data["3단계: 중기 자본확충 병행"]["bis"]),
        ("방법 2 - 회복", "회복 시나리오", sol2_data["회복 시나리오"]["rwa"], sol2_data["회복 시나리오"]["cap"], sol2_data["회복 시나리오"]["div"], sol2_data["회복 시나리오"]["bis"]),
        ("방법 2 - 강화", "강화 시나리오", sol2_data["강화 시나리오"]["rwa"], sol2_data["강화 시나리오"]["cap"], sol2_data["강화 시나리오"]["div"], sol2_data["강화 시나리오"]["bis"]),
        ("방법 2 - 최고", "최고 수준 회복 시나리오", sol2_data["최고 수준 회복 시나리오"]["rwa"], sol2_data["최고 수준 회복 시나리오"]["cap"], sol2_data["최고 수준 회복 시나리오"]["div"], sol2_data["최고 수준 회복 시나리오"]["bis"]),
    ]
    comp_df = pd.DataFrame(comp_rows, columns=["전략 구분", "세부 시나리오", "RWA (억원)", "자기자본 (억원)", "현금배당 (억원)", "평시 BIS (%)"])
    comp_df["RWA 변화 (억원)"] = comp_df["RWA (억원)"].apply(lambda x: f"{x - base_rwa_eok:+,.1f}")
    comp_df["BIS 개선폭 (%p)"] = comp_df["평시 BIS (%)"].apply(lambda x: f"{x - base_bis:+.2f}%p")
    comp_df["RWA (억원)"] = comp_df["RWA (억원)"].map("{:,.1f}".format)
    comp_df["자기자본 (억원)"] = comp_df["자기자본 (억원)"].map("{:,.1f}".format)
    comp_df["현금배당 (억원)"] = comp_df["현금배당 (억원)"].map("{:,.1f}".format)
    comp_df["평시 BIS (%)"] = comp_df["평시 BIS (%)"].map("{:.2f}%".format)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)


# =========================================================
# [탭 4] 솔루션 적용 후 재검증 (4단계 최종 완성)
# =========================================================
with tab4:
    st.subheader(f"✅ [결론 및 검증] 솔루션 적용 전·후 {crisis_short} 스트레스 테스트 재검증")
    st.markdown(
        f"앞서 설계한 **방법 1**과 **방법 2**를 적용한 상태에서 **{crisis_short}** 충격을 다시 가했을 때, "
        "위기 최저점(`2029.06`)의 BIS 자기자본비율이 얼마나 방어되는지 검증합니다."
    )

    ctrl_col1, ctrl_col2 = st.columns([1.2, 1.3])
    with ctrl_col1:
        view_group = st.radio(
            "비교할 솔루션 그룹 선택:",
            options=[
                "방법 1 전체 비교 (단기 → 중기 → 자본확충)",
                "방법 2 전체 비교 (회복 → 강화 → 최고 수준 회복)",
                "대표 최종안 직접 비교 (방법 1-3단계 vs 방법 2-강화·최고)"
            ],
            index=2
        )
    with ctrl_col2:
        focus_solution = st.selectbox(
            "상세 KPI 검증 대상 솔루션 선택:",
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
    v1.metric(
        label=f"적용 전 최저 BIS ({crisis_short})",
        value=f"{min_bis:.2f}%",
        delta=f"현재 기준({base_bis:.2f}%) 대비 {min_bis - base_bis:+.2f}%p",
        delta_color="normal"
    )
    v2.metric(
        label=f"적용 후 최저 BIS ({focus_solution.split('(')[0].strip()})",
        value=f"{focus_min_bis:.2f}%",
        delta=f"적용 전 최저 대비 +{defense_gain:.2f}%p 방어",
        delta_color="normal"
    )
    v3.metric(
        label="20% 건전성 마지노선 방어 여부",
        value="20% 이상 방어 성공 🎉" if focus_min_bis >= 20.0 else f"20% 기준선까지 {20.0 - focus_min_bis:.2f}%p",
        delta=f"현재 평시 BIS(22.13%) 대비 {gap_to_22:+.2f}%p",
        delta_color="off"
    )

    chart_col1, chart_col2 = st.columns([1.45, 1])

    with chart_col1:
        st.markdown(f"#### 📈 적용 전 vs 적용 후 BIS 비율 추이 ({crisis_short})")
        fig_post = go.Figure()

        # 기준선 2개 (현재 평시 22.13%, 건전성 마지노선 20.0%)
        fig_post.add_hline(
            y=base_bis, line_dash="dot", line_color="#475569",
            annotation_text=f"현재 평시 BIS ({base_bis:.2f}%)", annotation_position="top right"
        )
        fig_post.add_hline(
            y=20.0, line_dash="dash", line_color="#E67E22",
            annotation_text="건전성 마지노선 (20.00%)", annotation_position="bottom left"
        )

        # 적용 전(As-Is) 점선
        fig_post.add_trace(go.Scatter(
            x=periods, y=active_bis_list,
            mode="lines+markers+text",
            name="적용 전 (As-Is)",
            line=dict(color="#D9383A", width=3, dash="dash"),
            marker=dict(size=8, symbol="x"),
            text=[f"{v:.2f}%" for v in active_bis_list],
            textposition="bottom center"
        ))

        if "방법 1 전체" in view_group:
            traces_to_plot = [
                ("방법 1 - 1단계 (단기 집중위험 조정)", "#7FB3D5", 2.2),
                ("방법 1 - 2단계 (중기 위험자산 정상화)", "#2E86C1", 2.8),
                ("방법 1 - 3단계 (중기 자본확충 병행)", "#003366", 3.5),
            ]
        elif "방법 2 전체" in view_group:
            traces_to_plot = [
                ("방법 2 - 회복 시나리오", "#6BA5E7", 2.2),
                ("방법 2 - 강화 시나리오", "#0066CC", 2.8),
                ("방법 2 - 최고 수준 회복 시나리오", "#002B5B", 3.5),
            ]
        else:
            traces_to_plot = [
                ("방법 1 - 3단계 (중기 자본확충 병행)", "#2B7DE9", 2.8),
                ("방법 2 - 강화 시나리오", "#005BAC", 3.0),
                ("방법 2 - 최고 수준 회복 시나리오", "#002B5B", 3.6),
            ]

        for idx_t, (t_name, t_color, t_width) in enumerate(traces_to_plot):
            y_vals = post_stress_series[t_name]
            is_top = (idx_t == len(traces_to_plot) - 1)
            fig_post.add_trace(go.Scatter(
                x=periods, y=y_vals,
                mode="lines+markers+text" if is_top else "lines+markers",
                name=t_name,
                line=dict(color=t_color, width=t_width),
                marker=dict(size=8 if is_top else 6),
                text=[f"{v:.2f}%" for v in y_vals] if is_top else None,
                textposition="top center"
            ))

        fig_post.update_layout(
            height=440,
            yaxis_title="BIS 자기자본비율 (%)",
            yaxis=dict(range=[16.8, 28.5]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            plot_bgcolor="white"
        )
        fig_post.update_yaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_post, use_container_width=True)

    with chart_col2:
        st.markdown(f"#### 🏆 위기 최저점(2029.06) BIS 방어력 비교")
        bar_labels = [
            "적용 전 (As-Is)",
            "방법1-1단계(단기)",
            "방법2-회복",
            "방법1-2단계(중기)",
            "방법1-3단계(자본확충)",
            "방법2-강화",
            "방법2-최고수준회복"
        ]
        bar_keys = [
            "적용 전 (As-Is)",
            "방법 1 - 1단계 (단기 집중위험 조정)",
            "방법 2 - 회복 시나리오",
            "방법 1 - 2단계 (중기 위험자산 정상화)",
            "방법 1 - 3단계 (중기 자본확충 병행)",
            "방법 2 - 강화 시나리오",
            "방법 2 - 최고 수준 회복 시나리오"
        ]
        bar_mins = [min(post_stress_series[k]) for k in bar_keys]
        bar_colors = ["#D9383A" if v < 20.0 else ("#2B7DE9" if v < base_bis else "#003366") for v in bar_mins]

        fig_bar_min = go.Figure(go.Bar(
            x=bar_mins,
            y=bar_labels,
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.2f}% ({v - min_bis:+.2f}%p)" for v in bar_mins],
            textposition="outside"
        ))
        fig_bar_min.add_vline(x=20.0, line_dash="dash", line_color="#E67E22")
        fig_bar_min.add_vline(x=base_bis, line_dash="dot", line_color="#003366")
        fig_bar_min.update_layout(
            height=440,
            xaxis_title="위기 최저 BIS 비율 (%)",
            xaxis=dict(range=[16.0, 26.8]),
            margin=dict(l=10, r=20, t=50, b=20),
            plot_bgcolor="white"
        )
        fig_bar_min.update_xaxes(showgrid=True, gridcolor="#E2E8F0")
        st.plotly_chart(fig_bar_min, use_container_width=True)

    # 최종 핵심 결론 박스
    if "레고랜드" in selected_crisis:
        st.success(
            "🎯 **[레고랜드 사태 기준 최종 검증 결과]**\n"
            "- **적용 전(As-Is):** 조달금리 급등 및 대손비용 확대 충격으로 BIS 비율이 `22.13% → 17.72%(-4.41%p)`까지 하락합니다.\n"
            "- **방법 1(3단계 완료 시):** 단계적 RWA 감축(`-1,056억`)과 현금배당 50% 감축(`+45.1억`)을 병행하면 위기 최저 BIS가 **`19.64%` (`+1.92%p` 개선)**까지 회복됩니다.\n"
            "- **방법 2(강화·최고 수준 회복):** RWA를 `13.1%~18.6%` 선제 감축하고 배당을 유보할 경우, 극심한 위기 최저점에서도 **`20.51%`(강화) ~ `21.89%`(최고 수준 회복)**를 기록해 20% 건전성 방어선을 완벽히 사수합니다."
        )
    else:
        st.success(
            "🎯 **[저축은행 사태 기준 최종 검증 결과]**\n"
            "- **적용 전(As-Is):** 대규모 대손충당금 및 비이자손익 악화로 BIS 비율이 `22.13% → 19.22%(-2.91%p)`까지 하락합니다.\n"
            "- **방법 1(2·3단계 완료 시):** 중기 위험자산 정상화 단계(`20.71%`)부터 이미 20% 선을 안정적으로 상회하며, 3단계 완료 시 최저 BIS가 **`21.04%` (`+1.82%p` 개선)**까지 상승합니다.\n"
            "- **방법 2(강화·최고 수준 회복):** 위기 최저점에서도 **`22.23%`(강화) ~ `23.73%`(최고 수준 회복)**를 달성하여, 금융위기를 겪고도 현재 평시 BIS(`22.13%`)보다 높은 자본 건전성을 유지합니다."
        )

    st.markdown(f"#### 📋 {crisis_short} 시나리오 적용 전·후 전체 반기별 BIS 비율(%) 상세 비교표")
    full_comp_df = pd.DataFrame({"기간": periods})
    for label, series in post_stress_series.items():
        full_comp_df[label] = [f"{v:.2f}%" for v in series]
    st.dataframe(full_comp_df, use_container_width=True, hide_index=True)
