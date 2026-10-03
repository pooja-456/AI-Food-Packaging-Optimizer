# Raw Dataset: CIRAD / WUR Packaging Barrier Database

## 1. Source Identification & Primary Reference
- **Source Name:** CIRAD / Wageningen University (WUR) Packaging Barrier Database
- **Institutional Authorities:**
  - CIRAD - French Agricultural Research Centre for International Development, France.
  - Wageningen University & Research (WUR) - Food & Biobased Research, Netherlands.
- **Primary URL:** https://www.cirad.fr/ & https://www.wur.nl/

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Version:** 2026 Research Benchmark Ingestion Snapshot
- **Local Raw Files:** `cirad_wur_packaging_dataset.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format
- **Key Fields:**
  - `material_id`: Unique record identifier (e.g. `MAT-RAW-LDPE-50UM`).
  - `material_name`: Descriptive polymer specimen name string.
  - `polymer_code`: Standard polymer acronym (LDPE, HDPE, BOPP, BOPET, BOPA).
  - `structure_type`: `"monolayer"`, `"multilayer"`, or `"laminate"`.
  - `measured_thickness_um`: Specimen physical thickness in micrometers ($\mu\text{m}$).
  - `barrier_measurements`: Array of objects (`property`, `value`, `unit`, `test_temperature_c`, `test_rh_percent`, `test_standard`, `measurement_type`).
  - `sustainability_profile`: `recyclable`, `recycling_code`, `bio_based`, `compostable`.

## 4. Provenance & License Terms
- **License:** Open Academic Research Dataset.
- **Evidence Priority Tier:** Tier 1 (Peer-Reviewed / Institutional Open Database).
- **Source Operational Class:** Group A (Actual Data Source).

## 5. Scientific Scope & Known Limitations
- **Scope:** Provides experimental measurements for benchmark monolayer flexible packaging polymers (LDPE, HDPE, BOPP, BOPET, BOPA) with explicit recorded test conditions ($T, \text{RH}$, test standard).
- **Known Limitations:**
  - Test conditions follow standard ASTM protocols ($23^\circ\text{C}, 0\% \text{ RH}$ for OTR/CO2TR; $38^\circ\text{C}, 90\% \text{ RH}$ for WVTR).
  - Thickness normalization must NOT be performed unless physically validated for the specific specimen.
