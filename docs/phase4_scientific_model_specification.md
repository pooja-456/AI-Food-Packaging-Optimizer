# Phase 4 — Mechanism-Aware Scientific Packaging Requirement Engine Specification

## 1. Architectural Role & Boundary

The **Mechanism-Aware Scientific Packaging Requirement Engine** implements the physics, thermodynamic, and microbiological layer of the **AI-Based Intelligent Food Packaging Material Recommendation System**.

```
PackagingRequest (User Input)
       ↓
PropertyInferenceProfile (Phase 3 Scientific Inference)
       ↓
Deterioration-Mode Assessment (Mechanism Eligibility & Computability)
       ↓
Scientific Mechanism Models (Physics & Mass Balances)
       ↓
PackagingRequirementEnvelope (Required Performance Targets)
       ↓
[Phase 5: Deterministic Hard-Constraint Filtering]
```

### Core Boundary
- **Answers:** *"What packaging performance (OTR, CO2TR, WVTR, water activity, headspace atmospheres) is scientifically required to protect this food?"*
- **Does NOT Answer:** *"Which material or laminate should be selected?"* (Material selection, ranking, scoring, and multi-objective Pareto optimization strictly belong to Phase 5+).
- **Commodity-Agnostic:** Operates exclusively through generic schemas and evidence properties. Zero hardcoded commodity logic.

---

## 2. Core Epistemic Result States

All physics models evaluate their outputs into three explicit states:

| Status | Definition | Example |
| :--- | :--- | :--- |
| **`CALCULATED`** | All required inputs, physical parameters, and verified evidence exist to defensibly compute the output. | Complete EMAP gas mass balance with known respiration and product mass. |
| **`PARTIALLY_CALCULATED`** | Key physical metrics (e.g. gas consumption per kg, vapor pressure gradient $\Delta p_w$) are computed, but missing physical geometry (product mass, package area) prevents whole-package requirement closure. | OTR per kg computed, but package mass is omitted. |
| **`UNKNOWN`** | Essential scientific properties (respiration, water activity, organism growth kinetics) are absent. No guessing or placeholder values are used. | Microbial shelf life when target microorganism kinetics are unmeasured. |

---

## 3. Implemented Scientific Mechanisms

### 3.1 Model A — Respiration Kinetics Model

#### Purpose
Quantifies oxygen consumption rate ($r_{O_2}$) and carbon dioxide generation rate ($r_{CO_2}$) under modified atmospheres.

#### Mathematical Formulations
1. **Base Michaelis-Menten Kinetics:**
   $$r_{O_2} = \frac{V_m [O_2]}{K_m + [O_2]}$$
2. **Uncompetitive $\text{CO}_2$-Inhibited Michaelis-Menten Kinetics:**
   $$r_{O_2} = \frac{V_m [O_2]}{K_m + \left(1 + \frac{[CO_2]}{K_i}\right) [O_2]}$$
3. **Respiration Quotient:**
   $$r_{CO_2} = RQ \cdot r_{O_2}$$

#### Scientific Sources
- Peppelenbos, H. W., & Leven, J. V. (1996). *Postharvest Biology and Technology*, 7(1-2), 27-40.
- Hertog, M. L., et al. (1998). *Postharvest Biology and Technology*, 14(3), 335-349.
- Kader, A. A. (2002). *Postharvest Technology of Horticultural Crops* (3rd Ed.).

#### Required Inputs & Units
- $[O_2]$: Headspace oxygen concentration ($\%$)
- $[CO_2]$: Headspace carbon dioxide concentration ($\%$)
- $V_m$: Maximum respiration rate ($\text{mg } O_2/\text{kg}\cdot\text{hr}$)
- $K_m$: Michaelis constant for $O_2$ ($\% O_2$)
- $K_i$: $\text{CO}_2$ inhibition constant ($\% CO_2$)
- $RQ$: Respiration quotient (dimensionless, typically $0.9\text{--}1.1$)

---

### 3.2 Model B — Gas Exchange & Headspace Mass Balance (EMAP)

#### Purpose
Computes the required package Oxygen Transmission Rate ($\text{OTR}_{pkg}$), Carbon Dioxide Transmission Rate ($\text{CO2TR}_{pkg}$), and ideal film selectivity ratio ($\beta$) to establish target equilibrium modified atmospheres.

#### Mathematical Formulation (Steady-State EMAP)
$$\text{OTR}_{pkg,req} = \frac{r_{O_2} \cdot M_{product} \cdot 24}{y_{O_2,ext} - y_{O_2,target}} \quad \left[\frac{\text{cc } O_2}{\text{package}\cdot\text{day}}\right]$$

$$\text{CO2TR}_{pkg,req} = \frac{RQ \cdot r_{O_2} \cdot M_{product} \cdot 24}{y_{CO_2,target} - y_{CO_2,ext}} \quad \left[\frac{\text{cc } CO_2}{\text{package}\cdot\text{day}}\right]$$

$$\text{Ideal } \beta\text{ ratio} = \frac{\text{CO2TR}_{pkg,req}}{\text{OTR}_{pkg,req}} = RQ \cdot \frac{y_{O_2,ext} - y_{O_2,target}}{y_{CO_2,target} - y_{CO_2,ext}}$$

#### Normalized Transmission Rate (when package area $A$ is known)
$$\text{OTR}_{area,req} = \frac{\text{OTR}_{pkg,req}}{A} \quad \left[\frac{\text{cc } O_2}{\text{m}^2\cdot\text{day}\cdot\text{atm}}\right]$$

#### Scientific Sources
- Cameron, A. C., Talasila, P. C., & Joles, D. W. (1995). *HortTechnology*, 5(1), 25-34.
- Exama, A., et al. (1993). *Journal of Food Science*, 58(6), 1365-1370.
- Robertson, G. L. (2012). *Food Packaging: Principles and Practice* (3rd Ed.), CRC Press.

---

### 3.3 Model C — Moisture Transfer & Water Activity Dynamics

#### Purpose
Computes water vapor pressure gradients ($\Delta p_w$), required Water Vapor Transmission Rate ($\text{WVTR}$), and moisture-limited shelf life.

#### Mathematical Formulation
1. **Saturation Water Vapor Pressure (Tetens/Buck Equation):**
   $$P_{sat}(T) = 0.61078 \cdot \exp\left(\frac{17.27 \cdot T}{T + 237.3}\right) \quad [\text{kPa for } T \ge 0^\circ\text{C}]$$
2. **Vapor Pressure Driving Force:**
   $$p_{w,ext} = \left(\frac{RH_{ext}}{100}\right) P_{sat}(T), \quad p_{w,food} = a_w P_{sat}(T)$$
   $$\Delta p_w = |p_{w,ext} - p_{w,food}| \quad [\text{kPa}]$$
3. **Allowable Moisture Gain/Loss and Required WVTR:**
   $$\Delta M_{H_2O} = |m_{crit} - m_{init}| \cdot \left(\frac{M_{dry}}{100}\right) \quad [\text{g } H_2O]$$
   $$\text{WVTR}_{pkg,req} = \frac{\Delta M_{H_2O}}{t_{target}} \quad \left[\frac{\text{g } H_2O}{\text{package}\cdot\text{day}}\right]$$
4. **Moisture-Limited Shelf Life:**
   $$t_{shelf,moisture} = \frac{\Delta M_{H_2O}}{\text{WVTR}_{pkg}} \quad [\text{days}]$$

#### Sorption Isotherm Models (`MoistureSorptionModel`)
- **GAB Model:** $m(a_w) = \frac{m_0 C K a_w}{(1 - K a_w)(1 - K a_w + C K a_w)}$ (valid $a_w \in [0.05, 0.90]$).
- **Oswin Model:** $m(a_w) = a \cdot [a_w / (1 - a_w)]^b$.
- **Halsey Model:** $m(a_w) = [-a / \ln(a_w)]^{1/b}$.
- **Linear Model:** $m(a_w) = \text{slope} \cdot a_w + m_0$ (low $a_w < 0.45$).

#### Scientific Sources
- Tetens, O. (1930). *Zeitschrift für Geophysik*, 6:297–309.
- Labuza, T. P., & Contreras-Medellin, R. (1981). *Cereal Foods World*, 26(7), 335-343.
- van den Berg, C. (1984). *Engineering and Food*, 1, 311-321.

---

### 3.4 Model D — Evidence-Gated Predictive Microbiology

#### Purpose
Evaluates microbial proliferation limits, lag adaptation, and microbial shelf life when organism-specific kinetics are provided with evidence provenance.

#### Mathematical Formulation
$$\log_{10} N(t) = \log_{10} N_0 + \left(\frac{\mu_{max}}{\ln 10}\right) \cdot \max(0, t - \lambda)$$
$$t_{shelf,microbial} = \lambda + \frac{\log_{10} N_{crit} - \log_{10} N_0}{\mu_{max} / \ln 10} \quad [\text{days}]$$

- **Secondary Temperature Dependency (Ratkowsky Square-Root):**
  $$\sqrt{\mu_{max}(T)} = b \cdot (T - T_{min})$$

#### Gated Execution
If target organism, initial count ($N_0$), critical limit ($N_{crit}$), or specific growth rate ($\mu_{max}$) are missing, the model strictly outputs `status = UNKNOWN`.

#### Scientific Sources
- Baranyi, J., & Roberts, T. A. (1994). *Int. J. Food Microbiol.*, 23(3-4), 277-294.
- Ratkowsky, D. A., et al. (1982). *J. Bacteriol.*, 149(1), 1-5.

---

## 4. Scientific Traceability Model

Every computed result is coupled to a `ScientificTraceability` audit record containing:
- `model_name`: Standard model designation.
- `equation_form`: Mathematical equation string.
- `equation_reference`: Academic literature citation.
- `scientific_sources`: Array of verified bibliographic sources.
- `inputs_used`: Dictionary of input parameters.
- `parameters_used`: Kinetic, physical, and thermodynamic constants.
- `parameter_sources`: Provenance for every parameter used.
- `units_used`: Standard unit mapping.
- `validity_range`: Valid domains for temperature, $a_w$, and gas concentrations.
- `assumptions`: Explicit physical and biological assumptions.
- `uncertainty_description`: Description of uncertainty propagation.
- `uncertainty_interval`: Bounded $[\min, \max]$ range.
- `failure_or_unknown_reason`: Explicit diagnostic message if calculation is `UNKNOWN` or `PARTIALLY_CALCULATED`.
- `warnings`: Active boundary alerts and extrapolation caveats.
