# DV4 — Controlled Scientific Evidence Unit/Value Correction Report

**Project:** AI-Food-Packaging-Optimizer  
**Milestone:** DV4 — Controlled Scientific Evidence Unit/Value Correction  
**Date:** September 30, 2026  
**Status:** **DV4 CONTROLLED CORRECTION COMPLETE**  

---

## 1. Executive Summary

Milestone **DV4** completes the controlled unit and value correction for scientific evidence records **`FOOD-7`** and **`FOOD-8`** within `data/reference/food_evidence.json`.

Following the forensic finding in the DV3 follow-up audit, it was discovered that pre-ingestion mass unit conversion was performed on original volumetric respiration observations using an undocumented $\times 2.0 \text{ mg/mL}$ multiplier. In accordance with the frozen **DV0 Scientific Evidence Verification Protocol**, evidence layers must preserve exact external source observations without unconditioned or unsupported numerical transformations.

This milestone successfully:
1. Restored **`FOOD-7`** and **`FOOD-8`** to their exact volumetric source values and units (`mL CO2/kg/hr`).
2. Removed the undocumented pre-ingestion $\times 2.0 \text{ mg/mL}$ conversion multiplier.
3. Updated the provenance and transformation notes in `data/reference/food_evidence.json`.
4. Enforced strict data scope isolation: **0** other records were modified (`FOOD-1`–`FOOD-6`, `FOOD-9`–`FOOD-11`, `MAT-1-O1`, `MAT-1-O2`, `MAT-5-O10` remain untouched). `MAT-1-O1` and `MAT-1-O2` remain `RETAINED_AS_REJECTED`.
5. Conducted a downstream compatibility audit across physics and inference modules without mutating downstream code.
6. Added a focused regression test (`test_dv4_food_7_and_food_8_volumetric_unit_correction`) in `backend/tests/test_food_evidence.py`.
7. Executed the complete test suite: **314 collected, 313 passed, 1 expected downstream failure** (`test_exact_context_match_retrieval` in `test_property_inference.py`), maintaining the exact project baseline.

---

## 2. Affected Records & Source Grounding

Both affected records originate from the authoritative primary handbook source:
> **Source:** Kader, A.A. (2002). *Postharvest Technology of Horticultural Crops* (3rd ed.), University of California, Agriculture and Natural Resources, Publication 3311, Chapter 39 ("Postharvest Handling Systems: Small Fruits"), Table 39.2, p. 515.

| Record ID | Commodity | Variety | Product Form | Temp (°C) | Original Source Value & Unit | Pre-Ingestion Mass Conversion (Erroneous) | DV4 Restored Value & Unit | Range / Uncertainty |
|---|---|---|---|---|---|---|---|---|
| **FOOD-7** | Strawberry | `null` (generic) | Whole (raw) | 0.0 °C | 6–9 mL CO₂/kg/h | 12–18 mg CO₂/kg/h ($\times 2.0$) | **7.5 mL CO₂/kg/hr** | `[6.0, 9.0]` |
| **FOOD-8** | Strawberry | `null` (generic) | Whole (raw) | 20.0 °C | 50–100 mL CO₂/kg/h | 100–200 mg CO₂/kg/h ($\times 2.0$) | **75.0 mL CO₂/kg/hr** | `[50.0, 100.0]` |

---

## 3. Pre-Ingestion Artifact Analysis & Elimination

### 3.1 Forensic Breakdown of Erroneous Pre-Ingestion Multiplier
During original pre-ingestion data entry, volumetric CO₂ respiration rates ($\text{mL CO}_2/\text{kg}/\text{hr}$) were converted to mass rates ($\text{mg CO}_2/\text{kg}/\text{hr}$) by multiplying source range endpoints by a flat factor of $2.0 \text{ mg/mL}$:
* `FOOD-7` (0°C): Source $6 \text{ to } 9 \text{ mL CO}_2/\text{kg}/\text{h} \times 2.0 \rightarrow 12 \text{ to } 18 \text{ mg CO}_2/\text{kg}/\text{h}$
* `FOOD-8` (20°C): Source $50 \text{ to } 100 \text{ mL CO}_2/\text{kg}/\text{h} \times 2.0 \rightarrow 100 \text{ to } 200 \text{ mg CO}_2/\text{kg}/\text{h}$

### 3.2 Physicochemical & Scientific Invalidation
Ideal gas calculations dictate CO₂ gas density ($\rho_{\text{CO}_2} = \frac{P \cdot M}{R \cdot T}$):
* At 0 °C (273.15 K) and 1 atm: $\rho_{\text{CO}_2} = \frac{1.0 \text{ atm} \cdot 44.01 \text{ g/mol}}{0.08206 \text{ L}\cdot\text{atm}/(\text{mol}\cdot\text{K}) \cdot 273.15 \text{ K}} = 1.963 \text{ mg/mL}$
* At 20 °C (293.15 K) and 1 atm: $\rho_{\text{CO}_2} = \frac{1.0 \text{ atm} \cdot 44.01 \text{ g/mol}}{0.08206 \text{ L}\cdot\text{atm}/(\text{mol}\cdot\text{K}) \cdot 293.15 \text{ K}} = 1.830 \text{ mg/mL}$

Applying a static $2.0 \text{ mg/mL}$ factor introduces $+1.89\%$ error at 0°C and $+9.29\%$ error at 20°C. More importantly, DV0 Rule 4 strictly forbids performing unconditioned or undocumented unit conversions during data ingestion.

### 3.3 Elimination
The static $\times 2.0$ pre-ingestion multiplier has been completely eliminated. `data/reference/food_evidence.json` now stores exact volumetric values (`mL CO2/kg/hr`) directly transcribed from Table 39.2.

---

## 4. Scientific Evidence Dataset Audit & Scope Enforcement

### 4.1 Food Evidence Dataset Inventory (Post-DV4)

| Record ID | Commodity | Property | Value | Unit | Min | Max | DV4 Status |
|---|---|---|---|---|---|---|---|
| **FOOD-1** | Apple | moisture_content | 85.33 | % | 84.1 | 86.5 | UNTOUCHED (VERIFIED) |
| **FOOD-2** | Apple | respiration_rate | 4.5 | mg CO2/kg/hr | 3.0 | 6.0 | UNTOUCHED (RECLASSIFIED) |
| **FOOD-3** | Apple | respiration_rate | 35.0 | mg CO2/kg/hr | 25.0 | 50.0 | UNTOUCHED (RECLASSIFIED) |
| **FOOD-4** | Apple | respiration_rate | 15.0 | mg CO2/kg/hr | 12.0 | 18.0 | UNTOUCHED (RECLASSIFIED) |
| **FOOD-5** | Apple | ph | 3.4 | pH | 3.2 | 3.6 | UNTOUCHED (VERIFIED) |
| **FOOD-6** | Strawberry | moisture_content | 90.95 | % | 89.5 | 92.4 | UNTOUCHED (RECLASSIFIED) |
| **FOOD-7** | Strawberry | respiration_rate | **7.5** | **mL CO2/kg/hr** | **6.0** | **9.0** | **CORRECTED & VERIFIED** |
| **FOOD-8** | Strawberry | respiration_rate | **75.0** | **mL CO2/kg/hr** | **50.0** | **100.0** | **CORRECTED & VERIFIED** |
| **FOOD-9** | Durian | respiration_rate | 375.0 | mg CO2/kg/hr | 300.0 | 450.0 | UNTOUCHED (VERIFIED) |
| **FOOD-10** | Durian | respiration_rate | 55.0 | mg CO2/kg/hr | 40.0 | 70.0 | UNTOUCHED (VERIFIED) |
| **FOOD-11** | Salmon | fat_content | 12.35 | % | 10.5 | 14.8 | UNTOUCHED (VERIFIED) |

### 4.2 Material Evidence Status Audit (Post-DV4)
* `MAT-1-O1`: `RETAINED_AS_REJECTED` (Untouched)
* `MAT-1-O2`: `RETAINED_AS_REJECTED` (Untouched)
* `MAT-5-O10`: `RECLASSIFIED_AND_VERIFIABLE` (Untouched)
* All other 7 material observations: `VERIFIED` (Untouched)

---

## 5. Downstream Compatibility Audit

In accordance with DV4 milestone directives, no downstream physics engine or property inference code was modified during DV4. An exhaustive audit was conducted across downstream consumers of `respiration_rate`:

### 5.1 Audit Findings across Downstream Codebase
1. **Respiration Physics Module (`backend/app/physics/respiration.py`):**
   * Uses Michaelis-Menten respiration models.
   * Expects rates in volumetric or molar terms when computing gas balance.
   * Explicit stoichiometric conversions (`MOLAR_MASS_CO2_G_MOL`) are implemented in physics functions, expecting volumetric standard input or explicit mass-to-volume normalization.
2. **Property Inference Module (`backend/app/domain/property_inference.py`):**
   * Maps commodity requests to reference dataset records.
   * Preserves whatever unit is present in `food_evidence.json`.
3. **Database Models & Ingestion (`backend/app/models/evidence.py` & `backend/app/ingestion/`):**
   * Database schema stores `unit` as a string without hardcoded unit restrictions.
4. **Optimization & Candidate Schemas (`backend/app/schemas/`):**
   * Candidate evaluation and constraint models treat `ScientificResult` unit fields dynamically.

### 5.2 Recommendation for Future Milestones (M7 Execution / DV5)
When executing optimizer benchmarks in M7 or future physics integration, any engine layer component reading `respiration_rate` should explicitly check `record.unit` and invoke standard ideal gas density conversions ($\rho = 1.963 \text{ mg/mL}$ at 0°C, $1.830 \text{ mg/mL}$ at 20°C) when converting between mass and volumetric respiration rates.

---

## 6. Provenance & Transformation Documentation

The `notes` field for both `FOOD-7` and `FOOD-8` in `data/reference/food_evidence.json` has been updated with explicit transformation history:

### FOOD-7 Notes:
```
"DV4 CONTROLLED CORRECTION: Restored exact volumetric source observation from Kader (2002) Chap 39 Table 39.2 p. 515 (6-9 mL CO2/kg/h at 0°C). Removed undocumented pre-ingestion x2.0 mg/mL mass conversion multiplier."
```

### FOOD-8 Notes:
```
"DV4 CONTROLLED CORRECTION: Restored exact volumetric source observation from Kader (2002) Chap 39 Table 39.2 p. 515 (50-100 mL CO2/kg/h at 20°C). Removed undocumented pre-ingestion x2.0 mg/mL mass conversion multiplier."
```

---

## 7. Test Suite Verification

### 7.1 New Regression Unit Test
A new regression test was added to `backend/tests/test_food_evidence.py`:
```python
def test_dv4_food_7_and_food_8_volumetric_unit_correction() -> None:
    ref_path = Path(__file__).resolve().parent.parent.parent / "data" / "reference" / "food_evidence.json"
    with open(ref_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Index 6 is FOOD-7 (Strawberry respiration rate at 0°C)
    food_7 = data[6]
    assert food_7["commodity"] == "strawberry"
    assert food_7["temperature"] == 0.0
    assert food_7["property"] == "respiration_rate"
    assert food_7["unit"] == "mL CO2/kg/hr"
    assert food_7["minimum_value"] == 6.0
    assert food_7["maximum_value"] == 9.0
    assert food_7["value"] == 7.5
    assert food_7["uncertainty_range"] == [6.0, 9.0]
    assert "DV4 CONTROLLED CORRECTION" in food_7["notes"]

    # Index 7 is FOOD-8 (Strawberry respiration rate at 20°C)
    food_8 = data[7]
    assert food_8["commodity"] == "strawberry"
    assert food_8["temperature"] == 20.0
    assert food_8["property"] == "respiration_rate"
    assert food_8["unit"] == "mL CO2/kg/hr"
    assert food_8["minimum_value"] == 50.0
    assert food_8["maximum_value"] == 100.0
    assert food_8["value"] == 75.0
    assert food_8["uncertainty_range"] == [50.0, 100.0]
    assert "DV4 CONTROLLED CORRECTION" in food_8["notes"]
```

### 7.2 Pytest Execution Summary
* **Command:** `powershell -Command "Set-Item Env:USE_TEST_DB_URL 'sqlite:///:memory:'; python -m pytest --ignore=backend/tests/test_health.py"`
* **Total Collected:** 314 items
* **Passed:** 313 passed
* **Failed:** 1 failed (`test_exact_context_match_retrieval` in `test_property_inference.py`, expected baseline downstream failure)
* **Result:** 100% compliant with milestone acceptance criteria.

---

## 8. Zero Synthetic / Unsupported Conversion Metric Audit

| Metric | Target | Actual State | Compliance |
|---|---|---|---|
| Total Evidence Records | 21 | 21 (11 Food, 10 Material) | PASS |
| Verified Real-World Evidence | 19 | 19 | PASS |
| Retained Rejected Records | 2 | 2 (`MAT-1-O1`, `MAT-1-O2`) | PASS |
| Synthetic Records | 0 | 0 | PASS |
| Guessed / Estimated Values | 0 | 0 | PASS |
| QSAR Replacement Values | 0 | 0 | PASS |
| Unsupported Unit Conversions | 0 | 0 | PASS |

---

## 9. Verification Protocol (DV0) Compliance Checklist

| Rule ID | Requirement | FOOD-7 Status | FOOD-8 Status |
|---|---|---|---|
| **DV0-1** | Entity Identity | PASS (Strawberry whole raw) | PASS (Strawberry whole raw) |
| **DV0-2** | Property Identity | PASS (respiration_rate) | PASS (respiration_rate) |
| **DV0-3** | Value Match | PASS (7.5, min 6.0, max 9.0) | PASS (75.0, min 50.0, max 100.0) |
| **DV0-4** | Unit & Dimensional Check | PASS (`mL CO2/kg/hr`) | PASS (`mL CO2/kg/hr`) |
| **DV0-5** | Condition Context | PASS (0.0 °C, 95% RH) | PASS (20.0 °C, 70% RH) |
| **DV0-6** | Form & Maturity | PASS (whole, ripe) | PASS (whole, ripe) |
| **DV0-7** | Method Validation | PASS (Closed-system GC) | PASS (Closed-system GC) |
| **DV0-8** | Source Attribution | PASS (Kader 2002 Chap 39 Tab 39.2 p 515) | PASS (Kader 2002 Chap 39 Tab 39.2 p 515) |
| **DV0-9** | Provenance Record | PASS (Transformation notes recorded) | PASS (Transformation notes recorded) |

---

## 10. Final Conclusion & Status Declaration

Milestone **DV4 — Controlled Scientific Evidence Unit/Value Correction** is successfully completed. Records **`FOOD-7`** and **`FOOD-8`** strictly adhere to the frozen **DV0 Scientific Evidence Verification Protocol** and match their underlying primary scientific literature source.

**FINAL STATUS: DV4 CONTROLLED CORRECTION COMPLETE**
