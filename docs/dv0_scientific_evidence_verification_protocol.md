# DV0: Scientific Evidence Verification Protocol

## 1. Status
**PROPOSED SCIENTIFIC EVIDENCE VERIFICATION PROTOCOL — AUDIT READY**

## 2. Scope & Purpose
This document establishes the formal **Scientific Evidence Verification Protocol** for the AI-Food-Packaging-Optimizer project.

The primary purpose of this protocol is to prevent incorrectly attributed, incorrectly transcribed, unconditioned, or unsupported scientific values from entering the system as verified real-world evidence.

Milestone DV0 is strictly a **DESIGN-ONLY SPECIFICATION**. In accordance with project governance:
- **No existing scientific data is modified.**
- **No data records are corrected during DV0.**
- **No new scientific values are added.**
- **No replacement values are searched for.**
- **No synthetic values are introduced as scientific evidence.**
- **No verification workflows are implemented in production code.**
- **No database schema, Python source code, or test files are altered.**

This protocol establishes the unalterable rules, taxonomy, verification gates, and record schemas that will govern the execution of the upcoming **DV1 Scientific Evidence Verification Audit**.

---

## 3. Core Project Principle: Real Scientific Evidence
The AI-Food-Packaging-Optimizer requires **REAL** scientific evidence to perform valid inverse-design optimization and shelf-life predictions.

To be classified as **REAL SCIENTIFIC EVIDENCE**, a database record MUST satisfy all of the following criteria:
1. **Identifiable Origin**: Originates from a verified, identifiable external scientific paper, government database, manufacturer technical datasheet, or institutional report.
2. **Exact Entity Attribution**: Is correctly attributed to the specific food commodity, cultivar/variety, product form, packaging polymer/structure, or microorganism strain.
3. **Accurate Transcription**: Is verified to match the numerical value reported in the original source text, table, or figure without silent truncation or arbitrary rounding.
4. **Complete Condition Context**: Is bound to its original experimental test conditions (temperature, relative humidity, test method, gas partial pressure, layer thickness).
5. **Dimensional & Unit Integrity**: Is expressed in valid, dimensionally consistent scientific units with traceable, recoverable conversion factors.
6. **Pinpoint Traceability**: Is traceable to a precise location (page, table, figure, section, or row ID) within the source document.
7. **Explicit Status Classification**: Is explicitly distinguished from model-predicted (e.g. QSAR) or synthetic test data.

A citation existing in a database record (e.g. presence of a DOI or URL string) **DOES NOT** constitute proof that the record is verified.

---

## 4. Source Authority & Lineage
This verification protocol traces its authority directly to established project architecture and data contracts:
- `docs/scientific_knowledge_foundation.md`
- `docs/m1_source_audit.md`
- `docs/m2_data_acquisition.md`
- `docs/m2_1_raw_data_architecture.md`
- `docs/m3_data_profiling.md`
- `docs/m4_data_cleaning_normalization_validation.md`
- `docs/m5a_canonical_data_model.md`
- `docs/m5b1_database_foundation.md`
- `docs/m5b2_canonical_schema.md`
- `docs/m5b3_controlled_data_ingestion.md`
- `backend/app/schemas/food_evidence.py`
- `backend/app/schemas/material_evidence.py`
- `backend/app/schemas/physics.py`
- `backend/app/schemas/packaging_requirements.py`
- `data/reference/food_evidence.json`
- `data/reference/packaging_materials.json`

---

## 5. Verification Status Taxonomy
Every scientific data record in the repository MUST be classified under exactly one of five formal verification statuses:

```
VERIFICATION STATUS TAXONOMY:
┌──────────────────┐  --> Record verified against original source (9/9 audit gate pass)
│     VERIFIED     │
└──────────────────┘
┌──────────────────┐  --> Record present with source citation, but unverified by human audit
│    UNVERIFIED    │
└──────────────────┘
┌──────────────────┐  --> Record audited and rejected due to transcription/entity mismatch
│     REJECTED     │
└──────────────────┘
┌──────────────────┐  --> Record derived from QSAR, empirical regression, or ML model
│ MODEL_PREDICTED  │
└──────────────────┘
┌──────────────────┐  --> Required scientific value absent from dataset
│     MISSING      │
└──────────────────┘
```

### 5.1 Formal Non-Equivalence Rules
The verification taxonomy enforces strict, unalterable non-equivalence boundaries:

$$\text{MODEL\_PREDICTED} \ne \text{VERIFIED}$$
$$\text{UNVERIFIED} \ne \text{VERIFIED}$$
$$\text{REJECTED} \ne \text{VERIFIED}$$
$$\text{MISSING} \ne \text{VERIFIED}$$

- **REQ-TAX-01**: `MODEL_PREDICTED` records (e.g., PolyID QSAR permeability predictions) MUST NOT be promoted to `VERIFIED`.
- **REQ-TAX-02**: `UNVERIFIED` records MUST NOT be treated as `VERIFIED` merely because they pass structural Pydantic validation or schema checks.
- **REQ-TAX-03**: `REJECTED` records MUST NOT be included in scientific physics calculations or candidate feasibility evaluations.

---

## 6. The 9-Point Verification Audit Gate
To achieve `VERIFIED` status, a data record MUST independently pass all nine dimensions of the **9-Point Verification Audit Gate** against the original source document:

```
                          9-POINT AUDIT GATE
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. Entity Identity Check     (Commodity/Material/Strain)   │
  │ 2. Property Identity Check   (Respiration/OTR/WVTR/aw)     │
  │ 3. Value Match Check         (Scalar/Range/Min/Max)        │
  │ 4. Unit & Dimensional Check  (Original & Transformed Unit)  │
  │ 5. Condition Context Check   (Temp, RH, Test Method, Gas)  │
  │ 6. Form & Maturity Check     (Whole/Cut, Ripeness, Structure)│
  │ 7. Source Attribution Check  (Citation reflects source)    │
  │ 8. Pinpoint Location Check   (Table/Figure/Page/Row)       │
  │ 9. Status Classification Check (Experimental vs Predicted)  │
  └─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                     ALL 9 PASS? ──► YES ──► VERIFIED
                                 │
                                NO
                                 ▼
                      UNVERIFIED / REJECTED
```

- **REQ-GATE-01**: Passing 8 out of 9 audit dimensions **CANNOT** produce `VERIFIED`. All 9 dimensions are mandatory.
- **REQ-GATE-02**: Verification MUST be performed against the primary original document (PDF, official database record, TDS) whenever accessible.

---

## 7. Entity Verification Rules
Entity identity verifies that the scientific value in the database concerns the exact physical entity reported in the source.

### 7.1 Food Commodity & Cultivar Boundaries
- **REQ-ENT-01 (Cultivar Boundaries)**: A measurement reported for one cultivar (e.g. *Tommy Atkins* mango) **MUST NOT** be automatically assigned to another cultivar (e.g. *Alphonso* mango).
- **REQ-ENT-02 (Generic vs Specific)**: A value reported for a generic commodity (e.g. "fresh apple") **MUST NOT** be assigned to a specific cultivar (e.g. "Gala apple") without explicit source authority.
- **REQ-ENT-03 (Product Form & Processing)**: Values reported for "fresh-cut / sliced" produce **MUST NOT** be assigned to "whole" produce, and vice-versa.

### 7.2 Packaging Material & Structure Boundaries
- **REQ-ENT-04 (Polymer & Structure Boundaries)**: A barrier measurement reported for oriented polypropylene (OPP) **MUST NOT** be assigned to cast polypropylene (CPP) or generic PP.
- **REQ-ENT-05 (Laminate & Layer Identification)**: Barrier observations for multi-layer structures MUST explicitly match the layer ordering, thickness, and material composition reported in the source.

### 7.3 Microorganism Strain Boundaries
- **REQ-ENT-06 (Microbial Strain Boundaries)**: Growth kinetics for a specific microbial strain (e.g. *Listeria monocytogenes* strain Scott A) **MUST NOT** be assumed identical across all strains of that species.

---

## 8. Property Verification Rules
Property identity verifies that the database property field accurately reflects the physical quantity measured in the source.

- **REQ-PROP-01 (No Implicit Property Inference)**: A source discussing a related property (e.g. weight loss) **MUST NOT** be used to infer an unmeasured property (e.g. oxygen transmission rate) without an authorized physics model.
- **REQ-PROP-02 (Prohibition of Qualitative-to-Quantitative Conversion)**: Qualitative statements in scientific text (e.g. "low oxygen permeability", "rapid respiration", "high shelf-life") **MUST NOT** be converted into arbitrary quantitative numbers.
- **REQ-PROP-03 (Property Name Standardization)**: Property names MUST conform to authorized schema enumerations (e.g. `respiration_rate_co2`, `oxygen_transmission_rate`, `water_vapor_transmission_rate`).

---

## 9. Value Verification & Transcription Rules
Value verification compares the database numerical value against the exact text, table, or figure in the original source.

- **REQ-VAL-01 (Preservation of Value Types)**:
  - **Point Estimates / Means**: Must match reported mean or point estimate.
  - **Ranges**: Min/max ranges reported in sources MUST be preserved as ranges and **MUST NOT** be averaged into single point estimates.
  - **Inequalities**: Bounds expressed as $< X$ or $> Y$ MUST retain their inequality operators.
- **REQ-VAL-02 (Prohibition of Silent Rounding)**: Database values **MUST NOT** be rounded during verification unless the source itself reports the rounded number.
- **REQ-VAL-03 (Figure-Derived Data Identification)**: Values digitized from graphs or figures MUST be explicitly tagged with `measurement_method = "digitized_figure"` and assigned appropriate uncertainty bounds.
- **REQ-VAL-04 (Mismatch Handling)**: If a database value differs materially from the original source text (beyond standard floating-point representation), the record MUST be marked `UNVERIFIED` (if citation is ambiguous) or `REJECTED` (if transcription error is confirmed).

---

## 10. Unit & Dimensional Verification Rules
Unit verification ensures dimensional consistency and transparent, recoverable unit conversions.

- **REQ-UNIT-01 (Original Unit Preservation)**: The original unit reported in the source MUST be recorded alongside the database normalized unit.
- **REQ-UNIT-02 (Recoverability of Conversions)**: Any unit conversion applied during data ingestion MUST be documented with its exact conversion factor and mathematical formula.
- **REQ-UNIT-03 (Respiration Gas Species Integrity)**: Respiration rate measurements MUST explicitly identify the target gas species:
  - $\text{mg CO}_2 \cdot \text{kg}^{-1} \cdot \text{h}^{-1}$ (Carbon dioxide evolution rate)
  - $\text{mg O}_2 \cdot \text{kg}^{-1} \cdot \text{h}^{-1}$ (Oxygen consumption rate)
  - $\text{mmol CO}_2 \cdot \text{kg}^{-1} \cdot \text{h}^{-1}$
  - $\text{mL CO}_2 \cdot \text{kg}^{-1} \cdot \text{h}^{-1}$
  
  Silent conversion between $\text{CO}_2$ evolution and $\text{O}_2$ consumption without a verified Respiratory Quotient (RQ) is **STRICTLY PROHIBITED**.

---

## 11. Condition Verification Rules
Condition verification ensures that environmental and experimental test conditions are fully captured.

### 11.1 Food Evidence Conditions
Food evidence records MUST verify and record:
- Temperature ($^\circ\text{C}$)
- Relative Humidity ($\%$)
- Storage atmosphere ($\% \text{ O}_2, \% \text{ CO}_2, \% \text{ N}_2$)
- Commodity state (whole, fresh-cut, peeled, crushed)
- Maturity / Ripeness stage
- Storage duration (days)

### 11.2 Packaging Material Conditions
Packaging material evidence records MUST verify and record:
- Test temperature ($^\circ\text{C}$)
- Test relative humidity ($\% \text{ RH}$)
- Test gas partial pressure / gradient ($\text{atm}$ / $\text{kPa}$)
- Film thickness ($\mu\text{m}$ / $\text{mil}$)
- Standard test method (e.g. ASTM D3985 for OTR, ASTM E96 for WVTR, ISO 15105)

### 11.3 Microbial Kinetics Conditions
Microbial kinetics records MUST verify and record:
- Temperature ($^\circ\text{C}$)
- pH
- Water activity ($a_w$)
- Atmosphere ($\% \text{ O}_2, \% \text{ CO}_2$)
- Growth medium / food matrix

Unconditioned values (e.g., OTR reported without test temperature or RH) **MUST NOT** be marked `VERIFIED` if the missing condition materially affects physics modeling.

---

## 12. Source Attribution & Pinpoint Citation Standard
Source attribution requires verifying that the cited document actually contains the reported scientific claim.

### 12.1 Attribution Principles
- **REQ-ATTR-01**: The presence of a citation string in a database row is NOT evidence of attribution. The document MUST be inspected to confirm the value exists within it.
- **REQ-ATTR-02**: Review papers or meta-analyses cited as sources MUST be audited to determine whether they report primary measurements or reference earlier literature.

### 12.2 Pinpoint Citation Specification
Where structural page/table organization exists in the source, verification records MUST include a **Pinpoint Citation**:

```
PINPOINT CITATION EXAMPLES:
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ VALID PINPOINT CITATIONS:                                                              │
│ - "Fonseca et al. (2002), Table 2, row 'Cut Mango', p. 145"                             │
│ - "USDA FoodData Central FDC ID 1750341, Nutrient 'Water', Row 1"                      │
│ - "Kuraray EVAL F101B Technical Datasheet (2021), Section 'Barrier Properties', p. 2" │
│ - "ComBase Record ID CB-2004-LIS-012, Data Table 1"                                    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ INVALID PINPOINT CITATIONS:                                                            │
│ - "Fonseca et al."                (Missing table/page pinpoint)                         │
│ - "USDA"                          (Missing FDC ID and nutrient row)                     │
│ - "Manufacturer Datasheet"        (Missing manufacturer, grade, section)                │
│ - "Web Search Snippet"            (Prohibited source category)                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Source Hierarchy & Evidentiary Status
Sources are classified into formal hierarchy levels to establish evidentiary weight without inventing arbitrary numerical quality scores:

| Level | Source Category | Description & Examples | Evidentiary Status |
|:---|:---|:---|:---|
| **Level 1** | **Primary Peer-Reviewed Literature** | Original experimental measurements published in peer-reviewed scientific journals (e.g. *Postharvest Biology and Technology*, *Journal of Food Engineering*). | `PRIMARY_EXPERIMENTAL` |
| **Level 2** | **Official Institutional / Government DB** | Standard reference datasets maintained by government bodies (e.g. USDA FoodData Central, FAO, NIST). | `OFFICIAL_INSTITUTIONAL` |
| **Level 3** | **Manufacturer Technical Datasheet (TDS)** | Verified manufacturer specification sheets for commercial resins and films (e.g. Dupont, Kuraray EVAL, NatureWorks). | `COMMERCIAL_SPECIFICATION` |
| **Level 4** | **Curated Scientific Database** | Validated scientific repositories (e.g. ComBase for microbial kinetics, PubChem). | `CURATED_DATABASE` |
| **Level 5** | **Peer-Reviewed Review / Meta-Analysis** | Secondary scientific reviews summarizing primary literature. | `SECONDARY_REVIEW` |
| **Level 6** | **Search-Result Snippets / Web Pages** | Unverified search engine snippets, blog posts, unreferenced commercial marketing text. | **`PROHIBITED_AS_EVIDENCE`** |

- **REQ-HIER-01**: Level 6 sources (Search-Result Snippets) **MUST NOT** be used as scientific evidence. Records originating solely from Level 6 sources MUST be marked `REJECTED`.

---

## 14. Model-Predicted Data Handling
Model-predicted data (e.g. QSAR permeability estimations, empirical polynomial fits, machine-learning regressions) provide valuable surrogate estimates when experimental data is absent, but MUST NOT be conflated with empirical measurements.

- **REQ-PRED-01 (Status Assignment)**: All model-derived values MUST be assigned `verification_status = "MODEL_PREDICTED"`.
- **REQ-PRED-02 (Prohibition of Promotion)**: Model-predicted values **MUST NOT** be promoted to `VERIFIED`, even if the predictive model has been validated against external datasets.
- **REQ-PRED-03 (PolyID Model Separation)**: The separation established in M5 between experimental PolyID barrier observations and QSAR-predicted PolyID values MUST be strictly preserved.

---

## 15. Absolute Prohibition on Synthetic Data as Scientific Evidence
Synthetic, generated, or mock data fixtures introduced for software testing **MUST NOT** enter the scientific evidence dataset.

- **REQ-SYNTH-01 (Prohibition)**: Synthetic data fixtures MUST NOT be used to fill missing scientific evidence fields or to force optimization algorithms to pass.
- **REQ-SYNTH-02 (Scope Restriction)**: Synthetic fixtures are restricted strictly to software unit tests, integration tests, and pipeline execution validation (`SYNTHETIC_TEST`).
- **REQ-SYNTH-03 (Pipeline Tagging)**: Any candidate or requirement payload containing synthetic test data MUST be explicitly tagged with `data_origin = "SYNTHETIC_TEST"` and excluded from scientific evidence audits.

---

## 16. Conflicting Evidence Protocol
When multiple real, verified scientific sources report conflicting values for the same entity and property (e.g. two peer-reviewed papers reporting different respiration rates for *Gala* apples at $20^\circ\text{C}$):

- **REQ-CONF-01 (No Premature Averaging)**: Conflicting records **MUST NOT** be silently averaged, blended, or merged into a single mean value.
- **REQ-CONF-02 (Coexistence of Records)**: Both records MUST coexist as distinct evidence records in the database, retaining their respective provenance, citations, and experimental test conditions.
- **REQ-CONF-03 (Uncertainty Interval Representation)**: Downstream physics modules MUST represent conflicting evidence as bounded uncertainty intervals or explicit multi-record candidate evaluations as mandated by M6-B1 and M6-B2B.

---

## 17. Evidence Transformation Protocol
When a database value is transformed from its original source representation (e.g. converting temperature from Fahrenheit to Celsius, or converting $\text{cc}\cdot\text{mil}/(100\text{ in}^2\cdot\text{day}\cdot\text{atm})$ to $\text{m}^3\cdot\text{m}/(\text{m}^2\cdot\text{s}\cdot\text{Pa})$):

- **REQ-TRANS-01 (Preservation of Original State)**: The original value, original unit, and original text string MUST be preserved in the record.
- **REQ-TRANS-02 (Transformation Lineage)**: The transformation formula, conversion multiplier, and rationale MUST be recorded in the transformation metadata.
- **REQ-TRANS-03 (Prohibition of Unexplained Transformations)**: Unexplained or unrecorded numerical transformations are strictly prohibited. Any record containing an unexplained value shift MUST be marked `UNVERIFIED`.

---

## 18. Human Verification Metadata Specification
To establish formal human verification lineage during the DV1 audit, every evidence record MUST incorporate human review metadata.

### Required Metadata Fields:
- `human_verified` (Boolean): `TRUE` if a human auditor has verified the record against the pinpoint source document; `FALSE` otherwise.
- `verified_by` (String): Unique identifier or name of the human verifier (e.g. `"auditor_id_01"`).
- `verified_date` (ISO 8601 Date): Timestamp of human verification audit (e.g. `"2026-10-05"`).
- `verification_method` (Enum): Method used (`"PRIMARY_PDF_INSPECTION"`, `"DATABASE_API_CROSSCHECK"`, `"TDS_VERIFICATION"`).
- `verification_notes` (Text): Auditor observations, transcription corrections, or condition notes.
- `pinpoint_citation` (Text): Exact location within source document.

- **REQ-HUMAN-01**: If `human_verified == FALSE`, the record status **CANNOT** be set to `VERIFIED`.

---

## 19. Verification Evidence Record Schema Specification
The formal JSON schema for an independent **Verification Evidence Audit Record** (produced during DV1) is defined below:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ScientificEvidenceVerificationRecord",
  "type": "object",
  "required": [
    "audit_record_id",
    "evidence_record_id",
    "entity_type",
    "verification_status",
    "audit_gate_results",
    "human_verifier_metadata"
  ],
  "properties": {
    "audit_record_id": {"type": "string"},
    "evidence_record_id": {"type": "string"},
    "entity_type": {
      "type": "string",
      "enum": ["FOOD_COMMODITY", "PACKAGING_MATERIAL", "MICROBIAL_KINETICS"]
    },
    "verification_status": {
      "type": "string",
      "enum": ["VERIFIED", "UNVERIFIED", "REJECTED", "MODEL_PREDICTED", "MISSING"]
    },
    "audit_gate_results": {
      "type": "object",
      "required": [
        "entity_identity_pass",
        "property_identity_pass",
        "value_match_pass",
        "unit_check_pass",
        "condition_check_pass",
        "form_maturity_pass",
        "source_attribution_pass",
        "pinpoint_location_pass",
        "status_classification_pass"
      ],
      "properties": {
        "entity_identity_pass": {"type": "boolean"},
        "property_identity_pass": {"type": "boolean"},
        "value_match_pass": {"type": "boolean"},
        "unit_check_pass": {"type": "boolean"},
        "condition_check_pass": {"type": "boolean"},
        "form_maturity_pass": {"type": "boolean"},
        "source_attribution_pass": {"type": "boolean"},
        "pinpoint_location_pass": {"type": "boolean"},
        "status_classification_pass": {"type": "boolean"}
      }
    },
    "source_comparison": {
      "type": "object",
      "properties": {
        "database_value": {"type": ["number", "string", "null"]},
        "database_unit": {"type": ["string", "null"]},
        "source_reported_value": {"type": ["number", "string", "null"]},
        "source_reported_unit": {"type": ["string", "null"]},
        "pinpoint_citation": {"type": ["string", "null"]},
        "mismatch_detected": {"type": "boolean"},
        "mismatch_description": {"type": ["string", "null"]}
      }
    },
    "human_verifier_metadata": {
      "type": "object",
      "required": ["human_verified", "verified_by", "verified_date"],
      "properties": {
        "human_verified": {"type": "boolean"},
        "verified_by": {"type": "string"},
        "verified_date": {"type": "string", "format": "date"},
        "verification_method": {"type": "string"},
        "verification_notes": {"type": ["string", "null"]}
      }
    }
  },
  "additionalProperties": false
}
```

---

## 20. Record-Level Verification Decision Rules
During verification audit processing, every record MUST be evaluated through the following deterministic decision logic:

```
RECORD-LEVEL VERIFICATION DECISION TREE:

IF Source Document Missing or Unreachable:
    └─► Verification Status = MISSING / UNVERIFIED

ELSE IF Property is Derived from QSAR / Model:
    └─► Verification Status = MODEL_PREDICTED

ELSE IF Original Source Uninspected by Human Auditor:
    └─► Verification Status = UNVERIFIED

ELSE IF All 9 Audit Gate Dimensions Pass (9/9 TRUE) AND human_verified == TRUE:
    └─► Verification Status = VERIFIED

ELSE IF Entity Mismatch OR Value Mismatch OR Condition Mismatch Confirmed:
    └─► Verification Status = REJECTED
```

- **REQ-DEC-01**: Partial verification pass (e.g. 7/9 or 8/9 gate pass) MUST result in `UNVERIFIED` or `REJECTED`. It **CANNOT** produce `VERIFIED`.

---

## 21. Structural Validation vs Source Verification
This protocol enforces a fundamental distinction between structural code validation and scientific source verification:

- **Structural Validation** asks: *"Is the data JSON well-formed, matching Pydantic schema types, non-null where required, and within broad physical bounds?"*
- **Source Verification** asks: *"Does the original physical scientific document actually contain and support this specific measurement, for this specific cultivar/material, under these exact test conditions?"*

Passing structural validation is a **PREREQUISITE** for source verification, but **CANNOT SUBSTITUTE** for source verification.

---

## 22. Current Data Status Governance
Passing previous architectural milestones (M1 through M5) confirmed schema completeness, pipeline flow, and structural data model integrity. It **DID NOT** perform human source verification of individual data rows.

- **REQ-STAT-01**: Existing database records in `food_evidence.json` and `packaging_materials.json` currently hold status `literature`, `experimental`, or `predicted`.
- **REQ-STAT-02**: All un-audited literature records MUST be treated as `UNVERIFIED` until formally audited in Milestone DV1.
- **REQ-STAT-03**: No record statuses will be modified during DV0.

---

## 23. Anti-Assumptions Rules ("No Automatic Trust")
To maintain scientific rigor, auditors and automated validation checks MUST enforce the following anti-assumption rules:

1. **DOI Presence $\ne$ Value Correctness**: The presence of a valid DOI string does NOT prove that the numerical value in the database was correctly transcribed.
2. **Database ID Presence $\ne$ Entity Correctness**: The presence of an FDC ID or PolyID does NOT prove that the cultivar or polymer structure assignment is correct.
3. **Source Title Matching $\ne$ Citation Correctness**: Matching paper titles does NOT prove that the cited paper contains the specific reported measurement.
4. **Valid Units $\ne$ Scientific Applicability**: Expressing a value in valid units ($\text{cc}/\text{m}^2\cdot\text{day}$) does NOT prove that the measurement applies to the target storage temperature or humidity.
5. **Provenance Field Presence $\ne$ Provenance Verification**: The mere existence of provenance metadata fields does NOT substitute for human inspection of the source text.

---

## 24. Verification Priority Hierarchy for DV1
To maximize scientific impact during the upcoming DV1 audit, records will be prioritized in the following order:

1. **Respiration Kinetics Evidence**: ($\text{CO}_2$ evolution, $\text{O}_2$ consumption rates, Arrhenius activation energies, $Q_{10}$ values).
2. **Packaging Barrier Properties**: (OTR, WVTR, $\text{CO}_2\text{TR}$, temperature/RH test condition dependencies).
3. **Moisture / Sorption Isotherm Evidence**: (GAB/Halsey isotherm parameters, monolayer moisture content $m_0$, critical water activity $a_c$).
4. **Shelf-Life Requirement Parameters**: (Critical moisture gain/loss limits, gas concentration tolerances).
5. **Microbial Growth Kinetics**: (Lag time $\lambda$, maximum specific growth rate $\mu_{\max}$, cardinal temperature/pH/$a_w$ bounds).
6. **General Commodity Quality Metrics**: (Initial soluble solids, titratable acidity, firmness).

*Note: Numerical priority scores (e.g. Priority 1.5) are strictly prohibited.*

---

## 25. DV1 Audit Output Specification
Milestone DV1 will execute the audit protocol specified in DV0 and produce the following formal outputs:

1. `docs/dv1_scientific_evidence_verification_report.md`: Comprehensive forensic audit report detailing verification results across all evidence records.
2. `data/reference/verification_audit_log.json`: Machine-readable log containing a `ScientificEvidenceVerificationRecord` for every audited record.
3. Updated evidence status assignments (`VERIFIED`, `UNVERIFIED`, `REJECTED`, `MODEL_PREDICTED`, `MISSING`) applied to dataset records.

---

## 26. Explicit Non-Decisions & Unauthorized Scope
In accordance with zero-code design discipline, Milestone DV0 **DOES NOT AUTHORIZE**:

1. **Data Modification**: No scientific values in `food_evidence.json` or `packaging_materials.json` are modified.
2. **Data Correction**: No numerical transcription errors are corrected during DV0.
3. **Data Deletion**: No records are deleted from the repository.
4. **Data Addition**: No new scientific values or literature records are added.
5. **Web Searching**: No web searches or database lookups for replacement values are performed during DV0.
6. **Code / Schema Changes**: No Python source code (`backend/app/...`), database schemas, or pytest files are modified.
7. **Record Promotion**: No un-audited records are declared `VERIFIED`.

---

## 27. Forensic Self-Audit
Before finalizing this protocol, the following forensic audit assertions were verified:

- [x] **No scientific records modified.**
- [x] **No scientific values added.**
- [x] **No scientific values corrected.**
- [x] **No records deleted.**
- [x] **No synthetic evidence added as scientific data.**
- [x] **No MODEL_PREDICTED record promoted to VERIFIED.**
- [x] **Existing M1-M5 provenance preserved.**
- [x] **Source verification strictly separated from structural validation.**
- [x] **Exact source attribution required.**
- [x] **Pinpoint citation specified (table/figure/page/row).**
- [x] **Entity identity verification rules established.**
- [x] **Property identity verification rules established.**
- [x] **Numerical value verification rules established.**
- [x] **Unit & gas species integrity rules established.**
- [x] **Test condition verification rules established.**
- [x] **Human verification metadata schema specified.**
- [x] **Conflicting evidence coexistence policy specified.**
- [x] **Cultivar & entity substitution strictly prohibited.**
- [x] **Commodity-agnostic architectural scope preserved.**
- [x] **DV1 explicitly designated as audit execution milestone.**
- [x] **Zero production Python code files modified.**
- [x] **Zero unit test files modified.**
