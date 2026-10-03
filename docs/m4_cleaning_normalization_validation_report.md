# Milestone 4 (M4) ?" Data Cleaning, Normalization & Validation Report

**Project:** AI-Based Intelligent Food Packaging Material Recommendation System for Food Commodities  
**Milestone:** M4 ?" Data Cleaning, Normalization & Validation  
**Date:** September 27, 2026  
**Status:** Corrected & Validated  
**Pipeline Location:** `scripts/m4_pipeline.py`  
**Processed Datasets Location:** `data/processed/`  
**Test Suite Status:** 155 / 155 passed (`pytest -q` ?" 151 baseline + 4 M4 data engineering tests)  

---

## 1. Scope
The primary objective of Milestone 4 (M4) is to transition the raw evidence staging layer (`data/raw/`) into a clean, normalized, and machine-validated dataset foundation (`data/processed/`) ready for future canonical database schema design. This is strictly a data engineering pipeline. M4 does NOT perform scientific imputation, machine learning, or optimization.

---

## 2. Input Datasets
All 9 staging datasets from M2/M3 were ingested as inputs:
1. `data/raw/food/usda_fdc/usda_fdc_sample_foundation.json`
2. `data/raw/food/india_ifct/india_ifct_2017_composition.json`
3. `data/raw/postharvest/usda/usda_handbook_66_respiration.json`
4. `data/raw/postharvest/uc_davis/uc_davis_produce_facts.json`
5. `data/raw/postharvest/india/icar_iifpt_indian_postharvest.json`
6. `data/raw/materials/cirad_wur/cirad_wur_packaging_dataset.json`
7. `data/raw/materials/polyid/polyid_experimental_vs_predicted.json`
8. `data/raw/materials/manufacturer/manufacturer_tds_datasheets.json`
9. `data/raw/microbial/combase/combase_microbial_kinetics.json`

---

## 3. Output Datasets & Record Reconciliation
The immutable staging principle was strictly observed. `data/raw/` remains untouched.

| Dataset | Input Records | Output Records | Status |
|---|---:|---:|---|
| usda_fdc | 6 | 6 | Cleaned |
| india_ifct | 8 | 8 | Cleaned |
| usda_handbook_66 | 4 | 4 | Cleaned |
| uc_davis | 3 | 3 | Cleaned |
| indian_postharvest | 8 | 8 | Cleaned |
| cirad_wur | 5 | 5 | Cleaned |
| polyid | 4 | 4 | Cleaned |
| manufacturer_tds | 4 | 4 | Cleaned |
| combase | 5 | 5 | Cleaned |

---

## 4. Cleaning Transformations Actually Performed
- **Whitespace Trimming:** Applied to strings where necessary (e.g., commodity names, food categories).
- **Category Normalization:** Standardized casing (e.g., `processing_state` was capitalized to match categorical definitions).

---

## 5. Missingness Handling
Explicit missing representations ("N/A", "unknown", "") were safely mapped to `None` with corresponding logging indicating missing values. No data was implicitly replaced with averages, medians, or domain knowledge estimations.

---

## 6. Numeric / Range / Inequality Parsing
Numerical fields were actively evaluated using `parse_numeric_or_range`. It retains the `original_value` property and introduces `value`, `value_min`, `value_max`, `operator`, and `is_range`. String representations are appropriately tokenized (e.g., separating standard scalars from ">10" or "10 - 20").

---

## 7. Unit Normalization & Respiration Semantics
Respiration metrics successfully preserve their original semantic definitions (e.g., CO2 evolution versus O2 uptake rates). No "mg/kg-h" tags were blindly injected. Explicit, mathematically rigorous unit conversion is deferred unless exact boundary conditions for calculation (like density, surface area, test temperature, pressure) are present; otherwise, original properties are protected.

---

## 8. Material Barrier Handling & Preservation
Properties such as `OTR`, `CO2TR`, and `WVTR` are maintained discretely. No attempt is made to inter-derive transmission rates without explicit, evidence-backed mathematical conversions. Conditions (RH, Temperature, Material, Thickness) accompanying them are strictly preserved in their original hierarchy.

---

## 9. Provenance Preservation
The root-level `source_metadata` block (containing URL, snapshot date, authors, institution, and license details) remains rigorously attached at the root level of every processed JSON output, preserving traceability from parsed records back to origin endpoints.

---

## 10. Indian Evidence Handling
Locally significant variations such as Alphonso, Kesar, Guava, Okra, and Paneer remain intact as distinctly reported profiles. Validation states were left appropriately unchanged (e.g., `PARTIALLY_VERIFIED`).

---

## 11. Experimental vs Predictive Separation
The PolyID dataset segregates `experimental_observations` and `predicted_values` unambiguously, ensuring predictive QSAR outputs aren't miscategorized as experimentally validated ground truth.

---

## 12. Outlier Handling & Conflict Preservation
Scientifically plausible outliers, like the EVOH 85% RH OTR curve, were actively recognized and flagged with a `RETAIN` action. Overlapping observations for identical materials or foods across differing sources are stored concurrently without arbitrary averaging.

---

## 13. Validation & Test Coverage
The suite (`tests/test_m4_pipeline.py`) validates integration directly against the output files generated in `data/processed/`, ensuring that source_metadata persists, numeric parsing objects actually populate, polyid sets properly separate their origins, and no blind tags enter semantic fields. The baseline suite passed regression seamlessly without modification to `backend/app/` logic.

---

## 14. Phase 1-5 Regression & M5 Readiness
No functionality in the `backend/` or `scientific_engine/` was altered. No optimization, ML, or SQL configurations were introduced. The system remains prepared for Database Schema definitions (M5).
