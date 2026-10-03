# M6-A Interval Discretization Semantics

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Architectural Question
"What are the source-authorized semantics for representing interval-valued optimization requirements in a future precomputed lattice, given that collapsing interval geometry fundamentally alters Pareto dominance?"

## 3. Existing Interval Representation
**EXISTING FACT**: The optimization pipeline natively propagates intervals via:
- **Phase 4 (`ScientificResult`)**: `value`, `minimum_value`, `maximum_value`, `uncertainty_range`, `status`.
- **Phase 5 (`ConstraintEvaluation`)**: `required_value`, `required_range`, `comparison_operator`, `status`.
- **M6-B3/B4A (`ObjectiveValue`)**: `value`, `value_min`, `value_max`, `is_interval`, `direction`, `status`.

## 4. Point vs Degenerate Interval
**EXISTING FACT**: A scalar point (`value = X, value_min = NULL, value_max = NULL`) is mathematically indistinguishable from a degenerate interval (`value = NULL, value_min = X, value_max = X`) within the M6-B4A `dominates()` logic, which cleanly falls back (`wc_a = obj_a.value_max if obj_a.is_interval else obj_a.value`). 

## 5. Non-Degenerate Interval Semantics
**ARCHITECTURAL CONSEQUENCE**: A true interval (`value_min < value_max`) physically dictates the worst-case and best-case performance vectors during M6-B4A Pareto dominance evaluation. Collapsing this interval span into a single scalar fundamentally destroys the multi-objective overlap geometry, directly altering which candidates dominate each other.

## 6. Phase 5 Consumption
**EXISTING FACT**: Phase 5 (`ConstraintEvaluation`) natively consumes the exact `required_range` boundary alongside an explicit `comparison_operator` (`LE`, `GE`, `IN_RANGE`) to output deterministic boolean feasibility (`ConstraintStatus`).

## 7. Objective / Pareto Consumption
**EXISTING FACT**: M6-B4A dynamically extracts the worst-case interval bound (dependent on the `ObjectiveDirection`) for Candidate A and tests it strictly against the best-case interval bound for Candidate B. The interval width is mathematically required for safe conservative decision-making.

## 8. Interval-to-Scalar Analysis
**UNRESOLVED**: INTERVAL-TO-SCALAR COLLAPSE NOT AUTHORIZED. The existing architecture contains zero authorization to mathematically reduce an interval bound into a representative midpoint (`(min + max) / 2`) or any other compressed scalar for lattice optimization. 

## 9. Possible Lattice Representations
**ARCHITECTURAL CONSEQUENCE**: Because interval geometry cannot be collapsed without violating optimization safety, the lattice coordinate representing an interval must natively accommodate two degrees of freedom (e.g., lower-bound coordinate + upper-bound coordinate).
**UNRESOLVED**: The specific structural format of an interval lattice coordinate (e.g., binning the min and max independently) is not defined by existing schemas.

## 10. Constraint Direction
**EXISTING FACT**: The mathematical `ComparisonOperator` (`<=`, `>=`, `in_range`) fundamentally dictates whether an interval represents an upper maximum bound, a lower minimum bound, or a targeted window. 
**ARCHITECTURAL CONSEQUENCE**: The direction/operator is an absolute, immutable part of the interval's mathematical identity.

## 11. UNKNOWN Semantics
**EXISTING FACT**: An `UNKNOWN` calculation status explicitly short-circuits Phase 5 to `UNKNOWN` and M6-B4A Pareto dominance to `False`. 
**UNRESOLVED**: UNKNOWN LATTICE REPRESENTATION NOT AUTHORIZED. The architecture does not define a formal caching sentinel or namespace bin for `UNKNOWN` states, though mathematically they represent valid, distinct optimization states (which resolve to empty Pareto fronts).

## 12. Uncertainty vs Requirement Intervals
**EXISTING FACT**: A scientific uncertainty interval (e.g., "we estimate point X lies between [A, B]") defines an epistemic boundary. A requirement interval (e.g., "packaging must maintain gas between [A, B]") defines a physical target. While the pipeline schemas (`ScientificResult`) reuse fields for both, Phase 5 consumes them universally as strict numerical target boundaries (`required_range`).

## 13. Computational Binning vs Scientific Equivalence
**SOURCE-AUTHORIZED REQUIREMENT**: Any future computational binning of intervals (e.g., grouping `[10.1, 19.9]` and `[10.0, 20.0]` into a `[10, 20]` coordinate) creates retrieval efficiency. It explicitly does NOT establish scientific equivalence. The optimization engine relies on the raw precision of the underlying continuous inputs.

## 14. Continuous Input Preservation
**SOURCE-AUTHORIZED REQUIREMENT**: The original, unrounded continuous requirements (`value`, `minimum_value`, `maximum_value`, `comparison_operator`, `CalculationStatus`) must remain structurally preserved and attached to the runtime context. The computational lattice bucket must never overwrite the original scientific inputs.

## 15. Architectural Outcome
**ARCHITECTURAL CONSEQUENCE**: OUTCOME C — Existing architecture does not provide enough information to safely represent intervals in a lattice. While the optimization logic perfectly natively consumes interval boundaries, the architectural definition for how to physically cache, stringify, hash, or discretize a multi-dimensional interval geometry into a Tier 1 lattice node is completely missing.

## 16. Required Future Contract Changes
**PROPOSED DECISION**: The M6-A documentation must be amended to formally establish the rules for Interval Lattice Coordinates (e.g., hashing the `[min_coordinate, max_coordinate, operator]`), completely prohibiting unauthorized interval-to-scalar collapse.

## 17. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains fully BLOCKED. The Tier 1 lattice cannot be safely instantiated without an authorized geometric rule mapping numerical Phase 4 requirement intervals into discrete coordinate representations.
