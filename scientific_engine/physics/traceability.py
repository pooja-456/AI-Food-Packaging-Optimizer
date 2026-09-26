"""
Scientific traceability builder for Phase 4 physics and engineering calculations.
"""

from typing import Any, Dict, List, Optional, Tuple
from app.schemas.physics import ScientificTraceability


def make_traceability(
    model_name: str,
    equation_form: str,
    equation_reference: Optional[str] = None,
    scientific_sources: Optional[List[str]] = None,
    inputs_used: Optional[Dict[str, Any]] = None,
    parameters_used: Optional[Dict[str, Any]] = None,
    parameter_sources: Optional[Dict[str, str]] = None,
    units_used: Optional[Dict[str, str]] = None,
    validity_range: Optional[Dict[str, Tuple[float, float]]] = None,
    assumptions: Optional[List[str]] = None,
    uncertainty_description: Optional[str] = None,
    uncertainty_interval: Optional[Tuple[float, float]] = None,
    failure_or_unknown_reason: Optional[str] = None,
    warnings: Optional[List[str]] = None,
) -> ScientificTraceability:
    """Convenience factory for assembling a complete, validated ScientificTraceability record."""
    return ScientificTraceability(
        model_name=model_name,
        equation_form=equation_form,
        equation_reference=equation_reference,
        scientific_sources=scientific_sources or [],
        inputs_used=inputs_used or {},
        parameters_used=parameters_used or {},
        parameter_sources=parameter_sources or {},
        units_used=units_used or {},
        validity_range=validity_range or {},
        assumptions=assumptions or [],
        uncertainty_description=uncertainty_description,
        uncertainty_interval=uncertainty_interval,
        failure_or_unknown_reason=failure_or_unknown_reason,
        warnings=warnings or [],
    )
