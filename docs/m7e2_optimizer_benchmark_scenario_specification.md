# M7-E2: Optimizer Benchmark Scenario Specification

## 1. Status
**PROPOSED BENCHMARK SCENARIO SPECIFICATION — AUDIT READY**

## 2. Scope & Purpose
This document establishes the formal **Optimizer Benchmark Scenario Specification** for future Tier-3 multi-objective optimization algorithm evaluation within the AI-Food-Packaging-Optimizer project.

Milestone M7-E2 is strictly a **DESIGN-ONLY SPECIFICATION**. In accordance with project governance:
- **No benchmark code is implemented.**
- **No benchmarks are executed.**
- **No optimizer algorithm is selected.**
- **No algorithms are ranked, scored, or assigned winners.**
- **No benchmark results or Pareto fronts are generated or fabricated.**
- **No production workload or user demand distributions are fabricated.**
- **No production Python code or tests are modified.**

The purpose of M7-E2 is to establish the formal contract for what constitutes a valid, scientifically executable benchmark scenario so that M7-E4 can later implement benchmark trials after necessary algorithm and evaluation policies are formally authorized.

---

## 3. Source Authority & Lineage
This benchmark scenario specification traces all rules and constraints directly to authorized project contracts:
- `docs/scientific_knowledge_foundation.md`
- `docs/m6a_optimization_problem_definition.md`
- `docs/m6b1_optimization_contracts.md`
- `docs/m6b2a_candidate_construction.md`
- `docs/m6b2b_candidate_scientific_evaluation.md`
- `docs/m6b3_objective_evaluation.md`
- `docs/m6b4a_pareto_dominance.md`
- `docs/m6b4b_pareto_front_construction.md`
- `docs/m6b5a_precomputed_state_store_contract.md`
- `docs/m6b5b_canonical_optimization_state_representation.md`
- `docs/m6b5c_precomputed_state_generation_contract.md`
- `docs/m6b5d_exact_tier1_lookup_contract.md`
- `docs/m6b5e_tier2_warm_start_state_selection_contract.md`
- `docs/m6k_tier2_selection_strategy_evidence_audit.md`
- `docs/m7a_inverse_design_optimization_execution_contract.md`
- `docs/m7b_optimizer_algorithm_authorization_audit.md`
- `docs/m7c_optimizer_selection_requirements.md`
- `docs/m7d_optimizer_algorithm_decision_framework.md`
- `docs/m7e1_optimizer_evaluation_policy.md`

---

## 4. Core Governance & Identity Equivalence Principle
A benchmark scenario is an explicit, frozen optimization problem state intended to be passed into the scientific optimization execution pipeline defined in M7-A.

A benchmark scenario **MUST NOT** alter, expand, or redefine the M6 Optimization-State Identity.

The unalterable 4-part M6 Optimization-State Identity remains:

$$\text{Optimization Identity} = \left\langle \text{Phase 4 Requirement Envelope}, \; \text{Package Geometry}, \; \text{Active Objective Set}, \; \text{Resolved Eligible Candidate ID Set} \right\rangle$$

- **REQ-IDENTITY-01**: Raw biological commodity context (e.g. food names, cultivars, respiration rates) **MUST NOT** be included in the optimization identity. Biological context is fully resolved into the Phase 4 Requirement Envelope prior to optimization identity construction.
- **REQ-IDENTITY-02**: No identity component may be deleted, omitted, or replaced.
- **REQ-IDENTITY-03**: Provenance references (scientific source data, pipeline trace IDs) **MUST NOT** be embedded into the optimization identity. Provenance remains strictly separated from identity ($\text{IDENTITY} \ne \text{PROVENANCE}$).
- **REQ-IDENTITY-04**: Bookkeeping and experiment metadata (scenario ID, test tags, execution timestamp) **MUST NOT** be embedded into the optimization identity ($\text{IDENTITY} \ne \text{EXPERIMENT METADATA}$).

---

## 5. Scenario Identity Standard & Bookkeeping Metadata
Every benchmark scenario MUST specify its problem definition via references to authorized data contracts and maintain strict separation between problem identity and experiment metadata.

### 5.1 Optimization-State Identity References
1. **Phase 4 Requirement Envelope**: Referenced by structural envelope schema containing resolved target ranges, bounds, and uncertainty states for gas exchange, moisture, microbial, and shelf-life requirements.
2. **Package Geometry**: Referenced by target container geometry parameters (`package_surface_area_m2`, `package_headspace_volume_cm3`, and candidate layer thickness values).
3. **Active Objective Set**: Referenced by the set of active objective keys (`f_thickness`, `f_moisture_margin`, `f_gas_alignment`, `f_shelf_life_margin`) conforming to M6-B3.
4. **Eligible Candidate ID Set**: Referenced by the set of resolved `PackagingCandidate` IDs produced by M6-B2A candidate construction.

### 5.2 Experiment Bookkeeping Metadata (Non-Identity)
The following fields are strictly classified as **EXPERIMENT METADATA** and MUST NOT participate in canonical hashing or optimization state lookup:
- `scenario_id`: Unique identifier for the benchmark scenario (e.g., `SCEN-COLD-001`).
- `scenario_name`: Human-readable label for tracking.
- `scenario_origin`: Formal classification (`REAL_SCIENTIFIC_STATE`, `SYNTHETIC_TEST_SCENARIO`, `REAL_PRODUCTION_WORKLOAD`, etc.).
- `creation_timestamp`: ISO 8601 timestamp of scenario assembly.
- `tags`: Descriptive tags for experiment classification (e.g., `["cold-start", "boundary-case"]`).

---

## 6. Requirement Envelope Specification
A benchmark scenario MUST incorporate a fully resolved Phase 4 Requirement Envelope conforming to `backend/app/schemas/packaging_requirements.py` and M6-A/M6-B1.

- **REQ-ENV-01 (Preservation of Scientific States)**: Requirement fields MUST preserve their exact scientific states:
  - `CALCULATED`: Values derived from verified kinetic or sorption models.
  - `RANGE`: Bounded min/max intervals (e.g. target O₂ range 2.0% - 5.0%).
  - `UNKNOWN`: Explicit missing/unresolved scientific data.
  - `ABSENT`: Formally unrequested requirements.
- **REQ-ENV-02 (Prohibition of Interval Collapsing)**: Bounded intervals (ranges) **MUST NOT** be collapsed into single point-estimate averages (e.g., a range of $[2.0, 5.0]$ MUST NOT be converted to $3.5$).
- **REQ-ENV-03 (Prohibition of Numerical Substitution for UNKNOWN)**: `UNKNOWN` values **MUST NOT** be filled with default numbers, zero, mean values, or guessed constants.
- **REQ-ENV-04 (Prohibition of Value Invention)**: Scientific requirement values missing from source evidence **MUST NOT** be fabricated to make a scenario "pass".
- **REQ-ENV-05 (Traceability Preservation)**: Requirements requiring scientific provenance MUST retain their audit traceability references without injecting them into canonical state identity.

---

## 7. Package Geometry Specification
A benchmark scenario MUST include valid, deterministic package geometry parameters as specified in M6-A and M6-B2A.

- **REQ-GEO-01 (Required Geometry Fields)**: Package geometry MUST include:
  - `package_surface_area_m2`: Total surface area for mass transfer ($A > 0$).
  - `package_headspace_volume_cm3`: Headspace volume for gas exchange ($V > 0$).
  - Layer-specific thickness parameters ($\mu\text{m}$ / $\text{m}$) as defined per candidate structure.
- **REQ-GEO-02 (Prohibition of Unsupported Variables)**: Geometry variables not authorized by M6-A (e.g. arbitrary 3D spatial mesh geometries, folding crease ratios) **MUST NOT** be included.
- **REQ-GEO-03 (Prohibition of Silent Defaults)**: Missing or null package geometry values **MUST NOT** be silently filled with hidden default constants.
- **REQ-GEO-04 (Incomplete Geometry Handling)**: If package geometry is missing, invalid ($\le 0$), or incomplete, the benchmark scenario MUST be classified as `SCENARIO_INVALID_INCOMPLETE_GEOMETRY` and rejected prior to benchmark execution.

---

## 8. Active Objective Set Specification
A benchmark scenario MUST explicitly declare its set of active optimization objectives from the authorized M6-B3 objective pool.

- **REQ-OBJ-01 (Authorized Objective Definitions)**: Objectives MUST be selected strictly from M6-B3:
  1. `f_thickness` (Minimize)
  2. `f_moisture_margin` (Maximize)
  3. `f_gas_alignment` (Minimize)
  4. `f_shelf_life_margin` (Maximize)
- **REQ-OBJ-02 (Prohibition of Unauthorized Objectives)**: New objectives (e.g., custom sensory scores, brand appeal indices) **MUST NOT** be introduced.
- **REQ-OBJ-03 (Prohibition of Scalarization & Penalty Functions)**: Weighted objective sums, multi-attribute utility scores, or penalty-blended scalar functions **MUST NOT** be introduced into the scenario definition. Pareto optimization evaluates raw, multi-dimensional objective vectors.
- **REQ-OBJ-04 (Unordered Set Property)**: The active objective set is an unordered mathematical set. The ordering of objective keys in scenario definition files MUST NOT affect canonical identity or benchmark results.

---

## 9. Eligible Candidate Set Specification
A benchmark scenario MUST contain a resolved set of eligible `PackagingCandidate` IDs produced by the M6-B2A candidate construction process.

- **REQ-CAND-01 (Search Space Authorization)**: Candidates MUST belong strictly to the authorized search space constructed from verified material evidence.
- **REQ-CAND-02 (Prohibition of Invented Material Classes)**: Arbitrary or hypothetical material classes not present in the verified dataset **MUST NOT** be added to candidate sets.
- **REQ-CAND-03 (Prohibition of Hand-Picked Shortlists)**: Benchmark scenarios **MUST NOT** use arbitrary, hand-picked candidate shortlists designed to favor or penalize specific optimizer algorithms.
- **REQ-CAND-04 (Unordered Set Representation)**: The candidate set is an unordered set of candidate IDs. The candidate set **MUST NOT** contain pre-ordered candidate rankings or biased candidate sequences.

---

## 10. Scientific Validity & Executability Rules
A benchmark scenario is scientifically executable if and only if it passes all structural and scientific completeness checks required by the unalterable pipeline.

### 10.1 Executability Criteria
A scenario is `EXECUTABLE` if:
1. All 4 components of the M6 Optimization-State Identity are present and non-null.
2. Requirement Envelope contains valid, non-corrupted data structures.
3. Package Geometry values are strictly positive ($A > 0$, $V > 0$).
4. Active Objective Set contains $\ge 1$ authorized objective keys.
5. Eligible Candidate Set is fully resolved (may be non-empty or empty).

### 10.2 Legitimate Scientific Outcomes
The benchmark framework **MUST NOT** require every valid scenario to contain feasible solutions. Scientifically valid execution includes the following legitimate outcomes:
- **Feasible Pareto Front**: One or more candidates satisfy all Phase 5 hard constraints and form a non-dominated front.
- **Empty Feasible Front**: Zero candidates satisfy all Phase 5 hard constraints (all candidates are infeasible).
- **UNKNOWN Evaluation State**: Candidates evaluate to `UNKNOWN` due to missing kinetic/sorption parameters or unresolved properties.
- **Evaluation Failure**: Specific candidate evaluations fail due to out-of-bound numerical states.

An empty feasible Pareto front is a fully valid scientific outcome and MUST NOT be treated as a benchmark infrastructure failure.

---

## 11. Scenario Classification Taxonomy
To evaluate optimizer robustness across diverse scientific problem structures, benchmark scenarios are categorized into five formal structural classes:

| Scenario Class | Structural Characteristics | Scientific Purpose | Benchmark Expectation |
|:---|:---|:---|:---|
| **Class A: Fully Computable Deterministic** | All inputs `KNOWN`; all physics models computable; non-empty candidate set. | Baseline optimization performance and Pareto convergence. | Optimizer should locate non-dominated front smoothly. |
| **Class B: Interval / Uncertainty** | Requirement envelope contains `RANGE` intervals; candidates contain `PREDICTED` QSAR properties. | Robustness under input/property uncertainty. | Optimizer must evaluate candidates without collapsing ranges. |
| **Class C: Partially Unresolved** | Contains `UNKNOWN` requirement states or missing barrier observations. | Handling of incomplete scientific knowledge. | Candidates with `UNKNOWN` must be assigned `UNKNOWN` feasibility per M6-B2B. |
| **Class D: No-Feasible-Solution** | Highly restrictive constraints where 100% of candidates violate Phase 5 hard constraints. | Constraint handling and empty-front detection. | Optimizer must correctly return an empty Pareto front without crashing or returning invalid solutions. |
| **Class E: Scientific Evaluation Failure** | Contains candidates triggering numerical edge cases or physical boundary limits. | Fault tolerance and pipeline error propagation. | Pipeline must gracefully capture evaluation errors without halting solver loop. |

---

## 12. Structural Scenario Complexity (Easy / Medium / Hard)
Scenario complexity MUST be defined strictly through structural problem attributes rather than arbitrary numerical scoring functions or weighted difficulty metrics.

### 12.1 Structural Complexity Dimensions
- **Candidate-Space Size ($N$)**: Total number of eligible candidates in the search space ($N < 50$, $50 \le N \le 500$, $N > 500$).
- **Active Objective Count ($M$)**: Number of simultaneous objectives ($M = 2$, $M = 3$, $M = 4$).
- **Constraint Tightness & Count ($C$)**: Number and narrowness of active Phase 5 hard constraints.
- **Uncertainty Presence**: Absence or presence of `RANGE` intervals and `PREDICTED` QSAR values.
- **Physics Evaluation Cost**: Computational effort required per candidate evaluation (e.g., analytical vs numerical ODE integration for respiration/permeation).

### 12.2 Difficulty Classification Rules
- **Structural Easy**: Small candidate space ($N < 50$), $M=2$ objectives, deterministic inputs, loose constraints.
- **Structural Medium**: Moderate candidate space ($50 \le N \le 500$), $M=3$ objectives, mixed deterministic/range inputs.
- **Structural Hard**: Large candidate space ($N > 500$), $M=4$ objectives, tight constraints, high uncertainty (`RANGE`/`UNKNOWN`).
- **PROHIBITION**: Converting structural complexity into a single scalar "Difficulty Score" (e.g., $7.5/10$) is **STRICTLY PROHIBITED**.

---

## 13. Feasibility Coverage Policy
The benchmark scenario suite MUST provide structural coverage across all possible feasibility states to ensure solvers do not assume that all candidates are feasible.

- **REQ-FEAS-01**: Scenarios MUST expose solver algorithms to candidate sets containing mixtures of `FEASIBLE`, `INFEASIBLE`, and `UNKNOWN` candidates.
- **REQ-FEAS-02**: Scenarios MUST include boundary cases that result in 0% feasible candidates.
- **REQ-FEAS-03**: The benchmark framework **MUST NOT** fabricate or alter candidate properties to force infeasible candidates to become feasible.

---

## 14. Uncertainty Coverage Policy
Scenarios MUST preserve the four scientific uncertainty categories established in M6:

1. **`KNOWN`**: Experimentally verified data with documented test conditions.
2. **`RANGE`**: Min/max bounded intervals for requirements or properties.
3. **`PREDICTED`**: Model-derived properties (e.g. QSAR permeability predictions).
4. **`UNKNOWN`**: Missing property or requirement data.

- **REQ-UNCERT-01**: Scenarios supply scientific uncertainty states exactly as defined by M6 contracts.
- **REQ-UNCERT-02**: Inventing a custom optimizer uncertainty handling strategy (e.g. chance-constrained programming, fuzzy logic, Monte Carlo sampling) within the scenario specification is **STRICTLY PROHIBITED**. Optimizer treatment of uncertainty remains subject to future authorization in M7-E1/M7-F.

---

## 15. Scientific Data Provenance Protocol
Benchmark scenarios MUST maintain full scientific data provenance to support auditability and reproducibility without corrupting canonical problem identity.

$$\text{Provenanced Scenario Record} = \left\langle \text{Optimization Identity}, \; \text{Provenance References}, \; \text{Metadata} \right\rangle$$

- **REQ-PROV-01**: Provenance records MUST include references to source database evidence IDs (`EvidenceRecord`, `MaterialBarrierObservation`), ingestion trace IDs, and physics model versioning tags.
- **REQ-PROV-02**: Provenance records MUST be stored in the experiment metadata block of the scenario record.
- **REQ-PROV-03**: Provenance references **MUST NOT** be included in canonical state hashing. Two scenarios with identical Optimization-State Identities but different provenance trace IDs MUST yield identical canonical state hashes.

---

## 16. Scenario Origin Taxonomy (Real vs Synthetic)
Every benchmark scenario MUST be explicitly labeled with its origin category:

```
SCENARIO ORIGIN TAXONOMY:
- REAL_SCIENTIFIC_STATE       : Assembled from verified empirical database records and real food requirements.
- SYNTHETIC_TEST_SCENARIO     : Synthetically generated fixture for structural/boundary testing.
- REAL_PRODUCTION_WORKLOAD    : Derived from production system telemetry (CURRENTLY ABSENT).
- REAL_PILOT_WORKLOAD         : Derived from authorized pilot deployment telemetry (CURRENTLY ABSENT).
- DEMO                        : Educational or demonstration scenario.
```

- **REQ-ORIGIN-01**: Synthetic scenarios (`SYNTHETIC_TEST_SCENARIO`) **MUST NOT** be passed off or reported as production workload demand.
- **REQ-ORIGIN-02**: Fictional user demand distributions **MUST NOT** be generated or represented as real operational workloads.

---

## 17. Scientific Evidence vs Workload Telemetry Distinction
In strict accordance with M6-C3 and M6-D:

- **Scientific Evidence** answers: *"What scientific states can be evaluated based on verified physics models and material data?"*
- **Workload Telemetry** answers: *"What specific optimization problem states are actually submitted by real end-users in production?"*

These two concepts are **NOT INTERCHANGEABLE**.
- The current repository contains verified scientific evidence (M5 database).
- The current repository contains **ZERO authorized production workload telemetry** (`ABSENT`).
- Creating a fictional production workload distribution based on scientific evidence counts is **STRICTLY PROHIBITED**.

---

## 18. Scenario Sampling Policy

```
BENCHMARK SCENARIO SAMPLING STRATEGY NOT YET AUTHORIZED
```

### Policy Audit Status:
- **Exhaustive State Enumeration**: `UNEVALUATED` (Combinatorial explosion across continuous geometry ranges makes naive exhaustive enumeration unfeasible).
- **Domain-Priority Selection**: `NOT YET AUTHORIZED` (Requires domain authorization for specific food categories).
- **Workload-Driven Selection**: `NOT ESTABLISHED` (Requires production workload telemetry).
- **Random Sampling**: `NOT YET AUTHORIZED` (Requires statistical distribution policy).
- **Stratified Sampling**: `NOT YET AUTHORIZED` (Requires formal stratification grid authorization).
- **Boundary-Case Selection**: `PROVISIONAL` (Recommended for structural testing, but specific boundary thresholds remain unauthorized).

---

## 19. Scenario Budget & Count Policy

```
BENCHMARK SCENARIO COUNT NOT YET AUTHORIZED
```

### Policy Audit Status:
- **Total Scenario Count**: `NOT YET AUTHORIZED` (No fixed total scenario count is authorized).
- **Scenarios Per Class**: `NOT YET AUTHORIZED` (No per-class quota is authorized).
- **Scenarios Per Difficulty Tier**: `NOT YET AUTHORIZED` (No per-difficulty quota is authorized).
- **Scenarios Per Commodity**: `NOT YET AUTHORIZED` (No per-commodity quota is authorized).
- **Rule**: Inventing arbitrary numbers (e.g., "10 scenarios per category", "100 total benchmark scenarios") without source contract authority is **STRICTLY PROHIBITED**.

---

## 20. Commodity Coverage Policy

```
BENCHMARK COMMODITY COVERAGE STRATEGY NOT YET AUTHORIZED
```

### Policy Audit Status:
- The AI-Food-Packaging-Optimizer remains strictly **COMMODITY-AGNOSTIC**.
- Specific food commodities (e.g. durian, mango, fresh-cut produce) are domain examples and **MUST NOT** be hardcoded as default project scope or default benchmark scenarios.
- Benchmark scenario specifications MUST evaluate packaging requirement envelopes without assuming fixed commodity priorities.

---

## 21. Production Representativeness Criteria
To claim that a benchmark scenario suite is "representative of production workload", the project MUST possess empirical telemetry evidence.

### Required Evidence for Representativeness Claim:
1. Operational logs from `REAL_PRODUCTION_WORKLOAD` or `REAL_PILOT_WORKLOAD`.
2. Formally authorized domain-priority distributions from project stakeholders.

### Prohibited Representativeness Claims:
- Representativeness **CANNOT** be claimed from unit test fixtures.
- Representativeness **CANNOT** be claimed from synthetic test datasets.
- Representativeness **CANNOT** be claimed from material evidence observation counts.
- Representativeness **CANNOT** be claimed from arbitrary developer intuition.

---

## 22. Cold-Start Benchmark Execution Protocol
All Tier-3 optimizer benchmarks specified under M7-E2 are strictly **COLD-START BENCHMARKS**.

- **REQ-COLD-01 (Independent Executability)**: Cold-start benchmark scenarios MUST be executable starting from zero precomputed memory.
- **REQ-COLD-02 (Prohibition of Tier-1 Dependencies)**: Cold-start benchmarks **MUST NOT** require a Tier-1 exact cache hit.
- **REQ-COLD-03 (Prohibition of Tier-2 Warm-Start Seeds)**: Cold-start benchmarks **MUST NOT** require Tier-2 warm-start state selection or pre-existing seed populations.
- **REQ-COLD-04 (Prohibition of External Caches)**: Cold-start benchmarks **MUST NOT** require Redis, external disk caches, or precomputed solution stores.
- **REQ-COLD-05 (Execution Boundary)**: The optimizer MUST be evaluated strictly against the deep-optimization input contract defined in M7-A.

---

## 23. Tier-1 and Tier-2 Scenario Scope Boundaries
The three architectural tiers defined in M6 and M7 maintain strict separation within benchmark scenario design:

- **Tier-1 (Exact Lookup Engine)**:
  - Behavior: Exact matching against precomputed state store (B5A/B5D).
  - Benchmark Scope: Tier-1 is an exact memory retrieval mechanism, **NOT an optimizer**. Tier-1 exact hits MUST NOT be used to benchmark Tier-3 search solvers.
- **Tier-2 (Warm-Start Refinement Handoff)**:
  - Behavior: State selection strategy remains **UNAUTHORIZED** per M6-K.
  - Benchmark Scope: Scenario specifications **MUST NOT** define Tier-2 warm-start selection benchmark scenarios requiring specific distance or similarity metrics.
- **Tier-3 (Deep Inverse-Design Optimizer)**:
  - Behavior: Multi-objective search solver execution.
  - Benchmark Scope: **Primary focus of M7-E2 benchmark scenario specification**.

---

## 24. Expected Outcome Governance
A benchmark scenario defines the **PROBLEM INPUT**, not the optimization outcome.

- **REQ-OUTCOME-01 (Prohibition of Stored Winners)**: Benchmark scenarios **MUST NOT** store pre-selected "winning" algorithms or expected solver rankings.
- **REQ-OUTCOME-02 (Prohibition of Fabricated Pareto Fronts)**: Benchmark scenarios **MUST NOT** store fabricated or manually drawn expected Pareto fronts.
- **REQ-OUTCOME-03 (Separation of Input and Output)**: The scenario record defines problem inputs. Actual scientific model execution and solver search produce the problem outputs.
- **REQ-OUTCOME-04 (Reference Pareto Front Method Unresolved)**: If a reference Pareto front is required in future empirical trials to compute quality indicators (e.g. Hypervolume, IGD), the procedure for generating the reference front (e.g. exhaustive search, super-volume union) remains:

```
REFERENCE PARETO FRONT GENERATION METHOD NOT YET AUTHORIZED
```

---

## 25. Benchmark Scenario Record Specification (JSON Schema Structure)
The formal specification of a benchmark scenario record is defined below.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BenchmarkScenarioRecord",
  "type": "object",
  "required": [
    "metadata",
    "optimization_state_identity",
    "validity_status"
  ],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["scenario_id", "scenario_origin", "creation_timestamp"],
      "properties": {
        "scenario_id": {"type": "string"},
        "scenario_name": {"type": "string"},
        "scenario_origin": {
          "type": "string",
          "enum": [
            "REAL_SCIENTIFIC_STATE",
            "SYNTHETIC_TEST_SCENARIO",
            "REAL_PRODUCTION_WORKLOAD",
            "REAL_PILOT_WORKLOAD",
            "DEMO"
          ]
        },
        "creation_timestamp": {"type": "string", "format": "date-time"},
        "tags": {"type": "array", "items": {"type": "string"}}
      }
    },
    "optimization_state_identity": {
      "type": "object",
      "required": [
        "requirement_envelope",
        "package_geometry",
        "active_objectives",
        "eligible_candidate_ids"
      ],
      "properties": {
        "requirement_envelope": {"type": "object"},
        "package_geometry": {"type": "object"},
        "active_objectives": {"type": "array", "items": {"type": "string"}},
        "eligible_candidate_ids": {"type": "array", "items": {"type": "string"}}
      }
    },
    "scientific_provenance": {
      "type": "object",
      "description": "OPTIONAL metadata containing source database IDs, evidence records, and model version trace IDs. STRICTLY SEPARATE FROM IDENTITY."
    },
    "validity_status": {
      "type": "string",
      "enum": [
        "EXECUTABLE",
        "SCENARIO_INVALID_INCOMPLETE_GEOMETRY",
        "SCENARIO_INVALID_CORRUPTED_ENVELOPE",
        "SCENARIO_INVALID_EMPTY_OBJECTIVES",
        "SCENARIO_INVALID_UNAUTHORIZED_OBJECTIVE"
      ]
    },
    "structural_class": {
      "type": "string",
      "enum": [
        "CLASS_A_FULLY_COMPUTABLE",
        "CLASS_B_INTERVAL_UNCERTAINTY",
        "CLASS_C_PARTIALLY_UNRESOLVED",
        "CLASS_D_NO_FEASIBLE_SOLUTION",
        "CLASS_E_SCIENTIFIC_EVALUATION_FAILURE"
      ]
    },
    "reference_pareto_front": {
      "type": "null",
      "description": "NOT YET AUTHORIZED. Must remain null."
    }
  },
  "additionalProperties": false
}
```

---

## 26. Pre-Experiment Scenario Validation Suite (Design Specification)
Before any scenario is accepted into a future benchmark experiment, it MUST pass a pre-experiment validation suite.

### Required Validation Checks:
1. **Canonical Identity Check**: Hashing the 4-part identity succeeds and produces a valid 64-character SHA-256 string per M6-F.
2. **Identity Field Audit**: Hashing inputs contain ONLY Envelope, Geometry, Active Objectives, and Candidate IDs. No biological text, no provenance, no metadata.
3. **Candidate Set Validation**: All candidate IDs resolve to valid `PackagingCandidate` objects in the candidate space.
4. **Objective Set Validation**: All active objective keys belong to the authorized M6-B3 objective pool (`f_thickness`, `f_moisture_margin`, `f_gas_alignment`, `f_shelf_life_margin`).
5. **Geometry Validation**: Surface area $A > 0$ and headspace volume $V > 0$.
6. **Envelope Validation**: Requirement envelope contains no corrupted schema structures.
7. **Prohibition Audits**:
   - No pre-ordered candidate rankings embedded in candidate set.
   - No numerical values substituted for `UNKNOWN`.
   - No collapsed min/max intervals.
   - No stored expected Pareto fronts or algorithm winners.

---

## 27. Conceptual Benchmark Scenario Matrix
The matrix below outlines the conceptual scenario types required for future empirical benchmark suites, along with their authorization and readiness status:

| Scenario Type | Purpose | Authorization Status | Benchmark Readiness |
|:---|:---|:---|:---|
| **Cold-Start Class A (Deterministic)** | Baseline multi-objective optimization performance. | `AUTHORIZED` | **Ready for M7-E4** |
| **Cold-Start Class B (Interval/Uncertainty)** | Robustness under input ranges and QSAR predictions. | `AUTHORIZED` | **Ready for M7-E4** |
| **Cold-Start Class C (Partially Unresolved)** | Verification of `UNKNOWN` feasibility propagation. | `AUTHORIZED` | **Ready for M7-E4** |
| **Cold-Start Class D (No-Feasible-Solution)** | Empty Pareto front detection and constraint enforcement. | `AUTHORIZED` | **Ready for M7-E4** |
| **Cold-Start Class E (Scientific Failure)** | Error recovery and fault tolerance under model edge cases. | `AUTHORIZED` | **Ready for M7-E4** |
| **Production-Derived Scenarios** | Real-world operational workload benchmarking. | `NOT ESTABLISHED` | **Blocked (Requires Telemetry)** |
| **Pilot-Derived Scenarios** | Pilot deployment workload benchmarking. | `NOT ESTABLISHED` | **Blocked (Requires Telemetry)** |
| **Tier-1 Exact Lookup Scenarios** | Exact precomputed state retrieval benchmarking. | `AUTHORIZED (M6-H)` | **Out of Tier-3 Scope** |
| **Tier-2 Warm-Start Scenarios** | Warm-start state selection benchmarking. | `NOT YET AUTHORIZED` | **Blocked (Requires M6-K Strategy)** |

---

## 28. M7-E3 Implementation Readiness Matrix
This matrix assesses project readiness to move to Milestone M7-E3 (Optimizer Benchmark Infrastructure & Execution Design):

| Component | Status | Missing Authorization / Required Action |
|:---|:---|:---|
| **Scenario Identity Standard** | `AUTHORIZED` | None (M6-F 4-part identity frozen). |
| **Requirement Envelope Contract** | `AUTHORIZED` | None (M6-A / M6-B1 contract frozen). |
| **Package Geometry Contract** | `AUTHORIZED` | None (M6-A geometry fields frozen). |
| **Active Objective Set Contract** | `AUTHORIZED` | None (M6-B3 objectives frozen). |
| **Eligible Candidate Set Contract** | `AUTHORIZED` | None (M6-B2A candidate builder frozen). |
| **Scientific Data Provenance Protocol** | `AUTHORIZED` | None (Identity ≠ Provenance rule enforced). |
| **Uncertainty Coverage Policy** | `AUTHORIZED` | None (M6 uncertainty categories preserved). |
| **Feasibility Coverage Policy** | `AUTHORIZED` | None (All feasibility states supported). |
| **Cold-Start Execution Protocol** | `AUTHORIZED` | None (M7-A input contract frozen). |
| **Pre-Experiment Validation Design** | `AUTHORIZED` | None (Validation checks specified). |
| **Scenario Classification Taxonomy** | `AUTHORIZED` | None (Classes A through E defined). |
| **Scenario Sampling Strategy** | `NOT YET AUTHORIZED` | Sampling strategy decision required. |
| **Scenario Budget & Count** | `NOT YET AUTHORIZED` | Fixed scenario count decision required. |
| **Commodity Coverage Strategy** | `NOT YET AUTHORIZED` | Commodity priority authorization required. |
| **Production Representativeness** | `NOT ESTABLISHED` | Real production telemetry (`ABSENT`). |
| **Tier-2 Warm-Start Scenarios** | `NOT YET AUTHORIZED` | Tier-2 distance metric authorization required (M6-K). |
| **Reference Pareto Front Generation** | `NOT YET AUTHORIZED` | Reference front generation method decision required. |

---

## 29. Explicit Non-Decisions & Unauthorized Scope
In accordance with zero-code design discipline, Milestone M7-E2 **DOES NOT AUTHORIZE**:

1. **Optimizer Algorithm Selection**: No solver (NSGA-II, NSGA-III, MOEA/D, SPEA2, Bayesian Optimization, PSO) is selected or authorized.
2. **Optimizer Ranking / Scoring**: No algorithm ranking, scoring, or winner selection is performed.
3. **Scenario Sampling Distribution**: No numerical sampling method or scenario probability distribution is authorized.
4. **Scenario Count**: No numerical total scenario count or quota is invented or authorized.
5. **Production Workload Distribution**: No fictional production workload distribution is created.
6. **Commodity Priority**: No food commodity is given priority or assigned as default scope.
7. **Reference Pareto Front Method**: No procedure for computing reference Pareto fronts is authorized.
8. **Tier-2 State Selection Metric**: No distance or similarity function for Tier-2 warm-starting is authorized.
9. **Numerical Benchmark Thresholds**: No function evaluation caps, generation limits, or population sizes are authorized.
10. **Evaluation Budget & Termination**: No numerical budget caps or stopping criteria are authorized.

---

## 30. Forensic Self-Audit
Before finalizing this specification, the following forensic audit assertions were verified against the codebase and repository docs:

- [x] **M6-A through M6-J contracts remain 100% frozen and unchanged.**
- [x] **M7-A execution contract remains 100% frozen and unchanged.**
- [x] **M7-B authorization audit remains 100% frozen and unchanged.**
- [x] **M7-C selection requirements remain 100% frozen and unchanged.**
- [x] **M7-D decision framework remains 100% frozen and unchanged.**
- [x] **M7-E1 evaluation policy remains 100% frozen and unchanged.**
- [x] **No optimizer algorithm was selected, ranked, or scored.**
- [x] **No benchmark code was implemented or executed.**
- [x] **No synthetic benchmark results or Pareto fronts were fabricated.**
- [x] **No fictional production workload telemetry was generated.**
- [x] **No numerical scenario count or sampling distribution was invented.**
- [x] **No commodity priorities were assigned.**
- [x] **No Tier-2 state selection metrics were introduced.**
- [x] **No numerical budget thresholds were authorized.**
- [x] **Frozen M6 4-part Optimization-State Identity was strictly preserved.**
- [x] **Scientific provenance was strictly separated from canonical identity.**
- [x] **Commodity-agnostic architectural scope was preserved.**
- [x] **Zero production Python code files were modified.**
- [x] **Zero unit test files were modified.**
