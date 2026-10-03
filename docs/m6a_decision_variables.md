# M6-A: DECISION VARIABLES & CANDIDATE PACKAGING REPRESENTATION

**Project**: AI-Based Intelligent Food Packaging Material Recommendation System  
**Milestone**: M6-A (Decision Variables & Candidate Representation Design)  
**Date**: 2026-09-28  
**Status**: DESIGN COMPLETE — AUDIT READY  

---

## 1. Scope & Objective

This document defines the decision space $\mathcal{X}$ for the packaging optimization engine and provides the formal conceptual specification for `PackagingCandidate`.

In accordance with strict project rules:
- **No arbitrary continuous material properties** are assumed if the database contains only discrete measured material evidence.
- **Active packaging variables** (scavengers, emitters) are evaluated against actual M4/M5 database contents and classified appropriately.
- Every candidate packaging design is structured to be **completely traceable** back to underlying empirical or QSAR evidence in the canonical database.

---

## 2. Decision Space Definition ($\mathcal{X}$)

The decision space $\mathcal{X}$ represents the set of all controllable parameters that an optimization algorithm may manipulate to generate candidate packaging designs.

The decision vector is partitioned into four primary categories:
1. **Material Selection Variables** ($\mathcal{X}_{\text{material}}$)
2. **Structural & Layer Variables** ($\mathcal{X}_{\text{structure}}$)
3. **Geometric & Package Variables** ($\mathcal{X}_{\text{geometry}}$)
4. **Active / Functional Variables** ($\mathcal{X}_{\text{functional}}$)

---

## 3. Comprehensive Decision Variable Specification Table

| Variable Name | Symbol | Data Type | Units | Domain / Range | Discrete / Continuous | Source in M5 Canonical Database | Experimentally Supported? | Modifiability in Phase 6 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Material Identifier** | $x_{\text{mat\_id}}$ | UUID / String | None | 11 canonical materials in `PackagingMaterial` | Discrete (Categorical) | `PackagingMaterial.id`, `material_name` | Yes (10 Exp, 1 QSAR) | **Free Decision Variable** |
| **Structure Type** | $x_{\text{struct}}$ | Enum | None | `MONOLAYER`, `MULTILAYER`, `COATED` | Discrete (Categorical) | `PackagingMaterial.structure_type` | Yes | **Free Decision Variable** |
| **Layer Count** | $N_{\text{layer}}$ | Integer | Count | $1 \le N_{\text{layer}} \le 5$ (measured: 1 to 3) | Discrete (Integer) | `PackagingMaterial.layer_sequence` length | Yes | **Free Decision Variable** |
| **Layer Polymer Sequence** | $\mathbf{x}_{\text{layer\_seq}}$ | List[String] | None | Sequence of polymer codes (e.g., `["LDPE", "EVOH", "LDPE"]`) | Discrete (Permutation) | `PackagingMaterial.layer_sequence` (JSONB) | Yes (for coextruded/laminated materials) | **Constrained Permutation** |
| **Material Thickness** | $t_{\text{mat}}$ | Float | $\mu\text{m}$ | $12.0 \le t \le 70.0$ (discrete measured grades) | **Discrete Measured Points** *(see note below)* | `MaterialBarrierObservation.thickness_value` | Yes (12, 15, 25, 30, 40, 50, 70 $\mu\text{m}$) | **Discrete Selection** (Continuous scaling deferred) |
| **Package Surface Area** | $A_{\text{pkg}}$ | Float | $\text{m}^2$ | $0.01 \le A_{\text{pkg}} \le 0.50$ (default: 0.06 $\text{m}^2$) | Continuous | `PackagingRequest.package_surface_area_m2` | Yes (user / engineering input) | **Parameter or Bounded Variable** |
| **Headspace Volume** | $V_{\text{headspace}}$ | Float | $\text{cm}^3$ | $50.0 \le V \le 2000.0$ | Continuous | `PackagingRequest.package_headspace_volume_cm3` | Yes (user / engineering input) | **Parameter or Bounded Variable** |
| **Package Mass Load** | $M_{\text{food}}$ | Float | $\text{kg}$ | $0.05 \le M \le 5.00$ | Continuous | `PackagingRequest.product_mass_kg` | Yes (user input) | **Fixed Operational Parameter** |
| **Initial Gas Flush ($O_2$)** | $y_{O2,0}$ | Float | % | $0.0 \le y_{O2,0} \le 21.0$ | Continuous | Phase 4 `GasExchangeRequirement.target_o2_range` | Yes (MAP design parameter) | **Engineering Variable (MAP)** |
| **Initial Gas Flush ($CO_2$)** | $y_{CO2,0}$ | Float | % | $0.0 \le y_{CO2,0} \le 80.0$ | Continuous | Phase 4 `GasExchangeRequirement.target_co2_range` | Yes (MAP design parameter) | **Engineering Variable (MAP)** |
| **Active $O_2$ Scavenger Capacity** | $C_{scav,O2}$ | Float | $cc\text{ }O_2$ | None in database | Continuous | **NONE IN M5 DATABASE** | **NO (DATA GAP)** | **DEFERRED** |
| **Active Moisture Desiccant** | $C_{desic}$ | Float | $g\text{ }H_2O$ | None in database | Continuous | **NONE IN M5 DATABASE** | **NO (DATA GAP)** | **DEFERRED** |
| **Antimicrobial Coating Type** | $x_{AM}$ | String | None | None in database | Categorical | **NONE IN M5 DATABASE** | **NO (DATA GAP)** | **DEFERRED** |

---

## 4. Scientific Rule on Thickness Modifiability

### Continuous vs. Discrete Thickness Modeling
In classical polymer physics, barrier transmission follows the ideal permeability relation:

$$\text{Transmission Rate} = \frac{\text{Permeability Coefficient } (P)}{\text{Thickness } (t)}$$

Under this ideal assumption, doubling film thickness halves transmission ($TR \propto 1/t$).

However, M5 project governance strictly establishes:
> **"Do not assume arbitrary continuous material properties if the database only contains discrete measured material evidence. Do not normalize thickness unless already explicitly supported by M4."**

### Rationale:
1. Real multilayer barrier laminates (e.g., Kuraray EVAL EVOH coextrusions, DuPont foil laminates) have complex inter-layer tie layers and orientation effects. The barrier is dominated by an ultra-thin barrier core (e.g., $3 \mu\text{m}$ EVOH inside a $70 \mu\text{m}$ structure). Arbitrary linear scaling of total thickness produces non-physical permeabilities.
2. In the verified M5 database, thicknesses represent **real commercial film gauges** ($12 \mu\text{m}$, $15 \mu\text{m}$, $25 \mu\text{m}$, $30 \mu\text{m}$, $40 \mu\text{m}$, $50 \mu\text{m}$, $70 \mu\text{m}$). These are global observed thickness values; each material currently has a single evidenced thickness (e.g., LDPE at $50 \mu\text{m}$, BOPET at $12 \mu\text{m}$). Material-specific candidate eligibility requires evidence-level mapping. Fabricating continuous intermediate gauges ($28.37 \mu\text{m}$) that cannot be commercially ordered or manufactured violates practical engineering validity.

### Phase 6 Implementation Decision:
- **Primary Optimization Mode (Discrete Catalog Search)**: The optimizer selects from verified discrete commercial gauges present in the M5 database.
- **Secondary Mode (Exploratory Continuous Permeability Modeling)**: Permitted only for verified isotropic monolayers (e.g., LDPE, HDPE, PP, PLA) where permeability $P$ is explicitly recorded. If continuous scaling is used, the resulting candidate must be tagged with `thickness_scaled = True` and a mandatory warning indicating that commercial film availability must be verified.

---

## 5. Audit of Active / Functional Packaging Variables

A comprehensive inspection of the M4 processed datasets and M5 canonical PostgreSQL tables (`PackagingMaterial`, `MaterialBarrierObservation`, `EvidenceRecord`) was conducted to evaluate support for active packaging:

- **$O_2$ Scavengers**: Zero records in M4/M5.
- **$CO_2$ Scavengers / Emitters**: Zero records in M4/M5.
- **Ethylene Scrubbers**: Zero records in M4/M5.
- **Moisture Desiccants / Regulating Sachets**: Zero records in M4/M5.
- **Antimicrobial Films / Nano-coatings**: Zero records in M4/M5.

### Decision:
**All active packaging decision variables are formally DEFERRED — DATA GAP.**  
Phase 6 optimization will operate strictly on **passive barrier materials, multilayers, and MAP headspace gas composition**. No synthetic active packaging variables will be created without empirical acquisition in future milestones.

---

## 6. Formal Representation of a Candidate Packaging Design

Every candidate packaging design generated or evaluated during optimization must conform to a rigorous, structured schema. A candidate must never be an unexplained numeric vector.

### Conceptual Schema: `PackagingCandidate`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PackagingCandidate",
  "description": "Canonical representation of a single candidate packaging design evaluated during optimization.",
  "type": "object",
  "required": [
    "candidate_id",
    "material_id",
    "material_name",
    "structure_type",
    "total_thickness_um",
    "barrier_properties",
    "evidence_classification",
    "verification_status",
    "condition_match",
    "provenance"
  ],
  "properties": {
    "candidate_id": {
      "type": "string",
      "format": "uuid",
      "description": "Deterministic UUID for this candidate packaging design."
    },
    "material_id": {
      "type": "string",
      "format": "uuid",
      "description": "Foreign key reference to M5 PackagingMaterial entity."
    },
    "material_name": {
      "type": "string",
      "description": "Human-readable commercial material name or polymer specification."
    },
    "brand_grade": {
      "type": ["string", "null"],
      "description": "Manufacturer commercial resin grade (e.g., 'EVAL F101B', 'Ingeo 2003D')."
    },
    "structure_type": {
      "type": "string",
      "enum": ["MONOLAYER", "MULTILAYER", "COATED"],
      "description": "Morphological structure of the packaging film."
    },
    "layer_sequence": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Ordered sequence of polymer layer designations from exterior to food contact."
    },
    "total_thickness_um": {
      "type": "number",
      "minimum": 0.0,
      "description": "Total measured or nominal packaging thickness in micrometers."
    },
    "thickness_is_continuous_scaled": {
      "type": "boolean",
      "default": false,
      "description": "True if thickness was continuously derived via permeability scaling; False if discrete commercial datasheet."
    },
    "barrier_properties": {
      "type": "object",
      "required": ["otr", "co2tr", "wvtr"],
      "properties": {
        "otr": {
          "type": "object",
          "required": ["value", "unit", "test_temperature_c", "test_rh_percent"],
          "properties": {
            "value": { "type": "number", "minimum": 0.0 },
            "unit": { "type": "string", "enum": ["cc/m2-day-atm", "cc/m2-day"] },
            "value_min": { "type": ["number", "null"] },
            "value_max": { "type": ["number", "null"] },
            "is_range": { "type": "boolean" },
            "test_temperature_c": { "type": ["number", "null"] },
            "test_rh_percent": { "type": ["number", "null"] },
            "test_standard": { "type": ["string", "null"] }
          }
        },
        "co2tr": {
          "type": "object",
          "required": ["value", "unit", "test_temperature_c", "test_rh_percent"],
          "properties": {
            "value": { "type": "number", "minimum": 0.0 },
            "unit": { "type": "string", "enum": ["cc/m2-day-atm", "cc/m2-day"] },
            "value_min": { "type": ["number", "null"] },
            "value_max": { "type": ["number", "null"] },
            "is_range": { "type": "boolean" },
            "test_temperature_c": { "type": ["number", "null"] },
            "test_rh_percent": { "type": ["number", "null"] },
            "test_standard": { "type": ["string", "null"] }
          }
        },
        "wvtr": {
          "type": "object",
          "required": ["value", "unit", "test_temperature_c", "test_rh_percent"],
          "properties": {
            "value": { "type": "number", "minimum": 0.0 },
            "unit": { "type": "string", "enum": ["g/m2-day"] },
            "value_min": { "type": ["number", "null"] },
            "value_max": { "type": ["number", "null"] },
            "is_range": { "type": "boolean" },
            "test_temperature_c": { "type": ["number", "null"] },
            "test_rh_percent": { "type": ["number", "null"] },
            "test_standard": { "type": ["string", "null"] }
          }
        }
      }
    },
    "evidence_classification": {
      "type": "string",
      "enum": ["EXPERIMENTAL_LITERATURE_DATA", "SOURCE_MEASURED", "MODEL_PREDICTED"],
      "description": "Scientific nature of the underlying material evidence."
    },
    "verification_status": {
      "type": "string",
      "enum": ["VERIFIED_EXTRACT", "PARTIALLY_VERIFIED", "PREDICTIVE_ONLY"],
      "description": "Audited verification status from M2.1/M5."
    },
    "synthetic_prediction_warning": {
      "type": ["string", "null"],
      "description": "Mandatory warning flag if evidence is derived from computational QSAR models."
    },
    "condition_match": {
      "type": "string",
      "enum": ["EXACT", "SUPPORTED", "INCOMPATIBLE", "UNKNOWN"],
      "description": "Phase 5 environmental test condition compatibility level."
    },
    "provenance": {
      "type": "object",
      "required": ["source_id", "source_name", "record_identifier_in_source"],
      "properties": {
        "source_id": { "type": "string", "format": "uuid" },
        "source_name": { "type": "string" },
        "record_identifier_in_source": { "type": "string" },
        "literature_references": { "type": ["array", "object", "null"] }
      }
    },
    "manufacturing_constraints": {
      "type": "object",
      "properties": {
        "recyclable": { "type": ["boolean", "null"] },
        "recycling_code": { "type": ["string", "null"] },
        "bio_based": { "type": ["boolean", "null"] },
        "compostable": { "type": ["boolean", "null"] }
      }
    }
  }
}
```

---

## 7. Traceability Verification

Under this design:
1. Every candidate contains `material_id` and `provenance.source_id`, which directly query the PostgreSQL `PackagingMaterial`, `MaterialBarrierObservation`, and `Source` tables.
2. Every candidate contains explicit test conditions (`test_temperature_c`, `test_rh_percent`) ensuring that condition compatibility is traceable.
3. Every candidate explicitly records whether it is based on measured lab evidence or QSAR predictions, preventing synthetic model data from being passed off as physical measurements.
