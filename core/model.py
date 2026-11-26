import numpy as np
import pandas as pd
from core.data import load_excel_sheet


# ---------------------------------------------------------
# 1. 기준 재무 상태 (2026.06 결산 기준, 단위: 억 원 / %)
# ---------------------------------------------------------
BASE_STATE = {
    "bis": 22.13,
    "capital": 3248.0,      # 억 원 (자기자본)
    "rwa": 14675.0,         # 억 원 (위험가중자산 합계)
    "bal_4": 8849.0,        # ④ 부동산담보대출 RWA 잔액 (억 원)
    "bal_5": 3082.0,        # ⑤ 기타 잔여대출 RWA 잔액 (억 원)
    "bal_6": 2744.0,        # ⑥ 기타 유가증권·유형자산 RWA 잔액 (억 원)
    "dividend": 90.2,       # 기준 연간 현금배당 (억 원)
    "reg_min_bis": 8.0,     # 규제 최저선 (%)
    "rec_bis": 11.0,        # 감독 권고선 (%)
}

# 위기 시나리오별 반기 경로 (2026.06 출발 ~ 2029.06, 7개 시점)
STRESS_PERIODS = [
    "2026.06 (출발)",
    "2026.12",
    "2027.06",
    "2027.12",
    "2028.06",
    "2028.12",
    "2029.06",
]

STRESS_SCENARIOS = {
    "레고랜드 사태": {
        "subtitle": "레고랜드 사태 — 금리 급등으로 이자비용 급증 + 부동산 PF 부실로 대손비용 증가 (2021.12 → 2024.12 업계 변화폭)",
        "reproduced_half": ["기준 시점", "2022.06 충격", "2022.12 충격", "2023.06 충격", "2023.12 충격", "2024.06 충격", "2024.12 충격"],
        "baseline_bis": [22.13, 21.68, 21.42, 20.65, 19.65, 18.58, 17.72],
        "normal_2009": [10.12, 10.45, 10.72, 10.28, 9.64, 8.85, 8.38],
        "normal_2021": [26.54, 27.62, 27.95, 28.34, 27.92, 27.60, 27.65],
        "cum_net_income_eok": -573,
        "shock_vars": pd.DataFrame({
            "구분": ["이자수익률 (%)", "이자비용률 (%)", "대손비용률 (%)", "비이자손익률 (%)"],
            "2026.06(출발)": [6.12, 3.05, 1.42, 0.28],
            "2026.12": [6.45, 3.88, 1.85, 0.12],
            "2027.06": [6.72, 4.35, 2.24, -0.05],
            "2027.12": [6.68, 4.42, 2.68, -0.18],
            "2028.06": [6.40, 4.18, 2.95, -0.22],
            "2028.12": [6.15, 3.92, 3.12, -0.15],
            "2029.06": [5.95, 3.75, 3.04, -0.10],
        }),
    },
    "저축은행 사태": {
        "subtitle": "저축은행 사태 — 부동산 PF 대규모 부실화로 대손충당금 급증 + 비이자손익 악화 (2009.12 → 2012.12 업계 변화폭)",
        "reproduced_half": ["기준 시점", "2010.06 충격", "2010.12 충격", "2011.06 충격", "2011.12 충격", "2012.06 충격", "2012.12 충격"],
        "baseline_bis": [22.13, 21.85, 21.48, 20.92, 20.28, 19.65, 19.22],
        "normal_2009": [10.12, 10.24, 10.35, 10.10, 9.82, 9.48, 9.26],
        "normal_2021": [26.54, 27.10, 27.45, 27.68, 27.40, 27.20, 27.25],
        "cum_net_income_eok": -384,
        "shock_vars": pd.DataFrame({
            "구분": ["이자수익률 (%)", "이자비용률 (%)", "대손비용률 (%)", "비이자손익률 (%)"],
            "2026.06(출발)": [6.12, 3.05, 1.42, 0.28],
            "2026.12": [6.05, 3.18, 1.92, -0.14],
            "2027.06": [5.92, 3.24, 2.38, -0.35],
            "2027.12": [5.78, 3.20, 2.75, -0.48],
            "2028.06": [5.65, 3.12, 2.98, -0.52],
            "2028.12": [5.58, 3.04, 3.05, -0.44],
            "2029.06": [5.52, 2.98, 2.92, -0.36],
        }),
    },
}


def get_excel_stress_series():
    """엑셀 파일이 존재하면 실제 시트 수치를 반영하고, 없으면 기본 내장 시계열 반환."""
    df_raw = load_excel_sheet()
    if df_raw is None:
        return STRESS_SCENARIOS
    try:
        base_bis = round(float(df_raw.iloc[42, 1]), 2)
        bis_sb = [base_bis] + [round(float(x), 2) for x in df_raw.iloc[42, 2:8]]
        bis_lg = [base_bis] + [round(float(x), 2) for x in df_raw.iloc[42, 8:14]]
        net_lg = round(sum(float(df_raw.iloc[41, c]) for c in range(8, 14)) / 1e8)
        net_sb = round(sum(float(df_raw.iloc[41, c]) for c in range(2, 8)) / 1e8)

        scenarios = {
            "레고랜드 사태": dict(STRESS_SCENARIOS["레고랜드 사태"]),
            "저축은행 사태": dict(STRESS_SCENARIOS["저축은행 사태"]),
        }
        scenarios["레고랜드 사태"]["baseline_bis"] = bis_lg
        scenarios["레고랜드 사태"]["cum_net_income_eok"] = int(net_lg)
        scenarios["저축은행 사태"]["baseline_bis"] = bis_sb
        scenarios["저축은행 사태"]["cum_net_income_eok"] = int(net_sb)
        return scenarios
    except Exception:
        return STRESS_SCENARIOS


# ---------------------------------------------------------
# 2. 전략 프리셋 정의 (P4 & P5 공통 사용)
# ---------------------------------------------------------
STRATEGY_PRESETS = {
    "현상 유지": {
        "cut_4": 0.0,
        "cut_5": 0.0,
        "cut_6": 0.0,
        "dividend": 90.2,
        "years": 3,
        "desc": "기존 부동산담보대출 편중 및 연간 90.2억 원 현금배당 정책 유지",
    },
    "회복": {
        "cut_4": 650.0,
        "cut_5": 0.0,
        "cut_6": 202.0,
        "dividend": 76.17,
        "years": 1,
        "desc": "솔루션 1 · 기본 회복 목표 — 배당 정상화(76.2억) 및 RWA 852억 원 감축 (2025.06 수준 회복)",
    },
    "강화": {
        "cut_4": 1467.0,
        "cut_5": 0.0,
        "cut_6": 455.0,
        "dividend": 76.17,
        "years": 1,
        "desc": "솔루션 1 · 방어력 강화 — 배당 정상화(76.2억) 및 RWA 1,922억 원 감축 (2024.06 수준 달성)",
    },
    "최고 수준 회복": {
        "cut_4": 2083.0,
        "cut_5": 0.0,
        "cut_6": 646.0,
        "dividend": 76.17,
        "years": 1,
        "desc": "솔루션 1 · 최고 건전성 목표 — 배당 정상화(76.2억) 및 RWA 2,729억 원 감축 (2021.06 최고 BIS 회복)",
    },
    "단기 집중위험 조정": {
        "cut_4": 486.0,
        "cut_5": 0.0,
        "cut_6": 0.0,
        "dividend": 90.2,
        "years": 3,
        "desc": "솔루션 2 · 1단계 단기 처방 — 고위험 부동산담보대출(④) 486억 원 즉시 축소",
    },
    "중기 위험자산 정상화": {
        "cut_4": 486.0,
        "cut_5": 0.0,
        "cut_6": 570.0,
        "dividend": 90.2,
        "years": 3,
        "internal_bonus": 147.0,
        "desc": "솔루션 2 · 단계별 리스크 관리 — 기여 4·6 위험 관리 + 3년간 기준 배당 유지",
    },
    "중기 자본확충 병행": {
        "cut_4": 486.0,
        "cut_5": 0.0,
        "cut_6": 570.0,
        "dividend": 45.1,
        "years": 3,
        "internal_bonus": 147.0,
        "desc": "솔루션 2 · 3단계 종합 처방 — RWA 1,056억 원 감축 + 현금배당 50% 감축(사내유보 확대)",
    },
}


# ---------------------------------------------------------
# 3. 전략 시뮬레이터 및 스트레스 테스트 연동 계산 엔진
# ---------------------------------------------------------
def simulate_strategy(cut_4: float, cut_5: float, cut_6: float, dividend: float, years: int, internal_bonus: float = 0.0):
    """RWA 감축과 배당 조정을 반영해 평상시 목표 BIS와 위기 시 최저 BIS를 산출."""
    total_rwa_cut = float(cut_4 + cut_5 + cut_6)
    new_rwa = max(1000.0, BASE_STATE["rwa"] - total_rwa_cut)

    div_saved = max(0.0, BASE_STATE["dividend"] - float(dividend)) * int(years)
    cap_gain = div_saved + float(internal_bonus)
    new_cap = BASE_STATE["capital"] + cap_gain

    target_bis = (new_cap / new_rwa) * 100.0
    bis_diff = target_bis - BASE_STATE["bis"]
    re_cut_pct = (float(cut_4) / BASE_STATE["bal_4"]) * 100.0

    # 위기 시나리오별 경로 산출 (출발선 상승분 + RWA 축소에 따른 손실 민감도 완화 반영)
    scenarios = get_excel_stress_series()
    stress_paths = {}
    stress_mins = {}
    stress_min_diffs = {}

    rwa_ratio = new_rwa / BASE_STATE["rwa"]
    for sc_name, sc_data in scenarios.items():
        base_path = sc_data["baseline_bis"]
        base_min = min(base_path)
        new_path = [round(target_bis, 2)]
        for t in range(1, len(base_path)):
            cum_drop = base_path[0] - base_path[t]
            # RWA 감축 비율에 비례하여 위기 손실 충격이 완화됨
            adjusted_drop = cum_drop * (0.45 + 0.55 * rwa_ratio)
            new_path.append(round(target_bis - adjusted_drop, 2))
        stress_paths[sc_name] = new_path
        stress_mins[sc_name] = min(new_path)
        stress_min_diffs[sc_name] = round(min(new_path) - base_min, 2)

    return {
        "target_bis": round(target_bis, 2),
        "bis_diff": round(bis_diff, 2),
        "new_rwa": round(new_rwa),
        "rwa_cut": round(total_rwa_cut),
        "new_cap": round(new_cap),
        "cap_gain": round(cap_gain),
        "re_cut_pct": round(re_cut_pct, 1),
        "stress_paths": stress_paths,
        "stress_mins": stress_mins,
        "stress_min_diffs": stress_min_diffs,
    }


def reverse_calculate_bis(target_bis: float, target_dividend: float, years: int = 1):
    """목표 BIS(%)와 연간 배당(억원)으로 필요한 RWA 감축액을 계산하고 ④:⑥ 잔액 비율로 배분."""
    div_saved = max(0.0, BASE_STATE["dividend"] - float(target_dividend)) * int(years)
    adj_cap = BASE_STATE["capital"] + div_saved
    target_rwa = adj_cap / (float(target_bis) / 100.0)
    needed_cut = max(0.0, BASE_STATE["rwa"] - target_rwa)

    bal_4 = BASE_STATE["bal_4"]
    bal_6 = BASE_STATE["bal_6"]
    share_4 = bal_4 / (bal_4 + bal_6)

    cut_4 = needed_cut * share_4
    cut_6 = needed_cut * (1.0 - share_4)

    return {
        "needed_cut": round(needed_cut),
        "cut_4": round(cut_4),
        "cut_6": round(cut_6),
        "adj_cap": round(adj_cap),
        "target_rwa": round(target_rwa),
    }


def get_all_strategy_comparison():
    """P4 우측 덤벨 차트용: 현상 유지 + 6개 전략의 두 시나리오 최저 BIS 비교 데이터."""
    rows = []
    for name, params in STRATEGY_PRESETS.items():
        res = simulate_strategy(
            params["cut_4"],
            params["cut_5"],
            params["cut_6"],
            params["dividend"],
            params["years"],
            params.get("internal_bonus", 0.0),
        )
        rows.append({
            "전략": name,
            "레고랜드 사태": res["stress_mins"]["레고랜드 사태"],
            "저축은행 사태": res["stress_mins"]["저축은행 사태"],
        })
    return pd.DataFrame(rows)
