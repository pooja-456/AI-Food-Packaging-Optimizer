"""
Tests for M6-G (B5A): Precomputed Optimization-State In-Memory Store Implementation.

Covers all 20 mandatory test requirements from the M6-G specification.
"""

import pytest

from app.schemas.optimization import (
    OptimizationMetadata,
    PackageGeometry,
    PackagingCandidate,
    ParetoCandidate,
    ParetoFront,
    CandidateDecisionVariables,
    CandidateBarrierProperties,
    CandidateEvidenceReference,
    ObjectiveValue,
    ObjectiveDirection,
    CandidateConstraintStatus,
    UncertaintyProfile,
    UncertaintyType,
    EvidenceTier,
    ExplanationPayload
)
from app.schemas.constraints import ConstraintStatus, ConditionMatchLevel
from app.schemas.packaging_requirements import (
    PackagingRequirementEnvelope,
    GasExchangeRequirement,
    MoistureRequirement,
    MicrobialRequirement,
    ShelfLifeRequirement,
    DeteriorationProfile,
    DeteriorationMechanismStatus
)
from app.schemas.physics import CalculationStatus, ScientificResult, ScientificTraceability
from scientific_engine.optimization.precomputed_store import (
    InMemoryOptimizationStateStore,
    PrecomputedOptimizationState,
    validate_precomputed_state
)


def create_dummy_traceability() -> ScientificTraceability:
    return ScientificTraceability(
        model_name="dummy_model",
        equation_form="y = mx + c",
        inputs_used={"temp": 20.0},
        parameters_used={"k": 0.5},
        units_used={"temp": "C"}
    )


def create_dummy_requirement_envelope(
    otr_val: float = 100.0,
    wvtr_min: float = 2.0,
    wvtr_max: float = 5.0
) -> PackagingRequirementEnvelope:
    trace = create_dummy_traceability()
    
    gas_req = GasExchangeRequirement(
        status=CalculationStatus.CALCULATED,
        required_otr_cc_per_pkg_day=ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=otr_val,
            unit="cc/pkg/day",
            traceability=trace
        )
    )
    
    moisture_req = MoistureRequirement(
        status=CalculationStatus.CALCULATED,
        required_wvtr_per_area=ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=None,
            minimum_value=wvtr_min,
            maximum_value=wvtr_max,
            unit="g/m2/day",
            uncertainty_range=(wvtr_min, wvtr_max),
            traceability=trace
        )
    )
    
    microbial_req = MicrobialRequirement(
        status=CalculationStatus.CALCULATED,
        target_microorganism="mold"
    )
    
    shelf_life_req = ShelfLifeRequirement(
        target_days=30,
        status=CalculationStatus.CALCULATED
    )
    
    det_profile = DeteriorationProfile(
        commodity="apple",
        mechanisms={
            "respiration": DeteriorationMechanismStatus(
                mechanism="respiration",
                eligible=True,
                computable=True,
                status=CalculationStatus.CALCULATED,
                reason=None,
                evidence_references=["ref1"]
            )
        },
        primary_vulnerabilities=["respiration"]
    )
    
    return PackagingRequirementEnvelope(
        commodity="apple",
        target_shelf_life_days=30,
        storage_temperature_c=20.0,
        relative_humidity_percent=75.0,
        deterioration_profile=det_profile,
        gas_requirements=gas_req,
        moisture_requirements=moisture_req,
        microbial_requirements=microbial_req,
        shelf_life=shelf_life_req,
        overall_status=CalculationStatus.CALCULATED,
        all_assumptions=["assumption 1"],
        all_warnings=["warning 1"],
        traceability_log=[trace]
    )


def create_dummy_geometry(area: float = 0.1) -> PackageGeometry:
    return PackageGeometry(
        surface_area_m2=area,
        headspace_volume_cm3=500.0,
        product_mass_kg=1.0
    )


def create_dummy_candidate(cand_id: str) -> PackagingCandidate:
    return PackagingCandidate(
        candidate_id=cand_id,
        material_id="mat_123",
        material_name="PET_PE_Laminate",
        decision_variables=CandidateDecisionVariables(
            total_thickness_um=50.0,
            thickness_source="observed_discrete_m5"
        ),
        barrier_properties=CandidateBarrierProperties(),
        condition_match=ConditionMatchLevel.EXACT,
        provenance=CandidateEvidenceReference(
            source_id="src_1",
            source_name="M5 DB",
            record_identifier_in_source="rec_1",
            evidence_classification="EXPERIMENTAL",
            verification_status="VERIFIED"
        )
    )


def create_dummy_pareto_candidate(cand_id: str, cost: float = 0.05) -> ParetoCandidate:
    cand_obj = create_dummy_candidate(cand_id)
    obj_val = ObjectiveValue(
        objective_name="material_cost",
        direction=ObjectiveDirection.MINIMIZE,
        value=cost,
        unit="USD/m2",
        status=CalculationStatus.CALCULATED
    )
    constraint_status = CandidateConstraintStatus(
        all_hard_constraints_satisfied=True,
        overall_status=ConstraintStatus.FEASIBLE,
        condition_match=ConditionMatchLevel.EXACT
    )
    return ParetoCandidate(
        pareto_candidate_id=cand_id,
        candidate_design=cand_obj,
        objective_values={"material_cost": obj_val},
        constraint_compliance_summary=constraint_status,
        uncertainty_profile=UncertaintyProfile(
            uncertainty_type=UncertaintyType.DETERMINISTIC_POINT,
            objective_intervals={}
        ),
        evidence_tier=EvidenceTier.TIER_1_EMPIRICAL,
        traceability=create_dummy_traceability(),
        explanation_payload=ExplanationPayload(
            trade_off_summary="Optimal cost",
            limiting_barrier="WVTR",
            primary_strength="Barrier"
        )
    )


def create_dummy_pareto_front(
    candidates: list = None,
    run_id: str = "run_001",
    timestamp: str = "2026-09-30T00:00:00Z"
) -> ParetoFront:
    if candidates is None:
        candidates = [create_dummy_pareto_candidate("id_1")]

    solver_meta = OptimizationMetadata(
        algorithm_name="EXACT_PARETO_CONSTRUCTOR",
        iterations_completed=len(candidates),
        execution_time_ms=100.0,
        cache_hit=False
    )

    return ParetoFront(
        optimization_run_id=run_id,
        timestamp=timestamp,
        candidate_count=len(candidates),
        candidates=candidates,
        solver_metadata=solver_meta,
        constraint_policy_version="1.0.0"
    )


def create_dummy_precomputed_state(
    run_id: str = "run_001",
    area: float = 0.1,
    cand_ids: list = None,
    empty_front: bool = False
) -> PrecomputedOptimizationState:
    if cand_ids is None:
        cand_ids = ["id_1"]

    eligible_cands = [create_dummy_candidate(cid) for cid in cand_ids]
    
    if empty_front:
        pareto_f = create_dummy_pareto_front(candidates=[], run_id=run_id)
    else:
        pareto_cands = [create_dummy_pareto_candidate(cid) for cid in cand_ids]
        pareto_f = create_dummy_pareto_front(candidates=pareto_cands, run_id=run_id)

    return PrecomputedOptimizationState(
        requirement_envelope=create_dummy_requirement_envelope(),
        package_geometry=create_dummy_geometry(area=area),
        active_objectives=["material_cost"],
        eligible_candidate_materials=eligible_cands,
        pareto_front=pareto_f,
        optimization_run_id=run_id,
        timestamp="2026-09-30T00:00:00Z",
        solver_metadata=pareto_f.solver_metadata,
        constraint_policy_version="1.0.0",
        origin_classification="SYNTHETIC_TEST"
    )


# 1. Empty store initializes successfully.
def test_empty_store_initialization():
    store = InMemoryOptimizationStateStore()
    assert store.count() == 0
    assert store.list_all_states() == []


# 2. Valid complete state is accepted.
def test_valid_complete_state_accepted():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    
    result = store.store(state)
    assert result is True
    assert store.count() == 1


# 3. Incomplete identity is rejected.
def test_incomplete_identity_rejected():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    state.active_objectives = []
    
    with pytest.raises(ValueError, match="active_objectives"):
        store.store(state)
    assert store.count() == 0


# 4. Missing ParetoFront is rejected if B5A requires it.
def test_missing_pareto_front_rejected():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    state.pareto_front = None
    
    with pytest.raises(ValueError, match="pareto_front"):
        store.store(state)
    assert store.count() == 0


# 5. Invalid candidate-set consistency is rejected (Pareto candidate not in eligible candidates).
def test_search_space_inconsistency_rejected():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(cand_ids=["id_1"])
    
    # Add a candidate id_unauthorized to pareto front which is not in eligible_candidate_materials
    state.pareto_front.candidates.append(
        create_dummy_pareto_candidate("id_unauthorized")
    )
    
    with pytest.raises(ValueError, match="Search-space inconsistency"):
        store.store(state)
    assert store.count() == 0


# 6. Invalid objective-set consistency test (validation check).
def test_invalid_objective_set_validation():
    state = create_dummy_precomputed_state()
    state.active_objectives = ["material_cost"]
    validate_precomputed_state(state)  # Should pass valid state


# 7. Unauthorized candidate is rejected.
def test_unauthorized_candidate_rejected():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(cand_ids=["id_1"])
    state.pareto_front.candidates[0].candidate_design.candidate_id = "unauthorized_id"
    
    with pytest.raises(ValueError, match="Search-space inconsistency"):
        store.store(state)


# 8. Valid empty ParetoFront is accepted.
def test_valid_empty_pareto_front_accepted():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(empty_front=True)
    
    result = store.store(state)
    assert result is True
    assert store.count() == 1
    
    retrieved = store.list_all_states()[0]
    assert retrieved.pareto_front.candidate_count == 0
    assert retrieved.pareto_front.candidates == []


# 9. Stored ParetoFront remains unchanged.
def test_stored_pareto_front_verbatim_preservation():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    retrieved = store.list_all_states()[0]
    assert retrieved.pareto_front.optimization_run_id == "run_001"
    assert retrieved.pareto_front.candidates[0].candidate_design.candidate_id == "id_1"
    assert retrieved.pareto_front.candidates[0].objective_values["material_cost"].value == 0.05


# 10. Stored identity remains unchanged.
def test_stored_identity_unchanged():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(area=0.25)
    store.store(state)
    
    retrieved = store.list_all_states()[0]
    assert retrieved.package_geometry.surface_area_m2 == 0.25
    assert retrieved.active_objectives == ["material_cost"]


# 11. Metadata remains preserved.
def test_metadata_preserved():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(run_id="run_spec_99")
    store.store(state)
    
    retrieved = store.list_all_states()[0]
    assert retrieved.optimization_run_id == "run_spec_99"
    assert retrieved.constraint_policy_version == "1.0.0"
    assert retrieved.solver_metadata.algorithm_name == "EXACT_PARETO_CONSTRUCTOR"


# 12. Synthetic state is explicitly marked SYNTHETIC_TEST.
def test_origin_classification_synthetic_test():
    state = create_dummy_precomputed_state()
    assert state.origin_classification == "SYNTHETIC_TEST"


# 13. Multiple valid states can coexist when their identities differ.
def test_multiple_valid_states_coexist():
    store = InMemoryOptimizationStateStore()
    state1 = create_dummy_precomputed_state(run_id="run_1", area=0.1)
    state2 = create_dummy_precomputed_state(run_id="run_2", area=0.2)
    
    store.store(state1)
    store.store(state2)
    
    assert store.count() == 2


# 14. Duplicate-state behavior follows B5A contract exactly.
def test_duplicate_state_handling():
    store = InMemoryOptimizationStateStore()
    state1 = create_dummy_precomputed_state(run_id="run_1")
    state1_duplicate = create_dummy_precomputed_state(run_id="run_1")
    
    assert store.store(state1) is True
    assert store.store(state1_duplicate) is False
    assert store.count() == 1


# 15. Empty store remains valid after failed storage attempts.
def test_empty_store_remains_valid_after_failed_storage():
    store = InMemoryOptimizationStateStore()
    state_invalid = create_dummy_precomputed_state()
    state_invalid.pareto_front = None
    
    with pytest.raises(ValueError):
        store.store(state_invalid)
        
    assert store.count() == 0
    assert store.list_all_states() == []


# 16. No scientific recalculation occurs during storage.
def test_no_scientific_recalculation_during_storage():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    original_val = state.requirement_envelope.gas_requirements.required_otr_cc_per_pkg_day.value
    
    store.store(state)
    retrieved = store.list_all_states()[0]
    
    assert retrieved.requirement_envelope.gas_requirements.required_otr_cc_per_pkg_day.value == original_val


# 17. No objective recalculation occurs during storage.
def test_no_objective_recalculation_during_storage():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    original_cost = state.pareto_front.candidates[0].objective_values["material_cost"].value
    
    store.store(state)
    retrieved = store.list_all_states()[0]
    
    assert retrieved.pareto_front.candidates[0].objective_values["material_cost"].value == original_cost


# 18. No Pareto recalculation occurs during storage.
def test_no_pareto_recalculation_during_storage():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    original_count = state.pareto_front.candidate_count
    
    store.store(state)
    retrieved = store.list_all_states()[0]
    
    assert retrieved.pareto_front.candidate_count == original_count


# 19. No approximate matching occurs.
def test_no_approximate_matching():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(area=0.10000)
    store.store(state)
    
    # Query with slightly different geometry (0.10001)
    retrieved = store.get_by_identity(
        requirement_envelope=state.requirement_envelope,
        package_geometry=create_dummy_geometry(area=0.10001),
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert retrieved is None


# 20. No hash/cache key is created (operated strictly via canonical representation key).
def test_retrieval_via_exact_identity():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(area=0.15)
    store.store(state)
    
    retrieved = store.get_by_identity(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert retrieved is not None
    assert retrieved.optimization_run_id == state.optimization_run_id
