# M6-A Progressive-Tier Architectural Reconciliation

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Source Documents
- `docs/m6a_optimization_state_identity_contract.md`
- `docs/m6a_lattice_architectural_validity.md`
- `docs/m6a_tier1_addressability_resolution.md`
- `docs/m6a_warm_start_state_selection_contract.md`
- Original progressive response-tier research/design materials
- M6-A optimization problem definition

## 3. Tier-1 Contract
**SOURCE-AUTHORIZED REQUIREMENT**: Fast retrieval, exact state reuse, precomputation of optimization states.
**IMPLEMENTATION ASSUMPTION**: "Lattice" representation, scalar coordinate querying, bypassing Phase 4 deterministic engines.
**UNRESOLVED**: Cache lookup timing (before or after Phase 4 scientific resolution) and exact representation algorithm.

## 4. Tier-2 Contract
**SOURCE-AUTHORIZED REQUIREMENT**: Warm-start refinement, precomputed seed availability, candidate injection into optimizer.
**IMPLEMENTATION ASSUMPTION**: Nearest-neighbor selection, distance calculations.
**UNRESOLVED**: Mathematical similarity definition, candidate/objective compatibility rules.

## 5. Tier-3 Contract
**SOURCE-AUTHORIZED REQUIREMENT**: Deep optimization, cold optimization from scratch, background refinement.
**EXISTING FACT**: The architecture mandates falling back to Tier-3 whenever Tier-1 and Tier-2 mechanisms fail to provide a safe, rapid solution.

## 6. Precomputation Requirement
**ARCHITECTURAL CONSEQUENCE**: Precomputation is fundamentally required to be a **collection of reusable optimization states** (Outcome B). The architectural usage of the word "lattice" serves as a conceptual metaphor for state space coverage, while the assumption that it must physically be a scalar geometric grid is an unverified implementation detail that mathematically contradicts the interval-based Phase 4 requirement bounds.

## 7. Exact Reuse vs Warm Start

| Concept | Source-authorized? | Existing definition? |
|---|---|---|
| Exact optimization-state reuse | **YES** | **YES** (Frozen Identity) |
| Warm-start refinement | **YES** | **NO** |
| Nearest state | **NO** (Implementation Assumption) | **NO** |
| Compatible state | **YES** (Implied "suitable seed") | **NO** |
| Similar state | **NO** (Implementation Assumption) | **NO** |
| Distance | **NO** (Implementation Assumption) | **NO** |
| Similarity score | **NO** (Implementation Assumption) | **NO** |

## 8. Failure / Miss Semantics
**EXISTING FACT**: The architecture specifies that if Tier-1 (exact reuse) is unavailable, the system attempts Tier-2 (warm-start). If no suitable precomputed state exists for Tier-2, the system falls back to Tier-3 (cold optimization).
**UNRESOLVED**: Because the compatibility conditions for a Tier-2 warm start do not mathematically exist, the system has no authorized mechanism to determine when a Tier-2 failure occurs vs when a seed is safe to use.

## 9. Architectural Contradiction Analysis
**ARCHITECTURAL CONSEQUENCE**: The current architecture contains both **missing contracts** and **direct contradictions**. 
- **Contradiction**: The Tier-1 lookup design historically assumed querying a continuous scalar grid using raw environmental inputs. However, the true mathematical Optimization Identity (which dictates scientific safety) is interval-valued, set-valued, and biologically dependent. A scalar geometric lattice cannot safely represent the true optimization problem.
- **Missing Contract**: Tier-2 explicitly requires a "suitable seed," but suitability is mathematically undefined across non-scalar bounds, leaving the warm-start engine without operational rules.

## 10. Missing Contracts
Before any precomputed cache or lattice can be implemented, the architecture board must formally author:
1. **Tier-1 Addressability Contract**: Defining how non-scalar Phase 4 intervals and UUID sets are hashed, serialized, or grouped into a retrievable cache key.
2. **Tier-2 Compatibility Contract**: Defining the strict mathematical tolerances (geometry scaling, interval overlap, objective matching) required to safely inject a non-exact cached candidate into a new optimization run.

## 11. M6-B5 Readiness
**ARCHITECTURAL CONSEQUENCE**: **NOT READY — MISSING ARCHITECTURAL CONTRACTS**. M6-B5 (Optimization Lattice Generation and Lookup) cannot proceed. The physical layout of the cache (Grid vs. Key-Value) and the warm-start logic (Nearest-Neighbor vs. Tolerance-Compatibility) remain unresolvable under the current source definitions.

## 12. Required Future Decisions
**PROPOSED DECISION**: The architecture must explicitly separate the **Precomputed State Cache** (which must be a non-geometric Hash/KV store handling intervals/sets) from the **Tier-2 Compatibility Engine** (which must define physical tolerances rather than Euclidean distance). This redesign is explicitly OUT OF SCOPE for the current analysis and must be authorized by a new architectural decision record.
