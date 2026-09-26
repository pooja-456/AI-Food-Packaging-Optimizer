import pytest
from app.schemas.inference import InferredProperty, InferenceResolutionLevel
from app.schemas.physics import CalculationStatus
from app.schemas.property_status import PropertyStatusEnum
from scientific_engine.physics.respiration import RespirationKineticsModel


def test_valid_michaelis_menten_respiration() -> None:
    model = RespirationKineticsModel()
    res = model.calculate_respiration(
        o2_percent=5.0,
        temperature_c=10.0,
        vm=40.0,
        km=2.0,
    )
    assert res.status == CalculationStatus.CALCULATED
    assert res.value is not None
    # r = (40 * 5) / (2 + 5) = 200 / 7 ≈ 28.571
    assert abs(res.value - 28.571) < 0.01
    assert res.unit == "mg O2/kg/hr"
    assert "Peppelenbos" in res.traceability.equation_reference


def test_co2_inhibited_michaelis_menten_respiration() -> None:
    model = RespirationKineticsModel()
    # Without CO2: r = (40 * 5) / (2 + 5) ≈ 28.571
    # With 10% CO2 and Ki=15: denom = 2 + (1 + 10/15) * 5 = 2 + 1.667 * 5 = 2 + 8.333 = 10.333
    # r = 200 / 10.333 ≈ 19.355
    res = model.calculate_respiration(
        o2_percent=5.0,
        co2_percent=10.0,
        temperature_c=10.0,
        vm=40.0,
        km=2.0,
        ki=15.0,
    )
    assert res.status == CalculationStatus.CALCULATED
    assert res.value is not None
    assert res.value < 28.571  # Confirms inhibition reduces rate
    assert abs(res.value - 19.355) < 0.02


def test_respiration_from_inferred_evidence() -> None:
    model = RespirationKineticsModel()
    inferred_prop = InferredProperty(
        property_name="respiration_rate",
        value=35.0,
        unit="mg CO2/kg/hr",
        status=PropertyStatusEnum.literature,
        resolution_level=InferenceResolutionLevel.TEMPERATURE_MATCH,
        uncertainty_range=(25.0, 50.0),
        citations=["Kader (2002) Postharvest Technology"],
    )
    res = model.calculate_respiration(
        inferred_respiration=inferred_prop,
        temperature_c=20.0,
        rq=1.0,
    )
    assert res.status == CalculationStatus.CALCULATED
    # Stoichiometric conversion: r_O2 = (35.0 / 1.0) * (31.9988 / 44.0095) ≈ 25.448 mg O2/kg/hr
    assert abs(res.value - 25.448) < 0.01
    assert res.unit == "mg O2/kg/hr"
    assert res.uncertainty_range is not None
    assert abs(res.uncertainty_range[0] - 18.177) < 0.02
    assert abs(res.uncertainty_range[1] - 36.354) < 0.02


def test_missing_respiration_parameters_returns_unknown() -> None:
    model = RespirationKineticsModel()
    res = model.calculate_respiration()
    assert res.status == CalculationStatus.UNKNOWN
    assert res.value is None
    assert "Missing scientific evidence" in res.traceability.failure_or_unknown_reason or "Neither Michaelis-Menten" in res.traceability.failure_or_unknown_reason


def test_respiration_temperature_warning() -> None:
    model = RespirationKineticsModel()
    res = model.calculate_respiration(
        o2_percent=5.0,
        temperature_c=45.0,  # Exceeds 40°C threshold
        vm=40.0,
        km=2.0,
    )
    assert res.status == CalculationStatus.CALCULATED
    assert any("exceeds validated upper limit" in w for w in res.traceability.warnings)
