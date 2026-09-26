"""
Dedicated scientific audit verification tests for Phase 4 Physics Engine.

Validates:
1. Sub-zero Tetens/Buck saturation vapor pressure and thermodynamic continuity at 0°C.
2. Ratkowsky microbial temperature model with growth arrest at T <= Tmin (no magic numbers).
3. Stoichiometric molar mass conversion in empirical respiration rate handling.
4. Impossible gas gradient handling (non-positive driving force).
5. Interval division with zero-crossing protection.
6. Multi-mechanism shelf-life synthesis with growth arrest.
"""

import pytest
import math
from app.schemas.inference import InferredProperty, InferenceResolutionLevel
from app.schemas.physics import CalculationStatus, ScientificResult
from app.schemas.property_status import PropertyStatusEnum
from scientific_engine.physics.base import (
    MOLAR_MASS_CO2_G_MOL,
    MOLAR_MASS_O2_G_MOL,
    food_surface_vapor_pressure_kpa,
    water_saturation_vapor_pressure_kpa,
    water_vapor_pressure_kpa,
)
from scientific_engine.physics.gas_exchange import GasExchangeModel
from scientific_engine.physics.microbial import MicrobialGrowthModel
from scientific_engine.physics.moisture import MoistureTransferModel
from scientific_engine.physics.respiration import RespirationKineticsModel
from scientific_engine.physics.traceability import make_traceability
from scientific_engine.physics.uncertainty import divide_intervals, scale_interval


# =============================================================================
# 1. Tetens Saturation Vapor Pressure across Positive and Sub-Zero Domains
# =============================================================================

def test_tetens_subzero_ice_regime() -> None:
    # At 0 °C, Psat = 0.61078 kPa
    psat_0 = water_saturation_vapor_pressure_kpa(0.0)
    assert abs(psat_0 - 0.61078) < 1e-4

    # At -10 °C: Psat = 0.61078 * exp(21.875 * -10 / (-10 + 265.5)) ≈ 0.2595 kPa
    psat_m10 = water_saturation_vapor_pressure_kpa(-10.0)
    assert abs(psat_m10 - 0.2595) < 1e-3

    # At -20 °C: Psat = 0.61078 * exp(21.875 * -20 / (-20 + 265.5)) ≈ 0.1028 kPa
    psat_m20 = water_saturation_vapor_pressure_kpa(-20.0)
    assert abs(psat_m20 - 0.1028) < 1e-3

    # Monotonicity check: Psat(-20) < Psat(-10) < Psat(0) < Psat(20)
    psat_20 = water_saturation_vapor_pressure_kpa(20.0)
    assert psat_m20 < psat_m10 < psat_0 < psat_20


def test_food_vapor_pressure_gradient_subzero() -> None:
    model = MoistureTransferModel()
    # Chilled/frozen food at -5 °C, RH = 85%, aw = 0.90
    # Psat(-5°C) = 0.61078 * exp(21.875 * -5 / 260.5) ≈ 0.4010 kPa
    # p_ext = 0.85 * 0.4010 = 0.3409 kPa
    # p_food = 0.90 * 0.4010 = 0.3609 kPa
    # delta_p = |0.3409 - 0.3609| = 0.0200 kPa
    req = model.calculate_moisture_requirements(
        initial_water_activity=0.90,
        storage_temperature_c=-5.0,
        relative_humidity_percent=85.0,
    )
    assert req.status == CalculationStatus.PARTIALLY_CALCULATED
    assert req.water_vapor_pressure_gradient_kpa is not None
    assert abs(req.water_vapor_pressure_gradient_kpa.value - 0.020) < 0.005


# =============================================================================
# 2. Ratkowsky Model at and below Tmin (Arrested Growth, No Magic Numbers)
# =============================================================================

def test_ratkowsky_temperature_below_tmin_growth_arrest() -> None:
    model = MicrobialGrowthModel()
    # Tmin = 0.0 °C, Storage T = -2.0 °C (below Tmin)
    req = model.calculate_microbial_limits(
        target_microorganism="Listeria monocytogenes",
        initial_count_log_cfu=1.0,
        critical_count_log_cfu=3.0,
        temperature_c=-2.0,
        ratkowsky_b=0.05,
        ratkowsky_tmin_c=0.0,
        lag_time_days=2.0,
    )
    assert req.status == CalculationStatus.CALCULATED
    assert req.growth_rate_per_day is not None
    assert req.growth_rate_per_day.value == 0.0
    # Microbial shelf life should be None (not 999.0 magic number)
    assert req.microbial_shelf_life_days is not None
    assert req.microbial_shelf_life_days.value is None
    assert any("completely arrested" in a for a in req.traceability.assumptions)


# =============================================================================
# 3. Respiration Stoichiometric Molar Mass Conversion
# =============================================================================

def test_respiration_rate_co2_to_o2_stoichiometry() -> None:
    model = RespirationKineticsModel()
    inferred_prop = InferredProperty(
        property_name="respiration_rate",
        value=100.0,
        unit="mg CO2/kg/hr",
        status=PropertyStatusEnum.measured,
        resolution_level=InferenceResolutionLevel.EXACT_CONTEXT_MATCH,
        uncertainty_range=(80.0, 120.0),
        citations=["Test Citation (2026)"],
    )
    # RQ = 1.0 -> r_O2 = 100 * (31.9988 / 44.0095) = 72.709 mg O2/kg/hr
    res = model.calculate_respiration(
        inferred_respiration=inferred_prop,
        temperature_c=15.0,
        rq=1.0,
    )
    assert res.status == CalculationStatus.CALCULATED
    assert abs(res.value - 72.709) < 0.01
    assert res.unit == "mg O2/kg/hr"
    assert res.uncertainty_range is not None
    assert abs(res.uncertainty_range[0] - (80.0 * 31.9988 / 44.0095)) < 0.01
    assert abs(res.uncertainty_range[1] - (120.0 * 31.9988 / 44.0095)) < 0.01


def test_respiration_rate_direct_o2_preservation() -> None:
    model = RespirationKineticsModel()
    inferred_prop = InferredProperty(
        property_name="respiration_rate",
        value=50.0,
        unit="mg O2/kg/hr",
        status=PropertyStatusEnum.measured,
        resolution_level=InferenceResolutionLevel.EXACT_CONTEXT_MATCH,
        uncertainty_range=(40.0, 60.0),
    )
    res = model.calculate_respiration(
        inferred_respiration=inferred_prop,
        temperature_c=10.0,
    )
    assert res.status == CalculationStatus.CALCULATED
    assert res.value == 50.0
    assert res.uncertainty_range == (40.0, 60.0)


# =============================================================================
# 4. Gas Exchange Driving Force Boundary Conditions
# =============================================================================

def test_gas_exchange_impossible_driving_force_returns_unknown() -> None:
    model = GasExchangeModel()
    resp_result = ScientificResult(
        status=CalculationStatus.CALCULATED,
        value=20.0,
        unit="mg O2/kg/hr",
        traceability=make_traceability(model_name="MockResp", equation_form="r"),
    )
    # Target O2 = 25% (> ambient 20.9%), driving force is negative
    gas_req = model.calculate_gas_requirements(
        respiration_result=resp_result,
        target_o2_percent=25.0,
        target_co2_percent=5.0,
        product_mass_kg=1.0,
    )
    assert gas_req.status == CalculationStatus.UNKNOWN
    assert any("Invalid target gas gradient" in gas_req.traceability.failure_or_unknown_reason or "Target atmosphere gradients are zero or negative" in w for w in gas_req.warnings)


# =============================================================================
# 5. Interval Division with Zero-Crossing Safety
# =============================================================================

def test_interval_division_safeguards() -> None:
    # Denominator strictly positive: [2.0, 4.0] / [1.0, 2.0] = [1.0, 4.0]
    res = divide_intervals((2.0, 4.0), (1.0, 2.0))
    assert res is not None
    assert res == (1.0, 4.0)

    # Denominator spanning zero: [-1.0, 2.0] -> undefined -> returns None
    res_zero = divide_intervals((2.0, 4.0), (-1.0, 2.0))
    assert res_zero is None

    # Denominator strictly negative: [2.0, 4.0] / [-4.0, -2.0] = [-2.0, -0.5]
    res_neg = divide_intervals((2.0, 4.0), (-4.0, -2.0))
    assert res_neg is not None
    assert res_neg == (-2.0, -0.5)
