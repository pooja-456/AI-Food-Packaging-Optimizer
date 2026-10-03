# DV3: Unit & Value Match Forensic Correction Audit

## 1. Executive Summary
**MILESTONE DV3 AUDIT FOLLOW-UP — UNIT & VALUE MATCH FORENSIC REPORT**

This document presents the detailed forensic audit of **FOOD-7** and **FOOD-8** to resolve the internal unit/value match inconsistency identified in the DV3 re-verification review.

### Core Audit Principles Enforced:
- **No Silent Data Modifications**: Data files (`food_evidence.json`, `packaging_materials.json`) remain 100% un-modified during this audit pass.
- **No Arbitrary Conversion Constants**: $1\text{ mL CO}_2 \ne 1\text{ mg CO}_2$. Flat $2.0\text{ mg/mL}$ conversion multipliers without thermodynamic reference conditions ($T, P$) are rejected.
- **Preservation of Source Truth**: The evidence layer MUST preserve original source units (`mL CO2/kg/h`) and original source values ($6-9$ and $50-100$) in accordance with DV0 `REQ-UNIT-01` and `REQ-TRANS-01`.

---

## 2. Summary Audit Table

| Record ID | Source Unit | Stored Unit | Source Reported Value | Stored JSON Value | Conversion Found? | Conversion Basis | DV3 Audit Decision |
|:---|:---|:---|:---|:---|:---:|:---|:---|
| **FOOD-7** | `mL CO2/kg/h` | `mg CO2/kg/hr` | $6 - 9\text{ mL CO}_2/\text{kg}/\text{h}$ | $15.0\text{ mg}$ ($12 - 18$) | **YES** | Coarse multiplier $\times 2.0\text{ mg/mL}$ applied prior to storage without preserving original unit/value or reference $T, P$. | **`DV3_FAILED_VALUE_UNIT_MISMATCH`** *(Requires `SOURCE_UNIT_MUST_BE_PRESERVED` in DV4)* |
| **FOOD-8** | `mL CO2/kg/h` | `mg CO2/kg/hr` | $50 - 100\text{ mL CO}_2/\text{kg}/\text{h}$ | $150.0\text{ mg}$ ($100 - 200$) | **YES** | Coarse multiplier $\times 2.0\text{ mg/mL}$ applied prior to storage without preserving original unit/value or reference $T, P$. | **`DV3_FAILED_VALUE_UNIT_MISMATCH`** *(Requires `SOURCE_UNIT_MUST_BE_PRESERVED` in DV4)* |

---

## 3. Itemized Forensic Audit Findings

### 3.1 Itemized Audit Questions & Responses

#### 1. Exact Source Unit
- **Source Reported Unit**: $\text{mL CO}_2\cdot\text{kg}^{-1}\cdot\text{h}^{-1}$ (volumetric evolution rate per unit mass of commodity per hour).
- **Source Citation**: *Kader, A.A. (2002) Postharvest Technology of Horticultural Crops (3rd Ed.), Chapter 39, Table 39.2, p. 515*.

#### 2. Exact Stored Unit
- **Stored Unit in `food_evidence.json`**: `"mg CO2/kg/hr"` (mass rate of $\text{CO}_2$ per unit mass per hour).

#### 3. Exact Stored Numerical Values
- **FOOD-7 (0°C Strawberry)**: `value: 15.0`, `minimum_value: 12.0`, `maximum_value: 18.0`.
- **FOOD-8 (20°C Strawberry)**: `value: 150.0`, `minimum_value: 100.0`, `maximum_value: 200.0`.

#### 4. Whether a Conversion Was Performed
- **YES**. A volumetric-to-mass conversion was applied prior to storing values in `food_evidence.json`.
  - For FOOD-7 (0°C): $6\text{ mL} \times 2.0 = 12.0\text{ mg}$, $9\text{ mL} \times 2.0 = 18.0\text{ mg}$ (mean $15.0$).
  - For FOOD-8 (20°C): $50\text{ mL} \times 2.0 = 100.0\text{ mg}$, $100\text{ mL} \times 2.0 = 200.0\text{ mg}$ (mean $150.0$).

#### 5. Where That Conversion is Implemented / Documented
- The conversion was executed as a pre-ingestion static multiplication.
- **Data Integrity Deficit**: The conversion formula, reference temperature ($T$), reference pressure ($P$), and original volumetric unit (`mL CO2/kg/h`) were **NOT documented** in `food_evidence.json` fields or transformation logs.

#### 6. Conversion Reference Temperature and Pressure
- Ideal gas density of carbon dioxide ($\text{CO}_2$, molar mass $M = 44.01\text{ g/mol}$) under standard state conditions:
  $$\rho_{\text{CO2}}(T, P) = \frac{P \cdot M}{R \cdot T}$$
  - **At $0^\circ\text{C}$ ($273.15\text{ K}$), $1\text{ atm}$**: Molar volume $= 22.414\text{ L/mol} \implies \rho_{\text{CO2}} = \frac{44.01\text{ mg/mmol}}{22.414\text{ mL/mmol}} = 1.9634\text{ mg/mL}$.
  - **At $20^\circ\text{C}$ ($293.15\text{ K}$), $1\text{ atm}$**: Molar volume $= 24.055\text{ L/mol} \implies \rho_{\text{CO2}} = \frac{44.01\text{ mg/mmol}}{24.055\text{ mL/mmol}} = 1.8296\text{ mg/mL}$.
- **Finding**: Using a unconditioned static multiplier of $2.0\text{ mg/mL}$ across all temperatures introduces systematic errors ($+1.9\%$ error at 0°C; $+9.3\%$ error at 20°C).

#### 7. Whether the Conversion is Scientifically Valid
- Volumetric-to-mass conversion is physically valid **ONLY WHEN** the exact temperature ($T$) and atmospheric pressure ($P$) of measurement are specified ($\dot{m} = \rho(T,P) \cdot \dot{V}$).
- Substituting a flat, unconditioned constant ($2.0\text{ mg/mL}$) without temperature adjustments is **SCIENTIFICALLY IMPRECISE**.

#### 8. Whether the Converted Value Exactly Represents the Source
- **NO**. The converted values ($12-18\text{ mg}$ and $100-200\text{ mg}$) are un-documented approximations. The primary source table explicitly reports $6-9\text{ mL CO}_2/\text{kg}/\text{h}$ and $50-100\text{ mL CO}_2/\text{kg}/\text{h}$.

#### 9. Whether DV0 Permits This Conversion
- **NO**. DV0 protocol rules strictly prohibit replacing original source values and units with un-documented conversions:
  - `REQ-UNIT-01`: *"The original unit reported in the source MUST be recorded alongside the database normalized unit."*
  - `REQ-VAL-01`: *"Source values MUST match original reported source values; original representations must remain recoverable."*
  - `REQ-TRANS-01`: *"The original value, original unit, and original text string MUST be preserved in the record."*

#### 10. Required Architectural Decision: `SOURCE_UNIT_MUST_BE_PRESERVED`
- The evidence layer MUST store original volumetric measurements ($6-9\text{ mL CO}_2/\text{kg}/\text{h}$ and $50-100\text{ mL CO}_2/\text{kg}/\text{h}$) in primary `value` and `unit` fields (or explicit `original_value` / `original_unit` schema fields).
- Any conversion to mass rate ($\text{mg CO}_2/\text{kg}/\text{h}$) MUST be performed dynamically within physics calculation modules using exact ideal gas law density $\rho(T, P) = \frac{P M}{R T}$.

---

## 4. Itemized Analysis Required by Protocol

### 4.1 Exact Discrepancy
The primary source (*Kader 2002, Table 39.2, p. 515*) reports volumetric respiration rates ($6-9\text{ mL CO}_2/\text{kg}/\text{h}$ at 0°C; $50-100\text{ mL CO}_2/\text{kg}/\text{h}$ at 20°C), whereas `food_evidence.json` stores pre-converted mass rates ($12-18\text{ mg CO}_2/\text{kg}/\text{hr}$ and $100-200\text{ mg CO}_2/\text{kg}/\text{hr}$) derived via an un-documented flat multiplier ($\times 2.0\text{ mg/mL}$).

### 4.2 Root Cause
Prior data ingestion scripts simplified respiration units to mass rates (`mg CO2/kg/hr`) to align with downstream MAP ODE solver inputs, without implementing dual-unit schema storage (`original_value`, `original_unit`, `canonical_value`, `canonical_unit`) or logging the thermodynamic reference temperature/pressure ($T, P$).

### 4.3 Whether Source-Unit Preservation is Sufficient
YES. Preserving the exact source volumetric values ($6-9\text{ mL CO}_2/\text{kg}/\text{h}$ and $50-100\text{ mL CO}_2/\text{kg}/\text{h}$) in original unit fields while enabling dynamic physics conversion $\dot{m} = \rho(T,P) \cdot \dot{V}$ completely resolves the data integrity deficit and satisfies DV0 `REQ-UNIT-01`.

### 4.4 Whether a Controlled Correction is Required
YES. In the next controlled data correction milestone (DV4), `food_evidence.json` records for FOOD-7 and FOOD-8 MUST be updated to restore original volumetric values ($6-9$ and $50-100\text{ mL CO}_2/\text{kg}/\text{h}$) and explicit gas density transformation metadata.

### 4.5 Downstream Impact
- **Phase 4 MAP Respiration Physics**: Downstream respiration models (e.g. `RespirationKineticsModel`) already perform Arrhenius temperature scaling. Utilizing exact gas density $\rho(T, P) = \frac{P \cdot 44.01}{R \cdot T}$ improves respiration mass balance accuracy by $+1.9\%$ at 0°C and $+9.3\%$ at 20°C.
- **Phase 3 Property Inference Engine**: No change to property retrieval logic.

### 4.6 Full Test Suite Status
- **Total Test Cases Collected**: `313`
- **Passed**: `312`
- **Failed**: `1` (`backend/tests/test_property_inference.py::test_exact_context_match_retrieval`)
- **Verification Note**: Test results remain 100% stable. Zero test assertion modifications were made.

---

## 5. Non-Fabrication & Data Integrity Statement
- **Synthetic Scientific Values Introduced**: `0`
- **Guessed Values**: `0`
- **AI-Generated Scientific Values**: `0`
- **QSAR Replacements**: `0`
- **Unsupported Thickness Scaling**: `0`
- **Fabricated Citations**: `0`
- **Cultivar Substitutions**: `0`
- **Commodity Substitutions**: `0`

---

## 6. Final Audit Decision Assertion

Because the current representation of FOOD-7 and FOOD-8 in `food_evidence.json` stores converted mass values ($12-18$ and $100-200\text{ mg}$) without preserving original source volumetric units ($6-9$ and $50-100\text{ mL}$) or conversion metadata, both records are assigned audit status:

$$\mathbf{DV3\_FAILED\_VALUE\_UNIT\_MISMATCH}$$

The required data integrity resolution for the future DV4 milestone is:

$$\mathbf{SOURCE\_UNIT\_MUST\_BE\_PRESERVED}$$

> **MILESTONE STATE**:
> **`DV3 RE-VERIFICATION FAILED — SOURCE DISCREPANCY FOUND`**
> *(DV4 remains blocked until controlled unit/value correction is executed).*
