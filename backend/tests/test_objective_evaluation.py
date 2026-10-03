"""
Tests for M6-B3 Objective Evaluation.
"""

import pytest

from app.schemas.optimization import (
    PackagingCandidate,
    CandidateDecisionVariables,
    CandidateBarrierProperties,
    BarrierPropertyMetric,
    CandidateEvidenceReference,
    CandidateScientificEvaluationResult,
    CandidateConstraintStatus,
    UncertaintyProfile,
    UncertaintyType,
    ObjectiveDirection
)
from app.schemas.physics import CalculationStatus, ScientificResult, ScientificTraceability
from app.schemas.constraints import ConstraintStatus, ConditionMatchLevel
from app.schemas.packaging_requirements import (
    MoistureRequirement,
    GasExchangeRequirement,
    MicrobialRequirement,
    ShelfLifeRequirement
)
from scientific_engine.optimization.objective_evaluator import ObjectiveEvaluator

def _mock_traceability():
    return ScientificTraceability(
        model_name="mock",
        equation_form="mock",
        inputs_used={},
        units_used={}
    )

def _mock_candidate(thickness=50.0, wvtr=5.0, otr=10.0, co2tr=20.0):
    provenance = CandidateEvidenceReference(
        source_id="cand-123",
        source_name="M5",
        record_identifier_in_source="123",
        evidence_classification="EXPERIMENTAL_LITERATURE_DATA",
        verification_status="VERIFIED_EXTRACT"
    )
    
    barrier = CandidateBarrierProperties(
        otr=BarrierPropertyMetric(value=otr, unit="cc/m2/day") if otr is not None else None,
        wvtr=BarrierPropertyMetric(value=wvtr, unit="g/m2/day") if wvtr is not None else None,
        co2tr=BarrierPropertyMetric(value=co2tr, unit="cc/m2/day") if co2tr is not None else None
    )
    
    variables = CandidateDecisionVariables(
        structure_type="MONOLAYER",
        total_thickness_um=thickness,
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

def _mock_scientific_result(
    is_feasible=True,
    allowable_wvtr=10.0,
    target_otr=10.0,
    ideal_beta=2.0,
    achievable_shelf_life=40,
    target_shelf_life=30
):
    moisture_req = MoistureRequirement(
        status=CalculationStatus.CALCULATED,
        required_wvtr_per_area=ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=allowable_wvtr,
            unit="g/m2/day",
            traceability=_mock_traceability()
        )
    )
    
    gas_req = GasExchangeRequirement(
        status=CalculationStatus.CALCULATED,
        required_otr_per_area=ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=target_otr,
            unit="cc/m2/day",
            traceability=_mock_traceability()
        ),
        ideal_beta_ratio_co2_to_o2=ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=ideal_beta,
            unit="dimensionless",
            traceability=_mock_traceability()
        ) if ideal_beta is not None else None
    )
    
    sl_req = ShelfLifeRequirement(
        target_days=target_shelf_life,
        status=CalculationStatus.CALCULATED,
        supported_calculated_shelf_life_days=ScientificResult(
            status=CalculationStatus.CALCULATED,
            value=achievable_shelf_life,
            unit="days",
            traceability=_mock_traceability()
        ) if achievable_shelf_life is not None else None
    )
    
    constraint_profile = CandidateConstraintStatus(
        all_hard_constraints_satisfied=is_feasible,
        overall_status=ConstraintStatus.FEASIBLE if is_feasible else ConstraintStatus.INFEASIBLE,
        condition_match=ConditionMatchLevel.EXACT
    )
    
    return CandidateScientificEvaluationResult(
        candidate_id="cand-1",
        updated_moisture_requirement=moisture_req,
        updated_gas_exchange_requirement=gas_req,
        updated_microbial_requirement=MicrobialRequirement(status=CalculationStatus.UNKNOWN),
        candidate_shelf_life_requirement=sl_req,
        overall_status=CalculationStatus.CALCULATED,
        traceability=_mock_traceability(),
        constraint_profile=constraint_profile,
        uncertainty_profile=UncertaintyProfile(uncertainty_type=UncertaintyType.DETERMINISTIC_POINT, objective_intervals={}),
        warnings=[],
        failure_reasons=[]
    )

def test_objective_evaluator_basic():
    evaluator = ObjectiveEvaluator()
    candidate = _mock_candidate(thickness=55.0, wvtr=4.0, otr=8.0, co2tr=16.0)
    res = _mock_scientific_result(
        allowable_wvtr=10.0,
        target_otr=10.0,
        ideal_beta=2.0,
        achievable_shelf_life=45,
        target_shelf_life=30
    )
    
    obj = evaluator.evaluate_objectives(candidate, res)
    
    # 1. f_thickness
    assert obj["f_thickness"].status == CalculationStatus.CALCULATED
    assert obj["f_thickness"].direction == ObjectiveDirection.MINIMIZE
    assert obj["f_thickness"].value == 55.0
    
    # 2. f_moisture_margin
    assert obj["f_moisture_margin"].status == CalculationStatus.CALCULATED
    assert obj["f_moisture_margin"].direction == ObjectiveDirection.MAXIMIZE
    assert obj["f_moisture_margin"].value == (10.0 - 4.0) / 10.0  # 0.6
    
    # 3. f_gas_alignment
    assert obj["f_gas_alignment"].status == CalculationStatus.CALCULATED
    assert obj["f_gas_alignment"].direction == ObjectiveDirection.MINIMIZE
    # OTR diff = |8 - 10|/10 = 0.2
    # Beta = 16/8 = 2.0. Ideal = 2.0. Beta diff = 0.
    # Total = 0.2
    assert obj["f_gas_alignment"].value == 0.2
    
    # 4. f_shelf_life_margin
    assert obj["f_shelf_life_margin"].status == CalculationStatus.CALCULATED
    assert obj["f_shelf_life_margin"].direction == ObjectiveDirection.MAXIMIZE
    assert obj["f_shelf_life_margin"].value == (45 - 30) / 30  # 0.5

def test_infeasible_candidate():
    evaluator = ObjectiveEvaluator()
    candidate = _mock_candidate()
    res = _mock_scientific_result(is_feasible=False)
    
    obj = evaluator.evaluate_objectives(candidate, res)
    
    for k, v in obj.items():
        assert v.status == CalculationStatus.UNKNOWN
        assert "not feasible" in v.explanation_metadata

def test_candidate_differences():
    evaluator = ObjectiveEvaluator()
    
    # Candidate A
    candA = _mock_candidate(thickness=40.0, wvtr=2.0)
    resA = _mock_scientific_result(allowable_wvtr=10.0)
    objA = evaluator.evaluate_objectives(candA, resA)
    
    # Candidate B
    candB = _mock_candidate(thickness=80.0, wvtr=8.0)
    resB = _mock_scientific_result(allowable_wvtr=10.0)
    objB = evaluator.evaluate_objectives(candB, resB)
    
    assert objA["f_thickness"].value == 40.0
    assert objB["f_thickness"].value == 80.0
    assert objA["f_thickness"].value != objB["f_thickness"].value
    
    assert objA["f_moisture_margin"].value == (10.0 - 2.0)/10.0 # 0.8
    assert objB["f_moisture_margin"].value == (10.0 - 8.0)/10.0 # 0.2
    assert objA["f_moisture_margin"].value != objB["f_moisture_margin"].value

def test_interval_propagation():
    evaluator = ObjectiveEvaluator()
    candidate = _mock_candidate()
    # Mock interval WVTR
    candidate.barrier_properties.wvtr.is_range = True
    candidate.barrier_properties.wvtr.value_min = 4.0
    candidate.barrier_properties.wvtr.value_max = 6.0
    
    res = _mock_scientific_result(allowable_wvtr=10.0)
    
    obj = evaluator.evaluate_objectives(candidate, res)
    
    # Moisture margin should propagate interval
    mm = obj["f_moisture_margin"]
    assert mm.is_interval is True
    assert mm.value_min == (10.0 - 6.0)/10.0 # 0.4
    assert mm.value_max == (10.0 - 4.0)/10.0 # 0.6

def test_unknown_objectives():
    evaluator = ObjectiveEvaluator()
    candidate = _mock_candidate(thickness=1.0, wvtr=None, otr=None)
    res = _mock_scientific_result(achievable_shelf_life=None)
    
    obj = evaluator.evaluate_objectives(candidate, res)
    
    assert obj["f_thickness"].status == CalculationStatus.CALCULATED
    assert obj["f_moisture_margin"].status == CalculationStatus.UNKNOWN
    assert obj["f_gas_alignment"].status == CalculationStatus.UNKNOWN
    assert obj["f_shelf_life_margin"].status == CalculationStatus.UNKNOWN
