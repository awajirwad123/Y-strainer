"""
calculator.py — Core Y-strainer pressure-drop calculation logic.

All functions are pure (no I/O, no framework imports).
Formula reference: README_formula_analysis.md
Validated against 14 Forbes Marshall software screenshots (validate_screenshots.py).

Unit system: CGS throughout
  rho    : gm/cm³
  mu     : poise  (= cP × 0.01)
  V      : cm/s
  Area   : cm²
  g      : 981 cm/s²
  ΔP out : cm WC → ÷2.54 = in WC → ÷1000 = kg/cm²
"""

import math
from config import GRAVITY_CM_S2, C_VALUE_TABLE, CM_WC_TO_IN_WC, CM_WC_TO_KG_CM2


def lookup_C(Re: float) -> float:
    """Return discharge coefficient C for a given Reynolds number.

    - Re < 21  : C = √Re / 10  (derived from software behaviour for high-viscosity fluids)
    - Re ≥ 21  : interpolation-free range lookup from Perry's C_VALUE_TABLE
    """
    if Re < 21:
        return math.sqrt(Re) / 10.0
    for lo, hi, c in C_VALUE_TABLE:
        if hi is None and Re >= lo:
            return c
        if hi is not None and lo <= Re <= hi:
            return c
    raise ValueError(f"Reynolds number {Re:.4f} is outside the C value table range")


def volumetric_flow(W: float, flow_unit: str, rho: float) -> float:
    """Convert flow input to internal volumetric quantity Q_vol (CGS convention).

    kg/hr  → Q_vol = W / rho          (implicit CGS: preserves cm/s when divided by cm²)
    m³/hr  → Q_vol = W × 1e6 / 3600   (true cm³/s)
    """
    if flow_unit == "kg/hr":
        return W / rho
    return W * 1_000_000.0 / 3600.0


def _compute_condition(
    A_screen: float,
    Q_vol: float,
    alpha: float,
    D_open_cm: float,
    rho: float,
    mu_cP: float,
    A_pipe: float,
) -> dict:
    """Calculate pressure drop for one screen-cleanliness condition.

    Steps (all CGS):
      1. net_area      = A_screen × α
      2. ratio         = net_area / A_pipe
      3. V             = Q_vol / A_screen          (approach velocity at gross screen area)
      4. μ_poise       = μ_cP × 0.01
      5. D_eff         = D_open / α
      6. Re            = D_eff × V × ρ / μ_poise
      7. C             = lookup_C(Re)
      8. K             = (1 - α²) / (C² × α²)
      9. ΔP_cm         = K × ρ × V² / (2 × 981)
    """
    g = GRAVITY_CM_S2

    net_area = A_screen * alpha
    ratio = net_area / A_pipe
    V = Q_vol / A_screen
    mu_poise = mu_cP * 0.01
    D_eff = D_open_cm / alpha
    Re = D_eff * V * rho / mu_poise
    C = lookup_C(Re)
    K = (1.0 - alpha**2) / (C**2 * alpha**2)
    dP_cm = K * rho * V**2 / (2.0 * g)

    return {
        "surface_area_cm2": A_screen,
        "net_surface_area_cm2": net_area,
        "screening_area_ratio": ratio,
        "V_cm_s": V,
        "Re": Re,
        "C": C,
        "K": K,
        "delta_P_cm_wc": dP_cm,
        "delta_P_in_wc": dP_cm * CM_WC_TO_IN_WC,
        "delta_P_kg_cm2": dP_cm * CM_WC_TO_KG_CM2,
    }


def calculate(
    rho: float,
    mu_cP: float,
    W: float,
    flow_unit: str,
    D_pipe_cm: float,
    D_screen_cm: float,
    L_cm: float,
    D_open_cm: float,
    Q_pct: float,
    P_pct: float,
) -> dict:
    """Run the full Y-strainer pressure-drop calculation.

    Shared steps (common to both conditions):
      α         = (Q% / 100) × (P% / 100)
      A_pipe    = π/4 × D_pipe²
      A_screen  = π × D_screen × L          (100% clean gross area)
      Q_vol     = volumetric_flow(W, unit, ρ)

    Then computes _compute_condition for:
      - 100% clean  (A_screen = A100)
      - 50% clogged (A_screen = A100 / 2)

    Returns a plain dict (schema-compatible with CalculationResponse).
    """
    alpha = (Q_pct / 100.0) * (P_pct / 100.0)
    A_pipe = math.pi / 4.0 * D_pipe_cm**2
    A100 = math.pi * D_screen_cm * L_cm
    A50 = A100 / 2.0
    rho = rho / 1000.0 
    Q_vol = volumetric_flow(W, flow_unit, rho)

    return {
        "alpha": alpha,
        "A_pipe_cm2": A_pipe,
        "A_screen_gross_cm2": A100,
        "Q_vol_cm3_s": Q_vol,
        "clean_100pct": _compute_condition(A100, Q_vol, alpha, D_open_cm, rho, mu_cP, A_pipe),
        "clogged_50pct": _compute_condition(A50,  Q_vol, alpha, D_open_cm, rho, mu_cP, A_pipe),
    }
