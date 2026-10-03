# M6-C1 Precomputation Population Policy

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
- `m6c_precomputed_state_enumeration_strategy.md`

## 3. Population Policy Definition
**ARCHITECTURAL CONSEQUENCE**: A Precomputation Population Policy is the explicit set of rules that selects WHICH specific, scientifically valid Optimization-State Identities should be populated into the Tier-1 store out of the infinite continuous space. It governs population prioritization without altering the frozen Optimization-State Identity.

## 4. Policy Bases
**ARCHITECTURAL CONSEQUENCE**: Audit of potential policy bases:
- **Exhaustive**: Impossible over continuous physical input spaces.
- **Workload-Driven**: Selects states based on observed user request frequencies.
- **Demand-Predictive**: Selects states using predictive forecasting.
- **Domain-Priority**: Selects states by prioritizing specific commodities or industries.
- **Scientific-Coverage**: Selects states based on evidence density or scientific uncertainty.
- **Demand-Driven Cache Writeback**: Populates the store dynamically after runtime cache misses.

## 5. Existing Workload Data
**EXISTING FACT**: Inspection of the project repository reveals that NO AUTHORIZED WORKLOAD DATA IS AVAILABLE FOR POPULATION POLICY. The codebase contains no production API logs, user session traces, pilot demand metrics, or request frequency distributions.

## 6. Scientific Evidence vs Workload Evidence
**SOURCE-AUTHORIZED REQUIREMENT**: Scientific evidence records (e.g., the 47 material barrier observations in the M5 database) describe physical material properties and experimental observations. 
**ARCHITECTURAL CONSEQUENCE**: Scientific data MUST NOT be conflated with user-demand workload data. A commodity having more experimental permeability observations does NOT automatically authorize prioritizing that commodity for precomputation over others.

## 7. Commodity Prioritization
**UNRESOLVED**: COMMODITY PRIORITIZATION NOT AUTHORIZED. No project contract or architectural decision record authorizes prioritizing one commodity, variety, or storage condition over another for offline precomputation.

## 8. Coverage Semantics
**ARCHITECTURAL CONSEQUENCE**: "Coverage" in this architecture cannot be defined as a numerical percentage of the infinite continuous state space. Coverage can only be semantically defined as the presence of valid precomputed states within the store that satisfy specific target identities.

## 9. Tier-1 HIT Implications
**EXISTING FACT**: A Population Policy influences the empirical Tier-1 cache HIT rate, but CANNOT guarantee a specific hit percentage without production workload telemetry. An `EXACT_MISS` remains a neutral architectural signal indicating that cold/warm optimization is required.

## 10. Tier-2 Implications
**EXISTING FACT**: The precomputation population defines the candidate pool from which Tier-2 seeds can be extracted. However, because Tier-2 state selection logic remains unresolved (per B5E), population policy alone cannot guarantee a Tier-2 seed match.

## 11. Refresh / Regeneration Consequences
**ARCHITECTURAL CONSEQUENCE**: If M5 scientific evidence or Phase 4 physical equations change, precomputed states derived from those models become scientifically invalid and must be regenerated, regardless of the population policy in effect.

## 12. Representativeness Considerations
**ARCHITECTURAL CONSEQUENCE**: Selecting a population policy without production workload data risks arbitrarily overrepresenting certain test domains while ignoring actual user demand.

## 13. Policy Authorization Matrix

| Policy Basis | Existing Evidence | Authorized? | Missing Basis |
|---|---|---|---|
| Exhaustive Coverage | None (Continuous Space) | **NO** | Mathematically impossible. |
| Workload-Driven | None | **UNRESOLVED** | Missing production API request logs. |
| Demand-Predictive | None | **UNRESOLVED** | Missing predictive demand models. |
| Domain-Priority | None | **UNRESOLVED** | Missing authorized commodity priorities. |
| Scientific-Coverage | M5 Evidence Records | **UNRESOLVED** | Missing contract linking evidence count to priority. |
| Demand-Driven Writeback | None | **UNRESOLVED** | Missing runtime cache-population contract. |
| Hybrid Policy | None | **UNRESOLVED** | Missing foundational strategy authorizations. |

## 14. Missing Decisions / Data
To formally authorize a population policy in the future, the project requires:
1. Production API telemetry or an authorized user demand distribution.
2. An authorized architectural decision explicitly prioritizing specific commodities or use cases (if Domain-Priority is chosen).
3. A formal contract governing runtime cache population upon Tier-1 misses (if Demand-Driven Writeback is chosen).

## 15. Final Population Policy Status
**UNRESOLVED**: POPULATION POLICY NOT YET AUTHORIZED.
*Important Distinction*: Lacking an authorized population policy does NOT invalidate the precomputation architecture. The storage contracts (B5A), identity representation (B5B), offline generator (B5C), and exact lookup (B5D) function deterministically regardless of which valid states are populated.

## 16. M6-D Readiness
**ARCHITECTURAL CONSEQUENCE**: READY FOR REVIEW. The absence of a population policy does NOT block the verification of Milestone 6. The runtime Tier-1 exact lookup engine (B5D) and Tier-2 handoff (B5E) operate deterministically over any arbitrary set of valid stored states. The project is ready to proceed to M6-D for the final consolidated Milestone 6 verification report.
