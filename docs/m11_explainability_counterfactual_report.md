# Milestone M11 — Explainability & Counterfactual Analysis Report

**Project:** AI-Food-Packaging-Optimizer  
**Milestone:** M11 — Explainability + Counterfactual Analysis  
**Date:** October 1, 2026  
**Status:** **M11 VERIFIED**

---

## 1. Executive Summary

Milestone **M11 — Explainability + Counterfactual Analysis** has been successfully implemented, tested, and formally **VERIFIED**.

This milestone layer delivers deterministic explainability and counterfactual threshold analysis on top of the existing, verified M10 adaptive recommendation pipeline without altering frozen scientific equations, Phase 5 hard constraints, or Pareto dominance logic.

### Key Outcomes:
1. **Explainability & Counterfactual Schema Integration:** Created `backend/app/schemas/explainability.py` defining structured `ConstraintExplanation`, `ObjectiveExplanation`, `CounterfactualExplanation`, `EvidenceProvenanceReference`, `CandidateExplainabilityReport`, and `PipelineExplainabilitySummary`.
2. **Deterministic Explainability Engine:** Built `ExplainabilityEngine` in `scientific_engine/optimization/explainability_engine.py` to generate candidate-level feasibility reports, constraint evaluations, objective trade-offs, evidence citations, and counterfactual threshold analysis.
3. **Deterministic Counterfactual Engine:** Calculates precise threshold boundaries at which candidate feasibility or individual constraint status flips (e.g., allowable WVTR reductions or required OTR increases) using only existing evaluation data.
4. **UNKNOWN Preservation:** `UNKNOWN` feasibility/constraint status remains strictly `UNKNOWN`. Unresolved counterfactual states (`UNRESOLVED_DUE_TO_UNKNOWN`, `is_resolved=False`) are returned when data is missing; missing data is **NEVER** assigned numeric penalties or zero values.
5. **Interval Preservation:** Bounded intervals `[value_min, value_max]` are preserved without midpoint collapse across objectives and counterfactual threshold ranges.
6. **Additive API & Service Integration:** Integrated seamlessly into `RecommendationService` and REST API `POST /api/v1/recommend` without breaking existing contracts.
7. **Complete Regression Verification:** **363 / 363 PASSED** across full regression test suite (0 failures, 0 errors, 1 deprecation warning in 15.02 seconds).

---

## 2. Files Created & Modified

### Created Files:
1. **`backend/app/schemas/explainability.py`**: Pydantic models for constraint explanations, objective explanations, counterfactual threshold explanations, evidence provenance references, candidate explainability reports, and pipeline summaries.
2. **`scientific_engine/optimization/explainability_engine.py`**: Deterministic explainability and counterfactual engine.
3. **`backend/tests/test_explainability.py`**: Focused test suite covering candidate explanations, constraint logic, objective trade-offs, counterfactuals, interval preservation, provenance tracking, and API integration.
4. **`docs/m11_explainability_counterfactual_report.md`**: Milestone completion report.

### Modified Files:
1. **`backend/app/schemas/recommendation.py`**: Additively updated `CandidateEvaluationSummary` and `RecommendationResponse` with optional M11 explainability fields (`explainability` and `pipeline_explainability`).
2. **`scientific_engine/optimization/search_engine.py`**: Updated `DeterministicEnumerationSearchEngine` and `IntelligentInverseDesignSearchEngine` to invoke `ExplainabilityEngine` and attach `pipeline_explainability` to `InverseDesignSearchResult`.
3. **`backend/app/services/recommendation_service.py`**: Updated `RecommendationResponse` construction to forward `pipeline_explainability`.

---

## 3. API & Data Flow Architecture

### 3.1 Response Contract Integration (`POST /api/v1/recommend`)
The endpoint contract is updated additively. Existing response fields remain 100% backward-compatible while providing rich explainability reports:

```json
{
  "recommendation_run_id": "run-f1e2d3c4b5a6",
  "total_candidates_evaluated": 11,
  "feasible_candidates_count": 0,
  "pareto_front": { ... },
  "candidate_summaries": [
    {
      "candidate_id": "cand-001",
      "material_name": "Low-Density Polyethylene (LDPE 50 µm)",
      "constraint_status": "FEASIBLE",
      "explainability": {
        "candidate_id": "cand-001",
        "overall_feasibility_status": "FEASIBLE",
        "constraint_explanations": [ ... ],
        "objective_explanations": [ ... ],
        "provenance_reference": { ... },
        "counterfactual_explanations": [ ... ],
        "pareto_explanation": "This candidate is non-dominated under the four M6-B3 objectives."
      }
    }
  ],
  "pipeline_explainability": {
    "total_candidates_explained": 11,
    "feasible_candidates_explained": 0,
    "infeasible_candidates_explained": 0,
    "unknown_candidates_explained": 11,
    "candidate_reports": { ... }
  }
}
```

---

## 4. Counterfactual Calculation & Threshold Analysis

The counterfactual engine answers: *"What change in requirement threshold or candidate performance would cause this candidate's feasibility/constraint status to flip?"*

### 4.1 WVTR Counterfactual Rules
- **If Currently FEASIBLE** ($V_{wvtr} \le T_{wvtr}$):
  - Condition: `BECOMES_INFEASIBLE_IF`
  - Threshold: Allowable WVTR reduced below $V_{wvtr}$.
  - Explanation: `"Candidate WVTR ({V_wvtr} {unit}) currently satisfies allowable threshold (<= {T_wvtr} {unit}). It would become INFEASIBLE if maximum allowable WVTR were reduced below {V_wvtr} {unit}."`
- **If Currently INFEASIBLE** ($V_{wvtr} > T_{wvtr}$):
  - Condition: `BECOMES_FEASIBLE_IF`
  - Threshold: Allowable WVTR increased to at least $V_{wvtr}$ (or candidate WVTR reduced by $V_{wvtr} - T_{wvtr}$).
  - Explanation: `"Candidate WVTR ({V_wvtr} {unit}) exceeds allowable threshold (<= {T_wvtr} {unit}). It would become FEASIBLE if maximum allowable WVTR were increased to at least {V_wvtr} {unit}."`
- **If Currently UNKNOWN** (missing candidate or allowable WVTR):
  - Condition: `UNRESOLVED_DUE_TO_UNKNOWN` (`is_resolved=False`)
  - Explanation: `"Counterfactual threshold for moisture WVTR cannot be determined because candidate or allowable WVTR is UNKNOWN."`

### 4.2 OTR / CO2TR Counterfactual Rules
- Similar deterministic threshold bounds are computed for oxygen and carbon dioxide transmission rate requirements.

---

## 5. Forensic Compliance Self-Audit

| Ref | Self-Audit Item | Verification Result |
| :--- | :--- | :---: |
| **A** | **Files Created** | `backend/app/schemas/explainability.py`, `scientific_engine/optimization/explainability_engine.py`, `backend/tests/test_explainability.py`, `docs/m11_explainability_counterfactual_report.md` |
| **B** | **Files Modified** | `backend/app/schemas/recommendation.py`, `scientific_engine/optimization/search_engine.py`, `backend/app/services/recommendation_service.py` |
| **C** | **API Changes** | Additive optional fields `explainability` on candidate summaries and `pipeline_explainability` on recommendation response. Zero breaking changes. |
| **D** | **Explanation Data Flow** | Input Envelope $\rightarrow$ Search Engine $\rightarrow$ Candidate Evaluation $\rightarrow$ Objectives $\rightarrow$ Pareto Front $\rightarrow$ `ExplainabilityEngine` $\rightarrow$ Reports & Summaries |
| **E** | **Counterfactual Calculation Path** | Deterministically derived from candidate barrier metrics vs requirement envelope thresholds |
| **F** | **Evidence/Provenance Preservation** | Preserves evidence ID, source ID, measured vs model predicted status, and synthetic prediction warnings |
| **G** | **UNKNOWN Handling** | UNKNOWN remains strictly UNKNOWN. Unresolved counterfactual states returned; no numeric penalty scores or zeros introduced |
| **H** | **Interval Handling** | Bounded intervals `[value_min, value_max]` preserved across objectives and counterfactual threshold ranges without midpoint collapse |
| **I** | **Pareto Semantics Preservation** | Reuses M6-B4A `dominates()` and M6-B4B `ParetoFrontConstructor`. Descriptive Pareto trade-off comparisons only; zero scalar ranking |
| **J** | **M9 Baseline Preservation** | M9 `DeterministicEnumerationSearchEngine` fully intact and verified |
| **K** | **M10 Adaptive Search Preservation** | M10 `IntelligentInverseDesignSearchEngine` fully intact and verified |
| **L** | **Test Count** | **363 / 363 passed** across full test suite (7 new M11 tests in `test_explainability.py`) |
| **M** | **Test Failures / Errors** | **0 failures, 0 errors** |
| **N** | **Warnings** | 1 deprecation warning (`httpx` in Starlette `TestClient`) |
| **O** | **Genuine Limitations** | Counterfactual analysis is currently limited to deterministic single-variable boundary thresholds (WVTR, OTR, CO2TR). Multi-variable degradation kinetics (Arrhenius/Q10) remain intentionally excluded per scope boundaries. |

---

## 6. Test Suite Execution Summary

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
collected 363 items

backend\tests\test_benchmark_infrastructure.py ....................      [  5%]
backend\tests\test_candidate_construction.py .............               [  9%]
backend\tests\test_candidate_scientific_evaluation.py ....               [ 10%]
backend\tests\test_canonical_representation.py .................         [ 14%]
backend\tests\test_constraints.py ...................................... [ 25%]
........................                                                 [ 31%]
backend\tests\test_database_m5b1.py ...                                  [ 32%]
backend\tests\test_explainability.py .......                             [ 34%]
backend\tests\test_food_evidence.py ............                         [ 38%]
backend\tests\test_gas_exchange.py ...                                   [ 38%]
backend\tests\test_health.py ..                                          [ 39%]
backend\tests\test_ingestion_m5b3.py ............                        [ 42%]
backend\tests\test_intelligent_search.py ........                        [ 44%]
backend\tests\test_inverse_design_search.py .......                      [ 46%]
backend\tests\test_lattice_contract.py .....                             [ 48%]
backend\tests\test_material_evidence.py .......                          [ 50%]
backend\tests\test_microbial.py ....                                     [ 51%]
backend\tests\test_moisture.py ....                                      [ 52%]
backend\tests\test_objective_evaluation.py .....                         [ 53%]
backend\tests\test_optimization_schemas.py .......                       [ 55%]
backend\tests\test_packaging_request.py ..................               [ 60%]
backend\tests\test_packaging_requirements.py ....                        [ 61%]
backend\tests\test_pareto_dominance.py .......                           [ 63%]
backend\tests\test_pareto_front_construction.py .......                  [ 65%]
backend\tests\test_physics_audit_corrections.py .......                  [ 67%]
backend\tests\test_physics_traceability.py ..                            [ 68%]
backend\tests\test_physics_unknowns.py ...                               [ 68%]
backend\tests\test_pre_storage_validation.py ....................        [ 74%]
backend\tests\test_precomputed_state_store.py ....................       [ 79%]
backend\tests\test_property_inference.py ........                        [ 82%]
backend\tests\test_property_status.py ........                           [ 84%]
backend\tests\test_recommendation_pipeline.py ....                       [ 85%]
backend\tests\test_respiration.py .....                                  [ 86%]
backend\tests\test_schema_m5b2.py .....                                  [ 87%]
backend\tests\test_sorption.py .....                                     [ 89%]
backend\tests\test_tier1_lookup.py .................                     [ 94%]
backend\tests\test_tier2_handoff.py .................                    [ 98%]
tests\test_m4_pipeline.py ....                                           [100%]

======================= 363 passed, 1 warning in 15.02s =======================
```

---

## 7. Final Status

**FINAL STATUS:** **M11 VERIFIED**

Milestone M11 (Explainability + Counterfactual Analysis) is complete, fully tested, and verified.
