# M6-A Tier-1 Addressability Resolution

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Tier-1 Architecture Source Basis
**EXISTING FACT**: The M6 optimization design envisions a progressive response-tier architecture where "Tier-1" serves as a precomputed cache lattice providing instantaneous (`<100ms`) Pareto front retrieval, avoiding heavy iterations. 
**UNRESOLVED**: The architecture documents do not explicitly stipulate whether this "instant lookup" must bypass the Phase 3/4 deterministic physics engine, or whether the `<100ms` window is expected to encompass a fast Phase 3/4 execution prior to querying the cache.

## 3. Identity Availability Timing
**EXISTING FACT**: The components of the frozen Optimization-State Identity become available strictly sequentially:

| Identity component | Available at request time? | Available after Phase 3? | Available after Phase 4? | Available after filtering? |
|---|---|---|---|---|
| Package Geometry | YES | YES | YES | YES |
| Active Objective Set | YES | YES | YES | YES |
| Phase 4 Requirement Envelope | NO | NO | **YES** | YES |
| Eligible Candidate ID Set | NO | NO | NO | **YES** |

## 4. Addressability Requirement
**EXISTING FACT**: The existing source does not explicitly mandate that a Tier-1 cache address MUST be mathematically computable purely from raw user inputs without intermediate processing. 
**ARCHITECTURAL CONSEQUENCE**: The architecture conceptually permits deterministic scientific resolution (Phase 3/4/5) BEFORE executing the cache lookup, provided the latency budget allows it.

## 5. Performance Target Classification
**EXISTING FACT**: The `<100ms Tier-1 lookup` is classified as a design target and an empirical UX benchmark rather than a hard constraint that mathematically overrides scientific correctness.

## 6. Scientific Equivalence Boundary
**EXISTING FACT**: The architecture definitively establishes scientific equivalence for optimization at the **Phase 4 Requirement Envelope** (the physical bounding box) and the resulting **Eligible Candidate ID Set** (the search space). Equivalence is NOT established at the raw input layer, nor at the Phase 3 property layer independently of Phase 4 targets.

## 7. Cached Result Correctness Condition
**SOURCE-AUTHORIZED REQUIREMENT**: A cached Pareto front can only be safely reused if and only if the incoming request evaluates to the exact same Phase 4 Requirement bounds (intervals, points, statuses), the exact same Package Geometry scaling, the exact same unordered Active Objective Set, and the exact same unordered Eligible Candidate ID Set as the cached state.

## 8. Three-Way Addressability Paradox
**ARCHITECTURAL CONSEQUENCE**: The current lattice design is trapped in a formal three-way paradox:
A. The Phase 4 Optimization Identity cannot currently be directly scalarized because it contains interval bounds.
B. The raw primary scalar inputs (temp, RH, geometry) are mathematically insufficient because they cause distinct biological commodities (e.g., Apple vs Strawberry) to dangerously collide in the cache.
C. Appending the raw food context (`commodity`) to the scalars fractures the cache entirely when Phase 3 legitimately falls back to a generic baseline, destroying the utility of Tier-1.

## 9. Architectural Classification
**ARCHITECTURAL CONSEQUENCE**: This three-way paradox constitutes a **contradiction between the Tier-1 caching architecture and the scientific identity boundaries**. The original assumption that a continuous precomputed multidimensional array (the "lattice") could seamlessly cache discrete biological interval-based requirements using simple input coordinates is fundamentally flawed under the current schema semantics.

## 10. Permitted Architectural Relationships
**EXISTING FACT**: WITHOUT designing a solution, the existing source material theoretically permits:
- **Lookup after Phase 4 / Phase 5 resolution**: If the system executes the deterministic engines to produce the envelope and candidate list, it possesses the complete mathematical identity needed to securely query a cache (assuming an authorized hashing mechanism for intervals/sets is eventually defined).

## 11. Required Future Decision
**PROPOSED DECISION**: The architecture board must formally choose how to exit the paradox. The resolution must either:
1. Define a rigorous mathematical hashing algorithm that serializes intervals and sets into a discrete string key (abandoning the geometric "lattice array" in favor of a flat Key-Value cache hit *after* Phase 4 execution).
2. Or invent a "Biological Surrogate Index" mapping commodities into continuous coordinates.
*(Both paths remain strictly OUT OF SCOPE for this document).*

## 12. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains fully BLOCKED. The architectural contradiction between safe scientific boundaries and lattice addressability has not been resolved. No numerical discretization can occur.
