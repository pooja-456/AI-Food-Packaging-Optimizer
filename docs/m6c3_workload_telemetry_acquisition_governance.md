# M6-C3 Workload Telemetry Acquisition & Governance

## 1. Status
**PROPOSED DESIGN — AWAITING REVIEW**

## 2. Source Basis
**EXISTING FACT**: This governance contract builds upon:
- `m6a_optimization_state_identity_contract.md`
- `m6a_progressive_tier_contract_freeze.md`
- `m6b5a_precomputed_state_store_contract.md`
- `m6b5b_canonical_optimization_state_representation.md`
- `m6b5c_precomputed_state_generation_contract.md`
- `m6b5d_exact_tier1_lookup_contract.md`
- `m6b5e_tier2_warm_start_state_selection_contract.md`
- `m6c_precomputed_state_enumeration_strategy.md`
- `m6c1_precomputation_population_policy.md`
- `m6c2_precomputation_workload_data_requirements.md`

## 3. Workload Telemetry Definition
**ARCHITECTURAL CONSEQUENCE**: Workload Telemetry is strictly defined as observable events generated during runtime API execution, user session requests, or solver executions. Scientific database observations (M5) and synthetic test suite outputs are explicitly excluded.

## 4. Telemetry Event Lifecycle
**PROPOSED DESIGN**: The conceptual telemetry lifecycle progresses through six distinct stages:
```
1. REAL REQUEST (Incoming user API payload)
  ↓
2. TELEMETRY EVENT (Capturing request metadata)
  ↓
3. VALIDATION / CLASSIFICATION (Checking schema validity & real vs synthetic origin)
  ↓
4. SCIENTIFIC RESOLUTION (Phase 3/4/5 execution resolving identity)
  ↓
5. RUNTIME OUTCOME RECORDING (Logging Tier-1 Hit/Miss, Tier-2, or Tier-3 execution)
  ↓
6. WORKLOAD DATASET (Analytical store for future population policy evaluation)
```

## 5. Raw Request Preservation
**SOURCE-AUTHORIZED REQUIREMENT**: The telemetry layer MUST preserve raw user request parameters (`commodity`, `variety`, `storage_temperature_c`, `relative_humidity_percent`, `target_shelf_life_days`, `PackageGeometry`, `active_objectives`). Preserving raw requests enables analyzing user domain trends independently of Phase 4 fallback changes.

## 6. Resolved Optimization State
**EXISTING FACT**: Telemetry MUST record the resulting Phase 4 envelope, geometry, active objectives, and candidate ID set. Telemetry does NOT redefine the Optimization-State Identity; it merely logs the canonical identity output by the scientific pipeline.

## 7. Event Identifiers
**PROPOSED DESIGN**: Telemetry records require technical identifiers to correlate pipeline steps:
- `request_id` (Unique request UUID)
- `optimization_invocation_id` (Solver run UUID)
- `canonical_state_identity_hash` (Precomputed state reference)
- `timestamp` (UTC ISO-8601 string)

## 8. PII / User Identity
**ARCHITECTURAL CONSEQUENCE**: Workload analysis can operate entirely on technical request metadata. User PII (names, emails, phone numbers, IP addresses, device IDs) is NOT required for optimization analysis.
**UNRESOLVED**: WORKLOAD PRIVACY POLICY NOT YET AUTHORIZED. No legal compliance or privacy framework is defined.

## 9. Real vs Synthetic Classification
**SOURCE-AUTHORIZED REQUIREMENT**: Every recorded telemetry event MUST carry a mandatory origin classification:
- `REAL_PRODUCTION`
- `REAL_PILOT`
- `REAL_MANUAL`
- `SYNTHETIC_TEST`
- `DEMO`
- `UNKNOWN`

`SYNTHETIC_TEST` and `DEMO` events MUST NEVER be counted as evidence of user demand or used to justify precomputing states.

## 10. Scientific Evidence Separation
**SOURCE-AUTHORIZED REQUIREMENT**: Scientific experimental evidence (M5 permeability measurements, respiration observations) describes physical biology. It MUST remain strictly separated from workload telemetry logs and cannot be converted into demand evidence.

## 11. Runtime Outcomes
**PROPOSED DESIGN**: Telemetry records must classify the exact runtime fulfillment path:
- `VALIDATION_FAILURE`
- `SCIENTIFIC_UNKNOWN`
- `INFEASIBLE_REQUEST`
- `EXACT_HIT` (Tier-1 fulfilled)
- `EXACT_MISS` (Tier-1 cache miss)
- `TIER2_WARM_START` (Seed refined)
- `TIER3_COLD_OPTIMIZATION` (Executed from scratch)
- `EMPTY_PARETO_FRONT`

## 12. Tier Classification
**EXISTING FACT**: Telemetry records the tier transition outcome without altering the solver pipeline logic or making performance promises.

## 13. Invalid / Failed Requests
**PROPOSED DESIGN**: Invalid or malformed requests MUST be recorded with `VALIDATION_FAILURE` tags to track system errors, but MUST be excluded from user demand analysis.

## 14. Duplicates / Retries
**PROPOSED DESIGN**: Client retries and duplicated API events MUST be recorded with matching `request_id` values to prevent misinterpreting automated retries as genuine multi-user request volume.

## 15. Timestamp / Time Horizon
**EXISTING FACT**: Timestamps are required to order events.
**UNRESOLVED**: WORKLOAD ANALYSIS TIME HORIZON NOT YET AUTHORIZED. Rolling windows (7-day, 30-day) or time-decay metrics remain unauthorized.

## 16. Retention
**UNRESOLVED**: WORKLOAD TELEMETRY RETENTION POLICY NOT YET AUTHORIZED. No data retention period or log eviction schedule is authorized.

## 17. Data Provenance
**PROPOSED DESIGN**: Workload telemetry provenance records event source, telemetry schema version, collection context, and real/synthetic classification.

## 18. Data Quality
**PROPOSED DESIGN**: Telemetry records failing schema validation, missing timestamps, or lacking real/synthetic tags must be flagged as corrupted and excluded from workload analysis.

## 19. Security / Access
**UNRESOLVED**: WORKLOAD TELEMETRY SECURITY & ACCESS CONTROL POLICY NOT YET AUTHORIZED.

## 20. Population-Policy Boundary
**SOURCE-AUTHORIZED REQUIREMENT**: Telemetry acquisition provides observational data ONLY. Collecting telemetry DOES NOT automatically authorize precomputing states. A population policy requires an independent architectural authorization decision.

## 21. Conceptual Data Layers
**PROPOSED DESIGN**:
```
RAW TELEMETRY LOGS
  ↓ (Validation & Classification)
VALIDATED WORKLOAD DATASET
  ↓ (Identity Mapping)
ANALYTICAL WORKLOAD DATASET
  ↓ (Future Authorization)
POPULATION-POLICY INPUTS
```

## 22. Minimum Acquisition Contract
- **Traceability**: `request_id`, `timestamp`, `origin_classification` (`REAL_PRODUCTION` vs `SYNTHETIC_TEST`).
- **Identity Mapping**: Raw user inputs + resolved Phase 4 envelope + package geometry + active objectives + eligible candidate IDs.
- **Fulfillment Outcome**: Tier-1 Hit/Miss flag, solver tier outcome.

## 23. Missing Authorizations
1. Telemetry logging middleware / database schema implementation.
2. Telemetry retention and privacy/PII policies.
3. Telemetry access control and security policy.
4. Formal population policy authorization.

## 24. M6-C4 Readiness
**ARCHITECTURAL CONSEQUENCE**: READY FOR REVIEW. The workload telemetry acquisition and governance contract is complete. The project is ready to proceed to M6-C4 to audit Demand-Driven Runtime Cache Population Policies.
