# M6-A Warm-Start State Selection Contract

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Source Terminology
**EXISTING FACT**: The foundational documents use terms like "warm-start refinement," "suitable non-exact states," and "seed" to describe Tier-2 behavior. The intent is to use a precomputed solution to accelerate the convergence of the Pareto optimizer rather than iterating from a blank slate.

## 3. Warm-Start State Requirements
**EXISTING FACT**: M6-B4B (`ParetoFrontConstructor`) mathematically requires a population of `ParetoCandidate` objects, each fully populated with `ObjectiveValue` maps and valid `CalculationStatus` states. A warm-start seed must physically supply a collection of these evaluated candidates.

## 4. Objective Compatibility
**ARCHITECTURAL CONSEQUENCE**: If a cached state was optimized for Objective Set A (e.g., `[cost, shelf_life]`), its candidates mathematically lack the evaluated data for an entirely different Objective Set B (e.g., `[sustainability, shelf_life]`). Because M6-B4A explicitly rejects candidates with `UNKNOWN` objectives, transferring candidates across mismatched objective sets requires full re-evaluation.
**UNRESOLVED**: OBJECTIVE COMPATIBILITY NOT AUTHORIZED. The architecture does not define whether objective sets must be strictly identical for a warm start to occur.

## 5. Candidate-Set Compatibility
**UNRESOLVED**: CANDIDATE-SET COMPATIBILITY NOT AUTHORIZED. The architecture does not establish rules for subsets, supersets, or disjoint sets. Injecting cached candidates that the new request strictly forbids (e.g., non-biodegradable materials) would violate M6-B1 filtering semantics, but the system lacks a defined filtering layer for warm-start seeds.

## 6. Geometry Compatibility
**ARCHITECTURAL CONSEQUENCE**: Package geometry natively scales Phase 5 constraints and M6-B3 objectives (e.g., WVTR per unit area). Injecting a candidate whose objectives were precomputed under `0.1 m2` into a Pareto front targeting `1.0 m2` introduces false physics. 
**UNRESOLVED**: The architecture does not define whether geometry must perfectly match, or if an intermediate M6-B2B scaling pass is required during warm start.

## 7. Requirement Compatibility
**ARCHITECTURAL CONSEQUENCE**: Phase 4 physical requirements strictly govern Phase 5 `FEASIBLE` / `INFEASIBLE` status. A candidate that was feasible under cached State A's relaxed OTR requirement may be scientifically infeasible under the new State B's strict OTR requirement.
**UNRESOLVED**: The architecture provides no definition for when requirement intervals are "similar enough" to safely bypass Phase 5 feasibility re-checks.

## 8. Feasibility / Constraint Status
**EXISTING FACT**: M6-B4A dominance explicitly requires valid constraint statuses (no `UNKNOWN` or `INFEASIBLE` properties). A warm-start seed candidate must conceptually be `FEASIBLE` for the target request.

## 9. Exact State vs Warm Start vs Nearest State
**EXISTING FACT**:
- **Exact State Match**: 100% identity match. Safely reusable (Tier 1).
- **Nearest State**: Conceptually invalid; no metric space exists for sets/intervals.
- **Warm-Start State**: A non-exact state that is "suitable," but the architecture completely fails to define the mathematical boundaries of suitability.

## 10. Warm-Start Correctness
**SOURCE-AUTHORIZED REQUIREMENT**: For a selected warm-start state to be scientifically and computationally safe, its cached candidates must NOT violate the physical geometry scaling, the Phase 4 requirement boundaries, or the Phase 5 hard constraints of the new request. If they do, they must be stripped or re-evaluated, potentially negating the speed advantage of the cache.

## 11. Architectural Outcome
**ARCHITECTURAL CONSEQUENCE**: OUTCOME B — Warm-start refinement is source-required, but compatibility conditions are NOT defined. The architecture dictates that Tier-2 should occur, but provides zero mathematical or contractual definitions for which non-exact cached states are scientifically safe to use as seeds.

## 12. Required Future Decisions
**PROPOSED DECISION**: The architecture board must establish a formal **Warm-Start Compatibility Contract** defining:
1. Whether Objective Sets must strictly match (Equality).
2. Whether Package Geometry must strictly match, or if dynamic re-scaling is permitted.
3. Whether Phase 5 feasibility must be strictly re-evaluated for all injected warm-start candidates.

## 13. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains fully BLOCKED. The Tier-2 warm-start cache lookup mechanism cannot be implemented without formal mathematical rules dictating which cached states are permitted to be selected.
