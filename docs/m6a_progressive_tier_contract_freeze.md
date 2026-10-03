# M6-A Progressive-Tier Contract Freeze

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Source Basis
**EXISTING FACT**: This document represents the final consolidation of the progressive-tier optimization architecture. It strictly relies on:
- `m6a_optimization_state_identity_contract.md`
- `m6a_tier1_addressability_contract.md`
- `m6a_tier2_compatibility_contract.md`
- The foundational M6-A optimization problem definition.

## 3. Frozen Optimization-State Identity
**SOURCE-AUTHORIZED REQUIREMENT**: The exact scientific identity of an optimization problem is frozen as the union of:
1. Phase 4 Requirement Envelope
2. Package Geometry
3. Active Objective Set
4. Resolved Eligible Candidate ID Set

## 4. Tier-1 Exact Reuse
**SOURCE-AUTHORIZED REQUIREMENT**: Tier-1 serves to provide immediate, exact reuse of precomputed optimization states. A stored state may only be reused directly if its frozen Optimization-State Identity matches the requested identity mathematically perfectly.

## 5. Tier-1 HIT/MISS
**SOURCE-AUTHORIZED REQUIREMENT**: 
- **HIT**: Identical mathematical bounds, objectives, geometry, and search space. It MUST NOT mean an approximate match, similar geometry, or intersecting candidate subsets.
- **MISS**: An exact optimization-state identity match was not found. Bypasses to Tier-2 or Tier-3.

## 6. Tier-2 Warm Start
**SOURCE-AUTHORIZED REQUIREMENT**: Tier-2 serves to accelerate convergence by seeding the optimizer with a high-quality initial population derived from a previously computed non-exact state. A Tier-2 result is a SEED, not the final answer.

## 7. Tier-2 Re-evaluation
**SOURCE-AUTHORIZED REQUIREMENT**: A selected warm-start seed must undergo mandatory re-evaluation if the current Phase 4 requirements, Geometry, or Objective Sets differ from the seed's original context. The seed does NOT inherit feasibility or objective validity. It must physically exist in the target's candidate search space. `UNKNOWN` results cannot silently become feasible.

## 8. Tier-2 Seed Selection Gap
**EXISTING FACT**: The architecture defines the safety conditions AFTER a seed has been selected (the Tier-2 Compatibility Contract). It does NOT define the mathematical algorithm (e.g., nearest-neighbor, Jaccard overlap, Euclidean threshold) for SELECTING that seed from the storage layer. 

## 9. Tier-3 Deep/Cold/Background Path
**SOURCE-AUTHORIZED REQUIREMENT**: Tier-3 serves as the fallback mechanism when Tier-1 exact reuse is unavailable and no compatible Tier-2 warm-start seed exists. It represents deep analysis, cold optimization, or background refinement. The existing architecture establishes its existence but leaves the exact algorithmic implementation open.

## 10. Progressive-Tier State Machine
**ARCHITECTURAL CONSEQUENCE**:
```
REQUEST
  ↓
CAN EXACT OPTIMIZATION-STATE IDENTITY BE ADDRESSED?
  ├── YES → TIER-1 EXACT HIT → RETURN STORED STATE
  └── NO
       ↓
CAN A SOURCE-AUTHORIZED COMPATIBLE WARM-START SEED BE SELECTED? (Algorithm TBD)
       ├── YES → TIER-2 RE-EVALUATE/REFINE
       └── NO → TIER-3 DEEP/COLD/BACKGROUND PATH
```

## 11. Precomputation Architecture
- **Precomputation itself**: SOURCE-AUTHORIZED
- **Reusable optimization states**: SOURCE-AUTHORIZED
- **Numerical lattice (array)**: NOT AUTHORIZED (fails interval/set representation)
- **Multidimensional scalar grid**: NOT AUTHORIZED (fails identity completeness)
- **Nearest-neighbor lookup**: ASSUMPTION (blocked by missing metric space definitions)
- **Approximate interpolation**: ASSUMPTION / UNRESOLVED

## 12. Architecturally Frozen Decisions
- The Optimization-State Identity dimensions.
- The prohibition of interval scalarization or midpoints.
- The separation of scientific identity from raw context caching fragmentation.
- Tier-1 Exact Hit requirements.
- Tier-2 Candidate Re-evaluation and Compatibility requirements.

## 13. Implementation Decisions Still Open
- Physical representation of the Tier-1 address (e.g., Key structure).
- Serialization syntax (e.g., JSON canonicalization).
- Hashing algorithms (e.g., SHA-256).
- Storage technology (e.g., Redis, DB).
- Warm-start seed selection algorithms (e.g., set overlap metrics, similarity).
- Cache TTL and invalidation strategies.
- Optimizer algorithmic implementation (e.g., exact vs. NSGA-II).

## 14. Remaining Architectural Gaps
**EXISTING FACT**: There are no remaining scientific or semantic gaps preventing the structural implementation of the cache. The only remaining gaps are explicit computational implementation choices.

## 15. M6-B5 Readiness
**ARCHITECTURAL CONSEQUENCE**: READY. 
- Tier-1 exact addressability semantics are formally locked.
- Tier-2 compatibility semantics are formally locked.
- Progressive-tier behavior is internally consistent.
- Remaining implementation choices (hashing, similarity logic) can safely be deferred to M6-B5 because any algorithm designed MUST strictly adhere to the frozen scientific safety bounds.

## 16. Final Decision
**PROPOSED DECISION**: The M6-A Progressive-Tier Architecture is officially frozen. M6-B5 (Optimization Lattice Generation & Lookup) may formally proceed into implementation design, strictly adhering to the Key-Value Hash paradigm instead of a rigid scalar numerical grid.
