# M6-A Final Optimization-State Identity

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Previously Resolved Decisions
**EXISTING FACT**: 
- Raw commodity-only identity is scientifically unsafe (collapses distinct evidence).
- Raw full food-context identity is too strict (fragments cache on fallback).
- Phase 3 Resolved State lacks a canonical equivalence rule.
- Phase 4 Envelope is necessary but insufficient.
- Epistemic origin is pure traceability.
- Optimization Context includes Geometry and Objectives.
- Active Objectives behave as unordered sets.

## 3. Complete Identity Definition
**ARCHITECTURAL CONSEQUENCE**: Based on the prior analyses, the conceptual optimization problem appears bounded by:
A. Phase 4 `PackagingRequirementEnvelope`
B. `PackageGeometry`
C. `active_objectives` (unordered set)

## 4. Field-by-Field Traceability
- **Phase 4 Envelope**: Dictates the exact numerical bounds for Phase 5 hard constraints and the numerical targets for M6-B3 objectives.
- **PackageGeometry**: (`surface_area_m2`, `headspace_volume_cm3`, `product_mass_kg`). Dictates the candidate-specific recalculation scaling (e.g., package-level WVTR) in M6-B2B.
- **Active Objectives**: (`List[str]`). Dictates the dimensional space and directional goals evaluated by M6-B4A Pareto dominance.

## 5. Hidden Dependency Audit
**ARCHITECTURAL CONSEQUENCE**: A critical hidden dependency exists in the `OptimizationInputEnvelope`. 
Could two requests have identical Phase 4 requirements, Geometry, and Objectives, but produce different Pareto fronts? **YES**.
The `OptimizationInputEnvelope` explicitly contains `filtering_result` and `eligible_candidate_materials`. If Request A evaluates the entire material database, while Request B applies a user-filter restricting the search space to "only biodegradable materials", their resulting Pareto Fronts will be fundamentally different. The optimization identity MUST include the candidate search space / filtering constraints, which are currently unaccounted for in A, B, and C.

## 6. Food Context Interaction
**EXISTING FACT**: Utilizing the Phase 4 `PackagingRequirementEnvelope` as the identity basis perfectly resolves the earlier Food Context conflicts. By indexing the mathematical limits output by Phase 4, the architecture safely groups requests with differing raw inputs (e.g., Gala vs. Apple) that fell back to identical scientific states, while successfully separating requests that produced distinctly different physical constraints.

## 7. Epistemic Context Interaction
**EXISTING FACT**: The epistemic origin (`PropertyStatusEnum`, `EvidenceTier`) remains purely as traceability metadata. Two Phase 4 envelopes with identical numeric bounds and `CalculationStatus` will safely share an optimization state, regardless of whether the bounds were measured or predicted.

## 8. Objective Set Semantics
**EXISTING FACT**: 
- Objective order does NOT matter.
- Duplicate objectives do NOT create a distinct optimization problem.
- Objective direction (MIN/MAX) intrinsically comes from the objective definition.
- Omitted objectives alter the dimensionality of the Pareto front.

## 9. Package Geometry Semantics
**EXISTING FACT**: The three mandatory fields (`surface_area_m2`, `headspace_volume_cm3`, `product_mass_kg`) are sufficient and exclusively control geometric scaling in the M6-B2B evaluation pipeline.

## 10. UNKNOWN / Partial State Semantics
**EXISTING FACT**: An optimization state where a requirement is `UNKNOWN` deterministically restricts constraint feasibility to `UNKNOWN` and explicitly halts Pareto dominance. Two requests with identical `UNKNOWN` Phase 4 parameters are mathematically equivalent and share the identical empty/provisional optimization outcome.

## 11. Identity vs Representation
**EXISTING FACT**: This analysis defines the *conceptual identity dimensions* required to uniquely bound an optimization problem. The physical representation (hashing algorithm, cache string serialization, float rounding tolerance, Redis binning) remains a future implementation concern completely decoupled from this theoretical definition.

## 12. Final Architectural Decision
**PROPOSED DECISION**: OPTION B — OPTIMIZATION-STATE IDENTITY STILL BLOCKED.
The conceptual optimization identity cannot be frozen. The discovery of the candidate search space / filtering dependency proves that Phase 4 + Geometry + Objectives is insufficient. Without formally incorporating the filtering parameters into the identity definition, the Tier 1 lattice would dangerously serve global Pareto fronts to restricted requests.

## 13. Remaining Unresolved Questions
- How is the `filtering_result` or search space constraint mathematically represented in the caching identity?
- Does the Tier 1 lattice strictly assume a globally unfiltered search space (forcing filtered requests to Tier 2), or does it attempt to cache filtered Pareto fronts?

## 14. M6-B5 Gate
**ARCHITECTURAL CONSEQUENCE**: M6-B5 remains strictly BLOCKED. Do not proceed to lattice discretization until the search-space identity dimension is formally resolved.
