"""
Scientific physics schemas for Phase 4.

Defines calculation result states, comprehensive traceability structures,
and generic scientific result wrappers with uncertainty and unit metadata.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class CalculationStatus(str, Enum):
    """
    Epistemic calculation status for physics and engineering calculations.

    CALCULATED:
        All required inputs and verified model parameters exist; the result is
        scientifically defensible.

    PARTIALLY_CALCULATED:
        Some scientific outputs (e.g. gas consumption rate per kg, vapor pressure gradient)
        are computed, but missing physical geometry (mass, area) prevents complete
        package-level requirement closure.

    UNKNOWN:
        Critical scientific evidence or property values are missing; calculation cannot proceed.
    """
    CALCULATED = "CALCULATED"
    PARTIALLY_CALCULATED = "PARTIALLY_CALCULATED"
    UNKNOWN = "UNKNOWN"


class ScientificTraceability(BaseModel):
    """
    Reusable scientific provenance and audit trail for any physics calculation.

    Answers:
    1. Which model produced this?
    2. Which equation was used?
    3. Which inputs were used?
    4. Where did the parameters come from?
    5. What units were used?
    6. What validity range applies?
    7. What assumptions were made?
    8. What uncertainty exists?
    9. Why might the calculation be UNKNOWN or PARTIALLY_CALCULATED?
    """

    model_name: str = Field(..., description="Standardized scientific model identifier.")
    equation_form: str = Field(..., description="Mathematical representation of the equation.")
    equation_reference: Optional[str] = Field(
        default=None,
        description="Textbook, standard (ASTM/ISO), or peer-reviewed literature reference."
    )
    scientific_sources: List[str] = Field(
        default_factory=list,
        description="Bibliographic sources for parameters and underlying mechanisms."
    )
    inputs_used: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs of input variables supplied to the model."
    )
    parameters_used: Dict[str, Any] = Field(
        default_factory=dict,
        description="Physical constants, kinetic coefficients, or empirical parameters used."
    )
    parameter_sources: Dict[str, str] = Field(
        default_factory=dict,
        description="Provenance for each parameter used (e.g. 'literature_citation', 'user_input')."
    )
    units_used: Dict[str, str] = Field(
        default_factory=dict,
        description="SI or engineering units associated with inputs, parameters, and outputs."
    )
    validity_range: Dict[str, Tuple[float, float]] = Field(
        default_factory=dict,
        description="Applicable physical or physiological domains (e.g. temperature, aw)."
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Explicit physical and thermodynamic simplifications made by the model."
    )
    uncertainty_description: Optional[str] = Field(
        default=None,
        description="Description of how uncertainty in inputs propagates to the output."
    )
    uncertainty_interval: Optional[Tuple[float, float]] = Field(
        default=None,
        description="Numeric lower and upper bounds of the calculated quantity."
    )
    failure_or_unknown_reason: Optional[str] = Field(
        default=None,
        description="Explanation if calculation resulted in UNKNOWN or PARTIALLY_CALCULATED."
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Boundary warnings, extrapolation caveats, or safety alerts."
    )


class ScientificResult(BaseModel):
    """
    Generic wrapper for a scalar or interval scientific calculation result.
    """

    status: CalculationStatus = Field(..., description="Calculation epistemic state.")
    value: Optional[float] = Field(default=None, description="Point estimate or representative value.")
    unit: Optional[str] = Field(default=None, description="Scientific or engineering unit.")
    uncertainty_range: Optional[Tuple[float, float]] = Field(
        default=None,
        description="Propagated or observed uncertainty bounds [min, max]."
    )
    minimum_value: Optional[float] = Field(default=None, description="Conservative lower bound.")
    maximum_value: Optional[float] = Field(default=None, description="Conservative upper bound.")
    traceability: ScientificTraceability = Field(
        ...,
        description="Complete provenance and equation audit trail."
    )
