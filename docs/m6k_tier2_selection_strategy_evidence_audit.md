# M6-K Tier-2 Selection Strategy Evidence & Authorization Audit

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Source Basis & Documents Reviewed
This forensic audit reviews the authoritative contract suite across the project:
- `docs/m6a_optimization_state_identity_contract.md`
- `docs/m6a_progressive_tier_contract_freeze.md`
- `docs/m6a_tier1_addressability_contract.md`
- `docs/m6a_tier2_compatibility_contract.md`
- `docs/m6b5a_precomputed_state_store_contract.md`
- `docs/m6b5b_canonical_optimization_state_representation.md`
- `docs/m6b5c_precomputed_state_generation_contract.md`
- `docs/m6b5d_exact_tier1_lookup_contract.md`
- `docs/m6b5e_tier2_warm_start_state_selection_contract.md`
- `docs/m6c_precomputed_state_enumeration_strategy.md`
- `docs/m6c1_precomputation_population_policy.md`
- `docs/m6c2_precomputation_workload_data_requirements.md`
- `docs/m6c3_precomputation_workload_telemetry_acquisition_governance.md`
- `docs/m6d_precomputation_population_policy_decision.md`
- `docs/m6e_precomputed_state_implementation_readiness.md`

## 3. Existing Authorized Statements
Forensic examination of all project documentation confirms the following authoritative statements:

1. **Tier-2 Warm-Start Purpose** (`m6b5e_tier2_warm_start_state_selection_contract.md` Section 3):
   - Tier-2 accelerates optimizer convergence following a Tier-1 `EXACT_MISS`.
   - Tier-2 candidates are seeds ONLY and MUST NOT be returned as final answers without mandatory re-evaluation.
2. **Tier-2 Safety Boundaries** (`m6a_tier2_compatibility_contract.md` Sections 6–12):
   - Safety re-evaluation requirements (Phase 5 hard constraints, M6-B2B candidate evaluation, M6-B3 objective evaluation) are frozen and authorized.
3. **Unresolved Selection Strategy** (`m6b5e_tier2_warm_start_state_selection_contract.md` Section 12):
   - **`TIER-2 STATE SELECTION STRATEGY NOT YET AUTHORIZED`**. The existing architecture defines safety re-evaluation bounds but does NOT authorize any numerical selection metric (Euclidean distance, Jaccard similarity, weighted interval distance, top-K nearest neighbors, or heuristic scoring).
4. **Unresolved Multi-State Rule** (`m6b5e_tier2_warm_start_state_selection_contract.md` Section 13):
   - **`TIER-2 MULTI-STATE SELECTION RULE NOT YET AUTHORIZED`**. The architecture does not define a ranking or selection rule if multiple stored states are eligible to provide seeds.

## 4. Compatibility vs Selection Analysis
The architecture strictly distinguishes **Compatibility** from **Selection**:

- **Compatibility**: Architectural rules defining whether a stored state or candidate is eligible to be considered for warm-start seed extraction.
  - *Status*: **DEFINED & FROZEN** (`m6a_tier2_compatibility_contract.md`, `m6b5e_tier2_warm_start_state_selection_contract.md`). Requires Phase 5 re-checking for envelope changes, M6-B2B recalculation for geometry changes, M6-B3 recalculation for objective changes, and candidate search-space filtering (M6-B1).
- **Selection**: A deterministic mathematical rule or metric for choosing one or more stored states out of a collection of compatible states.
  - *Status*: **NOT DEFINED / NOT AUTHORIZED**. The architecture provides zero authorization for comparing candidate states, calculating proximity, or ranking eligible candidates.

## 5. Candidate-Set Compatibility Analysis
When comparing a target request's eligible candidate set $\{A, B, C\}$ against a stored state's eligible candidate set $\{A, B\}$:
- **Contract Rule** (`m6b5e_tier2_warm_start_state_selection_contract.md` Section 7): Candidates injected as seeds MUST physically exist in the target request's `eligible_candidate_materials` list.
- **Selection Metric Status**: **`CANDIDATE-SET COMPATIBILITY RULE NOT AUTHORIZED`** for similarity ranking. The contracts define subset filtering for safety but authorize no Jaccard overlap threshold, intersection weight, or candidate-set distance metric to rank states by search-space similarity.

## 6. Requirement Compatibility Analysis
When comparing target requirement envelopes against stored requirement envelopes (temperature, relative humidity, target shelf life, OTR, WVTR, package geometry):
- **Contract Rule** (`m6a_tier2_compatibility_contract.md` Sections 6–7): Any difference in requirement bounds or geometry invalidates cached feasibility and objective values, requiring mandatory re-evaluation (Phase 5, M6-B2B, M6-B3).
- **Selection Metric Status**: **NOT AUTHORIZED**. The contracts define zero mathematical formulas for Euclidean distance, Manhattan distance, interval containment, or normalized requirement distance across interval bounds.

## 7. Objective Compatibility Analysis
When comparing target active objectives against a stored state's active objectives (e.g., target $\{f_{\text{thickness}}, f_{\text{moisture\_margin}}\}$ vs stored $\{f_{\text{thickness}}, f_{\text{moisture\_margin}}, f_{\text{shelf\_life\_margin}}\}$):
- **Contract Rule** (`m6a_tier2_compatibility_contract.md` Section 8): If active objective sets differ, cached objective values are incomplete/invalid and MUST be recalculated via M6-B3 for the target set.
- **Selection Metric Status**: **NOT AUTHORIZED**. No contract authorizes treating subset/superset objective sets as more similar or ranking identical objective sets higher than non-identical sets.

## 8. Single-State vs Multi-State Analysis
- **Single-State Selection**: NOT AUTHORIZED. No contract specifies that exactly one warm-start state should be retrieved.
- **Multi-State Selection**: **`TIER-2 MULTI-STATE SELECTION RULE NOT YET AUTHORIZED`**. No contract specifies top-K selection, multi-state population merging, or population sizing rules.

## 9. Selection Metric Analysis

| Category | Authorization Status | Supporting Contract / Document |
|:---|:---|:---|
| Physical Requirement Distance | **NOT AUTHORIZED** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 12 |
| Normalized Requirement Distance | **NOT AUTHORIZED** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 12 |
| Objective-Space Distance | **NOT AUTHORIZED** | `m6a_tier2_compatibility_contract.md` Sec 13 |
| Candidate-Set Distance / Jaccard | **NOT AUTHORIZED** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 12 |
| Hybrid Requirement-Objective Metric | **NOT AUTHORIZED** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 12 |
| Learned / ML Similarity Metric | **NOT AUTHORIZED** | `m6a_tier2_compatibility_contract.md` Sec 17 |
| Empirical Workload Similarity | **NOT AUTHORIZED** | `m6c2_precomputation_workload_data_requirements.md` Sec 6 |

## 10. Workload Telemetry Status
Per `m6c2_precomputation_workload_data_requirements.md`, `m6c3_precomputation_workload_telemetry_acquisition_governance.md`, and `m6d_precomputation_population_policy_decision.md`:
1. **Real Production Telemetry**: `ABSENT` (Zero production API request logs exist).
2. **Pilot Request Distributions**: `ABSENT` (Zero pilot request logs exist).
3. **Synthetic Demand**: `SYNTHETIC_TEST` fixtures exist exclusively for unit testing.
4. **Governance Rule**: Synthetic test fixtures MUST NOT be used as evidence for production selection strategies.

## 11. Precomputation Population Status
Per `m6c_precomputed_state_enumeration_strategy.md` and `m6d_precomputation_population_policy_decision.md`:
- Numerical grid enumeration: **NOT AUTHORIZED / MATHEMATICALLY IMPOSSIBLE**.
- Domain-priority population: **UNRESOLVED / NOT AUTHORIZED**.
- Workload-driven population: **UNRESOLVED / NOT AUTHORIZED**.
- Demand-driven cache write-back: **UNRESOLVED / NOT AUTHORIZED**.

## 12. Failure-Case Analysis

| Case | Scenario | Status | Contract Definition |
|:---:|:---|:---:|:---|
| 1 | Tier-1 MISS | **DEFINED** | Triggers B5E handoff to Tier-2 / Tier-3 fallback |
| 2 | No compatible stored state exists | **DEFINED** | Immediate fallback to Tier-3 cold optimization (`m6b5e` Sec 14) |
| 3 | Exactly one compatible state exists | **NOT DEFINED** | No selection rule authorizing automatic single-state seed extraction |
| 4 | Multiple compatible states exist | **NOT DEFINED** | `TIER-2 MULTI-STATE SELECTION RULE NOT YET AUTHORIZED` (`m6b5e` Sec 13) |
| 5 | Candidate sets are incompatible | **DEFINED** | Candidates excluded by M6-B1 filtering cannot be injected (`m6b5e` Sec 7) |
| 6 | Objective sets are incompatible | **DEFINED** | Requires M6-B3 objective recalculation (`m6a` Sec 8) |
| 7 | Target re-evaluation rejects seed | **DEFINED** | Rejected candidate seed is discarded (`m6b5e` Sec 8) |
| 8 | All candidate seeds rejected | **DEFINED** | Immediate fallback to Tier-3 cold optimization (`m6b5e` Sec 14) |

## 13. Implementation-Readiness Matrix

| Component / Mechanism | Readiness | Reason / Blocker |
|:---|:---:|:---|
| **Tier-2 Compatibility Filtering** | **READY** | Safety boundaries & re-evaluation pipeline frozen in M6-A / M6-B5E |
| **Selection Metric** | **NOT READY** | Missing mathematical formulation and authorization |
| **Single-State Selection** | **NOT READY** | Missing single-state selection rule |
| **Multi-State Selection** | **NOT READY** | Missing multi-state selection rule and cardinality |
| **Warm-Start Population Construction** | **NOT READY** | Missing seed extraction & population sizing rules |

## 14. Mandatory Decision Matrix

| Decision | Authorized? | Evidence / Contract | Missing Input |
|:---|:---:|:---|:---|
| **Tier-2 compatibility rule** | **YES** | `m6a_tier2_compatibility_contract.md`, `m6b5e_tier2_warm_start_state_selection_contract.md` | None (Safety boundaries frozen) |
| **Candidate-set relation** | **PARTIAL** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 7 | Similarity metric for partial overlap |
| **Requirement compatibility** | **PARTIAL** | `m6a_tier2_compatibility_contract.md` Sec 6–7 | Numerical distance / proximity metric |
| **Objective-set compatibility** | **PARTIAL** | `m6a_tier2_compatibility_contract.md` Sec 8 | Objective-space distance / similarity metric |
| **Selection metric** | **NO** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 12 | Mathematical formulation & authorization |
| **Single-state selection** | **NO** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 13 | Single-state selection rule |
| **Multi-state selection** | **NO** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 13 | Multi-state selection rule / cardinality |
| **Number of seeds** | **NO** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 13 | Population sizing heuristic / contract |
| **Warm-start population rule** | **NO** | `m6b5e_tier2_warm_start_state_selection_contract.md` Sec 11 | Seed extraction & population rule |
| **Numerical state similarity** | **NO** | `m6a_tier2_compatibility_contract.md` Sec 13 | Metric authorization |
| **Workload-driven selection** | **NO** | `m6c2_precomputation_workload_data_requirements.md`, `m6d_precomputation_population_policy_decision.md` | Real production API workload telemetry |

## 15. Missing Authorization Inputs
To legitimately authorize a Tier-2 selection strategy in the future, the project requires:
1. **Mathematical Selection Specification**: A formal design document defining a distance/similarity metric across requirement envelopes, geometry parameters, active objective sets, and candidate search spaces.
2. **Cardinality & Multi-State Rule**: Formal specification of whether single-state, top-$K$, or population-level seed extraction is used.
3. **Empirical Workload Telemetry**: Production or pilot API request logs to benchmark acceleration vs re-evaluation overhead (per M6-C2 contract).
4. **Governance Approval**: Workload telemetry governance and retention policies (per M6-C3 contract).

## 16. Final Finding

```
M6-K TIER-2 SELECTION STRATEGY NOT YET AUTHORIZED
```
