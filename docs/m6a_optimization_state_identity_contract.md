# M6-A Optimization-State Identity Contract

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Purpose
This document consolidates the findings from architectural decisions #1A through #1E to establish the definitive, conceptual **Optimization-State Identity**. It formally bounds what constitutes mathematically identical optimization problems within the M6-A architecture, gating the subsequent M6-B5 lattice discretization.

## 3. Source Documents
- `docs/m6a_resolved_scientific_state_identity.md` (Decision #1A)
- `docs/m6a_optimization_state_equivalence.md` (Decision #1B)
- `docs/m6a_epistemic_equivalence.md` (Decision #1C)
- `docs/m6a_optimization_context_equivalence.md` (Decision #1D)
- `docs/m6a_candidate_search_space_equivalence.md` (Decision #1E)
- M6-B1 optimization contracts
- Phase 4 requirement specification
- Phase 5 hard-constraint specification
- M6-B4A Pareto dominance rules

## 4. Previously Resolved Decisions
- **Raw commodity-only identity is unsafe**: Collapses distinct scientific evidence.
- **Raw full food-context identity is too strict**: Fragments the cache prematurely when inference fallback converges to identical scientific states.
- **Epistemic origin is pure traceability**: Measured vs. predicted bounds are mathematically identical to the optimizer if their numerical values and calculation statuses match.
- **Optimization Context is mandatory**: The `PackageGeometry` and `active_objectives` inherently change the mathematical outcome.
- **Search Space is mandatory**: The exact population of evaluated candidates (`eligible_candidate_materials`) drives the exact shape of the Pareto front.

## 5. Complete Optimization-State Identity
The minimum safe conceptual identity that uniquely defines an optimization problem in M6-A is the union of:
1. **Phase 4 Requirement Envelope**
2. **Package Geometry**
3. **Active Objective Set**
4. **Resolved Eligible Candidate ID Set**

## 6. Food Context Boundary
The architecture explicitly distinguishes between **Raw User Context** (commodity, variety, product_form, ripeness_stage) and the **Resolved Scientific/Phase 4 Requirements**. The raw food context acts exclusively as an inference trigger. Once the scientific inference is resolved, the mathematical bounds embedded in the Phase 4 Requirement Envelope fully capture the physical reality. Therefore, raw food context is strictly excluded from the optimization identity. Including it would artificially break cache reuse for differing raw contexts that correctly yield identical packaging constraints.

## 7. Phase 4 Requirement Identity
The numerical targets, intervals (`value`, `minimum_value`, `maximum_value`), and explicit `CalculationStatus` embedded within the `PackagingRequirementEnvelope` dictate the boundaries for Phase 5 hard constraints and M6-B3 objectives. Two requests presenting mathematically identical Phase 4 parameters share an identical baseline constraint identity.

## 8. Epistemic Equivalence
Different epistemic origins (measured, inferred, literature, predicted) represent the identical optimization state when their resulting mathematical bounds and `CalculationStatus` are equal. Epistemic data (`PropertyStatusEnum`, `EvidenceTier`) is pure traceability metadata and must not be encoded into the mathematical optimization identity.

## 9. Package Geometry Identity
`PackageGeometry` contains mandatory numerical fields (`surface_area_m2`, `headspace_volume_cm3`, `product_mass_kg`) that geometrically scale candidate properties (e.g., package-level WVTR) during M6-B2B evaluation. Altering geometry natively alters candidate Phase 5 feasibility and M6-B3 objectives. It is an absolute requirement for optimization identity.

## 10. Active Objective Identity
The `active_objectives` list defines the dimensional space of the M6-B4 Pareto filter. Because Pareto dominance is fundamentally order-invariant, the objectives behave conceptually as an unordered mathematical set. Altering, omitting, or adding active objectives fundamentally redefines the optimization problem space. 

## 11. Candidate Search-Space Identity
The exact optimization population (`eligible_candidate_materials`) drives the Pareto frontier. The identity is governed by the *Resolved Eligible Candidate ID Set*—an unordered mathematical set of deterministic Candidate IDs. The search-space identity is distinctly separate from the *user filtering criteria* (e.g., "biodegradable"); two differing sets of filtering rules that resolve to the exact same list of candidate IDs represent the exact same mathematical search space.

## 12. Empty / UNKNOWN States
- **Empty Search Space**: If the resolved candidate set is empty, it represents a mathematically valid optimization problem whose result is an empty Pareto front.
- **UNKNOWN States**: If a specific requirement evaluates to `UNKNOWN`, both Phase 5 and M6-B4 explicitly short-circuit. Two requests sharing identically `UNKNOWN` constraints correctly share an identical provisional/indeterminate state.

## 13. Identity vs Representation
**IDENTITY** answers: "What makes two optimization problems mathematically the same?" This document strictly defines the conceptual identity.
**REPRESENTATION** answers: "How will that identity eventually be serialized, hashed, discretized, cached, or indexed?" This remains strictly out of scope and requires subsequent architectural resolution (e.g., M6-A lattice discretization).

## 14. Identity Inclusion / Exclusion Table

| Dimension | Identity? | Existing Source | Reason |
|-----------|-----------|-----------------|--------|
| Phase 4 requirements | **YES** | M6-B1, Phase 5 | Dictates all mathematical constraint boundaries. |
| Package geometry | **YES** | M6-B2B | Scales candidate barrier properties physically. |
| Active objectives | **YES** | M6-B3, M6-B4A | Defines the dimensionality of Pareto dominance. |
| Eligible candidate ID set | **YES** | M6-B4B | Defines the discrete search space boundary. |
| Raw food context | **NO** | Phase 4 | Fully abstracted by the mathematical requirements. |
| Filtering criteria | **NO** | M6-B1 | Triggers search space but does not define it. |
| Epistemic origin | **NO** | Phase 4/5, M6-B4A | Only numerical bounds affect the optimizer. |
| Provenance | **NO** | M6-B4B | Pure audit trail metadata. |
| Inference trace | **NO** | Phase 3/4 | Pure computational logging metadata. |

## 15. Architectural Freeze
**M6-A OPTIMIZATION-STATE IDENTITY FROZEN**
The existing architecture contains sufficient source-authorized information to formally define the conceptual bounds of the optimization problem.

## 16. Explicit Non-Decisions
This document strictly defines conceptual identity. The following dimensions remain explicitly undecided and OUT OF SCOPE:
- Hashing algorithms
- Serialization formats
- Floating-point normalization
- Numerical tolerance rules
- Lattice bin sizes / discretization rules
- Lattice domain boundaries
- Interpolation behavior
- Cache implementation specifics (Redis)
- TTL / Cache invalidation

## 17. M6-B5 Consequence
The M6-B5 lattice optimization contract remains physically BLOCKED pending the formal definition of the representation logic (lattice discretization) that will encode this frozen identity.
