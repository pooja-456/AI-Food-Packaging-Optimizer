"""
Tests for M6-B2B Candidate Scientific Evaluation.
"""

import pytest

from app.schemas.optimization import (
    CandidateScientificEvaluationRequest,
    PackagingCandidate,
    CandidateDecisionVariables,
    CandidateBarrierProperties,
    BarrierPropertyMetric,
    CandidateEvidenceReference,
    PackageGeometry,
    UncertaintyType
)
from app.schemas.packaging_requirements import (
    PackagingRequirementEnvelope,
    GasExchangeRequirement,
    MoistureRequirement,
    MicrobialRequirement,
    ShelfLifeRequirement,
    DeteriorationProfile
)
from app.schemas.physics import CalculationStatus, ScientificTraceability, ScientificResult
from app.schemas.constraints import ConditionMatchLevel, ConstraintStatus
from scientific_engine.optimization.candidate_evaluator import CandidateScientificEvaluator

def _mock_traceability():
    return ScientificTraceability(
        model_name="mock",
        equation_form="mock",
        inputs_used={},
        units_used={}
    )

def _mock_candidate():
    provenance = CandidateEvidenceReference(
        source_id="cand-123",
        source_name="M5",
        record_identifier_in_source="123",
        evidence_classification="EXPERIMENTAL_LITERATURE_DATA",
        verification_status="VERIFIED_EXTRACT"
    )
    
    barrier = CandidateBarrierProperties(
        otr=BarrierPropertyMetric(value=10.0, unit="cc/m2/day", test_temperature_c=23.0, test_rh_percent=0.0),
        wvtr=BarrierPropertyMetric(value=5.0, unit="g/m2/day", test_temperature_c=38.0, test_rh_percent=90.0)
    )
    
    variables = CandidateDecisionVariables(
        structure_type="MONOLAYER",
        total_thickness_um=50.0,
        thickness_source="observed_discrete_m5"
    )
    
    return PackagingCandidate(
        candidate_id="cand-1",
        material_id="mat-1",
        material_name="LDPE",
        decision_variables=variables,
        barrier_properties=barrier,
        condition_match=ConditionMatchLevel.EXACT,
        provenance=provenance
    )

def _mock_envelope():
    # Base requirements from Phase 4
    gas_req = GasExchangeRequirement(
        status=CalculationStatus.CALCULATED,
        required_otr_cc_per_pkg_day=ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=0.5,
            unit="cc/package/day",
            traceability=_mock_traceability()
        )
    )
    
    moisture_req = MoistureRequirement(
        status=CalculationStatus.CALCULATED,
        initial_water_activity=0.8,
        critical_water_activity=0.9,
        required_wvtr_g_per_pkg_day=ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=0.3, # Say target needs 0.3g/day max
            unit="g/package/day",
            traceability=_mock_traceability()
        ),
        traceability=ScientificTraceability(
            model_name="moisture",
            equation_form="eq",
            inputs_used={
                "m_init_%": 15.0,
                "m_crit_%": 18.0,
                "dry_mass_g": 500.0,
                "target_shelf_life_days": 30
            },
            units_used={}
        )
    )
    
    return PackagingRequirementEnvelope(
        commodity="Apple",
        target_shelf_life_days=30,
        storage_temperature_c=23.0,
        relative_humidity_percent=85.0,
        deterioration_profile=DeteriorationProfile(commodity="Apple", mechanisms={}),
        gas_requirements=gas_req,
        moisture_requirements=moisture_req,
        microbial_requirements=MicrobialRequirement(status=CalculationStatus.UNKNOWN),
        shelf_life=ShelfLifeRequirement(target_days=30, status=CalculationStatus.CALCULATED),
        overall_status=CalculationStatus.CALCULATED,
        traceability_log=[]
    )

def test_b2b_candidate_evaluation_pipeline():
    evaluator = CandidateScientificEvaluator()
    candidate = _mock_candidate()
    envelope = _mock_envelope()
    geometry = PackageGeometry(surface_area_m2=0.06, headspace_volume_cm3=500.0, product_mass_kg=0.5)
    
    req = CandidateScientificEvaluationRequest(
        candidate=candidate,
        base_requirement_envelope=envelope,
        package_geometry=geometry
    )
    
    res = evaluator.evaluate_candidate(req)
    
    # 1. Phase 4 candidate-specific evaluation
    assert res.updated_moisture_requirement.status == CalculationStatus.CALCULATED
    
    # Candidate WVTR is 5.0 g/m2/day. Area is 0.06 m2. pkg_wvtr is 0.3 g/pkg/day.
    # Base target required 0.3 g/pkg/day.
    # Therefore, moisture limited shelf life should be re-calculated!
    assert res.updated_moisture_requirement.moisture_limited_shelf_life_days is not None
    
    # 2. Phase 5 constraint evaluation
    assert res.constraint_profile is not None
    # We expect OTR and WVTR to have been evaluated.
    assert len(res.constraint_profile.evaluations) > 0
    
    # 3. Uncertainty Profile
    assert res.uncertainty_profile.uncertainty_type == UncertaintyType.DETERMINISTIC_POINT

def test_missing_geometry_partial_calculation():
    evaluator = CandidateScientificEvaluator()
    candidate = _mock_candidate()
    envelope = _mock_envelope()
    
    # Missing geometry
    req = CandidateScientificEvaluationRequest(
        candidate=candidate,
        base_requirement_envelope=envelope,
        package_geometry=None
    )
    
    res = evaluator.evaluate_candidate(req)
    # Warnings about missing geometry
    assert any("geometry" in w.lower() for w in res.warnings)
    # Moisture requirement itself is CALCULATED because WVTR target is still valid
    assert res.updated_moisture_requirement.status == CalculationStatus.CALCULATED
    # But shelf life cannot be fully evaluated for this candidate
    assert res.candidate_shelf_life_requirement.status == CalculationStatus.PARTIALLY_CALCULATED
    # Thus the candidate's overall Phase 4 evaluation is partially calculated
    assert res.overall_status == CalculationStatus.PARTIALLY_CALCULATED

def test_unknown_condition():
    evaluator = CandidateScientificEvaluator()
    candidate = _mock_candidate()
    candidate.condition_match = ConditionMatchLevel.UNKNOWN
    
    req = CandidateScientificEvaluationRequest(
        candidate=candidate,
        base_requirement_envelope=_mock_envelope(),
        package_geometry=PackageGeometry(surface_area_m2=0.06, product_mass_kg=0.5, headspace_volume_cm3=500.0)
    )
    
    res = evaluator.evaluate_candidate(req)
    assert res.constraint_profile.condition_match == ConditionMatchLevel.UNKNOWN
    
    # If conditions are UNKNOWN, constraint evaluation propagates UNKNOWN
    # Wait, the barrier constraint checks will yield UNKNOWN for the specific constraints.
    has_unknown = any(e.status == ConstraintStatus.UNKNOWN for e in res.constraint_profile.evaluations)
    assert has_unknown

def test_predicted_uncertainty():
    evaluator = CandidateScientificEvaluator()
    candidate = _mock_candidate()
    candidate.provenance.evidence_classification = "MODEL_PREDICTED"
    
    req = CandidateScientificEvaluationRequest(
        candidate=candidate,
        base_requirement_envelope=_mock_envelope(),
        package_geometry=PackageGeometry(surface_area_m2=0.06, product_mass_kg=0.5, headspace_volume_cm3=500.0)
    )
    
    res = evaluator.evaluate_candidate(req)
    assert res.uncertainty_profile.uncertainty_type == UncertaintyType.QSAR_CONFIDENCE_INTERVAL
