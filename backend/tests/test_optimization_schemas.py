import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.physics import (
    CalculationStatus, 
    ScientificTraceability, 
    ScientificResult
)
from app.schemas.constraints import (
    ConstraintStatus, 
    ConditionMatchLevel, 
    ComparisonOperator, 
    ConstraintEvaluation
)
from app.schemas.candidate_feasibility import FilteringResult
from app.schemas.packaging_requirements import (
    PackagingRequirementEnvelope,
    MoistureRequirement,
    MicrobialRequirement,
    GasExchangeRequirement,
    ShelfLifeRequirement,
    DeteriorationProfile
)
from app.schemas.optimization import (
    ObjectiveDirection,
    EvidenceTier,
    UncertaintyType,
    OptimizationExecutionTier,
    CandidateEvidenceReference,
    BarrierPropertyMetric,
    CandidateBarrierProperties,
    PackageGeometry,
    CandidateDecisionVariables,
    PackagingCandidate,
    CandidateScientificEvaluationRequest,
    CandidateScientificEvaluationResult,
    ObjectiveValue,
    CandidateConstraintStatus,
    UncertaintyProfile,
    ExplanationPayload,
    ParetoCandidate,
    SolverConfiguration,
    OptimizationInputEnvelope,
    OptimizationMetadata,
    ParetoFront,
    CounterfactualPerturbations,
    CounterfactualQuery
)

def _mock_traceability():
    return ScientificTraceability(
        model_name="mock_model",
        equation_form="mock = mock",
        equation_reference="mock",
        units_used={"mock": "mock"}
    )

def test_valid_and_invalid_candidate():
    # Valid candidate
    geometry = PackageGeometry(surface_area_m2=0.06, headspace_volume_cm3=500.0, product_mass_kg=0.5)
    assert geometry.surface_area_m2 == 0.06

    # Invalid geometry (negative mass)
    with pytest.raises(ValidationError):
        PackageGeometry(surface_area_m2=0.06, headspace_volume_cm3=500.0, product_mass_kg=-1.0)
        
    provenance = CandidateEvidenceReference(
        source_id="123",
        source_name="M5",
        record_identifier_in_source="rec-1",
        evidence_classification="EXPERIMENTAL_LITERATURE_DATA",
        verification_status="VERIFIED_EXTRACT"
    )
    
    barrier = CandidateBarrierProperties(
        otr=BarrierPropertyMetric(value=10.0, unit="cc/m2/day"),
        wvtr=BarrierPropertyMetric(value=5.0, unit="g/m2/day")
    )
    
    variables = CandidateDecisionVariables(
        structure_type="MONOLAYER",
        total_thickness_um=50.0,
        thickness_source="observed_discrete_m5"
    )
    
    candidate = PackagingCandidate(
        candidate_id="cand-1",
        material_id="mat-1",
        material_name="LDPE 50 um",
        decision_variables=variables,
        barrier_properties=barrier,
        condition_match=ConditionMatchLevel.EXACT,
        provenance=provenance
    )
    
    assert candidate.material_name == "LDPE 50 um"
    assert candidate.decision_variables.total_thickness_um == 50.0

def test_evidence_tier_and_predicted_warning():
    provenance = CandidateEvidenceReference(
        source_id="456",
        source_name="PolyID",
        record_identifier_in_source="qsar-1",
        evidence_classification="MODEL_PREDICTED",
        verification_status="PREDICTIVE_ONLY",
        synthetic_prediction_warning="QSAR uncertainty bounds apply"
    )
    assert "QSAR" in provenance.synthetic_prediction_warning

def test_constraint_status():
    status = CandidateConstraintStatus(
        all_hard_constraints_satisfied=False,
        overall_status=ConstraintStatus.INFEASIBLE,
        condition_match=ConditionMatchLevel.UNKNOWN,
        evaluations=[
            ConstraintEvaluation(
                constraint_type="wvtr_limit",
                status=ConstraintStatus.INFEASIBLE,
                comparison_operator=ComparisonOperator.LE,
                required_value=5.0,
                required_unit="g/m2/day",
                material_value=10.0,
                material_unit="g/m2/day",
                condition_match=ConditionMatchLevel.UNKNOWN,
                reason="Candidate WVTR exceeds maximum allowed",
                traceability=_mock_traceability()
            )
        ]
    )
    assert status.overall_status == ConstraintStatus.INFEASIBLE
    assert len(status.evaluations) == 1

def test_objective_values():
    scalar_obj = ObjectiveValue(
        objective_name="f_thickness",
        direction=ObjectiveDirection.MINIMIZE,
        value=50.0,
        unit="um",
        status=CalculationStatus.CALCULATED
    )
    assert scalar_obj.is_interval is False
    
    interval_obj = ObjectiveValue(
        objective_name="f_moisture_margin",
        direction=ObjectiveDirection.MAXIMIZE,
        value_min=0.2,
        value_max=0.5,
        is_interval=True,
        unit="ratio",
        status=CalculationStatus.CALCULATED
    )
    assert interval_obj.is_interval is True
    
    unknown_obj = ObjectiveValue(
        objective_name="f_cost",
        direction=ObjectiveDirection.MINIMIZE,
        unit="USD",
        status=CalculationStatus.UNKNOWN
    )
    assert unknown_obj.value is None

def test_f10_1_integration_interface():
    # Setup dummy packaging candidate
    provenance = CandidateEvidenceReference(
        source_id="123", source_name="M5", record_identifier_in_source="rec-1",
        evidence_classification="EXPERIMENTAL_LITERATURE_DATA", verification_status="VERIFIED_EXTRACT"
    )
    barrier = CandidateBarrierProperties(
        otr=BarrierPropertyMetric(value=10.0, unit="cc/m2/day"),
        wvtr=BarrierPropertyMetric(value=5.0, unit="g/m2/day")
    )
    variables = CandidateDecisionVariables(
        total_thickness_um=50.0, thickness_source="observed_discrete_m5"
    )
    candidate = PackagingCandidate(
        candidate_id="cand-1", material_id="mat-1", material_name="LDPE",
        decision_variables=variables, barrier_properties=barrier,
        condition_match=ConditionMatchLevel.EXACT, provenance=provenance
    )
    
    geometry = PackageGeometry(surface_area_m2=0.06, headspace_volume_cm3=500.0, product_mass_kg=0.5)
    base_env = PackagingRequirementEnvelope(
        commodity="Apple", target_shelf_life_days=30, storage_temperature_c=4.0,
        relative_humidity_percent=85.0, deterioration_profile=DeteriorationProfile(commodity="Apple", mechanisms={}),
        gas_requirements=GasExchangeRequirement(status=CalculationStatus.UNKNOWN),
        moisture_requirements=MoistureRequirement(status=CalculationStatus.UNKNOWN),
        microbial_requirements=MicrobialRequirement(status=CalculationStatus.UNKNOWN),
        shelf_life=ShelfLifeRequirement(target_days=30, status=CalculationStatus.UNKNOWN),
        overall_status=CalculationStatus.CALCULATED, traceability_log=[]
    )
    
    req = CandidateScientificEvaluationRequest(
        candidate=candidate,
        base_requirement_envelope=base_env,
        package_geometry=geometry
    )
    assert req.package_geometry.surface_area_m2 == 0.06
    assert req.candidate.material_name == "LDPE"
    
    shelf_life = ShelfLifeRequirement(
        target_days=30,
        status=CalculationStatus.CALCULATED,
        feasibility="achievable"
    )
    
    res = CandidateScientificEvaluationResult(
        candidate_id="cand-1",
        updated_moisture_requirement=MoistureRequirement(status=CalculationStatus.CALCULATED),
        candidate_shelf_life_requirement=shelf_life,
        overall_status=CalculationStatus.CALCULATED,
        traceability=_mock_traceability()
    )
    assert res.candidate_shelf_life_requirement.target_days == 30

def test_counterfactual_query():
    query = CounterfactualQuery(
        base_run_id="run-1",
        perturbations=CounterfactualPerturbations(
            delta_target_shelf_life_days=5,
            delta_storage_temperature_c=-2.0
        )
    )
    assert query.perturbations.delta_target_shelf_life_days == 5
    
    with pytest.raises(ValidationError):
        CounterfactualQuery(
            base_run_id="run-2",
            perturbations=CounterfactualPerturbations(
                relaxation_factor_wvtr=0.1 # too low, ge=0.5
            )
        )

def test_m6b2b_candidate_evaluation_result_correction():
    # Test proving the schema correction works and Phase 4/Phase 5 are isolated
    
    constraint_eval = ConstraintEvaluation(
        constraint_type="wvtr_limit",
        status=ConstraintStatus.INFEASIBLE,
        comparison_operator=ComparisonOperator.LE,
        required_value=5.0,
        required_unit="g/m2/day",
        material_value=10.0,
        material_unit="g/m2/day",
        condition_match=ConditionMatchLevel.EXACT,
        reason="Exceeds limit",
        traceability=_mock_traceability()
    )
    
    constraint_profile = CandidateConstraintStatus(
        all_hard_constraints_satisfied=False,
        overall_status=ConstraintStatus.INFEASIBLE,
        condition_match=ConditionMatchLevel.EXACT,
        evaluations=[constraint_eval]
    )
    
    uncertainty_profile = UncertaintyProfile(
        uncertainty_type=UncertaintyType.QSAR_CONFIDENCE_INTERVAL,
        objective_intervals={}
    )
    
    shelf_life = ShelfLifeRequirement(
        target_days=30,
        status=CalculationStatus.CALCULATED,
        feasibility="achievable"
    )
    
    # Prove Phase 4 CALCULATED + Phase 5 INFEASIBLE coexist
    res = CandidateScientificEvaluationResult(
        candidate_id="cand-1",
        updated_moisture_requirement=MoistureRequirement(status=CalculationStatus.CALCULATED),
        candidate_shelf_life_requirement=shelf_life,
        overall_status=CalculationStatus.CALCULATED, # Phase 4
        traceability=_mock_traceability(),
        constraint_profile=constraint_profile, # Phase 5
        uncertainty_profile=uncertainty_profile,
        warnings=["High humidity warning"],
        failure_reasons=["WVTR Exceeded limit"]
    )
    
    assert res.overall_status == CalculationStatus.CALCULATED
    assert res.constraint_profile is not None
    assert res.constraint_profile.overall_status == ConstraintStatus.INFEASIBLE
    assert res.uncertainty_profile.uncertainty_type == UncertaintyType.QSAR_CONFIDENCE_INTERVAL
    assert "High humidity warning" in res.warnings
    assert "WVTR Exceeded limit" in res.failure_reasons
    
    # Prove Phase 4 PARTIALLY_CALCULATED + Phase 5 UNKNOWN coexist
    constraint_profile_unk = CandidateConstraintStatus(
        all_hard_constraints_satisfied=False,
        overall_status=ConstraintStatus.UNKNOWN,
        condition_match=ConditionMatchLevel.UNKNOWN,
        evaluations=[]
    )
    
    res_unk = CandidateScientificEvaluationResult(
        candidate_id="cand-2",
        updated_moisture_requirement=MoistureRequirement(status=CalculationStatus.PARTIALLY_CALCULATED),
        candidate_shelf_life_requirement=ShelfLifeRequirement(target_days=30, status=CalculationStatus.UNKNOWN),
        overall_status=CalculationStatus.PARTIALLY_CALCULATED,
        traceability=_mock_traceability(),
        constraint_profile=constraint_profile_unk,
        failure_reasons=["Missing CO2TR"]
    )
    
    assert res_unk.overall_status == CalculationStatus.PARTIALLY_CALCULATED
    assert res_unk.constraint_profile.overall_status == ConstraintStatus.UNKNOWN
    
    # Ensure no Pareto or Objective fields were added to this schema
    assert not hasattr(res, "f_thickness")
    assert not hasattr(res, "pareto_status")

