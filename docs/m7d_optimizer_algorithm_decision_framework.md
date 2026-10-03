# M7-D: Optimizer Algorithm Decision Framework

## 1. Status
**PROPOSED DECISION FRAMEWORK — AUDIT READY**

## 2. Scope & Purpose
This document establishes the formal, algorithm-neutral **Optimizer Algorithm Decision Framework** for evaluating candidate Tier-3 multi-objective optimization algorithms in future controlled empirical trials (M7-E).

Milestone M7-D is strictly a **DECISION FRAMEWORK DESIGN**. In accordance with project governance:
- **No optimizer algorithm is selected.**
- **No optimizer algorithms are ranked, scored, or declared winners.**
- **No production code is implemented.**
- **No algorithms (NSGA-II, NSGA-III, MOEA/D, Bayesian optimization) are coded.**
- **No surrogate models** or evolutionary operators are implemented.
- **No benchmarks are executed or synthetic performance numbers fabricated.**

M7-D defines the reproducible 6-step procedure, mandatory compatibility gates, empirical measurement dimensions, and insufficient-evidence rules that a future M7-E evaluation MUST apply before an algorithm can be authorized.

---

## 3. Source Authority & Lineage
This decision framework traces all criteria directly to authorized project contracts:
- `docs/scientific_knowledge_foundation.md`
- `docs/m6a_optimization_problem_definition.md`
- `docs/m6b1_optimization_contracts.md`
- `docs/m6b2a_candidate_construction.md`
- `docs/m6b2b_candidate_scientific_evaluation.md`
- `docs/m6b3_objective_evaluation.md`
- `docs/m6b4a_pareto_dominance.md`
- `docs/m6b4b_pareto_front_construction.md`
- `docs/m7a_inverse_design_optimization_execution_contract.md`
- `docs/m7b_optimizer_algorithm_authorization_audit.md`
- `docs/m7c_optimizer_selection_requirements.md`

---

## 4. Candidate Algorithm Families
Based on project documentation review (M7-B Audit Section 4), the following candidate algorithm families are identified:

| Algorithm Family | Documented in Project | Example Candidates | Relevance to Packaging Problem |
|:---|:---:---|:---|:---|
| **Evolutionary Multi-Objective Optimization (EMOO)** | **YES** (Proposed Option) | NSGA-II, NSGA-III, SPEA2 | Population-based exploration over mixed-integer decision spaces |
| **Decomposition-Based Multi-Objective (MOEA/D)** | **YES** (Proposed Option) | MOEA/D | Multi-objective decomposition using sub-problems |
| **Surrogate-Assisted Optimization (SAOO)** | **YES** (Architectural Concept) | Gaussian Process + EGO, RF Surrogate | Acceleration for computationally expensive physics evaluations |
| **Bayesian Multi-Objective Optimization** | **YES** (Literature Reference) | qEHVI, ParEGO | Sequential sampling under tight evaluation budgets |
| **Swarm / Differential Evolution** | **NO** (General Option) | MOPSO, DEMO | General literature baseline options |

*Note: Listing algorithm families in this framework does NOT constitute authorization or selection of any specific solver.*

---

## 5. Mandatory Compatibility Gates
Before an algorithm candidate can undergo empirical trial in M7-E, it MUST pass 10 mandatory compatibility gates derived from `docs/m7c_optimizer_selection_requirements.md`:

| Gate ID | Mandatory Technical Requirement | Pass Condition | Source |
|:---|:---|:---|:---|
| **GATE-01** | **Multi-Objective Preservation** | Operates directly on $m=4$ objective vectors without scalar weighting ($w_1 f_1 + w_2 f_2$) or utility scores. | `m7c` REQ-OBJ-01 |
| **GATE-02** | **Exact Pareto Dominance Filtering** | Output non-dominated set matches exact $A \prec B$ dominance primitives (`m6b4a`). | `m7c` REQ-PAR-01 |
| **GATE-03** | **Hard Constraint Enforcement** | Strictly enforces Phase 5 constraints; excludes `INFEASIBLE` and `UNKNOWN` ($\text{UNKNOWN} \ne \text{FEASIBLE}$). | `m7c` REQ-CON-01 |
| **GATE-04** | **External Pipeline Compliance** | Evaluates candidates externally via M6-B2B and M6-B3 without re-implementing physics. | `m7c` REQ-SCI-01 |
| **GATE-05** | **Authorized Decision Space** | Operates strictly over `material_id`, `layer_structure`, `total_thickness_um`, `package_geometry`. | `m7c` REQ-DEC-01 |
| **GATE-06** | **Cold-Start Primacy** | Executes self-contained cold starts directly from `eligible_candidate_materials` without Tier-1/Tier-2. | `m7c` REQ-INI-01 |
| **GATE-07** | **UNKNOWN Preservation** | Excludes `UNKNOWN` states from deterministic Pareto fronts without scalar conversion. | `m7c` REQ-UNC-02 |
| **GATE-08** | **Interval Preservation** | Preserves objective intervals $[f_{min}, f_{max}]$ on emitted `ParetoCandidate` records. | `m7c` REQ-UNC-01 |
| **GATE-09** | **Deterministic Reproducibility** | Guarantees identical `ParetoFront` outputs when supplied with a fixed `random_seed`. | `m7c` REQ-REP-01 |
| **GATE-10** | **Framework Independence** | Operates as a domain module without importing web frameworks (FastAPI) or database ORMs. | `m7a` Sec 23 |

---

## 6. Optional Capabilities
The framework distinguishes mandatory compatibility gates from optional acceleration capabilities:
- **Warm-Start Seed Ingestion**: Ability to ingest an optional initial seed population from Tier-2 handoff (`optional_warm_start_population`).
- **Parallel Scientific Evaluation**: Ability to evaluate candidate populations concurrently across multiple CPU worker threads.
- **Surrogate Model Acceleration**: Ability to couple with an authorized surrogate ML model (when a surrogate specification is authorized).

*Rule*: An optional capability MUST NOT compensate for a failure on a mandatory compatibility gate.

---

## 7. Hard Compatibility Gates vs. Empirical Performance
This framework strictly separates **Compatibility** from **Performance**:

- **Compatibility Evaluation**: Binary determination (`COMPLIANT` / `NON-COMPLIANT`). If an algorithm fails any mandatory gate (GATE-01 through GATE-10), it is immediately disqualified from further evaluation.
- **Performance Evaluation**: Empirical measurement of execution behavior (timing, evaluations count, convergence rate) conducted ONLY on candidate algorithms that are 100% `COMPLIANT`.
- **Strict Rule**: High empirical performance or fast runtime MUST NEVER override a compatibility gate failure (e.g. an algorithm that scalarizes objectives or converts `UNKNOWN` to `FEASIBLE` is strictly disqualified, regardless of its speed).

---

## 8. Empirical Evaluation Dimensions for Future Trials (M7-E)
For compliant algorithms undergoing empirical evaluation in M7-E, the framework standardizes 7 measurement dimensions:

| Dimension | Description | Measurement Unit | Target / Benchmark Rule |
|:---|:---|:---:|:---|
| **Evaluations Count** | Total scientific function evaluations (M6-B2B + M6-B3 calls) to reach convergence. | Count | Minimization target |
| **Wall-Clock Latency** | Total execution time from input ingestion to `ParetoFront` emission. | Milliseconds (ms) | Target $< 3000\text{ ms}$ (`m6a`) |
| **Feasible Discovery Rate** | Percentage of evaluated candidate designs that satisfy Phase 5 hard constraints. | Percentage (%) | Measured metric |
| **Pareto Front Coverage** | Number of unique, non-dominated `ParetoCandidate` solutions discovered. | Count | Measured metric |
| **Repeatability / Seed Variance** | Variance in emitted Pareto fronts across repeated runs with different random seeds. | Standard Deviation | Minimization target |
| **Robustness to Over-Constraint** | Behavior when search space contains zero feasible solutions ($100\%$ infeasible). | Binary Pass/Fail | Must emit empty `ParetoFront` |
| **Memory Footprint** | Peak RAM consumption during population iteration. | Megabytes (MB) | Measured metric |

*Note: Numerical benchmark thresholds and target values for these dimensions are `NOT ESTABLISHED` and must be measured during M7-E.*

---

## 9. Pareto Quality Measurement Status

```
PARETO QUALITY METRIC NOT YET AUTHORIZED
```

### Audit Finding:
- Project contracts mandate exact Pareto dominance filtering ($A \prec B$).
- **No mathematical quality indicator (e.g., Hypervolume Indicator, Generational Distance, Epsilon Indicator, Spread / Diversity Index) is currently authorized by project contracts.**
- M7-E empirical trials MUST NOT calculate or rank algorithms using unauthorized quality indicators unless a formal design contract authorizes the specific quality metric.

---

## 10. Constraint & Failure Performance Evaluation
Future empirical trials MUST record constraint filtering behavior transparently through the existing M6 scientific pipeline:
- `feasible_count`: Count of candidates evaluated as `FEASIBLE` under Phase 5 constraints.
- `infeasible_count`: Count of candidates evaluated as `INFEASIBLE`.
- `unknown_count`: Count of candidates evaluated as `UNKNOWN`.
- `evaluation_errors`: Count of technical execution errors.

No penalty functions or constraint aggregation equations may be injected into the evaluation pipeline.

---

## 11. Uncertainty Evaluation Protocol
M7-E evaluation protocols MUST observe solver behavior under scientific uncertainty:
1. **Interval Bound Preservation**: Verify that $[f_{min}, f_{max}]$ bounds emitted by M6-B3 are preserved on all `ParetoCandidate` output records.
2. **UNKNOWN Exclusion**: Verify that `UNKNOWN` candidate states are excluded from the deterministic `ParetoFront`.
3. **Observation of Solver Sorting**: Document how candidate solvers handle interval objective values during internal selection without fabricating probabilistic scoring systems.

---

## 12. Reproducibility & Experiment Metadata Standard
Any future empirical benchmark trial in M7-E MUST record complete experiment metadata for 100% auditability:
```json
{
  "experiment_id": "EXP-M7E-001",
  "timestamp": "2026-09-30T00:00:00Z",
  "algorithm_id": "CANDIDATE_SOLVER_NAME",
  "algorithm_version": "1.0.0",
  "solver_configuration": {
    "random_seed": 42,
    "max_evaluations": 1000,
    "time_budget_ms": 3000.0
  },
  "dataset_id": "M5_EMPIRICAL_FIXTURE_V1",
  "environment": {
    "python_version": "3.14.0",
    "os": "Windows-11-10.0.26100-SP0",
    "cpu": "x86_64"
  },
  "metrics": {
    "wall_clock_ms": 1250.4,
    "scientific_evaluations": 450,
    "pareto_candidate_count": 12
  }
}
```

---

## 13. Experimental Dataset Standard
The framework establishes strict rules governing valid evaluation datasets:

| Dataset Category | Admissibility for M7-E Evaluation | Governance Rule |
|:---|:---:|:---|
| **M5 Canonical Empirical Database** | **ADMISSIBLE** | Primary empirical dataset (47 evidence units, 11 materials, 34 barrier records). |
| **M6 Synthetic Test Fixtures** | **ADMISSIBLE (Unit Testing Only)** | Validates code correctness; CANNOT serve as production benchmark evidence. |
| **Production API Workload Telemetry** | **ABSENT** | Zero production request logs exist (`m6c2`). |
| **Pilot API Request Logs** | **ABSENT** | Zero pilot request logs exist (`m6c2`). |

---

## 14. Benchmark Scenario Design Rules
Benchmark scenarios for M7-E empirical trials MUST be constructed strictly from authorized optimization states:
1. **Target Envelope**: Valid `PackagingRequirementEnvelope` derived from Phase 4 physics for authorized test commodities (durian, broccoli, apple).
2. **Package Geometry**: Valid `PackageGeometry` parameters ($surface\_area\_m2$, $headspace\_volume\_cm3$, $product\_mass\_kg$).
3. **Active Objectives**: Valid subset of authorized active objectives ($f_{\text{thickness}}$, $f_{\text{moisture\_margin}}$, $f_{\text{gas\_alignment}}$, $f_{\text{shelf\_life\_margin}}$).
4. **Eligible Candidate Search Space**: Valid candidate material subset derived from M6-B1 filtering over the M5 database.

No artificial, hypothetical, or unverified scenario parameters may be fabricated.

---

## 15. Repeated Runs & Statistical Policy

```
REPEATED-RUN STATISTICAL POLICY NOT YET AUTHORIZED
```

- **Contract Status**: The number of repeated stochastic runs (e.g. 30 independent runs), random seed sequences, and statistical confidence tests (e.g. Wilcoxon signed-rank test) are `NOT YET AUTHORIZED` by project contracts.
- **Trial Requirement**: M7-E trials MUST establish an authorized statistical policy contract before reporting comparative stochastic performance.

---

## 16. Performance Targets vs. Empirical Benchmarks
The decision framework enforces the strict distinction between architectural targets and empirical benchmarks:
- **Architectural Target**: $< 3000\text{ ms}$ total execution time (`m6a_optimization_problem_definition.md` Sec 10).
- **Empirical Benchmark**: `NOT ESTABLISHED`. Latency, throughput, and memory consumption MUST be empirically measured during M7-E trials.
- **Rule**: An architectural target MUST NOT be converted into a claimed empirical result prior to trial execution.

---

## 17. Fair Comparison Experimental Controls
To guarantee a fair comparison during M7-E empirical trials, all candidate solvers MUST be evaluated under identical experimental controls:
1. **Identical Search Space**: Exactly the same `eligible_candidate_materials` input.
2. **Identical Scientific Pipeline**: Exactly the same M6-B2B and M6-B3 evaluation code.
3. **Identical Execution Budgets**: Exactly the same evaluation caps (`max_evaluations`) and time limits (`time_budget_ms`).
4. **Identical Hardware/Software Environment**: Executed on the same physical host machine under the same OS and Python runtime.

---

## 18. Future 6-Step Decision Procedure
When M7-E empirical evaluation is authorized, the decision procedure MUST follow these 6 sequential steps:

```
  +-----------------------------------------------------------------------+
  | STEP 1: Evaluate Mandatory Compatibility Gates (GATE-01 to GATE-10)   |
  +-----------------------------------------------------------------------+
                                      |
                                      v
  +-----------------------------------------------------------------------+
  | STEP 2: Exclude Non-Compliant Candidates (Binary Disqualification)     |
  +-----------------------------------------------------------------------+
                                      |
                                      v
  +-----------------------------------------------------------------------+
  | STEP 3: Conduct Controlled Empirical Trials on Compliant Solvers      |
  +-----------------------------------------------------------------------+
                                      |
                                      v
  +-----------------------------------------------------------------------+
  | STEP 4: Report Measurements Transparently (No Weighted Scoring)       |
  +-----------------------------------------------------------------------+
                                      |
                                      v
  +-----------------------------------------------------------------------+
  | STEP 5: Apply Previously Authorized Decision Criteria Only            |
  +-----------------------------------------------------------------------+
                                      |
                                      v
  +-----------------------------------------------------------------------+
  | STEP 6: Maintain "NOT YET AUTHORIZED" if Evidence Remains Incomplete  |
  +-----------------------------------------------------------------------+
```

---

## 19. Insufficient-Evidence Mandatory Rule
If at the conclusion of an evaluation:
- Empirical benchmark data is incomplete,
- Benchmark scenarios are non-representative,
- Pareto quality metrics remain unauthorized,
- Termination or uncertainty policies remain unresolved,

**THEN THE FINAL DECISION MUST REMAIN**:

```
M7-B OPTIMIZER ALGORITHM NOT YET AUTHORIZED
```

The framework strictly prohibits declaring a "winner by default" or selecting an algorithm based on general engineering preference.

---

## 20. Algorithm-Neutral Candidate Compatibility Matrix

| Project Requirement / Gate | EMOO (e.g. NSGA-II) | MOEA/D | Bayesian Opt | Supporting Source Contract |
|:---|:---:|:---:|:---:|:---|
| **GATE-01: Multi-Objective Vector Preservation** | COMPLIANT | COMPLIANT | NOT ESTABLISHED | `m7c` REQ-OBJ-01 |
| **GATE-02: Exact Pareto Dominance ($A \prec B$)** | COMPLIANT | COMPLIANT | NOT ESTABLISHED | `m6b4a_pareto_dominance.md` |
| **GATE-03: Hard Constraint Enforcement ($\text{UNK} \ne \text{FEAS}$)** | COMPLIANT | COMPLIANT | NOT ESTABLISHED | `m6a_optimization_problem_definition.md` Sec 3 |
| **GATE-04: External Pipeline Compliance (B2B/B3)** | COMPLIANT | COMPLIANT | COMPLIANT | `m7c` REQ-SCI-01 |
| **GATE-05: Authorized Decision Space** | COMPLIANT | COMPLIANT | NOT ESTABLISHED | `m6b2a_candidate_construction.md` |
| **GATE-06: Cold-Start Primacy** | COMPLIANT | COMPLIANT | COMPLIANT | `m7a_inverse_design_optimization_execution_contract.md` Sec 14 |
| **GATE-07: UNKNOWN Status Preservation** | COMPLIANT | COMPLIANT | NOT ESTABLISHED | `m7c` REQ-UNC-02 |
| **GATE-08: Interval Objective Preservation** | COMPLIANT | COMPLIANT | NOT ESTABLISHED | `m7c` REQ-UNC-01 |
| **GATE-09: Deterministic Reproducibility** | COMPLIANT | COMPLIANT | COMPLIANT | `m7c` REQ-REP-01 |
| **GATE-10: Framework Independence** | COMPLIANT | COMPLIANT | COMPLIANT | `m7a` Sec 23 |
| **Empirical Target ($< 3000\text{ ms}$)** | NOT ESTABLISHED | NOT ESTABLISHED | NOT ESTABLISHED | `m6a_optimization_problem_definition.md` Sec 10 |

*Note: This matrix records technical compliance against documented requirements ONLY. It assigns zero numerical scores, rankings, tiers, or winner labels.*

---

## 21. Implementation-Readiness Matrix for M7-E Evaluation

| Evaluation Component | Readiness Status | Missing Authorization / Blocker |
|:---|:---:|:---|
| **Candidate Algorithm Definitions** | **NOT READY** | Specific algorithm implementations not authorized |
| **Mandatory Compatibility Gates** | **READY** | Gates 01–10 frozen in M7-C requirements |
| **Benchmark Scenarios** | **PARTIAL** | M5 empirical scenarios ready; production traces missing |
| **Evaluation Budget Policy** | **NOT READY** | `EVALUATION BUDGET NOT YET AUTHORIZED` |
| **Termination Policy** | **NOT READY** | `TERMINATION POLICY NOT YET AUTHORIZED` |
| **Pareto Quality Metric** | **NOT READY** | `PARETO QUALITY METRIC NOT YET AUTHORIZED` |
| **Uncertainty Sorting Policy** | **NOT READY** | `OPTIMIZER UNCERTAINTY HANDLING STRATEGY NOT YET AUTHORIZED` |
| **Reproducibility Seed Assignment** | **PARTIAL** | Schema field ready; default seed value unassigned |
| **Repeated-Run Statistical Policy** | **NOT READY** | `REPEATED-RUN STATISTICAL POLICY NOT YET AUTHORIZED` |
| **Hardware/Software Controls** | **READY** | Execution environment standardized |
| **6-Step Decision Procedure** | **READY** | Decision procedure frozen in this framework |

---

## 22. Explicit Unresolved Decisions
The following items remain explicitly unresolved and must be addressed prior to M7-E execution:
1. **Algorithm Authorization**: Selection of specific candidate solver algorithms (`m7b`).
2. **Evaluation Budget & Termination Caps**: Authorized numerical values for max evaluations and time budgets.
3. **Pareto Quality Indicator**: Formal authorization of hypervolume or alternative Pareto quality metrics.
4. **Interval Sorting Strategy**: Solver-level mathematical policy for comparing interval objective vectors.
5. **Repeated-Run Statistical Protocol**: Authorized number of runs and statistical confidence metrics.

---

## 23. Final Framework Status

```
M7-D OPTIMIZER ALGORITHM DECISION FRAMEWORK COMPLETE
```
