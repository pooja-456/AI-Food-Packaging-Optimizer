# M6-B5E Tier-2 Warm-Start State Selection Contract

## 1. Status
**PROPOSED DESIGN — AWAITING REVIEW**

## 2. Source Basis
**EXISTING FACT**: This design contract builds upon:
- `m6a_optimization_state_identity_contract.md`
- `m6a_tier2_compatibility_contract.md`
- `m6a_progressive_tier_contract_freeze.md`
- `m6b5a_precomputed_state_store_contract.md`
- `m6b5b_canonical_optimization_state_representation.md`
- `m6b5c_precomputed_state_generation_contract.md`
- `m6b5d_exact_tier1_lookup_contract.md`

## 3. Purpose of Tier-2
**SOURCE-AUTHORIZED REQUIREMENT**: Tier-2 serves to accelerate convergence when Tier-1 yields an `EXACT_MISS`. It retrieves a previously computed non-exact state or candidate population to seed the optimization pipeline. Tier-2 MUST NOT be treated as exact reuse or returned as a final answer without scientific re-evaluation.

## 4. Tier-1 vs Tier-2

| Dimension | Tier-1 Exact Reuse | Tier-2 Warm Start |
|---|---|---|
| **Identity Requirement** | 100% Exact Equivalence | Non-Exact / Compatible Context |
| **Output Type** | Final ParetoFront Answer | Initial Seed / Candidate Population |
| **Re-evaluation** | None | Mandatory (Phase 5, M6-B2B, M6-B3) |
| **Feasibility Inheritance** | Preserved | Explicitly Prohibited |
| **Objective Validity** | Preserved | Must be recalculated |

## 5. Tier-2 Input
**SOURCE-AUTHORIZED REQUIREMENT**: The input to Tier-2 selection is the requested Optimization-State Identity (Phase 4 Envelope, Geometry, Active Objectives, Eligible Candidate IDs) and the available collection of stored `PrecomputedOptimizationState` records.

## 6. Compatibility Requirements
**SOURCE-AUTHORIZED REQUIREMENT**: Per M6-A Decision #3B:
- **Phase 4 Requirement Differences**: Stored candidates MUST undergo Phase 5 constraint re-evaluation.
- **Geometry Differences**: Stored candidates MUST undergo M6-B2B candidate evaluation and M6-B3 objective recalculation.
- **Active Objective Differences**: Stored candidates MUST have their objective values recalculated for the new active set.

## 7. Candidate Search-Space Compatibility
**SOURCE-AUTHORIZED REQUIREMENT**: A stored candidate solution MUST NOT be injected as a Tier-2 seed unless its Candidate ID physically exists in the target request's `eligible_candidate_materials` list. Injecting materials excluded by M6-B1 filters is strictly prohibited.

## 8. Feasibility Re-evaluation
**SOURCE-AUTHORIZED REQUIREMENT**:
- Feasibility is NOT inherited from stored states.
- A stored `FEASIBLE` candidate must be re-tested against current Phase 5 constraints.
- A stored `UNKNOWN` candidate MUST NOT be converted to `FEASIBLE`.
- A stored `INFEASIBLE` candidate cannot serve as a valid seed unless explicit re-evaluation under relaxed requirements restores feasibility.

## 9. Objective Validity
**SOURCE-AUTHORIZED REQUIREMENT**: Stored objective values are bound to the specific context under which they were generated. If geometry, requirements, or objective sets change, the cached objective values are invalid and MUST be re-calculated via M6-B3.

## 10. Pareto Seed Semantics
**SOURCE-AUTHORIZED REQUIREMENT**: Extracting seeds from a stored `ParetoFront` yields a population of candidate decision variables and barrier properties. The stored `ParetoFront` record itself remains completely immutable in the store.

## 11. Mandatory Re-evaluation
**ARCHITECTURAL CONSEQUENCE**: The conceptual pipeline for Tier-2 seed injection is:
```
Extract Candidate Seeds from Stored State
  ↓
Filter against Target Candidate Search Space (M6-B1)
  ↓
Phase 5 Hard-Constraint Re-evaluation
  ↓
M6-B2B Candidate Scientific Evaluation (Target Geometry)
  ↓
M6-B3 Objective Evaluation (Target Objectives)
  ↓
Seed Initial Population into Tier-3 / Optimizer Pipeline
```

## 12. Similarity / Selection Strategy
**UNRESOLVED**: TIER-2 STATE SELECTION STRATEGY NOT YET AUTHORIZED. The existing architecture defines the safety bounds for seed injection (B5E sections 6–11), but does NOT authorize any numerical metric (Euclidean distance, Jaccard candidate similarity, weighted interval distance, top-K nearest neighbors, or heuristic scoring) for searching/selecting candidate states from the store.

## 13. Multiple Compatible States
**UNRESOLVED**: TIER-2 MULTI-STATE SELECTION RULE NOT YET AUTHORIZED. The architecture does not define a ranking or selection rule if multiple stored states are eligible to provide seeds.

## 14. No Compatible State
**SOURCE-AUTHORIZED REQUIREMENT**: If no compatible precomputed state is found, or if all extracted seeds fail target re-evaluation, the system immediately falls back to Tier-3 (Cold Optimization from scratch).

## 15. Result Integrity
**SOURCE-AUTHORIZED REQUIREMENT**: Tier-2 seed selection MUST NOT alter, overwrite, or mutate any stored precomputed state or Pareto front in the storage engine.

## 16. Enumeration Independence
**EXISTING FACT**: Tier-2 operates over whatever precomputed states currently exist in the store. It operates independently of the offline state enumeration strategy (which remains unresolved per B5C).

## 17. Performance Claims
**EXISTING FACT**: Tier-2 acceleration is an architectural goal. No O(1), sublinear, or latency guarantees are authorized without empirical benchmarking of the re-evaluation pipeline.

## 18. Explicitly Deferred Decisions
The following items are deferred until a formal mathematical selection decision is authored:
- Distance / Similarity metrics (Euclidean, Jaccard, Hausdorff).
- Top-K nearest-neighbor search algorithms.
- Candidate population sampling / pruning heuristics.
- Storage index structures for multi-dimensional similarity querying.
- Integration with iterative solver algorithms (NSGA-II).

## 19. M6-B6 Readiness
**ARCHITECTURAL CONSEQUENCE**: READY. The complete M6-B5 design contract suite (B5A Store, B5B Canonical Representation, B5C Generation, B5D Exact Lookup, B5E Tier-2 Handoff) is formally finalized. The project is now ready to consolidate the complete M6-B5 Architectural Verification Report before proceeding to M6-B6.
