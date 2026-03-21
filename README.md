# Y-Strainer Pressure Drop Calculator

## Overview

This project implements a Y-Strainer pressure drop calculator using the **MMKGS metric unit system**. The calculator supports both **incompressible fluids** (water, oil) and **compressible fluids** (steam, gas) using the Darcy–Weisbach equation as the core calculation method.

---

## Table of Contents

1. [Input Parameters](#1-input-parameters)
2. [Variable Definitions](#2-variable-definitions)
3. [Lookup Tables](#3-lookup-tables)
4. [Calculation Formulas](#4-calculation-formulas)
   - 4.1 [Derived Geometry](#41-derived-geometry)
   - 4.2 [Effective Open Area (α)](#42-effective-open-area-α)
   - 4.3 [Free Area Ratio](#43-free-area-ratio)
   - 4.4 [Incompressible Flow (Darcy–Weisbach)](#44-incompressible-flow-darcyweisbach)
   - 4.5 [Compressible Flow (Darcy–Weisbach)](#45-compressible-flow-darcyweisbach)
5. [Data Sources & References](#5-data-sources--references)
6. [Excel Lookup Data](#6-excel-lookup-data)
   - 6.1 [Mesh Data (ASTM E2016-15)](#61-mesh-data-astm-e2016-15)
   - 6.2 [Perforated Sheet Data (ASTM E674-12)](#62-perforated-sheet-data-astm-e674-12)
   - 6.3 [Discharge Coefficient C (Perry's)](#63-discharge-coefficient-c-perrys)
   - 6.4 [Pipe Sizes](#64-pipe-sizes-sample)
   - 6.5 [Strainer Geometry Data](#65-strainer-geometry-data)
   - 6.6 [Pressure Rating Classes](#66-pressure-rating-classes)
7. [Sample Calculations](#7-sample-calculations)
   - 7.1 [Incompressible Flow – Water](#71-sample-incompressible-flow--water)
   - 7.2 [Compressible Flow – Steam](#72-sample-compressible-flow--steam)

---

## 1. Input Parameters

All inputs are organized into four categories:

### Category 1 – Fluid Properties

| # | Parameter | Description | Unit |
|---|-----------|-------------|------|
| A | Density (ρ) | Fluid density at operating conditions | kg/m³ |
| B | Viscosity (μ) | Dynamic viscosity of fluid | cP |
| C | Specific Heat Ratio (k) | Cp/Cv — required for compressible fluids only | — |

> For compressible fluids: when density (ρ) is directly provided, assume **Z = 1** (ideal gas approximation).

---

### Category 2 – Flow Data

| # | Parameter | Description | Unit |
|---|-----------|-------------|------|
| A | Flow Rate (Q_flow) | Volumetric flow rate (incompressible) or mass flow rate (compressible) | m³/hr or kg/hr |
| B | Pipe Size | Nominal Bore (NPS) and schedule | — |
| C | Pipe ID | Internal diameter of the pipe | mm |
| D | Screen Length (L) | Axial length of the cylindrical strainer screen | mm |
| E | Screen OD (D_screen) | Outer diameter of the cylindrical strainer screen | mm |

---

### Category 3 – Screen Geometry

| # | Parameter | Description | Unit | Source |
|---|-----------|-------------|------|--------|
| A | Mesh Size | Mesh number (e.g., 10, 20, 40) | — | ASTM E2016-15 |
| B | SWG (Wire Gauge) | Standard Wire Gauge used with mesh | — | ASTM E2016-15 |
| C | Opening Width (D) | Clear aperture between wires | mm | ASTM E2016-15 |
| D | Open Area % (Q) | Percentage of gross area that is open | % | ASTM E2016-15 |
| E | Perforated Sheet | Hole diameter × pitch description | mm | ASTM E674-12 |
| F | Open Area % (P) | Percentage open area for perforated sheet | % | ASTM E674-12 |

> When both mesh and perforated sheet are combined, the effective open area uses the product of both open-area fractions.

---

### Category 4 – Other / Reference Data

| # | Parameter | Description | Unit |
|---|-----------|-------------|------|
| A | Pressure (P₁) | Operating inlet pressure | kg/cm² or bar(g) |
| B | Temperature (T) | Operating temperature | °C |
| C | Tag Number | Equipment instrument tag | — |
| D | Project | Project or client name | — |
| E | Model | Strainer model reference | — |

---

## 2. Variable Definitions

| Symbol | Description | Unit |
|--------|-------------|------|
| ΔP | Pressure drop across the strainer | Pa or bar |
| K | Velocity head loss coefficient (from Miller) | — |
| C | Coefficient of discharge (from Perry's, pg 5-40) | — |
| ρ | Fluid density | kg/m³ |
| μ | Dynamic viscosity of fluid | cP |
| V | Fluid velocity in the pipe | m/s |
| V_s | Superficial velocity through screen (based on gross screen area) | cm/s |
| Q_flow | Volumetric flow rate | m³/hr |
| A_pipe | Pipe internal cross-sectional area | m² |
| A_gross | Gross (total) surface area of cylindrical screen | mm² |
| α | Combined effective open area of screen element | mm² |
| D | Opening width of mesh wire (ASTM E2016-15) | mm |
| Q | % open area of wire mesh (ASTM E2016-15) | % |
| P | % open area of perforated sheet (ASTM E674-12) | % |
| Re | Reynolds number | — |
| f | Darcy friction factor | — |
| L | Screen length | m |
| g | Gravitational acceleration | 9.81 m/s² |
| k | Specific heat ratio Cp/Cv (compressible fluids) | — |
| Z | Compressibility factor (assumed = 1 when ρ is given) | — |
| ṁ | Mass flow rate (compressible fluids) | kg/s |

---

## 3. Lookup Tables

The calculation engine uses the following embedded lookup tables (source: `Pr drop cal data for Y strainer.xlsx`):

| Sheet Name | Contents |
|------------|----------|
| `Mesh Data` | Mesh # × SWG → Opening Width (mm) + Open Area % |
| `Perf Sheet` | Perforation description → % Open Area P |
| `Pipe sizes` | NPS + Schedule → Pipe OD, ID (mm), DN |
| `Pr Class` | Pressure rating numbers (150, 300, 600, 900, 1500, 2500) |
| `C Value` | Reynolds number range → Discharge coefficient C |
| `Strainer data` | Strainer model × NPS → Screen OD (D) and Screen Length (L) |
| `T strainer data` | T-strainer pipe size → dimensional data |

---

## 4. Calculation Formulas

### 4.1 Derived Geometry

**Pipe cross-sectional area:**
$$A_{pipe} = \frac{\pi \cdot D_{pipe}^2}{4}$$

**Gross screen area (cylindrical surface):**
$$A_{gross} = \pi \cdot D_{screen} \cdot L$$

**Pipe flow velocity:**
$$V = \frac{Q_{m^3/s}}{A_{pipe}}$$

**Reynolds number:**
$$Re = \frac{\rho \cdot V \cdot D_{pipe}}{\mu \times 10^{-3}}$$

> where μ is in cP → converted to Pa·s by multiplying by 10⁻³

---

### 4.2 Effective Open Area (α)

**Wire mesh only:**
$$\alpha = A_{gross} \times \frac{Q}{100}$$

**Perforated sheet only:**
$$\alpha = A_{gross} \times \frac{P}{100}$$

**Combined mesh + perforated sheet:**
$$\alpha_{combined} = A_{gross} \times \frac{Q}{100} \times \frac{P}{100}$$

> This formula represents the net unobstructed flow path when wire mesh is mounted over a perforated support plate.

---

### 4.3 Free Area Ratio

$$\text{Free Area Ratio} = \frac{\alpha}{A_{pipe}}$$

A ratio > 1 indicates the screen presents more flow area than the inlet pipe, typically desirable for low pressure drop.

---

### 4.4 Incompressible Flow (Darcy–Weisbach)

This is the **primary method** for incompressible fluids (water, oil, glycol).

**Step 1 — Velocity:**
$$V = \frac{Q_{m^3/s}}{A_{pipe}}$$

**Step 2 — Reynolds number:**
$$Re = \frac{\rho \cdot V \cdot D_{pipe}}{\mu \times 10^{-3}}$$

**Step 3 — Friction factor (Darcy friction factor):**

- If Re < 2000 (laminar):
$$f = \frac{64}{Re}$$

- If Re ≥ 2000 (turbulent, Blasius approximation):
$$f = 0.3164 \cdot Re^{-0.25}$$

**Step 4 — Pressure drop:**
$$\Delta P = f \cdot \frac{L}{D_{pipe}} \cdot \frac{\rho \cdot V^2}{2}$$

**Unit conversion:**
$$\Delta P_{bar} = \frac{\Delta P_{Pa}}{100{,}000}$$

> **Reference:** Darcy–Weisbach equation, Blasius correlation for turbulent pipe flow.

---

### 4.5 Compressible Flow (Darcy–Weisbach)

For compressible fluids (steam, gas, air), the velocity head method with inlet density is used.

**Step 1 — Mass flow conversion:**
$$\dot{m} = \frac{\dot{m}_{kg/hr}}{3600} \quad [\text{kg/s}]$$

**Step 2 — Pipe velocity (from mass flow and inlet density):**
$$V = \frac{\dot{m}}{\rho_1 \cdot A_{pipe}}$$

**Step 3 — Reynolds number:**
$$Re = \frac{\rho_1 \cdot V \cdot D_{pipe}}{\mu \times 10^{-5} \cdot 10}$$

> (μ in cP × 10⁻³ = Pa·s)

**Step 4 — Effective screen area (combined α):**
$$\alpha_{combined} = A_{gross} \times \frac{Q}{100} \times \frac{P}{100}$$

**Step 5 — Superficial velocity through screen:**
$$V_s = \frac{\dot{m}}{\rho_1 \cdot \alpha_{combined}}$$

**Step 6 — Pressure drop (velocity-head method with K from Miller):**
$$\Delta P = \frac{K \cdot \rho_1 \cdot V_s^2}{2 \times 10^5} \quad [\text{bar}]$$

> **Compressibility note:** When density (ρ₁) is directly provided at operating conditions (e.g., from steam tables), set Z = 1. No additional compressibility correction is applied. This is valid when the pressure drop is small relative to the inlet pressure (i.e., ΔP/P₁ < ~10%).

---

## 5. Data Sources & References

| # | Source | Data Used | Details |
|---|--------|-----------|---------|
| 1 | **ASTM E2016-15** | Wire cloth mesh table | Mesh number + SWG → Opening Width D (mm) and Open Area Q (%) |
| 2 | **ASTM E674-12** | Perforated plate table | Hole diameter + pitch → Open Area P (%) |
| 3 | **Perry's Chemical Engineers' Handbook, pg 5-40** | Discharge coefficient C | C lookup by Reynolds number: range 0.45 – 1.5 |
| 4 | **Miller, D.S. — Internal Flow Systems** | K velocity head loss coefficient | K range: 1.0 – 6.0 depending on screen type and cleanliness |
| 5 | **ISA 75.01 Annex C** | Gas properties table | Molecular weight (M) and specific heat ratio (k) for 40+ gases |
| 6 | **Darcy–Weisbach Equation** | Core pressure drop method | Used for both incompressible and compressible ΔP |
| 7 | **Blasius Correlation** | Turbulent friction factor | f = 0.3164 · Re⁻⁰·²⁵ for 3000 < Re < 10⁵ smooth pipe |

### Formula: Wire Mesh Opening Width (ASTM E2016-15)

$$D_{opening} = \frac{25.4}{n_{mesh}} - d_{wire}$$

$$Q\% = \left(\frac{D_{opening}}{25.4 / n_{mesh}}\right)^2 \times 100$$

Where:
- `n_mesh` = mesh count (openings per inch)
- `d_wire` = wire diameter in mm (from SWG table)

---

## 6. Excel Lookup Data

### 6.1 Mesh Data (ASTM E2016-15)

Source sheet: `Mesh Data`  
Columns: `mesh` (mesh/inch) | `swg` (Standard Wire Gauge) | `openSize` (mm) | `OpenArea` (%)

Sample rows:

| Mesh | SWG | Opening Width (mm) | Open Area (%) |
|------|-----|--------------------|---------------|
| 2 | 12 | 10.05 | 62.7 |
| 3 | 14 | 6.43 | 57.7 |
| 5 | 18 | 3.86 | 57.8 |
| 7 | 20 | 2.71 | 56.0 |
| 9 | 22 | 2.11 | 55.8 |
| 10 | 23 | 1.93 | 57.8 |
| 12 | 25 | 1.60 | 57.7 |
| 14 | 27 | 1.39 | 59.3 |
| 16 | 27 | 1.17 | 54.4 |
| 18 | 28 | 1.03 | 53.8 |

> Full table available in `Pr drop cal data for Y strainer.xlsx` → Sheet: `Mesh Data` (249 rows).

---

### 6.2 Perforated Sheet Data (ASTM E674-12)

Source sheet: `Perf Sheet`  
Columns: `Srno` | `Perforation` (description) | `PercentageOpenP` (%)

| # | Perforation | Open Area P (%) |
|---|-------------|-----------------|
| 1 | No Perforation | 100 |
| 2 | 4mm × Pitch 6mm | 40 |
| 3 | 6mm × Pitch 8mm | 51 |
| 4 | 8mm × Pitch 11.25mm | 55 |
| 5 | 8mm × Pitch 9.5mm | 64 |
| 6 | 12mm × Pitch 14mm | 67 |
| 7 | 0.8mm × Pitch 1.39mm | 30 |

---

### 6.3 Discharge Coefficient C (Perry's)

Source sheet: `C Value`  
Columns: `SrNo` | `RedStart` (Re lower bound) | `RedEnd` (Re upper bound) | `C` value

The coefficient C is looked up based on Reynolds number:

| Re Range | C Value |
|----------|---------|
| ≥ 5500 | 1.50 |
| 4000 – 4499 | 1.46 |
| 2907 – 3299 | 1.43 |
| 2200 – 2503 | 1.40 |
| 1600 – 1699 | 1.34 |
| 860 – 949 | 1.28 |
| 500 – 524 | 1.16 |
| 300 – 375 | 1.04 |
| 201 – 300 | 1.00 |
| 175 – 200 | 0.95 |
| 150 – 174 | 0.90 |
| 100 – 124 | 0.80 |
| 50 – 59 | 0.65 |
| 40 – 49 | 0.60 |
| 21 – 25 | 0.45 |

> Full table: 78 rows covering Re from 21 to ≥ 5500. Available in `C Value` sheet.

---

### 6.4 Pipe Sizes (Sample)

Source sheet: `Pipe sizes`  
Columns: `NPS_inch` | `Nominal bore` | `OD` (mm) | `SchNoCS1` | `SchNoCS2` | `ID` (mm) | `DN`

Sample rows:

| NPS | Nominal Bore | OD (mm) | Schedule | ID (mm) | DN |
|-----|-------------|---------|----------|---------|----|
| 1/2 | 15NB | 21.3 | STD / 40 | 6.36 | 15 |
| 3/4 | 20NB | 26.7 | STD / 40 | 30.10 | 20 |
| 1 | 25NB | 33.4 | STD / 40 | 36.66 | 25 |
| 1-1/2 | 40NB | 48.3 | STD / 40 | 49.22 | 40 |
| 2 | 50NB | 60.3 | STD / 40 | 53.94 | 50 |
| 3 | 80NB | 88.9 | STD / 40 | 102.26 | 80 |
| 4 | 100NB | 114.3 | STD / 40 | 162.76 | 100 |
| 6 | 150NB | 168.3 | STD / 40 | 188.92 | 150 |
| 8 | 200NB | 219.1 | STD / 40 | 254.46 | 200 |
| 10 | 250NB | 273.0 | STD / 40 | 304.74 | 250 |

> Full table: 248 rows. Available in `Pipe sizes` sheet.

---

### 6.5 Strainer Geometry Data

Source sheet: `Strainer data`  
Columns: `SType` (model) | `SrNo` | `NPS` | `OD` (nominal) | `D` (screen OD, mm) | `L` (screen length, mm)

| Model | NPS | Screen OD D (mm) | Screen Length L (mm) |
|-------|-----|------------------|----------------------|
| FMSTR54 | 1-1/2 | 42 | 113 |
| FMSTR54 | 2 | 57 | 136 |
| FMSTR54 | 3 | 90 | 176 |
| FMSTR54 | 4 | 118 | 202 |
| FMSTR54 | 6 | 150 | 295 |
| FMSTR54 | 8 | 200 | 368 |
| FMSTR54 | 10 | 254 | 474 |
| FMSTR54 | 12 | 304 | 505 |
| FMSTR34 | 3 | 78 | 166 |
| FMSTR34 | 4 | 104 | 186 |
| FMSTR34 | 6 | 150 | 275 |
| FMSTR34 | 8 | 200 | 347 |

---

### 6.6 Pressure Rating Classes

Source sheet: `Pr Class`

| Rating | Code |
|--------|------|
| 150 | 1 |
| 300 | 3 |
| 600 | 6 |
| 900 | 9 |
| 1500 | 5 |
| 2500 | 2 |

---

## 7. Sample Calculations

### 7.1 Sample: Incompressible Flow – Water

#### Given Inputs

| Parameter | Value | Unit |
|-----------|-------|------|
| Media | Water | — |
| Density (ρ) | 998 | kg/m³ |
| Viscosity (μ) | 1 | cP |
| Flow Rate | 10 | m³/hr |
| Pipe Size | 80NB, SCH40 | — |
| Pipe ID | 80 | mm |
| Screen Length | 220 | mm |
| Screen OD | 90 | mm |
| Mesh Size | 40 mesh | — |
| Perforated Sheet | 8 mm dia, pitch 11.25 mm | — |
| Open Area Q (mesh 40) | 36 | % |
| Open Area P (perf sheet) | 55 | % |
| Pressure | 70 | kg/cm² |
| Temperature | 220 | °C |
| Tag Number | SAMPLE-01 | — |

#### Step-by-Step Solution

**Unit Conversions:**
- Q = 10 m³/hr = 10/3600 = **0.002778 m³/s**
- D_pipe = 80 mm = **0.08 m**
- L = 220 mm = **0.22 m**
- μ = 1 cP = **0.001 Pa·s**

**Pipe Cross-Sectional Area:**
$$A_{pipe} = \frac{\pi \times 0.08^2}{4} = 0.005027 \text{ m}^2$$

**Pipe Velocity:**
$$V = \frac{0.002778}{0.005027} = 0.553 \text{ m/s}$$

**Reynolds Number:**
$$Re = \frac{998 \times 0.553 \times 0.08}{0.001} = 44{,}144 \quad \Rightarrow \text{Turbulent}$$

**Friction Factor (Blasius):**
$$f = 0.3164 \times 44144^{-0.25} = 0.0247$$

**Pressure Drop (Darcy–Weisbach):**
$$\Delta P = 0.0247 \times \frac{0.22}{0.08} \times \frac{998 \times 0.553^2}{2} = 21{,}158 \text{ Pa} = \mathbf{0.21 \text{ bar}}$$

**Gross Screen Area:**
$$A_{gross} = \pi \times 90 \times 220 = 62{,}204 \text{ mm}^2$$

**Combined Effective Open Area:**
$$\alpha = 62{,}204 \times \frac{36}{100} \times \frac{55}{100} = 12{,}316 \text{ mm}^2$$

**Free Area Ratio:**
$$\text{Ratio} = \frac{12{,}316}{5{,}027} = 2.45$$

---

### 7.2 Sample: Compressible Flow – Steam

#### Given Inputs

| Parameter | Value | Unit |
|-----------|-------|------|
| Media | Steam | — |
| Density (ρ₁) | 9.07 | kg/m³ |
| Viscosity (μ) | 0.016 | cP |
| Specific Heat Ratio (k) | 1.33 | — |
| Compressibility Factor (Z) | 1 (assumed, density given) | — |
| Inlet Pressure (P₁) | 17 | bar(g) |
| Temperature | 207 | °C |
| Mass Flow Rate | 3200 | kg/hr |
| Pipe ID | 50 | mm |
| Screen Length | 150 | mm |
| Screen OD | 60 | mm |
| Mesh Size | 40 Mesh | — |
| Perforated Sheet | 8 mm Ø, pitch 12 mm | — |
| Open Area Q (mesh 40) | 36 | % |
| Open Area P (perf 8×12) | 40.3 | % |
| Tag Number | SAMPLE-002 | — |

#### Step-by-Step Solution

**Mass Flow Rate:**
$$\dot{m} = \frac{3200}{3600} = 0.889 \text{ kg/s}$$

**Pipe Cross-Sectional Area:**
$$A_{pipe} = \frac{\pi \times 0.05^2}{4} = 0.001963 \text{ m}^2$$

**Pipe Velocity:**
$$V = \frac{0.889}{9.07 \times 0.001963} = 50.1 \text{ m/s}$$

**Reynolds Number:**
$$Re = \frac{9.07 \times 50.1 \times 0.05}{1.6 \times 10^{-5}} = 1.42 \times 10^6 \quad \Rightarrow \text{Turbulent}$$

**Gross Screen Area:**
$$A_{gross} = \pi \times 0.06 \times 0.15 = 0.02827 \text{ m}^2$$

**Combined Effective Open Area:**
$$\alpha = 0.02827 \times \frac{36}{100} \times \frac{40.3}{100} = 0.4101 \times 10^{-2} \text{ m}^2$$

**Superficial Velocity Through Screen:**
$$V_s = \frac{0.889}{9.07 \times 0.004101} = 23.9 \text{ m/s}$$

**Pressure Drop (K-method, K = 2.5):**
$$\Delta P = \frac{2.5 \times 9.07 \times 50.1^2}{2 \times 10^5} = \mathbf{0.285 \text{ bar}}$$

**Free Area Ratio:**
$$\text{Ratio} = \frac{0.004101}{0.001963} = 2.09$$

---

## Notes on Formula Selection

| Fluid Type | Method | Key Variable |
|------------|--------|-------------|
| Water, Oil (incompressible) | Darcy–Weisbach with Blasius friction factor | Velocity from volumetric flow |
| Steam, Gas (compressible) | K-based velocity head method using inlet density | Velocity from mass flow ÷ (ρ₁ × A) |
| Z = 1 assumed | When ρ is given directly at operating conditions | No additional correction needed |

---

*Unit System: MMKGS (metre–metre–kilogram–second metric system)*  
*Standards: ASTM E2016-15 (wire mesh), ASTM E674-12 (perforated plate), ISA 75.01 Annex C (gas properties)*  
*References: Perry's Chemical Engineers' Handbook (C values), Miller's Internal Flow Systems (K values)*
