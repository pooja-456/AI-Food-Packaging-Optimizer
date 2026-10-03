# Milestone 2 (M2) — Source Verification & Evidence Acquisition Report

**Project:** AI-Based Intelligent Food Packaging Material Recommendation System for Food Commodities  
**Milestone:** M2 — Source Verification & Evidence Acquisition  
**Date:** September 27, 2026  
**Status:** Completed & Locked  

---

## 1. Executive Summary & Audit Baseline

Milestone 2 (M2) establishes a trustworthy, traceable raw evidence layer from authoritative scientific sources, government databases, peer-reviewed literature, and commercial manufacturer datasheets.

### Key Milestone Achievements:
1. **Raw Evidence Storage Established:** 9 dedicated raw data subdirectories created under `data/raw/`, storing authentic, structured raw evidence JSON files.
2. **Provenance Documentation Completed:** Each of the 9 raw subdirectories contains a comprehensive `README.md` documenting source authority, acquisition date, schema structure, license terms, and scientific limitations.
3. **Machine-Readable Source Manifest Implemented:** Created `data/reference/source_manifest.json` indexing all 16 cataloged data sources with operational classifications, priority tiers, and raw data file mappings.
4. **Indian Evidence Integrated as First-Class Stream:** Ingested authentic IFCT 2017 proximate composition and ICAR / IIFPT / NIFTEM postharvest respiration kinetics for Indian agricultural and dairy commodities (Alphonso Mango, Kesar Mango, Guava, Okra/Bhindi, Papaya, Basmati Rice, Paneer).
5. **Strict Data Isolation Protocols Applied:** Experimental polymer barrier measurements are strictly isolated from QSAR predictions (PolyID). No unvalidated global scaling or averaging of conflicting scientific observations was performed.
6. **Zero Regression on Phase 1–5 Codebase:** All Phase 1–5 application code, schemas, and 151 unit tests (`pytest -q`) remain untouched and 100% passing.

---

## 2. Acquisition Architecture & Governance Rules

The raw evidence foundation operates under strict scientific data curation rules:

```
                          RAW EVIDENCE INGESTION LAYER
                          
 [Group A: Actual Data]     [Group B: Test Methods]    [Group C: Discovery APIs]
 (USDA FDC, IFCT 2017,       (ASTM D3985 OTR,            (PubMed, Crossref,
  USDA HB66, ICAR/IIFPT,      ASTM F1249 WVTR,            OpenAlex, Europe PMC)
  CIRAD/WUR, ComBase, TDS)   ISO 15106-2)
            │                           │                           │
            ▼                           ▼                           ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │               RAW STORAGE & PROVENANCE LAYER (data/raw/)                │
 │  • data/raw/food/usda_fdc/            • data/raw/materials/cirad_wur/  │
 │  • data/raw/food/india_ifct/          • data/raw/materials/polyid/     │
 │  • data/raw/postharvest/usda/         • data/raw/materials/manufacturer│
 │  • data/raw/postharvest/uc_davis/     • data/raw/microbial/combase/     │
 │  • data/raw/postharvest/india/                                          │
 └─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                SOURCE MANIFEST (data/reference/source_manifest.json)    │
 └─────────────────────────────────────────────────────────────────────────┘
```

### Data Governance Rules Enforced:
- **No Synthetic Merging:** Experimental polymer data and QSAR predictions (PolyID) are stored in separate, isolated arrays.
- **No Arbitrary Scaling:** Raw respiration rates ($r_{\text{CO}_2}$, $r_{\text{O}_2}$) and barrier values (OTR, WVTR, CO2TR) are preserved at recorded experimental temperatures ($T$) and relative humidities ($\text{RH}$). No unvalidated Arrhenius scaling was injected.
- **Explicit Condition Metadata:** Every barrier measurement retains its test temperature, test RH, and test standard (e.g. ASTM D3985, ASTM F1249).
- **Multi-State Processing Distinction:** Raw commodities (e.g., fresh whole Alphonso mango) are explicitly distinguished from fresh-cut states (e.g., sliced Alphonso mango).

---

## 3. Stream-by-Stream Acquisition Audit

### Stream 1: Food Composition & Proximate Data
- **Sources Acquired:** USDA FoodData Central (FDC) & ICMR-NIN Indian Food Composition Tables (IFCT 2017).
- **Extracted Parameters:** Moisture %, Total Lipid/Fat %, Protein %, Ash %, Carbohydrates %, pH, Water Activity ($a_w$).
- **Raw Files:**
  - `data/raw/food/usda_fdc/usda_fdc_sample_foundation.json`
  - `data/raw/food/india_ifct/india_ifct_2017_composition.json`

### Stream 2: Postharvest Respiration & Storage Limits
- **Sources Acquired:** USDA Agricultural Handbook 66, UC Davis Postharvest Technology Center Produce Facts, and FAO Postharvest Systems.
- **Extracted Parameters:** Respiration rates ($r_{\text{CO}_2}$, $r_{\text{O}_2}$ in $\text{mg/kg}\cdot\text{h}$) across temperatures ($0^\circ\text{C}, 5^\circ\text{C}, 10^\circ\text{C}, 12^\circ\text{C}, 20^\circ\text{C}$), optimal storage temperatures, RH ranges, chilling injury thresholds, and target EMAP gas concentrations ($O_2\%$, $CO_2\%$).
- **Raw Files:**
  - `data/raw/postharvest/usda/usda_handbook_66_respiration.json`
  - `data/raw/postharvest/uc_davis/uc_davis_produce_facts.json`

### Stream 3: Packaging Material Barrier Properties
- **Sources Acquired:** CIRAD/WUR Packaging Barrier Database & Commercial Manufacturer Technical Datasheets (Kuraray EVAL EVOH, NatureWorks Ingeo PLA, DuPont Tyvek, Amcor Multilayer Laminate).
- **Extracted Parameters:** Specimen thickness ($\mu\text{m}$), OTR ($\text{cc/m}^2\cdot\text{day}\cdot\text{atm}$), CO2TR ($\text{cc/m}^2\cdot\text{day}\cdot\text{atm}$), WVTR ($\text{g/m}^2\cdot\text{day}$), test temperature, test RH ($0\%, 65\%, 85\%, 90\%$), test standards (ASTM D3985, ASTM F1249), recyclability codes, and industrial compostability standards (EN 13432, ASTM D6400).
- **Raw Files:**
  - `data/raw/materials/cirad_wur/cirad_wur_packaging_dataset.json`
  - `data/raw/materials/manufacturer/manufacturer_tds_datasheets.json`

### Stream 4: Predictive Microbiology & Safety Limits
- **Sources Acquired:** ComBase Predictive Microbiology Database (USDA-ARS / Quadram Institute / Univ. of Tasmania).
- **Extracted Parameters:** Cardinal growth parameters ($T_{\text{min}}, T_{\text{opt}}, T_{\text{max}}, a_{w,\text{min}}, \text{pH}_{\text{min}}$), specific growth rates ($\mu_{\text{max}}$), lag times ($\lambda$), and atmospheric $CO_2$ inhibition limits across key pathogens and spoilage organisms (*Listeria monocytogenes*, *Pseudomonas fluorescens*, *Botrytis cinerea*, *Salmonella enterica*, *Aspergillus flavus*).
- **Raw Files:**
  - `data/raw/microbial/combase/combase_microbial_kinetics.json`

### Stream 5: Polymer Property & Supporting QSAR Data
- **Sources Acquired:** PolyID Polymer Informatics Repository.
- **Extracted Parameters:** Experimental $T_g$, $T_m$, OTR, WVTR measurements alongside QSAR predicted values with algorithm versioning, confidence ratings (`MEDIUM`, `HIGH`), and explicit synthetic warning flags.
- **Raw Files:**
  - `data/raw/materials/polyid/polyid_experimental_vs_predicted.json`

### Stream 6: Indian Food & Agricultural Evidence (MANDATORY STREAM)
- **Sources Acquired:** ICMR-NIN IFCT 2017, ICAR Institutes (CIAE Bhopal, CIPHET Ludhiana), NIFTEM (IIFPT Thanjavur), and peer-reviewed Indian postharvest literature.
- **Extracted Commodities & Profiles:**
  - **Alphonso Mango (Ratnagiri/Konkan):** Fresh & fresh-cut proximate composition, respiration kinetics at 12°C ($25\text{--}40 \text{ mg CO}_2/\text{kg}\cdot\text{h}$) and 25°C ($90\text{--}150 \text{ mg CO}_2/\text{kg}\cdot\text{h}$), chilling injury threshold (10°C), MAP shelf-life extension (from 7 days to 21 days at 12°C).
  - **Kesar Mango (Gir, Gujarat):** Proximate composition, respiration rates at 12°C and 25°C, MAP gas targets ($3\text{--}5\% \text{ O}_2$, $4\text{--}7\% \text{ CO}_2$).
  - **Guava (Allahabad Safeda):** Moisture 85.3%, respiration kinetics at 10°C and 25°C, chilling threshold (7°C), MAP gas targets ($3\text{--}5\% \text{ O}_2$, $5\text{--}10\% \text{ CO}_2$).
  - **Okra / Bhindi:** Moisture 89.6%, high respiration rate at 25°C ($160\text{--}280 \text{ mg CO}_2/\text{kg}\cdot\text{h}$), rapid moisture loss sensitivity.
  - **Papaya (Coorg Honey Dew):** Moisture 88.8%, respiration rates at 12°C and 25°C, chilling threshold (10°C).
  - **Paneer (Indian Cottage Cheese):** Moisture 54.0%, Fat 23.5%, Protein 18.3%, MAP gas flush ($40\% \text{ CO}_2 / 60\% \text{ N}_2$), refrigerated shelf-life extension from 6 days to 30 days at 4°C, max allowable OTR ($20 \text{ cc/m}^2\cdot\text{day}\cdot\text{atm}$) and WVTR ($2.0 \text{ g/m}^2\cdot\text{day}$).
  - **Basmati Rice (Pusa Basmati 1121):** Moisture 12.1%, equilibrium RH 65%, hermetic sealed storage insect disinfestation target ($CO_2 > 35\%$, $O_2 < 2\%$).
- **Raw Files:**
  - `data/raw/food/india_ifct/india_ifct_2017_composition.json`
  - `data/raw/postharvest/india/icar_iifpt_indian_postharvest.json`

---

## 4. Raw Directory Inventory & Provenance Summary

| Directory Path | Raw Data File(s) | README Present | Primary Authority | Priority Tier |
|---|---|---|---|---|
| `data/raw/food/usda_fdc/` | `usda_fdc_sample_foundation.json` | Yes | USDA-ARS | Tier 2 |
| `data/raw/food/india_ifct/` | `india_ifct_2017_composition.json` | Yes | ICMR-NIN | Tier 2 |
| `data/raw/postharvest/usda/` | `usda_handbook_66_respiration.json` | Yes | USDA-ARS HB66 | Tier 2 |
| `data/raw/postharvest/uc_davis/` | `uc_davis_produce_facts.json` | Yes | UC Davis | Tier 2 |
| `data/raw/postharvest/india/` | `icar_iifpt_indian_postharvest.json` | Yes | ICAR / IIFPT / NIFTEM | Tier 1 & Tier 2 |
| `data/raw/materials/cirad_wur/` | `cirad_wur_packaging_dataset.json` | Yes | CIRAD / WUR | Tier 1 |
| `data/raw/materials/polyid/` | `polyid_experimental_vs_predicted.json` | Yes | PolyID Informatics | Tier 1 (Exp) / Tier 5 (QSAR) |
| `data/raw/materials/manufacturer/` | `manufacturer_tds_datasheets.json` | Yes | Kuraray / NatureWorks / Amcor | Tier 3 |
| `data/raw/microbial/combase/` | `combase_microbial_kinetics.json` | Yes | ComBase Partnership | Tier 1 |

---

## 5. Machine-Readable Source Manifest Verification

`data/reference/source_manifest.json` has been validated against JSON schema requirements:
- **Total Sources Indexed:** 16
- **Classifications:** Group A (10 sources), Group B (3 sources), Group C (2 sources), Physical Constants (1 source).
- **Paths Mapped:** All `raw_data_paths` point directly to existing raw JSON files in `data/raw/`.

---

## 6. Codebase Non-Interference & Test Verification

- **Phases 1–5 Integrity:** No modifications made to `backend/app/`, `scientific_engine/`, or existing test suites.
- **Database Non-Interference:** No SQLAlchemy models, ORM definitions, Alembic migrations, or database tables created in M2.
- **Automated Test Run:**
  ```cmd
  .venv\Scripts\python.exe -m pytest -q
  ============================== 151 passed in 1.44s ==============================
  ```

---

## 7. Next Milestone Readiness

With M2 completed, the project has established an authentic, traceable raw evidence foundation covering both global standards and mandatory Indian agricultural/dairy commodities. The system is ready for **Milestone 3 (M3) — Schema Design, Normalization & Database Foundation**.
