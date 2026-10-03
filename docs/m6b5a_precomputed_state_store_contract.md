# M6-B5A Precomputed Optimization-State Store Contract

## 1. Status
**PROPOSED DESIGN — AWAITING REVIEW**

## 2. Source Basis
**EXISTING FACT**: This design contract relies strictly on the frozen architectural definitions from:
- `m6a_optimization_state_identity_contract.md`
- `m6a_progressive_tier_contract_freeze.md`
- `m6a_tier1_addressability_contract.md`
- M6-B1 and M6-B4 schemas (e.g., `OptimizationInputEnvelope`, `ParetoFront`).

## 3. Precomputed Optimization State
**PROPOSED DESIGN**: The conceptual entity `PrecomputedOptimizationState` serves as the fundamental record in the storage layer. It encapsulates the exact mathematical boundaries that produced an optimization result, the result itself, and the associated provenance metadata, explicitly isolating the Identity from the Result.

## 4. Identity Fields
**SOURCE-AUTHORIZED REQUIREMENT**: The Identity Fields exclusively define the mathematical optimization problem and govern exact Tier-1 reuse. They are explicitly limited to:
- Phase 4 `PackagingRequirementEnvelope`
- `PackageGeometry`
- `active_objectives` (unordered set)
- `eligible_candidate_materials` (unordered set of Candidate IDs)

## 5. Result Fields
**EXISTING FACT**: The Result Fields exclusively contain the solved output.
- `ParetoFront` (including its nested `List[ParetoCandidate]`)

## 6. Metadata Fields
**EXISTING FACT**: Metadata Fields describe the computation and lifecycle but MUST NOT silently alter the optimization identity.
- `optimization_run_id`
- `timestamp`
- `solver_metadata` (e.g., execution time, algorithm name)
- `constraint_policy_version`

## 7. Exact Lookup Contract
**PROPOSED DESIGN**: `lookup_exact(identity)` -> `EXACT_HIT` | `EXACT_MISS`
- **EXACT_HIT**: The stored state's Identity Fields are mathematically and structurally equivalent to the requested Identity.
- **EXACT_MISS**: No exact reusable state is available. Bypasses to Tier-2 or Tier-3.
*Note: The implementation of this lookup (e.g., hashing logic) remains deferred.*

## 8. Write Contract
**PROPOSED DESIGN**: `store(state)`
- **Identity Completeness**: The store MUST reject states lacking any of the four frozen Identity components.
- **Result Completeness**: The store MUST reject states lacking a properly formed `ParetoFront`.
- **Duplicate Identity**: If the store receives a state with an identity identical to a pre-existing state, the implementation must define overwrite vs. discard semantics (typically, newer solver versions overwrite, or identical versions discard to preserve older timestamps).

## 9. Pareto Front Preservation
**SOURCE-AUTHORIZED REQUIREMENT**: The stored `ParetoFront` MUST be preserved verbatim. The storage layer MUST NOT silently truncate candidate lists, alter objective interval bounds, drop `UNKNOWN` constraint statuses, or simplify `CandidateEvidenceReference` provenance data merely to compress storage footprint.

## 10. UNKNOWN / INFEASIBLE / EMPTY Front Semantics
**EXISTING FACT**: 
- **Empty Front**: The M6-B4B contract legally produces a `ParetoFront` with `candidate_count = 0`. This is a scientifically valid outcome of an over-constrained problem and MUST be eligible for storage.
- **UNKNOWN/INFEASIBLE**: Candidates with these statuses are legally evaluated by M6-B2B and gracefully rejected by M6-B4A. Their presence (or absence via exclusion) in the Pareto front is correct and MUST be preserved as calculated.

## 11. State Validity and Versioning
**EXISTING FACT**: The `ParetoFront` schema includes `constraint_policy_version` and `solver_metadata`.
**UNRESOLVED**: The architecture does not formally establish whether a bump in `constraint_policy_version` actively invalidates an existing Tier-1 hit, or whether the Version is considered part of the cache key (Identity) vs. a metadata expiration trigger.

## 12. State Immutability
**PROPOSED DESIGN**: A `PrecomputedOptimizationState`, once successfully persisted, MUST be treated as strictly immutable. If the underlying scientific models (Phase 3/Phase 4) or constraint policies change, the system must generate an entirely new state rather than mutating an existing record, ensuring perfect traceability between the stored Pareto front and its mathematical inputs.

## 13. Tier-2 Compatibility Hook
**SOURCE-AUTHORIZED REQUIREMENT**: To support future Tier-2 selection, the stored state MUST publicly expose its Identity Fields (specifically the Phase 4 bounds, Geometry, Objectives, and Candidate IDs). 
**PROPOSED DESIGN**: The storage layer must eventually support querying or iterating these exposed identity fields so a Tier-2 compatibility layer can assess suitability. The storage layer itself does NOT compute similarity.

## 14. Failure Semantics
**PROPOSED DESIGN**:
- **Exact State Absent**: Yields `EXACT_MISS`.
- **Malformed/Incomplete State**: Must be treated as `EXACT_MISS` and flagged for eviction.
- **Corrupted Result**: Must be treated as `EXACT_MISS`.
- **Duplicate Identity on Write**: Idempotent discard (if identical version) or targeted overwrite (if newer version).

## 15. Storage Technology Decision
**EXISTING FACT**: The foundational architecture mandates "fast retrieval" but does not dictate the persistence layer. 
**PROPOSED DESIGN**: STORAGE TECHNOLOGY NOT YET AUTHORIZED. The contract is agnostic to whether the implementation utilizes Redis, PostgreSQL, DocumentDB, or flat files.

## 16. Explicitly Deferred Decisions
The following physical mechanisms remain fully OUT OF SCOPE:
- Physical serialization formats (JSON canonicalization, protobufs).
- Cryptographic hashing of Identity fields (e.g., SHA-256).
- Unordered set hashing algorithms.
- Floating-point normalization / serialization.
- Storage technology (Redis, Postgres, etc.).
- TTL / Cache invalidation strategies.
- Tier-2 similarity search algorithms.

## 17. M6-B5B Readiness
**ARCHITECTURAL CONSEQUENCE**: READY. The abstract data contract and operational semantics for the Precomputed Optimization-State Store are completely formalized. M6-B5B may proceed to design the concrete hashing and serialization implementation for this store.
