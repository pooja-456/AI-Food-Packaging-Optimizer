# Raw Dataset: ComBase Predictive Microbiology Database

## 1. Source Identification & Primary Reference
- **Source Name:** ComBase Predictive Microbiology Database
- **Institutional Authorities:**
  - USDA Agricultural Research Service (USDA-ARS, USA)
  - Quadram Institute Bioscience (UK)
  - University of Tasmania (Australia)
- **Primary URL:** https://www.combase.cc/

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Version:** ComBase Online Knowledge Base Ingestion Snapshot
- **Local Raw Files:** `combase_microbial_kinetics.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format
- **Key Fields:**
  - `combase_id`: Unique ComBase record ID (e.g. `CB-ORG-001`).
  - `organism_name`: Binomial microbiological name.
  - `organism_type`: Functional classification (`Psychrotrophic Pathogenic Bacteria`, `Spoilage Mold`, etc.).
  - `cardinal_parameters`: Object containing $T_{\text{min}}, T_{\text{opt}}, T_{\text{max}}, a_{w,\text{min}}, \text{pH}_{\text{min}}, \text{pH}_{\text{opt}}, \text{pH}_{\text{max}}$.
  - `growth_kinetics`: Array of observations (`temperature_c`, `ph`, `water_activity_aw`, `specific_growth_rate_mu_max_1_h`, `lag_time_lambda_h`, `atmosphere`).
  - `gas_inhibition_responses`: `co2_sensitivity`, `minimum_co2_inhibition_percent`, inhibition notes.

## 4. Provenance & License Terms
- **License:** ComBase Partnership Open Educational/Research Data (Free re-use for academic and research modeling with attribution).
- **Evidence Priority Tier:** Tier 1 / Tier 2 (Validated International Database).
- **Source Operational Class:** Group A (Actual Data Source).

## 5. Scientific Scope & Known Limitations
- **Scope:** Defines quantitative microbial growth cardinal boundaries ($T_{\text{min}}, a_{w,\text{min}}, \text{pH}_{\text{min}}$) and kinetic rates ($\mu_{\text{max}}, \lambda$) for food safety and shelf-life modeling under packaging headspace atmospheres.
- **Known Limitations:** Kinetic parameters depend on substrate matrix; values represent laboratory broth or benchmark food matrix observations.
