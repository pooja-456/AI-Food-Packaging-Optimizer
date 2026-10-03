"""
Tests for M6-F (B5B): Canonical Optimization-State Representation.

Covers all 17 mandatory contract requirements from the M6-F specification.
"""

import json
import pytest

from app.schemas.optimization import (
    PackageGeometry,
    PackagingCandidate,
    CandidateDecisionVariables,
    CandidateBarrierProperties,
    CandidateEvidenceReference
)
from app.schemas.constraints import ConditionMatchLevel
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
from scientific_engine.optimization.canonical_representation import (
    CanonicalOptimizationState,
    build_canonical_representation
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
    shelf_life_days: int = 30,
    temp_c: float = 20.0,
    rh_pct: float = 75.0,
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


def create_dummy_geometry(
    area: float = 0.1,
    vol: float = 500.0,
    mass: float = 1.0
) -> PackageGeometry:
    return PackageGeometry(
        surface_area_m2=area,
        headspace_volume_cm3=vol,
        product_mass_kg=mass
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


# 1. Same identity -> same canonical representation.
def test_same_identity_same_representation():
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost", "shelf_life_margin"]
    cands = [create_dummy_candidate("id_1"), create_dummy_candidate("id_2")]
    
    repr1 = build_canonical_representation(env, geom, objs, cands)
    repr2 = build_canonical_representation(env, geom, objs, cands)
    
    assert repr1.to_canonical_json() == repr2.to_canonical_json()


# 2. Active objectives in different orders -> identical representation.
def test_objectives_different_order_identical_representation():
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    
    objs1 = ["material_cost", "shelf_life_margin", "sustainability_score"]
    objs2 = ["sustainability_score", "material_cost", "shelf_life_margin"]
    
    repr1 = build_canonical_representation(env, geom, objs1, cands)
    repr2 = build_canonical_representation(env, geom, objs2, cands)
    
    assert repr1.active_objectives == ["material_cost", "shelf_life_margin", "sustainability_score"]
    assert repr1.to_canonical_json() == repr2.to_canonical_json()


# 3. Candidate IDs in different orders -> identical representation.
def test_candidate_ids_different_order_identical_representation():
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    
    cands1 = [create_dummy_candidate("id_B"), create_dummy_candidate("id_A"), create_dummy_candidate("id_C")]
    cands2 = [create_dummy_candidate("id_A"), create_dummy_candidate("id_C"), create_dummy_candidate("id_B")]
    
    repr1 = build_canonical_representation(env, geom, objs, cands1)
    repr2 = build_canonical_representation(env, geom, objs, cands2)
    
    assert repr1.eligible_candidate_ids == ["id_A", "id_B", "id_C"]
    assert repr1.to_canonical_json() == repr2.to_canonical_json()


# 4. Different objective set -> different representation.
def test_different_objectives_different_representation():
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    
    repr1 = build_canonical_representation(env, geom, ["material_cost"], cands)
    repr2 = build_canonical_representation(env, geom, ["shelf_life_margin"], cands)
    
    assert repr1.to_canonical_json() != repr2.to_canonical_json()


# 5. Different candidate set -> different representation.
def test_different_candidate_set_different_representation():
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    objs = ["material_cost"]
    
    cands1 = [create_dummy_candidate("id_1")]
    cands2 = [create_dummy_candidate("id_1"), create_dummy_candidate("id_2")]
    
    repr1 = build_canonical_representation(env, geom, objs, cands1)
    repr2 = build_canonical_representation(env, geom, objs, cands2)
    
    assert repr1.to_canonical_json() != repr2.to_canonical_json()


# 6. Different PackageGeometry -> different representation.
def test_different_geometry_different_representation():
    env = create_dummy_requirement_envelope()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    geom1 = create_dummy_geometry(area=0.1)
    geom2 = create_dummy_geometry(area=0.2)
    
    repr1 = build_canonical_representation(env, geom1, objs, cands)
    repr2 = build_canonical_representation(env, geom2, objs, cands)
    
    assert repr1.to_canonical_json() != repr2.to_canonical_json()


# 7. Different Phase 4 requirement value -> different representation.
def test_different_phase4_requirement_value():
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    env1 = create_dummy_requirement_envelope(otr_val=100.0)
    env2 = create_dummy_requirement_envelope(otr_val=105.0)
    
    repr1 = build_canonical_representation(env1, geom, objs, cands)
    repr2 = build_canonical_representation(env2, geom, objs, cands)
    
    assert repr1.to_canonical_json() != repr2.to_canonical_json()


# 8. Different interval lower bound -> different representation.
def test_different_interval_lower_bound():
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    env1 = create_dummy_requirement_envelope(wvtr_min=2.0, wvtr_max=5.0)
    env2 = create_dummy_requirement_envelope(wvtr_min=2.5, wvtr_max=5.0)
    
    repr1 = build_canonical_representation(env1, geom, objs, cands)
    repr2 = build_canonical_representation(env2, geom, objs, cands)
    
    assert repr1.to_canonical_json() != repr2.to_canonical_json()


# 9. Different interval upper bound -> different representation.
def test_different_interval_upper_bound():
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    env1 = create_dummy_requirement_envelope(wvtr_min=2.0, wvtr_max=5.0)
    env2 = create_dummy_requirement_envelope(wvtr_min=2.0, wvtr_max=5.5)
    
    repr1 = build_canonical_representation(env1, geom, objs, cands)
    repr2 = build_canonical_representation(env2, geom, objs, cands)
    
    assert repr1.to_canonical_json() != repr2.to_canonical_json()


# 10. UNKNOWN != ABSENT.
def test_unknown_not_equal_absent():
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    env_unknown = create_dummy_requirement_envelope(moisture_status=CalculationStatus.UNKNOWN)
    env_normal = create_dummy_requirement_envelope()
    
    # Modify env_absent to have moisture_requirements = None
    env_absent = create_dummy_requirement_envelope()
    env_absent.moisture_requirements = None
    
    repr_unknown = build_canonical_representation(env_unknown, geom, objs, cands)
    repr_absent = build_canonical_representation(env_absent, geom, objs, cands)
    
    assert repr_unknown.requirement_envelope["moisture_requirements"]["status"] == "UNKNOWN"
    assert repr_absent.requirement_envelope["moisture_requirements"] == "ABSENT"
    assert repr_unknown.to_canonical_json() != repr_absent.to_canonical_json()


# 11. Scalar value != interval representation when contract treats them differently.
def test_scalar_vs_interval_preservation():
    env = create_dummy_requirement_envelope(wvtr_min=2.0, wvtr_max=5.0)
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    repr_res = build_canonical_representation(env, geom, objs, cands)
    wvtr_rep = repr_res.requirement_envelope["moisture_requirements"]["required_wvtr_per_area"]
    
    assert wvtr_rep["minimum_value"] == 2.0
    assert wvtr_rep["maximum_value"] == 5.0
    assert wvtr_rep["value"] is None  # Preserved as None, not collapsed


# 12. No midpoint collapse.
def test_no_midpoint_collapse():
    env = create_dummy_requirement_envelope(wvtr_min=2.0, wvtr_max=10.0)
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    repr_res = build_canonical_representation(env, geom, objs, cands)
    wvtr_rep = repr_res.requirement_envelope["moisture_requirements"]["required_wvtr_per_area"]
    
    # Midpoint would be 6.0. Verify 6.0 does not appear anywhere as a value
    assert wvtr_rep["value"] != 6.0
    assert wvtr_rep["minimum_value"] == 2.0
    assert wvtr_rep["maximum_value"] == 10.0


# 13. No float rounding is performed.
def test_no_float_rounding():
    precise_val = 12.345678912345678
    env = create_dummy_requirement_envelope(otr_val=precise_val)
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    repr_res = build_canonical_representation(env, geom, objs, cands)
    otr_rep = repr_res.requirement_envelope["gas_requirements"]["required_otr_cc_per_pkg_day"]
    
    assert otr_rep["value"] == precise_val


# 14. Canonical representation contains no timestamp/randomness.
def test_no_timestamp_or_randomness():
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    json_str = build_canonical_representation(env, geom, objs, cands).to_canonical_json()
    data = json.loads(json_str)
    
    # Verify no timestamp, uuid, run_id or metadata keys exist
    full_str = json.dumps(data)
    assert "timestamp" not in full_str
    assert "run_id" not in full_str
    assert "uuid" not in full_str
    assert "solver_metadata" not in full_str


# 15. Raw biological context is not silently added to identity.
def test_raw_biological_context_excluded():
    env_gala = create_dummy_requirement_envelope(commodity="Gala Apple")
    env_fuji = create_dummy_requirement_envelope(commodity="Fuji Apple")
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    repr1 = build_canonical_representation(env_gala, geom, objs, cands)
    repr2 = build_canonical_representation(env_fuji, geom, objs, cands)
    
    # Since Phase 4 requirement values are identical, raw commodity differences do NOT alter representation
    assert repr1.to_canonical_json() == repr2.to_canonical_json()


# 16. Provenance/epistemic metadata is not silently added to identity.
def test_provenance_metadata_excluded():
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1")]
    objs = ["material_cost"]
    
    repr_res = build_canonical_representation(env, geom, objs, cands)
    json_str = repr_res.to_canonical_json()
    
    assert "traceability" not in json_str
    assert "equation_form" not in json_str
    assert "assumptions" not in json_str
    assert "all_warnings" not in json_str


# 17. Repeated serialization of the same identity is deterministic.
def test_repeated_serialization_deterministic():
    env = create_dummy_requirement_envelope()
    geom = create_dummy_geometry()
    cands = [create_dummy_candidate("id_1"), create_dummy_candidate("id_2")]
    objs = ["material_cost", "shelf_life_margin"]
    
    repr_obj = build_canonical_representation(env, geom, objs, cands)
    
    json_results = [repr_obj.to_canonical_json() for _ in range(10)]
    assert len(set(json_results)) == 1
