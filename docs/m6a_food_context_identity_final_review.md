# M6-A Food Context Identity Final Review

## 1. Current Proposed Decision
**EXISTING FACT**: The prior amendment draft proposed Option B — Full Food Context (`commodity` + `variety` + `product_form` + `ripeness_stage`) as the required lattice identity, enforcing that two requests share a coordinate ONLY when all four raw contextual inputs are exactly identical.

## 2. Phase 3 Fallback Behavior
**EXISTING FACT**: The Phase 3 Generic Property Inference Engine (`InferenceResolutionLevel`) actively utilizes fallback logic (`VARIETY_FALLBACK`, `FORM_FALLBACK`, `GENERAL_COMMODITY_MATCH`). If specific evidence for a requested context (e.g., `variety="Gala"`) is missing, the engine falls back to generic evidence (e.g., generic apple). The resulting `InferredProperty` profile and traceability log record this fallback resolution.

## 3. Raw Context vs Resolved Context
**EXISTING FACT**: 
- **RAW INPUT CONTEXT**: The user-supplied strings (`PackagingRequest`).
- **INFERENCE RESOLUTION**: The structural depth at which evidence was found (e.g., `VARIETY_FALLBACK`).
- **SCIENTIFIC STATE**: The final calculated mathematical requirements (`PackagingRequirementEnvelope`).
- **LATTICE LOOKUP IDENTITY**: The caching index.
- **TRACEABILITY**: The immutable audit trail of provenance.
These concepts are distinct in the architecture.

## 4. Scientific-State Equivalence Analysis
- **CASE 1 (Gala vs NULL, no Gala evidence)**: Both requests undergo Phase 3 inference. Gala triggers a `VARIETY_FALLBACK`. Both resolve to the exact same `PropertyInferenceProfile` values, which generate the exact same `PackagingRequirementEnvelope`. Because the downstream constraints and requirements are mathematically identical, the optimization engine will produce an identical `ParetoFront`.
- **CASE 2 (Gala vs Granny Smith, both have distinct evidence)**: Both resolve via `EXACT_CONTEXT_MATCH`. They produce distinct `PropertyInferenceProfile` values (e.g., differing respiration rates) and distinct `PackagingRequirementEnvelope` constraints. They mathematically mandate distinct optimization states.
- **CASE 3 (Different raw, identical resolved)**: The scientific constraints are identical; therefore, the optimization boundaries are identical. 
- **CASE 4 (Identical raw, distinct evidence availability)**: Given a static database version (`evidence_database_version`), identical raw inputs deterministically produce identical resolved states.

## 5. NULL/Fallback Analysis
**ARCHITECTURAL CONSEQUENCE**: A raw input of `variety="Gala"` that falls back to a generic match is mathematically and scientifically equivalent (in Phase 4/5/6) to a raw input of `variety=NULL` that uses the same generic match. The raw string "Gala" only changes the *traceability*, not the *scientific state*. 

## 6. Safe Equivalence Rule
**UNRESOLVED — RESOLVED-SCIENTIFIC-STATE EQUIVALENCE IS NOT CURRENTLY AUTHORIZED**.
While it is an architectural fact that identical `PackagingRequirementEnvelope` objects will yield identical Pareto fronts, the M6-A contract ("Tier 1: Precomputed Lattice... Evaluates if the exact (commodity, target_days, temp, RH) matches a precomputed baseline") currently lacks a formal deterministic rule explicitly authorizing the system to group mathematically identical resolved states under a shared cache key.

## 7. Review of Option B
**EXISTING FACT**: The Option B rule ("same exact commodity + variety + product_form + ripeness_stage") is **TOO STRICT** and **UNSAFE** (in terms of system design, not physics). 
- It forces the lattice to fragment artificially based on RAW user input rather than actual SCIENTIFIC STATE. 
- It would cause cache misses for `variety="Gala"`, `variety="Fuji"`, and `variety=NULL` even if all three physiologically resolve to the exact same generic generic apple baseline.
- Therefore, Option B erroneously elevates a traceability/input detail to a scientific boundary constraint without architectural justification.

## 8. Final Architectural Finding
**PROPOSED DECISION**: The lattice identity must NOT be based on the Raw User Food Context. It is the Resolved Scientific Food Context (or its equivalent mathematical requirement envelope) that determines true scientific equivalency. Option B is formally rejected for cache identity, although full raw context must still be preserved for traceability. 

## 9. Required Future Contract Amendment
The architecture board must formally define how the Resolved Scientific Context is hashed or grouped to form the Tier 1 lattice key, replacing the simplistic raw `(commodity, target_days, temp, RH)` tuple currently defined in M6-A.

## 10. M6-B5 Gate
**ARCHITECTURAL CONSEQUENCE**: M6-B5 verification remains BLOCKED. Neither the raw `commodity` index (Option A) nor the full raw string index (Option B) are scientifically sound indexing structures for a caching system dependent on fallback resolutions.
