# M5-B3 FORENSIC AUDIT — DATA INGESTION

## 1. Executive Verdict
**M5-B3 NOT VERIFIED**

The ingestion pipeline successfully executed and satisfied the basic idempotency, phase boundary, and architectural requirements. However, critical scientific data loss was discovered during the audit. Specifically, maximum respiration boundaries were incorrectly overwritten by minimum values, microbial atmospheric conditions were discarded, and entire M4 entity classes (Validation Results and Data Transformations) were completely ignored. 

## 2. Scope
This forensic audit verified the M5-B3A data ingestion implementation (`backend/app/ingestion/pipeline.py`), inspecting mapping correctness, data preservation, constraint adherence, idempotency, and PostgreSQL validation limits.

## 3. Artifacts Audited
- `backend/app/ingestion/pipeline.py`
- `tests/test_ingestion_m5b3.py`
- `docs/m5b3_ingestion_implementation_report.md`
- `data/reference/m5b3_ingestion_reconciliation.json`
- M4 processed JSON inputs.

## 4. Dataset Reconciliation
The pipeline discovered and processed 9 datasets:
1. USDA FoodData Central: 6 inputs → 6 inserted
2. India IFCT: 8 inputs → 8 inserted
3. USDA Agriculture Handbook 66: 4 inputs → 4 inserted
4. UC Davis: 3 inputs → 3 inserted
5. Indian postharvest: 8 inputs → 8 inserted
6. CIRAD/WUR: 5 inputs → 5 inserted
7. PolyID: 4 inputs → 4 inserted
8. Manufacturer TDS: 4 inputs → 4 inserted
9. ComBase: 5 inputs → 5 inserted

**Claimed Total:** 47. 
**Actual Database Inserted:** 47. (Idempotency correctly skipped duplicates on subsequent runs).

## 5. Field-Level Mapping Audit
Significant mapping flaws were discovered:
- **Respiration Range Collapse (CRITICAL):** The parser logic `parsed = rm.get("min_parsed") or rm.get("max_parsed")` silently ignores the maximum bound. The minimum value overwrites the maximum field, permanently destroying scientific range intervals in the database.
- **ComBase Atmosphere (HIGH):** The field `atmosphere_condition` is present in M4 ComBase records (e.g., `"aerobic"`) but is entirely unmapped in `process_microbial()`. 
- **ValidationResult & DataTransformation (CRITICAL):** The pipeline completely failed to ingest `cleaning_log.json` or map `ValidationResult` assertions. The entities were not even imported in the pipeline module.
- **Literature References (HIGH):** The `literature_references` JSONB field in `EvidenceRecord` was not populated.

## 6. Scientific Value Preservation
- `value`, `value_min`, `value_max` are preserved for food properties.
- **Ranges/Inequalities:** Failed for respiration due to parsing logic flaw (see above).
- `original_value` correctly cast to string representation where mapped.

## 7. Missingness Audit
M4 `missingness_status` mapping was omitted. However, M4 processed datasets relied largely on omission rather than explicit ENUM tags for these 47 records. No artificial missingness values were invented (PASS).

## 8. Respiration Audit
- **rO2 vs rCO2:** Separated correctly into distinct rows based on gas species.
- **Gas Species:** `GasSpecies.O2` and `GasSpecies.CO2` ENUMs used properly.
- **Loss:** Maximum boundary ranges were corrupted due to dictionary key coalescing. 

## 9. Material Barrier Audit
- **OTR/CO2TR/WVTR:** Preserved as distinct properties.
- **Thickness/Temp/RH:** Accurately parsed and stored.

## 10. PolyID Audit
**EXPERIMENTAL_LITERATURE_DATA** and **MODEL_PREDICTED** are explicitly isolated. The parser maps the `predicted_values` array specifically to the `PREDICTIVE_ONLY` status, strictly protecting measured evidence from QSAR contamination. (PASS)

## 11. ComBase Audit
- `co2_sensitivity` and `minimum_co2_inhibition_percent` correctly mapped to `MicrobialGasInhibitionResponse`.
- Kinetics bounds preserved, EXCEPT for `atmosphere_condition`.

## 12. Indian Evidence Audit
`PostharvestGasTolerances` preserves `target_o2_min_percent`, `target_co2_max_percent`, `min_o2_fermentation_limit_percent`, and `max_co2_injury_limit_percent`. Source identity tracks back to Indian origin. Status remains `PARTIALLY_VERIFIED`. (PASS)

## 13. Provenance Audit
- `url`, `institution`, and `license` preserved in `Source`.
- `record_identifier_in_source` preserved.
- **LOSS:** Granular provenance (DOI, references) via `literature_references` was skipped.

## 14. Idempotency Audit
Uses a composite key check: `(source_id, record_identifier_in_source)`.
- **Limitation:** For datasets lacking a primary ID, the fallback is the array index (`str(idx)`). This makes deduplication brittle if upstream JSON array ordering changes. (MEDIUM severity).

## 15. Transaction Safety Audit
Handled holistically via SQLAlchemy session flushing. Failures trigger module-level aborts. (PASS).

## 16. PostgreSQL Validation Audit
**POSTGRESQL LIVE VALIDATION = NOT VERIFIED**
The ingestion implementation accurately reported that tests were run against a SQLite fallback environment. PostgreSQL-specific constraints (e.g., CheckConstraints, native ENUM rejections) remain untested. This is an environmental limitation, not a code defect, but stands as an outstanding validation gap.

## 17. Database Reconciliation
- `Source`: 9
- `EvidenceRecord`: 47
- `RespirationObservation`: 18
- `ValidationResult`: 0 (FAIL)
- `DataTransformation`: 0 (FAIL)

## 18. Reconciliation Artifact Audit
The JSON artifact (`m5b3_ingestion_reconciliation.json`) accurately reflects the runtime execution behavior (47 inputs, 47 inserted). 

## 19. Test Quality Audit
The 162 total tests (including 3 new pipeline tests) execute cleanly.
- Tests accurately proved idempotency and correct isolation of ComBase limits and OTR/WVTR.
- Tests failed to catch the `rate_max` respiration data loss and the missing `ValidationResult` ingestion.

## 20. Immutability Audit
`data/raw/` and `data/processed/` are completely unmodified. (PASS).

## 21. Architecture Boundary Audit
No Phase 6 ML/Optimization, Redis, Celery, or recommender logic was inserted. Strict boundary discipline was maintained. (PASS).

## 22. Reproducibility Audit
Execution is fully reproducible.

## 23. Findings
1. **Respiration Range Collapse:** `co2_production_rate_max_mg_kg_h` boundary lost due to dict key coalescing. (CRITICAL).
2. **Missing Entities:** `ValidationResult` and `DataTransformation` completely unmapped/ignored. (CRITICAL).
3. **ComBase Data Loss:** `atmosphere_condition` dropped. (HIGH).
4. **Provenance Loss:** `literature_references` skipped. (HIGH).
5. **Idempotency Fragility:** Relies on array indices if natural ID absent. (MEDIUM).

## 24. Severity Classification
**CRITICAL**

## 25. Corrective Actions Required
- Rewrite `RespirationObservation` parsing to independently extract `min_parsed` and `max_parsed`.
- Implement `cleaning_log.json` parsing into `DataTransformation` and `ValidationResult`.
- Map `atmosphere_condition` for Microbial kinetics.
- Map `literature_references` JSONB field in `EvidenceRecord`.

## 26. Final Scorecard
- Dataset Reconciliation: PASS
- Field-Level Mapping: FAIL
- Scientific Preservation: FAIL
- PolyID Isolation: PASS
- ComBase Structure: PASS WITH LIMITATION
- Indian Postharvest: PASS
- Idempotency: PASS WITH LIMITATION
- Immutability: PASS
- Boundary Discipline: PASS

## 27. Final Verdict
**M5-B3 NOT VERIFIED**
