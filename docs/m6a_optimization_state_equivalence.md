# M6-A Optimization-State Equivalence

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Architectural Question
"If two requests produce scientifically equivalent Phase 4 packaging requirements, may they safely reuse the same precomputed optimization state / Pareto Front?"
This analysis determines whether the `PackagingRequirementEnvelope` is mathematically sufficient to define optimization-state equivalence.

## 3. Phase 4 Requirement Envelope Trace
**EXISTING FACT**: The `PackagingRequirementEnvelope` contains:
| Field | Meaning | Source | Used by Phase 5? | Used by optimization? | Uncertainty? |
|---|---|---|---|---|---|
| `commodity` | Target food | Request | NO | NO (context only) | NO |
| `target_shelf_life_days` | Target time | Request | YES | YES | NO |
| `storage_temperature_c` | Temperature | Request | YES | YES | NO |
| `relative_humidity_percent` | RH | Request | YES | YES | NO |
| `deterioration_profile` | Active spoilage modes | Phase 4 | YES | NO | NO |
| `gas_requirements` | O2/CO2 targets | Phase 4 | YES | YES | YES (via ScientificResult) |
| `moisture_requirements` | WVTR/aw targets | Phase 4 | YES | YES | YES (via ScientificResult) |
| `microbial_requirements` | Spoilage limits | Phase 4 | YES | YES | YES (via ScientificResult) |
| `shelf_life` | Limit status | Phase 4 | YES | YES | YES (via ScientificResult) |
| `overall_status` | Computation success | Phase 4 | YES | YES | NO |
| `temperature_effects` | Kinetic shifts | Phase 4 | NO | NO | NO |
| `all_assumptions` | Scientific context | Phase 4 | NO | NO | NO |
| `all_warnings` | Scientific trace | Phase 4 | NO | NO | NO |
| `traceability_log` | Provenance | Phase 4 | NO | NO | NO |

## 4. Phase 4 → Phase 5 Dependency
**EXISTING FACT**: Phase 5 (Hard Constraints) directly evaluates packaging candidates against the numerical targets and intervals defined in `gas_requirements`, `moisture_requirements`, and `microbial_requirements`. Without identical Phase 4 envelopes, Phase 5 feasibility outputs will diverge.

## 5. Phase 4 → Optimization Dependency
**EXISTING FACT**: M6-B4 (Pareto Front) filters candidates based on Phase 5 feasibility, and then computes Pareto dominance based on M6-B3 Objective values. The optimization output is entirely dependent on the requirements envelope and the active objectives. 

## 6. Hard-Constraint Dependency
**EXISTING FACT**: Every mathematically required threshold for constraint evaluation (required OTR, WVTR, etc.) is present in the Phase 4 requirement envelope via `ScientificResult`. If the envelope contains intervals (min/max), Phase 5 natively evaluates against those bounds.

## 7. Objective Dependency
**EXISTING FACT**: M6-B3 evaluates objectives (e.g., `thickness_minimization`, `gas_barrier_alignment`). The gas barrier alignment specifically calculates the distance/margin between the candidate's barrier properties and the targets defined in the Phase 4 `gas_requirements`. However, the M6-B1 `OptimizationInputEnvelope` additionally introduces `active_objectives` and `package_geometry` (if not already baked into normalized Phase 4 requirements). If two requests have the exact same Phase 4 envelope but differing `active_objectives`, their Pareto fronts will fundamentally differ.

## 8. Uncertainty Equivalence
**EXISTING FACT**: Identical point values with differing intervals (e.g., WVTR target 10 ± 1 vs 10 ± 5) dictate different constraint boundaries in Phase 5 and different objective intervals in M6-B3. They cannot share an optimization state.
**UNRESOLVED**: Whether identical numeric intervals with different epistemic statuses (e.g., KNOWN vs PREDICTED) can share a lattice entry. The architecture does not formally authorize grouping distinct evidence tiers if they carry identical numerical bounds.

## 9. UNKNOWN / INFEASIBLE Semantics
**EXISTING FACT**: If a Phase 4 requirement is `UNKNOWN`, the constraint evaluation yields `UNKNOWN`, excluding the candidate from the deterministic Pareto Front. Two envelopes that are strictly `UNKNOWN` for the exact same reasons produce identical empty/provisional optimization states. 

## 10. Condition / Multilayer Context
**EXISTING FACT**: Phase 5 constraint checking explicitly requires the test conditions (`storage_temperature_c`, `relative_humidity_percent`) from the Phase 4 envelope to match the candidate evidence conditions. This context is fully preserved within the `PackagingRequirementEnvelope`.

## 11. Counterexample Analysis
**Conceptual Counterexample**:
- Request A: Generates Envelope X. User selects active objectives: `[Minimize Thickness]`.
- Request B: Generates Envelope X. User selects active objectives: `[Minimize Thickness, Maximize Shelf Life]`.
**Result**: The resulting Pareto Fronts will be completely different because the optimization space dimensionality has changed.
**Conclusion**: The Phase 4 `PackagingRequirementEnvelope` alone is mathematically insufficient to guarantee optimization-state equivalence. 

## 12. Minimum Safe Optimization State
**ARCHITECTURAL CONSEQUENCE**: A minimum safe optimization state requires BOTH the complete `PackagingRequirementEnvelope` AND the contextual optimization parameters (`active_objectives`, and `package_geometry` if not pre-normalized into the envelope). 

## 13. Architectural Outcome
**PARTIALLY AUTHORIZED**: The Phase 4 envelope is necessary but insufficient to define optimization-state equivalence. Additional existing information (`active_objectives`, `package_geometry`) from the `OptimizationInputEnvelope` is strictly required.

## 14. Required Future Contract Changes
**PROPOSED DECISION**: The architecture must explicitly define "Optimization State Identity" as a composite of the Phase 4 requirement envelope parameters and the active optimization directives. 

## 15. Unresolved Questions
- How are epistemic statuses (`PREDICTED` vs `MEASURED`) handled if their numerical bounds are identical? (REQUIREMENT-LEVEL UNCERTAINTY EQUIVALENCE IS NOT AUTHORIZED).
- Does the lattice precompute all combinations of `active_objectives`, or only a default set?

## 16. M6-B5 Gating Consequence
**ARCHITECTURAL CONSEQUENCE**: M6-B5 remains BLOCKED. The precomputed lattice cannot be safely keyed or verified until the architecture board establishes the formal hashing/equivalence rule for this composite Optimization State.
