# Raw Dataset: ICAR / IIFPT / NIFTEM Indian Postharvest Evidence

## 1. Source Identification & Primary Reference
- **Source Name:** ICAR / IIFPT / NIFTEM Indian Agricultural & Postharvest Database
- **Institutional Authorities:**
  - Indian Council of Agricultural Research (ICAR - CIAE Bhopal, CIPHET Ludhiana)
  - National Institute of Food Technology Entrepreneurship and Management (NIFTEM - IIFPT Thanjavur)
  - ICMR - National Institute of Nutrition (NIN Hyderabad)
- **Primary Peer-Reviewed References:**
  - Kudachikar et al. (2001). *Effect of MAP on quality of Alphonso mango*. Journal of Food Science and Technology India, 38(4): 355-359.
  - Jha et al. (2010). *Physico-chemical quality parameters of mangoes stored in modified atmosphere*. Postharvest Biology and Technology, 57(2): 108-113.
  - Nath et al. (2012). *Postharvest quality and shelf life extension of guava under MAP*. Journal of Food Science and Technology, 49(5): 583-591.
  - Sharma et al. (2019). *Modified atmosphere packaging of Paneer using barrier films*. Indian Journal of Agricultural Sciences, 89(7): 1120-1126.

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Version:** 2026 Indian Postharvest Evidence Ingestion Snapshot
- **Local Raw Files:** `icar_iifpt_indian_postharvest.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format
- **Key Fields:**
  - `commodity_id`: Unique identifier (`IND-POST-001` to `IND-POST-007`).
  - `commodity_name`: Standard English commodity name.
  - `indian_vernacular_name`: Vernacular Indian name (Hindi/Marathi/Gujarati/Telugu).
  - `scientific_name`: Botanical / Zoological binomial.
  - `origin_region`: Geographical production area in India (e.g. Ratnagiri, Gir, GI regions).
  - `processing_state`: `"raw"`, `"fresh_cut"`, `"processed"`.
  - `respiration_kinetics`: Array of observations across storage temperatures $T$ (12°C, 25°C) containing `co2_production_rate_min_mg_kg_h`, `co2_production_rate_max_mg_kg_h`, `respiratory_quotient_rq`.
  - `postharvest_storage_limits`: `optimum_temperature_c`, `chilling_injury_threshold_c`, `optimum_rh_percent`, `ambient_shelf_life_days`, `map_shelf_life_days`.
  - `emap_gas_tolerances`: Target $O_2\%$ and $CO_2\%$ ranges, fermentation limit ($O_2 < 2\%$), $CO_2$ injury threshold.
  - `map_packaging_requirements`: Dairy / Grains packaging specifications (MAP gas mixes, max allowable OTR/WVTR limits for Paneer and Basmati Rice).

## 4. Provenance & License Terms
- **License:** Open Academic / Research Reference (ICAR / NIFTEM Public Institutional Research Publications).
- **Evidence Priority Tier:** Tier 1 (Peer-Reviewed Primary Research Articles) & Tier 2 (Government Research Council Publications).
- **Source Operational Class:** Group A (Actual Data Source).

## 5. Scientific Scope & Known Limitations
- **Scope:** Mandatory first-class Indian evidence stream providing real experimental postharvest respiration rates, chilling injury limits, and MAP packaging shelf-life extensions for tropical Indian horticultural crops (Alphonso Mango, Kesar Mango, Guava, Okra, Papaya), dairy products (Paneer), and stored grains (Basmati Rice).
- **Known Limitations:** Respiration kinetics are specific to tropical temperature ranges (10°C to 25°C); requires explicit temperature matching with requirement conditions.
