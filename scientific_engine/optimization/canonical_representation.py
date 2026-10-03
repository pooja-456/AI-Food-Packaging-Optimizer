"""
M6-F (B5B): Canonical Optimization-State Representation Implementation.

Provides deterministic, order-invariant, structure-preserving canonical representation
for the frozen M6-A Optimization-State Identity:
1. Phase 4 Requirement Envelope (canonicalized)
2. Package Geometry (exact scalars)
3. Active Objective Set (unordered -> sorted unique strings)
4. Eligible Candidate ID Set (unordered -> sorted unique candidate IDs)

Adheres strictly to docs/m6b5b_canonical_optimization_state_representation.md:
- NO floating-point rounding, epsilon, or midpoint collapse.
- NO raw biological context (commodity, variety, etc.) in identity.
- NO provenance, evidence tier, citations, or warning logs.
- ABSENT and UNKNOWN statuses are preserved as distinct states.
"""

import json
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field

from app.schemas.optimization import OptimizationInputEnvelope, PackageGeometry, PackagingCandidate
from app.schemas.packaging_requirements import (
    PackagingRequirementEnvelope,
    GasExchangeRequirement,
    MoistureRequirement,
    MicrobialRequirement,
    ShelfLifeRequirement,
    DeteriorationProfile,
    DeteriorationMechanismStatus
)
from app.schemas.physics import CalculationStatus, ScientificResult


def _canonicalize_scientific_result(sr: Optional[ScientificResult]) -> Any:
    """Canonicalize a ScientificResult object or preserve ABSENT state."""
    if sr is None:
        return "ABSENT"
    
    status_str = sr.status.value if isinstance(sr.status, CalculationStatus) else str(sr.status)
    
    return {
        "presence": "PRESENT",
        "status": status_str,
        "value": sr.value,
        "unit": sr.unit,
        "minimum_value": sr.minimum_value,
        "maximum_value": sr.maximum_value,
        "uncertainty_range": list(sr.uncertainty_range) if sr.uncertainty_range is not None else None,
    }


def _canonicalize_deterioration_profile(profile: Optional[DeteriorationProfile]) -> Any:
    """Canonicalize DeteriorationProfile, excluding raw commodity and citations."""
    if profile is None:
        return "ABSENT"
    
    mechanisms_canon = {}
    for k in sorted(profile.mechanisms.keys()):
        mech = profile.mechanisms[k]
        mech_status = mech.status.value if isinstance(mech.status, CalculationStatus) else str(mech.status)
        mechanisms_canon[k] = {
            "mechanism": mech.mechanism,
            "eligible": mech.eligible,
            "computable": mech.computable,
            "status": mech_status,
            "reason": mech.reason
        }
        
    return {
        "mechanisms": mechanisms_canon,
        "primary_vulnerabilities": sorted(list(set(profile.primary_vulnerabilities))) if profile.primary_vulnerabilities else []
    }


def _canonicalize_gas_requirements(req: Optional[GasExchangeRequirement]) -> Any:
    """Canonicalize GasExchangeRequirement, excluding traceability and warnings."""
    if req is None:
        return "ABSENT"
    
    status_str = req.status.value if isinstance(req.status, CalculationStatus) else str(req.status)
    
    return {
        "status": status_str,
        "target_o2_percent": req.target_o2_percent,
        "target_o2_range": list(req.target_o2_range) if req.target_o2_range is not None else None,
        "target_co2_percent": req.target_co2_percent,
        "target_co2_range": list(req.target_co2_range) if req.target_co2_range is not None else None,
        "required_otr_cc_per_pkg_day": _canonicalize_scientific_result(req.required_otr_cc_per_pkg_day),
        "required_otr_per_area": _canonicalize_scientific_result(req.required_otr_per_area),
        "required_co2tr_cc_per_pkg_day": _canonicalize_scientific_result(req.required_co2tr_cc_per_pkg_day),
        "required_co2tr_per_area": _canonicalize_scientific_result(req.required_co2tr_per_area),
        "ideal_beta_ratio_co2_to_o2": _canonicalize_scientific_result(req.ideal_beta_ratio_co2_to_o2),
    }


def _canonicalize_moisture_requirements(req: Optional[MoistureRequirement]) -> Any:
    """Canonicalize MoistureRequirement, excluding traceability and warnings."""
    if req is None:
        return "ABSENT"
    
    status_str = req.status.value if isinstance(req.status, CalculationStatus) else str(req.status)
    
    return {
        "status": status_str,
        "initial_water_activity": req.initial_water_activity,
        "critical_water_activity": req.critical_water_activity,
        "water_vapor_pressure_gradient_kpa": _canonicalize_scientific_result(req.water_vapor_pressure_gradient_kpa),
        "moisture_transfer_rate_g_day": _canonicalize_scientific_result(req.moisture_transfer_rate_g_day),
        "required_wvtr_g_per_pkg_day": _canonicalize_scientific_result(req.required_wvtr_g_per_pkg_day),
        "required_wvtr_per_area": _canonicalize_scientific_result(req.required_wvtr_per_area),
        "moisture_limited_shelf_life_days": _canonicalize_scientific_result(req.moisture_limited_shelf_life_days),
    }


def _canonicalize_microbial_requirements(req: Optional[MicrobialRequirement]) -> Any:
    """Canonicalize MicrobialRequirement, excluding traceability and warnings."""
    if req is None:
        return "ABSENT"
    
    status_str = req.status.value if isinstance(req.status, CalculationStatus) else str(req.status)
    
    return {
        "status": status_str,
        "target_microorganism": req.target_microorganism,
        "initial_count_log_cfu": req.initial_count_log_cfu,
        "critical_count_log_cfu": req.critical_count_log_cfu,
        "growth_rate_per_day": _canonicalize_scientific_result(req.growth_rate_per_day),
        "lag_time_days": _canonicalize_scientific_result(req.lag_time_days),
        "microbial_shelf_life_days": _canonicalize_scientific_result(req.microbial_shelf_life_days),
        "atmosphere_inhibition_factor": req.atmosphere_inhibition_factor,
    }


def _canonicalize_shelf_life(req: Optional[ShelfLifeRequirement]) -> Any:
    """Canonicalize ShelfLifeRequirement, excluding traceability."""
    if req is None:
        return "ABSENT"
    
    status_str = req.status.value if isinstance(req.status, CalculationStatus) else str(req.status)
    
    return {
        "target_days": req.target_days,
        "limiting_mechanism": req.limiting_mechanism,
        "supported_calculated_shelf_life_days": _canonicalize_scientific_result(req.supported_calculated_shelf_life_days),
        "feasibility": req.feasibility,
        "status": status_str,
    }


def _canonicalize_requirement_envelope(env: PackagingRequirementEnvelope) -> Dict[str, Any]:
    """
    Canonicalize PackagingRequirementEnvelope.
    Excludes raw commodity context, assumptions, warnings, and traceability logs.
    """
    overall_status_str = env.overall_status.value if isinstance(env.overall_status, CalculationStatus) else str(env.overall_status)
    
    return {
        "target_shelf_life_days": env.target_shelf_life_days,
        "storage_temperature_c": env.storage_temperature_c,
        "relative_humidity_percent": env.relative_humidity_percent,
        "overall_status": overall_status_str,
        "deterioration_profile": _canonicalize_deterioration_profile(env.deterioration_profile),
        "gas_requirements": _canonicalize_gas_requirements(env.gas_requirements),
        "moisture_requirements": _canonicalize_moisture_requirements(env.moisture_requirements),
        "microbial_requirements": _canonicalize_microbial_requirements(env.microbial_requirements),
        "shelf_life": _canonicalize_shelf_life(env.shelf_life),
    }


def _canonicalize_package_geometry(geom: PackageGeometry) -> Dict[str, Any]:
    """Canonicalize PackageGeometry using exact scalar values."""
    return {
        "surface_area_m2": geom.surface_area_m2,
        "headspace_volume_cm3": geom.headspace_volume_cm3,
        "product_mass_kg": geom.product_mass_kg,
    }


def _canonicalize_active_objectives(objectives: List[str]) -> List[str]:
    """Canonicalize active objectives set by sorting unique identifiers lexicographically."""
    return sorted(list(set(objectives)))


def _canonicalize_candidate_ids(candidates: Union[List[PackagingCandidate], List[str]]) -> List[str]:
    """Canonicalize candidate materials by sorting unique Candidate IDs lexicographically."""
    ids = []
    for item in candidates:
        if isinstance(item, str):
            ids.append(item)
        elif hasattr(item, "candidate_id"):
            ids.append(item.candidate_id)
        elif isinstance(item, dict) and "candidate_id" in item:
            ids.append(item["candidate_id"])
    return sorted(list(set(ids)))


class CanonicalOptimizationState(BaseModel):
    """
    Structured, deterministic canonical representation of an Optimization-State Identity.
    """

    requirement_envelope: Dict[str, Any] = Field(
        ...,
        description="Canonicalized Phase 4 requirements."
    )
    package_geometry: Dict[str, Any] = Field(
        ...,
        description="Exact scalar package geometry parameters."
    )
    active_objectives: List[str] = Field(
        ...,
        description="Lexicographically sorted unique active objective identifiers."
    )
    eligible_candidate_ids: List[str] = Field(
        ...,
        description="Lexicographically sorted unique candidate material UUIDs."
    )

    def to_dict(self) -> Dict[str, Any]:
        """Return canonical state as a Python dictionary."""
        return {
            "requirement_envelope": self.requirement_envelope,
            "package_geometry": self.package_geometry,
            "active_objectives": self.active_objectives,
            "eligible_candidate_ids": self.eligible_candidate_ids,
        }

    def to_canonical_json(self) -> str:
        """
        Return deterministic JSON string representation with keys sorted recursively.
        Does NOT alter or round floating point values.
        """
        return json.dumps(self.to_dict(), sort_keys=True)


def build_canonical_representation(
    requirement_envelope: PackagingRequirementEnvelope,
    package_geometry: PackageGeometry,
    active_objectives: List[str],
    eligible_candidate_materials: Union[List[PackagingCandidate], List[str]]
) -> CanonicalOptimizationState:
    """
    Construct the canonical representation for a given optimization identity.
    """
    return CanonicalOptimizationState(
        requirement_envelope=_canonicalize_requirement_envelope(requirement_envelope),
        package_geometry=_canonicalize_package_geometry(package_geometry),
        active_objectives=_canonicalize_active_objectives(active_objectives),
        eligible_candidate_ids=_canonicalize_candidate_ids(eligible_candidate_materials)
    )


def build_canonical_representation_from_envelope(
    envelope: OptimizationInputEnvelope
) -> CanonicalOptimizationState:
    """
    Construct the canonical representation directly from an OptimizationInputEnvelope.
    """
    return build_canonical_representation(
        requirement_envelope=envelope.packaging_requirement_envelope,
        package_geometry=envelope.package_geometry,
        active_objectives=envelope.active_objectives,
        eligible_candidate_materials=envelope.eligible_candidate_materials
    )
