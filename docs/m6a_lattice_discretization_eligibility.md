# M6-A Lattice Discretization Eligibility

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Architectural Question
"Which components of the frozen Optimization-State Identity may legitimately participate in lattice discretization, before any numerical boundaries or resolutions are selected?"

## 3. Definition of Discretization
**EXISTING FACT**: At the architectural level, "lattice discretization" is the process of mapping an infinitely continuous or highly granular mathematical state space into a finite set of indexed, precomputable buckets (the Tier 1 cache coordinates).
- **Identity**: The pure mathematical definition of the problem.
- **Discrete/Continuous dimensions**: Numerical values bounded by physics.
- **Categorical dimensions**: Mutually exclusive strings (e.g., commodity).
- **Set-valued dimensions**: Unordered collections (e.g., objectives, candidate IDs).

## 4. Phase 4 Requirement Dimensions
**EXISTING FACT**: The `PackagingRequirementEnvelope` contains several classes of optimization-relevant fields:

| Field | Type | Continuous? | Interval? | Categorical? | Candidate for lattice discretization? | Reason |
|---|---|---|---|---|---|---|
| `commodity` | String | NO | NO | YES | YES | Categorical index. |
| `target_shelf_life_days` | Integer | YES | NO | NO | YES | Represents a continuous timeline. |
| `storage_temperature_c` | Float | YES | NO | NO | YES | Directly influences kinetic shift. |
| `relative_humidity_percent` | Float | YES | NO | NO | YES | Directly influences moisture flux. |
| OTR targets | ScientificResult | YES | YES | NO | YES | Governs Phase 5 gas feasibility. |
| WVTR targets | ScientificResult | YES | YES | NO | YES | Governs Phase 5 moisture feasibility. |
| CO2TR targets | ScientificResult | YES | YES | NO | YES | Governs Phase 5 gas feasibility. |
| Calculation statuses | Enum | NO | NO | YES | NO (State metadata) | Directly dictates validity; UNKNOWN bypasses optimization. |

## 5. Uncertainty / Interval Dimensions
**ARCHITECTURAL CONSEQUENCE**: A `ScientificResult` housing a Phase 4 requirement natively carries `[minimum_value, maximum_value]`. 
**UNRESOLVED — INTERVAL DISCRETIZATION SEMANTICS NOT AUTHORIZED**: The existing architecture explicitly relies on interval geometry to define Phase 5 hard constraints and M6-B4 Pareto dominance. It does NOT authorize collapsing an interval bounds array (e.g., `[10, 20]`) into a simple scalar coordinate, nor does it define how a lattice bin can simultaneously represent differing uncertainty spreads.

## 6. Package Geometry Dimensions
**EXISTING FACT**: `PackageGeometry` contains `surface_area_m2`, `headspace_volume_cm3`, and `product_mass_kg`. 
- **Classification**: All three are purely NUMERIC CONTINUOUS floating-point dimensions.
- **Eligibility**: Theoretically eligible for discretization.
- **UNRESOLVED**: The architecture does not yet authorize numerical bin sizes or scaling tolerances for geometric variables. Discretizing geometry without authorized error bounds could fundamentally alter scientific meaning by scaling candidate barrier properties (e.g., package WVTR) inaccurately.

## 7. Active Objective Dimension
**EXISTING FACT**: `active_objectives` is a collection of strings.
**ARCHITECTURAL CONSEQUENCE**: It is a SET-VALUED dimension. 
**PROPOSED DECISION**: Objectives should not be "discretized" (binned numerically), but rather represented directly as a categorical/set-valued namespace or dimension. It fundamentally alters the mathematical dimensionality of the optimization problem, meaning it governs the shape of the coordinate space rather than acting as a continuous axis within it.

## 8. Candidate Search-Space Dimension
**EXISTING FACT**: The resolved `eligible_candidate_materials` is an unordered collection of candidate IDs.
**ARCHITECTURAL CONSEQUENCE**: It is a SET-VALUED dimension.
**PROPOSED DECISION**: The candidate set represents the physical boundaries of the search space. It cannot be discretely "binned" along a numerical axis. It must select a lattice namespace (or be hashed into a discrete string coordinate) that segregates entirely different material universes. 

## 9. Complete Dimension Classification
**ARCHITECTURAL CONSEQUENCE**:
- **NUMERIC CONTINUOUS**: `storage_temperature_c`, `relative_humidity_percent`, `target_shelf_life_days`, `surface_area_m2`, `headspace_volume_cm3`, `product_mass_kg`.
- **NUMERIC INTERVAL**: Phase 4 targets (`required_otr_per_area`, `required_wvtr_per_area`, etc.).
- **CATEGORICAL**: `commodity`, `CalculationStatus`.
- **SET-VALUED**: `active_objectives`, `eligible_candidate_materials`.
- **METADATA (Not Eligible)**: Traceability, Epistemic origin flags, warnings.

## 10. Computational Discretization vs Scientific Equivalence
**SOURCE-AUTHORIZED REQUIREMENT**: Computational discretization creates a shared caching bucket; it does NOT establish scientific equivalence. Placing two distinct continuous inputs (e.g., 4.1°C and 4.9°C) into a single 5°C lattice bin purely accelerates retrieval. The architecture does not authorize treating those physical states as scientifically identical unless they genuinely share the exact same Phase 4 numerical requirements.

## 11. Continuous Input Preservation
**ARCHITECTURAL CONSEQUENCE**: The exact, unrounded, continuous inputs originally requested by the user and produced by Phase 4 models must be permanently retained in the optimization run trace. A computationally discretized lattice coordinate is exclusively a retrieval mechanism and must never permanently overwrite or destroy the physical precision of the candidate evaluation inputs.

## 12. Domain Coverage
**UNRESOLVED**: Any future numerical discretization of continuous or interval dimensions must establish strict domain boundaries (min/max acceptable values for the lattice). The existing architecture does not yet authorize Out-Of-Domain behavior or extrapolation boundaries for the lattice cache.

## 13. Authorized vs Unresolved Decisions
- **Authorized**: Categorical classification of the frozen identity components.
- **Authorized**: Separation of caching discretization from scientific equivalence.
- **Unresolved**: Interval binning rules, geometry numerical tolerances, and domain boundaries.

## 14. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains BLOCKED. Although the eligibility of identity components for discretization is now defined, the fatal lack of authorized numerical interval semantics means the lattice dimensions cannot yet be mathematically sized.
