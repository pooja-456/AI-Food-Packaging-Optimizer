import pytest
from app.schemas.physics import CalculationStatus
from scientific_engine.physics.sorption import GABModel, HalseyModel, LinearLowAwModel, OswinModel


def test_gab_model_valid_calculation() -> None:
    # Typical parameters for starchy food: m0 = 6.5 g/100g, C = 15.0, K = 0.82
    gab = GABModel(m0=6.5, c=15.0, k=0.82, parameter_source="Labuza (1984)")
    res = gab.calculate_moisture_content(water_activity=0.60, temperature_c=25.0)

    assert res.status == CalculationStatus.CALCULATED
    assert res.value is not None
    assert res.value > 0
    assert res.unit == "g H2O / 100g dry solids"
    assert "GAB" in res.traceability.model_name
    assert "van den Berg" in res.traceability.equation_reference


def test_gab_model_invalid_parameters_returns_unknown() -> None:
    # K must be > 0 and <= 1
    gab_invalid = GABModel(m0=6.5, c=15.0, k=1.5, parameter_source="Invalid")
    res = gab_invalid.calculate_moisture_content(water_activity=0.60)
    assert res.status == CalculationStatus.UNKNOWN
    assert "Thermodynamically invalid GAB parameters" in res.traceability.failure_or_unknown_reason


def test_oswin_model_valid_calculation() -> None:
    oswin = OswinModel(a=8.0, b=0.45, parameter_source="Oswin (1946)")
    res = oswin.calculate_moisture_content(water_activity=0.50)
    assert res.status == CalculationStatus.CALCULATED
    # at aw=0.5: aw/(1-aw) = 1.0 => m = 8.0 * (1.0)^0.45 = 8.0
    assert abs(res.value - 8.0) < 0.001


def test_halsey_model_valid_calculation() -> None:
    halsey = HalseyModel(a=0.08, b=1.5, parameter_source="Halsey (1948)")
    res = halsey.calculate_moisture_content(water_activity=0.50)
    assert res.status == CalculationStatus.CALCULATED
    assert res.value is not None
    assert res.value > 0


def test_linear_low_aw_model() -> None:
    linear_model = LinearLowAwModel(slope=20.0, m0=1.0, parameter_source="Labuza (1984)")
    res = linear_model.calculate_moisture_content(water_activity=0.20)
    assert res.status == CalculationStatus.CALCULATED
    # m = 20 * 0.2 + 1 = 5.0
    assert abs(res.value - 5.0) < 0.001
