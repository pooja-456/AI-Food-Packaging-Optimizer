# M6-C Precomputed-State Enumeration Strategy

## 1. Status
**PROPOSED DESIGN — AWAITING REVIEW**

## 2. Source Basis
**EXISTING FACT**: This architectural audit relies directly upon:
- `m6a_optimization_state_identity_contract.md`
- `m6a_progressive_tier_contract_freeze.md`
- `m6b5a_precomputed_state_store_contract.md`
- `m6b5b_canonical_optimization_state_representation.md`
- `m6b5c_precomputed_state_generation_contract.md`
- `m6b5d_exact_tier1_lookup_contract.md`
- `m6b5e_tier2_warm_start_state_selection_contract.md`

## 3. Enumeration Problem Definition
**ARCHITECTURAL CONSEQUENCE**: Enumeration is the strategy for selecting WHICH specific Optimization-State Identities should be precomputed offline and populated into the Tier-1 store. Enumeration governs population selection only; it does NOT alter the frozen Optimization-State Identity definition.

## 4. Enumerated State Components
**EXISTING FACT**: An enumerated state consists of:
- **Phase 4 Requirement Envelope**: Continuous and interval-valued physical requirements.
- **Package Geometry**: Continuous scalar geometry inputs.
- **Active Objective Set**: Unordered set of active objective identifiers.
- **Eligible Candidate ID Set**: Unordered set of candidate material UUIDs.

None of these dimensions possess a native, discrete, finite scalar resolution without an explicit authorization decision.

## 5. Numerical Grid Authorization
**EXISTING FACT**: Per M6-A Decision #2G and M6-B5C, a rigid, multidimensional scalar lattice array was NOT formally mandated and is structurally incompatible with interval/set identity bounds.
**UNRESOLVED**: NUMERICAL GRID ENUMERATION NOT YET AUTHORIZED. No numerical bin sizes, domains, or boundaries have been authorized for offline sampling.

## 6. Exhaustive Enumeration
**ARCHITECTURAL CONSEQUENCE**: Because Phase 4 requirements and Package Geometry contain infinite, continuous numerical ranges, exhaustive enumeration of the full optimization state space is mathematically impossible.

## 7. Structured Offline Sampling
**UNRESOLVED**: STRUCTURED OFFLINE SAMPLING NOT AUTHORIZED. The architecture has not defined sampling density, continuous interval step sizes, or coverage metrics for generating states offline.

## 8. Historical / Request-Derived Enumeration
**UNRESOLVED**: HISTORICAL ENUMERATION NOT AUTHORIZED. The project currently possesses no authorized historical request dataset, telemetry log, or production request distribution to drive offline population.

## 9. Demand-Driven Enumeration
**UNRESOLVED**: DEMAND-DRIVEN ENUMERATION NOT AUTHORIZED. Populating the Tier-1 store dynamically upon runtime cache misses is conceptually plausible, but no architectural contract currently authorizes a hybrid runtime write-back strategy for precomputation.

## 10. Hybrid Enumeration
**UNRESOLVED**: HYBRID ENUMERATION NOT AUTHORIZED.

## 11. Completeness vs Coverage
**EXISTING FACT**: 
- An `EXACT_MISS` at Tier-1 does NOT mean the user request is scientifically invalid or unresolvable.
- It merely indicates that the requested Optimization-State Identity does not exist in the precomputed store. The system falls back to Tier-2 or Tier-3.

## 12. Tier-1 Implications
**EXISTING FACT**: Tier-1 lookup operates with complete independence from the enumeration strategy. `lookup_exact()` simply queries whatever valid states happen to reside in the store. If an exact match is present, it yields `EXACT_HIT`; otherwise, it yields `EXACT_MISS`.

## 13. Tier-2 Implications
**EXISTING FACT**: The precomputed population density affects the likelihood of finding a compatible Tier-2 warm-start seed. However, because the Tier-2 similarity metric remains unresolved (per B5E), population density alone cannot guarantee a warm-start hit.

## 14. Data Availability
**EXISTING FACT**: The current project database contains scientific evidence records (e.g., M5 material barrier observations). 
**ARCHITECTURAL CONSEQUENCE**: Scientific evidence records describe material properties, NOT user request frequency or workload demand. Using scientific datasets to fabricate user-request demand distributions is explicitly prohibited. Workload evidence is currently absent.

## 15. Commodity / Scientific Context
**SOURCE-AUTHORIZED REQUIREMENT**: Precomputed states represent resolved Phase 4 requirement envelopes, package geometry, active objectives, and candidate ID sets. Enumeration strategies MUST NOT reintroduce raw biological food context into the optimization identity layer.

## 16. Population Size
**UNRESOLVED**: PRECOMPUTED STATE POPULATION SIZE NOT YET DETERMINABLE. Because state enumeration dimensions, sampling frequencies, and workload distributions are completely unresolved, calculating state counts, storage footprints, or memory feasibility is impossible without fabricating data.

## 17. Offline / Runtime Boundary
**EXISTING FACT**:
- **Offline Domain**: State selection strategy, precomputation execution (B5C), pre-storage validation, and storage writing (B5A).
- **Runtime Domain**: Tier-1 exact lookup (B5D), Tier-2 seed handoff (B5E), and Tier-3 cold optimization.

## 18. Regeneration / Version Consequences
**ARCHITECTURAL CONSEQUENCE**: If Phase 4 physical equations, M5 material evidence records, or M6-B1 candidate definitions change, affected precomputed states in the store become scientifically obsolete and require offline regeneration.

## 19. Decision Matrix

| Strategy | Status | Reason / Missing Dependency |
|---|---|---|
| Exhaustive Grid | **NOT AUTHORIZED** | Mathematically impossible over continuous fields. |
| Structured Offline Sampling | **UNRESOLVED** | Missing authorized sampling intervals and domains. |
| Historical / Request-Derived | **UNRESOLVED** | Missing production request workload logs. |
| Demand-Driven Write-back | **UNRESOLVED** | Missing runtime cache-population contract. |
| Hybrid Strategy | **UNRESOLVED** | Missing foundational strategy authorizations. |

## 20. Missing Authorizations
To authorize an enumeration strategy in a future milestone, the project must formally decide:
1. Whether offline precomputation uses fixed scientific benchmarks or demand-driven runtime caching.
2. The specific numerical sampling domains for Phase 4 requirements and package geometry if offline sampling is selected.
3. The cache invalidation and state regeneration policy upon M5 evidence updates.

## 21. M6-C Final Status
**UNRESOLVED**: ENUMERATION STRATEGY NOT YET AUTHORIZED.

## 22. M6-D Readiness
**ARCHITECTURAL CONSEQUENCE**: READY FOR REVIEW. The absence of an authorized offline enumeration strategy does NOT block the runtime architecture. Tier-1 exact lookup (B5D) and Tier-2 handoff (B5E) function deterministically over any arbitrary set of valid precomputed states. The project is ready to proceed to M6-D for the final consolidated Milestone 6 verification report.
