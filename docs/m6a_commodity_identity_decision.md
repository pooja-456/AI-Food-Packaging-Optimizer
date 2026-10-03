# M6-A LATTICE COMMODITY IDENTITY DECISION

## 1. Decision Status
**PROPOSED ARCHITECTURAL DECISION — AWAITING REVIEW**

## 2. Problem Statement
The M6-A Tier 1 Optimization Lattice relies on a canonical `commodity` string to index precomputed packaging recommendations. However, the Phase 3 scientific inference engine hierarchically distinguishes contextual identities (variety, product form, ripeness stage) that possess materially different physiological behaviors (e.g., respiration rate, microbial spoilage). We must determine what exactly one lattice identity is authorized and required to represent without introducing false scientific equivalency or collapsing necessary context.

## 3. Existing Source-of-Truth Authorization

| Concept | Existing representation | Scientific significance | Existing lattice authorization |
|---------|--------------------------|--------------------------|-------------------------------|
| Commodity | `PackagingRequest.commodity`, `PropertyInferenceProfile.commodity` | Base biological taxon/name. | AUTHORIZED (M6-A, M6-B1, M6-B5) |
| Variety | `PackagingRequest.variety`, `PropertyInferenceProfile.variety` | Cultivar specific physiological traits. | NOT AUTHORIZED in lattice key |
| Product Form | `PackagingRequest.product_form`, `PropertyInferenceProfile.product_form` | Processing state (whole, fresh-cut) impacting respiration/microbial growth. | NOT AUTHORIZED in lattice key |
| Ripeness Stage | `PackagingRequest.ripeness_stage`, `PropertyInferenceProfile.ripeness_stage` | Maturity impacting climacteric peaks and softening. | NOT AUTHORIZED in lattice key |
| Temperature | `PackagingRequest.storage_temperature_c` | Thermodynamic multiplier for all kinetics. | AUTHORIZED (M6-A, M6-B1, M6-B5) |

## 4. Existing Inference Hierarchy
The Phase 3 Generic Property Inference Engine (`backend/app/schemas/inference.py`) actively utilizes contextual hierarchy. 
- **Input**: The `PropertyInferenceProfile` model natively accepts `commodity`, `variety`, `product_form`, and `ripeness_stage`.
- **Context Matching**: The `InferenceResolutionLevel` enum explicitly includes `EXACT_CONTEXT_MATCH`, `VARIETY_FALLBACK`, and `FORM_FALLBACK`.
- **Scientific Impact**: Changing the product form (e.g., whole apple vs. sliced apple) fundamentally changes the inferred `respiration_rate` and microbial susceptibility. This data feeds directly into Phase 4 constraint models.
- **Traceability**: Context is explicitly preserved in the supporting evidence records.

## 5. Optimization-Contract Analysis
The M6-B1 Optimization Contract (`backend/app/schemas/optimization.py`) does **not** distinguish variety, product form, or ripeness stage.
- The `OptimizationInputEnvelope` only contains the base `commodity` field.
- The `PackagingRequirementEnvelope` (output of Phase 4, input to Phase 6) also only contains the base `commodity` field.
The optimization layer is currently blind to the contextual identity that generated the underlying gas, moisture, and microbial requirements.

## 6. Current Lattice-Contract Analysis
The M6-B5 Lattice Contract (`backend/app/schemas/lattice.py`) strictly mirrors M6-B1:
- The `LatticeCoordinate` uses `commodity: str` as the sole food-identity index.
- Variety, product form, and ripeness stage are entirely absent from the coordinate and the lookup key.

## 7. Context-Collapse Risk
**Risk**: High. 
**Example**: 
- Request A: `commodity="Apple"`, `product_form="whole"`
- Request B: `commodity="Apple"`, `product_form="fresh_cut"`
Phase 3 perfectly distinguishes these requests, generating a low respiration rate for Request A and a massively accelerated respiration rate for Request B. Phase 4 accurately translates these into distinct `PackagingRequirementEnvelope` targets. 
However, if Tier 1 caching is indexed solely by `commodity="Apple"`, the lattice forces both Request A and Request B to hit the exact same generic precomputed Pareto Front. This constitutes a severe violation of scientific integrity by manufacturing false equivalency between mathematically distinct evidence bases.

## 8. Option A Analysis (commodity only)
- **Compatibility with existing inference**: Incompatible (collapses explicit hierarchical resolution).
- **Context preservation**: Fails to preserve physiological form/ripeness/variety.
- **Risk of collapsing distinct evidence**: Extremely high.
- **Compatibility with M6-B1/B2A/B2B**: Fully compatible (they only expect `commodity`).
- **Compatibility with M6-B5**: Fully compatible.
- **Commodity agnosticism**: Generic string matching.
- **Traceability**: Loses upstream identity linkage for caching.
- **Implementation complexity**: Lowest (status quo).

## 9. Option B Analysis (commodity + variety + product_form + ripeness_stage)
- **Compatibility with existing inference**: Fully compatible.
- **Context preservation**: Preserves exact physiological state.
- **Risk of collapsing distinct evidence**: Eliminated.
- **Compatibility with M6-B1/B2A/B2B**: Incompatible (requires schema expansion).
- **Compatibility with M6-B5**: Incompatible (requires coordinate expansion).
- **Commodity agnosticism**: Fully agnostic.
- **Traceability**: Complete end-to-end traceability.
- **Implementation complexity**: High (requires structural expansion of M6-B1, M6-B5, and lattice generator).

## 10. Option C Analysis (hierarchical/context-dependent identity)
- **Compatibility with existing inference**: Theoretically aligned, but no established optimization logic supports conditional hierarchy indexing.
- **Risk of collapsing distinct evidence**: Moderate, depending on implementation.
- **Implementation complexity**: Very High (requires a dynamic hashing mechanism not supported by the current deterministic dictionary).

## 11. Context Preservation Requirements
Regardless of the final lattice coordinate design, the system must retain:
- **Lookup Identity**: The indexing key used for caching.
- **Scientific Evaluation Context**: The actual `PropertyInferenceProfile` inputs that generated the requirements.
- **Traceability Metadata**: The provenance of the evidence.
The original `variety`, `product_form`, and `ripeness_stage` MUST be preserved on the runtime request object, even if they fall back to a generic commodity bin during lookup.

## 12. Canonicalization Analysis
- M6-B5 currently normalizes the `commodity` string using `.strip().lower()`.
- **UNRESOLVED — CANONICAL COMMODITY REGISTRY NOT DEFINED**: The project source of truth does not contain a formal alias, synonym, or botanical name resolution registry. Lowercase normalization does not solve semantic identity (e.g., "Apple" vs "Apples" vs "Malus domestica").

## 13. Commodity-Agnostic Requirement
Any chosen identity structure must remain entirely generic. The lattice must not hard-code "Apple", "Durian", or "Salmon". The current reference datasets are test evidence, not a restrictive production schema.

## 14. Proposed Architectural Decision
**UNRESOLVED — REQUIRES ARCHITECTURAL DECISION**.
The source material places the architecture in a deadlock:
1. M6-B1/M6-B5 contracts strictly isolate `commodity` as the sole identity dimension.
2. Phase 3 Inference natively calculates divergent scientific realities based on `product_form` and `variety`.
We cannot silently choose Option B (modifying upstream optimization contracts) nor can we silently choose Option A (violating the no-false-science rule by collapsing biologically distinct contexts into a single cache). 

## 15. Unresolved Decisions
- Must M6-B1 and M6-A be formally expanded to include full contextual identity (variety, form, ripeness) in the optimization envelope?
- Or does the Tier 1 lattice only safely support generic whole commodities, defaulting all contextual subsets to Tier 2 (Warm Start) execution?
- How are commodity synonyms/aliases mathematically normalized before hashing?

## 16. Required M6-A Amendment
M6-A must be explicitly amended to dictate the identity boundary before M6-B5 can be verified. The architecture board must formally rule on whether Tier 1 caching is permitted to collapse biological contexts or whether the coordinate system must be expanded.

## 17. M6-B5 Gating Implications
M6-B5 verification remains blocked. The canonical key logic in `backend/app/schemas/lattice.py` cannot be scientifically verified until the identity parameters are mathematically defined.

