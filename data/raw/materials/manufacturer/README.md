# Raw Dataset: Commercial Polymer Manufacturer Technical Datasheets (TDS)

## 1. Source Identification & Primary Reference
- **Source Name:** Polymer Manufacturer Technical Datasheets (TDS)
- **Manufacturers Represented:**
  - Kuraray Co., Ltd. (EVAL EVOH Resins - https://www.evalevoh.com/)
  - NatureWorks LLC (Ingeo Biopolymers - https://www.natureworksllc.com/)
  - DuPont Specialty Products (https://www.dupont.com/)
  - Amcor Flexibles (https://www.amcor.com/)

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Version:** 2026 Commercial Datasheet Snapshot
- **Local Raw Files:** `manufacturer_tds_datasheets.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format
- **Key Fields:**
  - `datasheet_id`: Unique TDS identification code (e.g. `TDS-KURARAY-EVAL-F101B`).
  - `manufacturer`: Resin / Film manufacturing company.
  - `brand_grade`: Commercial grade name.
  - `polymer_type`: Chemical polymer class.
  - `ethylene_content_mol_percent`: Molar ethylene content for EVOH grades.
  - `structure_type`: `"monolayer"` or `"multilayer"`.
  - `nominal_thickness_um`: Specimen nominal thickness in micrometers ($\mu\text{m}$).
  - `layer_sequence`: Layer order string array for multilayer structures.
  - `barrier_profiles`: Array of barrier observations across test conditions ($T, \text{RH}$, test standard).
  - `sustainability_profile`: Recyclability, bio-based percentage, compostability certification standards (EN 13432, ASTM D6400).

## 4. Provenance & License Terms
- **License:** Publicly Distributed Manufacturer Technical Specifications.
- **Evidence Priority Tier:** Tier 3 (Manufacturer Technical Datasheet).
- **Source Operational Class:** Group A (Actual Data Source).

## 5. Scientific Scope & Known Limitations
- **Scope:** Gold-standard commercial performance values for specialized barrier polymers (EVOH 32 mol% and 44 mol%), bio-based compostable polymers (Ingeo PLA 4032D), and commercial MAP laminates (PET/EVOH/PE). Captures explicit RH dependence for hydrophilic EVOH barrier films across 0%, 65%, and 85% RH.
- **Known Limitations:** Manufacturer test data reflect standardized test coupons measured under laboratory conditions ($23^\circ\text{C}$ or $38^\circ\text{C}$).
