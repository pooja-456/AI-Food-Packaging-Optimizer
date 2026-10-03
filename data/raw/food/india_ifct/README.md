# Raw Dataset: Indian Food Composition Tables (IFCT 2017)

## 1. Source Identification & Primary Reference
- **Source Name:** Indian Food Composition Tables (IFCT 2017)
- **Institutional Authority:** ICMR - National Institute of Nutrition (NIN), Indian Council of Medical Research, Department of Health Research, Ministry of Health and Family Welfare, Government of India, Hyderabad, Telangana.
- **Primary URL:** https://www.ifct2017.com/
- **Institutional URL:** https://www.nin.res.in/

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Version:** IFCT 2017 Publication Edition
- **Local Raw Files:** `india_ifct_2017_composition.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format (derived from official IFCT 2017 database)
- **Key Fields:**
  - `ifct_code`: Official IFCT 4-character alphanumeric identification code (e.g., `A005`).
  - `commodity_name`: Standard English name for Indian agricultural/dairy commodity.
  - `indian_name`: Vernacular Indian language name (Hindi/Marathi/Gujarati/Telugu).
  - `scientific_name`: Botanical binomial name.
  - `food_category`: IFCT primary food classification.
  - `processing_state`: `"raw"`, `"fresh_cut"`, or `"processed"`.
  - `origin_region`: Geographic production / GI region in India.
  - `proximate_composition`: Nutrient breakdown (`moisture_percent`, `total_lipid_fat_percent`, `protein_percent`, `ash_percent`, `carbohydrate_by_difference_percent`, `total_sugars_percent`, `fiber_dietary_percent`).
  - `physicochemical_properties`: `ph_typical`, `titratable_acidity_percent`, `water_activity_aw`.

## 4. Provenance & License Terms
- **License:** ICMR-NIN Institutional Copyright. Academic, scientific research, and educational reference re-use.
- **Evidence Priority Tier:** Tier 2 (Authoritative Government National Database).
- **Source Operational Class:** Group A (Actual Data Source).

## 5. Scientific Scope & Known Limitations
- **Scope:** Provides precise laboratory-analyzed composition data for 528 key Indian food items, including regional Indian fruit cultivars (Alphonso Mango, Kesar Mango, Guava, Papaya), indigenous vegetables (Okra / Bhindi), cereals (Basmati Rice), and traditional dairy products (Paneer).
- **Known Limitations:**
  - Provides static proximate compositions; does NOT contain respiration kinetics ($r_{\text{CO}_2}$, $r_{\text{O}_2}$).
  - Postharvest storage gas tolerances and shelf-life data for Indian commodities are sourced separately in `data/raw/postharvest/india/`.
