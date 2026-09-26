import pytest
from app.schemas.physics import CalculationStatus, ScientificResult
from scientific_engine.physics.gas_exchange import GasExchangeModel
from scientific_engine.physics.traceability import make_traceability


def test_gas_exchange_with_complete_inputs() -> None:
    model = GasExchangeModel()
    # 20 mg O2/kg/hr respiration rate, 2 kg product mass
    resp_result = ScientificResult(
        status=CalculationStatus.CALCULATED,
        value=20.0,
        unit="mg O2/kg/hr",
        uncertainty_range=(15.0, 25.0),
        traceability=make_traceability(model_name="MockResp", equation_form="r"),
    )
    gas_req = model.calculate_gas_requirements(
        respiration_result=resp_result,
        target_o2_percent=3.0,
        target_co2_percent=5.0,
        product_mass_kg=2.0,
        package_area_m2=0.1,
        rq=1.0,
    )
    assert gas_req.status == CalculationStatus.CALCULATED
    assert gas_req.required_otr_cc_per_pkg_day is not None
    assert gas_req.required_otr_cc_per_pkg_day.value is not None
    assert gas_req.required_otr_cc_per_pkg_day.value > 0
    assert gas_req.required_otr_per_area is not None
    assert gas_req.required_otr_per_area.value is not None
    assert gas_req.ideal_beta_ratio_co2_to_o2 is not None
    assert gas_req.ideal_beta_ratio_co2_to_o2.value is not None
    # Beta = 1.0 * (20.9 - 3.0) / (5.0 - 0.04) = 17.9 / 4.96 ≈ 3.61
    assert abs(gas_req.ideal_beta_ratio_co2_to_o2.value - 3.61) < 0.05


def test_gas_exchange_missing_product_mass_returns_partially_calculated() -> None:
    model = GasExchangeModel()
    resp_result = ScientificResult(
        status=CalculationStatus.CALCULATED,
        value=20.0,
        unit="mg O2/kg/hr",
        traceability=make_traceability(model_name="MockResp", equation_form="r"),
    )
    # product_mass_kg is None
    gas_req = model.calculate_gas_requirements(
        respiration_result=resp_result,
        target_o2_percent=3.0,
        target_co2_percent=5.0,
        product_mass_kg=None,
    )
    assert gas_req.status == CalculationStatus.PARTIALLY_CALCULATED
    assert gas_req.required_otr_cc_per_pkg_day is not None
    assert gas_req.required_otr_cc_per_pkg_day.unit == "cc O2 / (kg product · day)"
    assert gas_req.required_otr_per_area is None  # Normalized area OTR cannot be computed without mass
    assert any("PARTIALLY_CALCULATED" in w for w in gas_req.warnings)


def test_gas_exchange_with_unknown_respiration_returns_unknown() -> None:
    model = GasExchangeModel()
    resp_unknown = ScientificResult(
        status=CalculationStatus.UNKNOWN,
        value=None,
        unit="mg O2/kg/hr",
        traceability=make_traceability(model_name="MockResp", equation_form="r", failure_or_unknown_reason="No data"),
    )
    gas_req = model.calculate_gas_requirements(
        respiration_result=resp_unknown,
        product_mass_kg=1.0,
    )
    assert gas_req.status == CalculationStatus.UNKNOWN
    assert gas_req.required_otr_cc_per_pkg_day is None
    assert any("UNKNOWN" in w for w in gas_req.warnings)
