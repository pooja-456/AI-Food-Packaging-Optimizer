"""
M7-E4: Benchmark Validation Engine.

Implements scenario contract validation and Pareto front structural validation
using the frozen M6-B3 objective definitions, M6-B4A dominance rules, and M6-B4B front construction.
"""

from typing import Dict, List, Tuple
from app.schemas.optimization import (
    PackagingCandidate,
    ParetoCandidate,
    ParetoFront,
    ObjectiveDirection,
)
from app.schemas.physics import CalculationStatus
from scientific_engine.optimization.benchmark_contracts import (
    BenchmarkScenario,
    AUTHORITATIVE_OBJECTIVES,
    OBJECTIVE_DIRECTIONS,
)
from scientific_engine.optimization.canonical_representation import build_canonical_representation
from scientific_engine.optimization.pareto import dominates


class ScenarioValidationError(ValueError):
    """Raised when a benchmark scenario fails contract validation."""
    pass


class ParetoValidationResult:
    """Result structure for Pareto front structural validation."""
    def __init__(self, is_valid: bool, errors: List[str]):
        self.is_valid = is_valid
        self.errors = errors


def validate_benchmark_scenario(scenario: BenchmarkScenario) -> str:
    """
    Validates a BenchmarkScenario against M6-A identity and M6-B3 objective contracts.
    Constructs the canonical 4-part representation per M6-F/B5B.
    Returns the canonical JSON representation string.
    """
    if not scenario.scenario_id:
        raise ScenarioValidationError("Scenario ID must not be empty.")

    if not scenario.requirement_envelope:
        raise ScenarioValidationError("Phase 4 Requirement Envelope must be present.")

    if not scenario.package_geometry:
        raise ScenarioValidationError("Package Geometry must be present.")

    if scenario.package_geometry.surface_area_m2 <= 0:
        raise ScenarioValidationError(
            f"Package surface area must be > 0, got {scenario.package_geometry.surface_area_m2}."
        )

    if not scenario.active_objectives:
        raise ScenarioValidationError("Active objective set must not be empty.")

    # Objective Set Validation: Must contain ONLY authorized M6-B3 objectives
    for obj_name in scenario.active_objectives:
        if obj_name not in AUTHORITATIVE_OBJECTIVES:
            raise ScenarioValidationError(
                f"Unauthorized objective '{obj_name}' in scenario. Objective pool MUST strictly match M6-B3: {AUTHORITATIVE_OBJECTIVES}."
            )

    if not scenario.eligible_candidate_ids:
        raise ScenarioValidationError("Eligible Candidate ID set must not be empty.")

    # Construct canonical 4-part identity representation per M6-F
    canonical_state = build_canonical_representation(
        requirement_envelope=scenario.requirement_envelope,
        package_geometry=scenario.package_geometry,
        active_objectives=scenario.active_objectives,
        eligible_candidate_materials=scenario.eligible_candidate_ids,
    )
    canonical_json = canonical_state.to_canonical_json()
    scenario.canonical_identity = canonical_json
    return canonical_json


def validate_pareto_front_structure(
    pareto_front: ParetoFront,
    scenario: BenchmarkScenario,
    eligible_candidates_map: Dict[str, PackagingCandidate],
) -> ParetoValidationResult:
    """
    Validates the structural integrity of a solver's returned ParetoFront against M6-B4A/B:
    1. Candidate membership check (candidates belong to eligible search space).
    2. Objective completeness check (all active objectives present).
    3. Feasibility compliance (no INFEASIBLE or UNKNOWN candidate on Pareto front).
    4. Dominance consistency check (no candidate on front dominates another candidate on front).
    """
    errors: List[str] = []

    if pareto_front is None:
        return ParetoValidationResult(is_valid=False, errors=["Pareto front object is None."])

    front_candidates = pareto_front.candidates

    # 1. Candidate Membership Check
    for cand in front_candidates:
        cand_id = cand.pareto_candidate_id
        if cand_id not in eligible_candidates_map:
            errors.append(
                f"Candidate '{cand_id}' on Pareto front does not belong to scenario's eligible candidate set."
            )

    # 2. Objective Completeness & Feasibility Compliance Check
    for cand in front_candidates:
        cand_id = cand.pareto_candidate_id
        
        # Hard constraint compliance check
        if not cand.constraint_compliance_summary.all_hard_constraints_satisfied:
            errors.append(
                f"Candidate '{cand_id}' on Pareto front violates Phase 5 hard constraints."
            )

        for obj_name in scenario.active_objectives:
            if obj_name not in cand.objective_values:
                errors.append(
                    f"Candidate '{cand_id}' missing active objective '{obj_name}'."
                )
                continue

            obj_val = cand.objective_values[obj_name]
            
            # UNKNOWN != FEASIBLE check
            if obj_val.status == CalculationStatus.UNKNOWN or (obj_val.value is None and not obj_val.is_interval):
                errors.append(
                    f"Candidate '{cand_id}' has UNKNOWN/null status for objective '{obj_name}' on Pareto front."
                )

            # Direction consistency check
            expected_direction = OBJECTIVE_DIRECTIONS.get(obj_name)
            if expected_direction and obj_val.direction != expected_direction:
                errors.append(
                    f"Candidate '{cand_id}' objective '{obj_name}' has direction '{obj_val.direction}', expected '{expected_direction}'."
                )

    # 3. Dominance Consistency Check (Internal Non-Domination)
    for i, cand_i in enumerate(front_candidates):
        for j, cand_j in enumerate(front_candidates):
            if i == j:
                continue
            if dominates(cand_j.objective_values, cand_i.objective_values):
                errors.append(
                    f"Pareto front integrity violation: Candidate '{cand_j.pareto_candidate_id}' dominates candidate '{cand_i.pareto_candidate_id}' on the same front."
                )

    is_valid = len(errors) == 0
    return ParetoValidationResult(is_valid=is_valid, errors=errors)
