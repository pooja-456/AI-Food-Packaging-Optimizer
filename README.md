# AI Food Packaging Optimizer

An **inverse-design** engineering system for intelligent food packaging material recommendations.

> **PROJECT STATUS:** Phase 1–5 completed.
> Precomputed lattice, multi-objective optimization, data acquisition pipelines, database, and material recommendation ranking are **not yet implemented**.

---

## Current Capabilities

- **Input Validation:** Structural validation of packaging requests via Pydantic (`PackagingRequest`).
- **Scientific Evidence Structures:** Schema-backed contextual evidence models (`FoodEvidenceRecord`, `PackagingMaterialSpec`).
- **Property Inference:** Multi-tier evidence resolution hierarchy with uncertainty quantification (`PropertyInferenceEngine`).
- **Scientific Requirement Calculation:** Physics-based kinetics for respiration, EMAP gas exchange, moisture transfer, and microbial proliferation (`PackagingRequirementEngine`).
- **Deterministic Material Feasibility Filtering:** Evidence-backed hard-constraint barrier filtering into `FEASIBLE`, `INFEASIBLE`, or `UNKNOWN` candidate sets (`HardConstraintEvaluator`).

---

## Current Limitations

The project does **NOT** yet contain the complete:
- Production data acquisition pipeline
- Data cleaning pipeline
- Production database
- Optimization layer (NSGA-II, Pareto optimization)
- AI recommendation layer
- Frontend / application layer

---

## Current Implemented Architecture

```
User Input
    ↓
Input Validation
    ↓
Property Inference
    ↓
Scientific Requirement Engine
    ↓
Deterministic Hard-Constraint Filter
    ↓
FEASIBLE / INFEASIBLE / UNKNOWN
```

---

## Next Development Track

```
Data requirements
→ source audit
→ data collection
→ cleaning
→ validation
→ database design
→ database population
```

---

## Core Principles

- **RULES FIRST. PHYSICS FIRST. AI ONLY WHERE IT ADDS REAL VALUE.**
- **Commodity-Agnostic:** Designed to represent arbitrary food commodity categories (fruits, vegetables, meats, seafood, dairy, bakery, processed foods). Specific commodities serve solely as validation test cases for complex multi-attribute biological behavior.
- **Context-Aware Evidence & Traceability:** Food properties strictly retain environmental and physiological context. Conflicting scientific observations coexist independently.
- **Strict Unknown Handling:** If no evidence is available, properties remain strictly `UNKNOWN` with `None` values. The system never fabricates or hallucinates unverified numbers.
- **No Material Selection in Phase 4/5:** Phase 4 strictly evaluates performance requirements (OTR, CO2TR, WVTR, water activity, headspace atmospheres), while Phase 5 filters materials into `FEASIBLE`, `INFEASIBLE`, or `UNKNOWN` candidate sets without ranking or scoring.

---

## Development Phases Status

### Phase 1 — Project Foundation + Input Validation ✅
- Base directory structure and virtual environment setup
- `PackagingRequest` Pydantic model with structural validation
- `PropertyStatus` epistemic model (`measured`, `literature`, `inferred`, `unknown`)
- `GET /health` FastAPI endpoint
- Pytest suite for Phase 1 (28 tests)

### Phase 2 — Generic Scientific Knowledge Foundation ✅
- Context-aware `FoodEvidenceRecord` & `FoodEvidenceDataset` data models
- Comprehensive packaging material schema `PackagingMaterialSpec` (monolayers, multilayers, laminates, foil, bio-polymers, active packaging, coated substrates)
- Environmental test condition preservation (`MaterialPropertyEvidence` with test temp, test RH, ASTM/ISO standard)
- Standard controlled vocabularies (`FoodProperty`, `CommodityCategory`, `ProcessingState`, `ProductForm`, `MaturityStage`, `MaterialCategory`, `PackagingProperty`)
- Reference datasets with genuine citations (`data/reference/food_evidence.json`, `data/reference/packaging_materials.json`)
- Scientific documentation (`docs/scientific_knowledge_foundation.md`)

### Phase 3 — Generic Property Inference Engine ✅
- `PropertyInferenceEngine` & `infer_commodity_properties` pipeline service
- Inference resolution hierarchy (`user_supplied` $\rightarrow$ `exact_context_match` $\rightarrow$ `variety_fallback` $\rightarrow$ `form_fallback` $\rightarrow$ `temperature_match` $\rightarrow$ `closest_temperature_bound` $\rightarrow$ `unknown`)
- Non-destructive uncertainty quantification ($[\min_{\text{obs}}, \max_{\text{obs}}]$)
- Full citation and bibliographic traceability
- Strict unknown handling with explicit domain warnings

### Phase 4 — Mechanism-Aware Scientific Packaging Requirement Engine ✅
- Model A: Respiration kinetics (Michaelis-Menten with uncompetitive CO2 inhibition + empirical evidence rates)
- Model B: Equilibrium Modified Atmosphere Packaging (EMAP) gas exchange mass balances ($\text{OTR}_{pkg,req}$, $\text{CO2TR}_{pkg,req}$, ideal $\beta$ ratio)
- Model C: Moisture transfer driving forces ($\Delta p_w$ via Tetens $P_{sat}(T)$ equation), sorption models (GAB, Oswin, Halsey, Linear), and $\text{WVTR}_{req}$
- Model D: Evidence-gated predictive microbial growth framework (Baranyi/exponential kinetics + Ratkowsky square-root temperature model)
- Deterioration mode assessment matrix (`DeteriorationProfile`)
- Packaging requirement synthesis (`PackagingRequirementEnvelope`) with full provenance audit trail (`ScientificTraceability`)

### Phase 5 — Deterministic Hard-Constraint Filtering Engine ✅
- `ConstraintStatus` enum (`FEASIBLE`, `INFEASIBLE`, `UNKNOWN`)
- `ComparisonOperator` enum (`LE`, `GE`, `EQ`, `IN_RANGE`) with operator semantics derived from Phase 4 physics (OTR/CO2TR $\ge$, WVTR $\le$)
- `ConditionMatchLevel` enum (`EXACT`, `SUPPORTED`, `INCOMPATIBLE`, `UNKNOWN`) with evidence-backed condition compatibility checking
- `HardConstraintEvaluator` candidate-level filtering orchestrator
- Area-normalised unit matching (`cc/(m²·day·atm)`, `g/(m²·day)`)
- Multilayer composite property handling
- Complete Pytest suite expanded to 151 tests (100% passing)
- Scientific specification document (`docs/phase5_constraint_specification.md`)

### Future Phases (Not Yet Implemented)
- **Phase 6:** Precomputed Optimization Lattice + Cache
- **Phase 7:** AI-Assisted Inverse-Design Optimization
- **Phase 8:** Multi-Objective Pareto Optimization (NSGA-II)
- **Phase 9:** Explainability and Counterfactual Analysis
- **Phase 10:** Recommendation Output & Real-World Continual Feedback Loop

---

## Technology Stack (Current)

| Tool | Purpose |
|------|---------|
| Python 3.14 | Core language |
| FastAPI | Web framework |
| Pydantic v2 | Data validation, scientific schemas, inference profiles, requirement envelopes |
| pytest | Test suite runner |
| httpx | FastAPI test client |

---

## Setup & Running

### 1. Create and activate virtual environment

```bash
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run FastAPI server

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000` (Docs at `/docs`).

### 4. Run test suite

```bash
pytest backend/tests/ -v
```

---

## Project Structure

```
AI-Food-Packaging-Optimizer/
├── .venv/                         # Python virtual environment (ignored by git)
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # GET /health
│   │   ├── core/config.py         # App settings
│   │   ├── models/                # (future: ORM models)
│   │   ├── schemas/
│   │   │   ├── candidate_feasibility.py # CandidateFeasibility & FilteringResult schemas
│   │   │   ├── constraints.py     # ConstraintStatus, ComparisonOperator & ConstraintEvaluation
│   │   │   ├── food_evidence.py   # FoodEvidenceRecord & dataset
│   │   │   ├── inference.py       # InferredProperty & profile models
│   │   │   ├── material_evidence.py # PackagingMaterialSpec & properties
│   │   │   ├── packaging_request.py # PackagingRequest model
│   │   │   ├── packaging_requirements.py # Requirement envelope schemas
│   │   │   ├── physics.py         # ScientificTraceability & result models
│   │   │   ├── property_status.py # PropertyStatus 4-state model
│   │   │   └── vocabularies.py    # Controlled scientific vocabularies
│   │   └── main.py
│   └── tests/
│       ├── test_constraints.py
│       ├── test_food_evidence.py
│       ├── test_gas_exchange.py
│       ├── test_health.py
│       ├── test_material_evidence.py
│       ├── test_microbial.py
│       ├── test_moisture.py
│       ├── test_packaging_request.py
│       ├── test_packaging_requirements.py
│       ├── test_physics_traceability.py
│       ├── test_physics_unknowns.py
│       ├── test_property_inference.py
│       ├── test_property_status.py
│       ├── test_respiration.py
│       └── test_sorption.py
├── scientific_engine/
│   ├── constraints/               # Phase 5 hard-constraint filtering engine
│   ├── inference/                 # PropertyInferenceEngine implementation
│   └── physics/                   # Respiration, GasExchange, Moisture, Sorption, Microbial, RequirementEngine
├── data/
│   ├── raw/                       # Placeholders for raw ingested datasets
│   ├── processed/                 # Placeholders for cleaned datasets
│   └── reference/                 # Small reference datasets (food_evidence.json, packaging_materials.json)
├── database/                      # Placeholders for database schemas and seeds
├── optimization/                  # Placeholders for optimization models and lattice
├── frontend/                      # (future phases)
├── docs/                          # Scientific specifications
├── tests/                         # Root tests placeholder
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```
