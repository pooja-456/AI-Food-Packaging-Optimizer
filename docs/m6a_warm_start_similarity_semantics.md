# M6-A Warm-Start Similarity Semantics

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Source Terminology
**EXISTING FACT**: The foundational architecture uses several terms related to Tier-2 behavior:
- "Warm-start refinement"
- "Nearest-neighbor runtime" (mentioned in the M6-B5 scope)
- "Suitable non-exact states"
- "Precomputed solution"
The language envisions a capability to seed the runtime Pareto optimizer with a high-quality initial population derived from a previously computed state, avoiding starting from scratch.

## 3. Warm-Start Requirement
**SOURCE-AUTHORIZED REQUIREMENT**: The architecture formally requires the ability to execute a "warm start" (Tier-2) when a Tier-1 exact cache retrieval is unavailable, to accelerate the optimization timeline.

## 4. Tier-2 State Selection
**UNRESOLVED**: WARM-START STATE SELECTION MECHANISM NOT SOURCE-AUTHORIZED. The existing architecture entirely fails to specify *how* a suitable precomputed state is algorithmically selected when an exact match is missing. 

## 5. Nearest-Neighbor Requirement
**EXISTING FACT**: While the term "nearest-neighbor" appears as a design objective for M6-B5, the architecture does not provide the mathematical framework necessary to explicitly mandate the "mathematically nearest optimization state." 

## 6. Distance / Similarity Definition
**ARCHITECTURAL CONSEQUENCE**: BLOCKED — NEAREST-NEIGHBOR DISTANCE NOT AUTHORIZED. The Optimization-State Identity comprises intervals and sets. The architecture provides absolutely zero mathematical definitions for calculating distance or similarity across these non-scalar data structures.

## 7. Interval Similarity
**EXISTING FACT**: The architecture defines interval bounds (e.g., `[min, max]`) but provides no metric for comparing them.
**ARCHITECTURAL CONSEQUENCE**: The system cannot currently measure the similarity between Interval A and Interval B for warm-start purposes.

## 8. Candidate-Set Similarity
**EXISTING FACT**: The search space is defined by an unordered set of UUIDs.
**ARCHITECTURAL CONSEQUENCE**: The architecture does not define how to compare two candidate sets (e.g., no authorized set intersection rules or Jaccard similarity metrics).

## 9. Objective-Set Similarity
**EXISTING FACT**: The Pareto space is defined by an unordered set of active objective strings.
**ARCHITECTURAL CONSEQUENCE**: The architecture does not authorize interchanging objective sets. Attempting to warm-start an optimization problem targeting `[cost, shelf_life]` using a cached solution that optimized for `[sustainability, shelf_life]` is mathematically undefined and potentially destructive to the Pareto front construction.

## 10. Geometry Similarity
**EXISTING FACT**: Package geometry uses continuous floating-point values.
**ARCHITECTURAL CONSEQUENCE**: The architecture lacks any authorized numerical tolerance or similarity curve for deciding when two slightly different package geometries are "similar enough" to share warm-start data.

## 11. Exact vs Suitable vs Nearest
**EXISTING FACT**: 
- **Exact Reusable Optimization State**: Source-authorized (Tier-1 exact match).
- **Suitable Warm-Start State**: Source-authorized (Tier-2 conceptual goal to provide a good initial population).
- **Nearest Optimization State**: **Blocked/Undefined**. "Nearest" requires a defined mathematical metric space across intervals and sets, which does not exist in the current architecture.

## 12. Tier-1 vs Tier-2

| Tier | Source-authorized purpose | Required state | Selection mechanism | Distance required? |
|---|---|---|---|---|
| Tier-1 | Instant cache retrieval | EXACT state | Deterministic lookup / Hash match | NO |
| Tier-2 | Accelerated optimization | SUITABLE state | **UNRESOLVED** | **UNRESOLVED** |

## 13. Architectural Outcome
**ARCHITECTURAL CONSEQUENCE**: OUTCOME B — Warm-start refinement is source-required, but nearest-neighbor and its distance semantics are NOT defined and cannot be natively supported under the frozen Optimization-State Identity.

## 14. Required Future Decisions
**PROPOSED DECISION**: The architecture board must replace the assumed "nearest-neighbor" coordinate-distance concept with a formal set of authorized "similarity selection" rules. These rules must explicitly define:
- Acceptable interval overlap tolerances.
- Acceptable candidate-set intersections.
- Strict equality enforcement for Active Objectives (objectives likely cannot be swapped).

## 15. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains fully BLOCKED. The conceptual "Optimization Lattice Contract" cannot implement Tier-2 warm starts until the mathematical definition of "suitability" or "similarity" across Phase 4 requirements and candidate sets is formally established by the architecture.
