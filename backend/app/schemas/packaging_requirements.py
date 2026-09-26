"""
Packaging Requirement Envelope schemas for Phase 4.

Structures the output of the Physics & Packaging Requirement Engine,
defining gas barrier targets, moisture barrier targets, microbial safety limits,
and shelf-life feasibility without selecting or recommending specific materials.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.schemas.physics import CalculationStatus, ScientificResult, ScientificTraceability


class DeteriorationMechanismStatus(BaseModel):
    """Assessment of an individual deterioration mode for a food commodity."""

    mechanism: str = Field(..., description="Mechanism name (e.g. 'respiration', 'moisture_transfer', 'microbial_growth').")
    eligible: bool = Field(..., description="Whether this food commodity physically undergoes this degradation mode.")
    computable: bool = Field(..., description="Whether sufficient property/environmental evidence exists to calculate requirements.")
    status: CalculationStatus = Field(..., description="Overall calculation state for this mechanism.")
    reason: Optional[str] = Field(default=None, description="Explanation for ineligibility or non-computability.")
    evidence_references: List[str] = Field(default_factory=list, description="Associated evidence or inference citations.")


class DeteriorationProfile(BaseModel):
    """Complete deterioration matrix identifying active and limiting degradation pathways."""

    commodity: str = Field(..., description="Commodity name.")
    mechanisms: Dict[str, DeteriorationMechanismStatus] = Field(
        default_factory=dict,
        description="Dictionary mapping mechanism names to their respective assessment status."
    )
    primary_vulnerabilities: List[str] = Field(
        default_factory=list,
        description="Ranked or identified critical degradation mechanisms."
    )


class GasExchangeRequirement(BaseModel):
    """
    Scientific packaging gas permeability requirements (OTR, CO2TR, beta ratio)
    derived from respiration rates and modified atmosphere preservation targets.
    """

    status: CalculationStatus = Field(..., description="Gas exchange calculation status.")
    target_o2_percent: Optional[float] = Field(default=None, description="Target equilibrium O2 concentration in headspace (%).")
    target_o2_range: Optional[Tuple[float, float]] = Field(default=None, description="Safe equilibrium O2 range (min%, max%).")
    target_co2_percent: Optional[float] = Field(default=None, description="Target equilibrium CO2 concentration in headspace (%).")
    target_co2_range: Optional[Tuple[float, float]] = Field(default=None, description="Safe equilibrium CO2 range (min%, max%).")

    required_otr_cc_per_pkg_day: Optional[ScientificResult] = Field(
        default=None,
        description="Required absolute Oxygen Transmission Rate per whole package (cc / package / day)."
    )
    required_otr_per_area: Optional[ScientificResult] = Field(
        default=None,
        description="Required normalized OTR (cc / (m² · day · atm)) if package area is specified."
    )
    required_co2tr_cc_per_pkg_day: Optional[ScientificResult] = Field(
        default=None,
        description="Required absolute CO2 Transmission Rate per whole package (cc / package / day)."
    )
    required_co2tr_per_area: Optional[ScientificResult] = Field(
        default=None,
        description="Required normalized CO2TR (cc / (m² · day · atm)) if package area is specified."
    )
    ideal_beta_ratio_co2_to_o2: Optional[ScientificResult] = Field(
        default=None,
        description="Ideal film permeability selectivity ratio (P_CO2 / P_O2)."
    )
    traceability: Optional[ScientificTraceability] = Field(
        default=None,
        description="Provenance of gas exchange mass balance calculation."
    )
    warnings: List[str] = Field(default_factory=list)


class MoistureRequirement(BaseModel):
    """
    Scientific moisture barrier requirements (WVTR, water vapor permeance)
    derived from water activity limits, product sorption, and ambient RH gradients.
    """

    status: CalculationStatus = Field(..., description="Moisture calculation status.")
    initial_water_activity: Optional[float] = Field(default=None, description="Initial food water activity (aw).")
    critical_water_activity: Optional[float] = Field(default=None, description="Critical spoilage/collapse water activity (aw,crit).")
    water_vapor_pressure_gradient_kpa: Optional[ScientificResult] = Field(
        default=None,
        description="Water vapor pressure driving force (Δp_w) in kPa."
    )
    moisture_transfer_rate_g_day: Optional[ScientificResult] = Field(
        default=None,
        description="Allowable or expected moisture flux in grams H2O / day."
    )
    required_wvtr_g_per_pkg_day: Optional[ScientificResult] = Field(
        default=None,
        description="Required absolute Water Vapor Transmission Rate per package (g H2O / package / day)."
    )
    required_wvtr_per_area: Optional[ScientificResult] = Field(
        default=None,
        description="Required normalized WVTR (g / (m² · day)) if package area is specified."
    )
    moisture_limited_shelf_life_days: Optional[ScientificResult] = Field(
        default=None,
        description="Estimated shelf life limited purely by moisture gain/loss."
    )
    traceability: Optional[ScientificTraceability] = Field(
        default=None,
        description="Provenance of moisture transfer calculation."
    )
    warnings: List[str] = Field(default_factory=list)


class MicrobialRequirement(BaseModel):
    """
    Predictive microbiological safety limits derived from growth kinetics,
    pH, water activity, and temperature hurdles.
    """

    status: CalculationStatus = Field(..., description="Microbial calculation status.")
    target_microorganism: Optional[str] = Field(default=None, description="Target spoilage or pathogenic organism.")
    initial_count_log_cfu: Optional[float] = Field(default=None, description="Initial microbial load (log10 CFU/g).")
    critical_count_log_cfu: Optional[float] = Field(default=None, description="Unacceptable microbial threshold (log10 CFU/g).")
    growth_rate_per_day: Optional[ScientificResult] = Field(default=None, description="Specific growth rate (µ_max in 1/day).")
    lag_time_days: Optional[ScientificResult] = Field(default=None, description="Microbial adaptation lag time in days.")
    microbial_shelf_life_days: Optional[ScientificResult] = Field(
        default=None,
        description="Shelf life limited by microbial proliferation to critical threshold."
    )
    atmosphere_inhibition_factor: Optional[float] = Field(
        default=None,
        description="Growth rate reduction factor due to elevated CO2 / anaerobic conditions."
    )
    traceability: Optional[ScientificTraceability] = Field(
        default=None,
        description="Provenance of microbial model calculation."
    )
    warnings: List[str] = Field(default_factory=list)


class ShelfLifeRequirement(BaseModel):
    """
    Shelf life feasibility assessment combining supported deterioration mechanisms.
    """

    target_days: int = Field(..., description="Target shelf life requested by user.")
    limiting_mechanism: Optional[str] = Field(
        default=None,
        description="Earliest scientifically supported limiting deterioration mode."
    )
    supported_calculated_shelf_life_days: Optional[ScientificResult] = Field(
        default=None,
        description="Calculated shelf life based only on computable mechanisms."
    )
    feasibility: Optional[str] = Field(
        default=None,
        description="Feasibility designation: 'achievable', 'constrained', 'uncertain', 'unknown'."
    )
    status: CalculationStatus = Field(..., description="Overall shelf life calculation status.")
    traceability: Optional[ScientificTraceability] = Field(
        default=None,
        description="Audit trail for multi-mechanism shelf life comparison."
    )


class PackagingRequirementEnvelope(BaseModel):
    """
    Complete scientific packaging performance requirement envelope.

    Defines the exact required gas, moisture, and microbial barrier envelopes
    required to protect the food product under specified environmental conditions.
    Contains absolutely NO material selection or material ranking.
    """

    commodity: str = Field(..., description="Target food commodity.")
    target_shelf_life_days: int = Field(..., description="User requested shelf life.")
    storage_temperature_c: Optional[float] = Field(default=None, description="Storage temperature in °C.")
    relative_humidity_percent: Optional[float] = Field(default=None, description="Ambient relative humidity in %.")

    deterioration_profile: DeteriorationProfile = Field(
        ...,
        description="Active and dormant deterioration mechanism breakdown."
    )
    gas_requirements: GasExchangeRequirement = Field(
        ...,
        description="Oxygen, Carbon Dioxide, and respiration barrier envelope."
    )
    moisture_requirements: MoistureRequirement = Field(
        ...,
        description="Water vapor barrier, sorption, and water activity envelope."
    )
    microbial_requirements: MicrobialRequirement = Field(
        ...,
        description="Microbial growth limits and hurdle requirements."
    )
    shelf_life: ShelfLifeRequirement = Field(
        ...,
        description="Shelf life feasibility and supported limiting mechanism."
    )

    overall_status: CalculationStatus = Field(
        ...,
        description="Overall calculation status across all scientific mechanisms."
    )
    temperature_effects: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of temperature-dependent kinetic shifts."
    )
    all_assumptions: List[str] = Field(
        default_factory=list,
        description="Consolidated list of physical and scientific assumptions across all active models."
    )
    all_warnings: List[str] = Field(
        default_factory=list,
        description="Consolidated scientific caveats and domain warnings."
    )
    traceability_log: List[ScientificTraceability] = Field(
        default_factory=list,
        description="Full audit trail of all scientific models executed."
    )
