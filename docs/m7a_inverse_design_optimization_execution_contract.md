# M7-A: Inverse-Design Optimization Execution Contract

## 1. Status
**PROPOSED DESIGN CONTRACT — AUDIT READY**

## 2. Scope & Purpose
This document establishes the formal design contract for the **Tier-3 Deep Inverse-Design Optimization Execution Path** of the AI-Based Intelligent Food Packaging Material Recommendation System.

Milestone M7-A is strictly a **DESIGN CONTRACT**. In accordance with project governance:
- **No optimization algorithms** (e.g., NSGA-II, MOEA/D, Bayesian optimization) are implemented.
- **No surrogate machine learning models** are trained, evaluated, or instantiated.
- **No evolutionary operators** (mutation, crossover, selection) are coded.
- **No Tier-2 state selection metrics** are introduced.
- Existing scientific contracts (M6-A problem formulation, M6-B1 filtering, M6-B2A candidate construction, M6-B2B candidate evaluation, M6-B3 objective evaluation, M6-B4A Pareto dominance, M6-B4B Pareto front construction, and M6-B5 storage contracts) remain immutable foundations.

M7-A defines the execution boundary, data pipeline, input/output schemas, and failure states for deep multi-objective inverse optimization.

---

## 3. Terminology & Schema Lineage
This contract strictly reuses existing, authorized project terminology and schemas:

| Term / Symbol | Definition & Authority | Source Contract |
|:---|:---|:---|
| `PackagingRequirementEnvelope` | Phase 4 requirement envelope (OTR, WVTR, temperature, RH, etc.) | `app/schemas/packaging_requirements.py` |
| `PackageGeometry` | Package dimensions, surface area, headspace, product mass | `app/schemas/optimization.py` |
| `active_objectives` | List of active objective identifiers ($f_1 \dots f_4$) | `docs/m6a_objective_contract.md` |
| `eligible_candidate_materials` | Feasible candidate materials passing M6-B1 search-space filters | `docs/m6b1_optimization_contracts.md` |
| `PackagingCandidate` | Constructed candidate design with decision variables & properties | `docs/m6b2a_candidate_construction.md` |
| `CandidateScientificEvaluationResult` | Scientific evaluation result & Phase 5 constraint compliance | `docs/m6b2b_candidate_scientific_evaluation_report.md` |
| `ObjectiveValue` / `ObjectiveEvaluator` | Objective evaluations ($f_{\text{thickness}}, f_{\text{moisture\_margin}}, \dots$) | `docs/m6b3_objective_evaluation_report.md` |
| `dominates()` | Exact Pareto dominance primitive ($A \prec B$) | `docs/m6b4a_pareto_dominance_report.md` |
| `ParetoFront` / `ParetoCandidate` | Immutable non-dominated solution collection and solver metadata | `docs/m6b4b_pareto_front_report.md` |
| `PrecomputedOptimizationState` | Stored optimization record (Identity, Result, Metadata) | `docs/m6b5a_precomputed_state_store_contract.md` |

No existing terminology is replaced or modified.

---

## 4. Optimization Input Contract
The input to the M7 deep optimizer is defined by the frozen M6-A Optimization-State Identity. M7 MUST NOT introduce a secondary or competing definition of optimization identity.

### Input Schema Definition
```python
class DeepOptimizationInput(BaseModel):
    """
    Formal input contract for Tier-3 deep inverse-design optimization.
    """
    requirement_envelope: PackagingRequirementEnvelope = Field(
        ...,
        description="Phase 4 PackagingRequirementEnvelope defining Target OTR, WVTR, temperature, RH, and shelf life."
    )
    package_geometry: PackageGeometry = Field(
        ...,
        description="Target PackageGeometry defining surface area, headspace volume, and product mass."
    )
    active_objectives: List[str] = Field(
        ...,
        description="Active objective identifiers (e.g. ['material_cost', 'shelf_life_margin'])."
    )
    eligible_candidate_materials: List[PackagingCandidate] = Field(
        ...,
        description="Collection of eligible PackagingCandidate materials composing the search space."
    )
    solver_configuration: Optional[DeepOptimizerConfiguration] = Field(
        default=None,
        description="Optional execution configuration (max evaluations, time budget, random seed)."
    )
    optional_warm_start_population: Optional[List[PackagingCandidate]] = Field(
        default=None,
        description="Abstract optional seed population from Tier-2 handoff (if available and authorized)."
    )
```

M7 cold-start execution is completely self-contained and operates directly on `requirement_envelope`, `package_geometry`, `active_objectives`, and `eligible_candidate_materials`.

---

## 5. Candidate Search-Space Contract
M7 operates over candidate design vectors $\mathbf{x} \in \mathcal{X}$ derived from the M6-B1 candidate search space.

### Decision Variable Boundaries (Authorized M6-A / M6-B):
1. **Material Identifier** (`material_id`): Verified material UUID from M5 database.
2. **Layer Structure** (`layer_structure`): Single layer (`MONO`) or laminated structure (`LAMINATE`) where empirically verified in M5 evidence.
3. **Thickness** (`thickness_m` / `total_thickness_um`): Discrete thickness values from empirical M5 observations or authorized discretization intervals.

### Strict Boundary Rules:
- **NO Invented Decision Variables**: M7 MUST NOT introduce unauthorized decision variables (e.g., invented barrier coatings, unmeasured additive concentrations).
- **NO Invented Material Classes**: M7 MUST NOT generate hypothetical materials absent from M5 database evidence.
- **NO Invented Geometries**: Package geometry variables are limited to the target `PackageGeometry` passed in the input.
- **NO Unauthorized Objectives**: Economic cost and quantitative LCA carbon footprint objectives remain `DEFERRED — DATA GAP` per M6-A objective contract.

---

## 6. Execution Pipeline & Orchestration Sequence
M7 orchestrates existing M6 scientific primitives in a strict, unalterable execution sequence:

```
                  +-----------------------------------+
                  |      DeepOptimizationInput        |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  1. Candidate Construction        |  (M6-B2A)
                  |     (PackagingCandidate)          |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  2. Candidate Scientific Eval     |  (M6-B2B)
                  |     (Recalculate Transmission)    |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  3. Hard Constraint Evaluation    |  (Phase 5)
                  |     (FEASIBLE / INFEASIBLE / UNK) |
                  +-----------------------------------+
                                    |
                  +-----------------+-----------------+
                  |                                   |
           (If INFEASIBLE / UNKNOWN)           (If FEASIBLE)
                  |                                   |
                  v                                   v
          [Discard / Log]             +-----------------------------------+
                                      |  4. Objective Evaluation          |  (M6-B3)
                                      |     (f_1, f_2, f_3, f_4)          |
                                      +-----------------------------------+
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |  5. Pareto Dominance Filtering    |  (M6-B4A)
                                      |     (dominates() Primitive)       |
                                      +-----------------------------------+
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |  6. Pareto Front Construction     |  (M6-B4B)
                                      |     (ParetoFront Output)          |
                                      +-----------------------------------+
```

M7 MUST NOT duplicate or rewrite the scientific logic inside M6-B2A, M6-B2B, M6-B3, M6-B4A, or M6-B4B.

---

## 7. Hard-Constraint & Feasibility Boundary
M7 MUST NOT bypass or relax Phase 5 deterministic hard constraints:

1. **Strict Non-Feasibility Exclusion**: A candidate evaluated as `INFEASIBLE` under Phase 5 constraints MUST NOT enter the feasible Pareto set under any circumstances.
2. **Strict UNKNOWN Rule**: An `UNKNOWN` constraint status MUST NOT be converted to `FEASIBLE` ($\text{UNKNOWN} \ne \text{FEASIBLE}$). Candidates with `UNKNOWN` status are excluded from the deterministic Pareto front.
3. **No Compensatory Safety Trade-offs**: An optimizer MUST NEVER trade off food safety or barrier violation ($WVTR > WVTR_{max}$ or $OTR < OTR_{ferment}$) against resource or thickness minimization.

---

## 8. Multi-Objective Boundary & Non-Scalarization
M7 is strictly a **Multi-Objective Optimizer**:

1. **No Scalar Weighting**: M7 MUST NOT collapse the multi-objective vector into an arbitrary weighted single score ($w_1 f_1 + w_2 f_2$).
2. **No Utility / Ranking Functions**: M7 MUST NOT calculate composite "best material" scores.
3. **Preservation of Objective Directions**: Objectives are evaluated in their native trade-off directions as defined by M6-B3:
   - $f_{\text{thickness}}$: `MINIMIZE` ($\mu\text{m}$)
   - $f_{\text{moisture\_margin}}$: `MAXIMIZE` (Margin beyond $WVTR_{max}$)
   - $f_{\text{gas\_alignment}}$: `MINIMIZE` (Target envelope distance)
   - $f_{\text{shelf\_life\_margin}}$: `MAXIMIZE` (Days beyond target shelf life)

---

## 9. Uncertainty Handling
M7 preserves scientific uncertainty across all evaluation steps:

1. **Interval Arithmetic**: When barrier properties or requirement targets are expressed as intervals $[v_{min}, v_{max}]$, objective evaluations MUST preserve interval bounds rather than collapsing to midpoints.
2. **Uncertainty Profiles**: Every `ParetoCandidate` emitted by M7 retains its `UncertaintyProfile` (`DETERMINISTIC_POINT`, `INTERVAL`, `QSAR_BOUNDED`).
3. **Zero Conversion of UNKNOWN**: Epistemic uncertainty (`UNKNOWN`) is preserved explicitly in metadata logs.

---

## 10. Pareto Output Contract
The logical output of M7 is an immutable `ParetoFront` object defined by the M6-B4B schema.

### Emitted Payload Properties:
- `optimization_run_id`: Unique execution UUID.
- `timestamp`: ISO-8601 timestamp.
- `candidate_count`: Integer count of non-dominated Pareto candidates.
- `candidates`: List of non-dominated `ParetoCandidate` objects.
- `solver_metadata`: `OptimizationMetadata` recording algorithm name, iterations completed, execution time (ms), and `cache_hit = False`.
- `constraint_policy_version`: Policy version string.

M7 MUST NOT introduce a competing Pareto front schema.

---

## 11. Empty Pareto Front Handling
When no candidate in the search space satisfies all required hard constraints (over-constrained problem):
1. M7 MUST NOT fabricate synthetic fallback candidates.
2. M7 MUST NOT select an `INFEASIBLE` candidate as a "least-bad" solution.
3. M7 MUST NOT convert `UNKNOWN` candidates into `FEASIBLE` seeds.
4. M7 MUST emit a valid, empty `ParetoFront` with `candidate_count = 0` and `candidates = []`, accompanied by solver metadata indicating zero feasible solutions found.

---

## 12. Optimizer Algorithm Authorization Status

```
OPTIMIZER ALGORITHM NOT YET AUTHORIZED
```

### Forensic Audit Findings:
- M6-A Section 10 describes NSGA-II, NSGA-III, and MOEA/D as *conceptual response tiers* for deep optimization.
- However, **no specific numerical solver algorithm, population size, mutation operator, crossover mechanism, or selection routine has been formally authorized or selected** in project design documents.
- M7-A leaves the solver implementation class abstract (`BaseDeepOptimizerEngine`). No algorithm is selected based on general engineering preference.

---

## 13. Surrogate Model Authorization Status

```
SURROGATE MODEL SPECIFICATION NOT YET AUTHORIZED
```

### Forensic Audit Findings:
- Research documentation references surrogate-guided optimization as a potential future acceleration mechanism.
- However, **no surrogate model architecture (e.g. Random Forest, Gaussian Process, Neural Network), training dataset, feature representation, target outputs, loss function, or retraining policy is authorized**.
- M7 execution MUST NOT depend on or invoke surrogate ML models.

---

## 14. Initialization Contract & Cold-Start Primacy
M7 MUST support **COLD-START EXECUTION** from scratch without requiring Tier-1 cache hits or Tier-2 warm-start seeds.

### Initialization Architecture:
- **Cold-Start (Default)**: Generates initial candidate configurations directly from `eligible_candidate_materials`.
- **Warm-Start (Optional)**: If `optional_warm_start_population` is provided (via M6-J Tier-2 handoff), M7 ingests the candidates as an initial population seed.

---

## 15. Warm-Start Boundary
The boundary between Tier-2 handoff (M6-J) and Tier-3 deep optimization (M7) is defined as:

$$\text{Tier2HandoffRequest} \xrightarrow{\text{extract seeds}} \text{Target Search-Space Filter (M6-B1)} \xrightarrow{\text{re-evaluate}} \text{Initial Population} \to \text{M7 Optimizer}$$

### Boundary Constraints:
- M7 DOES NOT define how Tier-2 seeds are selected from the store (blocked per M6-K).
- M7 DOES NOT define similarity, nearest-neighbor, or distance metrics.
- If no warm-start seed is provided, M7 automatically executes a cold start.

---

## 16. Termination Contract
M7 defines abstract configuration parameters for solver termination without assigning hardcoded numerical values:

```python
class DeepOptimizerConfiguration(BaseModel):
    """
    Abstract solver execution parameters.
    """
    max_generations: Optional[int] = Field(default=None, description="Maximum solver iterations/generations.")
    max_evaluations: Optional[int] = Field(default=None, description="Maximum scientific evaluations budget.")
    time_budget_ms: Optional[float] = Field(default=None, description="Maximum execution time budget in milliseconds.")
    convergence_tolerance: Optional[float] = Field(default=None, description="Objective stability tolerance.")
    random_seed: Optional[int] = Field(default=None, description="Controlled random seed for reproducibility.")
```

Numerical values for budgets and tolerances MUST be supplied via runtime policy configurations.

---

## 17. Execution Failure States
M7 defines explicit execution failure classifications, distinguishing scientific `UNKNOWN` from technical execution `ERROR`:

| Failure Classification | Trigger Cause | System Response |
|:---|:---|:---|
| `INVALID_INPUT` | Malformed envelope or invalid geometry parameters | Raises `ValueError` with detailed validation context |
| `EMPTY_SEARCH_SPACE` | M6-B1 returns zero eligible candidate materials | Returns empty `ParetoFront` (`candidate_count = 0`) |
| `ALL_INFEASIBLE` | 100% of candidate space fails Phase 5 hard constraints | Returns empty `ParetoFront` (`candidate_count = 0`) |
| `ALL_UNKNOWN` | 100% of candidate space has `UNKNOWN` status | Returns empty `ParetoFront` (or provisional front if requested) |
| `EXECUTION_TIMEOUT` | Time budget (`time_budget_ms`) exceeded | Returns best non-dominated `ParetoFront` discovered before timeout |
| `EVALUATION_ERROR` | Technical exception in scientific evaluation module | Raises `RuntimeError` isolating the failing candidate |

---

## 18. Determinism & Reproducibility Boundary
M7 MUST guarantee **deterministic execution** when supplied with a fixed `random_seed` and identical `DeepOptimizationInput`:
1. Candidate evaluation order is deterministic.
2. Dominance comparison ties are broken using lexicographical candidate ID sorting.
3. Stochastic solver algorithms (when authorized) MUST accept an explicit seed parameter.

---

## 19. Performance Boundary
M6-A Section 10 specifies a Tier-3 execution target of $< 3000\text{ ms}$.
- **Architectural Target**: $< 3000\text{ ms}$ is an architectural design target.
- **No Empirical Claim**: M7-A DOES NOT claim that 3000 ms latency has been achieved prior to implementation and benchmarking.

---

## 20. Progressive Tier Relationship (Tier 1 $\to$ Tier 2 $\to$ Tier 3)
The complete runtime flow across optimization tiers is:

```
[User Optimization Request]
            |
            v
   Tier-1 Exact Lookup (B5D)
   - Match canonical identity?
       ├── YES ──> Return stored ParetoFront verbatim (Tier 1 HIT)
       └── NO  ──> Tier-1 EXACT_MISS
                       |
                       v
              Tier-2 Warm-Start (B5E)
              - Compatible seed available & authorized?
                  ├── YES ──> Inject seed into M7 initial population (Tier 2 WARM START)
                  └── NO  ──> Fallback to M7 Cold Start
                                  |
                                  v
                         Tier-3 Deep Optimization (M7)
                         - Executes full multi-objective search
                         - Returns ParetoFront
```

Tier-3 execution DOES NOT depend on Tier-1 or Tier-2 availability.

---

## 21. Precomputed-State Output Relationship
Upon successful execution of M7:
1. Emitted `ParetoFront` can be combined with `DeepOptimizationInput` to form a candidate `PrecomputedOptimizationState`.
2. Submitted to B5C `PreStorageValidator` for integrity validation.
3. Stored in B5A `InMemoryOptimizationStateStore` if precomputed state storage is authorized.

---

## 22. Feedback-Loop & Downstream Boundaries
M7 execution terminates upon emitting the `ParetoFront`:
- **Phase 7 Recommendation**: Downstream MCDA ranking and user preference elicitation operate on the M7 `ParetoFront`.
- **Real-World Feedback Loops**: Material testing feedback and model retrain loops are external downstream components. M7 contains NO internal feedback or learning rules.

---

## 23. API & Data Access Boundaries
- **Framework Independence**: M7 is a pure domain-level optimization engine module. It MUST NOT import FastAPI, HTTP routing, or web server components.
- **Domain Data Access**: M7 consumes candidate materials through M6-B1 domain contracts. It MUST NOT hardcode raw JSON datasets or execute direct SQL queries inside the optimizer.

---

## 24. Implementation Readiness Assessment

| Component | Readiness | Status / Blocker |
|:---|:---:|:---|
| **Input Schema (`DeepOptimizationInput`)** | **READY** | Reuses frozen M6-A identity & M6-B schemas |
| **Search Space Contract** | **READY** | Reuses M6-B1 filtering & candidate variables |
| **Scientific Pipeline (B2A, B2B, B3, B4A, B4B)** | **READY** | Fully implemented and verified (275 tests passing) |
| **Output Schema (`ParetoFront`)** | **READY** | Reuses verified M6-B4B contract |
| **Solver Algorithm (NSGA-II / MOEA/D)** | **NOT READY** | `OPTIMIZER ALGORITHM NOT YET AUTHORIZED` |
| **Surrogate Model Specification** | **NOT READY** | `SURROGATE MODEL SPECIFICATION NOT YET AUTHORIZED` |
| **Tier-2 Selection Metric** | **NOT READY** | `TIER-2 SELECTION STRATEGY NOT YET AUTHORIZED` (M6-K) |

---

## 25. Forensic Self-Audit
- [x] M6 contracts remain immutable and unchanged.
- [x] M6-K decision (`TIER-2 SELECTION STRATEGY NOT YET AUTHORIZED`) remains unchanged.
- [x] No production code or solver algorithms implemented.
- [x] No NSGA-II, MOEA/D, or surrogate models coded.
- [x] No distance, similarity, or ranking metrics created.
- [x] Phase 4/5 scientific boundaries strictly preserved.
- [x] M6-B2B, M6-B3, M6-B4A, and M6-B4B primitives reused conceptually.
- [x] `UNKNOWN` status and interval bounds preserved.
- [x] Empty Pareto front behavior explicit.
- [x] Cold-start execution independent of Tier-1/Tier-2.
- [x] Framework and data-access boundaries strictly enforced.

---

## 26. Final Contract Status

```
M7-A INVERSE-DESIGN OPTIMIZATION EXECUTION CONTRACT COMPLETE
```
