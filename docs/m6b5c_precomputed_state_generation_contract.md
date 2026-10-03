# M6-B5C Precomputed Optimization-State Generation Contract

## 1. Status
**PROPOSED DESIGN — AWAITING REVIEW**

## 2. Source Basis
**EXISTING FACT**: This generation contract builds strictly upon:
- `m6a_optimization_state_identity_contract.md`
- `m6a_progressive_tier_contract_freeze.md`
- `m6b5a_precomputed_state_store_contract.md`
- `m6b5b_canonical_optimization_state_representation.md`
- M6-B1 through M6-B4B verified modules.

## 3. Definition of a Precomputed State
**SOURCE-AUTHORIZED REQUIREMENT**: A `PrecomputedOptimizationState` generated offline is valid for Tier-1 storage if and only if:
1. Its Optimization-State Identity is complete and unambiguous.
2. The scientific evaluation pipeline has executed completely.
3. Hard-constraint feasibility and candidate objective evaluations are complete.
4. Pareto front construction has been performed according to M6-B4B rules.
5. The pre-storage validation suite passes completely.

## 4. Authorized Generation Inputs
**SOURCE-AUTHORIZED REQUIREMENT**: Offline precomputation MUST accept inputs that resolve to the four frozen Identity components:
- Phase 4 `PackagingRequirementEnvelope`
- `PackageGeometry`
- `active_objectives` (unordered set)
- `eligible_candidate_materials` (unordered set of Candidate IDs)

Inputting raw user commodity or single environmental scalars alone without resolving the complete Phase 4 requirement envelope is strictly prohibited.

## 5. State Enumeration Strategy
**UNRESOLVED**: PRECOMPUTATION STATE ENUMERATION STRATEGY NOT YET AUTHORIZED. Having formally rejected the rigid scalar grid assumption in M6-A Decision #2G, the architecture has not yet selected a specific offline population sampling strategy (e.g., demand-driven caching upon request vs. offline batch generation over historical request domains).

## 6. Scientific Evaluation Pipeline
**EXISTING FACT**: Precomputation MUST execute the verified pipeline sequentially without bypassing layers:
```
Phase 4 (Packaging Requirements)
  ↓
Phase 5 (Deterministic Constraint Filtering)
  ↓
M6-B2B (Candidate Scientific Evaluation)
  ↓
M6-B3 (Objective Value Evaluation)
  ↓
M6-B4B (Pareto Front Construction)
```

## 7. Candidate Search Space
**SOURCE-AUTHORIZED REQUIREMENT**: Candidate construction and evaluation MUST strictly evaluate candidates from the `eligible_candidate_materials` list associated with the state's Identity. Injecting candidate materials outside this list into the precomputation pipeline is prohibited.

## 8. Feasibility Semantics
**EXISTING FACT**: 
- `FEASIBLE` candidates proceed to objective evaluation.
- `INFEASIBLE` or `UNKNOWN` candidates are gracefully processed by M6-B2B, but are excluded from the final Pareto front by M6-B4B logic.
- `UNKNOWN` MUST NEVER be converted into `FEASIBLE` or `0.0`.

## 9. Active Objective Set
**SOURCE-AUTHORIZED REQUIREMENT**: The precomputed state MUST evaluate ONLY the active objectives specified in `active_objectives`. The generation pipeline MUST NOT add unrequested objectives, drop requested active objectives, or apply weighted scalar composite scores.

## 10. Pareto Result Requirements
**EXISTING FACT**: The resulting `ParetoFront` MUST preserve:
- Complete candidate identities and decision variables.
- Raw objective bounds, intervals, directions, and statuses.
- Candidate evidence references and provenance.
- The front MUST NOT be scalarized, ranked, or pruned down to a single "recommended winner."

## 11. Empty Pareto Front
**EXISTING FACT**: An empty `ParetoFront` (`candidate_count = 0`) is a valid outcome of an over-constrained scientific requirement (e.g., no material satisfies the required WVTR). An empty front is scientifically valid and MUST be stored as a valid precomputed state to prevent redundant recalculation.

## 12. Pre-Storage Validation
**PROPOSED DESIGN**: Before a generated state is passed to `store()`, it MUST satisfy these validation checks:
1. **Identity Completeness**: All 4 identity components are present and non-null.
2. **Search-Space Consistency**: All candidates in the Pareto front belong to `eligible_candidate_materials`.
3. **Objective-Set Consistency**: Objective values in the Pareto candidates match `active_objectives`.
4. **Pareto Dominance Correctness**: No candidate in the Pareto front is dominated by any other candidate in the front (per M6-B4A).
5. **No Midpoint Scalarization**: No interval values have been collapsed to scalars.

## 13. Failure Semantics
**PROPOSED DESIGN**: If any stage of the evaluation pipeline or pre-storage validation fails (e.g., Phase 4 exception, evaluation timeout, validation failure), the state is considered invalid and MUST NOT be written to the Tier-1 precomputed store.

## 14. Determinism / Reproducibility
**EXISTING FACT**: M6-B4B exact pairwise dominance is strictly deterministic. Provided the Phase 4 inputs, candidate data, geometry, and objectives are identical, the offline generation pipeline will produce identical candidate lists and non-dominated fronts.

## 15. Model / Data Version
**EXISTING FACT**: The generated `ParetoFront` carries `constraint_policy_version` and solver metadata.
**SOURCE-AUTHORIZED REQUIREMENT**: Version metadata must be stamped during generation, but remains metadata and does not alter the mathematical Optimization-State Identity.

## 16. Offline vs Runtime Boundary
**ARCHITECTURAL CONSEQUENCE**: Offline precomputation may consume arbitrary compute time to execute the pipeline. Runtime Tier-1 execution strictly queries the store for an exact match and MUST NOT re-run the generator if a valid match exists.

## 17. Tier-2 Relationship
**EXISTING FACT**: Generated states persisted by B5C provide the population repository that a future Tier-2 compatibility layer can read as warm-start seeds. B5C does not implement seed selection logic.

## 18. Explicitly Deferred Implementation Decisions
The following physical elements remain deferred:
- Generator batch orchestration / worker queues (Celery, RQ).
- Parallel/distributed worker execution logic.
- Offline state sampling / enumeration algorithms.
- Physical storage writing scripts / Redis loading scripts.
- Tier-2 similarity search algorithms.

## 19. M6-B5D Readiness
**ARCHITECTURAL CONSEQUENCE**: READY. The offline generation pipeline contract and pre-storage validation rules are complete. M6-B5D may proceed to design the final overall M6-B5 Architecture & Gating Report.
