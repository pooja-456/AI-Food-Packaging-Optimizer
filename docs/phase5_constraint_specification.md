# Phase 5 — Deterministic Hard-Constraint Filtering Specification

## Overview

Phase 5 evaluates candidate packaging materials against Phase 4 `PackagingRequirementEnvelope` objects using strict, evidence-driven, deterministic hard constraints.

**Target Scope:** Phase 5 terminates at candidate feasibility assessment (`FEASIBLE`, `INFEASIBLE`, `UNKNOWN`). It does **NOT** rank materials, score candidates, perform Pareto optimization, execute inverse design, or make final packaging recommendations.

---

## 1. Input / Output Pipeline Location

```
[User Request]
       │
       ▼
[Phase 1 & 3: Input Validation & Property Inference]
       │
       ▼
[Phase 4: Scientific Requirement Engine]
       │  (PackagingRequirementEnvelope)
       ▼
[Phase 5: Deterministic Hard-Constraint Filtering Engine]
       │  (FilteringResult & List[CandidateFeasibility])
       ▼
[Future Phase 6+: Lattice Lookup / Pareto Optimization / Inverse Design]
```

---

## 2. Comparison Semantics

Comparison operators are derived strictly from Phase 4 physics requirement semantics:

| Constraint Type | Direction | Operator | Rationale |
|---|---|---|---|
| **Oxygen Transmission Rate (OTR)** | Minimum Required Transmission | `>=` (`GE`) | The packaging film must transmit **at least** the required O₂ flux to sustain respiration at steady-state equilibrium (EMAP) and prevent anaerobiosis. |
| **Carbon Dioxide Transmission Rate (CO₂TR)** | Minimum Required Transmission | `>=` (`GE`) | The packaging film must transmit **at least** the required CO₂ flux to prevent toxic accumulation and fermentation injury. |
| **Water Vapor Transmission Rate (WVTR)** | Maximum Allowable Transmission | `<=` (`LE`) | The packaging film must **not exceed** the maximum allowable moisture flux over the target shelf life to prevent moisture gain/loss deterioration. |

---

## 3. Classification Logic

Each candidate material is evaluated against all applicable barrier requirements and classified as follows:

- **`FEASIBLE`**: All evaluated constraints have numeric evidence and are **definitively satisfied** (`mat_min >= req_max` for `GE`, `mat_max <= req_min` for `LE`).
- **`INFEASIBLE`**: At least one evaluated constraint is **definitively violated** (`mat_max < req_min` for `GE`, `mat_min > req_max` for `LE`).
- **`UNKNOWN`**: No constraints are violated, but at least one constraint cannot be determined due to missing evidence, unit mismatch, incompatible test conditions, or interval overlap (`UNCERTAIN`).

---

## 4. Evidence Compatibility & Safeguards

1. **Unit Compatibility:** Material area-normalised units (`cc/(m²·day·atm)`, `g/(m²·day)`) are compared **only** against area-normalised Phase 4 requirements (`required_otr_per_area`, `required_wvtr_per_area`). Package-level requirements without area normalization result in `status = UNKNOWN`.
2. **Temperature Matching:** Test temperature is compared against requirement storage temperature.
   - `ΔT ≤ 3.0°C`: `EXACT` match.
   - `3.0°C < ΔT ≤ 10.0°C`: `SUPPORTED` match (with warning).
   - `ΔT > 10.0°C`: `INCOMPATIBLE` match → `status = UNKNOWN`.
   - **No fakeArrhenius/Q10 factors are invented for materials.**
3. **Relative Humidity Matching:** Test RH is compared against requirement storage RH.
   - `ΔRH ≤ 5.0%`: `EXACT` match.
   - `5.0% < ΔRH ≤ 15.0%`: `SUPPORTED` match (with warning).
   - `ΔRH > 15.0%`: `INCOMPATIBLE` match → `status = UNKNOWN`.
   - **No fake humidity correction factors are invented for materials.**
4. **Multilayer Composites:** Multilayer materials use measured composite barrier properties. If a composite property is missing, the property evaluates to `UNKNOWN` (individual layer properties are not combined without a validated permeation model).
5. **Full Traceability:** Every `ConstraintEvaluation` records inputs, parameters, test conditions, evidence references, and warnings in a `ScientificTraceability` block.
