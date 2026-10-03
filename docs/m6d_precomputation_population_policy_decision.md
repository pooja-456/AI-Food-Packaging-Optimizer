# M6-D Precomputation Population Policy Decision

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Source Basis
**EXISTING FACT**: This architectural decision builds strictly upon:
- `m6a_optimization_state_identity_contract.md`
- `m6a_progressive_tier_contract_freeze.md`
- `m6b5a_precomputed_state_store_contract.md`
- `m6b5b_canonical_optimization_state_representation.md`
- `m6b5c_precomputed_state_generation_contract.md`
- `m6b5d_exact_tier1_lookup_contract.md`
- `m6b5e_tier2_warm_start_state_selection_contract.md`
- `m6c_precomputed_state_enumeration_strategy.md`
- `m6c1_precomputation_population_policy.md`
- `m6c2_precomputation_workload_data_requirements.md`
- `m6c3_workload_telemetry_acquisition_governance.md`

## 3. Decision Question
**EXISTING FACT**: Does the current project possess a sufficient authorized basis to define which valid Optimization-State Identities should be precomputed offline?

## 4. Authorized Policy Bases
**ARCHITECTURAL CONSEQUENCE**: Forensic review of all candidate policy bases confirms that NONE of the proposed strategies currently possess a complete, authorized source basis in the project architecture.

## 5. Exhaustive Coverage
**EXISTING FACT**: Continuous physical input fields (temperature, RH, geometry) and un-collapsible Phase 4 interval bounds create an infinite continuous state space.
**ARCHITECTURAL CONSEQUENCE**: Exhaustive precomputation of the full identity space is mathematically impossible without introducing unauthorized discretization grids.

## 6. Workload-Driven Coverage
**EXISTING FACT**: M6-C1 and M6-C2 established that NO AUTHORIZED WORKLOAD DATA IS AVAILABLE.
**ARCHITECTURAL CONSEQUENCE**: Workload-driven precomputation is blocked by the complete absence of production API request logs, user session traces, and demand telemetry.

## 7. Scientific-Coverage Policy
**SOURCE-AUTHORIZED REQUIREMENT**: Scientific evidence records (e.g., M5 permeability/respiration observations) describe physical material biology. They MUST NOT be treated as user demand telemetry. The architecture does NOT authorize precomputing more states for a commodity simply because it possesses more experimental observations.

## 8. Domain Priority
**UNRESOLVED**: DOMAIN PRIORITY NOT AUTHORIZED. No project contract authorizes prioritizing specific commodities, storage conditions, or packaging use cases for precomputation.

## 9. Demand-Driven Population
**UNRESOLVED**: DEMAND-DRIVEN POPULATION NOT AUTHORIZED. No contract currently governs dynamic runtime cache population upon Tier-1 misses.

## 10. HIT-Rate Claims
**UNRESOLVED**: TIER-1 HIT-RATE TARGET NOT YET AUTHORIZED. No empirical or theoretical HIT-rate target (e.g., 80%, 95%) can be claimed without workload telemetry.

## 11. Completeness / Coverage
**ARCHITECTURAL CONSEQUENCE**: Because no population policy is authorized, the precomputed store cannot currently guarantee specific domain coverage or hit rates. An `EXACT_MISS` remains a neutral signal triggering Tier-2/Tier-3 optimization.

## 12. Minimum Missing Inputs
To move toward authorizing a population policy, the project requires:
1. **Required Data**: Production API workload telemetry logs (per M6-C2 contract).
2. **Required Architectural Decision**: Selection of an offline sampling domain strategy OR a runtime demand-driven cache write-back contract.
3. **Required Governance Decision**: Authorized workload telemetry retention, time horizon, and security policies (per M6-C3 contract).
4. **Required Domain Decision**: Authorized commodity/use-case priority definitions (if Domain Priority is chosen).

## 13. Non-Blockers
**EXISTING FACT**: The absence of a population policy does NOT invalidate or block:
- M6-A Optimization-State Identity (Frozen).
- M6-B5A Precomputed State Store Contract (Ready).
- M6-B5B Canonical Representation Contract (Ready).
- M6-B5C Precomputed State Generation Contract (Ready).
- M6-B5D Exact Tier-1 Lookup Contract (Ready).
- M6-B5E Tier-2 Warm-Start State Selection Contract (Ready).

The runtime architecture is 100% sound and operational over any valid precomputed states present in the store.

## 14. Implementation Readiness
**ARCHITECTURAL CONSEQUENCE**:
- **Runtime Tier-1 Lookup (B5D)**: READY for implementation.
- **Offline Generation Pipeline (B5C)**: READY for implementation.
- **Precomputed State Store (B5A)**: READY for implementation.
- **Offline Batch Population**: NOT READY (missing population policy & enumeration strategy).

## 15. Decision Matrix

| Policy Basis | Evidence Exists | Source Authorized | Decision |
|---|---|---|---|
| Exhaustive Coverage | NO | NO | **UNRESOLVED** (Mathematically impossible) |
| Workload-driven | NO | NO | **UNRESOLVED** (Missing workload data) |
| Historical request | NO | NO | **UNRESOLVED** (Missing API logs) |
| Predictive demand | NO | NO | **UNRESOLVED** (Missing demand models) |
| Domain priority | NO | NO | **UNRESOLVED** (Missing priority rules) |
| Scientific coverage | YES (M5) | NO | **UNRESOLVED** (Evidence != Demand) |
| Demand-driven write-back | NO | NO | **UNRESOLVED** (Missing write-back contract) |
| Hybrid policy | NO | NO | **UNRESOLVED** (Missing foundational policies) |

## 16. Final Architectural Decision
**PROPOSED DECISION**: M6-D PRECOMPUTATION POPULATION POLICY NOT YET AUTHORIZED — MISSING INPUTS IDENTIFIED.

The precomputation storage and runtime exact-lookup contracts are fully finalized and ready for implementation. However, the policy dictating *which* specific valid states should be precomputed offline remains unauthorized until real production workload telemetry or domain priority decisions are provided.

## 17. M6-E Readiness
**ARCHITECTURAL CONSEQUENCE**: READY FOR REVIEW. Milestone 6 design verification is complete. The project is ready to proceed to M6-E for the final Milestone 6 Synthesis & Hand-off Report.
