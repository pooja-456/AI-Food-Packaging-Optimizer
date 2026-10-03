# M6-A Optimization Context Equivalence

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Active Objective Contract
**EXISTING FACT**: The M6-B1 `OptimizationInputEnvelope` defines `active_objectives: List[str]`. 
- **Identification**: By string name (e.g., `"f_thickness"`).
- **Direction**: Intrinsic to the `ObjectiveValue.direction` (MINIMIZE/MAXIMIZE), not the string identifier.
- **Empty Set**: Permitted by the schema, though logically results in all candidates being mutually non-dominating.

## 3. Objective Equivalence
**ARCHITECTURAL CONSEQUENCE**: Optimization problems are order-invariant and duplicate-invariant with respect to objectives. The Pareto dominance mathematical primitive evaluates simultaneous multi-dimensional thresholds. Therefore, `["f_thickness", "f_moisture_margin"]` is strictly equivalent to `["f_moisture_margin", "f_thickness"]`.
**PROPOSED DECISION**: `active_objectives` must be treated as an unordered mathematical set for equivalence purposes.

## 4. Package Geometry Contract
**EXISTING FACT**: `PackageGeometry` enforces three mandatory numerical fields:
- `surface_area_m2` (float > 0.0)
- `headspace_volume_cm3` (float >= 0.0)
- `product_mass_kg` (float > 0.0)
There are no optional fields. The schema does not support `None` or omitted fields within a valid `OptimizationInputEnvelope`. Units are intrinsic to the field names. Values are raw inputs, unrounded by the schema.

## 5. Geometry Equivalence
**EXISTING FACT**: Geometry fields natively impact the M6-B2B `CandidateScientificEvaluator` (e.g., recalculating package-level WVTR using `surface_area_m2`).
**ARCHITECTURAL CONSEQUENCE**: Two requests can only share an optimization state if their `PackageGeometry` fields are numerically identical. 
**PROPOSED DECISION**: Without a formally authorized numerical tolerance (e.g., epsilon rounding), equivalence currently requires strict floating-point equality. 

## 6. Missing / Partial Geometry
**EXISTING FACT**: Missing geometry is structurally impossible in the M6-B1 `OptimizationInputEnvelope`. While the downstream `CandidateScientificEvaluationRequest` permits an `Optional[PackageGeometry]`, the top-level optimization contract strictly enforces its presence. Two M6-B1 optimization requests therefore cannot exhibit "missing" geometry.

## 7. Scientific Requirements + Optimization Context
**ARCHITECTURAL CONSEQUENCE**: The conceptual identity of a specific optimization problem is defined by the union of:
1. `PackagingRequirementEnvelope` (the physical boundaries).
2. `PackageGeometry` (the scaling factors for mass/area-dependent objectives and candidate recalculations).
3. `active_objectives` (as an unordered set, defining the dimensional space of the Pareto front).
*Note*: The `eligible_candidate_materials` (search space) determines the actual output but is assumed to be the global canonical database for Tier 1 precomputation caching.

## 8. Counterexamples
- **Same requirements + different objectives**: Different optimization state. The Pareto front occupies a different dimensionality.
- **Same requirements + different geometry**: Different optimization state. The candidate scaling (e.g., absolute package moisture transfer) will diverge, altering objective values and feasibility.
- **Same requirements + same geometry + reordered objectives**: Same optimization state. Pareto dominance is order-invariant.

## 9. Minimum Safe Optimization Context
**ARCHITECTURAL CONSEQUENCE**: The minimum safe optimization context required to define cache identity encompasses:
1. The numeric bounds and statuses of the Phase 4 `PackagingRequirementEnvelope`.
2. The numeric values of `PackageGeometry`.
3. The set of `active_objectives`.

## 10. Architectural Finding
**PROPOSED DECISION**: To safely index the Tier 1 lattice, the architecture must expand its conceptual key from the simplistic `(commodity, target_days, temp, RH)` to a composite signature representing the Minimum Safe Optimization Context (Requirements + Geometry + Objective Set).

## 11. Required Future Contract Changes
**PROPOSED DECISION**: The M6-A documentation and M6-B5 schema must formally define the mathematical normalization/hashing of `PackageGeometry` floats and `active_objectives` sets into the canonical lattice coordinate.

## 12. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains BLOCKED. It is scientifically unsafe to proceed with optimization caching until the coordinate structure natively accounts for geometry scaling and objective selection.
