"""
Tests for M6-B4B Pareto Front Construction.
"""

import pytest
from typing import Dict
from app.schemas.optimization import (
    ParetoCandidate, ObjectiveValue, ObjectiveDirection,
    CandidateConstraintStatus, UncertaintyProfile, EvidenceTier,
    ExplanationPayload, PackagingCandidate, CandidateDecisionVariables,
    CandidateBarrierProperties, CandidateEvidenceReference, UncertaintyType
)
from app.schemas.physics import CalculationStatus, ScientificTraceability
from app.schemas.constraints import ConstraintStatus, ConditionMatchLevel
from scientific_engine.optimization.pareto_front import ParetoFrontConstructor

def _obj(name: str, val: float, direction: ObjectiveDirection) -> ObjectiveValue:
    return ObjectiveValue(
        objective_name=name,
        direction=direction,
        value=val,
        unit="unit",
        status=CalculationStatus.CALCULATED
    )

def _mock_traceability():
    return ScientificTraceability(
        model_name="mock",
        equation_form="mock",
        inputs_used={},
        units_used={}
    )

def _mock_candidate_design(cand_id: str):
    provenance = CandidateEvidenceReference(
        source_id="123",
        source_name="M5",
        record_identifier_in_source="123",
        evidence_classification="EXPERIMENTAL_LITERATURE_DATA",
        verification_status="VERIFIED_EXTRACT"
    )
    variables = CandidateDecisionVariables(
        structure_type="MONOLAYER",
        total_thickness_um=50.0,
        thickness_source="observed_discrete_m5"
    )
    return PackagingCandidate(
        candidate_id=cand_id,
        material_id="mat-1",
        material_name="mock",
        decision_variables=variables,
        barrier_properties=CandidateBarrierProperties(),
        condition_match=ConditionMatchLevel.EXACT,
        provenance=provenance
    )

def _mock_pareto_candidate(cid: str, t: float, m: float, g: float, s: float) -> ParetoCandidate:
    objs = {
        "f_thickness": _obj("f_thickness", t, ObjectiveDirection.MINIMIZE),
        "f_moisture_margin": _obj("f_moisture_margin", m, ObjectiveDirection.MAXIMIZE),
        "f_gas_alignment": _obj("f_gas_alignment", g, ObjectiveDirection.MINIMIZE),
        "f_shelf_life_margin": _obj("f_shelf_life_margin", s, ObjectiveDirection.MAXIMIZE)
    }
    
    constraint_summary = CandidateConstraintStatus(
        all_hard_constraints_satisfied=True,
        overall_status=ConstraintStatus.FEASIBLE,
        condition_match=ConditionMatchLevel.EXACT
    )
    
    return ParetoCandidate(
        pareto_candidate_id=cid,
        candidate_design=_mock_candidate_design(cid),
        objective_values=objs,
        constraint_compliance_summary=constraint_summary,
        uncertainty_profile=UncertaintyProfile(uncertainty_type=UncertaintyType.DETERMINISTIC_POINT, objective_intervals={}),
        evidence_tier=EvidenceTier.TIER_1_EMPIRICAL,
        traceability=_mock_traceability(),
        explanation_payload=ExplanationPayload(
            trade_off_summary="mock",
            limiting_barrier="mock",
            primary_strength="mock",
            primary_limitation=None,
            dominance_warnings=[]
        )
    )

def test_single_candidate():
    c = _mock_pareto_candidate("c1", 10.0, 0.5, 0.2, 5.0)
    builder = ParetoFrontConstructor()
    front = builder.construct_front([c])
    assert front.candidate_count == 1
    assert front.candidates[0].pareto_candidate_id == "c1"

def test_two_candidates_a_dominates_b():
    a = _mock_pareto_candidate("a", 10.0, 0.9, 0.1, 5.0)
    b = _mock_pareto_candidate("b", 20.0, 0.5, 0.4, 2.0)
    builder = ParetoFrontConstructor()
    front = builder.construct_front([a, b])
    assert front.candidate_count == 1
    assert front.candidates[0].pareto_candidate_id == "a"

def test_two_candidates_mutually_non_dominated():
    a = _mock_pareto_candidate("a", 10.0, 0.5, 0.4, 2.0)
    b = _mock_pareto_candidate("b", 20.0, 0.9, 0.4, 2.0)
    builder = ParetoFrontConstructor()
    front = builder.construct_front([a, b])
    assert front.candidate_count == 2
    ids = {c.pareto_candidate_id for c in front.candidates}
    assert ids == {"a", "b"}

def test_three_candidates_middle_dominated():
    # 'a' is better than 'm' in thickness and moisture
    a = _mock_pareto_candidate("a", 10.0, 0.9, 0.1, 5.0)
    # 'm' is strictly dominated by 'a'
    m = _mock_pareto_candidate("m", 20.0, 0.5, 0.2, 2.0)
    # 'b' is better than 'a' in gas, but worse in moisture (non-dominated)
    b = _mock_pareto_candidate("b", 15.0, 0.1, 0.0, 10.0)
    
    builder = ParetoFrontConstructor()
    front = builder.construct_front([a, m, b])
    
    assert front.candidate_count == 2
    ids = {c.pareto_candidate_id for c in front.candidates}
    assert ids == {"a", "b"}

def test_identical_objectives_retained():
    a = _mock_pareto_candidate("a", 10.0, 0.5, 0.4, 2.0)
    b = _mock_pareto_candidate("b", 10.0, 0.5, 0.4, 2.0)
    builder = ParetoFrontConstructor()
    front = builder.construct_front([a, b])
    assert front.candidate_count == 2

def test_infeasible_excluded_implicitly():
    a = _mock_pareto_candidate("a", 10.0, 0.9, 0.1, 5.0)
    # Make a UNKNOWN
    a.objective_values["f_thickness"].status = CalculationStatus.UNKNOWN
    
    b = _mock_pareto_candidate("b", 10.0, 0.5, 0.4, 2.0)
    
    builder = ParetoFrontConstructor()
    front = builder.construct_front([a, b])
    
    assert front.candidate_count == 1
    assert front.candidates[0].pareto_candidate_id == "b"

def test_input_permutation_invariance():
    a = _mock_pareto_candidate("a", 10.0, 0.9, 0.1, 5.0)
    b = _mock_pareto_candidate("b", 20.0, 0.5, 0.4, 2.0)
    builder = ParetoFrontConstructor()
    
    f1 = builder.construct_front([a, b])
    f2 = builder.construct_front([b, a])
    
    assert f1.candidates[0].pareto_candidate_id == "a"
    assert f2.candidates[0].pareto_candidate_id == "a"
