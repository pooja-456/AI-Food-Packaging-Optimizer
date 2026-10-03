# M6-B5D Exact Tier-1 Lookup Contract

## 1. Status
**PROPOSED DESIGN — AWAITING REVIEW**

## 2. Source Basis
**EXISTING FACT**: This runtime lookup contract builds directly upon:
- `m6a_optimization_state_identity_contract.md`
- `m6a_tier1_addressability_contract.md`
- `m6b5a_precomputed_state_store_contract.md`
- `m6b5b_canonical_optimization_state_representation.md`
- `m6b5c_precomputed_state_generation_contract.md`

## 3. Lookup Input
**SOURCE-AUTHORIZED REQUIREMENT**: The runtime Tier-1 lookup engine receives as input ONLY the frozen Optimization-State Identity:
1. Phase 4 `PackagingRequirementEnvelope`
2. `PackageGeometry`
3. `active_objectives` (unordered set)
4. `eligible_candidate_materials` (unordered set of Candidate IDs)

Inputting raw user commodity, evidence tier, or filtering rationale into the lookup engine is strictly prohibited.

## 4. Exact Identity Matching
**SOURCE-AUTHORIZED REQUIREMENT**: `lookup_exact(requested_identity)` -> `EXACT_HIT` | `EXACT_MISS`
- **EXACT_HIT**: The requested identity is mathematically identical across all 4 identity components to a valid stored state.
- **EXACT_MISS**: The requested identity does not match any valid stored state.

## 5. Canonical Representation Relationship
**SOURCE-AUTHORIZED REQUIREMENT**: The lookup engine must map the incoming `requested_identity` to its `Canonical Representation` (per B5B contract) and query the storage layer (per B5A contract). The lookup succeeds if and only if an exact match of the canonical representation exists in the store.

## 6. Interval Matching
**SOURCE-AUTHORIZED REQUIREMENT**: Interval Phase 4 requirements MUST match exactly in bounds and operators:
- `[value_min, value_max]` with operator `GE` matches ONLY `[value_min, value_max]` with operator `GE`.
- Different lower bounds, upper bounds, or comparison operators result in `EXACT_MISS`.

## 7. UNKNOWN / ABSENT Semantics
**SOURCE-AUTHORIZED REQUIREMENT**:
- A field carrying `status=UNKNOWN` matches ONLY another state with `status=UNKNOWN` for that field.
- An `ABSENT` (None) field matches ONLY another `ABSENT` field.
- `UNKNOWN` vs `ABSENT` comparison yields `EXACT_MISS`.

## 8. Floating-Point Semantics
**EXISTING FACT**: Per B5B contract, `FLOATING-POINT CANONICALIZATION NOT YET AUTHORIZED`.
**ARCHITECTURAL CONSEQUENCE**: Float matching requires exact identity representation without numerical tolerances, epsilon ranges, or rounding. Requests differing by minute floating-point variations (e.g., `4.000000000000001` vs `4.0`) will yield `EXACT_MISS`.

## 9. Set-Valued Identity Matching
**SOURCE-AUTHORIZED REQUIREMENT**: 
- `active_objectives` matching is order-invariant (`{A, B}` matches `{B, A}`).
- `eligible_candidate_materials` Candidate ID matching is order-invariant (`{id1, id2}` matches `{id2, id1}`).

## 10. State Validity
**SOURCE-AUTHORIZED REQUIREMENT**:
- If exact identity exists and state is `VALID`: Yields `EXACT_HIT`.
- If exact identity exists but state is `INVALID` or `CORRUPTED`: Yields `EXACT_MISS` and triggers state eviction.
- If exact identity exists but state is `INCOMPLETE`: Yields `EXACT_MISS`.

## 11. Duplicate Exact States
**PROPOSED DESIGN**: If multiple valid states share an identical identity (e.g., from re-runs), the store returns the record with the newest timestamp or highest policy version.

## 12. Empty Pareto Front
**EXISTING FACT**: An exact match on a precomputed state with a valid empty `ParetoFront` (`candidate_count = 0`) is an `EXACT_HIT`. It accurately returns the precomputed proof of unfeasibility.

## 13. Result Integrity
**SOURCE-AUTHORIZED REQUIREMENT**: Upon an `EXACT_HIT`, the lookup layer MUST return the stored `ParetoFront` verbatim without recalculating objectives, modifying bounds, filtering candidates, or scalarizing ranks.

## 14. HIT Semantics
**SOURCE-AUTHORIZED REQUIREMENT**: `EXACT_HIT` immediately returns the stored `ParetoFront` to the caller, setting `solver_metadata.cache_hit = True`.

## 15. MISS Semantics
**SOURCE-AUTHORIZED REQUIREMENT**: `EXACT_MISS` signals that Tier-1 exact reuse cannot fulfill the request. The system hands off the request to Tier-2 (Warm-Start) or Tier-3 (Cold Optimization).

## 16. Approximation Prohibition
**SOURCE-AUTHORIZED REQUIREMENT**: Tier-1 lookup has ZERO approximation semantics. It MUST NOT perform nearest-neighbor lookups, scalar range snapping, or partial objective matching.

## 17. Enumeration Independence
**EXISTING FACT**: Tier-1 lookup semantics operate independently of how states are precomputed offline. Lookup simply queries whatever valid precomputed states currently reside in the store.

## 18. Runtime Handoff
**ARCHITECTURAL CONSEQUENCE**:
- On `EXACT_HIT`: Short-circuits solver pipeline, returns cached `ParetoFront`.
- On `EXACT_MISS`: Short-circuits cache layer, forwards `OptimizationInputEnvelope` to Tier-2 / Tier-3.

## 19. Explicitly Deferred Decisions
The following physical mechanisms are deferred:
- Hash algorithm implementation (SHA-256 vs BLAKE3).
- Key lookup storage engines (Redis `GET`, SQL `SELECT`).
- Memory cache TTL and eviction algorithms (LRU, LFU).
- Tier-2 warm-start similarity algorithms.

## 20. M6-B5E Readiness
**ARCHITECTURAL CONSEQUENCE**: READY. The runtime exact lookup contract is completely specified. M6-B5E may proceed to draft the final consolidated M6-B5 Architectural Synthesis & Verification Report.
