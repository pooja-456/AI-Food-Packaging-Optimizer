import pytest
from app.schemas.physics import CalculationStatus
from scientific_engine.physics.gas_exchange import GasExchangeModel
from scientific_engine.physics.moisture import MoistureTransferModel
from scientific_engine.physics.respiration import RespirationKineticsModel


def test_respiration_traceability_audit_fields() -> None:
    model = RespirationKineticsModel()
    res = model.calculate_respiration(
        o2_percent=5.0,
        temperature_c=10.0,
        vm=50.0,
        km=3.0,
    )
    trace = res.traceability
    assert trace.model_name == "MichaelisMentenRespirationKinetics"
    assert trace.equation_form is not None
    assert trace.equation_reference is not None
    assert len(trace.scientific_sources) > 0
    assert "o2_percent" in trace.inputs_used
    assert "Vm" in trace.parameters_used
    assert "r_O2" in trace.units_used
    assert len(trace.assumptions) > 0


def test_moisture_traceability_audit_fields() -> None:
    model = MoistureTransferModel()
    req = model.calculate_moisture_requirements(
        initial_water_activity=0.50,
        storage_temperature_c=20.0,
        relative_humidity_percent=80.0,
    )
    trace = req.water_vapor_pressure_gradient_kpa.traceability
    assert trace.model_name == "VaporPressureMoistureTransfer"
    assert "Tetens" in trace.equation_reference
    assert "aw" in trace.inputs_used
    assert "Psat_kPa" in trace.parameters_used
    assert "Δp_w" in trace.units_used
