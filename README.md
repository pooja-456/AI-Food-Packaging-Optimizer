# AI Food Packaging Optimizer

An **inverse-design** engineering system for intelligent food packaging material recommendations.

> **PROJECT STATUS:** Phase 1–13 backend foundation and M13 initial frontend recommendation interface completed.

---

## Current Capabilities (Backend)

- **Input Validation:** Structural validation of packaging requests via Pydantic (`PackagingRequest`).
- **Scientific Evidence Structures:** Schema-backed contextual evidence models (`FoodEvidenceRecord`, `PackagingMaterialSpec`).
- **Data Ingestion & Database:** Canonical PostgreSQL model and evidence ingestion pipelines completed.
- **Property Inference:** Multi-tier evidence resolution hierarchy with uncertainty quantification (`PropertyInferenceEngine`).
- **Scientific Requirement Calculation:** Physics-based kinetics for respiration, EMAP gas exchange, moisture transfer, and microbial proliferation (`PackagingRequirementEngine`).
- **Deterministic Material Feasibility Filtering:** Evidence-backed hard-constraint barrier filtering into `FEASIBLE`, `INFEASIBLE`, or `UNKNOWN` candidate sets (`HardConstraintEvaluator`).
- **Multi-Objective Optimization:** Pareto optimization and search pipeline completed (identifying non-dominated material candidates).
- **Recommendation API & Explainability:** FastAPI endpoints delivering structured recommendations with interval-preserving objective displays and scientific explainability tracing.
- **Feedback Infrastructure:** Core infrastructure for capturing user feedback and handling model updates.
- **CORS Configuration:** FastAPI configured for local frontend integration.

## Current Capabilities (Frontend)

The **M13 Phase 1 Frontend** is implemented with the following stack and features:
- **Stack:** Vite, React, TypeScript, Tailwind CSS
- **Packaging Request Builder:** Interactive form to define food product context (commodity, mass, temperature, shelf life, etc.).
- **Recommendation Dashboard:** Displays the evaluated packaging solutions from the backend API.
- **Pareto Candidate Display:** Renders recommended material candidates (e.g., `ParetoCandidateCard`) emphasizing non-dominated solutions.
- **Interval-Preserving Objectives:** Visualizes property ranges and intervals returned by the scientific engine.
- **Typed API Client:** Strongly-typed TypeScript client for seamless communication with the backend recommendation API.

---

## Current Limitations

The project does **NOT** yet contain:
- Complete frontend UI for feedback, explainability, or full traceability.
- Automatic live model retraining loops.
- Advanced evolutionary optimization algorithms (e.g., NSGA-II, MOEA/D) or Bayesian optimization.
- Weighted scoring functions for candidates.
- Cost or carbon footprint optimization models.

---

## Core Principles

- **RULES FIRST. PHYSICS FIRST. AI ONLY WHERE IT ADDS REAL VALUE.**
- **Commodity-Agnostic:** Designed to represent arbitrary food commodity categories (fruits, vegetables, meats, seafood, dairy, bakery, processed foods).
- **Context-Aware Evidence & Traceability:** Food properties strictly retain environmental and physiological context.
- **Strict Unknown Handling:** If no evidence is available, properties remain strictly `UNKNOWN` with `None` values. The system never fabricates or hallucinates unverified numbers.

---

## Technology Stack

| Component | Stack |
|-----------|-------|
| **Backend Core** | Python 3.14, FastAPI, Pydantic v2, PostgreSQL (schema) |
| **Testing** | pytest (100% passing suite with 300+ tests), httpx |
| **Frontend UI** | Vite, React, TypeScript, Tailwind CSS |

---

## Setup & Running

### 1. Backend Setup

```bash
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Run FastAPI server:
```bash
cd backend
uvicorn app.main:app --reload
```
API available at: `http://localhost:8000` (Docs at `/docs`).

Run backend test suite:
```bash
pytest backend/tests/ -v
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

Run Vite development server:
```bash
npm run dev
```

Build for production:
```bash
npm run build
```

---

## Data Collection & Evidence Sources

The system relies on evidence-backed scientific sources for food composition, postharvest respiration kinetics, predictive microbiology, packaging barrier measurements, and thermophysical constants. Detailed catalogs are maintained in the `docs/` directory.
