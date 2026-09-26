import pytest
from app.schemas.physics import CalculationStatus
from scientific_engine.physics.gas_exchange import GasExchangeModel
from scientific_engine.physics.microbial import MicrobialGrowthModel
from scientific_engine.physics.moisture import MoistureTransferModel
from scientific_engine.physics.respiration import RespirationKineticsModel


def test_respiration_unknown_when_no_inputs() -> None:
    model = RespirationKineticsModel()
    res = model.calculate_respiration(inferred_respiration=None)
    assert res.status == CalculationStatus.UNKNOWN
    assert res.value is None
    assert res.traceability.failure_or_unknown_reason is not None


def test_moisture_unknown_when_no_aw_or_moisture() -> None:
    model = MoistureTransferModel()
    req = model.calculate_moisture_requirements(
        initial_water_activity=None,
        initial_moisture_percent=None,
    )
    assert req.status == CalculationStatus.UNKNOWN
    assert req.water_vapor_pressure_gradient_kpa is None


def test_microbial_unknown_when_no_target_organism() -> None:
    model = MicrobialGrowthModel()
    req = model.calculate_microbial_limits(
        target_microorganism=None,
        initial_count_log_cfu=None,
    )
    assert req.status == CalculationStatus.UNKNOWN
    assert req.growth_rate_per_day is None
    assert req.microbial_shelf_life_days is None
