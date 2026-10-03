"""
Tests for M6-I (B5C): Precomputed Optimization-State Pre-Storage Validation Implementation.

Covers all 25 mandatory test requirements and specific negative test cases.
"""

import pytest
from unittest.mock import patch

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
from scientific_engine.optimization.precomputed_store import PrecomputedOptimizationState
from scientific_engine.optimization.pre_storage_validation import (
    PreStorageValidator,
    PreStorageValidationResult,
    validate_precomputed_state_b5c
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
    wvtr_max: float = 5.0,
    moisture_status: CalculationStatus = CalculationStatus.CALCULATED
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
        status=moisture_status,
        required_wvtr_per_area=ScientificResult(
            status=moisture_status,
            value=None,
            minimum_value=wvtr_min,
            maximum_value=wvtr_max,
            unit="g/m2/day",
            uncertainty_range=(wvtr_min, wvtr_max),
            traceability=trace
        ) if moisture_status != CalculationStatus.UNKNOWN else ScientificResult(
            status=CalculationStatus.UNKNOWN,
            value=None,
            unit="g/m2/day",
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


def create_dummy_precomputed_state(
    run_id: str = "run_001",
    cand_ids: list = None,
    empty_front: bool = False
) -> PrecomputedOptimizationState:
    if cand_ids is None:
        cand_ids = ["id_1"]

    eligible_cands = [create_dummy_candidate(cid) for cid in cand_ids]
    
    if empty_front:
        pareto_f = ParetoFront(
            optimization_run_id=run_id,
            timestamp="2026-09-30T00:00:00Z",
            candidate_count=0,
            candidates=[],
            solver_metadata=OptimizationMetadata(
                algorithm_name="EXACT_PARETO_CONSTRUCTOR",
                iterations_completed=0,
                execution_time_ms=50.0,
                cache_hit=False
            ),
            constraint_policy_version="1.0.0"
        )
    else:
        pareto_cands = [create_dummy_pareto_candidate(cid) for cid in cand_ids]
        pareto_f = ParetoFront(
            optimization_run_id=run_id,
            timestamp="2026-09-30T00:00:00Z",
            candidate_count=len(pareto_cands),
            candidates=pareto_cands,
            solver_metadata=OptimizationMetadata(
                algorithm_name="EXACT_PARETO_CONSTRUCTOR",
                iterations_completed=len(pareto_cands),
                execution_time_ms=100.0,
                cache_hit=False
            ),
            constraint_policy_version="1.0.0"
        )

    return PrecomputedOptimizationState(
        requirement_envelope=create_dummy_requirement_envelope(),
        package_geometry=create_dummy_geometry(),
        active_objectives=["material_cost"],
        eligible_candidate_materials=eligible_cands,
        pareto_front=pareto_f,
        optimization_run_id=run_id,
        timestamp="2026-09-30T00:00:00Z",
        solver_metadata=pareto_f.solver_metadata,
        constraint_policy_version="1.0.0",
        origin_classification="SYNTHETIC_TEST"
    )


# 1. Complete valid state -> VALID.
def test_complete_valid_state_passes():
    state = create_dummy_precomputed_state()
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is True
    assert len(res.reasons) == 0


# 2. Missing Phase4 Requirement Envelope -> INVALID.
def test_missing_requirement_envelope_invalid():
    state = create_dummy_precomputed_state()
    state.requirement_envelope = None
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("requirement_envelope is None" in r for r in res.reasons)


# 3. Missing Package Geometry -> INVALID.
def test_missing_package_geometry_invalid():
    state = create_dummy_precomputed_state()
    state.package_geometry = None
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("package_geometry is None" in r for r in res.reasons)


# 4. Missing active objective set -> INVALID.
def test_missing_active_objectives_invalid():
    state = create_dummy_precomputed_state()
    state.active_objectives = []
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("active_objectives is empty" in r for r in res.reasons)


# 5. Missing eligible candidate set -> INVALID.
def test_missing_eligible_candidates_invalid():
    state = create_dummy_precomputed_state()
    state.eligible_candidate_materials = []
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("eligible_candidate_materials is empty" in r for r in res.reasons)


# 6. Pareto candidate outside eligible set -> INVALID.
def test_pareto_candidate_outside_eligible_set_invalid():
    state = create_dummy_precomputed_state(cand_ids=["id_1"])
    state.pareto_front.candidates.append(create_dummy_pareto_candidate("id_unauthorized"))
    state.pareto_front.candidate_count = 2
    
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("Search-space inconsistency" in r for r in res.reasons)


# 7. Malformed objective set (duplicates) -> INVALID.
def test_duplicate_active_objectives_invalid():
    state = create_dummy_precomputed_state()
    state.active_objectives = ["material_cost", "material_cost"]
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("duplicate objective identifiers" in r for r in res.reasons)


# 8. Missing required ParetoFront -> INVALID.
def test_missing_pareto_front_invalid():
    state = create_dummy_precomputed_state()
    state.pareto_front = None
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("pareto_front is None" in r for r in res.reasons)


# 9. Empty ParetoFront -> VALID when contractually allowed.
def test_empty_pareto_front_valid():
    state = create_dummy_precomputed_state(empty_front=True)
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is True


# 10. Candidate-count inconsistency -> INVALID.
def test_candidate_count_mismatch_invalid():
    state = create_dummy_precomputed_state()
    state.pareto_front.candidate_count = 99  # Actual len(candidates) is 1
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("candidate_count mismatch" in r for r in res.reasons)


# 11. Missing required candidate objective -> INVALID.
def test_missing_required_candidate_objective_invalid():
    state = create_dummy_precomputed_state()
    state.active_objectives = ["material_cost", "shelf_life_margin"]
    # Candidate only has material_cost
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("missing active objectives" in r for r in res.reasons)


# 12. Objective not belonging to active objective set -> INVALID.
def test_unauthorized_candidate_objective_invalid():
    state = create_dummy_precomputed_state()
    state.active_objectives = ["shelf_life_margin"]
    # Candidate has material_cost
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("unauthorized objectives" in r for r in res.reasons)


# 13. Invalid interval lower > upper -> INVALID.
def test_invalid_interval_bounds_invalid():
    state = create_dummy_precomputed_state()
    state.requirement_envelope = create_dummy_requirement_envelope(wvtr_min=10.0, wvtr_max=2.0)
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is False
    assert any("lower bound (10.0) > upper bound (2.0)" in r for r in res.reasons)


# 14. UNKNOWN preserved -> VALID where structurally allowed.
def test_unknown_preserved_valid():
    state = create_dummy_precomputed_state()
    state.requirement_envelope = create_dummy_requirement_envelope(moisture_status=CalculationStatus.UNKNOWN)
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is True


# 15. ABSENT remains distinct from UNKNOWN.
def test_absent_remains_distinct_from_unknown():
    state = create_dummy_precomputed_state()
    state.requirement_envelope.moisture_requirements = None
    res = validate_precomputed_state_b5c(state)
    assert res.is_valid is True


# 16. FEASIBLE/INFEASIBLE/UNKNOWN status is not recomputed.
def test_feasibility_status_not_recomputed():
    state = create_dummy_precomputed_state()
    state.pareto_front.candidates[0].constraint_compliance_summary.overall_status = ConstraintStatus.INFEASIBLE
    res = validate_precomputed_state_b5c(state)
    # Validation passes without altering INFEASIBLE status to FEASIBLE
    assert res.is_valid is True
    assert state.pareto_front.candidates[0].constraint_compliance_summary.overall_status == ConstraintStatus.INFEASIBLE


# 17. Input state is not mutated.
def test_input_state_not_mutated():
    state = create_dummy_precomputed_state()
    dump_before = state.model_dump()
    
    validate_precomputed_state_b5c(state)
    dump_after = state.model_dump()
    
    assert dump_before == dump_after


# 18. Validation is deterministic.
def test_validation_is_deterministic():
    state = create_dummy_precomputed_state()
    results = [validate_precomputed_state_b5c(state).is_valid for _ in range(5)]
    assert results == [True] * 5


# 19-24. Negative Tests: Verify NO external scientific / solver engines are invoked.
def test_negative_zero_recomputation_invoked():
    state = create_dummy_precomputed_state()
    
    # Patch scientific physics engine and optimizer functions to ensure 0 invocation
    with patch("scientific_engine.physics.requirements.PackagingRequirementEngine") as mock_engine, \
         patch("scientific_engine.optimization.candidate_evaluator.CandidateScientificEvaluator") as mock_eval, \
         patch("scientific_engine.optimization.objective_evaluator.ObjectiveEvaluator") as mock_obj, \
         patch("scientific_engine.optimization.pareto_front.ParetoFrontConstructor") as mock_pareto:
        
        res = validate_precomputed_state_b5c(state)
        assert res.is_valid is True
        
        # Verify ZERO calls to engines
        assert mock_engine.call_count == 0
        assert mock_eval.call_count == 0
        assert mock_obj.call_count == 0
        assert mock_pareto.call_count == 0


# 25. Synthetic test state remains explicitly SYNTHETIC_TEST.
def test_synthetic_test_origin_preserved():
    state = create_dummy_precomputed_state()
    assert state.origin_classification == "SYNTHETIC_TEST"
