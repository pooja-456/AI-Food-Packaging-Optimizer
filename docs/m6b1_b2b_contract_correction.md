# M6-B1 to M6-B2B Contract Correction Report

**Project**: AI-Based Intelligent Food Packaging Material Recommendation System
**Purpose**: M6-B1 Contract Correction for M6-B2B Implementation
**Date**: 2026-09-29

---

## 1. Discovered Contract Gap
During the preparation for the M6-B2B (Candidate Scientific Evaluation) milestone, it was discovered that the `CandidateScientificEvaluationResult` schema completely lacked fields to store Phase 5 constraint evaluation results.

## 2. Why It Blocks B2B
M6-B2B requires the evaluation engine to combine both Phase 4 candidate-specific calculations (e.g., recalculated gas exchange, shelf life) and Phase 5 hard constraint filtering into a single cohesive output. Without fields to store the constraint results (`FEASIBLE`, `INFEASIBLE`, `UNKNOWN`) or uncertainty profiling, the M6-B2B engine is blocked from completing its output contract.

## 3. Existing Contract Limitation
Prior to the correction, `CandidateScientificEvaluationResult` contained only Phase 4 outputs:
- `overall_status` (Phase 4 `CalculationStatus`)
- Updated Phase 4 requirements (Moisture, Gas, Microbial, Shelf Life)
- `traceability` (Phase 4 `ScientificTraceability`)

There were no fields for:
- Phase 5 `constraint_results`
- Phase 5 `overall_feasibility`
- `uncertainty`
- `warnings`
- `failure_reasons`

## 4. Corrected Contract Design
The schema in `backend/app/schemas/optimization.py` was extended minimally to incorporate existing, standardized M6-B1 enums and models. The new fields added are:
```python
    constraint_profile: Optional['CandidateConstraintStatus'] = Field(default=None)
    uncertainty_profile: Optional['UncertaintyProfile'] = Field(default=None)
    warnings: List[str] = Field(default_factory=list)
    failure_reasons: List[str] = Field(default_factory=list)
```

## 5. Phase 4 / Phase 5 Separation
The new design strictly preserves the conceptual boundary:
- **Phase 4**: Remains represented by `overall_status: CalculationStatus` (e.g., `CALCULATED`, `PARTIALLY_CALCULATED`).
- **Phase 5**: Is encapsulated entirely inside the `constraint_profile: CandidateConstraintStatus`, whose `overall_status` is a `ConstraintStatus` (e.g., `FEASIBLE`, `INFEASIBLE`, `UNKNOWN`).
This prevents a scenario where an uncomputable Phase 4 model silently becomes an "INFEASIBLE" candidate without explicit constraint traceability.

## 6. Uncertainty Representation
The `uncertainty_profile` leverages the existing M6-B1 `UncertaintyProfile` and `UncertaintyType` taxonomy (`KNOWN`, `BOUNDED_INTERVAL`, `QSAR_CONFIDENCE_INTERVAL`, `UNKNOWN`).

## 7. Warning / Reason Representation
Instead of hard-coding enum reasons (which lack extensibility), lightweight `List[str]` fields for `warnings` and `failure_reasons` were added. This allows descriptive, traceable text without forcing constraints to fit a predefined hierarchy.

## 8. Backward Compatibility
The new schema fields were typed as `Optional` and/or provided with `default=None` and `default_factory=list`. No existing M6-B1 object construction is broken.

## 9. Tests
A new test suite function `test_m6b2b_candidate_evaluation_result_correction` was added to `backend/tests/test_optimization_schemas.py`. 
It successfully proves that:
- Phase 4 results and Phase 5 constraints coexist cleanly.
- Phase 4 `CALCULATED` + Phase 5 `INFEASIBLE` is representable.
- Phase 4 `PARTIALLY_CALCULATED` + Phase 5 `UNKNOWN` is representable.
- No objectives or Pareto fields bleed into the contract.

## 10. Explicit Statement
**M6-B2B WAS NOT IMPLEMENTED.**
This milestone executes a schema correction only. No Phase 4 equations, Phase 5 constraints, objective evaluations, or Pareto rankings were coded or executed. M6-B2B implementation remains halted pending audit approval of this contract change.
