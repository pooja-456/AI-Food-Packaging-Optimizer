# M6-A CONTRACT AMENDMENT — LATTICE DISCRETIZATION SPECIFICATION

## 1. Amendment Purpose
This document amends the M6-A optimization architecture to formally specify the computational discretization (binning) logic required to project continuous continuous runtime requests onto the Tier 1 Precomputed Lattice.

## 2. Existing M6-A Authorization
M6-A currently authorizes the following dimensions for the Precomputed Lattice: `(commodity, target_days, temp, RH)`.

## 3. Identified Contract Gap
M6-A previously authorized conceptual dimensions but completely omitted the physical binning mathematics, sizes, and boundary rules for these variables, leading to unauthorized implicit discretization (e.g., arbitrary rounding and integer casting) in the M6-B5 schema design.

## 4. Formal Discretization Contract
The following rules formally map the physical dimensions into the discrete precomputed optimization index.

### Dimension-by-Dimension Specification & 15. Unresolved Decisions

| Dimension | Source Unit | Discretization | Resolution | Min | Max | Boundary Rule | Out-of-Domain | Original Value Preserved |
|-----------|-------------|----------------|------------|-----|-----|---------------|----------------|--------------------------|
| **Commodity** | String (Name) | Exact Match (Case-Insensitive String normalization) | N/A | N/A | N/A | Exact match | Unsupported | Yes |
| **Target Shelf Life** | Days (Integer) | **UNRESOLVED — REQUIRES ARCHITECTURAL DECISION** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | Yes |
| **Storage Temperature** | °C (Float) | **UNRESOLVED — REQUIRES ARCHITECTURAL DECISION** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | Yes |
| **Relative Humidity** | % (Float) | **UNRESOLVED — REQUIRES ARCHITECTURAL DECISION** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | **UNRESOLVED** | Yes |

## 5. Bin Semantics
A lattice coordinate represents an indexing computational bin, acting as a lookup key for a precomputed Pareto set. It represents a strict computational interval grouping, not a mathematical point.

## 6. Boundary Mathematics
**UNRESOLVED — REQUIRES ARCHITECTURAL DECISION**. (Requires physical bin resolutions and exact clamping boundaries).

## 7. Out-of-Domain Behavior
**UNRESOLVED — REQUIRES ARCHITECTURAL DECISION**. (Rules for inputs outside the supported physical bounding boxes).

## 8. Original-Input Preservation
The runtime lookup request MUST retain the `original_target_shelf_life_days`, `original_storage_temperature_c`, and `original_relative_humidity_percent` unmodified on the resulting object, separately from the canonical lattice coordinate.

## 9. Canonical Identity/Key Contract
The canonical key is defined as a deterministic cryptographic hash (SHA-256) over the string-serialized payload of the normalized commodity and the discretized values of target days, temperature, and RH. Field ordering is strictly sorted (alphabetical). 

## 10. Versioning
Any change to bin widths, domain boundaries, boundary convention math, or canonicalization protocols forces a full version invalidation of the lattice data structures.

## 11. No-Interpolation Rule
A lattice lookup MUST NOT mathematically interpolate physical properties between lattice points unless a future specification explicitly authorizes and tests such behavior. A MISS remains a MISS.

## 12. Scientific Limitation
The discretization is a computational indexing/lookup mechanism. It does not establish that all continuous physical states within a bin are scientifically equivalent. Any scientific validity of a lattice result must come from the underlying scientific evaluation and evidence, not from the binning operation itself.

## 13. Decision Authority / Traceability
- **Commodity Normalization**: Authorized by engineering standard practice (case-insensitive string matching).
- **Physical Bin Widths/Resolutions**: **UNRESOLVED**. Cannot be synthetically assumed.

## 14. Future M6-B5 Verification Cases
1. Exact minimum boundary
2. Exact maximum boundary
3. Just below minimum
4. Just above maximum
5. Exact bin boundary
6. Just below boundary
7. Just above boundary
8. Midpoint/tie case if nearest-neighbor discretization is authorized
9. Floating-point representation case
10. Missing value
11. Invalid value
12. Non-finite value
13. Unsupported commodity
14. Commodity canonicalization
15. Deterministic canonical serialization
16. Version change identity
17. Original continuous value preservation
18. No interpolation on MISS
19. Same normalized input → same coordinate
20. Different authorized coordinates → different lattice identity

## 15. Regression Compatibility
This amendment imposes strict new design limitations but does not physically modify Phase 4 models, Phase 5 constraints, or M6-B1/B2/B3/B4 contracts.

## 16. Amendment Status
**M6-A AMENDMENT BLOCKED — UNRESOLVED CONTRACT DECISIONS**
