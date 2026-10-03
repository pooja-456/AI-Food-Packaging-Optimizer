# M5-A: Canonical Data Model & Database Schema Design

## 1. Purpose
This document specifies the canonical relational database schema for the AI-Food-Packaging-Optimizer. The purpose is to transition the verified, immutable JSON staging data (M4) into a structured SQL representation that preserves 100% of the scientific meaning, hierarchical structure, and lineage of the evidence.

## 2. Design Principles
1. **Scientific Fidelity:** Do not force unrelated physical properties into generic columns. Separate Respiration from Barrier properties. 
2. **First-Class Provenance:** Every observation must trace back to a unified `EvidenceRecord` and `Source`.
3. **No Destructive Flattening:** Deeply nested JSON data (e.g., ComBase growth kinetics and gas inhibitions) must be preserved via explicit relational mapping, not abandoned or hidden in opaque JSON blobs.
4. **Value & Range Preservation:** The schema natively supports exact bounds, inequality operators, and ranges for observations (e.g., `value_min`, `value_max`, `operator`).
5. **No Invented Conversions:** M4 did not blindly convert units; the schema will store the parsed `original_value` alongside `canonical_unit` which defaults to NULL until downstream physics normalizations occur.
6. **Missingness Preservation:** Values missing in literature are not simply converted to SQL `NULL`; they are qualified via a `missingness_status` Enum (e.g., `NOT_REPORTED`, `BELOW_DETECTION_LIMIT`) to preserve the exact semantic absence.

## 3. Actual M4 Dataset Inventory
An independent audit found the actual volume to be 47 root evidence records:
1. **usda_fdc** (6) - Proximate and physicochemical properties.
2. **india_ifct** (8) - Indian food composition.
3. **usda_handbook_66** (4) - Apple/Strawberry/Tomato/Spinach respiration limits.
4. **uc_davis** (3) - Produce facts (temperature-dependent respiration).
5. **indian_postharvest** (8) - Indian-specific produce and respiration limits.
6. **cirad_wur** (5) - Baseline material barrier properties.
7. **polyid** (4) - PolyID QSAR & Experimental barrier data.
8. **manufacturer_tds** (4) - Commercial TDS sheets with multilayer barrier data.
9. **combase** (5) - Microbial kinetic and cardinal growth parameters.

## 4. Entity Inventory
**15 Entities Total:**
- **Core Lineage:** `Source`, `EvidenceRecord`, `DataTransformation`, `ValidationResult`
- **Food Evidence:** `FoodCommodity`, `FoodObservation`, `RespirationObservation`, `PostharvestStorageLimits`, `PostharvestGasTolerances`
- **Material Evidence:** `PackagingMaterial`, `MaterialBarrierObservation`
- **Microbial Evidence:** `MicrobialOrganism`, `MicrobialCardinalParameters`, `MicrobialGrowthKinetics`, `MicrobialGasInhibitionResponse`

## 5. Entity Definitions & Primary Keys
All Primary Keys (PKs) will utilize `UUIDv4` to safely support distributed/offline ingestion without integer collision. Foreign Keys (FK) link down the hierarchy.

## 6. Relationships & Foreign Keys
- A `Source` has many `EvidenceRecord`s.
- An `EvidenceRecord` acts as the provenance anchor. It represents exactly 1 `FoodCommodity`, 1 `PackagingMaterial`, OR 1 `MicrobialOrganism`.
- A `FoodCommodity` has many `FoodObservation`s, `RespirationObservation`s, `PostharvestStorageLimits`, and `PostharvestGasTolerances`.
- A `PackagingMaterial` has many `MaterialBarrierObservation`s.
- A `MicrobialOrganism` has 1 `MicrobialCardinalParameters`, 1 `MicrobialGasInhibitionResponse`, and many `MicrobialGrowthKinetics`.

## 7. Unique Constraints
- `Source`: `UNIQUE(url)`
- `FoodCommodity`: `UNIQUE(scientific_name, processing_state, origin_region)`
- `MicrobialOrganism`: `UNIQUE(organism_name, strain)`

## 8. Scientific Value Representation
To preserve the robust M4 parsing, numeric values are structured as follows across `Observation` tables:
- `original_value` (VARCHAR)
- `value` (FLOAT, exact midpoint or parsed single value)
- `value_min` (FLOAT)
- `value_max` (FLOAT)
- `operator` (VARCHAR: '=', '<', '>', '<=', '>=', 'RANGE')
- `is_range` (BOOLEAN)
- `missingness_status` (ENUM)

## 9. Unit Strategy
- `original_unit` (VARCHAR): Preserves the source text exactly as scraped.
- `canonical_unit` (VARCHAR NULL): Intended for the physics-standardized unit. Defaults to NULL on insertion.

## 10. Condition Strategy
Conditions (Temperature, RH, pH) are tightly coupled to the phenomena they describe (Hybrid Model).
- For `RespirationObservation`: `temperature_c` (and its parsed variants) are columns on the observation.
- For `MaterialBarrierObservation`: `test_temperature_c` and `test_rh_percent` are columns on the barrier measurement.
- This prevents creating an over-normalized `Condition` table that joins to everything but enforces nothing.

## 11. Provenance Model
The `EvidenceRecord` acts as the junction.
- It stores `record_identifier_in_source`.
- It explicitly flags `evidence_classification` (e.g., `MODEL_PREDICTED` vs `EXPERIMENTAL_LITERATURE_DATA`), ensuring PolyID predictive values are safely isolated.
- It retains the `verification_status` to protect Indian dataset limits (`PARTIALLY_VERIFIED`).

## 12. Food & Respiration Model
Respiration is extremely specific:
- `RespirationObservation` explicitly requires a `gas_species` (`O2` or `CO2`).
- It structurally prevents the database from assuming all respiration relates to a single gas.
- `PostharvestStorageLimits` separates chilling injury constraints from composition.
- **Indian EMAP Limits:** `PostharvestGasTolerances` explicitly captures critical physiological boundaries (`min_o2_fermentation_limit_percent`, `max_co2_injury_limit_percent`), proving they are source evidence measurements, not downstream AI recommendations.

## 13. Material & Barrier Model
`PackagingMaterial` supports `layer_sequence` (JSONB) to safely store multilayer structures (e.g., PET/EVOH/PE).
`MaterialBarrierObservation` mandates a `property_type` (`OTR`, `CO2TR`, `WVTR`), preventing cross-contamination of permeability domains.

## 14. Microbial Model (ComBase Explicit Handling)
The relational schema fully accommodates the complex ComBase JSON layout:
- `MicrobialCardinalParameters`: Captures the global organism limits (min/opt/max temp/pH/aw).
- `MicrobialGrowthKinetics`: Captures the specific growth rate (`mu_max`), lag time, and specific environment (`temp`, `pH`, `aw`) for an experimental observation.
- `MicrobialGasInhibitionResponse`: Explicitly maps the organism's `co2_sensitivity` and `minimum_co2_inhibition_percent`, preventing the silent data loss previously identified during audit.

## 15. JSON Archival Strategy
PostgreSQL JSONB is strictly utilized for:
- Archiving the original `data/raw` payload into a `raw_json_payload` column on `EvidenceRecord` to guarantee absolute lineage traceability.
- Variable-length non-queryable arrays like `literature_references`.
- JSONB is NOT used to hide first-class scientific fields like gas inhibition; those remain fully relational.

## 16. Validation & Lineage
M4 operations are recorded identically as they occurred:
- `DataTransformation` logs actions like `NUMERIC_PARSE` and `MISSINGNESS_NORMALIZATION`.
- `ValidationResult` explicitly stores M4 assertions (dataset, record, rule, status, severity, message) linked back to the `EvidenceRecord`.

## 17. Normalization Decisions
- **Anti-Overnormalization:** We embed conditions directly into observations.
- **Anti-Denormalization:** We strictly separate OTR and WVTR into distinct rows via `property_type`, rather than creating extremely sparse wide columns.

## 18. Indexing & Database Technology
- **Database:** PostgreSQL.
- **Why:** Safely bridges strict ACID relational mapping with JSONB support for archival payloads and layered material sequences.
- **Indexes:** BTREE on `(commodity_id, property_name)`, GIN on `raw_json_payload`.

## 19. Future Compatibility
The schema isolates source evidence. Future tables (e.g., `PackagingCandidate`, `OptimizationParetoFront`) will be built on top of this model but will not alter or pollute the underlying evidence tables.

## 20. Known Limitations
- Sparse material thickness in some primary literature (CIRAD records) limits strict dimensional permeability scaling.
- The 47-record volume is an operational constraint-checker foundation; it does not support supervised ML surrogate modeling.

## 21. Next Steps (M5-B)
1. Instantiate the PostgreSQL Docker configuration.
2. Implement SQL schema via SQLAlchemy ORM or raw DDL migrations matching this specification.
3. Construct the ingestion script to map the 9 verified M4 JSONs into the relational tables.
