"""
Scientific Physics and Packaging Requirement Engine (Phase 4).

Modules:
- base: Physical constants, thermodynamic vapor pressure (Tetens), and gas conversions.
- traceability: Traceability builder for full scientific provenance.
- uncertainty: Interval arithmetic and non-destructive range propagation.
- applicability: Domain validity checks for temperatures, water activity, and gas fractions.
- respiration: Michaelis-Menten respiration kinetics and empirical rates (Model A).
- gas_exchange: Equilibrium Modified Atmosphere Packaging (EMAP) mass balances (Model B).
- sorption: Moisture sorption isotherm models: GAB, Oswin, Halsey, Linear (Model C Sorption).
- moisture: Moisture transfer driving forces, vapor pressure gradients, and WVTR targets (Model C).
- microbial: Evidence-gated predictive microbiological proliferation limits (Model D).
- requirements: PackagingRequirementEngine orchestrator.
"""

from scientific_engine.physics.base import (
    food_surface_vapor_pressure_kpa,
    mg_co2_to_ml_co2,
    mg_o2_to_ml_o2,
    ml_co2_to_mg_co2,
    ml_o2_to_mg_o2,
    water_saturation_vapor_pressure_kpa,
    water_vapor_pressure_kpa,
)
from scientific_engine.physics.gas_exchange import GasExchangeModel
from scientific_engine.physics.microbial import MicrobialGrowthModel
from scientific_engine.physics.moisture import MoistureTransferModel
from scientific_engine.physics.requirements import PackagingRequirementEngine
from scientific_engine.physics.respiration import RespirationKineticsModel
from scientific_engine.physics.sorption import (
    GABModel,
    HalseyModel,
    LinearLowAwModel,
    MoistureSorptionModel,
    OswinModel,
)
from scientific_engine.physics.traceability import make_traceability
from scientific_engine.physics.uncertainty import (
    add_intervals,
    divide_interval_by_scalar,
    multiply_intervals,
    scale_interval,
    subtract_intervals,
)

__all__ = [
    "water_saturation_vapor_pressure_kpa",
    "water_vapor_pressure_kpa",
    "food_surface_vapor_pressure_kpa",
    "mg_co2_to_ml_co2",
    "ml_co2_to_mg_co2",
    "mg_o2_to_ml_o2",
    "ml_o2_to_mg_o2",
    "make_traceability",
    "add_intervals",
    "subtract_intervals",
    "scale_interval",
    "multiply_intervals",
    "divide_interval_by_scalar",
    "RespirationKineticsModel",
    "GasExchangeModel",
    "MoistureSorptionModel",
    "GABModel",
    "OswinModel",
    "HalseyModel",
    "LinearLowAwModel",
    "MoistureTransferModel",
    "MicrobialGrowthModel",
    "PackagingRequirementEngine",
]
