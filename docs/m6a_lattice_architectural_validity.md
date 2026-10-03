# M6-A Lattice Architectural Validity

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Terminology Trace
**EXISTING FACT**: The M6-A architectural documents use terms like "Optimization Lattice", "Tier-1 Lattice Lookup", and "Lattice Cache". 
- These terms consistently describe an abstraction for offline precomputation, coverage of the state space, and fast retrieval. 
- The M6-B5 scope mentions components like "nearest-neighbor runtime," which implies an assumed geometric proximity structure.
- However, the foundational M6-A definitions prioritize the *function* (precomputed optimization states) over the rigid mathematical array structure.

## 3. Source-Authorized Lattice Purpose
**EXISTING FACT**: The source-authorized purpose of the "lattice" is to serve as a repository of **precomputed optimization states** to enable instant (Tier-1) retrieval and rapid (Tier-2) initialization without executing heavy, iterative Pareto optimization at runtime.

## 4. Geometric Lattice Requirement
**EXISTING FACT**: While earlier design phases and M6-B5 implementations assumed a coordinate-based array, NO SOURCE-AUTHORIZED REQUIREMENT FOR A SCALAR GEOMETRIC LATTICE FOUND. The foundational M6-A specification strictly mandates the preservation of scientific constraint boundaries (the optimization identity), but never explicitly binds the architecture to a rigid scalar multidimensional grid representation.

## 5. Frozen Optimization Identity Compatibility
**ARCHITECTURAL CONSEQUENCE**: The mathematical term "lattice" (in the sense of a continuous numeric array) is structurally incompatible with the frozen optimization identity. An N-dimensional continuous scalar grid cannot natively accommodate the un-collapsible interval limits, the unordered string sets (active objectives), or the unordered UUID sets (eligible candidates) that form the strict boundaries of the optimization problem, without inventing entirely new, unauthorized representation mechanics.

## 6. Precomputation vs Representation
**ARCHITECTURAL CONSEQUENCE**: The architecture explicitly requires the **precomputation** and caching of the optimization states. It does not strictly dictate the **representation** of that cache as a continuous numerical grid. 

## 7. Tier-1 Requirement
**EXISTING FACT**: Tier-1 fundamentally requires a **fast reusable precomputed optimization state**. The use of the word "lattice" is an architectural metaphor for the state space coverage, not a strict mandate for an array-based data structure.

## 8. Warm-Start Requirement
**EXISTING FACT**: The M6-B5 scope references a "nearest-neighbor runtime" for Tier 2 warm starts.
**UNRESOLVED**: If the architecture Abandons the geometric grid for Tier-1 (due to interval and set incompatibility), calculating the "nearest neighbor" for a cache miss becomes mathematically undefined. The architecture does not yet specify how to calculate Euclidean distance between two Phase 4 Requirement Envelopes (which contain overlapping intervals and different calculation statuses) or between different unordered candidate sets. 

## 9. Miss / Fallback Semantics
**EXISTING FACT**: When a precomputed state cannot be safely reused (a cache miss), the architecture requires fallback to Tier 2 (Warm Start) or Tier 3 (Deep Optimization) to iteratively calculate the Pareto front at runtime. 

## 10. Architectural Classification
**ARCHITECTURAL CONSEQUENCE**: OUTCOME B — Precomputed optimization-state retrieval is source-required, but a scalar geometric lattice is NOT explicitly source-required. The foundational requirement is caching and reuse, which the geometric lattice assumption has proven incapable of supporting safely.

## 11. Future Representation Decisions
**PROPOSED DECISION**: The architecture board must formally replace the "scalar lattice array" assumption with a representation mechanism capable of natively handling sets and intervals.
*Note: Explicitly OUT OF SCOPE for this decision are the selections of hashing algorithms, KV stores, Redis implementation, serialization formats, or the re-design of the nearest-neighbor warm-start distance metric.*

## 12. M6-B5 Consequence
**EXISTING FACT**: M6-B5 remains strictly BLOCKED. The conceptual "Optimization Lattice" contract cannot be designed until the physical representation paradigm (hash vs. grid) and the warm-start distance metric are formally resolved by the architecture board.
