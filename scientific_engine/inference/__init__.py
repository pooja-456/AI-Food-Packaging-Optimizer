"""
Generic Property Inference Module (Phase 3).

Provides evidence-driven property inference for missing scientific parameters
with explicit uncertainty quantification, full literature traceability, and strict
unknown handling.
"""

from scientific_engine.inference.engine import PropertyInferenceEngine, infer_commodity_properties

__all__ = [
    "PropertyInferenceEngine",
    "infer_commodity_properties",
]
