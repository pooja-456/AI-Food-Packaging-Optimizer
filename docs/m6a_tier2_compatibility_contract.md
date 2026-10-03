# M6-A Tier-2 Warm-Start Compatibility Contract

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Purpose
This document formally establishes the architectural rules for safely utilizing a previously computed non-exact optimization state as an initial seed ("warm start") for a new optimization request. It defines the scientific and computational boundaries that must be respected during state injection.

## 3. Tier-1 Exact Reuse vs Tier-2 Warm Start
**EXISTING FACT**:
- **Tier-1 Exact Reuse**: The requested Optimization-State Identity exactly matches the cached identity. The cached Pareto front is returned immediately as the final scientifically valid answer.
- **Tier-2 Warm Start**: The cached state is NOT mathematically identical to the requested state. The cached candidates serve ONLY as an initialization aid (a seed) and MUST NOT be returned as the final optimization result without undergoing mandatory scientific re-evaluation or refinement.

## 4. Warm-Start Eligibility
**SOURCE-AUTHORIZED REQUIREMENT**: Eligibility determines whether a stored state or candidate may be conceptually retrieved to act as an initial population seed. Eligibility does not guarantee final scientific correctness. 

## 5. Warm-Start Validity
**SOURCE-AUTHORIZED REQUIREMENT**: Validity determines whether an injected warm-start candidate survives scientific scrutiny under the *current* request's rules. A seed MUST NOT bypass the formal scientific validity evaluations (M6-B2B, Phase 5, M6-B3).

## 6. Requirement Envelope Compatibility
**ARCHITECTURAL CONSEQUENCE**: If the Phase 4 requirement envelope changes (e.g., stricter OTR targets), previously cached candidates may no longer be feasible. They are eligible to serve as warm starts, but they MUST undergo Phase 5 constraint re-evaluation to establish validity for the new request.

## 7. Package Geometry Compatibility
**ARCHITECTURAL CONSEQUENCE**: If Package Geometry changes (`surface_area_m2`, `headspace_volume_cm3`, `product_mass_kg`), the physical transmission rates and concentrations mathematically scale. Cached candidates are eligible for warm start but MUST undergo M6-B2B candidate recalculation and M6-B3 objective re-evaluation before Pareto dominance can be assessed.

## 8. Active Objective Compatibility
**ARCHITECTURAL CONSEQUENCE**: If the Active Objective Set changes, the previously cached objective values are incomplete or mathematically irrelevant to the new Pareto space. Cached candidates are eligible as seeds but MUST undergo M6-B3 objective evaluation for the new active set.

## 9. Candidate Search-Space Compatibility
**SOURCE-AUTHORIZED REQUIREMENT**: If the Eligible Candidate ID Set changes, only cached candidates that physically exist within the *new* requested search space are permitted to act as valid seeds. Injecting a candidate that the new request's filters explicitly excluded (e.g., injecting a non-biodegradable cached candidate into a strictly biodegradable request) violates the core M6-B1 filtering contract.

## 10. Constraint Re-evaluation
**SOURCE-AUTHORIZED REQUIREMENT**: No False Feasibility. A candidate mathematically feasible under a cached state MUST NOT inherit its feasibility for a new request. It must establish feasibility strictly against the current Phase 5 constraints.

## 11. Objective Re-evaluation
**SOURCE-AUTHORIZED REQUIREMENT**: No False Objective Validity. Cached objective values MUST NOT be assumed valid if any upstream mathematical input affecting them (Geometry, Phase 4 limits) has changed. 

## 12. UNKNOWN Handling
**SOURCE-AUTHORIZED REQUIREMENT**: An `UNKNOWN` result from a cached state MUST NOT be silently converted into a feasible or finite numerical value during warm-start injection.

## 13. Similarity / Distance Semantics
**EXISTING FACT**: NO SOURCE-AUTHORIZED NUMERICAL SIMILARITY METRIC EXISTS. The architecture dictates that Tier-2 warm starts occur but provides absolutely zero mathematical definitions for Euclidean distance, weighted similarity, or nearest-neighbor thresholds across intervals and sets.

## 14. Candidate-Level vs State-Level Warm Start
**UNRESOLVED**: The architecture implies extracting high-quality initial populations from cached states, but does not formally define whether warm-start mechanisms must retrieve entire intact `ParetoFront` objects (State-Level) or dynamically query individual `ParetoCandidate` records (Candidate-Level).

## 15. Non-Exact Context Cases

| Case | Change from Request | Classification | Reason / Re-evaluation Required |
|---|---|---|---|
| A | None (Exact match) | EXACT REUSE | Meets Tier-1 identity criteria. |
| B | Diff Phase 4 Envelope | POTENTIAL WARM START | Requires Phase 5 feasibility re-check & M6-B3 objectives. |
| C | Diff Geometry | POTENTIAL WARM START | Requires M6-B2B recalculation & M6-B3 objectives. |
| D | Diff Objective Set | POTENTIAL WARM START | Requires M6-B3 objective re-evaluation. |
| E | Diff Candidate ID Set | POTENTIAL WARM START | M6-B4A Dominance must be rerun. Only subset-matching candidates are valid. |
| F | Diff Epistemic Origin | EXACT REUSE | Identical optimization semantics (per Decision #1C). |

## 16. Warm-Start Failure Semantics
**EXISTING FACT**: If no compatible warm-start seed is found, or if all injected seeds fail the mandatory re-evaluations, the architecture requires falling back to deep/cold optimization (Tier-3) from scratch.

## 17. Explicitly Deferred Implementation Decisions
The following mechanisms are OUT OF SCOPE and must not be implemented until an architectural resolution defines them:
- Distance / Similarity metrics
- Scoring / Thresholds / Tolerances
- Nearest-neighbor indexing algorithms
- Cache storage mechanisms (Redis, DB)
- Serialization / Hashing formats
- Interpolation / Extrapolation algorithms
- NSGA-II / Surrogate ML implementations

## 18. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains fully BLOCKED. While the safety boundaries for injecting a seed are now defined (this document), the actual *Selection Algorithm* (how to find a "similar" seed without a metric space) remains fundamentally undefined by the architecture.
