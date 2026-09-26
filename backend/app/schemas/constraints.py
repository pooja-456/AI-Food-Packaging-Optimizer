"""
Pydantic schemas for deterministic hard-constraint filtering (Phase 5).

Defines individual constraint evaluation records, comparison operators,
environmental condition match levels, and status indicators without ranking
or recommending materials.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.schemas.physics import ScientificTraceability


class ConstraintStatus(str, Enum):
    """
    Deterministic feasibility status for an individual constraint or candidate material.

    FEASIBLE:
        The material evidence definitively satisfies the requirement under compatible conditions.

    INFEASIBLE:
        The material evidence definitively violates the requirement.

    UNKNOWN:
        Missing property evidence, incompatible/unsupported test conditions,
        unresolvable unit mismatch, or indeterminate overlapping uncertainty intervals.
    """
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    UNKNOWN = "UNKNOWN"


class ComparisonOperator(str, Enum):
    """
    Explicit mathematical comparison operator governing a constraint evaluation.
    """
    LE = "<="        # Material property must be less than or equal to maximum allowable requirement (e.g. WVTR, max OTR)
    GE = ">="        # Material property must be greater than or equal to minimum required threshold
    EQ = "=="        # Material property must match a target value
    IN_RANGE = "in_range"  # Material property must lie within target interval [min, max] (e.g. EMAP OTR window)


class ConditionMatchLevel(str, Enum):
    """
    Assessment of test condition compatibility (Temperature, RH, Test Standard).
    """
    EXACT = "exact"              # Test condition directly matches requirement environmental condition (within delta tolerance)
    SUPPORTED = "supported"      # Test condition is scientifically applicable to requirement condition
    INCOMPATIBLE = "incompatible"# Test condition significantly diverges with no validated correction model
    UNKNOWN = "unknown"          # Test condition is unrecorded in material evidence or requirement


class ConstraintEvaluation(BaseModel):
    """
    Evaluation record for a single hard constraint applied to a material candidate.
    """

    constraint_type: str = Field(
        ...,
        description="Standard property identifier (e.g. 'oxygen_transmission_rate', 'water_vapor_transmission_rate')."
    )
    status: ConstraintStatus = Field(
        ...,
        description="Outcome of deterministic constraint evaluation: FEASIBLE, INFEASIBLE, or UNKNOWN."
    )
    comparison_operator: ComparisonOperator = Field(
        ...,
        description="Explicit mathematical comparison operator used."
    )
    required_value: Optional[float] = Field(
        default=None,
        description="Point estimate or representative required barrier target."
    )
    required_unit: Optional[str] = Field(
        default=None,
        description="Engineering unit of the requirement."
    )
    required_range: Optional[Tuple[float, float]] = Field(
        default=None,
        description="Target allowable range or uncertainty interval [min, max] of requirement."
    )
    material_value: Optional[float] = Field(
        default=None,
        description="Point estimate or representative value from material evidence."
    )
    material_unit: Optional[str] = Field(
        default=None,
        description="Engineering unit of the material measurement."
    )
    material_range: Optional[Tuple[float, float]] = Field(
        default=None,
        description="Reported range or tolerance interval [min, max] from material evidence."
    )
    condition_match: ConditionMatchLevel = Field(
        default=ConditionMatchLevel.UNKNOWN,
        description="Environmental test condition compatibility status."
    )
    test_temperature_c: Optional[float] = Field(
        default=None,
        description="Temperature at which material property was measured."
    )
    test_relative_humidity_percent: Optional[float] = Field(
        default=None,
        description="Relative humidity at which material property was measured."
    )
    material_evidence_reference: Optional[str] = Field(
        default=None,
        description="Bibliographic citation, handbook, or datasheet source of material evidence."
    )
    reason: Optional[str] = Field(
        default=None,
        description="Deterministic scientific explanation for the assigned status."
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Condition mismatch warnings, unit caveats, or uncertainty flags."
    )
    traceability: Optional[ScientificTraceability] = Field(
        default=None,
        description="Audit trail for the constraint evaluation."
    )
