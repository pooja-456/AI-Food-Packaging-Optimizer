# M6-A Tier-1 Addressability Contract

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Purpose
This document formally defines the architectural requirements for safely addressing and retrieving an exact, precomputed optimization state (Tier-1). It specifies *what* guarantees the address representation must provide to preserve scientific validity, without designing the implementation (e.g., hashes, serialization).

## 3. Exact Reuse Definition
**SOURCE-AUTHORIZED REQUIREMENT**: Two independent optimization requests may mathematically reuse the same precomputed Tier-1 Pareto front if and only if their frozen Optimization-State Identities are absolutely equivalent. 

## 4. Frozen Optimization Identity
**EXISTING FACT**: The complete identity comprises:
1. Phase 4 Requirement Envelope
2. Package Geometry
3. Active Objective Set
4. Resolved Eligible Candidate ID Set

## 5. Address Correctness Properties
**SOURCE-AUTHORIZED REQUIREMENT**: Any future physical representation of the Tier-1 address must mathematically guarantee:
- **Determinism**: The same Optimization-State Identity must always map to the identical address.
- **Collision Safety**: Two mathematically distinct Optimization-State Identities MUST NOT ever resolve to the same address.
- **Completeness**: Every mathematically valid Optimization-State Identity must be representable.
- **Stability**: The address representation must remain structurally immune to variations in non-identity metadata.
- **Order Invariance**: The address must guarantee semantic equivalence regardless of the chronological list ordering of active objectives or candidate IDs.
- **Interval Preservation**: The mathematical boundaries of intervals must remain structurally distinguishable.
- **UNKNOWN Preservation**: An `UNKNOWN` calculation status must never silently default to a numerical representation or null zero.

## 6. Requirement Envelope Representation Semantics
**SOURCE-AUTHORIZED REQUIREMENT**: The representation must strictly preserve the distinction between:
- A point (`value`)
- A physical bounding interval (`minimum_value`, `maximum_value`)
- An indeterminate state (`UNKNOWN`)
- The applied directional constraint (`comparison_operator` where applicable in Phase 5).

## 7. Package Geometry Semantics
**SOURCE-AUTHORIZED REQUIREMENT**: The representation must natively capture the scalar inputs for `surface_area_m2`, `headspace_volume_cm3`, and `product_mass_kg`.

## 8. Active Objective Set Semantics
**SOURCE-AUTHORIZED REQUIREMENT**: The Active Objective Set is an unordered mathematical set. The address must treat `[cost, shelf_life]` and `[shelf_life, cost]` as the exact same identical constraint space.

## 9. Candidate ID Set Semantics
**SOURCE-AUTHORIZED REQUIREMENT**: The Eligible Candidate ID Set defines the discrete, unordered population of the search space. The address must guarantee mathematical equivalence irrespective of the order in which the M6-B1 filtering logic emitted the UUIDs.

## 10. Excluded Metadata
**SOURCE-AUTHORIZED REQUIREMENT**: The address representation MUST NOT embed or alter its identity based on:
- Raw user biological context (`commodity`, `variety`, `product_form`, `ripeness_stage`)
- User filtering rationale (e.g., "biodegradable")
- Epistemic origin or Evidence Tier (e.g., measured vs. predicted)
- Inference traces or calculation provenance logs

## 11. Exact HIT Semantics
**SOURCE-AUTHORIZED REQUIREMENT**: A Tier-1 HIT means the precomputed state corresponds exactly to the requested Optimization-State Identity. It MUST NOT ever be interpreted as "approximately similar," "sharing the same scalar inputs," "same commodity," "geometry within tolerance," or "overlapping candidate subsets." 

## 12. MISS Semantics
**EXISTING FACT**: A Tier-1 MISS means an exact optimization-state identity match was not found in the precomputed cache. The system must immediately fall back to Tier-2 (Warm-Start) or Tier-3 (Cold Optimization). A MISS cannot be silently treated as an approximate match.

## 13. Version / State Validity
**UNRESOLVED**: VERSION IDENTITY SEMANTICS NOT YET AUTHORIZED. While schemas contain fields like `constraint_policy_version` or `solver_configuration`, the architecture has not yet formally established whether a global algorithm version or scientific model version must be cryptographically hashed into the optimization-state identity to safely expire obsolete caches.

## 14. Identity vs Physical Representation
**ARCHITECTURAL CONSEQUENCE**: The **Identity Contract** defines what physical bounds and sets make two optimization problems distinct. The **Representation Contract** defines how those bounds are physically serialized, hashed, or encoded for storage. This document finalizes the Identity Contract properties.

## 15. Implementation Decisions Explicitly Deferred
The following physical mechanisms remain fully OUT OF SCOPE and are explicitly deferred:
- Hash algorithms (e.g., SHA-256)
- Serialization formats (e.g., JSON, Protocol Buffers)
- Canonical ordering implementations (e.g., sorting algorithms for arrays)
- Floating-point normalization or epsilon tolerance
- Interval serialization encoding
- Unordered set encoding
- Storage engine selection (Redis, DB)
- Cache Time-To-Live (TTL)
- Cache invalidation and eviction logic
- Payload compression

## 16. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains strictly BLOCKED. Although the Tier-1 Addressability *Contract* is now established, the system still fundamentally lacks the mathematical *Implementation* (the Representation Contract) that dictates exactly how the system will safely execute canonical serialization and hashing for floating-point boundaries, intervals, and unordered sets.
