"""
Pydantic schemas for the Generic Property Inference Engine (Phase 3).

Captures inferred scientific properties, epistemic status, uncertainty intervals,
context resolution levels, source evidence traceability, and domain warnings.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.schemas.food_evidence import FoodEvidenceRecord
from app.schemas.property_status import PropertyStatusEnum


class InferenceResolutionLevel(str, Enum):
    """Resolution depth at which an evidence match or inference was achieved."""
    USER_SUPPLIED = "user_supplied"
    EXACT_CONTEXT_MATCH = "exact_context_match"
    VARIETY_FALLBACK = "variety_fallback"
    FORM_FALLBACK = "form_fallback"
    TEMPERATURE_MATCH = "temperature_match"
    CLOSEST_TEMPERATURE_BOUND = "closest_temperature_bound"
    GENERAL_COMMODITY_MATCH = "general_commodity_match"
    UNKNOWN = "unknown"


class InferenceWarning(BaseModel):
    """Domain warning or caveat associated with an inferred property value."""
    code: str = Field(..., description="Machine-readable error/warning code (e.g. 'NO_EVIDENCE', 'TEMP_EXTRAPOLATION').")
    message: str = Field(..., description="Human-readable explanation.")
    severity: str = Field(default="warning", description="'info', 'warning', or 'critical'.")


class InferredProperty(BaseModel):
    """
    Representation of an inferred or user-supplied property value with complete
    scientific provenance, uncertainty range, and confidence scoring.
    """

    property_name: str = Field(
        ...,
        description="Standard property identifier (e.g. 'respiration_rate', 'moisture_percent', 'ph')."
    )
    value: Optional[float] = Field(
        default=None,
        description="Point estimate or best representative value. NULL if strictly unknown."
    )
    unit: Optional[str] = Field(
        default=None,
        description="Standard unit of measurement (e.g. '%', 'mg CO2/kg/hr', 'pH')."
    )
    status: PropertyStatusEnum = Field(
        default=PropertyStatusEnum.unknown,
        description="Epistemic status ('measured', 'literature', 'inferred', 'unknown')."
    )
    resolution_level: InferenceResolutionLevel = Field(
        default=InferenceResolutionLevel.UNKNOWN,
        description="Matching level in the evidence hierarchy."
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score [0.0 - 1.0] reflecting evidence strength and context alignment."
    )
    uncertainty_range: Optional[Tuple[float, float]] = Field(
        default=None,
        description="Observed or derived lower and upper uncertainty bounds (min, max)."
    )
    minimum_value: Optional[float] = Field(
        default=None,
        description="Absolute minimum observed value in supporting evidence."
    )
    maximum_value: Optional[float] = Field(
        default=None,
        description="Absolute maximum observed value in supporting evidence."
    )
    supporting_evidence: List[FoodEvidenceRecord] = Field(
        default_factory=list,
        description="Full scientific evidence records used to derive this estimate."
    )
    citations: List[str] = Field(
        default_factory=list,
        description="Formatted bibliographic citations and DOIs of supporting literature."
    )
    acquisition_method: Optional[str] = Field(
        default=None,
        description="Method description (e.g. 'user_input', 'literature_exact_match', 'multi_source_range')."
    )
    warnings: List[InferenceWarning] = Field(
        default_factory=list,
        description="Specific caveats, data gaps, or boundary warnings."
    )


class PropertyInferenceProfile(BaseModel):
    """
    Complete inferred scientific profile for a commodity request.

    Maps all evaluated food properties to their respective InferredProperty results.
    """

    commodity: str = Field(..., description="Target commodity name.")
    variety: Optional[str] = Field(default=None, description="Cultivar or variety if known.")
    product_form: Optional[str] = Field(default=None, description="Product form (whole, sliced, fillet).")
    ripeness_stage: Optional[str] = Field(default=None, description="Maturity or ripeness stage.")
    storage_type: Optional[str] = Field(default=None, description="Storage regime (ambient, chilled, frozen).")
    storage_temperature_c: Optional[float] = Field(default=None, description="Operating storage temperature in °C.")
    relative_humidity_percent: Optional[float] = Field(default=None, description="Operating storage RH in %.")

    properties: Dict[str, InferredProperty] = Field(
        default_factory=dict,
        description="Key-value mapping from property name to its detailed InferredProperty object."
    )
    all_warnings: List[InferenceWarning] = Field(
        default_factory=list,
        description="Aggregated list of warnings across all evaluated properties."
    )
    overall_confidence: Optional[float] = Field(
        default=None,
        description="Mean confidence across all resolved properties, or None if all are unknown."
    )
