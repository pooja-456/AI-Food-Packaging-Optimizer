# Data Collection & Evidence Source Catalog

**Project:** AI-Based Intelligent Food Packaging Material Recommendation System  
**Milestone:** M1 Data Audit & Source Catalog  
**Status:** Audit & Source Design Only (No Data Collection or DB Implementation Executed in M1)

---

## 1. Source Priority Hierarchy

Evidence ingested by the system follows a strict 5-tier priority hierarchy:

- **Tier 1: Direct Experimental Evidence / Validated Datasets**  
  Peer-reviewed primary research articles containing direct experimental measurements with recorded test standards, temperature, and RH.
- **Tier 2: Government & Authoritative Scientific Databases**  
  Institutional reference resources (USDA FoodData Central, ComBase, USDA Handbook 66, NIST WebBook).
- **Tier 3: Manufacturer Technical Datasheets (TDS)**  
  Official polymer manufacturer datasheets (Kuraray EVAL, NatureWorks Ingeo, Dupont, Sabic) reporting standardized ASTM/ISO barrier measurements.
- **Tier 4: Standards & Test Methods**  
  Standardized measurement protocols (ASTM D3985, ASTM F1249, ISO 15106-2). *Note: Standards define testing protocols, not numerical barrier datasets.*
- **Tier 5: Reviews & Secondary Literature**  
  Compilations, review articles, and secondary handbooks.

> **Discovery Engines Note:** Search APIs (PubMed, Crossref, OpenAlex, Europe PMC) serve solely as **Discovery Sources** to locate primary literature; they are not underlying evidence data points.

---

## 2. Source Classification Framework

Sources are categorized into three operational classes:

1. **Group A: Actual Data Sources** — Provide direct quantitative observations (food composition, respiration rates, polymer transmission rates).
2. **Group B: Test-Method Sources** — Define standard experimental procedures and measurement methods.
3. **Group C: Discovery Sources** — Enable automated indexing and API retrieval of peer-reviewed publications.

---

## 3. Data Source Catalog

### A. Food Composition & Proximate Data

#### 1. USDA FoodData Central (FDC)
- **Official URL:** [https://fdc.nal.usda.gov/](https://fdc.nal.usda.gov/)
- **Bulk Data Download URL:** [https://fdc.nal.usda.gov/download-datasets.html](https://fdc.nal.usda.gov/download-datasets.html)
- **Data Type:** Foundation Foods, SR Legacy Nutrients (Moisture %, Total Lipids/Fat %, Protein %, Ash %).
- **What We Will Extract:** `commodity`, `variety`, `moisture_content` (%), `fat_content` (%), `processing_state` (`"raw"`, `"fresh_cut"`).
- **Why Relevant:** Provides gold-standard, government-validated proximate composition necessary for initial water content and lipid oxidation risk assessment.
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 2 (Government Database)
- **Expected Evidence Strength:** `high`
- **Important Limitations:** Does not provide respiration rates, water activity ($a_w$), or critical moisture limits.
- **Verification Status:** `AVAILABLE DATA` (Currently used in reference dataset for apple, strawberry, salmon).

---

### B. Postharvest Respiration & Storage Conditions

#### 2. USDA Agricultural Handbook 66 (Commercial Storage of Fruits, Vegetables, and Florist and Nursery Stocks)
- **Official URL:** [https://www.ars.usda.gov/is/np/CommercialStorage/CommercialStorage.pdf](https://www.ars.usda.gov/is/np/CommercialStorage/CommercialStorage.pdf)
- **Data Type:** Postharvest respiration rates ($r_{\text{CO}_2}$, $r_{\text{O}_2}$), recommended storage temperature ranges, relative humidity requirements, ethylene production.
- **What We Will Extract:** `commodity`, `respiration_rate` ($\text{mg CO}_2/\text{kg/hr}$), `storage_temperature_c`, `relative_humidity_percent`, `target_o2_percent`, `target_co2_percent`.
- **Why Relevant:** Authoritative source for respiration rates across multiple temperatures ($0^\circ\text{C}, 5^\circ\text{C}, 10^\circ\text{C}, 20^\circ\text{C}$) and optimal EMAP gas tolerances.
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 2 (Authoritative Government Handbook)
- **Expected Evidence Strength:** `high`
- **Important Limitations:** Respiration is reported in broad ranges; requires parsing into uncertainty bounds $[\min, \max]$.
- **Verification Status:** `AVAILABLE DATA` (Currently used in reference dataset for apple, strawberry).

#### 3. UC Davis Postharvest Technology Center — Produce Facts
- **Official URL:** [https://postharvest.ucdavis.edu/Commodity_Resources/Fact_Sheets/](https://postharvest.ucdavis.edu/Commodity_Resources/Fact_Sheets/)
- **Data Type:** Commodity-specific postharvest physiological profiles, optimal storage conditions, respiration rates, sensitivity to $CO_2$ and $O_2$.
- **What We Will Extract:** Commodity respiration ranges, chilling injury thresholds, optimum gas concentrations ($O_2\%$, $CO_2\%$).
- **Why Relevant:** Comprehensive postharvest factsheets covering a wide spectrum of fruits and vegetables.
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 2 (University Research Center)
- **Expected Evidence Strength:** `high`
- **Important Limitations:** Unstructured web pages; requires semi-automated extraction during M2.
- **Verification Status:** `Requires source-level verification during M2.`

#### 4. FAO Postharvest Compendium & Systems (Food and Agriculture Organization)
- **Official URL:** [https://www.fao.org/post-harvest-compendium/en/](https://www.fao.org/post-harvest-compendium/en/)
- **Data Type:** Postharvest losses, tropical commodity storage profiles, traditional and commercial packaging conditions.
- **What We Will Extract:** Storage life estimates, ambient storage temperature/RH profiles for tropical/subtropical commodities.
- **Why Relevant:** Provides international postharvest data for commodities grown in developing regions.
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 2 (International Organization)
- **Expected Evidence Strength:** `medium`
- **Important Limitations:** Qualitative storage guidelines; quantitative respiration rates are sparse.
- **Verification Status:** `Requires source-level verification during M2.`

---

### C. Predictive Microbiology & Safety Limits

#### 5. ComBase (USDA-ARS / Quadram Institute / University of Tasmania)
- **Official URL:** [https://www.combase.cc/](https://www.combase.cc/)
- **Data Type:** Quantitative microbial growth & survival kinetics ($N_0$, $\mu_{\text{max}}$, lag time $\lambda$, cardinal growth temperatures $T_{\text{min}}, T_{\text{opt}}, T_{\text{max}}$, $\text{pH}_{\text{min}}$, $a_{w,\text{min}}$).
- **What We Will Extract:** `target_microorganism` (*Listeria monocytogenes*, *Salmonella*, *Pseudomonas*, *Botrytis cinerea*), specific growth rate ($\mu_{\text{max}}$), lag time ($\lambda$), temperature/pH/$a_w$ growth boundaries.
- **Why Relevant:** Primary international repository for predictive food microbiology; directly feeds `MicrobialGrowthModel` (Baranyi & Ratkowsky models).
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 1 / Tier 2 (Validated International Database)
- **Expected Evidence Strength:** `high`
- **Important Limitations:** Requires ComBase API access or browser session query during M2 ingestion.
- **Verification Status:** `Requires source-level verification during M2.`

---

### D. Packaging Test Methods (Standard Protocols)

#### 6. ASTM D3985 — Standard Test Method for Oxygen Gas Transmission Rate Through Plastic Film and Sheeting Using a Coulometric Sensor
- **Official URL:** [https://www.astm.org/d3985-17.html](https://www.astm.org/d3985-17.html)
- **Data Type:** Measurement protocol standard for OTR testing ($23^\circ\text{C}, 0\% \text{ RH}$ or controlled RH, $1\text{ atm}$ pure $O_2$).
- **What We Will Extract:** Standard name string (`"ASTM D3985"`), test condition baseline definition.
- **Why Relevant:** Standard test procedure referenced by material evidence records to confirm OTR validity.
- **Source Type:** Group B (Test-Method Source)
- **Source Priority:** Tier 4 (Standard Specification)
- **Expected Evidence Strength:** N/A (Method Definition)
- **Important Limitations:** Defines test method only; does **NOT** contain material barrier dataset values.
- **Verification Status:** `AVAILABLE DATA` (Referenced in reference packaging materials dataset).

#### 7. ASTM F1249 — Standard Test Method for Water Vapor Transmission Rate Through Plastic Film and Sheeting Using a Modulated Infrared Sensor
- **Official URL:** [https://www.astm.org/f1249-20.html](https://www.astm.org/f1249-20.html)
- **Data Type:** Measurement protocol standard for WVTR testing ($38^\circ\text{C}, 90\% \text{ RH}$).
- **What We Will Extract:** Standard name string (`"ASTM F1249"`), test condition baseline definition.
- **Why Relevant:** Standard test procedure referenced by material evidence records to confirm WVTR validity.
- **Source Type:** Group B (Test-Method Source)
- **Source Priority:** Tier 4 (Standard Specification)
- **Expected Evidence Strength:** N/A (Method Definition)
- **Important Limitations:** Defines test method only; does **NOT** contain material barrier dataset values.
- **Verification Status:** `AVAILABLE DATA` (Referenced in reference packaging materials dataset).

#### 8. ISO 15106-2 — Plastics — Film and sheeting — Determination of water vapour transmission rate — Part 2: Infrared detection sensor method
- **Official URL:** [https://www.iso.org/standard/43621.html](https://www.iso.org/standard/43621.html)
- **Data Type:** International measurement standard for WVTR testing.
- **What We Will Extract:** Standard name string (`"ISO 15106-2"`).
- **Why Relevant:** European/International equivalent to ASTM F1249 for global material specification compatibility.
- **Source Type:** Group B (Test-Method Source)
- **Source Priority:** Tier 4 (Standard Specification)
- **Expected Evidence Strength:** N/A (Method Definition)
- **Important Limitations:** Method definition only.
- **Verification Status:** `Requires source-level verification during M2.`

---

### E. Packaging Material Barrier Datasets & Datasheets

#### 9. Kuraray EVAL EVOH Technical Datasheets & Bulletins
- **Official URL:** [https://www.evalevoh.com/en/products-and-services/eval-resins/](https://www.evalevoh.com/en/products-and-services/eval-resins/)
- **Data Type:** Technical specifications for EVOH barrier resins (32, 38, 44 mol% ethylene grades), OTR vs relative humidity curves ($0\%, 65\%, 85\%, 90\% \text{ RH}$), temperature dependence.
- **What We Will Extract:** `material_name`, `structure_type`, OTR values at $0\%$ and $85\% \text{ RH}$, test temperature, test standard (`ASTM D3985`).
- **Why Relevant:** Essential for modeling moisture-sensitive gas barrier polymers.
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 3 (Manufacturer Technical Datasheet)
- **Expected Evidence Strength:** `high`
- **Important Limitations:** Manufacturer test conditions are standardized ($23^\circ\text{C}$); non-standard storage conditions require explicit cross-condition evidence flags.
- **Verification Status:** `AVAILABLE DATA` (Currently used in reference dataset for `MAT-EVOH-15UM`).

#### 10. NatureWorks Ingeo PLA Technical Data Sheets
- **Official URL:** [https://www.natureworksllc.com/Technical-Resources](https://www.natureworksllc.com/Technical-Resources)
- **Data Type:** Polylactic acid (PLA) film specifications, OTR, WVTR, density, industrial compostability standards (`ASTM D6400`, `EN 13432`).
- **What We Will Extract:** `material_name`, `total_thickness_um`, OTR, WVTR, compostability standard.
- **Why Relevant:** Representative bio-based, compostable monolayer polymer specification.
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 3 (Manufacturer Technical Datasheet)
- **Expected Evidence Strength:** `high`
- **Important Limitations:** Proprietary resin grades; values represent commercial film grades.
- **Verification Status:** `AVAILABLE DATA` (Currently used in reference dataset for `MAT-PLA-30UM`).

#### 11. Polymer Permeability Handbook & Literature Compendia (Comyn, J.; Pauly, S.; Massey, L.K.)
- **Official URL:** [https://www.sciencedirect.com/book/9781884207976/permeability-properties-of-plastics-and-elastomers](https://www.sciencedirect.com/book/9781884207976/permeability-properties-of-plastics-and-elastomers)
- **Data Type:** Permeability coefficients ($P$, $D$, $S$), OTR, WVTR, $\text{CO}_2\text{TR}$ for LDPE, LLDPE, HDPE, PP, PET, PA, PVC, PS, Aluminium foil.
- **What We Will Extract:** OTR, WVTR, $\text{CO}_2\text{TR}$ values, activation energies ($E_p$), specimen thicknesses.
- **Why Relevant:** Primary source for baseline polymer permeability values and $\text{CO}_2\text{TR}$ data currently missing from simple datasheets.
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 1 / Tier 2 (Peer-Reviewed Reference Book)
- **Expected Evidence Strength:** `high`
- **Important Limitations:** Values presented as ranges; requires explicit extraction of test conditions ($T, \text{RH}$).
- **Verification Status:** `AVAILABLE DATA` (Currently used in reference dataset for `MAT-LDPE-50UM`, `MAT-BOPET-12UM`).

---

### F. Thermophysical Constants

#### 12. NIST Chemistry WebBook (National Institute of Standards and Technology)
- **Official URL:** [https://webbook.nist.gov/chemistry/](https://webbook.nist.gov/chemistry/)
- **Data Type:** Thermophysical property data for fluids and gases (water vapor saturation pressure, gas molar volumes, ideal gas constants).
- **What We Will Extract:** Pure water saturation vapor pressure constants, universal gas constant ($R = 8.314 \text{ J/mol}\cdot\text{K}$), molar masses ($M_{\text{O}_2} = 31.998 \text{ g/mol}$, $M_{\text{CO}_2} = 44.01 \text{ g/mol}$).
- **Why Relevant:** Provides gold-standard physical constants used by `MoistureTransferModel` and `RespirationKineticsModel`.
- **Source Type:** Group A (Actual Data Source)
- **Source Priority:** Tier 2 (Government Scientific Agency)
- **Expected Evidence Strength:** `high` (Fundamental Constants)
- **Important Limitations:** Provides pure physical constants, not food-specific degradation parameters.
- **Verification Status:** `AVAILABLE DATA` (Embedded in `scientific_engine/physics/base.py`).

---

### G. Scientific Literature Discovery Sources (APIs)

#### 13. PubMed / MEDLINE API (NCBI Entrez Utilities)
- **Official URL:** [https://pubmed.ncbi.nlm.nih.gov/](https://pubmed.ncbi.nlm.nih.gov/)
- **API Endpoint:** [https://eutils.ncbi.nlm.nih.gov/entrez/eutils/](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/)
- **Data Type:** Bibliographic metadata, abstracts, DOIs, PMIDs for food microbiology and postharvest research.
- **What We Will Extract:** Citation metadata (`source_title`, `publication_year`, `DOI`, `authors`).
- **Why Relevant:** Automated discovery of primary peer-reviewed literature for postharvest respiration and food safety.
- **Source Type:** Group C (Discovery Source)
- **Source Priority:** N/A (Search Engine / Indexing API)
- **Expected Evidence Strength:** N/A
- **Important Limitations:** Provides metadata and abstracts; full quantitative tables require PDF parsing or manual extraction.
- **Verification Status:** `Requires source-level verification during M2.`

#### 14. Crossref REST API
- **Official URL:** [https://www.crossref.org/](https://www.crossref.org/)
- **API Endpoint:** [https://api.crossref.org/works](https://api.crossref.org/works)
- **Data Type:** Bibliographic metadata, DOI resolution, journal titles, publisher metadata.
- **What We Will Extract:** Verified DOI resolution, publication titles, peer-review verification.
- **Why Relevant:** Ensures every ingested literature citation has a verified DOI and canonical citation string.
- **Source Type:** Group C (Discovery Source)
- **Source Priority:** N/A (Metadata API)
- **Expected Evidence Strength:** N/A
- **Important Limitations:** Bibliographic metadata only.
- **Verification Status:** `Requires source-level verification during M2.`

#### 15. OpenAlex API
- **Official URL:** [https://openalex.org/](https://openalex.org/)
- **API Endpoint:** [https://api.openalex.org/works](https://api.openalex.org/works)
- **Data Type:** Fully open scholarly catalog indexing 250M+ scientific papers, open access PDF links, citation counts.
- **What We Will Extract:** Open-access PDF URLs, topic taxonomy tags, peer-reviewed article metadata.
- **Why Relevant:** Fast, open API for indexing postharvest biology and polymer permeability papers.
- **Source Type:** Group C (Discovery Source)
- **Source Priority:** N/A (Scholarly Index)
- **Expected Evidence Strength:** N/A
- **Important Limitations:** Indexing API only.
- **Verification Status:** `Requires source-level verification during M2.`

#### 16. Europe PMC REST API
- **Official URL:** [https://europepmc.org/](https://europepmc.org/)
- **API Endpoint:** [https://europepmc.org/RestFulForm](https://europepmc.org/RestFulForm)
- **Data Type:** Full-text open-access article XML/JSON, biological entity annotations.
- **What We Will Extract:** Full-text scientific article text, structured tables of respiration and barrier data.
- **Why Relevant:** Provides open-access full-text articles for text mining food respiration and sorption tables.
- **Source Type:** Group C (Discovery Source)
- **Source Priority:** N/A (Full-Text Repository API)
- **Expected Evidence Strength:** N/A
- **Important Limitations:** Full-text availability restricted to open-access subset.
- **Verification Status:** `Requires source-level verification during M2.`

---

## 4. Verification Summary Table

| Source Name | Official URL | Source Type | Data Expected | Verification Status |
|---|---|---|---|---|
| **USDA FoodData Central** | `https://fdc.nal.usda.gov/` | Group A | Moisture %, Fat %, Protein %, pH | `AVAILABLE DATA` |
| **USDA Handbook 66** | `https://www.ars.usda.gov/is/np/CommercialStorage/` | Group A | Respiration rates, Storage T/RH, Gas tolerances | `AVAILABLE DATA` |
| **UC Davis Produce Facts** | `https://postharvest.ucdavis.edu/` | Group A | Postharvest factsheets, respiration ranges | `Requires verification in M2` |
| **FAO Postharvest Compendium** | `https://www.fao.org/post-harvest-compendium/en/` | Group A | Tropical storage life & postharvest guidelines | `Requires verification in M2` |
| **ComBase** | `https://www.combase.cc/` | Group A | Pathogen/spoilage kinetics ($N_0, \mu_{\text{max}}, T_{\text{min}}, a_{w,\text{min}}$) | `Requires verification in M2` |
| **ASTM D3985** | `https://www.astm.org/d3985-17.html` | Group B | OTR test method protocol definition | `AVAILABLE DATA` |
| **ASTM F1249** | `https://www.astm.org/f1249-20.html` | Group B | WVTR test method protocol definition | `AVAILABLE DATA` |
| **ISO 15106-2** | `https://www.iso.org/standard/43621.html` | Group B | Infrared WVTR test method protocol | `Requires verification in M2` |
| **Kuraray EVAL EVOH Datasheets** | `https://www.evalevoh.com/` | Group A | EVOH OTR vs RH ($0\%, 85\%$), thickness | `AVAILABLE DATA` |
| **NatureWorks Ingeo PLA TDS** | `https://www.natureworksllc.com/` | Group A | PLA OTR, WVTR, compostability standards | `AVAILABLE DATA` |
| **Polymer Permeability Handbook** | `https://www.sciencedirect.com/book/9781884207976/` | Group A | OTR, WVTR, $\text{CO}_2\text{TR}$ values, $E_p$ for polymers | `AVAILABLE DATA` |
| **NIST Chemistry WebBook** | `https://webbook.nist.gov/chemistry/` | Group A | Water saturation pressure $P_{\text{sat}}(T)$, gas constants | `AVAILABLE DATA` |
| **PubMed API** | `https://eutils.ncbi.nlm.nih.gov/` | Group C | Literature discovery, PMID/DOI resolution | `Requires verification in M2` |
| **Crossref API** | `https://api.crossref.org/` | Group C | DOI resolution, journal metadata | `Requires verification in M2` |
| **OpenAlex API** | `https://api.openalex.org/` | Group C | Open access PDF discovery, scholarly index | `Requires verification in M2` |
| **Europe PMC API** | `https://europepmc.org/` | Group C | Full-text article mining API | `Requires verification in M2` |

---

## 5. Explicit Execution Safeguard Statement

- **No external datasets were downloaded or scraped during M1.**
- **No production code, ORM models, database tables, or ETL pipelines were created.**
- **Phase 1 through Phase 5 code, schemas, and 151/151 tests remain untouched.**
