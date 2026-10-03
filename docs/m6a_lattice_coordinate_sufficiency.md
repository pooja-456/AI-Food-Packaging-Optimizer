# M6-A Lattice Coordinate Sufficiency

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Architectural Question
"Are the six authorized primary scalar dimensions sufficient to uniquely determine the optimization-relevant Phase 4 state under the existing architecture?"

## 3. Six Authorized Scalar Dimensions
**EXISTING FACT**: The authorized numerical scalar dimensions for lattice discretization are:
1. `storage_temperature_c`
2. `relative_humidity_percent`
3. `target_shelf_life_days`
4. `surface_area_m2`
5. `headspace_volume_cm3`
6. `product_mass_kg`

## 4. Dependency Trace
**EXISTING FACT**: These six scalars map directly from User Input into Phase 4 (kinetics, moisture bounds), Phase 5 (environmental condition checks), and M6-B2B candidate recalculations (scaling per unit area/mass). 

## 5. Upstream Scientific Dependencies
**EXISTING FACT**: The Phase 4 Requirement Envelope is heavily dependent on Phase 3 output properties (e.g., respiration rate, initial water activity, microbial parameters), which in turn depend entirely on the raw biological food context (`commodity`, `variety`, `product_form`, `ripeness_stage`). 
**ARCHITECTURAL CONSEQUENCE**: The six scalar dimensions only supply the environmental and geometric parameters. They are physically blind to the biological properties of the food being packaged.

## 6. Counterexamples
**Conceptual Counterexample**:
- Request A: 5°C, 85% RH, 14 days shelf life, 0.1m² area, 500cm³ headspace, 1kg mass. Commodity = Apple.
- Request B: 5°C, 85% RH, 14 days shelf life, 0.1m² area, 500cm³ headspace, 1kg mass. Commodity = Strawberry.
**Result**: The six authorized scalar dimensions are strictly identical. However, the biological respiration rates, moisture contents, and spoilage mechanisms of an apple vs. a strawberry are fundamentally distinct. The resulting Phase 4 `PackagingRequirementEnvelope` (specifically the required OTR, CO2TR, and WVTR intervals) will be entirely different. 
**ARCHITECTURAL CONSEQUENCE**: The six scalars are completely insufficient to guarantee a unique Phase 4 optimization state. 

## 7. Phase 4 State Determinacy
**EXISTING FACT**: Two requests with identical six primary scalar values but different Phase 3 resolved scientific states (e.g., respiration rates) produce different Phase 4 requirements.
**ARCHITECTURAL CONSEQUENCE**: The Phase 4 state is non-deterministic with respect to the six scalar dimensions alone.

## 8. Optimization Identity Test
**ARCHITECTURAL CONSEQUENCE**: 
OUTCOME B — NO. Additional existing optimization-relevant state is mathematically required. The frozen identity demands the Phase 4 Requirement Envelope, which depends on biological traits that the six scalars omit.

## 9. Lattice Coordinate vs Optimization Identity
**EXISTING FACT**: An optimization identity represents the mathematical boundaries defining the Pareto optimization problem. A lattice coordinate represents the retrieval key for a precomputed cache. 
**ARCHITECTURAL CONSEQUENCE**: While the six scalars are conceptually valid lattice coordinates, using them alone as the *complete* coordinate signature catastrophically detaches the lattice from the actual optimization identity it is attempting to cache.

## 10. Raw Food Context Paradox
**ARCHITECTURAL CONSEQUENCE**: 
OUTCOME C — The existing architecture does not yet define how the lattice reaches the frozen Phase 4 identity. 
- M6-A Decision #1 excluded raw food context from the identity because the Phase 4 Envelope mathematically resolves it (avoiding fragmentation on identical fallbacks).
- M6-A Decision #2 excluded Phase 4 Envelopes from lattice dimensions because they contain interval geometries that cannot be collapsed to scalars.
- Using only the remaining primary scalars removes biological identity, causing different foods to collide in the cache. The architecture is mathematically gridlocked.

## 11. Safe Lattice Reuse Test
**EXISTING FACT**: Conceptually testing identical six scalars + identical objectives + identical geometry + identical candidate sets, but **different** Phase 4 requirement envelopes (e.g., Apple vs Strawberry).
**ARCHITECTURAL CONSEQUENCE**: Reuse is scientifically UNSAFE. Retrieving a precomputed Pareto front calculated against an Apple's physical requirements and presenting it as the solution for a Strawberry fundamentally violates the M6-B1 and Phase 5 constraint contracts. 

## 12. Architectural Outcome
**PROPOSED DECISION**: The six authorized scalar dimensions are absolutely INSUFFICIENT to define a safe Tier 1 lattice coordinate. Attempting to build the lattice strictly from these parameters will generate scientifically invalid, cross-commodity packaging recommendations.

## 13. Unresolved Design Questions
- How does the architecture reconcile the necessity of caching biological constraints (Phase 4) with the prohibition against scalarizing interval bounds?
- Must the lattice coordinate expand to include the raw `commodity` string (sacrificing cross-commodity biological unification) or introduce an intermediate hashing of the Phase 3 property profile?

## 14. M6-B5 Gating Consequence
**EXISTING FACT**: M6-B5 remains strictly BLOCKED. The architectural contradiction preventing the formulation of a safe, sufficient lattice coordinate signature remains formally unresolved. Discretization boundaries and Redis caching mechanics cannot proceed.
