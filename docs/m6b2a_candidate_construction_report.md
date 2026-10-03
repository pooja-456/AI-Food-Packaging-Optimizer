# M6-B2A CANDIDATE CONSTRUCTION REPORT

**Project**: AI-Based Intelligent Food Packaging Material Recommendation System
**Milestone**: M6-B2A (Candidate Construction)
**Status**: IMPLEMENTATION COMPLETE, PENDING AUDIT

---

## 1. Objective
Implement a deterministic candidate-construction layer to transform M5 canonical evidence into valid M6-B1 `PackagingCandidate` objects, while enforcing strict material-specific thickness rules, provenance preservation, and omitting all algorithmic optimization components.

## 2. Architecture & Location
- **Inspected Architecture**: The `scientific_engine/optimization/` directory was found to be the correctly designated target for Phase 6 computational components.
- **Implementation**: Created `scientific_engine/optimization/candidate_builder.py` housing the `CandidateBuilder` class.
- **Tests**: Created `backend/tests/test_candidate_construction.py`.

## 3. M5 → M6-B2A Mapping & Flow
1. **Iterate Materials**: Fetch all `PackagingMaterial` instances.
2. **Evidence Grouping**: Fetch associated `MaterialBarrierObservation` records and group them by `(evidence_id, thickness_value)`. This structurally prevents cross-evidence mixing (e.g., gluing Material A's thickness to Material B's barrier property).
3. **Cartesian Alignment**: Separate observations by `PropertyType` (OTR, CO2TR, WVTR) and emit a Cartesian product for distinct test-condition sets (e.g., EVOH's OTR at 0%, 65%, 85% RH each generates a distinct valid representation state).
4. **Instantiation**: Instantiate `PackagingCandidate` adhering strictly to M6-B1 rules.

## 4. Material-Specific Thickness (F-5.1 Corrected Logic)
The implementation rigorously respects the material-specific thickness rule. A candidate is only constructed for the `thickness_value` literally present in its `MaterialBarrierObservation`. The global M5 set of `{12, 15, 25, 30, 40, 50, 70}` is **not** treated as a universal permutation matrix. (For example, LDPE produces *only* 50 μm candidates).

## 5. PolyID, Multilayer, and Predicted Semantics
- **PolyID (Null Structures)**: When `structure_type` is NULL in the DB, it is natively mapped as `None`. The candidate builder does not invent structures.
- **Multilayer Order**: `layer_sequence` arrays are preserved exactly.
- **Predicted vs Empirical**: `evidence_classification.name` securely routes to `EvidenceTier` (e.g. `MODEL_PREDICTED`). `synthetic_prediction_warning` is pulled directly from the `EvidenceRecord`.

## 6. Barrier and Condition Handling
- OTR and WVTR are required to construct a valid candidate (following M6-B1 rules).
- CO2TR remains cleanly optional / `None` if missing.
- Test conditions (Temp, RH) are mapped precisely to the `BarrierPropertyMetric`.
- `ConditionMatchLevel` defaults strictly to `UNKNOWN` because Phase 5 feasibility has not run.

## 7. Deterministic Identity
Candidate UUIDs are generated using `uuid.uuid5` with a dedicated namespace and a deterministic string key:
`{material_id}_{evidence_id}_{thickness}_{otr_id}_{wvtr_id}_{co2tr_id}`
This ensures identical evidence records always yield identical candidate IDs across runs, aiding cacheability and testability.

## 8. Geometry
Geometry is explicitly omitted from `PackagingCandidate` (matching the M6-B1 data contract definition), ensuring no fake default values (like 1m² or 1kg) are ever embedded into the candidate's core identity.

## 9. Tests and Regression
Using real M5 evidence (via `DataIngestionPipeline` targeting an in-memory SQLite backend), 12 tests were written verifying all requested rules (PolyID null structure, un-invented thickness, global set non-universality, missing geometry, lack of Phase 5 actions).

**Regression output**:
- **Previous Baseline**: 177 tests passing.
- **New Tests**: +12
- **Final Result**: 189 tests passing, 0 failures, 1 warning (Starlette deprecation).

## 10. Explicit Phase Boundary Confirmation
This implementation is strictly a data-translation mechanism. 
**It does NOT implement:**
- Phase 5 condition matching or feasibility filtering
- Phase 4 recalculation (F-10.1)
- Objective calculation ($f_{\text{thickness}}$, etc.)
- Pareto sorting, NSGA-II, MOEA/D, or genetic loops
- Redis/Celery integration or recommendation scoring

*M6-B2A is complete. No self-certification is claimed. Ready for M6-B2A Forensic Audit.*
