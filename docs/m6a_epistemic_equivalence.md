# M6-A Epistemic Equivalence

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Existing Epistemic States
**EXISTING FACT**: The architecture employs epistemic tracking across three layers:
- Phase 3 inference: `PropertyStatusEnum` (measured, literature, inferred, unknown).
- Phase 4 physics: `CalculationStatus` (CALCULATED, PARTIALLY_CALCULATED, UNKNOWN).
- M6-B1 candidates/objectives: `EvidenceTier` (TIER_1_EMPIRICAL, TIER_2_PREDICTIVE_QSAR), `UncertaintyType` (DETERMINISTIC_POINT, BOUNDED_INTERVAL, QSAR_CONFIDENCE_INTERVAL, UNKNOWN).

## 3. Numerical Representation
**EXISTING FACT**: In Phase 4, the output of the mathematical models is housed in a `ScientificResult`. This explicitly bounds uncertainty using `value`, `minimum_value`, `maximum_value`, and `uncertainty_range`. Epistemic status dictates the *source* of the bounds, but the bounds themselves are strictly numerical.

## 4. Phase 5 Treatment
**EXISTING FACT**: Phase 5 (`ConstraintEvaluation`) determines hard feasibility exclusively by applying mathematical operators (`<`, `>=`, `in_range`) against the numeric bounds (`required_range` vs `material_range`). It explicitly ignores `PropertyStatusEnum` or `EvidenceTier` when calculating boolean feasibility, relying entirely on the numerical interval geometry.

## 5. Objective / Pareto Treatment
**EXISTING FACT**: M6-B4A (`pareto.py`) implements Pareto dominance by extracting `value_min` and `value_max` from `ObjectiveValue` to establish worst-case vs best-case multi-objective dominance. It checks for `CalculationStatus.UNKNOWN` but does NOT distinguish between empirical or predictive intervals.

## 6. Identical Interval / Different Status
**ARCHITECTURAL CONSEQUENCE**: If Case A (requirement interval [10,20], status = measured) and Case B (requirement interval [10,20], status = inferred) share identical numeric bounds, Phase 5 produces identical constraints and M6-B3/B4 produces identical Pareto dominance geometries. They are mathematically indistinguishable by the optimization engine and may safely share the same optimization state.

## 7. UNKNOWN Semantics
**EXISTING FACT**: If a requirement is `UNKNOWN` (via `CalculationStatus`), both Phase 5 and M6-B4A explicitly short-circuit. M6-B4A states: "If any objective is UNKNOWN, we cannot establish dominance." Two requests sharing identical `UNKNOWN` optimization boundaries will correctly produce an identical empty or indeterminate Pareto outcome.

## 8. Point vs Degenerate Interval
**EXISTING FACT**: M6-B4A seamlessly treats a scalar point value (`value=15`) identically to a degenerate interval (`[15, 15]`) via its min/max fallback logic (`wc_a = obj_a.value_max if obj_a.is_interval else obj_a.value`). They are functionally equivalent optimization states.

## 9. Measured / Inferred / Predicted / Literature
**EXISTING FACT**: These labels (`PropertyStatusEnum`) are entirely consumed by the Phase 3 to Phase 4 transition to generate appropriate traceability warnings. They do not penetrate the numeric logic of the Phase 5 evaluator or the M6-B4 Pareto filter. For optimization reuse, they are completely interchangeable *provided their numerical bounds are identical*.

## 10. Scientific Metadata vs Optimization Identity
**EXISTING FACT**: Epistemic status is vital scientific metadata (Traceability). It is NOT an optimization-state identity dimension. Excluding epistemic status from the lattice key does not violate scientific integrity because the optimizer only physically operates on the numerical requirement boundaries that the epistemic status generated.

## 11. Safe Reuse Rule
**SOURCE-AUTHORIZED REQUIREMENT**: "Same numerical requirement + different epistemic status = same optimization state." The existing project schemas authorize treating differing epistemic states with identical numerical requirements as equivalent for optimization reuse.

## 12. Architectural Finding
**PROPOSED DECISION**: Epistemic status must NOT be part of the Optimization-State Identity. Identity must be governed solely by the numerical boundaries (point, min, max), geometry, active objectives, and `CalculationStatus` of the requirements.

## 13. Required Future Contract Change
**PROPOSED DECISION**: The final definition of Optimization-State Identity (the cache key) must explicitly strip epistemic provenance flags (like `PropertyStatusEnum` or `EvidenceTier`) and hash only the resolved numerical intervals and active objectives.

## 14. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains BLOCKED until the complete mathematical hashing formula for the numerical intervals is formalized.
