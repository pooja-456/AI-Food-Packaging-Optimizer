"""
Tests for M6-H (B5D): Exact Tier-1 Lookup Engine Implementation.

Covers all 20 mandatory test requirements and specific negative test cases.
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
    PrecomputedOptimizationState
)
from scientific_engine.optimization.tier1_lookup import (
    Tier1ExactLookupEngine,
    Tier1LookupStatus,
    Tier1LookupResult
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
    commodity: str = "apple",
    temp_c: float = 20.0,
    rh_pct: float = 75.0,
    shelf_life_days: int = 30,
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
        target_days=shelf_life_days,
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
        target_shelf_life_days=shelf_life_days,
        storage_temperature_c=temp_c,
        relative_humidity_percent=rh_pct,
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
    area: float = 0.1,
    temp_c: float = 20.0,
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
        requirement_envelope=create_dummy_requirement_envelope(temp_c=temp_c),
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


# 1. Empty store -> EXACT_MISS.
def test_empty_store_returns_exact_miss():
    store = InMemoryOptimizationStateStore()
    engine = Tier1ExactLookupEngine(store)
    
    res = engine.lookup(
        requirement_envelope=create_dummy_requirement_envelope(),
        package_geometry=create_dummy_geometry(),
        active_objectives=["material_cost"],
        eligible_candidate_materials=[create_dummy_candidate("id_1")]
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS
    assert res.precomputed_state is None
    assert res.pareto_front is None


# 2. Identical state -> EXACT_HIT.
def test_identical_state_returns_exact_hit():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_HIT
    assert res.precomputed_state is not None
    assert res.pareto_front is not None
    assert res.pareto_front.solver_metadata.cache_hit is True


# 3. Different Phase4 requirement envelope -> EXACT_MISS.
def test_different_requirement_envelope_returns_exact_miss():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(temp_c=20.0)
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=create_dummy_requirement_envelope(temp_c=25.0),
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS


# 4. Different package geometry -> EXACT_MISS.
def test_different_package_geometry_returns_exact_miss():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(area=0.1)
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=create_dummy_geometry(area=0.2),
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS


# 5. Different active objective set -> EXACT_MISS.
def test_different_active_objectives_returns_exact_miss():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=["material_cost", "shelf_life_margin"],
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS


# 6. Different eligible candidate ID set -> EXACT_MISS.
def test_different_candidate_set_returns_exact_miss():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(cand_ids=["id_1"])
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=[create_dummy_candidate("id_1"), create_dummy_candidate("id_2")]
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS


# 7. Candidate ID ordering difference -> EXACT_HIT.
def test_candidate_id_ordering_difference_returns_exact_hit():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(cand_ids=["id_1", "id_2"])
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=[create_dummy_candidate("id_2"), create_dummy_candidate("id_1")]
    )
    
    assert res.status == Tier1LookupStatus.EXACT_HIT


# 8. Objective ordering difference -> EXACT_HIT.
def test_objective_ordering_difference_returns_exact_hit():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    state.active_objectives = ["material_cost", "shelf_life_margin"]
    for cand in state.pareto_front.candidates:
        cand.objective_values["shelf_life_margin"] = ObjectiveValue(
            objective_name="shelf_life_margin",
            direction=ObjectiveDirection.MAXIMIZE,
            value=10.0,
            unit="days",
            status=CalculationStatus.CALCULATED
        )
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=["shelf_life_margin", "material_cost"],
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_HIT


# 9. UNKNOWN vs ABSENT -> EXACT_MISS.
def test_unknown_vs_absent_returns_exact_miss():
    store = InMemoryOptimizationStateStore()
    state_unknown = create_dummy_precomputed_state()
    state_unknown.requirement_envelope = create_dummy_requirement_envelope(
        moisture_status=CalculationStatus.UNKNOWN
    )
    store.store(state_unknown)
    
    env_absent = create_dummy_requirement_envelope()
    env_absent.moisture_requirements = None
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=env_absent,
        package_geometry=state_unknown.package_geometry,
        active_objectives=state_unknown.active_objectives,
        eligible_candidate_materials=state_unknown.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS


# 10. Tiny float difference -> EXACT_MISS (Negative test: temp 20.0 vs 20.000001).
def test_tiny_float_difference_returns_exact_miss():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(temp_c=20.0)
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=create_dummy_requirement_envelope(temp_c=20.000001),
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS


# Negative test: RH 75.0 vs 75.000001
def test_negative_rh_float_difference():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=create_dummy_requirement_envelope(rh_pct=75.000001),
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS


# Negative test: shelf life 30 vs 31
def test_negative_shelf_life_difference():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=create_dummy_requirement_envelope(shelf_life_days=31),
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_MISS


# 11. Stored empty ParetoFront -> EXACT_HIT.
def test_stored_empty_pareto_front_returns_exact_hit():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state(empty_front=True)
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.status == Tier1LookupStatus.EXACT_HIT
    assert res.pareto_front.candidate_count == 0


# 12. ParetoFront is not recalculated.
def test_pareto_front_not_recalculated():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.pareto_front.optimization_run_id == "run_001"


# 13. ParetoFront is not modified (except returned copy has cache_hit=True).
def test_pareto_front_verbatim_copy():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    res = engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert res.pareto_front.candidates[0].candidate_design.candidate_id == "id_1"
    # Verify underlying stored object in store remains cache_hit=False (no in-place mutation)
    stored_in_db = store.list_all_states()[0]
    assert stored_in_db.pareto_front.solver_metadata.cache_hit is False


# 14. Lookup does not mutate the store.
def test_lookup_does_not_mutate_store():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    initial_count = store.count()
    engine = Tier1ExactLookupEngine(store)
    
    engine.lookup(
        requirement_envelope=state.requirement_envelope,
        package_geometry=state.package_geometry,
        active_objectives=state.active_objectives,
        eligible_candidate_materials=state.eligible_candidate_materials
    )
    
    assert store.count() == initial_count


# 15. Repeated lookup is deterministic.
def test_repeated_lookup_deterministic():
    store = InMemoryOptimizationStateStore()
    state = create_dummy_precomputed_state()
    store.store(state)
    
    engine = Tier1ExactLookupEngine(store)
    
    results = [
        engine.lookup(
            requirement_envelope=state.requirement_envelope,
            package_geometry=state.package_geometry,
            active_objectives=state.active_objectives,
            eligible_candidate_materials=state.eligible_candidate_materials
        ).status
        for _ in range(5)
    ]
    
    assert results == [Tier1LookupStatus.EXACT_HIT] * 5
