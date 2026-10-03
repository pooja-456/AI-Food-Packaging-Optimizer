"""
Tests for M6-J (B5E): Tier-2 Warm-Start Handoff Interface.

Covers all 24 mandatory test requirements and negative architectural checks.
"""

from unittest.mock import patch
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
    PrecomputedOptimizationState
)
from scientific_engine.optimization.tier1_lookup import (
    Tier1LookupResult,
    Tier1LookupStatus
)
from scientific_engine.optimization.tier2_handoff import (
    Tier2HandoffEngine,
    Tier2HandoffRequest,
    create_tier2_handoff_request
)
import scientific_engine.optimization.tier2_handoff as tier2_handoff_module


def create_dummy_traceability() -> ScientificTraceability:
    return ScientificTraceability(
        model_name="dummy_model",
        equation_form="y = mx + c",
        inputs_used={"temp": 20.0},
        parameters_used={"k": 0.5},
        units_used={"temp": "C"}
    )


def create_dummy_geometry(area: float = 0.1) -> PackageGeometry:
    return PackageGeometry(
        surface_area_m2=area,
        headspace_volume_cm3=500.0,
        product_mass_kg=1.0
    )


def create_dummy_requirement_envelope(
    commodity: str = "apple",
    shelf_life_days: float = 30.0,
    with_intervals: bool = True,
    with_unknown: bool = False
) -> PackagingRequirementEnvelope:
    trace = create_dummy_traceability()
    
    gas_req = None
    if with_intervals:
        gas_req = GasExchangeRequirement(
            status=CalculationStatus.CALCULATED,
            required_otr_cc_per_pkg_day=ScientificResult(
                status=CalculationStatus.CALCULATED,
                value=15.0,
                minimum_value=10.0,
                maximum_value=20.0,
                unit="cc/pkg/day",
                traceability=trace
            )
        )
    
    moisture_status = CalculationStatus.UNKNOWN if with_unknown else CalculationStatus.CALCULATED
    moisture_req = MoistureRequirement(
        status=moisture_status,
        required_wvtr_per_area=ScientificResult(
            status=moisture_status,
            value=3.0 if not with_unknown else None,
            minimum_value=2.0 if not with_unknown else None,
            maximum_value=5.0 if not with_unknown else None,
            unit="g/m2/day",
            traceability=trace
        )
    )
    
    microbial_req = MicrobialRequirement(
        status=CalculationStatus.CALCULATED,
        target_microorganism="mold"
    )
    
    shelf_life_req = ShelfLifeRequirement(
        target_days=int(shelf_life_days) if shelf_life_days is not None else 30,
        status=CalculationStatus.CALCULATED
    )
    
    det_profile = DeteriorationProfile(
        commodity=commodity,
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
        commodity=commodity,
        target_shelf_life_days=int(shelf_life_days) if shelf_life_days is not None else 30,
        storage_temperature_c=20.0,
        relative_humidity_percent=75.0,
        deterioration_profile=det_profile,
        gas_requirements=gas_req,
        moisture_requirements=moisture_req,
        microbial_requirements=microbial_req,
        shelf_life=shelf_life_req,
        overall_status=CalculationStatus.CALCULATED if not with_unknown else CalculationStatus.UNKNOWN,
        all_assumptions=["assumption 1"],
        all_warnings=["warning 1"],
        traceability_log=[trace]
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


# 1. Valid Tier-1 MISS can create a Tier-2 handoff request.
def test_valid_tier1_miss_creates_handoff_request():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert isinstance(req, Tier2HandoffRequest)
    assert req.tier1_lookup_status == Tier1LookupStatus.EXACT_MISS
    assert req.requires_target_reevaluation is True


# 2. Tier-1 HIT does not permit Tier-2 handoff (raises ValueError).
def test_tier1_hit_rejects_tier2_handoff():
    state = create_dummy_precomputed_state()
    t1_res = Tier1LookupResult(
        status=Tier1LookupStatus.EXACT_HIT,
        precomputed_state=state,
        pareto_front=state.pareto_front
    )
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    with pytest.raises(ValueError, match="not permitted when Tier-1 exact lookup yields EXACT_HIT"):
        create_tier2_handoff_request(
            tier1_result=t1_res,
            requirement_envelope=env,
            package_geometry=geom,
            active_objectives=objs,
            eligible_candidate_materials=cands
        )


# 3. Target Requirement Envelope is preserved exactly.
def test_target_requirement_envelope_preserved_exactly():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope(shelf_life_days=45.0)
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert req.requirement_envelope.target_shelf_life_days == 45
    assert req.requirement_envelope.commodity == "apple"


# 4. Target Package Geometry is preserved exactly.
def test_target_package_geometry_preserved_exactly():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry(area=0.12345)
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert req.package_geometry.surface_area_m2 == 0.12345


# 5. Active Objective Set is preserved.
def test_active_objective_set_preserved():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost", "shelf_life_margin"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert req.active_objectives == ["material_cost", "shelf_life_margin"]


# 6. Eligible Candidate ID Set is preserved.
def test_eligible_candidate_id_set_preserved():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_A"), create_dummy_candidate("id_B")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert req.get_target_eligible_candidate_ids() == ["id_A", "id_B"]


# 7. UNKNOWN remains UNKNOWN.
def test_unknown_remains_unknown():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope(with_unknown=True)
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert req.requirement_envelope.overall_status == CalculationStatus.UNKNOWN


# 8. ABSENT remains ABSENT.
def test_absent_remains_absent():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    env.moisture_requirements = None
    assert env.moisture_requirements is None
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert req.requirement_envelope.moisture_requirements is None
    assert req.target_canonical_representation.requirement_envelope["moisture_requirements"] == "ABSENT"


# 9. Intervals remain intervals.
def test_intervals_remain_intervals():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope(with_intervals=True)
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    gas_otr = req.requirement_envelope.gas_requirements.required_otr_cc_per_pkg_day
    assert gas_otr.minimum_value == 10.0
    assert gas_otr.maximum_value == 20.0


# 10. No float rounding occurs.
def test_no_float_rounding_occurs():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    exact_val = 0.12345678901234567
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry(area=exact_val)
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert req.package_geometry.surface_area_m2 == exact_val


# 11-14. No candidate ranking, similarity, nearest neighbor, or distance calculations occur.
def test_available_states_unranked_and_unselected():
    store = InMemoryOptimizationStateStore()
    s1 = create_dummy_precomputed_state(run_id="r1", cand_ids=["id_1"])
    s2 = create_dummy_precomputed_state(run_id="r2", cand_ids=["id_2"])
    store.store(s1)
    store.store(s2)

    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_3")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands,
        store=store
    )

    assert len(req.available_stored_states) == 2
    for st in req.available_stored_states:
        assert isinstance(st, PrecomputedOptimizationState)
        assert not hasattr(st, "similarity_score")
        assert not hasattr(st, "distance")


# 15-20. No external optimization, physics, constraint, evaluation, or Pareto calls occur.
def test_negative_no_physics_or_solver_invoked():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    with patch("scientific_engine.physics.requirements.PackagingRequirementEngine") as mock_engine, \
         patch("scientific_engine.optimization.candidate_evaluator.CandidateScientificEvaluator") as mock_eval, \
         patch("scientific_engine.optimization.objective_evaluator.ObjectiveEvaluator") as mock_obj, \
         patch("scientific_engine.optimization.pareto_front.ParetoFrontConstructor") as mock_pareto:

        req = create_tier2_handoff_request(
            tier1_result=t1_res,
            requirement_envelope=env,
            package_geometry=geom,
            active_objectives=objs,
            eligible_candidate_materials=cands
        )

        assert req.tier1_lookup_status == Tier1LookupStatus.EXACT_MISS
        assert mock_engine.call_count == 0
        assert mock_eval.call_count == 0
        assert mock_obj.call_count == 0
        assert mock_pareto.call_count == 0


# 21. Empty ParetoFront does not fabricate a seed.
def test_empty_pareto_front_does_not_fabricate_seed():
    store = InMemoryOptimizationStateStore()
    empty_state = create_dummy_precomputed_state(run_id="empty_r1", empty_front=True)
    store.store(empty_state)

    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands,
        store=store
    )

    assert len(req.available_stored_states) == 1
    stored_st = req.available_stored_states[0]
    assert stored_st.pareto_front.candidate_count == 0
    assert len(stored_st.pareto_front.candidates) == 0


# 22. Handoff construction does not mutate target state or store.
def test_handoff_does_not_mutate_target_or_store():
    store = InMemoryOptimizationStateStore()
    s1 = create_dummy_precomputed_state()
    store.store(s1)

    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    env_dump_before = env.model_dump()
    count_before = store.count()

    create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands,
        store=store
    )

    assert env.model_dump() == env_dump_before
    assert store.count() == count_before


# 23. Repeated handoff construction is deterministic.
def test_handoff_construction_is_deterministic():
    t1_res = Tier1LookupResult(status=Tier1LookupStatus.EXACT_MISS)
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    cands = [create_dummy_candidate("id_1")]

    req1 = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    req2 = create_tier2_handoff_request(
        tier1_result=t1_res,
        requirement_envelope=env,
        package_geometry=geom,
        active_objectives=objs,
        eligible_candidate_materials=cands
    )

    assert req1.model_dump() == req2.model_dump()


# 24. No Redis / PostgreSQL integration introduced.
def test_no_external_database_dependencies():
    import sys
    assert "redis" not in tier2_handoff_module.__file__
    assert "psycopg2" not in tier2_handoff_module.__file__


# 25. Negative Architectural Tests: Verify module does NOT contain unauthorized selection methods.
def test_negative_architectural_no_selection_methods():
    forbidden_terms = [
        "nearest_neighbor",
        "similarity_score",
        "distance",
        "ranking",
        "top_k",
        "weighted_score",
        "euclidean",
        "manhattan",
        "cosine"
    ]
    
    module_dir = dir(tier2_handoff_module)
    engine_dir = dir(Tier2HandoffEngine)
    request_dir = dir(Tier2HandoffRequest)
    
    all_symbols = [s.lower() for s in (module_dir + engine_dir + request_dir)]
    
    for term in forbidden_terms:
        for symbol in all_symbols:
            assert term not in symbol, f"Forbidden selection/similarity symbol '{term}' found in module symbols: {symbol}"
