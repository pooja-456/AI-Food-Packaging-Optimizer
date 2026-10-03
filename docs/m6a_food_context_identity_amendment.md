# M6-A Food Context Identity Amendment

## 1. Status
**PROPOSED DECISION — AWAITING REVIEW**

## 2. Problem Being Resolved
The M6-A optimization architecture currently indexes the Tier 1 Precomputed Lattice using only the `commodity` string. However, the upstream scientific inference pipeline (Phase 3) generates materially different biological requirements based on `variety`, `product_form`, and `ripeness_stage`. Using `commodity` alone as the cache key forces distinct physiological states (e.g., whole vs. fresh-cut apple) to dangerously collapse into the exact same precomputed optimization result.

## 3. Existing Source-of-Truth Evidence
- **Phase 3 Inference**: `PropertyInferenceProfile` natively accepts `commodity`, `variety`, `product_form`, and `ripeness_stage`.
- **Phase 3 Matching**: `InferenceResolutionLevel` explicitly distinguishes `EXACT_CONTEXT_MATCH`, `VARIETY_FALLBACK`, and `FORM_FALLBACK`.
- **Optimization Envelope**: `OptimizationInputEnvelope` and `PackagingRequirementEnvelope` explicitly define ONLY `commodity`. `variety`, `product_form`, and `ripeness_stage` are dropped from the schema before optimization.
- **Lattice Contract**: `LatticeCoordinate` (M6-B5) currently only uses `commodity`.

## 4. Scientific Dependency Trace
| Field | Input | Used in inference | Can affect scientific output | Reaches Phase 4 | Reaches Phase 5 | Traceable | Source evidence |
|------|------|-------------------|------------------------------|------------------|------------------|-----------|-----------------|
| commodity | YES | YES | YES | YES | YES | YES | `PackagingRequest`, `PropertyInferenceProfile` |
| variety | YES | YES | YES | NO (Dropped) | NO (Dropped) | YES | `PackagingRequest`, `PropertyInferenceProfile` |
| product_form | YES | YES | YES | NO (Dropped) | NO (Dropped) | YES | `PackagingRequest`, `PropertyInferenceProfile` |
| ripeness_stage | YES | YES | YES | NO (Dropped) | NO (Dropped) | YES | `PackagingRequest`, `PropertyInferenceProfile` |

*(Note: While variety, form, and ripeness are dropped as named schema fields in Phase 4/5, their mathematical effects on the calculated barrier requirements absolutely reach Phase 4/5).*

## 5. Scientific Evaluation Context
**EXISTING FACT**: The scientific evaluation context includes `commodity`, `variety`, `product_form`, `ripeness_stage`, and environmental factors (temperature, RH). This is the minimum necessary context for Phase 3 to accurately calculate the scientific requirements.

## 6. Lattice Lookup Identity
**PROPOSED DECISION**: The dimensions that determine which precomputed ParetoFront may safely be reused. Because biological requirements diverge based on variety, form, and ripeness, the lattice lookup identity must include them to prevent false equivalency.

## 7. Traceability Context
**EXISTING FACT**: The original user/evidence context that must remain visible for audit and explanation. This is distinct from the lookup identity; even if a dimension is dropped or normalized for caching, it must remain fully preserved in the provenance records.

## 8. Option A — Commodity Only
- **Analysis**: Scientifically unsafe.
- **Evaluation**: Would allow mathematically distinct biological states (e.g. mature vs ripe, whole vs fresh-cut) to reuse the same ParetoFront. This directly violates the scientific integrity rule.

## 9. Option B — Full Food Context
- **Analysis**: Scientifically safe.
- **Evaluation**: Incorporates `commodity`, `variety`, `product_form`, and `ripeness_stage` into the optimization identity. This perfectly aligns with Phase 3 inference, preventing false caching equivalency, though it requires expanding the M6-B1 and M6-A contracts.

## 10. Option C — Hierarchical Identity
- **Analysis**: Theoretically efficient, but NO DETERMINISTIC SOURCE-AUTHORIZED RULE EXISTS to determine when a contextual field is "materially relevant" enough to split the cache. Implementing this would require inventing a dynamic caching rule not supported by the current deterministic architecture.

## 11. Safe Lattice Equivalence Rule
**ARCHITECTURAL CONSEQUENCE**: Two requests may safely share a precomputed ParetoFront ONLY IF their exact combinations of `commodity`, `variety`, `product_form`, and `ripeness_stage` are identical. It is scientifically unsafe to assume distinct physiological contexts produce equivalent packaging constraints unless the underlying models explicitly output identical requirement envelopes.

## 12. Missing Context / NULL Handling
**PROPOSED DECISION**: If a contextual field (e.g., `variety`) is NULL in the request, the lattice lookup identity explicitly uses NULL for that dimension. A request with `commodity="Apple", variety=NULL` may safely share a cache with another `commodity="Apple", variety=NULL` request, but it CANNOT share a cache with `commodity="Apple", variety="Fuji"`. 

## 13. Canonicalization
**EXISTING FACT**: The project source of truth authorizes case-insensitive string normalization for inputs. 
**UNRESOLVED**: The project does not define a formal alias, synonym, or botanical name resolution registry. "Apple" and "Apples" currently resolve to distinct strings unless separately managed by an undefined frontend layer.

## 14. Commodity-Agnostic Requirement
**SOURCE-AUTHORIZED REQUIREMENT**: The lattice identity model remains entirely generic. It mathematically treats all commodities identically and does not hard-code logic for specific foods (e.g., Apple, Salmon) or assume the current test datasets represent the production universe.

## 15. Architectural Decision
**PROPOSED DECISION**: Option B (Full Food Context). The lattice lookup identity MUST be expanded to formally include `commodity`, `variety`, `product_form`, and `ripeness_stage`. This is the only mathematically defensible way to preserve the scientific integrity of the Phase 3 inference engine when caching optimization results.

## 16. Required Contract Changes
**PROPOSED DECISION**: 
- `OptimizationInputEnvelope` (M6-B1) must be expanded to include `variety`, `product_form`, and `ripeness_stage`.
- `PackagingRequirementEnvelope` (Phase 4 output) must be expanded to include `variety`, `product_form`, and `ripeness_stage`.
- `LatticeCoordinate` (M6-B5) must be expanded to include `variety`, `product_form`, and `ripeness_stage`.

## 17. Unresolved Questions
- **Alias Resolution**: How are synonyms (e.g., "Tomato" vs "Tomatoes") resolved prior to caching? (UNRESOLVED — REQUIRES EXPLICIT ARCHITECTURAL DECISION).
- **Lattice Size Explosion**: Adding three dimensions to the grid exponentially increases the theoretical lattice size. Does the system still intend to precompute the *entire* grid (Tier 1), or will it rely entirely on on-demand calculation + runtime caching for anything other than generic whole commodities? (UNRESOLVED).

## 18. M6-B5 Gating Consequence
**ARCHITECTURAL CONSEQUENCE**: M6-B5 remains NOT VERIFIED. Its current implementation (`commodity` only) violates the Safe Lattice Equivalence Rule established in this document. M6-B5 cannot be rewritten until this proposed amendment and the associated contract changes are formally approved.
