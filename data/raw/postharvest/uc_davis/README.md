# Raw Dataset: UC Davis Postharvest Technology Center - Produce Facts

## 1. Source Identification & Primary Reference
- **Source Name:** UC Davis Postharvest Technology Center - Produce Facts Recommendations
- **Institutional Authority:** Department of Plant Sciences, University of California, Davis, USA.
- **Primary URL:** https://postharvest.ucdavis.edu/Commodity_Resources/Fact_Sheets/

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Version:** Produce Facts Recommendations Database
- **Local Raw Files:** `uc_davis_produce_facts.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format (derived from web factsheets)
- **Key Fields:**
  - `commodity_name`: Standard English name.
  - `scientific_name`: Botanical binomial name.
  - `respiration_profile`: Respiration rate ranges across temperatures $T$ (°C).
  - `physiological_limits`: `optimum_temperature_c`, `optimum_rh_percent`, `chilling_sensitivity`, `chilling_threshold_c`, `ethylene_sensitivity`, `emap_o2_min_percent`, `emap_o2_max_percent`, `emap_co2_min_percent`, `emap_co2_max_percent`, `co2_injury_threshold_percent`.

## 4. Provenance & License Terms
- **License:** University of California Educational / Scientific Research Use.
- **Evidence Priority Tier:** Tier 2 (University Research Center Reference).
- **Source Operational Class:** Group A (Actual Data Source).

## 5. Scientific Scope & Known Limitations
- **Scope:** Provides specialized chilling injury thresholds, ethylene sensitivity ratings, and EMAP optimal gas tolerances for fruits and vegetables.
- **Known Limitations:** Factsheets represent compiled extension recommendations; values are reported in physiological ranges.
