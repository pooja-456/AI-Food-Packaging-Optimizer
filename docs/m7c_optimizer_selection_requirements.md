# M7-C: Optimizer Selection Requirements Specification

## 1. Status
**PROPOSED REQUIREMENTS SPECIFICATION — AUDIT READY**

## 2. Scope & Purpose
This document establishes the formal, source-grounded **Optimizer Selection Requirements Specification** for any future Tier-3 multi-objective optimizer implementation in the AI-Based Intelligent Food Packaging Material Recommendation System.

Milestone M7-C is strictly a **REQUIREMENTS SPECIFICATION**. In accordance with project governance:
- **No optimizer algorithm is selected.**
- **No optimizer algorithms are ranked or scored.**
- **No production code is implemented.**
- **No algorithms (NSGA-II, NSGA-III, MOEA/D, Bayesian optimization) are coded.**
- **No surrogate machine learning models** or evolutionary operators are implemented.
- Existing M6 and M7 design contracts remain authoritative and immutable.

M7-C defines the mandatory technical requirements that **ANY** candidate optimizer solver must satisfy before it can be authorized for implementation.

---

## 3. Source Authority & Lineage
All requirements in this specification are derived strictly from authorized project contracts:
- `docs/scientific_knowledge_foundation.md`
- `docs/m6a_optimization_problem_definition.md`
- `docs/m6a_objective_contract.md`
- `docs/m6b1_optimization_contracts.md`
- `docs/m6b2a_candidate_construction.md`
- `docs/m6b2b_candidate_scientific_evaluation.md`
- `docs/m6b3_objective_evaluation.md`
- `docs/m6b4a_pareto_dominance.md`
- `docs/m6b4b_pareto_front_construction.md`
- `docs/m6b5a_precomputed_state_store_contract.md`
- `docs/m6b5e_tier2_warm_start_state_selection_contract.md`
- `docs/m6k_tier2_selection_strategy_evidence_audit.md`
- `docs/m7a_inverse_design_optimization_execution_contract.md`
- `docs/m7b_optimizer_algorithm_authorization_audit.md`

---

## 4. Requirement Classification Rules
For strict governance, every requirement in this document is classified under one of five formal categories:
1. **`AUTHORIZED`**: Formally frozen and authorized by an existing contract.
2. **`ARCHITECTURAL REQUIREMENT`**: Mandatory structural constraint dictated by upstream physics/system architecture.
3. **`IMPLEMENTATION REQUIREMENT`**: Contractual boundary governing code execution and schema integration.
4. **`NOT YET AUTHORIZED`**: Identified requirement whose specific parameter values or mathematical formulation remain unresolved.
5. **`NOT ESTABLISHED`**: Missing empirical benchmark or workload data that cannot be assumed without empirical testing.

---

## 5. Input Requirements
A candidate optimizer implementation MUST ingest the frozen M6-A Optimization-State Identity without modification.

| Requirement ID | Requirement Description | Classification | Source Authority |
|:---|:---|:---:|:---|
| **REQ-INP-01** | Must accept `requirement_envelope` (`PackagingRequirementEnvelope`) containing Phase 4 target OTR, WVTR, temperature, RH, and shelf-life requirements. | **AUTHORIZED** | `m6a_optimization_problem_definition.md` |
| **REQ-INP-02** | Must accept `package_geometry` (`PackageGeometry`) containing surface area, headspace volume, and product mass. | **AUTHORIZED** | `m6a_optimization_problem_definition.md` |
| **REQ-INP-03** | Must accept `active_objectives` as a list of active objective strings ($f_1 \dots f_4$). | **AUTHORIZED** | `m6a_objective_contract.md` |
| **REQ-INP-04** | Must accept `eligible_candidate_materials` as a list of `PackagingCandidate` objects passing M6-B1 search-space filtering. | **AUTHORIZED** | `m6b1_optimization_contracts.md` |
| **REQ-INP-05** | Must accept an optional `DeepOptimizerConfiguration` object specifying execution budgets and random seed. | **IMPLEMENTATION REQUIREMENT** | `m7a_inverse_design_optimization_execution_contract.md` Sec 4 |
| **REQ-INP-06** | Must accept an optional `optional_warm_start_population` list for Tier-2 seed injection. | **IMPLEMENTATION REQUIREMENT** | `m7a_inverse_design_optimization_execution_contract.md` Sec 4 |

---

## 6. Decision-Space Requirements
The candidate optimizer MUST operate exclusively over authorized decision variables in the candidate search space $\mathcal{X}$.

| Decision Variable | Variable Type | Unit / Scope | Bound Status | Classification | Source |
|:---|:---:|:---:|:---:|:---:|:---|
| `material_id` | Categorical | UUID string | M5 Verified Materials | **AUTHORIZED** | `m5a_canonical_data_model.md` |
| `layer_structure` | Categorical | `MONO` / `LAMINATE` | M5 Observed Structures | **AUTHORIZED** | `m6b2a_candidate_construction.md` |
| `total_thickness_um` | Bounded Continuous / Discrete | $\mu\text{m}$ | M5 Empirical Observations / Ranges | **AUTHORIZED** | `m6b2a_candidate_construction.md` |
| `package_geometry` | Scalar | $m^2, cm^3, kg$ | Defined in input `PackageGeometry` | **AUTHORIZED** | `m6a_optimization_problem_definition.md` |

### Prohibited Extensions:
- **REQ-DEC-01**: The optimizer MUST NOT introduce unauthorized decision variables (e.g., invented barrier coatings, unmeasured additive concentrations).
- **REQ-DEC-02**: The optimizer MUST NOT invent hypothetical material classes absent from M5 database evidence.
- **REQ-DEC-03**: The optimizer MUST NOT invent hardcoded population sizes or numerical decision-space discretization grids.

---

## 7. Objective Requirements
The future optimizer MUST preserve multi-objective trade-off semantics without scalarization.

| Objective ID | Metric / Description | Direction | Units | Classification | Source Authority |
|:---|:---|:---:|:---:|:---:|:---|
| $f_{\text{thickness}}$ | Resource / Thickness Minimization | `MINIMIZE` | $\mu\text{m}$ | **AUTHORIZED** | `m6b3_objective_evaluation.md` |
| $f_{\text{moisture\_margin}}$ | Moisture Transmission Margin beyond $WVTR_{max}$ | `MAXIMIZE` | $g/(pkg \cdot day)$ | **AUTHORIZED** | `m6b3_objective_evaluation.md` |
| $f_{\text{gas\_alignment}}$ | Gas Transmission Alignment / Target Envelope Distance | `MINIMIZE` | $cc/(pkg \cdot day)$ | **AUTHORIZED** | `m6b3_objective_evaluation.md` |
| $f_{\text{shelf\_life\_margin}}$ | Shelf-Life Margin beyond target | `MAXIMIZE` | days | **AUTHORIZED** | `m6b3_objective_evaluation.md` |

### Strict Objective Boundary Rules:
- **REQ-OBJ-01**: The optimizer MUST NOT collapse multi-objective vectors into a single scalar weighted sum ($w_1 f_1 + w_2 f_2$).
- **REQ-OBJ-02**: The optimizer MUST NOT apply composite utility ranking scores or "best material" single-score scalarization.
- **REQ-OBJ-03**: The optimizer MUST preserve interval objective values $[f_{min}, f_{max}]$ without midpoint collapse.

---

## 8. Constraint Requirements
The future optimizer MUST enforce Phase 5 hard feasibility constraints externally.

| Constraint Status | Optimizer Admissibility Rule | Classification | Source Authority |
|:---|:---|:---:|:---|
| `FEASIBLE` | Candidate is admissible to the Pareto optimization space. | **AUTHORIZED** | `m6a_optimization_problem_definition.md` Sec 3 |
| `INFEASIBLE` | Candidate is strictly disqualified from entering the Pareto front. | **AUTHORIZED** | `m6a_optimization_problem_definition.md` Sec 3 |
| `UNKNOWN` | Candidate is strictly disqualified from the deterministic Pareto front ($\text{UNKNOWN} \ne \text{FEASIBLE}$). | **AUTHORIZED** | `m6a_optimization_problem_definition.md` Sec 3 |

### Strict Constraint Boundary Rules:
- **REQ-CON-01**: The optimizer MUST NOT trade off food safety or hard constraint violations against economic or operational objectives.
- **REQ-CON-02**: The optimizer MUST NOT invent internal penalty functions that allow infeasible candidates to survive into the feasible Pareto front.
- **REQ-CON-03**: The optimizer MUST delegate constraint evaluations externally to Phase 5 / M6-B2B primitives.

---

## 9. Scientific Evaluation Pipeline Requirements
The future optimizer MUST execute scientific evaluations strictly through the existing M6 pipeline:

$$\text{Candidate Construction (B2A)} \to \text{Scientific Evaluation (B2B)} \to \text{Phase 5 Hard Constraints} \to \text{Objective Evaluation (B3)} \to \text{Pareto Processing (B4A/B4B)}$$

- **REQ-SCI-01**: The optimizer MUST NOT duplicate, bypass, or re-implement scientific physics calculations.
- **REQ-SCI-02**: The optimizer MUST pass all candidate designs through `CandidateScientificEvaluator` (M6-B2B) and `ObjectiveEvaluator` (M6-B3).

---

## 10. Evaluation-Cost & Latency Requirements
- **REQ-CST-01 (Architectural Target)**: Tier-3 deep optimization execution SHOULD target a total runtime of $< 3000\text{ ms}$ (`m6a_optimization_problem_definition.md` Sec 10).
- **REQ-CST-02 (Measured Benchmark)**: `NOT ESTABLISHED`. No empirical latency benchmarks or evaluation time profiles exist in the codebase.
- **REQ-CST-03 (Evaluation Budget Policy)**: **`EVALUATION BUDGET NOT YET AUTHORIZED`**. Authorized numerical evaluation budget values (max iterations, max function calls) remain unresolved.

---

## 11. Pareto Requirements
The future optimizer MUST produce an immutable `ParetoFront` output conforming strictly to M6-B4A and M6-B4B:

- **REQ-PAR-01**: Must identify non-dominated Pareto candidates using exact Pareto dominance primitives ($A \prec B$) defined in `m6b4a_pareto_dominance.md`.
- **REQ-PAR-02**: Must emit an immutable `ParetoFront` object conforming to `m6b4b_pareto_front_construction.md`.
- **REQ-PAR-03**: Prohibits hypervolume indicators, $\epsilon$-dominance thresholds, or R2 indicators unless explicitly authorized by project contracts.

---

## 12. Uncertainty Requirements
- **REQ-UNC-01**: The optimizer MUST preserve interval bounds $[v_{min}, v_{max}]$ and `UncertaintyProfile` on all emitted `ParetoCandidate` objects.
- **REQ-UNC-02**: The optimizer MUST NOT convert `UNKNOWN` status to known scalar values.
- **REQ-UNC-03**: **`OPTIMIZER UNCERTAINTY HANDLING STRATEGY NOT YET AUTHORIZED`**. The mathematical policy for sorting or comparing interval objective vectors during solver iterations remains unresolved.

---

## 13. Initialization & Cold-Start Requirements
- **REQ-INI-01 (Cold-Start Primacy)**: The optimizer MUST support self-contained cold-start execution directly from `eligible_candidate_materials` without requiring Tier-1 or Tier-2 success.
- **REQ-INI-02 (Warm-Start Abstraction)**: The optimizer MAY accept an optional warm-start seed population (`optional_warm_start_population`) if provided by Tier-2 handoff.
- **REQ-INI-03 (No Population Sizing)**: The optimizer specification MUST NOT hardcode population sizes, seed selection heuristics, or warm-start seed metrics.

---

## 14. Tier-2 Boundary Requirements
Per M6-K decision (`TIER-2 SELECTION STRATEGY NOT YET AUTHORIZED`):
- **REQ-T2-01**: The optimizer requirements define ONLY the optional input slot for a warm-start population.
- **REQ-T2-02**: The optimizer requirements MUST NOT define how Tier-2 warm-start seeds are retrieved, selected, or ranked from the precomputed state store.

---

## 15. Termination Requirements
- **REQ-TRM-01**: The solver engine MUST accept configurable termination parameters (`max_generations`, `max_evaluations`, `time_budget_ms`, `convergence_tolerance`).
- **REQ-TRM-02**: **`TERMINATION POLICY NOT YET AUTHORIZED`**. Hardcoded numerical values for termination thresholds MUST NOT be assigned in the specification.

---

## 16. Reproducibility & Randomness Requirements
- **REQ-REP-01**: The solver engine MUST guarantee 100% deterministic Pareto front outputs when supplied with a fixed `random_seed` and identical `DeepOptimizationInput`.
- **REQ-REP-02**: **`REPRODUCIBILITY POLICY NOT YET AUTHORIZED`**. Default numerical random seed values remain unassigned.

---

## 17. Surrogate Model Requirements
- **REQ-SUR-01**: **`SURROGATE MODEL REQUIREMENTS NOT YET AUTHORIZED`**.
- **REQ-SUR-02**: No surrogate model class (Gaussian Process, Random Forest, Neural Network), training dataset, feature representation, acquisition function, or retraining schedule is authorized. Candidate optimizers MUST NOT depend on surrogate ML models.

---

## 18. Execution Failure Requirements
The solver engine MUST implement explicit error and failure handling:

| Failure Scenario | Mandatory System Behavior | Classification | Source |
|:---|:---|:---:|:---|
| `INVALID_INPUT` | Raise `ValueError` with detailed validation context | **IMPLEMENTATION REQUIREMENT** | `m7a` Sec 17 |
| `EMPTY_SEARCH_SPACE` | Return empty `ParetoFront` (`candidate_count = 0`) | **IMPLEMENTATION REQUIREMENT** | `m7a` Sec 17 |
| `ALL_INFEASIBLE` | Return empty `ParetoFront` (`candidate_count = 0`) | **IMPLEMENTATION REQUIREMENT** | `m7a` Sec 17 |
| `ALL_UNKNOWN` | Return empty `ParetoFront` (or provisional front if requested) | **IMPLEMENTATION REQUIREMENT** | `m7a` Sec 17 |
| `EXECUTION_TIMEOUT` | Return best non-dominated `ParetoFront` discovered before timeout | **IMPLEMENTATION REQUIREMENT** | `m7a` Sec 17 |
| `EVALUATION_ERROR` | Raise `RuntimeError` isolating the failing candidate | **IMPLEMENTATION REQUIREMENT** | `m7a` Sec 17 |

---

## 19. Performance Requirements
- **REQ-PRF-01 (Target)**: Optimization execution SHOULD target $< 3000\text{ ms}$ total latency.
- **REQ-PRF-02 (Measured Benchmark)**: `NOT ESTABLISHED`. Empirical throughput and latency MUST be established via benchmarking after solver implementation.

---

## 20. Output Requirements
The solver output MUST conform to the verified M6-B4B `ParetoFront` schema:
- Must preserve all non-dominated `ParetoCandidate` objects, decision variables, objective values, objective intervals, feasibility summaries, evidence references, uncertainty profiles, and solver metadata (`OptimizationMetadata`).

---

## 21. Precomputation Compatibility Requirements
- **REQ-PRE-01**: Emitted `ParetoFront` output MUST be compatible with B5C pre-storage validation (`PreStorageValidator`) and B5A precomputed state storage (`InMemoryOptimizationStateStore`).

---

## 22. Mandatory Testing Requirements for Future Solvers
Any future candidate optimizer solver implementation MUST provide unit test suites validating:
1. Multi-objective preservation (zero scalarization, zero weighted sums).
2. Strict Phase 5 hard constraint enforcement ($\text{UNKNOWN} \ne \text{FEASIBLE}$, `INFEASIBLE` exclusion).
3. Exact Pareto dominance filtering matching `dominates()` (M6-B4A).
4. Verbatim preservation of objective intervals $[f_{min}, f_{max}]$ and uncertainty profiles.
5. Correct empty `ParetoFront` emission (`candidate_count = 0`) when search space is over-constrained.
6. 100% deterministic reproducibility when `random_seed` is fixed.
7. Independent cold-start execution without Tier-1 or Tier-2 dependencies.

---

## 23. Algorithm-Neutral Compliance Checklist
Before any specific optimizer algorithm (e.g. NSGA-II, MOEA/D, Bayesian optimization) can be authorized, it MUST be evaluated against this algorithm-neutral checklist:

- [ ] Satisfies `DeepOptimizationInput` schema requirement without adding un-authorized inputs?
- [ ] Operates strictly over authorized decision variables (`material_id`, `layer_structure`, `thickness_m`)?
- [ ] Preserves 4 active objectives in multi-objective trade-off directions (`MINIMIZE`/`MAXIMIZE`)?
- [ ] Prohibits arbitrary scalar weighting ($w_1 f_1 + w_2 f_2$) and single-score utility functions?
- [ ] Enforces Phase 5 hard constraints externally with strict $\text{UNKNOWN} \ne \text{FEASIBLE}$?
- [ ] Delegates scientific evaluations to M6-B2B and objective calculations to M6-B3?
- [ ] Preserves objective intervals $[f_{min}, f_{max}]$ without midpoint collapse?
- [ ] Emits immutable `ParetoFront` conforming strictly to M6-B4B schema?
- [ ] Emits valid empty `ParetoFront` when search space is 100% infeasible?
- [ ] Supports cold-start execution from scratch without Tier-1/Tier-2 dependencies?
- [ ] Guarantees 100% deterministic output given a fixed `random_seed`?
- [ ] Operates independently of surrogate ML models?

*Note: This checklist evaluates compliance with documented requirements ONLY. It assigns zero algorithm scores, rankings, or winner selections.*

---

## 24. Missing Requirements List
The following requirements CANNOT be finalized until explicit design contracts or benchmark evidence are provided:

1. **Optimizer Algorithm Selection**: Specific solver algorithm (NSGA-II, MOEA/D, etc.) is `NOT YET AUTHORIZED`.
2. **Population Sizing Policy**: Population size and generation limits are `NOT YET AUTHORIZED`.
3. **Termination Policy Values**: Authorized numerical values for time budget and evaluation caps are `NOT YET AUTHORIZED`.
4. **Interval Pareto Sorting Policy**: Mathematical rule for sorting interval objective vectors is `NOT YET AUTHORIZED`.
5. **Surrogate Model Specification**: Model architecture, training data, and loss function are `NOT YET AUTHORIZED`.
6. **Default Random Seed**: Default numerical reproducibility seed is `NOT YET AUTHORIZED`.
7. **Empirical Evaluation Benchmark**: Measured solver performance data is `NOT ESTABLISHED`.

---

## 25. Implementation-Readiness Matrix

| Requirement Area | Status | Source Contract | Missing Input / Decision |
|:---|:---:|:---|:---|
| **Input Contract** | **READY** | `m7a_inverse_design_optimization_execution_contract.md` | None (Reuses frozen M6-A identity) |
| **Decision Space** | **READY** | `m6b2a_candidate_construction.md` | None (Reuses authorized decision variables) |
| **Objectives** | **READY** | `m6b3_objective_evaluation.md` | None (Reuses frozen M6-B3 objectives) |
| **Constraints** | **READY** | `m6a_optimization_problem_definition.md` Sec 3 | None (Phase 5 hard constraints frozen) |
| **Scientific Evaluation** | **READY** | `m6b2b_candidate_scientific_evaluation.md` | None (Pipeline primitives verified) |
| **Pareto Output** | **READY** | `m6b4b_pareto_front_construction.md` | None (Reuses M6-B4B schema) |
| **Uncertainty** | **PARTIAL** | `m6a_optimization_problem_definition.md` Sec 6 | Solver-level interval sorting policy |
| **Cold Start** | **READY** | `m7a_inverse_design_optimization_execution_contract.md` Sec 14 | None (Cold-start primacy established) |
| **Warm Start Boundary** | **PARTIAL** | `m7a_inverse_design_optimization_execution_contract.md` Sec 15 | Tier-2 seed selection metric (M6-K) |
| **Termination Policy** | **NOT READY** | `m7a_inverse_design_optimization_execution_contract.md` Sec 16 | Authorized numerical budget thresholds |
| **Reproducibility** | **PARTIAL** | `m7a_inverse_design_optimization_execution_contract.md` Sec 18 | Default random seed assignment |
| **Surrogate Model** | **NOT READY** | `m7a_inverse_design_optimization_execution_contract.md` Sec 13 | Model specification, dataset, & loss policy |
| **Failure Handling** | **READY** | `m7a_inverse_design_optimization_execution_contract.md` Sec 17 | None (Execution failure states defined) |
| **Performance Boundary** | **PARTIAL** | `m6a_optimization_problem_definition.md` Sec 10 | Measured empirical benchmark data |
| **Precomputation Compatibility** | **READY** | `m6b5a_precomputed_state_store_contract.md` | None (B5C validator integration defined) |

---

## 26. Final Milestone Status

```
M7-C OPTIMIZER SELECTION REQUIREMENTS COMPLETE
```
