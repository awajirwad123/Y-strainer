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
