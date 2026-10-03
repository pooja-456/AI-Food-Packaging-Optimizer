# M6-A Candidate Search Space Equivalence

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Architectural Question
"Determine the exact source-authorized semantics of Candidate Search Space and establish whether it must become part of Optimization-State Identity."

## 3. Search-Space Lifecycle
**EXISTING FACT**: 
- `filtering_result`: The deterministic output of Phase 5 constraint evaluation. It is passed as context into M6-B1.
- `eligible_candidate_materials`: A raw list of `PackagingCandidate` objects passed into the M6-B1 `OptimizationInputEnvelope`. 
- **Ordering**: The list ordering has no semantic meaning.
- **Duplicates**: Permitted by the list structure, but mathematically redundant.
- **Candidate IDs**: Deterministic UUID5 hashes of material, evidence, and thickness properties (via `CandidateBuilder`).

## 4. Filtering Criteria vs Resolved Candidate Set
**ARCHITECTURAL CONSEQUENCE**: The optimization engine is completely blind to user filtering criteria (e.g., "biodegradable = true"). It only physically receives the resolved `eligible_candidate_materials`. If Request A and Request B employ different filtering criteria but resolve to the identical list of candidate materials, they represent mathematically identical optimization problems. 

## 5. Pareto Population Trace
**EXISTING FACT**: The M6-B4B `ParetoFrontConstructor` iterates exactly over the candidates evaluated by M6-B3, which maps 1:1 with the `eligible_candidate_materials` list provided in M6-B1. The Pareto search population is controlled entirely by `eligible_candidate_materials` (Option B). `filtering_result` is purely provenance/context at this layer.

## 6. Candidate Set Equality
**ARCHITECTURAL CONSEQUENCE**: Optimization search-space equality is mathematically defined by the unordered set of Candidate IDs. 
- `[candidate_1, candidate_2]` and `[candidate_2, candidate_1]` represent the exact same optimization problem.
- `[candidate_1, candidate_2]` and `[candidate_1, candidate_2, candidate_3]` represent distinct optimization problems.

## 7. Candidate Identifier Semantics
**EXISTING FACT**: Candidate IDs are deterministic hashes mapping directly to the candidate's exact material parameters, decision variables, and evidence record. The Candidate ID alone is robustly sufficient to uniquely identify a member of the optimization search space without requiring recursive object inspection.

## 8. Filtering vs Hard Constraints
**EXISTING FACT**: 
- **Search-Space Filtering**: Excludes materials from `eligible_candidate_materials` prior to M6-B1 optimization construction.
- **Hard Constraints (Phase 5)**: Explicitly re-evaluated within the optimization loop (M6-B2B). If a candidate is Phase 5 `INFEASIBLE`, it remains physically in the search space but its objectives are flagged `UNKNOWN`, causing the M6-B4A Pareto filter to explicitly discard it.

## 9. Empty Search-Space Semantics
**EXISTING FACT**: If `eligible_candidate_materials` is an empty list, M6-B4B naturally processes 0 iterations and correctly returns a formally valid `ParetoFront` object with `candidate_count = 0` and an empty list of candidates. This is a mathematically valid "empty Pareto front", not a system error or an UNKNOWN state.

## 10. Equivalence Cases
- **Case A & B** (same candidates, different criteria): **EQUIVALENT**. Criteria are traceability; the set defines the physical space.
- **Case C** (one additional candidate): **NOT EQUIVALENT**. The extra candidate alters the mathematical bounds of the Pareto front.
- **Case D** (different ordering): **EQUIVALENT**. Pareto dominance is order-invariant.

## 11. Minimum Safe Optimization Identity
**ARCHITECTURAL CONSEQUENCE**: The Minimum Safe Optimization Identity is now:
1. Phase 4 `PackagingRequirementEnvelope`
2. `PackageGeometry`
3. `active_objectives` (unordered set)
4. `eligible_candidate_materials` (unordered set of candidate IDs)

## 12. Identity vs Traceability
**EXISTING FACT**: 
- **Optimization Identity**: Resolved candidate ID set.
- **Traceability Metadata**: Original user filtering criteria, `filtering_result` metadata, and full candidate evidence provenance. 

## 13. Architectural Outcome
**PROPOSED DECISION**: The Candidate Search Space (represented as an unordered set of candidate IDs) is an absolute, mathematically required dimension of the Optimization-State Identity. It must be hashed or encoded into the Tier 1 lattice coordinate.

## 14. Required Future Contract Changes
**PROPOSED DECISION**: The M6-B5 Lattice Schema and coordinate generation logic must be updated to formally hash the candidate search space set, the active objectives, the package geometry, and the Phase 4 requirements into the definitive Tier 1 index.

## 15. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains strictly BLOCKED until the complete unified multi-dimensional hashing function is authorized and implemented.
