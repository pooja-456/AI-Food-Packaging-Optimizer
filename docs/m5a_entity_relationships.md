# M5-A Entity Relationship Tree

```text
Source
  │
  └── EvidenceRecord
          │
          ├── FoodCommodity
          │       │
          │       ├── FoodObservation (moisture, fat, pH, aw)
          │       │
          │       ├── RespirationObservation (O2 consumption, CO2 production)
          │       │
          │       ├── PostharvestStorageLimits (chilling injury, map limits)
          │       │
          │       └── PostharvestGasTolerances (fermentation/injury EMAP bounds)
          │
          ├── PackagingMaterial
          │       │
          │       └── MaterialBarrierObservation (OTR, CO2TR, WVTR)
          │
          └── MicrobialOrganism
                  │
                  ├── MicrobialCardinalParameters (min/max temp, pH, aw limits)
                  │
                  ├── MicrobialGrowthKinetics (growth rate at specific temp/pH/aw)
                  │
                  └── MicrobialGasInhibitionResponse (CO2 sensitivity and inhibition boundaries)

(Cross-cutting Lineage Entities)
DataTransformation ─────────► EvidenceRecord
ValidationResult ───────────► EvidenceRecord
```

### Explanation of Scientific Segregation

1. **Food vs Material vs Microbes:** We do not force these into a single "Observation" table. Food commodities have respiration and biological constraints. Materials have multilayer physical properties. Microbes have non-linear kinetic models. They are separated into domain-specific entities branching from a unified `EvidenceRecord`.
2. **Respiration Isolation:** `RespirationObservation` explicitly requires a `gas_species` enum. O2 consumption is structurally isolated from CO2 production.
3. **Barrier Isolation:** `MaterialBarrierObservation` explicitly requires a `property_type` (OTR/CO2TR/WVTR), preventing generic "barrier values" from losing their identity.
4. **ComBase Nesting (Microbial):** The nested ComBase fields are safely housed in `MicrobialGrowthKinetics` (for the nested array of environments) and `MicrobialCardinalParameters` (for the generic organism-level bounds). Gas inhibition properties (e.g., CO2 sensitivity) are securely captured in `MicrobialGasInhibitionResponse`, preventing flat-table data loss.
5. **Indian Postharvest EMAP Bounds:** Specific limits identifying biological injury (e.g., `min_o2_fermentation_limit_percent`) are explicitly preserved via `PostharvestGasTolerances` rather than being discarded or mixed up with generic storage limits.
6. **Missingness Preservation:** Every observation entity contains a `missingness_status` Enum to structurally prevent `NOT_REPORTED`, `BELOW_DETECTION_LIMIT`, and `UNKNOWN` from collapsing indiscriminately into a silent SQL `NULL`.
7. **PolyID (Experimental vs Predicted):** The `EvidenceRecord` contains the `evidence_classification` (e.g., `MODEL_PREDICTED` vs `EXPERIMENTAL_LITERATURE_DATA`), maintaining strict isolation for PolyID predictive values.
