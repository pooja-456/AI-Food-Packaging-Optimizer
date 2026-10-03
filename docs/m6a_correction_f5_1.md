# M6-A CORRECTION REPORT — FINDING F-5.1

**Project**: AI-Based Intelligent Food Packaging Material Recommendation System  
**Finding**: F-5.1 (Thickness List Mismatch)  
**Correction Date**: 2026-09-29  
**Source Audit**: `docs/m6a_forensic_design_audit.md`  

---

## 1. Original Incorrect Domain

M6-A design artifacts claimed the following discrete thickness search domain:

```
{15, 25, 30, 40, 45, 50, 65} μm
```

With bounds: $15.0 \le t \le 65.0$

This appeared in:
- `docs/m6a_decision_variables.md` (L41, L66, L67)
- `data/reference/m6a_data_availability_matrix.json` (L70)

---

## 2. Actual M5 Evidence Domain

Independent query of all `MaterialBarrierObservation.thickness_value` records across the verified M5 database:

```
Global observed thickness values: {12.0, 15.0, 25.0, 30.0, 40.0, 50.0, 70.0} μm
```

With bounds: $12.0 \le t \le 70.0$

### Discrepancy

| Value | In M6-A Claim | In M5 Evidence | Action |
|-------|--------------|---------------|--------|
| 12 μm | ❌ Absent | ✅ BOPET 12 μm | ADDED |
| 15 μm | ✅ | ✅ BOPA 15 μm, EVOH 15 μm | — |
| 25 μm | ✅ | ✅ PBAT 25 μm, PHA 25 μm | — |
| 30 μm | ✅ | ✅ BOPP 30 μm, PLA 30 μm | — |
| 40 μm | ✅ | ✅ HDPE 40 μm | — |
| **45 μm** | ❌ Phantom | ❌ NOT IN M5 | **REMOVED** |
| 50 μm | ✅ | ✅ LDPE 50 μm | — |
| **65 μm** | ❌ Phantom | ❌ NOT IN M5 | **REMOVED** |
| 70 μm | ❌ Absent | ✅ Multilayer PET/EVOH/PE 70 μm | ADDED |

---

## 3. Material-Specific Thickness Limitation

Each material in M5 currently has exactly **one** observed thickness:

| Material | Thickness (μm) |
|----------|:--------------:|
| BOPET 12 μm | 12.0 |
| BOPA 15 μm | 15.0 |
| EVOH | 15.0 |
| PBAT Film | 25.0 |
| PHA / PHBV | 25.0 |
| BOPP 30 μm | 30.0 |
| PLA | 30.0 |
| PLA Film Specimen | 30.0 |
| HDPE 40 μm | 40.0 |
| LDPE 50 μm | 50.0 |
| Multilayer PET/EVOH/PE | 70.0 |

The corrected set `{12, 15, 25, 30, 40, 50, 70}` represents **global observed thickness values** across all materials. It does NOT mean every material supports every thickness.

No material-specific thickness mapping was invented. Future candidate generation must respect material-specific evidence: a candidate for LDPE must use 50.0 μm (the only LDPE thickness in M5), not 12.0 μm.

---

## 4. Files Changed

| File | Change |
|------|--------|
| `docs/m6a_decision_variables.md` L41 | Corrected table row: range $12.0 \le t \le 70.0$, set {12, 15, 25, 30, 40, 50, 70} |
| `docs/m6a_decision_variables.md` L66 | Corrected illustrative example: "inside a $70 \mu\text{m}$ structure" (was $45 \mu\text{m}$) |
| `docs/m6a_decision_variables.md` L67 | Corrected gauge list to {12, 15, 25, 30, 40, 50, 70}; added material-specific caveat |
| `data/reference/m6a_data_availability_matrix.json` L70 | Corrected `current_coverage` string to {12, 15, 25, 30, 40, 50, 70} with material-specific caveat |

### Files NOT Changed (confirmed clean)

| File | Reason |
|------|--------|
| `docs/m6a_optimization_problem_definition.md` | Does not contain specific thickness values |
| `docs/m6a_objective_contract.md` | Does not contain specific thickness values |
| `docs/m6a_optimization_data_contract.md` | Does not contain specific thickness values |
| `docs/m6a_forensic_design_audit.md` | Audit report references finding — not corrected (audit is read-only record) |

---

## 5. Validation

### 5.1 — Absence of Phantom Values

Searched all corrected M6-A artifacts for `45` and `65` as thickness values:

- `docs/m6a_decision_variables.md`: **0 hits**
- `data/reference/m6a_data_availability_matrix.json`: **0 hits**
- `docs/m6a_optimization_problem_definition.md`: **0 hits**
- `docs/m6a_objective_contract.md`: **0 hits**
- `docs/m6a_optimization_data_contract.md`: **0 hits**

45 μm and 65 μm no longer appear as supported thickness values in any M6-A design artifact.

### 5.2 — Presence of Correct Values

Confirmed `{12, 15, 25, 30, 40, 50, 70}` appears in:
- `docs/m6a_decision_variables.md` L41 (table row)
- `docs/m6a_decision_variables.md` L67 (rationale paragraph)
- `data/reference/m6a_data_availability_matrix.json` L70 (coverage string)

### 5.3 — No Material-Specific Mapping Invented

The corrected text explicitly states:
> "Global observed thickness values are available; material-specific candidate eligibility requires evidence-level mapping."

No mapping from arbitrary thicknesses to arbitrary materials was created.

### 5.4 — No Implementation Code Modified

Zero `.py` files were modified. Only `.md` and `.json` design documentation was corrected.

---

## 6. Test Result

```
171 passed, 1 warning in 3.34s
```

- 171 tests passing
- 0 failures
- 1 warning (Starlette deprecation — pre-existing, unrelated)

No regression detected.

---

## 7. Scope Boundary

- M5 database, schema, and ingestion pipeline: NOT MODIFIED
- Phase 3/4/5 scientific engine: NOT MODIFIED
- No optimization implementation introduced
- No M6-B implementation begun
