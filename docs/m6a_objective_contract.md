# M6-A: OPTIMIZATION OBJECTIVE CONTRACT

**Project**: AI-Based Intelligent Food Packaging Material Recommendation System  
**Milestone**: M6-A (Objective Function Formulation & Data Contract)  
**Date**: 2026-09-28  
**Status**: DESIGN COMPLETE — AUDIT READY  

---

## 1. Executive Summary & Anti-Fabrication Mandate

Milestone M6-A establishes the formal mathematical objective contract for the multi-objective optimization engine.

### Strict Governance Mandates:
1. **Anti-Fabrication Policy**: An objective function may only be designated as `AVAILABLE NOW` if the underlying scientific or commercial data exists in the verified M4/M5 database, or can be derived deterministically from verified Phase 4 physics equations.
2. **No Mock or Placeholder Constants**: The project strictly prohibits creating synthetic cost numbers (e.g., "$2.50 / kg for LDPE") or fabricated carbon footprint coefficients (e.g., "1.8 kg CO2 / kg PET") without verified source provenance.
3. **Transparent Data Gap Auditing**: Proposed objectives lacking empirical backing are classified as `DEFERRED — DATA GAP`.

---

## 2. Objective Function Inventory & Feasibility Classification

| Objective Identifier | Objective Name | Goal | Units | Mathematical Basis | Evidence Source | Status |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| **$f_{\text{thickness}}$** | Material Resource / Thickness Minimization | **Minimize** | $\mu\text{m}$ | Total film thickness | M5 `MaterialBarrierObservation.thickness_value` | **AVAILABLE NOW** |
| **$f_{\text{moisture\_margin}}$** | Moisture Barrier Safety Margin | **Maximize** | Dimensionless | Ratio of barrier headroom relative to $WVTR_{max}$ | Phase 4 `MoistureRequirement` & M5 `WVTR` | **AVAILABLE NOW** |
| **$f_{\text{gas\_alignment}}$** | Gas Barrier Alignment Penalty | **Minimize** | Dimensionless | Normalized Euclidean distance to target $O_2/CO_2$ window | Phase 4 `GasExchangeRequirement` & M5 `OTR/CO2TR` | **AVAILABLE NOW** |
| **$f_{\text{shelf\_life\_margin}}$** | Shelf-Life Extension Margin | **Maximize** | Dimensionless | Achievable days beyond target shelf-life | Phase 4 `ShelfLifeRequirement` & M5 Barriers | **AVAILABLE NOW** |
| **$f_{\text{cost}}$** | Packaging Material Economic Cost | **Minimize** | $\$ / \text{package}$ | Cost per unit mass / area | **None in M4 / M5 database** | **DEFERRED — DATA GAP** |
| **$f_{\text{carbon\_footprint}}$** | Cradle-to-Gate Life Cycle Impact (GWP) | **Minimize** | $\text{kg CO}_2\text{-eq} / \text{kg}$ | Life Cycle Assessment (LCA) | **None in M4 / M5 database** | **DEFERRED — DATA GAP** |
| **$f_{\text{recyclability}}$** | Packaging Circularity Index | **Maximize** | Qualitative / Categorical | Polymer resin identification & mechanical recycling | M4 TDS & CIRAD sustainability tags | **PARTIALLY AVAILABLE (FILTER ONLY)** |

---

## 3. Detailed Specifications for Computable Objectives (`AVAILABLE NOW`)

### Objective 1: Material Resource / Thickness Minimization ($f_{\text{thickness}}$)
- **Identifier**: `f_thickness`
- **Direction**: $\text{Minimize}$
- **Mathematical Formulation**:
  $$f_{\text{thickness}}(\mathbf{x}) = t_{\text{total}}(\mathbf{x}) = \sum_{l=1}^{N_{\text{layer}}} t_l$$
  *(For monolayer materials, $f_{\text{thickness}}(\mathbf{x}) = t_{\text{measured}}$).*
- **Units**: Micrometers ($\mu\text{m}$)
- **Scientific Rationale**: Minimizing packaging thickness directly minimizes polymer material consumption, reduces packaging tare weight, decreases freight transport energy, and reflects source reduction principles (ISO 18602).
- **Inputs**:
  - `PackagingCandidate.total_thickness_um`
- **Evidence Source**: `backend/app/models/evidence.py` $\to$ `MaterialBarrierObservation.thickness_value`.
- **Classification**: Measured empirical property from manufacturer datasheets and literature.
- **Uncertainty**: Nominal commercial gauge; tolerance typically $\pm 5\%$.
- **Status**: **AVAILABLE NOW**

---

### Objective 2: Moisture Barrier Safety Margin ($f_{\text{moisture\_margin}}$)
- **Identifier**: `f_moisture_margin`
- **Direction**: $\text{Maximize}$ (Formulated as $-f_{\text{moisture\_margin}} \to \text{Minimize}$)
- **Mathematical Formulation**:
  $$f_{\text{moisture\_margin}}(\mathbf{x}) = \frac{WVTR_{\text{allowable}}(\mathcal{E}) - WVTR_{\text{mat}}(\mathbf{x})}{WVTR_{\text{allowable}}(\mathcal{E})}$$
  Where:
  - $WVTR_{\text{allowable}}(\mathcal{E})$ is the maximum allowable water vapor transmission rate derived by Phase 4 (`MoistureRequirement.required_wvtr_per_area.value`).
  - $WVTR_{\text{mat}}(\mathbf{x})$ is the candidate material's water vapor transmission rate.
  - Since the candidate has passed Phase 5 hard constraints, $WVTR_{\text{mat}}(\mathbf{x}) \le WVTR_{\text{allowable}}(\mathcal{E})$, guaranteeing $f_{\text{moisture\_margin}}(\mathbf{x}) \ge 0$.
- **Units**: Dimensionless ratio ($0.0 \le f \le 1.0$)
- **Scientific Rationale**: A higher margin provides robust protection against ambient humidity fluctuations, handling abuse, micro-pinholing, and storage temperature excursions.
- **Inputs**:
  - Phase 4 `MoistureRequirement.required_wvtr_per_area`
  - M5 `MaterialBarrierObservation` where `property_type = 'WVTR'`
- **Evidence Source**: Processed moisture mass balance + ASTM F1249 / ASTM E96 measurements in PostgreSQL.
- **Classification**: Derived physical ratio combining Phase 4 physics and empirical barrier data.
- **Uncertainty**: When $WVTR_{\text{mat}}$ is reported as an interval $[v_{\min}, v_{\max}]$, the margin is computed conservatively using $v_{\max}$:
  $$f_{\text{moisture\_margin}}^{\text{conservative}} = \frac{WVTR_{\text{allowable}} - v_{\max}}{WVTR_{\text{allowable}}}$$
- **Status**: **AVAILABLE NOW**

---

### Objective 3: Gas Barrier Alignment Penalty ($f_{\text{gas\_alignment}}$)
- **Identifier**: `f_gas_alignment`
- **Direction**: $\text{Minimize}$
- **Mathematical Formulation**:
  For respiring produce (fresh fruit/vegetables), optimal modified atmosphere packaging (EMAP) requires balancing $O_2$ ingress with respiration consumption to achieve a target headspace equilibrium $[y_{O2,\min}, y_{O2,\max}]$. Unlike moisture (where "more barrier is always safer"), gas packaging has both a lower bound (preventing anaerobic fermentation) and an upper bound (retarding senescence).

  $$f_{\text{gas\_alignment}}(\mathbf{x}) = \left| \frac{OTR_{\text{mat}}(\mathbf{x}) - OTR_{\text{target}}(\mathcal{E})}{OTR_{\text{target}}(\mathcal{E})} \right| + \lambda_{\beta} \left| \frac{\beta_{\text{mat}}(\mathbf{x}) - \beta_{\text{ideal}}(\mathcal{E})}{\beta_{\text{ideal}}(\mathcal{E})} \right|$$
  Where:
  - $OTR_{\text{target}}(\mathcal{E})$ is the target equilibrium OTR derived by Phase 4 (`GasExchangeRequirement.required_otr_per_area.value`).
  - $\beta_{\text{ideal}} = \left(\frac{P_{CO2}}{P_{O2}}\right)_{\text{ideal}}$ is the required selectivity ratio from Phase 4.
  - $\beta_{\text{mat}} = \frac{CO2TR_{\text{mat}}}{OTR_{\text{mat}}}$ is the candidate film's selectivity ratio.
  - $\lambda_{\beta}$ is a non-dimensional scaling weight (default: 0.5) when $CO_2$ tolerances are active.
  *(For non-respiring food where $O_2$ is purely degradative, $f_{\text{gas\_alignment}}$ simplifies to normalized OTR minimization: $OTR_{\text{mat}} / OTR_{\text{allowable}}$).*
- **Units**: Dimensionless penalty ($\ge 0$)
- **Scientific Rationale**: Aligns film permeability with the biological respiration rate ($R_{O2}, R_{CO2}$) to prevent chilling injury, off-flavors, and fermentation.
- **Inputs**:
  - Phase 4 `GasExchangeRequirement`
  - M5 `MaterialBarrierObservation` where `property_type = 'OTR'` and `'CO2TR'`
- **Evidence Source**: Cameron et al. / Jurin & Karel mass balance equations in Phase 4 + ASTM D3985 measurements in PostgreSQL.
- **Classification**: Derived biophysical alignment metric.
- **Uncertainty**: Preserves range intervals $[OTR_{\min}, OTR_{\max}]$ through bounding.
- **Status**: **AVAILABLE NOW**

---

### Objective 4: Shelf-Life Preservation Margin ($f_{\text{shelf\_life\_margin}}$)
- **Identifier**: `f_shelf_life_margin`
- **Direction**: $\text{Maximize}$ (Formulated as $-f_{\text{shelf\_life\_margin}} \to \text{Minimize}$)
- **Mathematical Formulation**:
  $$f_{\text{shelf\_life\_margin}}(\mathbf{x}) = \frac{t_{\text{achievable}}(\mathbf{x}, \mathcal{E}) - t_{\text{target}}(\mathcal{E})}{t_{\text{target}}(\mathcal{E})}$$
  Where:
  - $t_{\text{target}}(\mathcal{E})$ is user-requested shelf life (days).
  - $t_{\text{achievable}}(\mathbf{x}, \mathcal{E})$ is the minimum shelf life across all active deterioration modes evaluated with candidate $\mathbf{x}$:
    $$t_{\text{achievable}}(\mathbf{x}) = \min \left( t_{\text{moisture}}(\mathbf{x}), \, t_{\text{gas}}(\mathbf{x}), \, t_{\text{microbial}}(\mathbf{x}), \, t_{\text{ambient\_shelf\_life}} \right)$$
    Where:
    - $t_{\text{moisture}}(\mathbf{x}) = \frac{M_{\text{food}} \cdot \Delta m_{\text{crit}}}{A_{\text{pkg}} \cdot WVTR_{\text{mat}}(\mathbf{x}) \cdot \Delta p_w}$
    - $t_{\text{microbial}}(\mathbf{x})$ is derived from ComBase kinetics under the candidate's equilibrium gas composition.
- **Units**: Dimensionless ratio ($\ge 0$ for feasible candidates)
- **Scientific Rationale**: Direct commercial value metric: indicates how many additional days of retail buffer the packaging provides beyond the customer's minimum specification.
- **Inputs**:
  - Phase 4 `ShelfLifeRequirement.target_days`
  - Phase 4 moisture sorption and microbial kinetic equations
  - Candidate material barrier properties ($WVTR_{\text{mat}}$, $OTR_{\text{mat}}$)
- **Evidence Source**: Phase 4 physical models + M5 empirical measurements.
- **Classification**: Derived physical kinetics metric.
- **Status**: **AVAILABLE NOW**

---

## 4. Audit of Deferred Objectives (`DATA GAP`)

### Objective 5: Packaging Material Cost ($f_{\text{cost}}$) — DEFERRED
- **Proposed Meaning**: Total material acquisition cost per package ($\$ / \text{package}$ or $\text{INR} / \text{package}$).
- **Required Inputs**: Raw polymer resin spot prices ($\$ / \text{metric ton}$), film conversion/extrusion markups, lamination processing costs, regional import tariffs.
- **Audit of M4/M5 Database**:
  - `PackagingMaterial`: 0 economic fields.
  - `MaterialBarrierObservation`: 0 cost fields.
  - M4 technical datasheets: Contain technical specifications only; commercial pricing is proprietary and volatile.
- **Anti-Fabrication Verdict**: **DEFERRED — DATA GAP**.
  - No synthetic pricing (e.g. assigning arbitrary dollars per kilogram) will be introduced.
  - *Mitigation Plan for Future Milestones*: A formal economic evidence stream (ICIS, Plastics News resin pricing, Indian polymer spot indexes) must be ingested with verified provenance in Phase 7 before this objective can be activated.

---

### Objective 6: Cradle-to-Gate Carbon Footprint ($f_{\text{carbon\_footprint}}$) — DEFERRED
- **Proposed Meaning**: Global Warming Potential (GWP 100a) in $\text{kg CO}_2\text{-equivalent} / \text{kg polymer}$ or $\text{g CO}_2\text{-eq} / \text{package}$.
- **Required Inputs**: Life Cycle Inventory (LCI) datasets (e.g., Ecoinvent, PlasticsEurope eco-profiles), regional electrical grid carbon intensity, extrusion energy consumption.
- **Audit of M4/M5 Database**:
  - M5 database contains qualitative polymer structure codes (`LDPE`, `HDPE`, `PP`, `PET`, `EVOH`, `PLA`), but zero numerical LCA emission factors.
- **Anti-Fabrication Verdict**: **DEFERRED — DATA GAP**.
  - Fabricating generic carbon intensity factors violates project authenticity rules.
  - *Mitigation Plan*: A verified secondary life-cycle database (e.g. openLCA / PlasticsEurope verified profiles) must be integrated via an authenticated pipeline before activating this objective.

---

### Objective 7: Packaging Circularity / Recyclability — PARTIALLY AVAILABLE (FILTER ONLY)
- **Audit of M4/M5 Database**:
  - Manufacturer TDS and CIRAD datasets contain qualitative sustainability metadata:
    - `recyclable`: `True` / `False`
    - `recycling_code`: `"LDPE-04"`, `"HDPE-02"`, `"PP-05"`, `"PET-01"`, `"PLA-07"`, `"OTHER-07"`
    - `bio_based`: `True` / `False`
    - `compostable`: `True` / `False`
- **Architectural Decision**:
  - Because recyclability is currently recorded as categorical flags rather than an audited continuous metric (such as the Ellen MacArthur Foundation Material Circularity Indicator), it **cannot be formulated as a continuous Pareto objective without arbitrary subjective weighting**.
  - **Handling**: In M6, recyclability is treated as a **Discrete Categorical Constraint / Preference Filter** (e.g., `filter_bio_based=True`, `require_recyclable=True`) rather than a continuous Pareto optimization objective.

---

## 5. Active Multi-Objective Formulation for Phase 6

Based on verified data availability, the operational multi-objective problem for Phase 6 consists of the following 3-dimensional or 4-dimensional continuous trade-off space across feasible candidates:

$$\min_{\mathbf{x} \in \mathcal{X}_{\text{feasible}}} \; \mathbf{F}(\mathbf{x}) = \begin{bmatrix}
f_{\text{thickness}}(\mathbf{x}) \\
-f_{\text{moisture\_margin}}(\mathbf{x}) \\
f_{\text{gas\_alignment}}(\mathbf{x}) \\
-f_{\text{shelf\_life\_margin}}(\mathbf{x})
\end{bmatrix}$$

### Active Trade-Off Dynamics:
1. **Thickness vs. Moisture Margin**: Thinner packaging reduces material usage ($f_{\text{thickness}} \downarrow$), but decreases barrier capability and narrows the moisture safety margin ($-f_{\text{moisture\_margin}} \uparrow$).
2. **Gas Alignment vs. Thickness**: Achieving high gas alignment for respiring produce often requires multilayer structures or micro-perforations, which may increase thickness or structural complexity.
3. **Shelf-Life Margin vs. Resource Use**: Maximizing shelf-life preservation headroom requires heavier, higher-barrier films, creating a direct physical trade-off against resource minimization.
