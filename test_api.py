"""
test_api.py — Pytest test suite for the Y-Strainer Pressure Drop Calculator API.

All 14 cases are sourced directly from validate_screenshots.py and cross-checked
against Forbes Marshall software screenshots.
Tolerance: 1% relative for ΔP; 0.5% for all other values.

Run:
    pip install -r requirements.txt
    pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _rel_err(actual: float, expected: float) -> float:
    return abs(actual - expected) / abs(expected)


def _check(result: dict, key: str, expected: float, tol: float, label: str) -> None:
    actual = result[key]
    err = _rel_err(actual, expected)
    assert err <= tol, (
        f"[{label}] {key}: got {actual:.6f}, expected {expected:.6f}, "
        f"rel_err={err*100:.4f}% (limit={tol*100:.1f}%)"
    )


def _run(case: dict) -> None:
    resp = client.post("/calculate", json=case["input"])
    assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text}"
    data = resp.json()
    name = case["id"]
    tol_geo = 0.005   # 0.5%
    tol_dp  = 0.010   # 1.0%

    # Shared values
    for key, val in case.get("shared", {}).items():
        _check(data, key, val, tol_geo, name)

    # Per-condition values
    for key, val in case.get("clean", {}).items():
        tol = tol_dp if "delta_P" in key else tol_geo
        _check(data["clean_100pct"], key, val, tol, f"{name}/clean")

    for key, val in case.get("clogged", {}).items():
        tol = tol_dp if "delta_P" in key else tol_geo
        _check(data["clogged_50pct"], key, val, tol, f"{name}/clogged")


# ── Test cases — 14 validated screenshots ─────────────────────────────────────
# Values sourced verbatim from validate_screenshots.py

CASES = [
    # ─────────────────────────────────────────────────────────────────────────
    # SS1  ND031-PZSY-0303 | FMSTR51/52CL600 | Size 1 | LOW PRES STEAM | kg/hr
    # Mesh 40×SWG38: Q=62.7%, D=0.05 cm | Perf 51%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS1-ND031-PZSY-0303",
        "input": {
            "rho": 951.0, "mu_cP": 0.248, "W": 165, "flow_unit": "kg/hr",
            "D_pipe_cm": 2.5, "D_screen_cm": 2.6, "L_cm": 8.0,
            "D_open_cm": 0.05, "Q_pct": 62.7, "P_pct": 51,
        },
        "shared": {
            "alpha": 0.31977,
            "A_pipe_cm2": 4.909375,
            "A_screen_gross_cm2": 65.3536,
            "Q_vol_cm3_s": 173.501577,
        },
        "clean": {
            "net_surface_area_cm2": 20.89812,
            "screening_area_ratio": 4.25678,
            "V_cm_s": 2.65481,
            "Re": 159.18239,
            "C": 0.9,
            "K": 10.83911,
            "delta_P_cm_wc": 0.037029,
            "delta_P_in_wc": 0.014579,
            "delta_P_kg_cm2": 3.7029e-5,
        },
        "clogged": {
            "net_surface_area_cm2": 10.44906,
            "screening_area_ratio": 2.12839,
            "V_cm_s": 5.30963,
            "Re": 318.36479,
            "C": 1.01,
            "K": 8.60668,
            "delta_P_cm_wc": 0.11761,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS2  ND031-PZSY-0305 | FMSTR51/52CL600 | Size 1 | m3/hr input
    # Mesh 40×SWG38: Q=62.7%, D=0.05 cm | Perf 51% | rho=0.951, mu=0.248
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS2-ND031-PZSY-0305-m3hr",
        "input": {
            "rho": 951.0, "mu_cP": 0.248, "W": 0.165, "flow_unit": "m3/hr",
            "D_pipe_cm": 2.5, "D_screen_cm": 2.6, "L_cm": 8.0,
            "D_open_cm": 0.05, "Q_pct": 62.7, "P_pct": 51,
        },
        "shared": {
            "alpha": 0.31977,
            "A_pipe_cm2": 4.909375,
            "A_screen_gross_cm2": 65.3536,
            "Q_vol_cm3_s": 45.83205,
        },
        "clean": {
            "screening_area_ratio": 4.25678,
            "V_cm_s": 0.70129,
            "Re": 42.04951,
            "C": 0.6,
            "K": 24.388,
            "delta_P_cm_wc": 0.005814,
        },
        "clogged": {
            "V_cm_s": 1.40259,
            "Re": 84.09901,
            "C": 0.75,
            "K": 15.60832,
            "delta_P_cm_wc": 0.014883,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS3  ND031-PZSY-0309 | FMSTR54-T | Size 2 | CAUSTIC 10% | kg/hr
    # Mesh 40×SWG34: Q=39.9%, D=0.04 cm | Perf 51%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS3-ND031-PZSY-0309-Caustic",
        "input": {
            "rho": 1100.0, "mu_cP": 14.0, "W": 4000, "flow_unit": "kg/hr",
            "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
            "D_open_cm": 0.04, "Q_pct": 39.9, "P_pct": 51,
        },
        "shared": {
            "alpha": 0.20349,
            "A_pipe_cm2": 19.6375,
            "A_screen_gross_cm2": 247.14972,
            "Q_vol_cm3_s": 3636.36364,
        },
        "clean": {
            "net_surface_area_cm2": 50.29250,
            "screening_area_ratio": 2.56104,
            "V_cm_s": 14.71320,
            "Re": 22.72421,
            "C": 0.45,
            "K": 114.32009,
            "delta_P_cm_wc": 13.874924,
        },
        "clogged": {
            "V_cm_s": 29.42640,
            "Re": 45.44842,
            "C": 0.6,
            "K": 64.30505,
            "delta_P_cm_wc": 31.218578,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS4  ND031-PZSY-1304 | FMSTR51/52CL600 | Size 1.5 | LOW PRES STEAM
    # Mesh 40×SWG38: Q=62.7%, D=0.05 cm | Perf 51% | W=1050 kg/hr
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS4-ND031-PZSY-1304-Size1.5",
        "input": {
            "rho": 951.0, "mu_cP": 0.248, "W": 1050, "flow_unit": "kg/hr",
            "D_pipe_cm": 4.0, "D_screen_cm": 4.8, "L_cm": 12.0,
            "D_open_cm": 0.05, "Q_pct": 62.7, "P_pct": 51,
        },
        "shared": {
            "alpha": 0.31977,
            "A_pipe_cm2": 12.568,
            "A_screen_gross_cm2": 180.9792,
            "Q_vol_cm3_s": 1104.10095,
        },
        "clean": {
            "net_surface_area_cm2": 57.87172,
            "screening_area_ratio": 4.60469,
            "V_cm_s": 6.10071,
            "Re": 365.79793,
            "C": 1.04,
            "K": 8.11731,
            "delta_P_cm_wc": 0.146438,
        },
        "clogged": {
            "V_cm_s": 12.20141,
            "Re": 731.59586,
            "C": 1.25,
            "K": 5.61899,
            "delta_P_cm_wc": 0.405471,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS5  ND031-PZSY-1311 | FMSTR54-T | Size 3 | SUSPENDING AGENT | No Mesh
    # No Mesh (Q=100%), D_open=0.2 cm | Perf 40% | rho=1.025, mu=450 cP
    # Re < 21: C = sqrt(Re) / 10
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS5-ND031-PZSY-1311-NoMesh-mu450",
        "input": {
            "rho": 1025.0, "mu_cP": 450.0, "W": 9225, "flow_unit": "kg/hr",
            "D_pipe_cm": 8.0, "D_screen_cm": 9.0, "L_cm": 18.7,
            "D_open_cm": 0.2, "Q_pct": 100.0, "P_pct": 40.0,
        },
        "shared": {
            "alpha": 0.4,
            "A_pipe_cm2": 50.272,
            "A_screen_gross_cm2": 528.7986,
            "Q_vol_cm3_s": 9000.0,
        },
        "clean": {
            "net_surface_area_cm2": 211.51944,
            "screening_area_ratio": 4.2075,
            "V_cm_s": 17.01971,
            "Re": 1.93836,
            "K": 270.84752,
            "delta_P_cm_wc": 40.987757,
        },
        "clogged": {
            "V_cm_s": 34.03942,
            "Re": 3.87671,
            "K": 135.42411,
            "delta_P_cm_wc": 81.975726,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS6  ND031-PZSY-1312 | FMSTR54-T | Size 3 | SUSPENDING AGENT | No Mesh
    # No Mesh (Q=100%), D_open=0.2 cm | Perf 40% | rho=1.025, mu=230 cP
    # Re < 21: C = sqrt(Re) / 10
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS6-ND031-PZSY-1312-NoMesh-mu230",
        "input": {
            "rho": 1025.0, "mu_cP": 230.0, "W": 10250, "flow_unit": "kg/hr",
            "D_pipe_cm": 8.0, "D_screen_cm": 9.0, "L_cm": 18.7,
            "D_open_cm": 0.2, "Q_pct": 100.0, "P_pct": 40.0,
        },
        "shared": {
            "alpha": 0.4,
            "A_pipe_cm2": 50.272,
            "A_screen_gross_cm2": 528.7986,
            "Q_vol_cm3_s": 10000.0,
        },
        "clean": {
            "net_surface_area_cm2": 211.51944,
            "screening_area_ratio": 4.2075,
            "V_cm_s": 18.91079,
            "Re": 4.21382,
            "K": 124.59004,
            "delta_P_cm_wc": 23.277032,
        },
        "clogged": {
            "V_cm_s": 37.82158,
            "Re": 8.42764,
            "K": 62.29502,
            "delta_P_cm_wc": 46.554063,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS7  ND031-PZSY-1319 | FMSTR54-T | Size 2 | LOW PRES STEAM | W=4415
    # Mesh 40×SWG34: Q=39.9%, D=0.04 cm | Perf 12mm×14mm → P=67%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS7-ND031-PZSY-1319",
        "input": {
            "rho": 951.0, "mu_cP": 0.245, "W": 4415, "flow_unit": "kg/hr",
            "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
            "D_open_cm": 0.04, "Q_pct": 39.9, "P_pct": 67.0,
        },
        "shared": {
            "alpha": 0.26733,
            "A_pipe_cm2": 19.6375,
            "A_screen_gross_cm2": 247.14972,
            "Q_vol_cm3_s": 4642.48160,
        },
        "clean": {
            "net_surface_area_cm2": 66.07053,
            "screening_area_ratio": 3.36451,
            "V_cm_s": 18.78409,
            "Re": 1090.98001,
            "C": 1.29,
            "K": 7.8077,
            "delta_P_cm_wc": 1.335318,
        },
        "clogged": {
            "V_cm_s": 37.56817,
            "Re": 2181.96002,
            "C": 1.39,
            "K": 6.7247,
            "delta_P_cm_wc": 4.600389,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS8  ND031-PZSY-1616 | FMSTR54-T | Size 4 | LOW PRES STEAM | W=28443
    # Mesh 40×SWG36: Q=48.4%, D=0.044 cm | Perf 12mm×14mm → P=67%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS8-ND031-PZSY-1616-W28443",
        "input": {
            "rho": 998.0, "mu_cP": 1.0, "W": 28443, "flow_unit": "kg/hr",
            "D_pipe_cm": 10.0, "D_screen_cm": 11.8, "L_cm": 22.2,
            "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 67.0,
        },
        "shared": {
            "alpha": 0.32428,
            "A_pipe_cm2": 78.55,
            "A_screen_gross_cm2": 823.07832,
            "Q_vol_cm3_s": 28500.0,
        },
        "clean": {
            "net_surface_area_cm2": 266.90784,
            "screening_area_ratio": 3.39794,
            "V_cm_s": 34.62611,
            "Re": 468.88544,
            "C": 1.12,
            "K": 6.78376,
            "delta_P_cm_wc": 4.137228,
        },
        "clogged": {
            "V_cm_s": 69.25222,
            "Re": 937.77089,
            "C": 1.28,
            "K": 5.19381,
            "delta_P_cm_wc": 12.670244,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS9  ND031-PZSY-4311 | FMSTR54-T | Size 2 | WATER | W=3932
    # Mesh 40×SWG36: Q=48.4%, D=0.044 cm | Perf 6mm×8mm → P=51%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS9-ND031-PZSY-4311-Water",
        "input": {
            "rho": 983.0, "mu_cP": 0.5, "W": 3932, "flow_unit": "kg/hr",
            "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
            "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0,
        },
        "shared": {
            "alpha": 0.24684,
            "A_pipe_cm2": 19.6375,
            "A_screen_gross_cm2": 247.14972,
            "Q_vol_cm3_s": 4000.0,
        },
        "clean": {
            "net_surface_area_cm2": 61.00644,
            "screening_area_ratio": 3.10663,
            "V_cm_s": 16.18452,
            "Re": 567.17949,
            "C": 1.18,
            "K": 11.06886,
            "delta_P_cm_wc": 1.452637,
        },
        "clogged": {
            "V_cm_s": 32.36904,
            "Re": 1134.35899,
            "C": 1.29,
            "K": 9.26163,
            "delta_P_cm_wc": 4.861851,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS10  ND031-PZSY-4312 | FMSTR54-T | Size 2 | WATER Rating300 | W=3953
    # Mesh 40×SWG36: Q=48.4%, D=0.044 cm | Perf 6mm×8mm → P=51%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS10-ND031-PZSY-4312-Water-W3953",
        "input": {
            "rho": 941.0, "mu_cP": 0.3, "W": 3953, "flow_unit": "kg/hr",
            "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
            "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0,
        },
        "shared": {
            "alpha": 0.24684,
            "A_pipe_cm2": 19.6375,
            "A_screen_gross_cm2": 247.14972,
            "Q_vol_cm3_s": 4200.85016,
        },
        "clean": {
            "screening_area_ratio": 3.10663,
            "V_cm_s": 16.99719,
            "Re": 950.3478,
            "C": 1.29,
            "K": 9.26163,
            "delta_P_cm_wc": 1.283312,
        },
        "clogged": {
            "V_cm_s": 33.99438,
            "Re": 1900.69561,
            "C": 1.37,
            "K": 8.21156,
            "delta_P_cm_wc": 4.551247,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS11  ND031-PZSY-4312-1 | FMSTR54-T | Size 2 | WATER | W=5100
    # Mesh 40×SWG36: Q=48.4%, D=0.044 cm | Perf 12mm×14mm → P=67%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS11-ND031-PZSY-4312-1-W5100",
        "input": {
            "rho": 941.0, "mu_cP": 0.3, "W": 5100, "flow_unit": "kg/hr",
            "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
            "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 67.0,
        },
        "shared": {
            "alpha": 0.32428,
            "A_pipe_cm2": 19.6375,
            "A_screen_gross_cm2": 247.14972,
            "Q_vol_cm3_s": 5419.76621,
        },
        "clean": {
            "net_surface_area_cm2": 80.14571,
            "screening_area_ratio": 4.08126,
            "V_cm_s": 21.92908,
            "Re": 933.3001,
            "C": 1.28,
            "K": 5.19381,
            "delta_P_cm_wc": 1.197892,
        },
        "clogged": {
            "V_cm_s": 43.85816,
            "Re": 1866.60019,
            "C": 1.37,
            "K": 4.53383,
            "delta_P_cm_wc": 4.1827,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS12  ND031-PZSY-4312-2 | FMSTR54-T | Size 2 | WATER | W=5600
    # Mesh 40×SWG34: Q=39.9%, D=0.04 cm | Perf 12mm×14mm → P=67%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS12-ND031-PZSY-4312-2-W5600",
        "input": {
            "rho": 983.0, "mu_cP": 0.3, "W": 5600, "flow_unit": "kg/hr",
            "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
            "D_open_cm": 0.04, "Q_pct": 39.9, "P_pct": 67.0,
        },
        "shared": {
            "alpha": 0.26733,
            "A_pipe_cm2": 19.6375,
            "A_screen_gross_cm2": 247.14972,
            "Q_vol_cm3_s": 5696.84639,
        },
        "clean": {
            "net_surface_area_cm2": 66.07053,
            "screening_area_ratio": 3.36451,
            "V_cm_s": 23.05018,
            "Re": 1130.10538,
            "C": 1.29,
            "K": 7.8077,
            "delta_P_cm_wc": 2.078387,
        },
        "clogged": {
            "V_cm_s": 46.10037,
            "Re": 2260.21076,
            "C": 1.4,
            "K": 6.62898,
            "delta_P_cm_wc": 7.05846,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS13  ND031-PZSY-4312-2 | FMSTR54-T | Size 2 | WATER | W=7250
    # Mesh 40×SWG39 (≈SWG38): Q=62.7%, D=0.05 cm | Perf 12mm×14mm → P=67%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS13-ND031-PZSY-4312-2-W7250",
        "input": {
            "rho": 983.0, "mu_cP": 0.3, "W": 7250, "flow_unit": "kg/hr",
            "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
            "D_open_cm": 0.05, "Q_pct": 62.7, "P_pct": 67.0,
        },
        "shared": {
            "alpha": 0.42009,
            "A_pipe_cm2": 19.6375,
            "A_screen_gross_cm2": 247.14972,
            "Q_vol_cm3_s": 7375.38149,
        },
        "clean": {
            "net_surface_area_cm2": 103.82513,
            "screening_area_ratio": 5.28708,
            "V_cm_s": 29.84176,
            "Re": 1163.81591,
            "C": 1.3,
            "K": 2.76125,
            "delta_P_cm_wc": 1.231995,
        },
        "clogged": {
            "V_cm_s": 59.68351,
            "Re": 2327.63182,
            "C": 1.4,
            "K": 2.38087,
            "delta_P_cm_wc": 4.249119,
        },
    },
    # ─────────────────────────────────────────────────────────────────────────
    # SS14  ND031-PZSY-1616 | FMSTR54-T | Size 4 | LOW PRES STEAM | W=10200
    # Mesh 40×SWG38: Q=57.8%(≈SWG38 alt), D=0.048 cm | Perf 12mm×14mm → P=67%
    # ─────────────────────────────────────────────────────────────────────────
    {
        "id": "SS14-ND031-PZSY-1616-W10200",
        "input": {
            "rho": 998.0, "mu_cP": 1.0, "W": 10200, "flow_unit": "kg/hr",
            "D_pipe_cm": 10.0, "D_screen_cm": 11.8, "L_cm": 22.2,
            "D_open_cm": 0.048, "Q_pct": 57.8, "P_pct": 67.0,
        },
        "shared": {
            "alpha": 0.38726,
            "A_pipe_cm2": 78.55,
            "A_screen_gross_cm2": 823.07832,
            "Q_vol_cm3_s": 10220.44088,
        },
        "clean": {
            "net_surface_area_cm2": 318.74531,
            "screening_area_ratio": 4.05787,
            "V_cm_s": 12.41734,
            "Re": 153.60226,
            "C": 0.9,
            "K": 6.99751,
            "delta_P_cm_wc": 0.548823,
        },
        "clogged": {
            "V_cm_s": 24.83467,
            "Re": 307.20452,
            "C": 1.01,
            "K": 5.5563,
            "delta_P_cm_wc": 1.743148,
        },
    },
]


# ── Parametrized test ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_calculate(case: dict) -> None:
    _run(case)


# ── Quick smoke test for lookup endpoints ──────────────────────────────────────

def test_lookup_meshes() -> None:
    resp = client.get("/lookup/meshes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert "mesh" in data[0] and "opening_mm" in data[0]


def test_lookup_perforations() -> None:
    resp = client.get("/lookup/perforations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert "description" in data[0] and "open_area_pct" in data[0]


def test_lookup_strainer_models() -> None:
    resp = client.get("/lookup/strainer-models")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert "model" in data[0] and "screen_D_mm" in data[0]


def test_from_selection_basic() -> None:
    """Smoke test the from-selection endpoint using SS7-equivalent inputs.

    FMSTR54-T size 2: D_pipe=50mm, D_screen=57mm, L=138mm (from catalogue)
    mesh=40, swg=34 → Q=39.9%, D_open=0.4mm
    perf='Perf.: 12mm x Pitch: 14mm' → P=67%
    """
    resp = client.post("/calculate/from-selection", json={
        "rho": 0.951, "mu_cP": 0.245, "W": 4415, "flow_unit": "kg/hr",
        "model": "FMSTR54-T", "nps": "2",
        "mesh": 40, "swg": 34,
        "perforation": "Perf.: 12mm x Pitch: 14mm",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "clean_100pct" in data
    assert data["clean_100pct"]["delta_P_cm_wc"] > 0


def test_invalid_strainer_model() -> None:
    resp = client.post("/calculate/from-selection", json={
        "rho": 1000.0, "mu_cP": 1.0, "W": 100, "flow_unit": "kg/hr",
        "model": "INVALID-MODEL", "nps": "2",
        "mesh": 40, "swg": 38,
        "perforation": "Perf. : 12mm x Pitch: 14mm",
    })
    assert resp.status_code == 404


def test_no_mesh_requires_d_open_override() -> None:
    resp = client.post("/calculate/from-selection", json={
        "rho": 1025.0, "mu_cP": 450.0, "W": 1000, "flow_unit": "kg/hr",
        "model": "FMSTR54-T", "nps": "3",
        "mesh": 0, "swg": 0,
        "perforation": "Perf. : 4mm x Pitch: 6mm",
        # D_open_cm_override intentionally omitted
    })
    assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# BASKET STRAINER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

import math as _math
from calculator import lookup_C as _lookup_C


# ── Unit tests: lookup_C fractional-Re boundary fix ───────────────────────────

def test_lookup_c_re_below_21_uses_formula() -> None:
    """Re < 21 must use C = sqrt(Re)/10, not the table."""
    for re in [0.5, 1.0, 4.0, 10.0, 20.0, 20.9]:
        assert abs(_lookup_C(re) - _math.sqrt(re) / 10.0) < 1e-10, f"Re={re}"


def test_lookup_c_re_at_21_uses_table() -> None:
    """Re = 21 is the first table entry — must return the table value exactly, not the formula."""
    c = _lookup_C(21.0)
    assert c == 0.45  # (21, 25, 0.45) from C_VALUE_TABLE
    # formula would give sqrt(21)/10 ≈ 0.4583; table gives 0.45 exactly
    assert c == 0.45


def test_lookup_c_fractional_re_89_8925() -> None:
    """Re=89.8925 was the actual production failure; int(89.8925)=89 → C=0.75."""
    assert _lookup_C(89.8925) == 0.75


def test_lookup_c_fractional_re_near_each_boundary() -> None:
    """All fractional Re values that could slip between integer table bounds."""
    boundary_pairs = [
        (89.0,  0.75),   # range (80, 89)
        (89.1,  0.75),   # still int=89, same range
        (89.9,  0.75),   # still int=89, same range
        (90.0,  0.77),   # int=90, range (90, 99)
        (90.5,  0.77),
        (99.9,  0.77),   # int=99, range (90, 99)
        (100.0, 0.80),   # int=100, range (100, 124)
        (174.9, 0.90),   # int=174, range (150, 174)
        (175.0, 0.95),   # int=175, range (175, 200)
        (200.9, 0.95),   # int=200, range (175, 200)
        (201.0, 1.00),   # int=201, range (201, 300)
    ]
    for re, expected_c in boundary_pairs:
        got = _lookup_C(re)
        assert got == expected_c, f"Re={re}: expected C={expected_c}, got C={got}"


def test_lookup_c_no_exception_for_all_integer_re() -> None:
    """Every integer Re from 21 to 6000 must resolve without raising."""
    for re in range(21, 6001):
        _lookup_C(float(re))  # must not raise


# ── /lookup/pipe-schedules endpoint ───────────────────────────────────────────

def test_lookup_pipe_schedules_returns_200() -> None:
    resp = client.get("/lookup/pipe-schedules")
    assert resp.status_code == 200


def test_lookup_pipe_schedules_structure() -> None:
    resp = client.get("/lookup/pipe-schedules")
    data = resp.json()
    assert len(data) > 0
    first = data[0]
    assert "nps" in first
    assert "schedule" in first
    assert "id_mm" in first
    assert isinstance(first["id_mm"], (int, float))
    assert isinstance(first["nps"], str)
    assert isinstance(first["schedule"], str)


def test_lookup_pipe_schedules_no_blank_or_dash() -> None:
    """Blank, '-', '–', '—' schedule values must be excluded from the API."""
    resp = client.get("/lookup/pipe-schedules")
    data = resp.json()
    forbidden = {"-", "\u2013", "\u2014", ""}
    for entry in data:
        assert entry["schedule"] not in forbidden, (
            f"Blank/dash schedule for NPS={entry['nps']}: '{entry['schedule']}'"
        )


def test_lookup_pipe_schedules_all_ids_positive() -> None:
    """Every pipe ID returned by the API must be > 0."""
    resp = client.get("/lookup/pipe-schedules")
    data = resp.json()
    for entry in data:
        assert entry["id_mm"] > 0, (
            f"Non-positive ID for NPS={entry['nps']} sch={entry['schedule']}: {entry['id_mm']}"
        )


def test_lookup_pipe_schedules_nps_half_inch_has_both_named_and_numeric() -> None:
    """NPS 1/2 must expose both named (STD, XS, XXS) and numeric schedules."""
    resp = client.get("/lookup/pipe-schedules")
    data = resp.json()
    nps_half = [e for e in data if e["nps"] == "1/2"]
    assert len(nps_half) > 0, "No schedule entries for NPS 1/2"
    schedules = {e["schedule"] for e in nps_half}
    assert len(schedules & {"STD", "XS", "XXS"}) > 0, (
        f"Missing named schedules for 1/2\": got {schedules}"
    )
    assert len(schedules & {"5", "10", "30", "40", "80", "160"}) > 0, (
        f"Missing numeric schedules for 1/2\": got {schedules}"
    )


def test_lookup_pipe_schedules_nps_three_quarter_present() -> None:
    """NPS 3/4 (or unicode fraction variant) must have schedule entries."""
    resp = client.get("/lookup/pipe-schedules")
    data = resp.json()
    # Excel may encode as "3/4" or "3⁄4" (unicode fraction slash)
    entries = [e for e in data if e["nps"] in ("3/4", "3\u20444")]
    assert len(entries) > 0, "No schedule entries for 3/4 NPS"


def test_lookup_pipe_schedules_has_multiple_nps_sizes() -> None:
    """API must return schedules for more than one NPS size."""
    resp = client.get("/lookup/pipe-schedules")
    data = resp.json()
    nps_set = {e["nps"] for e in data}
    assert len(nps_set) >= 2, f"Expected ≥2 NPS sizes, got: {nps_set}"


# ── Basket strainer — calculation smoke tests ─────────────────────────────────

def test_basket_end_to_end_schedule_to_calculate() -> None:
    """Fetch schedule for any NPS with STD entry, derive pipe ID, run /calculate."""
    resp = client.get("/lookup/pipe-schedules")
    assert resp.status_code == 200
    schedules = resp.json()
    std_entries = [e for e in schedules if e["schedule"] == "STD"]
    assert len(std_entries) > 0, "No STD schedule entries found"

    entry = std_entries[0]
    d_pipe_cm = entry["id_mm"] / 10.0

    resp = client.post("/calculate", json={
        "rho": 998.0,
        "mu_cP": 1.0,
        "W": 8000,
        "flow_unit": "kg/hr",
        "D_pipe_cm": d_pipe_cm,
        "D_screen_cm": d_pipe_cm * 1.15,
        "L_cm": 20.0,
        "D_open_cm": 0.05,
        "Q_pct": 62.7,
        "P_pct": 51.0,
        "tag_no": "BSKT-001",
        "fluid_name": "Water",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["tag_no"] == "BSKT-001"
    assert data["fluid_name"] == "Water"
    assert data["clean_100pct"]["delta_P_kg_cm2"] > 0
    assert data["clogged_50pct"]["delta_P_kg_cm2"] > data["clean_100pct"]["delta_P_kg_cm2"]


def test_basket_re_fractional_boundary_does_not_500() -> None:
    """Confirm the Re≈89.89 production failure is resolved (was HTTP 500 before fix)."""
    # ss2 case re-used with reduced flow to drive Re into the 80–90 range
    resp = client.post("/calculate", json={
        "rho": 998.0,
        "mu_cP": 1.2,
        "W": 3200,
        "flow_unit": "kg/hr",
        "D_pipe_cm": 4.0,
        "D_screen_cm": 4.8,
        "L_cm": 18.0,
        "D_open_cm": 0.05,
        "Q_pct": 62.7,
        "P_pct": 51.0,
    })
    assert resp.status_code == 200, f"Unexpected HTTP {resp.status_code}: {resp.text}"


def test_basket_high_viscosity_re_below_21() -> None:
    """Very viscous fluid → Re < 21 for both conditions → C = sqrt(Re)/10 path."""
    resp = client.post("/calculate", json={
        "rho": 1070.0,
        "mu_cP": 350.0,
        "W": 800,
        "flow_unit": "kg/hr",
        "D_pipe_cm": 3.0,
        "D_screen_cm": 3.5,
        "L_cm": 12.0,
        "D_open_cm": 0.2,
        "Q_pct": 100.0,
        "P_pct": 40.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    c50  = data["clogged_50pct"]
    c100 = data["clean_100pct"]
    assert c100["Re"] < 21
    assert c50["Re"] < 21
    assert c100["delta_P_kg_cm2"] > 0
    assert c50["delta_P_kg_cm2"] > c100["delta_P_kg_cm2"]


def test_basket_m3hr_flow_unit() -> None:
    """Basket strainer with m³/hr input — must not raise and must produce positive ΔP."""
    resp = client.post("/calculate", json={
        "rho": 900.0,
        "mu_cP": 2.0,
        "W": 0.3,
        "flow_unit": "m3/hr",
        "D_pipe_cm": 2.0,
        "D_screen_cm": 2.5,
        "L_cm": 10.0,
        "D_open_cm": 0.04,
        "Q_pct": 39.9,
        "P_pct": 51.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["clean_100pct"]["delta_P_kg_cm2"] > 0
    assert data["clogged_50pct"]["delta_P_kg_cm2"] > data["clean_100pct"]["delta_P_kg_cm2"]


# ── Basket strainer — parametrized calculation cases with exact values ─────────
#
# Expected values were produced by running the checked-in formula (calculator.py)
# directly. Tolerance: 0.5% for geometry/velocity, 1% for ΔP.

BASKET_CASES = [
    # ──────────────────────────────────────────────────────────────────────────
    # BS1  Water | 2" pipe | 40×SWG36 mesh (Q=48.4%) | Perf 51% | kg/hr
    # A_screen = π·d·L + π·(d/2)²  (cylinder + bottom circle)
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "BS1-Water-2inch-sch40",
        "input": {
            "rho": 998.0, "mu_cP": 1.0, "W": 5000, "flow_unit": "kg/hr",
            "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
            "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0,
            "strainer_type": "Basket",
        },
        "shared": {
            "alpha": 0.24684,
            "A_pipe_cm2": 19.63495,
            "A_screen_gross_cm2": 272.63526,
            "Q_vol_cm3_s": 5010.02004,
        },
        "clean": {
            "net_surface_area_cm2": 67.29729,
            "screening_area_ratio": 3.42742,
            "V_cm_s": 18.37627,
            "Re": 326.90767,
            "C": 1.02,
            "K": 14.81380,
            "delta_P_kg_cm2": 0.002545,
        },
        "clogged": {
            "net_surface_area_cm2": 33.64864,
            "screening_area_ratio": 1.71371,
            "V_cm_s": 36.75255,
            "Re": 653.81534,
            "C": 1.22,
            "K": 10.35493,
            "delta_P_kg_cm2": 0.007115,
        },
    },
    # ──────────────────────────────────────────────────────────────────────────
    # BS2  High-viscosity fluid (Re < 21 → C = sqrt(Re)/10)
    # A_screen = π·d·L + π·(d/2)²  (cylinder + bottom circle)
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "BS2-HighViscosity-Re<21",
        "input": {
            "rho": 1070.0, "mu_cP": 350.0, "W": 800, "flow_unit": "kg/hr",
            "D_pipe_cm": 3.0, "D_screen_cm": 3.5, "L_cm": 12.0,
            "D_open_cm": 0.2, "Q_pct": 100.0, "P_pct": 40.0,
            "strainer_type": "Basket",
        },
        "shared": {
            "alpha": 0.40000,
            "A_pipe_cm2": 7.06858,
            "A_screen_gross_cm2": 141.56802,
            "Q_vol_cm3_s": 747.66355,
        },
        "clean": {
            "V_cm_s": 5.28130,
            "Re": 0.80728,
            "K": 650.32809,
            "delta_P_cm_wc": 9.892348,
        },
        "clogged": {
            "V_cm_s": 10.56261,
            "Re": 1.61457,
            "K": 325.16404,
            "delta_P_cm_wc": 19.784696,
        },
    },
    # ──────────────────────────────────────────────────────────────────────────
    # BS3  m³/hr input | medium viscosity | fractional-Re boundary region
    # A_screen = π·d·L + π·(d/2)²  (cylinder + bottom circle)
    # ──────────────────────────────────────────────────────────────────────────
    {
        "id": "BS3-m3hr-FractionalRe",
        "input": {
            "rho": 900.0, "mu_cP": 2.0, "W": 0.3, "flow_unit": "m3/hr",
            "D_pipe_cm": 2.0, "D_screen_cm": 2.5, "L_cm": 10.0,
            "D_open_cm": 0.04, "Q_pct": 39.9, "P_pct": 51.0,
            "strainer_type": "Basket",
        },
        "shared": {
            "alpha": 0.20349,
            "A_pipe_cm2": 3.14159,
            "A_screen_gross_cm2": 83.44855,
            "Q_vol_cm3_s": 83.33333,
        },
        "clean": {
            "V_cm_s": 0.99862,
            "Re": 8.83343,
            "K": 262.07054,
            "delta_P_cm_wc": 0.119884,
        },
        "clogged": {
            "V_cm_s": 1.99724,
            "Re": 17.66686,
            "K": 131.03527,
            "delta_P_cm_wc": 0.239768,
        },
    },
]


@pytest.mark.parametrize("case", BASKET_CASES, ids=[c["id"] for c in BASKET_CASES])
def test_basket_calculate(case: dict) -> None:
    _run(case)


# ── Basket strainer — input validation ────────────────────────────────────────

def test_basket_validation_missing_rho() -> None:
    resp = client.post("/calculate", json={
        "mu_cP": 1.0, "W": 5000, "flow_unit": "kg/hr",
        "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
        "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0,
    })
    assert resp.status_code == 422


def test_basket_validation_zero_density() -> None:
    resp = client.post("/calculate", json={
        "rho": 0.0, "mu_cP": 1.0, "W": 5000, "flow_unit": "kg/hr",
        "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
        "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0,
    })
    assert resp.status_code == 422


def test_basket_validation_zero_viscosity() -> None:
    resp = client.post("/calculate", json={
        "rho": 998.0, "mu_cP": 0.0, "W": 5000, "flow_unit": "kg/hr",
        "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
        "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0,
    })
    assert resp.status_code == 422


def test_basket_validation_invalid_flow_unit() -> None:
    resp = client.post("/calculate", json={
        "rho": 998.0, "mu_cP": 1.0, "W": 5000, "flow_unit": "L/hr",
        "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
        "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0,
    })
    assert resp.status_code == 422


def test_basket_validation_q_pct_over_100() -> None:
    resp = client.post("/calculate", json={
        "rho": 998.0, "mu_cP": 1.0, "W": 5000, "flow_unit": "kg/hr",
        "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
        "D_open_cm": 0.044, "Q_pct": 105.0, "P_pct": 51.0,
    })
    assert resp.status_code == 422


def test_basket_metadata_round_trips() -> None:
    """tag_no and fluid_name must be returned unchanged in the response."""
    resp = client.post("/calculate", json={
        "rho": 998.0, "mu_cP": 1.0, "W": 5000, "flow_unit": "kg/hr",
        "D_pipe_cm": 5.0, "D_screen_cm": 5.7, "L_cm": 13.8,
        "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0,
        "tag_no": "BSKT-TEST-42",
        "fluid_name": "Cooling Water",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["tag_no"] == "BSKT-TEST-42"
    assert data["fluid_name"] == "Cooling Water"


def test_basket_clogged_dp_always_greater_than_clean() -> None:
    """50% clogged ΔP must always exceed 100% clean ΔP for any valid input."""
    test_inputs = [
        {"rho": 998.0,  "mu_cP": 1.0,   "W": 5000,  "D_pipe_cm": 5.0,  "D_screen_cm": 5.7,  "L_cm": 13.8, "D_open_cm": 0.044, "Q_pct": 48.4, "P_pct": 51.0},
        {"rho": 1100.0, "mu_cP": 14.0,  "W": 4000,  "D_pipe_cm": 5.0,  "D_screen_cm": 5.7,  "L_cm": 13.8, "D_open_cm": 0.04,  "Q_pct": 39.9, "P_pct": 51.0},
        {"rho": 1070.0, "mu_cP": 350.0, "W": 800,   "D_pipe_cm": 3.0,  "D_screen_cm": 3.5,  "L_cm": 12.0, "D_open_cm": 0.2,   "Q_pct": 100.0,"P_pct": 40.0},
        {"rho": 900.0,  "mu_cP": 2.0,   "W": 0.3,   "D_pipe_cm": 2.0,  "D_screen_cm": 2.5,  "L_cm": 10.0, "D_open_cm": 0.04,  "Q_pct": 39.9, "P_pct": 51.0},
    ]
    for i, inp in enumerate(test_inputs):
        payload = {**inp, "flow_unit": "kg/hr" if inp["W"] > 1 else "m3/hr"}
        resp = client.post("/calculate", json=payload)
        assert resp.status_code == 200, f"Input #{i} failed: {resp.text}"
        data = resp.json()
        assert data["clogged_50pct"]["delta_P_kg_cm2"] > data["clean_100pct"]["delta_P_kg_cm2"], (
            f"Input #{i}: clogged ΔP not greater than clean ΔP"
        )
