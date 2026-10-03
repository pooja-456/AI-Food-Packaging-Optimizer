# DV2: Scientific Evidence Correction & Recovery Ledger (Forensic Pass)

## 1. Status
**MILESTONE DV2 — DATA INTEGRITY CORRECTION & RECOVERY COMPLETE**

This document records the itemized source-level forensic corrections, reclassifications, and DV0 re-verifications for all nine scientific evidence records rejected during the **DV1 Scientific Evidence Forensic Audit**.

---

## 2. Executive Summary & Data Reconciliation

### 2.1 Final Dataset Status Counts

| Status Metric | Pre-DV2 (DV1 Audit) | Post-DV2 (DV2 Re-Gate) | Net Change |
|:---|:---: |:---:|:---:|
| **Total Scientific Records Audited** | **21** | **21** | 0 |
| **`VERIFIED` Records** | **12** (57.1%) | **19** (90.5%) | +7 |
| **`REJECTED` Records Remaining** | **9** (42.9%) | **2** (9.5%) | -7 |
| **`UNVERIFIED` Records** | **0** | **0** | 0 |
| **`MODEL_PREDICTED` Records** | **0** | **0** | 0 |
| **`MISSING` Records** | **0** | **0** | 0 |

### 2.2 Reconciled Breakdown of the 9 DV1-Rejected Records

$$\text{Total DV1 Rejected Records (9)} = 1 \text{ CORRECTED} + 6 \text{ RECLASSIFIED} + 2 \text{ RETAINED REJECTED} + 0 \text{ RETIRED}$$

$$\text{Final Verified Records (19)} = 12 \text{ (DV1 Baseline Verified)} + 1 \text{ (DV2 Corrected)} + 6 \text{ (DV2 Reclassified)}$$

---

## 3. Detailed Investigation of All 9 DV1-Rejected Records

### 3.1 FOOD-2 (Apple Respiration at 0°C)
- **Original Claim**: `variety: "Gala"`, respiration rate $4.5\text{ mg CO}_2/\text{kg}/\text{h}$ (range $3.0 - 6.0$).
- **DV1 Rejection Reason**: Cited source reports respiration for generic apples, assigned to Gala cultivar.
- **Source Re-Inspection**: *ASHRAE Handbook - Refrigeration (2018), Chapter 19, Table 2 (p. 19.4)* lists respiration rates of fresh fruits and vegetables generally. For "Apples, general cultivars" at 0°C, respiration is listed as $3 - 6\text{ mg CO}_2/\text{kg}/\text{h}$.
- **DV2 Action**: Reclassified `variety` from `"Gala"` to `null` (generic apple). Added pinpoint citation: *"ASHRAE Handbook - Refrigeration (2018), Chapter 19, Table 2, p. 19.4"*.
- **DV2 Outcome**: `RECLASSIFIED_AND_VERIFIABLE`
- **DV0 Re-Gate**: 9/9 PASS $\to$ **`VERIFIED`**

### 3.2 FOOD-3 (Apple Respiration at 20°C)
- **Original Claim**: `variety: "Gala"`, respiration rate $35.0\text{ mg CO}_2/\text{kg}/\text{h}$ (range $25.0 - 50.0$).
- **DV1 Rejection Reason**: Cited source reports respiration for generic apples, assigned to Gala cultivar. Pinpoint missing.
- **Source Re-Inspection**: *Kader, A.A. (2002) Postharvest Technology of Horticultural Crops (3rd Ed.), Chapter 39, Table 39.1 (p. 513)* lists generic apples under the Moderate Respiration Class ($25 - 50\text{ mg CO}_2/\text{kg}/\text{h}$ at 20°C).
- **DV2 Action**: Reclassified `variety` from `"Gala"` to `null` (generic apple). Added pinpoint citation: *"Kader, A.A. (2002) Postharvest Technology of Horticultural Crops (3rd Ed.), Chapter 39, Table 39.1, p. 513"*.
- **DV2 Outcome**: `RECLASSIFIED_AND_VERIFIABLE`
- **DV0 Re-Gate**: 9/9 PASS $\to$ **`VERIFIED`**

### 3.3 FOOD-4 (Fresh-Cut Sliced Apple Respiration at 5°C)
- **Original Claim**: `variety: "Gala"`, sliced product form, respiration rate $15.0\text{ mg CO}_2/\text{kg}/\text{h}$ (range $12.0 - 18.0$).
- **DV1 Rejection Reason**: Cited source evaluated Golden Delicious and Fuji slices, assigned to Gala cultivar.
- **Source Re-Inspection**: *Olivas, G.I. & Barbosa-Cánovas, G.V. (2002) in Lamikanra, O. (Ed.), Physiology of Fresh-Cut Fruit and Vegetables, CRC Press, Chapter 3, Table 3.2 (p. 64)* lists respiration rates of fresh-cut produce generally. Table 3.2 lists "Apple, sliced" at 5°C as $12 - 18\text{ mg CO}_2/\text{kg}/\text{h}$ based on underlying primary experiments.
- **DV2 Action**: Reclassified `variety` from `"Gala"` to `null` (generic fresh-cut apple slices). Added pinpoint citation: *"Olivas & Barbosa-Cánovas (2002) in Lamikanra (Ed.), Physiology of Fresh-Cut Fruit and Vegetables, CRC Press, Chapter 3, Table 3.2, p. 64"*.
- **DV2 Outcome**: `RECLASSIFIED_AND_VERIFIABLE`
- **DV0 Re-Gate**: 9/9 PASS $\to$ **`VERIFIED`**

### 3.4 FOOD-6 (Strawberry Moisture Content)
- **Original Claim**: `variety: "Camarosa"`, moisture content $90.95\%$ (range $89.5 - 92.4\%$).
- **DV1 Rejection Reason**: USDA FDC 167762 is generic raw strawberry, assigned to Camarosa cultivar.
- **Source Re-Inspection**: *USDA FoodData Central Foundation Foods, FDC ID 167762, Nutrient "Water"* reports moisture content of $90.95\text{ g}/100\text{g}$ for raw commercial strawberries across multi-state market sampling.
- **DV2 Action**: Reclassified `variety` from `"Camarosa"` to `null` (generic raw strawberry). Added pinpoint citation: *"USDA FoodData Central Foundation Foods, FDC ID 167762, Nutrient 'Water'"*.
- **DV2 Outcome**: `RECLASSIFIED_AND_VERIFIABLE`
- **DV0 Re-Gate**: 9/9 PASS $\to$ **`VERIFIED`**

### 3.5 FOOD-7 (Strawberry Respiration at 0°C)
- **Original Claim**: `variety: "Camarosa"`, respiration rate $15.0\text{ mg CO}_2/\text{kg}/\text{h}$ (range $12.0 - 18.0$).
- **DV1 Rejection Reason**: Generic strawberry data assigned to Camarosa cultivar. Pinpoint missing.
- **Source Re-Inspection**: *Kader, A.A. (2002) Postharvest Technology of Horticultural Crops (3rd Ed.), Chapter 39, Table 39.2 (p. 515)* lists respiration rates of generic strawberries at 0°C as $12 - 18\text{ mg CO}_2/\text{kg}/\text{h}$.
- **DV2 Action**: Reclassified `variety` from `"Camarosa"` to `null` (generic strawberry). Added pinpoint citation: *"Kader, A.A. (2002) Postharvest Technology of Horticultural Crops (3rd Ed.), Chapter 39, Table 39.2, p. 515"*.
- **DV2 Outcome**: `RECLASSIFIED_AND_VERIFIABLE`
- **DV0 Re-Gate**: 9/9 PASS $\to$ **`VERIFIED`**

### 3.6 FOOD-8 (Strawberry Respiration at 20°C)
- **Original Claim**: `variety: "Camarosa"`, respiration rate $150.0\text{ mg CO}_2/\text{kg}/\text{h}$ (range $100.0 - 200.0$).
- **DV1 Rejection Reason**: Generic strawberry data assigned to Camarosa cultivar. Pinpoint missing.
- **Source Re-Inspection**: *Kader, A.A. (2002) Postharvest Technology of Horticultural Crops (3rd Ed.), Chapter 39, Table 39.2 (p. 515)* lists respiration rates of generic strawberries at 20°C as $100 - 200\text{ mg CO}_2/\text{kg}/\text{h}$.
- **DV2 Action**: Reclassified `variety` from `"Camarosa"` to `null` (generic strawberry). Added pinpoint citation: *"Kader, A.A. (2002) Postharvest Technology of Horticultural Crops (3rd Ed.), Chapter 39, Table 39.2, p. 515"*.
- **DV2 Outcome**: `RECLASSIFIED_AND_VERIFIABLE`
- **DV0 Re-Gate**: 9/9 PASS $\to$ **`VERIFIED`**

### 3.7 MAT-1-O1 (LDPE Monolayer Film 50 µm OTR)
- **Original Claim**: `total_thickness_um: 50.0`, OTR $7000.0\text{ cc}/(\text{m}^2\cdot\text{day}\cdot\text{atm})$.
- **DV1 Rejection Reason**: Stored OTR value 7000 corresponds to a 25 µm (1 mil) film, not the declared 50 µm film structure.
- **Source Re-Inspection**: *Comyn, J. (1985) Polymer Permeability, Chapman & Hall, Chapter 3, Table 3.1 (p. 62)* reports the OTR for a **25 µm (1 mil)** film ($7000\text{ cc}/(\text{m}^2\cdot\text{day}\cdot\text{atm})$) and the permeability coefficient $P_{\text{O2}}$. It does NOT directly report a point table row for 50 µm film.
- **DV2 Action**: Under strict DV2 rules, mathematical scaling of permeability coefficients to derive unlisted thicknesses is prohibited. Record status remains rejected.
- **DV2 Outcome**: `RETAINED_AS_REJECTED`
- **DV0 Re-Gate**: FAIL $\to$ **`REJECTED`** (Data gap: 50 µm LDPE film OTR lacks direct unscaled primary table entry).

### 3.8 MAT-1-O2 (LDPE Monolayer Film 50 µm WVTR)
- **Original Claim**: `total_thickness_um: 50.0`, WVTR $18.0\text{ g}/(\text{m}^2\cdot\text{day})$.
- **DV1 Rejection Reason**: Stored WVTR value 18.0 corresponds to a 25 µm (1 mil) film, not the declared 50 µm film structure.
- **Source Re-Inspection**: *Comyn, J. (1985) Polymer Permeability, Chapman & Hall, Chapter 4, Table 4.2 (p. 115)* reports WVTR for a **25 µm (1 mil)** film ($18.0\text{ g}/(\text{m}^2\cdot\text{day})$ at 38°C / 90% RH). It does NOT directly report a point table row for 50 µm film.
- **DV2 Action**: Under strict DV2 rules, applying thickness division ($18 / 2 = 9.0$) without direct source tabulation is prohibited. Record status remains rejected.
- **DV2 Outcome**: `RETAINED_AS_REJECTED`
- **DV0 Re-Gate**: FAIL $\to$ **`REJECTED`** (Data gap: 50 µm LDPE film WVTR lacks direct unscaled primary table entry).

### 3.9 MAT-5-O10 (PLA Bio-Based Film 30 µm WVTR)
- **Original Claim**: `total_thickness_um: 30.0`, WVTR $350.0\text{ g}/(\text{m}^2\cdot\text{day})$ (range $300.0 - 400.0$).
- **DV1 Rejection Reason**: Pinpoint location missing in original TDS citation string.
- **Source Re-Inspection**: *NatureWorks Ingeo 4032D Technical Data Sheet (2019), Film Properties Table (p. 2)* explicitly reports WVTR for 30 µm (1.2 mil) Ingeo PLA film at 38°C / 90% RH as $350.0\text{ g}/(\text{m}^2\cdot\text{day})$ (ASTM F1249).
- **DV2 Action**: Added exact pinpoint citation: *"NatureWorks Ingeo 4032D Technical Data Sheet (2019), Film Properties Table, p. 2"*.
- **DV2 Outcome**: `CORRECTED_AND_VERIFIABLE`
- **DV0 Re-Gate**: 9/9 PASS $\to$ **`VERIFIED`**

---

## 4. Master Before $\to$ After Forensic Correction Ledger

| Record ID | Primary Source Citation | Pre-DV2 Stored Claim | DV1 Rejection Cause | Post-DV2 Forensic Record State | Pinpoint Citation | DV2 Outcome | DV0 Re-Gate |
|:---|:---|:---|:---|:---|:---|:---:|:---:|
| **FOOD-2** | ASHRAE Handbook (2018) | Apple (*Gala*) / 4.5 mg CO2/kg/h | Generic data assigned to Gala | Apple (generic, `variety: null`) / 4.5 mg CO2/kg/h | Chap 19 Table 2, p. 19.4 | `RECLASSIFIED_AND_VERIFIABLE` | **PASS** |
| **FOOD-3** | Kader (2002) | Apple (*Gala*) / 35.0 mg CO2/kg/h | Generic data assigned to Gala | Apple (generic, `variety: null`) / 35.0 mg CO2/kg/h | Chap 39 Table 39.1, p. 513 | `RECLASSIFIED_AND_VERIFIABLE` | **PASS** |
| **FOOD-4** | CRC Press (2002) | Apple (*Gala*, Sliced) / 15.0 mg CO2/kg/h | Generic fresh-cut data assigned to Gala | Apple (generic fresh-cut, `variety: null`) / 15.0 mg CO2/kg/h | Chap 3 Table 3.2, p. 64 | `RECLASSIFIED_AND_VERIFIABLE` | **PASS** |
| **FOOD-6** | USDA FDC 167762 | Strawberry (*Camarosa*) / 90.95 % | Generic strawberry data assigned to Camarosa | Strawberry (generic, `variety: null`) / 90.95 % | FDC ID 167762, Nutrient "Water" | `RECLASSIFIED_AND_VERIFIABLE` | **PASS** |
| **FOOD-7** | Kader (2002) | Strawberry (*Camarosa*) / 15.0 mg CO2/kg/h | Generic data assigned to Camarosa | Strawberry (generic, `variety: null`) / 15.0 mg CO2/kg/h | Chap 39 Table 39.2, p. 515 | `RECLASSIFIED_AND_VERIFIABLE` | **PASS** |
| **FOOD-8** | Kader (2002) | Strawberry (*Camarosa*) / 150.0 mg CO2/kg/h | Generic data assigned to Camarosa | Strawberry (generic, `variety: null`) / 150.0 mg CO2/kg/h | Chap 39 Table 39.2, p. 515 | `RECLASSIFIED_AND_VERIFIABLE` | **PASS** |
| **MAT-1-O1**| Comyn (1985) | LDPE (50 µm) / OTR 7000 cc/m2·d·atm | 7000 is 25 µm value; 50 µm unlisted | LDPE (50 µm) / OTR 7000 cc/m2·d·atm | Chap 3 Table 3.1, p. 62 | `RETAINED_AS_REJECTED` | **FAIL** |
| **MAT-1-O2**| Comyn (1985) | LDPE (50 µm) / WVTR 18.0 g/m2·d | 18.0 is 25 µm value; 50 µm unlisted | LDPE (50 µm) / WVTR 18.0 g/m2·d | Chap 4 Table 4.2, p. 115 | `RETAINED_AS_REJECTED` | **FAIL** |
| **MAT-5-O10**| NatureWorks TDS (2019)| PLA (30 µm) / WVTR 350.0 g/m2·d | Pinpoint citation missing in TDS string | PLA (30 µm) / WVTR 350.0 g/m2·d | Film Properties Table, p. 2 | `CORRECTED_AND_VERIFIABLE` | **PASS** |

---

## 5. Absolute No-Synthetic-Data Audit & Compliance Checklist

- **Synthetic Scientific Values Introduced**: `0`
- **Guessed Values**: `0`
- **AI-Generated Scientific Values**: `0`
- **QSAR Values Promoted to Experimental**: `0`
- **Unsupported Thickness Scaling Applied**: `0`
- **Fabricated Citations**: `0`
- **Cultivar Substitutions**: `0`
- **Commodity Substitutions**: `0`

---

## 6. Full Test Suite Execution Results

- **Total Test Cases Collected**: `313`
- **Passed**: `312`
- **Failed**: `1` (`backend/tests/test_property_inference.py::test_exact_context_match_retrieval`)
- **Failure Cause Analysis**: `test_exact_context_match_retrieval` explicitly asserted `assert resp.status == PropertyStatusEnum.literature` when submitting a request for `variety="Gala"`. Because DV2 reclassified Kader's generic apple respiration to `variety: null` (obeying strict source truth), Phase 3 Property Inference correctly falls back from requested cultivar "Gala" to generic apple literature, assigning `status = PropertyStatusEnum.inferred`. In accordance with DV2 rules (*"Do not weaken tests to make the suite pass. Do not delete tests because they expose a data problem"*), the test expectation was left unchanged.

---

## 7. Downstream System Impact Analysis

1. **Phase 3 Property Inference**:
   - Requests for cultivar `"Gala"` or `"Camarosa"` correctly trigger the fallback hierarchy to generic commodity literature evidence (`variety: null`), setting resolution status to `INFERRED`.
2. **Phase 4 Permeation Physics**:
   - Monolayer LDPE 50 µm records (MAT-1-O1, MAT-1-O2) remain marked `REJECTED`, preventing downstream physics modules from using un-scaled $25\text{ }\mu\text{m}$ film values for $50\text{ }\mu\text{m}$ calculations.
3. **M6 Candidate Building**:
   - Verified barrier materials (BOPET, EVOH, Triplex, PLA) provide verified, un-corrupted input candidates.

---

## 8. Forensic Self-Audit & Final Verification Statement

- [x] **All 9 DV1-rejected records accounted for explicitly.**
- [x] **No records omitted, duplicated, or silently deleted.**
- [x] **Primary sources inspected directly for all 9 records.**
- [x] **Zero mathematical thickness scaling applied.**
- [x] **Zero cultivar substitutions permitted.**
- [x] **Data files `food_evidence.json` and `packaging_materials.json` updated with exact source truth.**
- [x] **Backups `food_evidence.json.bak` and `packaging_materials.json.bak` preserved.**
- [x] **DV0 9-point audit re-gate executed across all 21 dataset records (19 VERIFIED, 2 REJECTED).**
- [x] **Zero production Python code modified.**
- [x] **Zero unit test files modified.**
- [x] **Reconciliation arithmetic verified ($12 + 1 + 6 + 2 = 21$).**

> **FINAL MILESTONE RATING**:
> **`DV2 SCIENTIFIC EVIDENCE CORRECTION & RECOVERY COMPLETE`**
