# M6-A: FORMAL OPTIMIZATION PROBLEM DEFINITION

**Project**: AI-Based Intelligent Food Packaging Material Recommendation System  
**Milestone**: M6-A (Optimization Problem Definition & Formulation Design)  
**Date**: 2026-09-28  
**Status**: DESIGN COMPLETE — AUDIT READY  

---

## 1. Executive Summary & Purpose

The primary objective of Milestone M6-A is to formally define the multi-objective optimization problem for the AI-Based Intelligent Food Packaging Material Recommendation System. 

M6-A is strictly a **DESIGN MILESTONE**. In accordance with project governance:
- **No optimization algorithms** (e.g., NSGA-II, MOEA/D, Bayesian optimization) are implemented in this milestone.
- **No surrogate machine learning models** are trained or evaluated.
- **No candidate lattice generators, Redis caches, Celery tasks, or recommendation endpoints** are introduced.
- Existing scientific contracts established in Phase 3 (Inference), Phase 4 (Physics Requirements), Phase 5 (Deterministic Hard Constraints), and M5 (PostgreSQL Canonical Data Ingestion) are treated as **immutable foundations**.

This document defines:
1. The mathematical formulation of the optimization problem.
2. The fundamental separation between **Optimization** (finding the Pareto front of feasible, non-dominated candidate designs) and **Recommendation** (filtering, ranking, and selecting designs for specific user utility).
3. The boundary between **Hard Constraints** (mandatory feasibility criteria) and **Optimization Objectives** (trade-off dimensions).
4. The handling of scientific uncertainty, evidence provenance, condition compatibility, and counterfactual queryability.

---

## 2. Separation of Optimization vs. Recommendation

A critical architectural requirement is the clean separation of the optimization layer from the recommendation layer:

```
+-----------------------------------------------------------------------------------+
|                               PHASE 4: PHYSICS ENGINE                             |
|               Derives PackagingRequirementEnvelope (OTR, WVTR, CO2TR, etc.)       |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        PHASE 5: HARD CONSTRAINT FILTER                            |
|     Filters M5 Database Materials: Evaluates FEASIBLE, INFEASIBLE, UNKNOWN        |
|                  Strict Rule: UNKNOWN is NEVER treated as FEASIBLE               |
+-----------------------------------------------------------------------------------+
                                          |
                        Feasible & Bounded Candidate Space
                                          |
                                          v
+===================================================================================+
|                        PHASE 6: MULTI-OBJECTIVE OPTIMIZATION                     |
|                                                                                   |
|  Mathematical Goal: Identify the Non-Dominated Pareto Front P*                    |
|  - Operates purely on objective vectors: f(x) = [f_1(x), f_2(x), ..., f_m(x)]     |
|  - NO arbitrary scalar weighting (no hidden W1*f1 + W2*f2)                       |
|  - NO "best material" score or single-score ranking                              |
|  - Strictly preserves uncertainty intervals and provenance                        |
|                                                                                   |
|  Output: ParetoFront (Collection of non-dominated, feasible ParetoCandidates)     |
+===================================================================================+
                                          |
                             Non-Dominated Pareto Set P*
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                      PHASE 7+: RECOMMENDATION & EXPLANATION                       |
|  - Applies user preference elicitation (e.g., prioritize shelf-life over mass)    |
|  - Evaluates qualitative corporate sustainability policies                        |
|  - Ranks candidates according to explicit Multi-Criteria Decision Analysis (MCDA)|
|  - Generates counterfactual explanations ("Why was Material A chosen over B?")    |
+-----------------------------------------------------------------------------------+
```

### Governance Rules:
1. **The Optimizer does not recommend.** It evaluates trade-offs across competing physical, operational, and material dimensions, identifying all mathematically non-dominated solutions.
2. **The Optimizer does not hide trade-offs.** It never collapses multi-objective spaces into an arbitrary weighted single score ($w_1 f_1 + w_2 f_2$).
3. **The Recommender does not optimize.** It inspects the non-dominated Pareto front, incorporates stakeholder preferences, and presents structured rationales.

---

## 3. Mathematical Problem Formulation

Let $\mathcal{M}$ denote the universe of candidate packaging materials verified in the M5 database.  
Let $\mathbf{x} \in \mathcal{X}$ denote a candidate packaging design vector defined in the decision space $\mathcal{X}$.  
Let $\mathcal{E}$ denote the scientific `PackagingRequirementEnvelope` derived by Phase 4 for a target commodity under specified environmental conditions.

The formal optimization problem is formulated as:

$$\min_{\mathbf{x} \in \mathcal{X}} \; \mathbf{f}(\mathbf{x}) = \left[ f_1(\mathbf{x}), \, f_2(\mathbf{x}), \, \dots, \, f_m(\mathbf{x}) \right]^T$$

Subject to:

### 1. Deterministic Hard Feasibility Constraints:
$$g_j(\mathbf{x}, \mathcal{E}) \le 0, \quad \forall j \in \{1, \dots, J\}$$
$$h_k(\mathbf{x}, \mathcal{E}) = 0, \quad \forall k \in \{1, \dots, K\}$$
$$\text{Status}\left(C_r(\mathbf{x}, \mathcal{E})\right) = \text{FEASIBLE}, \quad \forall C_r \in \mathcal{C}_{\text{required}}$$

Where:
- $\mathcal{C}_{\text{required}}$ is the set of required hard constraints derived by Phase 5 (e.g., maximum allowable WVTR, allowable OTR interval, test condition compatibility).
- A candidate $\mathbf{x}$ is admissible to the optimization space if and only if **all required hard constraints are strictly `FEASIBLE`**.
- If any required constraint is `INFEASIBLE`, $\mathbf{x}$ is disqualified.
- If any required constraint is `UNKNOWN`, $\mathbf{x}$ is disqualified from the deterministic Pareto set (or segregated into an exploratory provisional tier, retaining `UNKNOWN \ne FEASIBLE`).

### 2. Objective Vector:
The objective functions $f_i(\mathbf{x})$ represent competing design criteria:
- $f_1(\mathbf{x})$: Resource / Thickness Minimization ($\mu\text{m}$) $\to \min$
- $f_2(\mathbf{x})$: Moisture Transmission Deficit / Margin $\to \max$ (formulated as $-f_2(\mathbf{x}) \to \min$)
- $f_3(\mathbf{x})$: Gas Transmission Alignment / Target Envelope Distance $\to \min$
- $f_4(\mathbf{x})$: Shelf-Life Margin beyond target $\to \max$ (formulated as $-f_4(\mathbf{x}) \to \min$)

*(Economic cost and quantitative carbon footprint objectives are evaluated in `docs/m6a_objective_contract.md` and currently marked `DEFERRED — DATA GAP` due to lack of verified empirical pricing/LCA evidence in M5).*

### 3. Pareto Dominance Definition:
A feasible candidate packaging design $\mathbf{x}^{(A)}$ is said to **dominate** another feasible design $\mathbf{x}^{(B)}$ (denoted $\mathbf{x}^{(A)} \prec \mathbf{x}^{(B)}$) if and only if:

$$\forall i \in \{1, \dots, m\}, \quad f_i(\mathbf{x}^{(A)}) \le f_i(\mathbf{x}^{(B)}) \quad \land \quad \exists i \in \{1, \dots, m\} : f_i(\mathbf{x}^{(A)}) < f_i(\mathbf{x}^{(B)})$$

The goal of optimization is to determine the non-dominated Pareto front $\mathcal{P}^*$:

$$\mathcal{P}^* = \left\{ \mathbf{x}^* \in \mathcal{X}_{\text{feasible}} \;\big|\; \nexists \, \mathbf{x} \in \mathcal{X}_{\text{feasible}} : \mathbf{x} \prec \mathbf{x}^* \right\}$$

---

## 4. Input Lineage and Integration Architecture

The optimization engine does **not** operate on raw food names or direct user prompts. It ingests a strictly typed pipeline of upstream contracts:

```
[User Request: commodity, target_days, temp, RH, dimensions]
                            |
                            v
          Phase 3: Property Inference Engine
          (Infers missing physiological/compositional properties)
                            |
                            v
          Phase 4: Physics & Packaging Engine
          (Executes mass balances, respiration, sorption, kinetics)
          --> Emits: PackagingRequirementEnvelope
                            |
                            v
          Phase 5: Deterministic Hard-Constraint Filter
          (Evaluates candidate materials against envelope)
          --> Emits: FilteringResult (FEASIBLE, INFEASIBLE, UNKNOWN)
                            |
                            v
          M5 Database: Canonical Material Evidence
          (Retrieves detailed observations, layers, thickness, citations)
                            |
                            v
          Phase 6: Multi-Objective Optimization Engine
          --> Ingests: OptimizationInputEnvelope
          --> Evaluates: Decision Variables, Objectives, Bounds
          --> Emits: ParetoFront
```

### Upstream Scientific Dependencies:
1. **From Phase 3 (`backend/app/schemas/inference.py`)**:
   - Inferred commodity properties with uncertainty bounds and provenance tracking.
2. **From Phase 4 (`backend/app/schemas/packaging_requirements.py`)**:
   - `GasExchangeRequirement`: Required OTR per area ($cc / (m^2 \cdot day \cdot atm)$), required CO2TR, target $O_2$ and $CO_2$ ranges, ideal $\beta$-ratio ($P_{CO2}/P_{O2}$).
   - `MoistureRequirement`: Required WVTR per area ($g / (m^2 \cdot day)$), critical water activity ($a_{w,crit}$), moisture-limited shelf life.
   - `MicrobialRequirement`: Critical microbial threshold, growth rate ($\mu_{max}$), hurdle limits.
   - `ShelfLifeRequirement`: Target days vs. limiting mechanism.
3. **From Phase 5 (`backend/app/schemas/constraints.py`, `candidate_feasibility.py`)**:
   - `ConstraintEvaluation`: Evaluated status for each barrier (`LE`, `GE`, `IN_RANGE`), condition match level (`EXACT`, `SUPPORTED`, `INCOMPATIBLE`, `UNKNOWN`), delta warnings.
   - `CandidateFeasibility`: Aggregate feasibility partition (`FEASIBLE`, `INFEASIBLE`, `UNKNOWN`).
4. **From M5 Canonical Database (`backend/app/models/evidence.py`)**:
   - 11 packaging materials, 34 barrier observations (32 experimental, 2 QSAR predicted), thickness, structure type, layer sequences, and full literature citations.

---

## 5. Hard Constraints vs. Optimization Objectives

The boundary between hard constraints and optimization objectives is absolute:

| Feature | Hard Constraint (Phase 5) | Optimization Objective (Phase 6) |
| :--- | :--- | :--- |
| **Scientific Role** | Biological & physical survival envelope | Commercial & engineering trade-off space |
| **Pass/Fail Nature** | Binary gate: Must be `FEASIBLE` | Continuous: Non-dominated Pareto frontier |
| **Relaxation** | **Non-negotiable**: Cannot be relaxed for cost | Compensatory: Traded off across objectives |
| **Handling of UNKNOWN** | Excluded from deterministic feasibility | Preserved as uncertainty interval in Pareto metadata |
| **Examples** | $WVTR \le WVTR_{max}$, $OTR \in [OTR_{min}, OTR_{max}]$ | Total thickness minimization, shelf-life margin |

### Critical Scientific Principle:
**An optimization algorithm must never trade off food safety or biological spoilage against economic or operational objectives.** A material that violates the moisture threshold ($WVTR > WVTR_{max}$) or induces anaerobic fermentation ($OTR < OTR_{ferment}$) cannot enter the Pareto front, regardless of its low cost, minimal thickness, or sustainability credentials.

---

## 6. Uncertainty Representation and Handling

The system preserves scientific uncertainty across all calculation tiers. M6 formalizes uncertainty handling under the following rules:

1. **Measurement Uncertainty in Evidence**:
   - When material barrier properties are reported as ranges $[v_{min}, v_{max}]$ (e.g., PolyID QSAR predictions or literature intervals), the hard constraint filter tests the conservative bound.
   - In optimization objectives, interval arithmetic is preserved: the objective value is recorded as an interval $[f_{min}, f_{max}]$ rather than a collapsed midpoint.
2. **Phase 5 Rule Upheld: $\text{UNKNOWN} \ne \text{FEASIBLE}$**:
   - If test conditions are unrecorded or incompatible, the candidate status is `UNKNOWN`.
   - Candidates with `UNKNOWN` constraint status cannot enter the deterministic Pareto front $\mathcal{P}^*$.
   - They may be recorded in a separate `ProvisionalParetoFront` for exploratory analysis, accompanied by explicit warnings indicating which test data must be experimentally gathered.
3. **Predicted Evidence (PolyID QSAR)**:
   - Experimental evidence (`EXPERIMENTAL_LITERATURE_DATA`, `VERIFIED_EXTRACT`) and QSAR model predictions (`MODEL_PREDICTED`, `PREDICTIVE_ONLY`) are never combined into a single unweighted pool.
   - Every candidate retains its `evidence_classification` and any `synthetic_prediction_warning`.
   - The user interface and downstream recommendation layer must explicitly flag when a Pareto point relies on computational QSAR evidence.

---

## 7. Condition Compatibility Constraints

Permeability is temperature- and humidity-dependent. Phase 5 established explicit condition match levels:
- `EXACT`: Measured within $\pm 2^\circ\text{C}$ and $\pm 5\%\text{ RH}$ of requirement conditions.
- `SUPPORTED`: Measured under standard ambient conditions ($23^\circ\text{C}, 0\%\text{ RH}$ for gases; $38^\circ\text{C}, 90\%\text{ RH}$ for WVTR) with verified physical applicability.
- `INCOMPATIBLE`: Measured under divergent conditions without validated Arrhenius/sorption models.
- `UNKNOWN`: Environmental test conditions unrecorded in literature.

### Optimization Admissibility Rule:
Only candidates with `EXACT` or `SUPPORTED` condition matches on all active barrier constraints are admissible to the deterministic Pareto set. No arbitrary global Arrhenius, $Q_{10}$, or GAB extrapolation may be applied during optimization unless verified and emitted by the Phase 4 scientific engine.

---

## 8. Counterfactual Query Compatibility

The optimization output must structure all physical and decision variables so that counterfactual queries ("what-if" scenarios) can be executed without re-engineering the model:

1. **Shelf-Life Sensitivity**:
   - Query: *"What changes if target shelf-life increases from 14 days to 30 days?"*
   - Architecture: Upstream Phase 4 recalculates tighter $WVTR_{max}$ and $OTR$ window $\to$ Phase 5 re-filters $\to$ Optimizer computes new Pareto front $\to$ Delta comparison isolates discarded candidates.
2. **Temperature Shift**:
   - Query: *"What changes if storage temperature rises from $4^\circ\text{C}$ to $12^\circ\text{C}$?"*
   - Architecture: Respiration rate rises exponentially $\to$ Headspace $O_2$ consumption increases $\to$ Required OTR increases $\to$ Incompatible materials identified.
3. **Thickness Adjustment**:
   - Query: *"Can a thinner grade of Material X meet the requirement if package surface area increases?"*
   - Architecture: Surface area parameter adjusted in requirement envelope $\to$ Normalized barrier demand recalculated.

---

## 9. Commodity-Agnostic Principle

The optimization model is completely **commodity-agnostic**:
- It contains **zero** hardcoded food rules (e.g., no "durian rules", no "apple rules", no "fish rules").
- Durian, broccoli, and apples in the repository serve strictly as empirical test fixtures to validate the end-to-end physics and filtering pipeline.
- The optimization engine interfaces exclusively with the mathematical `PackagingRequirementEnvelope`. Any food product whose deterioration modes can be expressed via gas exchange, moisture migration, or microbial proliferation is automatically supported.

---

## 10. Runtime Performance Architecture

To achieve the runtime performance targets specified in the system design, Phase 6 optimization is structured into three execution tiers:

```
[User Request]
       |
       v
Tier 1: Precomputed Lattice / Instant Cache Lookup (< 50 ms)
- Evaluates if the exact (commodity, target_days, temp, RH) matches a precomputed baseline.
- If hit: Returns cached ParetoFront with validated timestamp.
       |
       v (Cache Miss / Custom Requirements)
Tier 2: Warm-Start Optimization (< 500 ms)
- Seeds initial population with Phase 5 FEASIBLE candidates and closest lattice neighbors.
- Solves discrete Pareto ranking across active materials.
       |
       v (High-Dimensional / Multilayer Design)
Tier 3: Deep Multi-Objective Optimization (< 3000 ms)
- Full NSGA-II / MOEA/D exploration across multilayer sequences and thickness permutations.
```

*Note: In M6-A, this architecture is defined as an interface specification. Implementation of caching, warm-starting, and deep algorithms is reserved for M6-B and M6-C.*

---

## 11. Design Consistency Confirmation

This problem definition has been reconciled against:
- Phase 3: `backend/app/schemas/inference.py` (Consistent)
- Phase 4: `backend/app/schemas/packaging_requirements.py` (Consistent)
- Phase 5: `backend/app/schemas/constraints.py` (Consistent)
- Phase 5: `backend/app/schemas/candidate_feasibility.py` (Consistent)
- M5 Canonical Data Model: `backend/app/models/evidence.py` (Consistent)
- Verified M5-B3 Database State: 47 evidence units, 11 materials, 34 barrier records (Consistent)
