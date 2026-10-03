# M6-A Resolved Scientific State Identity

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Problem Definition
The forensic review established that indexing the optimization lattice by "Raw Food Context" (e.g., commodity + variety) is too strict and artificially fragments caching, while indexing by "Commodity Only" is scientifically unsafe (collapses distinct evidence). A "Resolved Scientific State Identity" is required to deterministically group requests that produce identical scientific requirements, without improperly grouping distinct biological states. We must formally define what constitutes a minimum safe identity.

## 3. Phase 3 Resolved-State Output
Based on `PropertyInferenceProfile` and `InferredProperty`:

| Resolved field | Source | Scientific meaning | Can affect Phase 4? | Can affect Phase 5? | Uncertainty represented? |
|---|---|---|---|---|---|
| properties.value | `InferredProperty` | Point estimate of biological trait | YES | YES | NO |
| properties.unit | `InferredProperty` | Unit of measurement | YES | YES | NO |
| properties.uncertainty_range | `InferredProperty` | Lower/upper bounds | YES | YES | YES |
| properties.status | `InferredProperty` | Epistemic status | YES | YES | YES |
| resolution_level | `InferredProperty` | Evidence match depth | NO | NO | NO |
| confidence | `InferredProperty` | Score of evidence strength | NO | NO | NO |
| supporting_evidence | `InferredProperty` | Literature/DB records | NO | NO | NO |
| citations | `InferredProperty` | DOIs/Titles | NO | NO | NO |
| warnings | `InferredProperty` | Contextual caveats | NO | NO | NO |

## 4. Scientific-State Fields
**EXISTING FACT**: The scientific-state fields that physically drive the Phase 4 optimization calculations are `properties.value`, `properties.unit`, `properties.uncertainty_range`, and `properties.status` for every inferred property (e.g., respiration rate, pH, moisture content). 

## 5. Minimum Safe Identity
**ARCHITECTURAL CONSEQUENCE**: To safely cache optimization results without false scientific equivalency, the minimum safe identity must mathematically encompass the inputs that dictate the optimization outcome. This requires capturing the collection of inferred properties (`value`, `unit`, `uncertainty_range`, `status`) combined with the optimization targets (`commodity`, `target_shelf_life_days`, `storage_temperature_c`, `relative_humidity_percent`).

## 6. User Input vs Scientific State
**EXISTING FACT**: User inputs like `variety`, `product_form`, and `ripeness_stage` are inference triggers. They are NOT the resolved scientific state. Two different varieties that resolve to the exact same respiration and moisture parameters share an identical scientific state, despite differing user inputs.

## 7. Scientific State vs Provenance
**EXISTING FACT**: Fields like `supporting_evidence`, `citations`, and `acquisition_method` are provenance. Two states with identical biological parameters but sourced from different literature citations are scientifically identical with respect to Phase 4 packaging requirements. Provenance must not fragment the cache identity.

## 8. Scientific State vs Inference Trace
**EXISTING FACT**: Fields like `resolution_level` and `warnings` describe the inference process (trace), not the biological reality (state). They do not alter the Phase 4 equations and must not fragment the cache identity.

## 9. Uncertainty Semantics
**EXISTING FACT**: `status` and `uncertainty_range` explicitly define epistemic boundaries. States with identical point values but differing uncertainty bounds (e.g., `[5, 10]` vs `[5, 15]`) produce different Pareto dominance intervals. 
**UNRESOLVED — UNCERTAINTY EQUIVALENCE NOT AUTHORIZED**: The existing architecture does not explicitly authorize rules for equating differing uncertainty bounds for caching purposes. 

## 10. Missing/Unknown Semantics
**EXISTING FACT**: If an inferred property is `UNKNOWN` or `NULL`, the resulting Phase 4 and Phase 5 evaluations explicitly incorporate that unknown status, directly affecting feasibility. Two states sharing the exact same `UNKNOWN` properties are scientifically equivalent.

## 11. Equality / Equivalence Requirements
**UNRESOLVED**: The architecture implies that "State A == State B" if their inferred values and uncertainties are mathematically equivalent. However, the existing source DOES NOT authorize a mechanism to evaluate, normalize, or hash a complete `PropertyInferenceProfile` into a lattice lookup key. 

## 12. Traceability Requirements
**SOURCE-AUTHORIZED REQUIREMENT**: The provenance, trace metadata, and raw user inputs must remain indelibly attached to the runtime context and the final Pareto front for auditability. They are decoupled from the indexing mechanism but permanently retained in the data payload.

## 13. Proposed Identity Contract
**UNRESOLVED**: Because the existing M6-A contract explicitly defines the tier 1 lattice key strictly as `(commodity, target_days, temp, RH)`, it provides absolutely no authority to hash or construct a key from the dynamically inferred properties (e.g., respiration rate, pH) output by Phase 3.

## 14. Unresolved Questions
- How is a dictionary of floating-point biological properties mathematically normalized for a deterministic cache key? (Floating-point precision matching).
- How are missing properties handled in the hash?
- Is Tier 1 caching actually viable if it requires waiting for Phase 3 inference to complete in order to build the cache key?

## 15. M6-B5 Gating Consequence
**M6-A RESOLVED SCIENTIFIC STATE IDENTITY BLOCKED — INSUFFICIENT SOURCE BASIS**

The existing project documentation fundamentally lacks the architectural authorization and mathematical definitions required to map a complex Phase 3 `PropertyInferenceProfile` into a deterministic Tier 1 caching identity. No safe minimum identity can be established from the current source.
