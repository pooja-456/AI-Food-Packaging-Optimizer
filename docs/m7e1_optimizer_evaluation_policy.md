# M7-E1: Optimizer Evaluation Policy & Benchmark Contract

## 1. Status
**PROPOSED EVALUATION POLICY CONTRACT — AUDIT READY**

## 2. Scope & Purpose
This document establishes the formal **Optimizer Evaluation Policy & Benchmark Contract** required before any Tier-3 multi-objective optimization algorithm can be empirically benchmarked in future trials.

Milestone M7-E1 is strictly an **EVALUATION POLICY SPECIFICATION**. In accordance with project governance:
- **No benchmark code is implemented.**
- **No benchmarks are executed.**
- **No optimizer algorithm is selected.**
- **No algorithms are ranked, scored, or assigned winners.**
- **No synthetic benchmark results are generated or fabricated.**
- **No production code or tests are modified.**

M7-E1 specifies **HOW** future empirical experiments must be conducted and logged, while explicitly classifying which numerical budgets, quality indicators, and statistical policies currently lack authorization.

---

## 3. Source Authority & Lineage
This evaluation policy traces all rules directly to authorized project contracts:
- `docs/scientific_knowledge_foundation.md`
- `docs/m6a_optimization_problem_definition.md`
- `docs/m6b1_optimization_contracts.md`
- `docs/m6b2a_candidate_construction.md`
- `docs/m6b2b_candidate_scientific_evaluation.md`
- `docs/m6b3_objective_evaluation.md`
- `docs/m6b4a_pareto_dominance.md`
- `docs/m6b4b_pareto_front_construction.md`
- `docs/m6b5a_precomputed_state_store_contract.md`
- `docs/m6b5d_exact_tier1_lookup_contract.md`
- `docs/m6b5e_tier2_warm_start_state_selection_contract.md`
- `docs/m6k_tier2_selection_strategy_evidence_audit.md`
- `docs/m7a_inverse_design_optimization_execution_contract.md`
- `docs/m7b_optimizer_algorithm_authorization_audit.md`
- `docs/m7c_optimizer_selection_requirements.md`
- `docs/m7d_optimizer_algorithm_decision_framework.md`

---

## 4. Policy Classification Rules
Every numerical threshold, budget cap, quality metric, and protocol rule in this document is classified under one of four formal categories:
1. **`AUTHORIZED`**: Formally frozen and authorized by an existing project contract.
2. **`PROVISIONAL / EXPERIMENTAL ONLY`**: Proposed rule for experimental control that does not constitute permanent production authorization.
3. **`NOT YET AUTHORIZED`**: Identified policy whose specific parameter values or mathematical formulation remain unresolved.
4. **`NOT ESTABLISHED`**: Missing empirical benchmark or workload data that cannot be assumed without empirical testing.

---

## 5. Evaluation Unit Definitions
To prevent conflation during benchmarking, the policy establishes atomic evaluation units:

| Evaluation Unit | Definition | Measurement Scope | Distinction / Rule |
|:---|:---|:---|:---|
| **Scientific Evaluation** | Single call to M6-B2B + M6-B3 for one `PackagingCandidate`. | Scientific physics calculation count | **MUST NOT** be conflated with optimizer generation count. |
| **Optimizer Generation / Iteration** | Single population iteration loop inside the solver algorithm. | Solver loop count | May contain multiple scientific evaluations. |
| **Benchmark Scenario** | Fixed optimization problem instance (Envelope + Geometry + Objectives + Search Space). | Scenario ID | Immutable problem definition. |
| **Optimization Run** | Single execution of a solver on a benchmark scenario under a specific random seed. | Execution run ID | Atomic unit of stochastic execution. |
| **Complete Experiment** | Collection of optimization runs across scenarios, algorithms, and random seeds. | Experiment ID | Full empirical benchmark trial. |

---

## 6. Benchmark Scenario Identity Standard
Every benchmark scenario MUST maintain 100% identity equivalence with the frozen M6 Optimization-State Identity:

$$\text{Benchmark Scenario Identity} = \left\langle \text{Envelope}, \; \text{Geometry}, \; \text{Active Objectives}, \; \text{Eligible Candidate IDs} \right\rangle$$

- **REQ-ID-01**: Benchmark scenarios MUST NOT include raw commodity names or biological descriptions in the optimization identity.
- **REQ-ID-02**: Benchmark scenarios MUST NOT modify or remove any component of the frozen 4-part identity.

---

## 7. Scientific Pipeline Control Protocol
Every candidate optimizer evaluated in future trials MUST execute scientific evaluation strictly through the unalterable M6 scientific pipeline:

$$\text{Candidate Construction (B2A)} \to \text{Scientific Evaluation (B2B)} \to \text{Phase 5 Hard Constraints} \to \text{Objective Evaluation (B3)} \to \text{Pareto Dominance (B4A)} \to \text{ParetoFront (B4B)}$$

- **REQ-PIP-01**: Candidate algorithms MUST NOT replace scientific physics models with proxy equations.
- **REQ-PIP-02**: Candidate algorithms MUST NOT bypass Phase 5 hard constraints ($\text{UNKNOWN} \ne \text{FEASIBLE}$).
- **REQ-PIP-03**: Candidate algorithms MUST NOT calculate custom or independent objective definitions.

---

## 8. Evaluation Budget Policy

```
EVALUATION BUDGET NOT YET AUTHORIZED
```

### Policy Audit Status:
- **Maximum Scientific Evaluations**: `NOT YET AUTHORIZED` (No numerical function evaluation cap is authorized).
- **Maximum Optimizer Generations**: `NOT YET AUTHORIZED` (No numerical generation limit is authorized).
- **Maximum Population Size**: `NOT YET AUTHORIZED` (No population sizing policy is authorized).
- **Maximum Wall-Clock Time**: `PROVISIONAL` (Architectural target $< 3000\text{ ms}$ per `m6a_optimization_problem_definition.md` Sec 10; not a measured benchmark).
- **Rule**: Literature conventions (e.g. 100 generations, 10,000 evaluations) MUST NOT be treated as authorized project policy prior to formal contract approval.

---

## 9. Termination Policy

```
TERMINATION POLICY NOT YET AUTHORIZED
```

### Policy Audit Status:
- `m7a_inverse_design_optimization_execution_contract.md` Section 16 exposes abstract configuration parameters (`max_generations`, `max_evaluations`, `time_budget_ms`, `convergence_tolerance`).
- **Rule**: Numerical thresholds, patience values, and convergence criteria MUST NOT be assigned in this policy document. They remain unresolved pending empirical benchmarking.

---

## 10. Randomness, Reproducibility & Experiment Metadata Standard
Any future empirical trial MUST log complete execution metadata to guarantee 100% reproducibility:

| Metadata Field | Field Description | Classification |
|:---|:---|:---:|
| `experiment_id` | Unique UUID for the benchmark trial | **AUTHORIZED** |
| `algorithm_id` | Solver algorithm identifier and implementation tag | **AUTHORIZED** |
| `implementation_version` | Git commit hash / version tag of solver code | **AUTHORIZED** |
| `benchmark_scenario_id` | Unique UUID of the benchmark scenario | **AUTHORIZED** |
| `random_seed` | Controlled integer seed for stochastic execution | **AUTHORIZED** |
| `python_version` | Python runtime version (e.g. 3.14.0) | **AUTHORIZED** |
| `dependency_versions` | Versions of pytest, pydantic, etc. | **AUTHORIZED** |
| `environment_hardware` | Host CPU model, RAM, OS build string | **AUTHORIZED** |

- **Default Seed Status**: `NOT YET AUTHORIZED`. No numerical seed value (e.g. `seed=42`) is assigned as a permanent project default.

---

## 11. Repeated Runs & Statistical Policy

```
REPEATED-RUN STATISTICAL POLICY NOT YET AUTHORIZED
```

### Policy Audit Status:
- **Number of Repetitions**: `NOT YET AUTHORIZED` (The number of independent stochastic runs, e.g. 10, 30, or 50, is unresolved).
- **Statistical Significance Tests**: `NOT YET AUTHORIZED` (Wilcoxon signed-rank test, Mann-Whitney U test, or confidence interval thresholds are unresolved).
- **Reporting Metrics**: `PROVISIONAL ONLY` (Empirical trials may report mean, median, standard deviation, and min/max provisionally once repeated runs are authorized).

---

## 12. Uncertainty Evaluation Protocol
Benchmarking protocols MUST observe solver handling of scientific uncertainty without altering core contracts:
- **Interval Preservation**: Emitted `ParetoCandidate` records MUST preserve interval objective values $[f_{min}, f_{max}]$ emitted by M6-B3.
- **UNKNOWN Exclusion**: Candidates evaluated as `UNKNOWN` under Phase 5 MUST NOT enter the deterministic `ParetoFront`.
- **Prohibited Conversions**: Benchmarks MUST NOT apply interval midpoint collapse, pessimistic/optimistic scalar bounds, or probabilistic penalties unless explicitly authorized by a design contract.

---

## 13. Pareto Quality Indicator Status

```
PARETO QUALITY METRIC NOT YET AUTHORIZED
```

### Policy Audit Status:
- **Hypervolume Indicator**: `NOT YET AUTHORIZED`.
- **Generational Distance (GD / IGD)**: `NOT YET AUTHORIZED`.
- **Epsilon Indicator ($\epsilon$)**: `NOT YET AUTHORIZED`.
- **Spread / Diversity Index**: `NOT YET AUTHORIZED`.
- **Benchmark Data Rule**: Experiments MUST log raw non-dominated `ParetoFront` points so that quality metrics can be computed retroactively if a metric is authorized in the future.

---

## 14. Feasible Discovery Tracking Protocol
Future empirical trials MUST record constraint filtering performance transparently:
- `scientific_evaluations_count`: Total M6-B2B calls.
- `feasible_candidates_count`: Count of candidates evaluated as `FEASIBLE`.
- `infeasible_candidates_count`: Count of candidates evaluated as `INFEASIBLE`.
- `unknown_candidates_count`: Count of candidates evaluated as `UNKNOWN`.
- `first_feasible_eval_index`: Evaluation index where the first `FEASIBLE` candidate was discovered.

No artificial penalties or constraint scalarizations may be introduced into these counts.

---

## 15. Wall-Clock Latency Protocol
Wall-clock timing MUST isolate solver overhead from scientific calculation time:

$$\text{Total Wall-Clock Time} = \text{Preprocessing Time} + \text{Scientific Evaluation Time} + \text{Optimizer Overhead} + \text{Postprocessing Time}$$

- **REQ-TIM-01**: Timestamps MUST be recorded using high-resolution monotonic timers (`time.perf_counter_ns()`).
- **REQ-TIM-02**: Architectural latency targets ($< 3000\text{ ms}$) MUST NOT be reported as empirical results prior to benchmark execution.

---

## 16. Resource Measurement Protocol
Empirical benchmark trials SHOULD track host system resource utilization:
- `peak_ram_mb`: Peak resident set size (RSS) RAM in megabytes.
- `cpu_utilization_pct`: Average CPU core utilization percentage.
- `process_count`: Number of active execution worker processes.

No arbitrary hardware scoring functions may be created.

---

## 17. Benchmark Data Source Classification

| Data Source Category | Admissibility for M7-E Benchmarks | Governance Rule |
|:---|:---:|:---|
| **A. Scientific Evidence Records (M5)** | **ADMISSIBLE** | Primary empirical source (47 evidence units, 11 materials, 34 barrier observations). |
| **B. Synthetic Unit-Test Fixtures** | **ADMISSIBLE (Correctness Only)** | Validates schema compliance; CANNOT serve as performance benchmark evidence. |
| **C. Synthetic Benchmark Scenarios** | **PROVISIONAL** | Useful for edge-case coverage; MUST be explicitly tagged as `SYNTHETIC_SCENARIO`. |
| **D. REAL_PRODUCTION Workload Telemetry** | **ABSENT** | Zero production request logs exist (`m6c2`). |
| **E. REAL_PILOT Workload Telemetry** | **ABSENT** | Zero pilot request logs exist (`m6c2`). |
| **F. DEMO Workload Data** | **PROVISIONAL** | Synthetic demonstration scenarios; CANNOT replace real production demand. |

---

## 18. Scenario Representativeness Standard
Per `m6c2_precomputation_workload_data_requirements.md` and `m6d_precomputation_population_policy_decision.md`:
- Synthetic benchmark scenarios CANNOT claim to represent actual user demand in production.
- Representativeness claims require real production API workload logs or an authorized domain-priority policy.

---

## 19. Fair Comparison Experimental Controls
To ensure objective, unbiased benchmarking during M7-E trials, all candidate algorithms MUST be evaluated under identical experimental controls:
1. **Identical Search Space**: Exactly the same `eligible_candidate_materials` input.
2. **Identical Scientific Pipeline**: Exactly the same M6-B2B and M6-B3 evaluation code.
3. **Identical Execution Budgets**: Exactly the same evaluation caps (`max_evaluations`) and time limits (`time_budget_ms`).
4. **Identical Hardware/Software Environment**: Executed on the same physical host machine under the same OS and Python runtime.

---

## 20. Warm-Start & Tier-2 Boundary Policy
Per M6-K decision (`TIER-2 SELECTION STRATEGY NOT YET AUTHORIZED`):
- **Primary Benchmark Path**: Cold-start optimization (Condition A) is the primary benchmark path and MUST be tested independently.
- **Warm-Start Benchmark Path**: Warm-start optimization (Condition C) MUST NOT be benchmarked until a Tier-2 seed selection policy is formally authorized.

---

## 21. Precomputation Tier Separation
Future benchmark trials MUST evaluate and log optimization tiers under separate experimental conditions:
- **Condition A (Cold-Start Tier 3)**: Optimizer executes from scratch over search space $\mathcal{X}$.
- **Condition B (Tier-1 Exact Hit)**: Instant precomputed state lookup ($< 50\text{ ms}$ target).
- **Condition C (Tier-2 Warm Start)**: Seed injection from precomputed state store (pending M6-K resolution).

Condition B and Condition C performance MUST NOT be blended into Cold-Start Tier 3 benchmarks.

---

## 22. Output Data Contract (Benchmark Execution Log Schema)
Future empirical trials MUST serialize execution records using the following JSON schema:

```json
{
  "experiment_id": "EXP-M7E1-20260930-001",
  "timestamp_iso": "2026-09-30T09:30:00Z",
  "algorithm_id": "CANDIDATE_SOLVER_NAME",
  "implementation_version": "1.0.0",
  "benchmark_scenario_id": "SCENARIO_DURIAN_01",
  "experimental_condition": "CONDITION_A_COLD_START",
  "random_seed": 42,
  "solver_configuration": {
    "max_evaluations": null,
    "time_budget_ms": 3000.0
  },
  "metrics": {
    "scientific_evaluations_count": 450,
    "optimizer_generations_count": 15,
    "total_wall_clock_ms": 1250.4,
    "scientific_eval_time_ms": 1100.2,
    "optimizer_overhead_ms": 150.2,
    "feasible_candidates_count": 14,
    "infeasible_candidates_count": 410,
    "unknown_candidates_count": 26,
    "first_feasible_eval_index": 12,
    "peak_ram_mb": 145.2
  },
  "execution_status": "COMPLETED_SUCCESSFULLY",
  "pareto_front_summary": {
    "candidate_count": 14,
    "cache_hit": false
  }
}
```

---

## 23. Failure Handling Protocol
Future benchmark execution MUST track and classify execution failures transparently:

| Execution Failure Type | Benchmark Logging Response | Protocol Action |
|:---|:---|:---|
| **Algorithm Execution Failure** | Record status `ALGORITHM_ERROR` | Log stack trace; retain experiment record. |
| **Scientific Model Exception** | Record status `SCIENTIFIC_EVAL_ERROR` | Log candidate ID; isolate failing component. |
| **Invalid Candidate Input** | Record status `INVALID_CANDIDATE_INPUT` | Log validation error string. |
| **Database Access Failure** | Record status `DATABASE_ERROR` | Log connection trace. |
| **Execution Timeout** | Record status `TIMEOUT_EXCEEDED` | Emit partial non-dominated front; log timeout. |
| **Resource Exhaustion** | Record status `OOM_KILLED` | Log memory peak; flag resource failure. |
| **Empty Feasible Pareto Front** | Record status `EMPTY_FEASIBLE_FRONT` | Emit valid empty `ParetoFront` (`candidate_count = 0`). |

No failed run may be silently discarded or hidden from benchmark reports.

---

## 24. Statistical Reporting Protocol

```
STATISTICAL REPORTING POLICY NOT YET AUTHORIZED
```

- **Policy Status**: Specific statistical aggregation methods (e.g. bootstrapping, confidence bounds) remain unresolved.
- **Reporting Rule**: When repeated runs are authorized, reports MAY provisionally publish mean, median, standard deviation, and min/max alongside raw run data.

---

## 25. Evidence Sufficiency Rule
If upon completing an empirical benchmark trial:
- Benchmark scenarios are non-representative,
- Repeated run counts are insufficient,
- Pareto quality indicators remain unauthorized,
- Evaluation budget caps remain unresolved,

**THEN THE FINAL EVALUATION REPORT MUST CONCLUDE**:

```
M7-B OPTIMIZER ALGORITHM NOT YET AUTHORIZED
```

No algorithm may be selected or declared a winner simply because it was tested or yielded fast runtime under a limited trial.

---

## 26. Implementation-Readiness Matrix for Evaluation Policy

| Policy / Contract Area | Status | Source Contract | Missing Authorization / Decision |
|:---|:---:|:---|:---|
| **Evaluation Unit Definition** | **READY** | `m7e1` Sec 5 | None (Atomic units defined) |
| **Benchmark Scenario Identity** | **READY** | `m6a_optimization_problem_definition.md` | None (Reuses frozen M6-A identity) |
| **Scientific Pipeline Control** | **READY** | `m6b2b`, `m6b3`, `m6b4a`, `m6b4b` | None (Pipeline primitives verified) |
| **Evaluation Budget Policy** | **NOT READY** | `m7e1` Sec 8 | Authorized numerical budget caps |
| **Termination Policy** | **NOT READY** | `m7a` Sec 16 | Authorized numerical termination thresholds |
| **Random Seed Standard** | **PARTIAL** | `m7e1` Sec 10 | Authorized default random seed |
| **Repeated Runs Policy** | **NOT READY** | `m7e1` Sec 11 | Authorized repetition count & stat policy |
| **Uncertainty Protocol** | **PARTIAL** | `m6a` Sec 6 | Optimizer-level interval sorting policy |
| **Pareto Quality Indicator** | **NOT READY** | `m7e1` Sec 13 | Authorized Pareto quality metric |
| **Feasible Discovery Protocol** | **READY** | `m7e1` Sec 14 | None (Tracking protocol standardized) |
| **Wall-Clock Latency Protocol** | **READY** | `m7e1` Sec 15 | None (Timer instrumentation defined) |
| **Resource Measurement Protocol** | **READY** | `m7e1` Sec 16 | None (Resource metrics standardized) |
| **Benchmark Data Sources** | **READY** | `m5a`, `m6c2` | None (Data categories classified) |
| **Scenario Representativeness** | **READY** | `m6c2`, `m6d` | Real production workload telemetry |
| **Fair Comparison Controls** | **READY** | `m7e1` Sec 19 | None (Experimental controls standardized) |
| **Warm-Start Boundary** | **PARTIAL** | `m6k` | Tier-2 selection policy (M6-K) |
| **Precomputation Separation** | **READY** | `m7e1` Sec 21 | None (Condition A, B, C defined) |
| **Output Log Data Contract** | **READY** | `m7e1` Sec 22 | None (JSON execution schema defined) |
| **Failure Handling Protocol** | **READY** | `m7e1` Sec 23 | None (Failure logging rules defined) |
| **Statistical Reporting Protocol** | **NOT READY** | `m7e1` Sec 24 | Authorized statistical reporting policy |
| **Evidence Sufficiency Rule** | **READY** | `m7e1` Sec 25 | None (Rule frozen) |

---

## 27. Explicit Non-Decisions List
This milestone explicitly DOES NOT authorize:
1. Specific optimizer algorithm or solver selection.
2. Specific optimizer algorithm family.
3. Population size or generation count values.
4. Maximum scientific evaluations budget cap.
5. Maximum wall-clock time budget cap.
6. Convergence tolerance numerical thresholds.
7. Default numerical random seed value.
8. Authorized number of repeated stochastic runs.
9. Authorized Pareto quality indicator (hypervolume, GD, IGD, $\epsilon$).
10. Authorized interval objective sorting strategy.
11. Authorized surrogate ML model architecture or training policy.
12. Tier-2 warm-start seed selection metric.
13. Production workload representativeness claims.
14. Benchmark winner or algorithm ranking.

---

## 28. Final Milestone Status

```
M7-E1 OPTIMIZER EVALUATION POLICY COMPLETE
```
