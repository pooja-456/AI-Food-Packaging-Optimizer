import pytest
from app.schemas.physics import CalculationStatus
from scientific_engine.physics.base import water_saturation_vapor_pressure_kpa
from scientific_engine.physics.moisture import MoistureTransferModel
from scientific_engine.physics.sorption import GABModel


def test_tetens_water_saturation_vapor_pressure() -> None:
    # At 20 °C, Psat is approx 2.338 kPa
    psat_20 = water_saturation_vapor_pressure_kpa(20.0)
    assert abs(psat_20 - 2.338) < 0.02

    # At 0 °C, Psat is approx 0.611 kPa
    psat_0 = water_saturation_vapor_pressure_kpa(0.0)
    assert abs(psat_0 - 0.611) < 0.01


def test_moisture_transfer_vapor_pressure_gradient() -> None:
    model = MoistureTransferModel()
    # At 20°C: Psat = 2.338 kPa. Ext RH = 80% (p_ext = 1.870 kPa), food aw = 0.50 (p_food = 1.169 kPa)
    # delta_p = 1.870 - 1.169 = 0.701 kPa
    req = model.calculate_moisture_requirements(
        initial_water_activity=0.50,
        storage_temperature_c=20.0,
        relative_humidity_percent=80.0,
    )
    assert req.status == CalculationStatus.PARTIALLY_CALCULATED  # Delta_p is calculated, but WVTR needs mass/shelf-life
    assert req.water_vapor_pressure_gradient_kpa is not None
    assert req.water_vapor_pressure_gradient_kpa.status == CalculationStatus.CALCULATED
    assert abs(req.water_vapor_pressure_gradient_kpa.value - 0.701) < 0.05


def test_moisture_transfer_with_complete_inputs() -> None:
    model = MoistureTransferModel()
    # Food initial moisture 5.0%, critical moisture 8.0%, dry mass 500 g, target shelf-life 30 days, area 0.05 m2
    # delta_m = (8.0 - 5.0) * (500 / 100) = 3.0 * 5 = 15.0 g H2O
    # WVTR_pkg = 15.0 / 30 = 0.5 g / pkg / day
    # WVTR_area = 0.5 / 0.05 = 10.0 g / (m2 day)
    req = model.calculate_moisture_requirements(
        initial_water_activity=0.30,
        critical_water_activity=0.60,
        initial_moisture_percent=5.0,
        critical_moisture_percent=8.0,
        storage_temperature_c=20.0,
        relative_humidity_percent=75.0,
        target_shelf_life_days=30,
        dry_mass_g=500.0,
        package_area_m2=0.05,
    )
    assert req.status == CalculationStatus.CALCULATED
    assert req.required_wvtr_g_per_pkg_day is not None
    assert abs(req.required_wvtr_g_per_pkg_day.value - 0.5) < 0.001
    assert req.required_wvtr_per_area is not None
    assert abs(req.required_wvtr_per_area.value - 10.0) < 0.01


def test_moisture_transfer_with_unknown_moisture_returns_unknown() -> None:
    model = MoistureTransferModel()
    req = model.calculate_moisture_requirements(
        initial_water_activity=None,
        initial_moisture_percent=None,
    )
    assert req.status == CalculationStatus.UNKNOWN
    assert any("UNKNOWN" in w for w in req.warnings)
