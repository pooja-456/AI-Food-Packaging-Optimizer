# DV5-C — Controlled Scientific Engine Safety Correction Report

**Project:** AI-Food-Packaging-Optimizer  
**Milestone:** DV5-C — CO₂-Only Respiration Safety Boundary  
**Date:** September 30, 2026  
**Status:** **DV5-C CONTROLLED SAFETY CORRECTION COMPLETE**  

---

## 1. Executive Summary & Original Defect

Following the forensic audit in `docs/dv5_co2_o2_conversion_basis_audit.md`, an architectural safety defect was identified in `RespirationKineticsModel`:

* **Original Defect:** When processing volumetric carbon dioxide respiration rates ($\text{mL CO}_2/\text{kg}/\text{hr}$), the engine automatically derived an oxygen consumption rate ($r_{\text{O}_2}$ in $\text{mg O}_2/\text{kg}/\text{hr}$) using an unverified default Respiration Quotient ($\text{RQ} = 1.0$) and an unverified standard molar volume at STP ($22.414 \text{ mL/mmol}$).
* **Scientific Reality:** Converting volumetric $\text{CO}_2$ evolution to $\text{O}_2$ consumption requires:
  1. A verified, commodity-specific, temperature-specific Respiration Quotient ($\text{RQ} = \frac{\text{mol CO}_2}{\text{mol O}_2}$).
  2. Verified gas measurement reference conditions ($T, P$) defining the molar volume $V_m(T,P)$.
* **Correction Implemented:** A controlled runtime safety guard was inserted in `RespirationKineticsModel.calculate_respiration` in `scientific_engine/physics/respiration.py`. If evidence provides volumetric $\text{CO}_2$ respiration without verified RQ or gas reference conditions, the engine **preserves** the source $\text{CO}_2$ observation intact but strictly evaluates $r_{\text{O}_2}$ as **`CalculationStatus.UNKNOWN`**.

---

## 2. Scientific Basis for Safety Correction

1. **DV0 Verification Protocol:** Rule 4 & 5 strictly forbid assuming unstated measurement conditions or unverified parameter values (such as defaulting $\text{RQ} = 1.0$ or assuming STP for $20^\circ\text{C}$ measurements).
2. **Phase 4 Scientific Contract:** `docs/phase4_scientific_model_specification.md` Section 2 states: *"`UNKNOWN`: Essential scientific properties ... are absent. No guessing or placeholder values are used."*
3. **Epistemic Integrity:** When essential parameters ($\text{RQ}$, gas measurement reference conditions) are absent, calculating a numerical $r_{\text{O}_2}$ value fabricates data. Setting $r_{\text{O}_2} =$ `CalculationStatus.UNKNOWN` accurately reflects the state of knowledge.

---

## 3. Exact Runtime Safety Boundary

```python
if "CO2" in raw_unit:
    if "ml" in raw_unit.lower() or "cc" in raw_unit.lower():
        # Volumetric CO2 respiration (e.g. mL CO2/kg/hr) cannot be converted to r_O2
        # without verified commodity-specific RQ and gas volume measurement reference conditions.
        assumptions.append("Volumetric CO2 respiration rate preserved intact from literature evidence.")
        assumptions.append("Conversion from volumetric CO2 (mL CO2/kg/hr) to O2 consumption rate (mg O2/kg/hr) is UNKNOWN because verified RQ and gas volume measurement reference conditions are absent.")

        trace = make_traceability(
            model_name="EmpiricalEvidenceRespiration",
            equation_form="r_O2 = UNKNOWN (Volumetric CO2 cannot be converted to O2 without verified RQ and gas reference condition)",
            equation_reference="DV5 Forensic Audit: docs/dv5_co2_o2_conversion_basis_audit.md",
            scientific_sources=inferred_respiration.citations,
            inputs_used={"inferred_respiration": raw_r, "unit": raw_unit, "temperature_c": temperature_c},
            parameters_used={},
            parameter_sources={"inferred_respiration": "Phase 3 PropertyInferenceProfile"},
            units_used={"r_O2": "mg O2/kg/hr", "r_observed": raw_unit},
            assumptions=assumptions,
            uncertainty_description="Source uncertainty interval preserved intact.",
            uncertainty_interval=unc_range,
            failure_or_unknown_reason=(
                f"Respiration rate is reported in volumetric CO2 ({raw_unit}), "
                "but conversion to O2 consumption rate (r_O2) requires a verified commodity-specific "
                "Respiration Quotient (RQ) and gas volume measurement reference convention, which are not present in the evidence record."
            ),
            warnings=warnings + [w.message for w in inferred_respiration.warnings] + [
                f"Volumetric CO2 respiration ({raw_r} {raw_unit}) preserved intact; O2 consumption rate calculation is UNKNOWN."
            ],
        )

        return ScientificResult(
            status=CalculationStatus.UNKNOWN,
            value=None,
            unit="mg O2/kg/hr",
            uncertainty_range=unc_range,
            minimum_value=unc_range[0] if unc_range else None,
            maximum_value=unc_range[1] if unc_range else None,
            traceability=trace,
        )
```

---

## 4. Files & Functions Changed

| File Path | Function / Test | Description of Change |
|---|---|---|
| `scientific_engine/physics/respiration.py` | `RespirationKineticsModel.calculate_respiration` | Added safety guard returning `CalculationStatus.UNKNOWN` for volumetric $\text{CO}_2$ respiration when RQ/STP conditions are unverified. |
| `backend/tests/test_packaging_requirements.py` | `test_partial_calculation_when_product_mass_is_missing` | Updated test request commodity from strawberry to apple (which has mass-based respiration evidence) to test `PARTIALLY_CALCULATED` per-kg requirement logic. |
| `backend/tests/test_food_evidence.py` | `test_dv5c_food_7_safety_guard_regression`<br>`test_dv5c_food_8_safety_guard_regression` | Added focused regression tests validating the 7 required safety conditions for `FOOD-7` and `FOOD-8`. |

---

## 5. Record-Level Pipeline Verification

### 5.1 FOOD-7 Verification (Strawberry at 0°C)
* **Evidence Value:** `7.5`
* **Evidence Unit:** `"mL CO2/kg/hr"` (Preserved)
* **Evidence Range:** `(6.0, 9.0)` (Preserved)
* **Evidence Source:** Kader (2002) Chap 39 Table 39.2 p. 515 (Attached)
* **Physics $r_{\text{O}_2}$ Calculation:** `status = CalculationStatus.UNKNOWN`, `value = None` (No numeric $r_{\text{O}_2}$ fabricated!)
* **Reason:** `Respiration rate is reported in volumetric CO2 (mL CO2/kg/hr), but conversion to O2 consumption rate (r_O2) requires a verified commodity-specific Respiration Quotient (RQ) and gas volume measurement reference convention...`

### 5.2 FOOD-8 Verification (Strawberry at 20°C)
* **Evidence Value:** `75.0`
* **Evidence Unit:** `"mL CO2/kg/hr"` (Preserved)
* **Evidence Range:** `(50.0, 100.0)` (Preserved)
* **Evidence Source:** Kader (2002) Chap 39 Table 39.2 p. 515 (Attached)
* **Physics $r_{\text{O}_2}$ Calculation:** `status = CalculationStatus.UNKNOWN`, `value = None` (No numeric $r_{\text{O}_2}$ fabricated!)
* **Reason:** `Respiration rate is reported in volumetric CO2 (mL CO2/kg/hr), but conversion to O2 consumption rate (r_O2) requires a verified commodity-specific Respiration Quotient (RQ) and gas volume measurement reference convention...`

---

## 6. End-to-End UNKNOWN Propagation

$$\text{Unsupported Volumetric } \text{CO}_2 \text{ Evidence } (\text{FOOD-7} / \text{FOOD-8})$$
$$\downarrow$$
$$\text{RespirationKineticsModel: } r_{\text{O}_2} = \text{UNKNOWN} \quad (\text{value} = \text{None})$$
$$\downarrow$$
$$\text{GasExchangeModel: } \text{GasExchangeRequirement}(\text{status} = \text{UNKNOWN})$$
$$\downarrow$$
$$\text{PackagingRequirementEngine: Envelope with } \text{gas\_requirements.status} = \text{UNKNOWN}$$
$$\downarrow$$
$$\text{HardConstraintEvaluator: Candidate Overall Status} = \text{ConstraintStatus.UNKNOWN}$$

**Verification:** $\mathbf{\text{UNKNOWN} \neq \text{FEASIBLE}}$. Phase 5 evaluates candidate materials for strawberry as `UNKNOWN` rather than `FEASIBLE` or `INFEASIBLE`, strictly preventing unverified material recommendations.

---

## 7. Positive Control Verification

* **Test Record:** `FOOD-3` (Apple whole raw at 20°C, `35.0 mg CO2/kg/hr`)
* **Call:** `RespirationKineticsModel().calculate_respiration(inferred_respiration=profile.properties['respiration_rate'], temperature_c=20.0, rq=1.0)`
* **Output:** `CalculationStatus.CALCULATED`, `value = 25.448 mg O2/kg/hr`, `uncertainty_range = (18.177, 36.354)`
* **Finding:** Valid mass-based respiration evidence continues to function properly without being blocked by the volumetric safety guard.

---

## 8. Test Suite Verification Results

Pytest execution results across all test suites:

* **Total Items Collected:** 316
* **Passed:** 315
* **Failed:** 1 (`test_exact_context_match_retrieval` in `backend/tests/test_property_inference.py`, known stale baseline failure)
* **New Failures:** 0
* **Test Suite Status:** 100% compliant with milestone requirements.

---

## 9. Separate Stale-Test Issue (Downstream Backlog)

* **Test Function:** `test_exact_context_match_retrieval` in `backend/tests/test_property_inference.py`
* **Description:** Expects `resp.status == PropertyStatusEnum.literature` for a Gala apple request. In DV2, record `FOOD-3` was reclassified from Gala to generic apple (`variety=null`). Querying Gala now correctly triggers `VARIETY_FALLBACK` to species level, setting status to `inferred`.
* **Action:** Left untouched during DV5-C in strict compliance with milestone boundaries. Documented for future test contract maintenance.

---

## 10. Remaining Limitations & Boundaries

1. **Direct $\text{CO}_2$ Applications:** Volumetric $\text{CO}_2$ respiration data (`mL CO2/kg/hr`) remains fully preserved in the evidence layer and can be consumed directly by future models that specifically require $\text{CO}_2$ output without converting to $r_{\text{O}_2}$.
2. **RQ Provenance Extension:** If future scientific evidence datasets provide verified commodity-specific RQ values and gas reference conditions, `calculate_respiration` can be extended to utilize them with explicit provenance.

---

## 11. Final Decision & Status Declaration

* The unauthorized volumetric $\text{CO}_2 \rightarrow \text{O}_2$ conversion has been eliminated.
* `FOOD-7` and `FOOD-8` source evidence remains untouched.
* Unsupported $\text{O}_2$-dependent respiration calculations evaluate to `CalculationStatus.UNKNOWN`.
* `UNKNOWN` states propagate safely through Phase 4 to Phase 5 (`UNKNOWN != FEASIBLE`).
* Positive controls confirm valid calculations remain unblocked.
* Zero optimizer files or evidence datasets were modified.

**FINAL DECISION:** **DV5-C CONTROLLED SAFETY CORRECTION COMPLETE**
