# Raw Dataset: USDA Handbook 66 (Commercial Storage of Fruits, Vegetables, and Florist and Nursery Stocks)

## 1. Source Identification & Primary Reference
- **Source Name:** USDA Agricultural Handbook 66
- **Institutional Authority:** United States Department of Agriculture (USDA) - Agricultural Research Service (ARS)
- **Primary Reference Document:** Gross, K.C., Wang, C.Y., Saltveit, M. (2016). *The Commercial Storage of Fruits, Vegetables, and Florist and Nursery Stocks*. USDA Agricultural Handbook 66.
- **Primary URL:** https://www.ars.usda.gov/is/np/CommercialStorage/CommercialStorage.pdf

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Snapshot Version:** HB66 Revised Edition
- **Local Raw Files:** `usda_handbook_66_respiration.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format
- **Key Fields:**
  - `commodity_name`: Standard English commodity name.
  - `scientific_name`: Binomial taxonomic name.
  - `respiration_measurements`: Array of objects per temperature $T$ (°C) containing `co2_production_rate_min_mg_kg_h`, `co2_production_rate_max_mg_kg_h`, `o2_consumption_rate_min_mg_kg_h`, `o2_consumption_rate_max_mg_kg_h`, `respiratory_quotient_rq_typical`.
  - `recommended_storage_conditions`: `storage_temperature_min_c`, `storage_temperature_max_c`, `relative_humidity_min_percent`, `relative_humidity_max_percent`, `approximate_shelf_life_days`.
  - `emap_tolerances`: `target_o2_min_percent`, `target_o2_max_percent`, `target_co2_min_percent`, `target_co2_max_percent`, `min_o2_fermentation_limit_percent`, `max_co2_injury_limit_percent`.

## 4. Provenance & License Terms
- **License:** US Government Public Domain (CC0 Equivalent).
- **Evidence Priority Tier:** Tier 2 (Authoritative Government Handbook).
- **Source Operational Class:** Group A (Actual Data Source).

## 5. Scientific Scope & Known Limitations
- **Scope:** Defines postharvest respiration kinetics ($r_{\text{CO}_2}$, $r_{\text{O}_2}$) and optimum storage gas limits across multiple temperatures ($0^\circ\text{C}, 5^\circ\text{C}, 10^\circ\text{C}, 20^\circ\text{C}$) for temperate horticultural produce.
- **Known Limitations:**
  - Respiration rates are reported as experimental ranges $[\min, \max]$; requires explicit maintenance of bounds.
  - Subtropical/tropical fruits and specialized Indian cultivars are covered in `data/raw/postharvest/india/`.
