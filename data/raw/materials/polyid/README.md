# Raw Dataset: PolyID Polymer Property Database (Experimental vs. Predicted)

## 1. Source Identification & Primary Reference
- **Source Name:** PolyID Polymer Property Database & QSAR Prediction Repository
- **Institutional Authority:** PolyID Informatics Research Group
- **Primary URL:** https://polyid.org/

## 2. Acquisition Metadata
- **Acquisition Date:** September 25, 2026
- **Dataset Version:** PolyID v2.4 Release
- **Local Raw Files:** `polyid_experimental_vs_predicted.json`

## 3. Data Format & Schema Structure
- **Format:** JSON format with strict isolation between `experimental_observations` and `predicted_values`.
- **Key Fields in `experimental_observations`:**
  - `polyid_exp_id`: Unique physical measurement ID.
  - `polymer_name`, `polymer_smiles`, `measured_thickness_um`, `density_g_cm3`, `glass_transition_temp_tg_c`, `melting_temp_tm_c`.
  - `experimental_otr`, `experimental_wvtr`: Measurement object with value, unit, test temperature, test RH, test standard, and laboratory reference.
- **Key Fields in `predicted_values`:**
  - `polyid_pred_id`: Unique model prediction ID.
  - `polymer_name`, `predicted_property`, `predicted_value`, `unit`, `reference_thickness_um`.
  - `prediction_confidence`, `uncertainty_range_lower`, `uncertainty_range_upper`, `qsar_algorithm`, `model_training_r2`, `warning_flag`.

## 4. Provenance & License Terms
- **License:** Research License / Creative Commons CC BY 4.0.
- **Evidence Priority Tier:**
  - `experimental_observations`: Tier 1 (Direct Experimental Evidence).
  - `predicted_values`: Tier 5 / Model Output (Informational QSAR Estimate).
- **Source Operational Class:** Group A (Actual Data Source - split into experimental vs computational).

## 5. Governance & Data Isolation Rules
- **STRICT ISOLATION RULE:** QSAR model predictions MUST NEVER be merged, averaged, or mixed with physical experimental observations.
- Physical barrier screening in Phase 5 utilizes experimental data. Predicted QSAR values carry explicit `prediction_confidence` ratings and `warning_flag` annotations.
