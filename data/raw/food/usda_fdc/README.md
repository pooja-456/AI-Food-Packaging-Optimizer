# Raw Dataset: USDA FoodData Central (FDC)

## 1. Source Identification & Primary Reference
- **Source Name:** USDA FoodData Central (FDC)
- **Institutional Authority:** United States Department of Agriculture (USDA) - Agricultural Research Service (ARS)
- **Primary URL:** https://fdc.nal.usda.gov/
- **Bulk Download Portal:** https://fdc.nal.usda.gov/download-datasets.html

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Snapshot Version:** FDC April 2026 Release / SR Legacy & Foundation Foods
- **Local Raw Files:** `usda_fdc_sample_foundation.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format (derived from official USDA CSV/JSON exports)
- **Key Fields:**
  - `fdc_id`: Unique USDA FoodData Central ID integer.
  - `commodity_name`: Common English commodity name string.
  - `scientific_name`: Botanical / Zoological taxonomic binomial string.
  - `food_category`: Broad USDA food group.
  - `processing_state`: Commercial processing state (`"raw"`, `"fresh_cut"`, `"processed"`).
  - `proximate_composition`: Object containing percentage composition for `moisture_percent`, `total_lipid_fat_percent`, `protein_percent`, `ash_percent`, `carbohydrate_by_difference_percent`.
  - `physicochemical_properties`: `ph_typical`, `water_activity_aw`.

## 4. Provenance & License Terms
- **License:** US Government Public Domain (CC0 Equivalent). Free for commercial and non-commercial re-use with citation.
- **Evidence Priority Tier:** Tier 2 (Authoritative Government Scientific Database).
- **Source Operational Class:** Group A (Actual Data Source).

## 5. Scientific Scope & Known Limitations
- **Scope:** Provides gold-standard, laboratory-analyzed proximate nutrient composition (moisture, lipid, protein, ash) across agricultural commodities.
- **Known Limitations:**
  - Does NOT contain postharvest respiration rates ($r_{\text{CO}_2}$, $r_{\text{O}_2}$).
  - Does NOT contain dynamic moisture sorption isotherms ($a_w$ vs moisture content curves).
  - Does NOT contain target equilibrium packaging atmosphere requirements ($O_2\%$, $CO_2\%$).
  - Concentrates primarily on US/North American cultivars; Indian regional cultivars (e.g., Alphonso mango, Desi guava) are covered in `data/raw/food/india_ifct/`.
