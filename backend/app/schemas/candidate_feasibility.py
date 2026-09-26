"""
Candidate feasibility output schema for Phase 5 deterministic hard-constraint filtering.

Defines the candidate-level feasibility assessment aggregating individual
constraint evaluations across gas barrier, moisture barrier, and any
future barrier requirements — without ranking, scoring, or recommendation.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.constraints import ConstraintEvaluation, ConstraintStatus
from app.schemas.physics import ScientificTraceability


class CandidateFeasibility(BaseModel):
    """
    Overall hard-constraint feasibility assessment for a single candidate material
    against a Phase 4 PackagingRequirementEnvelope.

    Logic:
        IF any required constraint is INFEASIBLE → overall = INFEASIBLE
        ELSE IF all required constraints are FEASIBLE → overall = FEASIBLE
        ELSE → overall = UNKNOWN
    """

    material_id: str = Field(
        ...,
        description="Unique identifier for the candidate material."
    )
    material_name: str = Field(
        ...,
        description="Human-readable material name."
    )
    material_category: Optional[str] = Field(
        default=None,
        description="Material structural category (e.g. 'mono_polymer', 'foil_laminate')."
    )
    overall_status: ConstraintStatus = Field(
        ...,
        description="Aggregate feasibility status: FEASIBLE, INFEASIBLE, or UNKNOWN."
    )
    constraint_results: List[ConstraintEvaluation] = Field(
        default_factory=list,
        description="Complete list of individual constraint evaluations."
    )
    passed_constraints: List[str] = Field(
        default_factory=list,
        description="Constraint types that evaluated to FEASIBLE."
    )
    failed_constraints: List[str] = Field(
        default_factory=list,
        description="Constraint types that evaluated to INFEASIBLE."
    )
    unknown_constraints: List[str] = Field(
        default_factory=list,
        description="Constraint types that evaluated to UNKNOWN."
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Aggregated warnings across all constraint evaluations."
    )
    traceability: Optional[ScientificTraceability] = Field(
        default=None,
        description="Aggregated audit trail for the candidate feasibility evaluation."
    )


class FilteringResult(BaseModel):
    """
    Complete output of Phase 5 deterministic hard-constraint filtering
    across all candidate materials in the reference dataset.
    """

    commodity: str = Field(
        ...,
        description="Target food commodity."
    )
    total_candidates_evaluated: int = Field(
        ...,
        description="Total number of materials evaluated."
    )
    feasible_candidates: List[CandidateFeasibility] = Field(
        default_factory=list,
        description="Materials that passed ALL hard constraints."
    )
    infeasible_candidates: List[CandidateFeasibility] = Field(
        default_factory=list,
        description="Materials that failed at least one hard constraint."
    )
    unknown_candidates: List[CandidateFeasibility] = Field(
        default_factory=list,
        description="Materials with indeterminate feasibility (no failures, but at least one unknown)."
    )
    all_results: List[CandidateFeasibility] = Field(
        default_factory=list,
        description="Full list of all candidate evaluations in evaluation order."
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="System-level warnings."
    )
