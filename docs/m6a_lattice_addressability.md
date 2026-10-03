# M6-A Lattice Addressability

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Optimization Identity vs Lattice Address
**EXISTING FACT**: 
- **Raw User Input**: The initial payload (commodity, target shelf-life, temperature, RH, geometry).
- **Scientific Derived State**: The biological traits inferred by Phase 3 (respiration rate, water activity).
- **Optimization-State Identity**: The frozen mathematical problem bounds (Phase 4 Envelope + Geometry + Objectives + Candidate IDs).
- **Lattice Address**: The index or key used to query the Tier 1 precomputed cache.

## 3. Request-to-State Trace
**EXISTING FACT**: 
An incoming request must execute Phase 3 (inference) and Phase 4 (physics requirement generation) before the exact mathematical Optimization-State Identity physically exists in memory. The system does not possess the required frozen identity until Phase 4 completes.

## 4. Phase 3 → Phase 4 Mapping
**EXISTING FACT**: The architecture establishes a deterministic relationship where the Phase 3 resolved scientific state + primary environmental inputs mathematically dictate the Phase 4 requirement envelope. 
**ARCHITECTURAL CONSEQUENCE**: However, the existing schemas do not provide an authorized mapping mechanism to jump straight from a Request to a Lattice Address without first executing Phase 4.

## 5. Interval Addressability Constraint
**EXISTING FACT**: The frozen optimization identity relies directly on the Phase 4 Requirement Envelope, which contains non-degenerate interval bounds (OTR, WVTR). 
**ARCHITECTURAL CONSEQUENCE**: Because interval-to-scalar lattice projection is explicitly unauthorized (Decision #2B), the architecture is mathematically blocked from natively using the actual optimization-state bounds as a simple numeric lattice address.

## 6. Raw Food Context Boundary
**EXISTING FACT**: Raw food context (`commodity`, `variety`) was formally excluded from the Optimization-State Identity because its scientific effect is completely abstracted by Phase 4. 
**UNRESOLVED**: Determine whether raw food context may be used as an UPSTREAM LOOKUP INPUT. The architecture does not establish if raw context is permitted to act purely as an address namespace to bypass interval hashing, nor how to prevent such usage from reintroducing the caching fragmentation paradox identified in Decision #1A.

## 7. Collision Analysis
**Conceptual Counterexample**:
- **Request A**: Apple, 20°C, 70% RH, 30 days, same geometry/objectives/candidates.
- **Request B**: Strawberry, 20°C, 70% RH, 30 days, same geometry/objectives/candidates.
**ARCHITECTURAL CONSEQUENCE**: The primary scalar coordinates for these two requests are mathematically identical. However, their Phase 4 requirements and frozen optimization identities are fundamentally different due to distinct biological traits. A lattice indexed solely by primary scalar variables cannot distinguish them.

## 8. Safe Reuse Analysis
**ARCHITECTURAL CONSEQUENCE**: 
UNSAFE — LATTICE COORDINATES ARE NOT SUFFICIENT TO ESTABLISH OPTIMIZATION-STATE EQUIVALENCE. 
Sharing the exact same primary scalar inputs, geometry, objectives, and candidate set does NOT guarantee the identical Phase 4 requirement bounds. Reusing a lattice result based solely on these coordinates will serve scientifically dangerous cross-commodity recommendations.

## 9. Existing Addressability Mechanism
**ARCHITECTURAL CONSEQUENCE**: The existing architecture relies purely on the M6-B1 schema definition (`OptimizationInputEnvelope`), which defines the optimization inputs. It provides absolutely no caching layer lookup algorithms, surrogate models, context signature hashing, or multi-stage caching logic. 

## 10. Architectural Outcome
**ARCHITECTURAL CONSEQUENCE**: OUTCOME C — Existing architecture contains a contradiction that must be resolved before lattice design can continue. 
The system defines a strict optimization identity (Phase 4), but prohibits interval scalarization. Alternatively, using the safe primary scalar variables causes scientific collision. Introducing raw context fragments the cache. The architecture lacks a source-authorized mapping from request to cache address.

## 11. Required Future Decisions
**PROPOSED DECISION**: The architecture board must formally introduce a new caching resolution layer. Potential options remain OUT OF SCOPE but must decide whether to:
- Define interval hashing/serialization semantics for Phase 4 Envelopes.
- Introduce commodity-specific lattice namespaces.
- Create a two-stage cache hashing the Phase 3 resolved biological state.

## 12. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains fully BLOCKED. The project cannot proceed to lattice discretization, redis caching, or interval interpolation until a safe, unified Lattice Addressability mechanism is mathematically defined.
