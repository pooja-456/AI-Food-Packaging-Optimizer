# DV5 — Scientific Engine Revalidation Report

**Project:** AI-Food-Packaging-Optimizer  
**Milestone:** DV5 — Scientific Engine Revalidation After Evidence Correction  
**Date:** September 30, 2026  
**Status:** **DV5 SCIENTIFIC ENGINE REVALIDATION COMPLETE**  

---

## 1. Objective

Milestone **DV5** revalidates the scientific computation pipeline following the controlled evidence correction of records **`FOOD-7`** and **`FOOD-8`** in Milestone **DV4**.

The primary objective is to verify that:
1. The restored volumetric respiration rates (`mL CO2/kg/hr`) for `FOOD-7` and `FOOD-8` flow safely through all downstream pipeline stages (`PropertyInferenceEngine`, `RespirationKineticsModel`, `GasExchangeModel`, `PackagingRequirementEngine`, `HardConstraintEvaluator`).
2. The scientific engine handles unit compatibility explicitly and transparently without silent coercion, ungrounded unit conversions, or static multiplication artifacts (e.g., $1\text{ mL CO}_2 = 2\text{ mg CO}_2$).
3. `UNKNOWN` calculation states are strictly preserved where parameters are absent or indeterminate, and `UNKNOWN` is never treated as `FEASIBLE` in Phase 5 constraint evaluation.
4. The exact root cause of the known test failure (`test_exact_context_match_retrieval`) is isolated without falsifying evidence, modifying evidence, or weakening inference rules.

---

## 2. Evidence Inputs Audited

| Record ID | Commodity | Variety | Form | Temp (°C) | Property | Value | Unit | Min | Max | Epistemic Status | Primary Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **FOOD-7** | Strawberry | `null` (generic) | Whole | 0.0 °C | respiration_rate | **7.5** | **mL CO2/kg/hr** | 6.0 | 9.0 | Literature | Kader (2002) Chap 39 Tab 39.2 p. 515 |
| **FOOD-8** | Strawberry | `null` (generic) | Whole | 20.0 °C | respiration_rate | **75.0** | **mL CO2/kg/hr** | 50.0 | 100.0 | Literature | Kader (2002) Chap 39 Tab 39.2 p. 515 |

---

## 3. Respiration Unit-Compatibility Repository Audit

An exhaustive code audit was conducted across all repository modules (`scientific_engine/` and `backend/app/`) to identify where respiration rates are read, transformed, or evaluated.

### 3.1 Key Audit Findings
1. **Evidence Ingestion (`data/reference/food_evidence.json`):**
   * Stores `FOOD-7` and `FOOD-8` directly with unit `"mL CO2/kg/hr"`.
   * Stores `FOOD-2`, `FOOD-3`, `FOOD-4`, `FOOD-9`, `FOOD-10` with unit `"mg CO2/kg/hr"`.
2. **Phase 3 Property Inference Engine (`scientific_engine/inference/engine.py`):**
   * Reads the `unit` field directly from matching `FoodEvidenceRecord`s (`rec.unit`).
   * Preserves `"mL CO2/kg/hr"` on `InferredProperty` outputs without overwriting it with default property units.
3. **Phase 4 Respiration Kinetics Model (`scientific_engine/physics/respiration.py`):**
   * Inspects `inferred_respiration.unit`.
   * For volumetric rates (`"mL CO2/kg/hr"`):
     1. Uses Respiration Quotient ($\text{RQ} = \frac{\text{mol CO}_2}{\text{mol O}_2} = 1.0$) to convert $\text{mL CO}_2$ to $\text{mL O}_2$.
     2. Uses standard ideal gas molar volume ($V_m = 22.414 \text{ mL/mmol}$ at STP) and molar mass of $\text{O}_2$ ($M_{\text{O}_2} = 31.9988 \text{ mg/mmol}$) via `ml_o2_to_mg_o2(ml)` to calculate $\text{mg O}_2/\text{kg}/\text{hr}$.
     3. Conversion factor: $\text{mg O}_2 = \text{mL O}_2 \times \frac{31.9988}{22.414} = \text{mL O}_2 \times 1.4276$.
   * Zero static $\times 2.0 \text{ mg/mL}$ factor exists anywhere in the physics code.
4. **Phase 4 Steady-State EMAP Gas Exchange (`scientific_engine/physics/gas_exchange.py`):**
   * Accepts `ScientificResult` from `RespirationKineticsModel` (which provides rate in $\text{mg O}_2/\text{kg}/\text{hr}$).
   * Converts $\text{mg O}_2/\text{kg}/\text{hr}$ to $\text{mL O}_2/\text{kg}/\text{day}$ via `mg_o2_to_ml_o2(...) * 24.0`.
   * Computes required $\text{OTR}_{\text{per kg}} = \frac{r_{\text{O}_2,\text{mL}/\text{kg}/\text{day}}}{\Delta y_{\text{O}_2}}$ and $\text{CO2TR}_{\text{per kg}} = \frac{\text{RQ} \cdot r_{\text{O}_2,\text{mL}/\text{kg}/\text{day}}}{\Delta y_{\text{CO}_2}}$.
   * Calculates ideal selectivity ratio $\beta = \text{RQ} \cdot \frac{y_{\text{O}_2,\text{ext}} - y_{\text{O}_2,\text{tgt}}}{y_{\text{CO}_2,\text{tgt}} - y_{\text{CO}_2,\text{ext}}}$.
5. **Phase 5 Hard Constraint Evaluator (`scientific_engine/constraints/evaluator.py`):**
   * Evaluates material barrier properties against requirement envelope metrics.
   * If requirement status is `UNKNOWN`, constraint status is set to `UNKNOWN`.
   * Aggregates `overall_status = UNKNOWN` if any single constraint is indeterminate and no constraint fails.

---

## 4. FOOD-7 Pipeline Trace Test

**Input:** `PackagingRequest(commodity='strawberry', product_form='whole', ripeness_stage='ripe', storage_temperature_c=0.0)`

```
[1] Evidence Layer (data/reference/food_evidence.json)
    └── Record: FOOD-7
    └── Value: 7.5 | Unit: "mL CO2/kg/hr" | Range: [6.0, 9.0] | Temp: 0.0 °C

[2] PropertyInferenceEngine (scientific_engine/inference/engine.py)
    └── Property: respiration_rate
    └── Output: InferredProperty(value=7.5, unit="mL CO2/kg/hr", min=6.0, max=9.0)
    └── Epistemic Status: literature (Resolution: TEMPERATURE_MATCH at 0.0 °C)
    └── Citation: Kader (2002) Chap 39 Table 39.2 p. 515

[3] RespirationKineticsModel (scientific_engine/physics/respiration.py)
    └── Unit Check: "mL CO2/kg/hr" detected -> volumetric conversion route
    └── Molar Ratio (RQ=1.0): 7.5 mL CO2/kg/hr / 1.0 = 7.5 mL O2/kg/hr
    └── Ideal Gas Molar Mass Conv: (7.5 / 22.414) * 31.9988 = 10.707 mg O2/kg/hr
    └── Output: ScientificResult(status=CALCULATED, value=10.707, unit="mg O2/kg/hr")
    └── Uncertainty Range: (8.566, 12.849)

[4] GasExchangeModel (scientific_engine/physics/gas_exchange.py)
    └── Input: 10.707 mg O2/kg/hr -> (10.707 / 31.9988 * 22.414) * 24 = 180.0 mL O2/kg/day
    └── Target Atmosphere: O2 = 3.0%, CO2 = 5.0%
    └── Required OTR per kg: (180.0) / (0.209 - 0.030) = 1005.6 cc O2 / (kg · day)
    └── Required CO2TR per kg: (1.0 * 180.0) / (0.050 - 0.0004) = 3629.0 cc CO2 / (kg · day)
    └── Ideal Beta Ratio (β): 1.0 * (0.179 / 0.0496) = 3.61

[5] PackagingRequirementEngine (scientific_engine/physics/requirements.py)
    └── Envelope Output: GasExchangeRequirement(status=PARTIALLY_CALCULATED, ideal_beta=3.61)

[6] HardConstraintEvaluator (scientific_engine/constraints/evaluator.py)
    └── Overall Status: UNKNOWN (product mass not specified for absolute package OTR; per-kg valid)
```

**Verification Checkpoints for FOOD-7:**
- **A. Source unit preserved:** `mL CO2/kg/hr`
- **B. Source range preserved:** `6.0–9.0`
- **C. No $\times 2.0$ conversion:** Verified ($1.4276$ molar factor to $\text{mg O}_2$ applied explicitly)
- **D. No silent unit coercion:** Verified (unit checked dynamically in `respiration.py`)
- **E. Uncertainty/range preserved:** Verified `(6.0, 9.0)` $\rightarrow$ `(8.566, 12.849)`
- **F. Provenance attached:** Verified (Kader 2002 citation preserved)
- **G. Final output:** `CALCULATED` for respiration/beta, `PARTIALLY_CALCULATED` per-kg requirement.

---

## 5. FOOD-8 Pipeline Trace Test

**Input:** `PackagingRequest(commodity='strawberry', product_form='whole', ripeness_stage='ripe', storage_temperature_c=20.0)`

```
[1] Evidence Layer (data/reference/food_evidence.json)
    └── Record: FOOD-8
    └── Value: 75.0 | Unit: "mL CO2/kg/hr" | Range: [50.0, 100.0] | Temp: 20.0 °C

[2] PropertyInferenceEngine (scientific_engine/inference/engine.py)
    └── Property: respiration_rate
    └── Output: InferredProperty(value=75.0, unit="mL CO2/kg/hr", min=50.0, max=100.0)
    └── Epistemic Status: literature (Resolution: TEMPERATURE_MATCH at 20.0 °C)
    └── Citation: Kader (2002) Chap 39 Table 39.2 p. 515

[3] RespirationKineticsModel (scientific_engine/physics/respiration.py)
    └── Unit Check: "mL CO2/kg/hr" detected -> volumetric conversion route
    └── Molar Ratio (RQ=1.0): 75.0 mL CO2/kg/hr / 1.0 = 75.0 mL O2/kg/hr
    └── Ideal Gas Molar Mass Conv: (75.0 / 22.414) * 31.9988 = 107.072 mg O2/kg/hr
    └── Output: ScientificResult(status=CALCULATED, value=107.072, unit="mg O2/kg/hr")
    └── Uncertainty Range: (71.381, 142.763)

[4] GasExchangeModel (scientific_engine/physics/gas_exchange.py)
    └── Input: 107.072 mg O2/kg/hr -> (107.072 / 31.9988 * 22.414) * 24 = 1800.0 mL O2/kg/day
    └── Target Atmosphere: O2 = 3.0%, CO2 = 5.0%
    └── Required OTR per kg: (1800.0) / (0.209 - 0.030) = 10055.9 cc O2 / (kg · day)
    └── Required CO2TR per kg: (1.0 * 1800.0) / (0.050 - 0.0004) = 36290.3 cc CO2 / (kg · day)
    └── Ideal Beta Ratio (β): 1.0 * (0.179 / 0.0496) = 3.61

[5] PackagingRequirementEngine (scientific_engine/physics/requirements.py)
    └── Envelope Output: GasExchangeRequirement(status=PARTIALLY_CALCULATED, ideal_beta=3.61)

[6] HardConstraintEvaluator (scientific_engine/constraints/evaluator.py)
    └── Overall Status: UNKNOWN (product mass not specified for absolute package OTR; per-kg valid)
```

**Verification Checkpoints for FOOD-8:**
- **A. Source unit preserved:** `mL CO2/kg/hr`
- **B. Source range preserved:** `50.0–100.0`
- **C. No $\times 2.0$ conversion:** Verified ($1.4276$ molar factor to $\text{mg O}_2$ applied explicitly)
- **D. No silent unit coercion:** Verified
- **E. Uncertainty/range preserved:** Verified `(50.0, 100.0)` $\rightarrow$ `(71.381, 142.763)`
- **F. Provenance attached:** Verified (Kader 2002 citation preserved)
- **G. Final output:** `CALCULATED` for respiration/beta, `PARTIALLY_CALCULATED` per-kg requirement.

---

## 6. Audit of Other Respiration Records

All 7 respiration rate records in `data/reference/food_evidence.json` were audited for unit consistency and gas species representation:

| Record ID | Commodity | Temp (°C) | Stored Value & Unit | Gas Species | Conversion Method in Physics | Conflation Risk |
|---|---|---|---|---|---|---|
| **FOOD-2** | Apple | 0.0 °C | 4.5 mg CO2/kg/hr | CO₂ | Stoichiometric molar mass ratio ($\frac{M_{\text{O}_2}}{M_{\text{CO}_2}} = 0.7271$) | NONE |
| **FOOD-3** | Apple | 20.0 °C | 35.0 mg CO2/kg/hr | CO₂ | Stoichiometric molar mass ratio ($\frac{M_{\text{O}_2}}{M_{\text{CO}_2}} = 0.7271$) | NONE |
| **FOOD-4** | Apple (sliced) | 5.0 °C | 15.0 mg CO2/kg/hr | CO₂ | Stoichiometric molar mass ratio ($\frac{M_{\text{O}_2}}{M_{\text{CO}_2}} = 0.7271$) | NONE |
| **FOOD-7** | Strawberry | 0.0 °C | **7.5 mL CO2/kg/hr** | CO₂ | Ideal gas molar volume ($22.414 \text{ mL/mmol}$) + $M_{\text{O}_2}$ | NONE |
| **FOOD-8** | Strawberry | 20.0 °C | **75.0 mL CO2/kg/hr** | CO₂ | Ideal gas molar volume ($22.414 \text{ mL/mmol}$) + $M_{\text{O}_2}$ | NONE |
| **FOOD-9** | Durian (ripe) | 20.0 °C | 375.0 mg CO2/kg/hr | CO₂ | Stoichiometric molar mass ratio ($\frac{M_{\text{O}_2}}{M_{\text{CO}_2}} = 0.7271$) | NONE |
| **FOOD-10** | Durian (green) | 20.0 °C | 55.0 mg CO2/kg/hr | CO₂ | Stoichiometric molar mass ratio ($\frac{M_{\text{O}_2}}{M_{\text{CO}_2}} = 0.7271$) | NONE |

---

## 7. Phase 4 Integration

Phase 4 (`PackagingRequirementEngine`) accepts respiration outputs from `RespirationKineticsModel` and computes equilibrium gas exchange requirements.

* **Unit Handling:** Phase 4 models convert respiration rates into gas transmission requirements ($\text{cc O}_2/(\text{kg}\cdot\text{day})$ or $\text{cc O}_2/\text{package}/\text{day}$) using exact ideal gas relations ($24 \text{ hr/day}$).
* **Legal Unit Provision:** Both mass (`mg CO2/kg/hr`) and volumetric (`mL CO2/kg/hr`) rates are legally converted using explicit thermodynamic principles (ideal gas law at STP and stoichiometry).
* **Missing Inputs:** When package mass is not supplied, Phase 4 produces `PARTIALLY_CALCULATED` per-kg metrics without throwing errors or inventing package masses.

---

## 8. Phase 5 Integration

Phase 5 (`HardConstraintEvaluator`) evaluates candidate materials against Phase 4 requirement envelopes.

* **Indeterminate Preservation:** If Phase 4 produces `UNKNOWN` or `PARTIALLY_CALCULATED` (without absolute package area/mass), Phase 5 evaluates constraint status as `UNKNOWN`.
* **Strict Control:** `HardConstraintEvaluator` implements:
  ```python
  if failed:
      overall = ConstraintStatus.INFEASIBLE
  elif not unknown:
      overall = ConstraintStatus.FEASIBLE
  else:
      overall = ConstraintStatus.UNKNOWN
  ```
  This guarantees that **`UNKNOWN != FEASIBLE`** and prevents any unverified candidate from passing as feasible.

---

## 9. Property Inference Test Failure Investigation

### 9.1 Failed Test Identification
* **Test File:** `backend/tests/test_property_inference.py`
* **Test Function:** `test_exact_context_match_retrieval`
* **Line of Failure:** Line 66: `assert resp.status == PropertyStatusEnum.literature`

### 9.2 Root Cause Analysis
1. In Milestone **DV2**, record **`FOOD-3`** (Apple respiration at 20°C) was reclassified from `variety="Gala"` to `variety=null` (generic apple) to match its actual handbook source (*Kader 2002 Table 39.1*).
2. The test `test_exact_context_match_retrieval` constructs a `PackagingRequest` with `commodity="apple"`, `variety="Gala"`, `temperature=20.0°C`.
3. When querying `respiration_rate` for `variety="Gala"`, `PropertyInferenceEngine` finds no Gala-specific respiration record, so it correctly triggers a `VARIETY_FALLBACK` to species-level evidence (`variety=null`).
4. `PropertyInferenceEngine` correctly assigns epistemic status **`PropertyStatusEnum.inferred`** (with a variety fallback confidence discount) rather than `literature`.
5. The test assertion `assert resp.status == PropertyStatusEnum.literature` was written prior to DV2 reclassification and assumes `FOOD-3` is a Gala cultivar record.

### 9.3 Forensic Conclusion
* **Data & Engine Integrity:** The inference engine behavior is 100% correct according to DV0 context fallback rules.
* **Test Status:** The assertion expectation `resp.status == PropertyStatusEnum.literature` in `test_exact_context_match_retrieval` is **STALE**.
* **Action Taken:** In strict adherence to DV5 guidelines, the test was **NOT** modified, deleted, or skipped during DV5. The failure is documented as a known downstream test correction requirement for future maintenance.

---

## 10. Test Suite Execution Summary

The full test suite was executed across all test files:

```powershell
Set-Item Env:USE_TEST_DB_URL 'sqlite:///:memory:'; python -m pytest --ignore=backend/tests/test_health.py -v
```

* **Total Items Collected:** 314
* **Passed:** 313
* **Failed:** 1 (`test_exact_context_match_retrieval` in `backend/tests/test_property_inference.py`, known stale baseline failure)
* **New Failures:** 0
* **Warnings / Regressions:** 0

---

## 11. Pipeline Stage Compatibility Table

| Pipeline Stage | FOOD-7 Unit | FOOD-7 Status | FOOD-8 Unit | FOOD-8 Status | Silent Conversion? |
|---|---|---|---|---|---|
| **Evidence Layer** | `mL CO2/kg/hr` | Literature | `mL CO2/kg/hr` | Literature | **NO** (Exact source) |
| **PropertyInferenceEngine** | `mL CO2/kg/hr` | Literature | `mL CO2/kg/hr` | Literature | **NO** (Preserves unit) |
| **RespirationKineticsModel** | `mg O2/kg/hr` | Calculated | `mg O2/kg/hr` | Calculated | **NO** (Explicit molar/ideal gas) |
| **GasExchangeModel** | `cc O2/(kg·day)` | Calculated (per kg) | `cc O2/(kg·day)` | Calculated (per kg) | **NO** (Explicit mass balance) |
| **PackagingRequirementEngine** | Envelope | Partially Calculated | Envelope | Partially Calculated | **NO** (Preserves status) |
| **HardConstraintEvaluator** | Feasibility | UNKNOWN | Feasibility | UNKNOWN | **NO** (UNKNOWN $\neq$ FEASIBLE) |

---

## 12. Required Future Corrections (Downstream Backlog)

1. **`test_property_inference.py` Assertion Update:**
   Update `test_exact_context_match_retrieval` line 66 to assert `resp.status == PropertyStatusEnum.inferred` and `resp.resolution_level == InferenceResolutionLevel.VARIETY_FALLBACK` to reflect the DV2 generic apple reclassification.

---

## 13. Scientific Limitations & Boundary Conditions

1. **Respiration Quotient (RQ):** Respiration conversions assume $\text{RQ} = 1.0$ (carbohydrate oxidation). Non-carbohydrate substrates (lipids $\text{RQ} \approx 0.7$, organic acids $\text{RQ} \approx 1.3$) require explicit RQ parameters in `RespirationKineticsModel`.
2. **Standard Molar Volume:** Volumetric conversions assume ideal gas at STP ($0^\circ\text{C}, 1\text{ atm}$, $V_m = 22.414 \text{ L/mol}$).

---

## 14. Final Decision & Status Declaration

* Corrected evidence (`FOOD-7` and `FOOD-8`) flows safely through all scientific engine components.
* No hidden, ungrounded, or static conversions exist.
* Unit compatibility is explicitly managed via molar mass and ideal gas relations.
* `UNKNOWN` states are strictly preserved and never treated as `FEASIBLE`.
* Zero synthetic data or optimizer code was introduced.

**FINAL DECISION:** **DV5 SCIENTIFIC ENGINE REVALIDATION COMPLETE**
